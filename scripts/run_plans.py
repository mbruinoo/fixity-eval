"""Run the checksum-plans study (decision record 26): each session gets the
request, then the follow-up, then the debrief, as three turns of one
conversation, with no tools and no system prompt.

Sessions advance in lockstep: each turn goes out for every session as one
Message Batches request (half price), with the cost guard (run_api.Ledger)
reserving each call's worst case before the batch is sent. A turn's
"max_tokens" can be set per model ("max_tokens_by_model": {model: {turn:
n}}): the newest models think at length on their defaults. Every request,
response and reply is saved under <experiment>/runs/<model key>-r<N>/:
request_<turn>.json, response_<turn>.json, reply_<turn>.md, and meta.json
(model served, stop reasons, usage, cost, the SHA-256 of each prompt file).
A failed or refused call is saved as it came back; the conversation goes on
with the next turn only if the call returned a message.

Usage:
    python scripts/run_plans.py experiments/checksum-plans/config.json
"""
import hashlib
import json
import os
import pathlib
import sys
import time

import anthropic

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from run_api import Ledger, now  # noqa: E402

REPO = pathlib.Path(__file__).parent.parent


def text_of(msg):
    return "".join(b.text for b in msg.content if b.type == "text")


def run_batch(client, requests, poll=15):
    """Send {custom_id: params} as one batch; return {custom_id: result}."""
    b = client.messages.batches.create(requests=[{"custom_id": k, "params": p} for k, p in requests.items()])
    print(f"[batch {b.id}] {len(requests)} requests submitted", flush=True)
    while b.processing_status != "ended":
        time.sleep(poll)
        b = client.messages.batches.retrieve(b.id)
    return b, {r.custom_id: r.result for r in client.messages.batches.results(b.id)}


def main(cfg_path, client=None, poll=15):
    cfg_path = pathlib.Path(cfg_path)
    cfg = json.loads(cfg_path.read_text())
    root = cfg_path.parent
    runs = root / "runs"
    if runs.exists() and any(runs.iterdir()):
        sys.exit(f"{runs} already holds runs; not starting")
    prompts = [(t, (REPO / t["prompt_file"]).read_text(encoding="utf-8").strip()) for t in cfg["turns"]]
    ledger = Ledger(root / "cost_ledger.json", cfg)
    client = client or anthropic.Anthropic(api_key=os.environ["FIXITY_ANTHROPIC_API_KEY"], max_retries=3)
    sessions = {}
    # "variants": {name: prompt file} swaps the first turn's prompt, one set of
    # sessions per variant (the 2x2 study, decision record 30).
    variants = cfg.get("variants") or {None: cfg["turns"][0]["prompt_file"]}
    for v, first in variants.items():
        files = [first] + [t["prompt_file"] for t in cfg["turns"][1:]]
        for key, model in cfg["models"].items():
            for n in range(1, cfg["repeats"] + 1):
                d = runs / (f"{v}-{key}-r{n}" if v else f"{key}-r{n}")
                d.mkdir(parents=True)
                sessions[d.name] = {"dir": d, "model": model, "messages": [], "alive": True,
                                    "prompts": [(REPO / f).read_text(encoding="utf-8").strip() for f in files],
                                    "meta": {"run": d.name, "model": model, "variant": v, "started": now(),
                                             "calls": [], "prompt_files": files,
                                             "prompt_sha256": {t["name"]: hashlib.sha256((REPO / f).read_bytes())
                                                               .hexdigest() for t, f in zip(cfg["turns"], files)}}}
    batch_log = []
    for i, (turn, prompt) in enumerate(prompts, 1):
        todo, worst = {}, {}
        for sid, s in sessions.items():
            if s["alive"]:
                msgs = s["messages"] + [{"role": "user", "content": s["prompts"][i - 1]}]
                cap = cfg.get("max_tokens_by_model", {}).get(s["model"], {}).get(turn["name"], turn["max_tokens"])
                todo[sid] = {"model": s["model"], "max_tokens": cap, "messages": msgs}
        if not todo:
            break
        # The whole turn's worst case must fit under the guard before any of it is sent.
        est = {sid: len(json.dumps(p["messages"], ensure_ascii=False)) // 3 + 100 for sid, p in todo.items()}
        need = sum((est[sid] * ledger.prices(p["model"])[0] + p["max_tokens"] * ledger.prices(p["model"])[1])
                   * ledger.price_factor for sid, p in todo.items())
        if ledger.data["spent_usd"] + need > ledger.budget:
            print(f"cost guard: spent ${ledger.data['spent_usd']:.4f} + this turn's worst case ${need:.4f} "
                  f"> ${ledger.budget}; stopped before turn {turn['name']!r}, nothing sent", flush=True)
            break
        for sid, p in todo.items():
            s = sessions[sid]
            s["messages"] = p["messages"]
            worst[sid] = ledger.reserve(est[sid], p["max_tokens"], p["model"])
            (s["dir"] / f"request_{i}.json").write_text(json.dumps(p, indent=1, ensure_ascii=False))
        b, results = run_batch(client, todo, poll)
        batch_log.append({"id": b.id, "turn": turn["name"], "requests": len(todo), "ended": now()})
        (root / "batches.json").write_text(json.dumps(batch_log, indent=1))
        for sid in todo:
            s, r = sessions[sid], results.get(sid)
            call = {"turn": turn["name"], "finished": now()}
            if r is not None and r.type == "succeeded":
                msg = r.message
                call.update({"model_served": msg.model, "stop_reason": msg.stop_reason,
                             "usage": msg.usage.model_dump(),
                             "cost_usd": ledger.settle(worst[sid], sid, turn["name"], msg.usage, s["model"])})
                (s["dir"] / f"response_{i}.json").write_text(msg.model_dump_json(indent=1))
                (s["dir"] / f"reply_{i}.md").write_text(text_of(msg) + "\n", encoding="utf-8")
                # Every block goes back unchanged (thinking blocks included): the history is append-only.
                s["messages"].append({"role": "assistant",
                                      "content": [blk.model_dump(exclude_none=True) for blk in msg.content]})
            else:
                ledger.settle(worst[sid], sid, turn["name"], None, s["model"])
                call["error"] = f"{getattr(r, 'type', 'missing')}: {getattr(r, 'error', '')}"
                s["alive"] = False
            s["meta"]["calls"].append(call)
            s["meta"]["cost_usd"] = round(sum(c.get("cost_usd", 0) for c in s["meta"]["calls"]), 6)
            (s["dir"] / "meta.json").write_text(json.dumps(s["meta"], indent=1, ensure_ascii=False, default=str))
    print(f"ledger: ${ledger.data['spent_usd']:.4f} over {ledger.data['calls']} calls")


if __name__ == "__main__":
    main(sys.argv[1])
