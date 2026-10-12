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
        self.data = json.loads(path.read_text()) if path.exists() else {"spent_usd": 0.0, "calls": 0, "entries": []}
        self.reserved = 0.0
        self.reserved_calls = 0

    def cost(self, usage):
        return usage.input_tokens * self.price_in + usage.output_tokens * self.price_out

    def reserve(self, est_in, max_out):
        worst = est_in * self.price_in + max_out * self.price_out
        with LOCK:
            if self.data["spent_usd"] + self.reserved + worst > self.budget:
                raise RuntimeError(f"budget guard: spent {self.data['spent_usd']:.4f} + reserved "
                                   f"{self.reserved:.4f} + worst {worst:.4f} > {self.budget}")
            if self.data["calls"] + self.reserved_calls + 1 > self.max_calls:
                raise RuntimeError("call-count guard")
            self.reserved += worst
            self.reserved_calls += 1
        return worst

    def settle(self, worst, run_id, turn, usage):
        c = self.cost(usage) if usage else 0.0
        with LOCK:
            self.reserved -= worst
            self.reserved_calls -= 1
            self.data["spent_usd"] += c
            self.data["calls"] += 1
            self.data["entries"].append({"run": run_id, "turn": turn, "cost_usd": round(c, 6), "at": now()})
            self.path.write_text(json.dumps(self.data, indent=2) + "\n")
        return c


def build_params(cfg, cond, messages):
    p = {"model": cfg["model"], "max_tokens": cond.get("max_tokens", cfg["max_tokens"]), "messages": messages}
    if cond.get("system"):
        p["system"] = cfg["systems"][cond["system"]]
    if cond.get("effort"):
        p["output_config"] = {"effort": cond["effort"]}
    if cond.get("thinking") == "disabled":
        p["thinking"] = {"type": "disabled"}
    return p


def run_one(client, cfg, root, ledger, cond, rep):
    run_id = f"{cond['id']}-r{rep}"
    d = root / "runs" / run_id
    if (d / "meta.json").exists():
        return run_id, "skipped (exists)"
    d.mkdir(parents=True, exist_ok=True)
    data = pathlib.Path(cfg["inputs"][cond.get("input", "default")]).read_text(encoding="utf-8")
    turns = [cond["prompt"] + "\n\n" + data] + cond.get("followups", [])
    messages, meta = [], {"run": run_id, "condition": cond, "started": now(), "turns": []}
    for i, text in enumerate(turns, 1):
        messages.append({"role": "user", "content": text})
        params = build_params(cfg, cond, messages)
        (d / f"request_turn{i}.json").write_text(json.dumps(params, indent=1, ensure_ascii=False))
        est_in = len(params.get("system", "")) // 3 + sum(len(m["content"]) if isinstance(m["content"], str) else 0 for m in messages) // 3
        worst = ledger.reserve(est_in, params["max_tokens"])
        t0, usage = now(), None
        try:
            with client.messages.stream(**params) as s:
                msg = s.get_final_message()
            usage = msg.usage
        finally:
            cost = ledger.settle(worst, run_id, i, usage)
        (d / f"response_turn{i}.json").write_text(msg.model_dump_json(indent=1))
        text_out = "".join(b.text for b in msg.content if b.type == "text")
        meta["turns"].append({
            "turn": i, "started": t0, "finished": now(), "model": msg.model,
            "stop_reason": msg.stop_reason, "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens, "cost_usd": round(cost, 6),
            "content_types": [b.type for b in msg.content],
        })
        # Thinking blocks are passed back unchanged, as the API expects.
        messages.append({"role": "assistant", "content": [b.model_dump(exclude_none=True) for b in msg.content]})
    (d / "response.md").write_text(text_out, encoding="utf-8")
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
    jobs = [(c, r) for c in conds for r in range(1, c.get("repeats", a.repeats or cfg["repeats"]) + 1)]
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
