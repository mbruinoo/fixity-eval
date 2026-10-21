"""Send the debrief to a session the runner couldn't debrief (e.g. one
stopped by the cost guard, which run_tools.py doesn't debrief, so as not to
spend past it).

Takes the session's last saved request (the call that was never sent), adds
a sentence saying why the session was stopped and the condition's debrief,
alongside any pending tool results as run_tools.py does, and sends it once,
with tools switched off. Saves request_debrief.json, response_debrief.json
and debrief.md in the run folder, and adds the call to the experiment's
cost ledger. --guard is the most this one call may add to the ledger; it is
set by the repo author.

Usage:
    python scripts/send_debrief.py experiments/<name> <run id> --guard 0.10 \
        --note "We've had to stop the session here, ..."
"""
import argparse
import json
import os
import pathlib
import re
import sys

import anthropic

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from run_api import Ledger, now  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("experiment")
    ap.add_argument("run")
    ap.add_argument("--guard", type=float, required=True, help="most this call may add, in USD")
    ap.add_argument("--note", required=True, help="sentence put before the debrief")
    a = ap.parse_args()
    root = pathlib.Path(a.experiment)
    d = root / "runs" / a.run
    if (d / "debrief.md").exists():
        sys.exit(f"{a.run} already has a debrief")
    cfg = json.loads((root / "config.json").read_text())
    cond = next(c for c in cfg["conditions"] if re.sub(r"-r\d+$", "", a.run) == c["id"])
    ledger_path = root / "cost_ledger.json"
    spent = json.loads(ledger_path.read_text())["spent_usd"] if ledger_path.exists() else 0.0
    ledger = Ledger(ledger_path, {**cfg, "budget_stop_usd": spent + a.guard, "max_calls": 10**6})
    reqs = sorted(d.glob("request_[0-9]*.json"), key=lambda f: int(re.sub(r"\D", "", f.stem)))
    last = json.loads(reqs[-1].read_text())
    messages = last["messages"]
    note = a.note.strip() + " " + cond["debrief"]
    if messages[-1]["role"] == "user":  # stopped mid-tool-use: answer alongside the tool results
        if isinstance(messages[-1]["content"], str):
            messages[-1]["content"] = [{"type": "text", "text": messages[-1]["content"]}]
        messages[-1]["content"].append({"type": "text", "text": note})
    else:
        messages.append({"role": "user", "content": note})
    params = {"model": cond["model"], "max_tokens": 1000, "system": last["system"], "tools": last["tools"],
              "tool_choice": {"type": "none"}, "messages": messages}
    worst = ledger.reserve(len(json.dumps(messages, ensure_ascii=False)) // 3 + 1500, 1000, cond["model"])
    (d / "request_debrief.json").write_text(json.dumps(params, indent=1, ensure_ascii=False))
    client = anthropic.Anthropic(api_key=os.environ["FIXITY_ANTHROPIC_API_KEY"], max_retries=3)  # as run_tools.py
    try:
        msg = client.messages.create(**params)
    except anthropic.APIError as e:  # nothing was sent to the session: remove the unsent request
        (d / "request_debrief.json").unlink()
        sys.exit(f"{a.run}: not sent ({type(e).__name__}: {str(e)[:200]})")
    cost = ledger.settle(worst, a.run, "debrief", msg.usage, cond["model"])
    (d / "response_debrief.json").write_text(msg.model_dump_json(indent=1))
    reply = "".join(b.text for b in msg.content if b.type == "text")
    (d / "debrief.md").write_text(f"**Debrief sent:**\n\n{note}\n\n**Reply:**\n\n{reply}\n", encoding="utf-8")
    meta = json.loads((d / "meta.json").read_text())
    meta["calls"].append({"call": "debrief", "started": now(), "finished": now(), "model": msg.model,
                          "cost_usd": cost, "sent_by": "scripts/send_debrief.py"})
    meta["cost_usd"] = (meta.get("cost_usd") or 0) + cost
    meta["debrief_cut_short_note"] = True
    (d / "meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    print(f"[{a.run} debrief] ${cost:.4f}\n{reply}")


if __name__ == "__main__":
    main()
