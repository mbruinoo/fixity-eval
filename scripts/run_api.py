"""Run chat conditions against the Messages API directly (no Claude Code,
no tools; a system prompt only when the condition names one), with a hard cost guard.

Each condition sends one user message: the prompt, a blank line, then the
full text of the input file. A condition may add follow-up turns
("followups"), each sent after the model's previous reply.

The key is read from FIXITY_ANTHROPIC_API_KEY and never written anywhere.
Every call's cost is added to <experiment>/cost_ledger.json. A call is not
started if its worst case (estimated input + max_tokens of output) could
push the ledger past the config's budget_stop_usd, or if the call count
would reach max_calls.

Saved per run, under <experiment>/runs/<id>/:
    request_turn<N>.json    the request body (no key)
    response_turn<N>.json   the full API response
    response.md             text of the final reply
    meta.json               usage, cost, stop reasons, timestamps

Usage:
    python scripts/run_api.py experiments/spike-03/config.json [--only ID ...] [--dry-run]
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import pathlib
import threading

import anthropic

LOCK = threading.Lock()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


class Ledger:
    def __init__(self, path, cfg):
        self.path = path
        self.budget = cfg["budget_stop_usd"]
        self.max_calls = cfg["max_calls"]
        self.price_in = cfg["price_per_mtok"]["input"] / 1e6
        self.price_out = cfg["price_per_mtok"]["output"] / 1e6
        self.model_prices = cfg.get("model_prices", {})
        self.data = json.loads(path.read_text()) if path.exists() else {"spent_usd": 0.0, "calls": 0, "entries": []}
        self.reserved = 0.0
        self.reserved_calls = 0

    def prices(self, model):
        p = self.model_prices.get(model)
        return (p["input"] / 1e6, p["output"] / 1e6) if p else (self.price_in, self.price_out)

    def cost(self, usage, model=None):
        pin, pout = self.prices(model)
        return usage.input_tokens * pin + usage.output_tokens * pout

    def reserve(self, est_in, max_out, model=None):
        pin, pout = self.prices(model)
        worst = est_in * pin + max_out * pout
        with LOCK:
            if self.data["spent_usd"] + self.reserved + worst > self.budget:
                raise RuntimeError(f"budget guard: spent {self.data['spent_usd']:.4f} + reserved "
                                   f"{self.reserved:.4f} + worst {worst:.4f} > {self.budget}")
            if self.data["calls"] + self.reserved_calls + 1 > self.max_calls:
                raise RuntimeError("call-count guard")
            self.reserved += worst
            self.reserved_calls += 1
        return worst

    def settle(self, worst, run_id, turn, usage, model=None):
        c = self.cost(usage, model) if usage else 0.0
        with LOCK:
            self.reserved -= worst
            self.reserved_calls -= 1
            self.data["spent_usd"] += c
            self.data["calls"] += 1
            self.data["entries"].append({"run": run_id, "turn": turn, "cost_usd": round(c, 6), "at": now()})
            self.path.write_text(json.dumps(self.data, indent=2) + "\n")
        return c


def build_params(cfg, cond, messages):
    p = {"model": cond.get("model", cfg["model"]), "max_tokens": cond.get("max_tokens", cfg["max_tokens"]), "messages": messages}
    if cond.get("system"):
        p["system"] = cfg["systems"][cond["system"]]
    if cond.get("effort"):
        p["output_config"] = {"effort": cond["effort"]}
    if cond.get("thinking") == "disabled":
        p["thinking"] = {"type": "disabled"}
    if cond.get("tools") == "code_execution":
        p["tools"] = [{"type": "code_execution_20250825", "name": "code_execution"}]
    return p


def first_message(client, cfg, cond, run_dir):
    """The opening user message. "attach" decides how the sheet arrives:
    pasted after the prompt (default), as a text document block (like a
    file attached in a chat app), or uploaded into the code-execution
    sandbox (like a file the model reads with tools)."""
    path = pathlib.Path(cfg["inputs"][cond.get("input", "default")])
    data = path.read_text(encoding="utf-8")
    how = cond.get("attach", "paste")
    if how == "paste":
        return cond["prompt"] + "\n\n" + data, len(data)
    if how == "document":
        return [{"type": "document", "title": cond.get("filename", path.name),
                 "source": {"type": "text", "media_type": "text/plain", "data": data}},
                {"type": "text", "text": cond["prompt"]}], len(data)
    if how == "upload":
        up = client.beta.files.upload(file=(cond.get("filename", path.name), path.read_bytes(), "text/plain"))
        (run_dir / "uploaded_file.json").write_text(json.dumps({"file_id": up.id, "filename": up.filename}))
        return [{"type": "text", "text": cond["prompt"]},
                {"type": "container_upload", "file_id": up.id}], 200
    raise ValueError(how)


def save_output_files(client, msg, run_dir):
    """Download files the model created in the sandbox."""
    saved = []
    for b in msg.content:
        content = getattr(b, "content", None)
        for ref in getattr(content, "content", None) or []:
            fid = getattr(ref, "file_id", None)
            if not fid:
                continue
            meta = client.beta.files.retrieve_metadata(fid)
            name = os.path.basename(meta.filename) or fid
            out = run_dir / "output_files" / name
            out.parent.mkdir(exist_ok=True)
            client.beta.files.download(fid).write_to_file(out)
            saved.append(name)
    return saved


def run_one(client, cfg, root, ledger, cond, rep):
    run_id = f"{cond['id']}-r{rep}"
    d = root / "runs" / run_id
    if (d / "meta.json").exists():
        return run_id, "skipped (exists)"
    d.mkdir(parents=True, exist_ok=True)
    first, data_chars = first_message(client, cfg, cond, d)
    turns = [first] + cond.get("followups", [])
    messages, meta = [], {"run": run_id, "condition": cond, "started": now(), "turns": []}
    container, all_text = None, []
    i = 0
    pending = list(turns)
    while (pending or meta["turns"][-1]["stop_reason"] == "pause_turn") and i < 10:
        i += 1
        if not (meta["turns"] and meta["turns"][-1]["stop_reason"] == "pause_turn"):
            messages.append({"role": "user", "content": pending.pop(0)})
        params = build_params(cfg, cond, messages)
        if container:
            params["container"] = container
        (d / f"request_turn{i}.json").write_text(json.dumps(params, indent=1, ensure_ascii=False))
        est_in = (len(params.get("system", "")) + data_chars + len(json.dumps(messages[1:]))) // 3 + 3000
        worst = ledger.reserve(est_in, params["max_tokens"], params["model"])
        t0, usage = now(), None
        try:
            with client.messages.stream(**params) as s:
                msg = s.get_final_message()
            usage = msg.usage
        finally:
            cost = ledger.settle(worst, run_id, i, usage, params["model"])
        if getattr(msg, "container", None):
            container = msg.container.id
        files = save_output_files(client, msg, d) if cond.get("tools") else []
        (d / f"response_turn{i}.json").write_text(msg.model_dump_json(indent=1))
        text_out = "".join(b.text for b in msg.content if b.type == "text")
        meta["turns"].append({
            "turn": i, "started": t0, "finished": now(), "model": msg.model,
            "stop_reason": msg.stop_reason, "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens, "cost_usd": round(cost, 6),
            "content_types": [b.type for b in msg.content], "output_files": files,
        })
        all_text.append(text_out)
        # Thinking blocks are passed back unchanged, as the API expects.
        messages.append({"role": "assistant", "content": [b.model_dump(exclude_none=True) for b in msg.content]})
    (d / "response.md").write_text("\n\n".join(t for t in all_text if t), encoding="utf-8")
    meta["finished"] = now()
    meta["cost_usd"] = round(sum(t["cost_usd"] for t in meta["turns"]), 6)
    (d / "meta.json").write_text(json.dumps(meta, indent=2))
    return run_id, f"${meta['cost_usd']:.4f} stop={[t['stop_reason'] for t in meta['turns']]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--repeats", type=int)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    cfg_path = pathlib.Path(a.config)
    cfg = json.loads(cfg_path.read_text())
    root = cfg_path.parent
    ledger = Ledger(root / "cost_ledger.json", cfg)
    conds = [c for c in cfg["conditions"] if not a.only or c["id"] in a.only]
    jobs = [(c, r) for c in conds for r in range(1, (a.repeats or c.get("repeats", cfg["repeats"])) + 1)]
    if a.dry_run:
        for c, r in jobs:
            print(c["id"], r)
        print(len(jobs), "runs; ledger so far", ledger.data["spent_usd"], ledger.data["calls"])
        return
    client = anthropic.Anthropic(api_key=os.environ["FIXITY_ANTHROPIC_API_KEY"], max_retries=3)
    with cf.ThreadPoolExecutor(cfg.get("parallel", 4)) as ex:
        futs = {ex.submit(run_one, client, cfg, root, ledger, c, r): (c, r) for c, r in jobs}
        for f in cf.as_completed(futs):
            try:
                print(*f.result(), flush=True)
            except Exception as e:  # report and keep going; the ledger is already settled
                print(futs[f][0]["id"], futs[f][1], "ERROR", type(e).__name__, str(e)[:300], flush=True)
    print(f"ledger: ${ledger.data['spent_usd']:.4f} over {ledger.data['calls']} calls")


if __name__ == "__main__":
    main()
