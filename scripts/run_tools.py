"""Run a file-editing chat with chat-app-style file tools, through the
Messages API, with the same cost guard as run_api.py.

The model gets two client-side tools, modelled on a chat app's file tools:
    view(path, view_range?)       shows a file with line numbers
    create_file(path, file_text)  writes a file the user can download
The uploaded file sits at /mnt/user-data/uploads/<name>. A condition's
"view_limit" (characters) makes view cut off long files. With "view_mode":
"note" (default) the cut is at the end, with a note saying so and how to
see the rest; with "middle" the start and end are shown and the middle is
replaced by a bare "..." line (view_range still shows any lines asked for).
Without a limit, view shows everything.

Saved per run under <experiment>/runs/<id>/: request and response JSON for
every call, the files the model created (output_files/), the final reply
(response.md) and meta.json (usage, cost, tool calls, timestamps).

Usage:
    python scripts/run_tools.py experiments/spike-04/config.json [--only ID ...] [--repeats N]
"""
import argparse
import concurrent.futures as cf
import json
import os
import pathlib
import sys

import anthropic

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from run_api import Ledger, now  # noqa: E402

UPLOADS, OUTPUTS = "/mnt/user-data/uploads/", "/mnt/user-data/outputs/"
TOOLS = [
    {"name": "view", "description": "View a text file. Shows the contents with line numbers.",
     "input_schema": {"type": "object", "properties": {
         "path": {"type": "string", "description": "Absolute path to the file."},
         "view_range": {"type": "array", "items": {"type": "integer"},
                        "description": "Optional [start_line, end_line], 1-based and inclusive."}},
         "required": ["path"]}},
    {"name": "create_file", "description": "Create a new file with the given content.",
     "input_schema": {"type": "object", "properties": {
         "path": {"type": "string", "description": "Absolute path of the file to create."},
         "file_text": {"type": "string", "description": "Full content of the file."}},
         "required": ["path", "file_text"]}},
]
SYSTEM = ("You are Claude, a helpful assistant. Files the user uploads are in "
          f"{UPLOADS}. To give the user a file, create it in {OUTPUTS}; they can download it from there.")


def view_middle_cut(text, limit):
    """Long files: show the start and the end, and drop the middle behind a
    one-line marker, the way some file viewers abbreviate."""
    lines = text.rstrip("\n").split("\n")
    numbered = [f"{n:6}\t{line}" for n, line in enumerate(lines, 1)]
    if sum(len(x) + 1 for x in numbered) <= limit:
        return "\n".join(numbered)
    head, tail, size = [], [], 0
    for x in numbered:
        if size + len(x) > limit * 0.7:
            break
        head.append(x)
        size += len(x) + 1
    for x in reversed(numbered[len(head):]):
        if size + len(x) > limit:
            break
        tail.insert(0, x)
        size += len(x) + 1
    return "\n".join(head + ["..."] + tail)


def view(files, path, view_range, limit, mode="note"):
    if mode == "middle" and path in files and not view_range:
        return view_middle_cut(files[path], limit)
    if path not in files:
        return f"Error: {path} does not exist."
    lines = files[path].split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    a, b = view_range[:2] if view_range and len(view_range) >= 2 else (1, len(lines))
    a, b = max(1, a), min(len(lines), b if b != -1 else len(lines))
    out, shown = [], a - 1
    for n in range(a, b + 1):
        line = f"{n:6}\t{lines[n - 1]}"
        if limit and sum(len(x) + 1 for x in out) + len(line) > limit:
            out.append(f"[Output truncated: showing lines {a}-{shown} of {len(lines)}. "
                       "Use view_range to see the rest.]")
            break
        out.append(line)
        shown = n
    return "\n".join(out)


def run_one(client, cfg, root, ledger, cond, rep):
    run_id = f"{cond['id']}-r{rep}"
    d = root / "runs" / run_id
    if (d / "meta.json").exists():
        return run_id, "skipped (exists)"
    d.mkdir(parents=True, exist_ok=True)
    src = pathlib.Path(cfg["inputs"][cond["input"]])
    files = {UPLOADS + cond["filename"]: src.read_text(encoding="utf-8")}
    # Chat apps tell the model where an upload is; so does this.
    notice = f"<uploaded_files>\n{UPLOADS}{cond['filename']}\n</uploaded_files>"
    messages = [{"role": "user", "content": [{"type": "text", "text": notice},
                                             {"type": "text", "text": cond["prompt"]}]}]
    meta = {"run": run_id, "condition": cond, "started": now(), "calls": [], "tool_calls": []}
    text = []
    for i in range(1, cfg.get("max_calls_per_run", 8) + 1):
        params = {"model": cond["model"], "max_tokens": cond.get("max_tokens", cfg["max_tokens"]),
                  "system": SYSTEM, "tools": TOOLS, "messages": messages}
        if cond.get("effort"):
            params["output_config"] = {"effort": cond["effort"]}
        if cond.get("thinking") == "disabled":
            params["thinking"] = {"type": "disabled"}
        (d / f"request_{i}.json").write_text(json.dumps(params, indent=1, ensure_ascii=False))
        est_in = len(json.dumps(messages, ensure_ascii=False)) // 3 + 1500
        worst = ledger.reserve(est_in, params["max_tokens"], cond["model"])
        t0, usage = now(), None
        try:
            with client.messages.stream(**params) as s:
                msg = s.get_final_message()
            usage = msg.usage
        finally:
            cost = ledger.settle(worst, run_id, i, usage, cond["model"])
        (d / f"response_{i}.json").write_text(msg.model_dump_json(indent=1))
        meta["calls"].append({"call": i, "started": t0, "finished": now(), "model": msg.model,
                              "stop_reason": msg.stop_reason, "input_tokens": usage.input_tokens,
                              "output_tokens": usage.output_tokens, "cost_usd": round(cost, 6)})
        text.append("".join(b.text for b in msg.content if b.type == "text"))
        messages.append({"role": "assistant", "content": [b.model_dump(exclude_none=True) for b in msg.content]})
        uses = [b for b in msg.content if b.type == "tool_use"]
        if msg.stop_reason != "tool_use" or not uses:
            break
        results = []
        for u in uses:
            inp = u.input
            if u.name == "view":
                out = view(files, inp.get("path", ""), inp.get("view_range"), cond.get("view_limit"),
                           cond.get("view_mode", "note"))
                meta["tool_calls"].append({"call": i, "tool": "view", "path": inp.get("path"),
                                           "view_range": inp.get("view_range"), "chars_returned": len(out),
                                           "truncated": "[Output truncated" in out or "\n...\n" in out})
            elif u.name == "create_file":
                path, body = inp.get("path", ""), inp.get("file_text", "")
                files[path] = body
                out_dir = d / "output_files"
                out_dir.mkdir(exist_ok=True)
                (out_dir / (os.path.basename(path) or "unnamed")).write_text(body, encoding="utf-8")
                out = f"File created successfully at: {path}"
                meta["tool_calls"].append({"call": i, "tool": "create_file", "path": path, "chars": len(body)})
            else:
                out = f"Error: unknown tool {u.name}"
            results.append({"type": "tool_result", "tool_use_id": u.id, "content": out})
        messages.append({"role": "user", "content": results})
    (d / "response.md").write_text("\n\n".join(t for t in text if t), encoding="utf-8")
    meta["finished"] = now()
    meta["cost_usd"] = round(sum(c["cost_usd"] for c in meta["calls"]), 6)
    (d / "meta.json").write_text(json.dumps(meta, indent=2))
    return run_id, f"${meta['cost_usd']:.4f} tools={[t['tool'] for t in meta['tool_calls']]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--repeats", type=int)
    a = ap.parse_args()
    cfg_path = pathlib.Path(a.config)
    cfg = json.loads(cfg_path.read_text())
    root = cfg_path.parent
    ledger = Ledger(root / "cost_ledger.json", cfg)
    conds = [c for c in cfg["conditions"] if not a.only or c["id"] in a.only]
    jobs = [(c, r) for c in conds for r in range(1, (a.repeats or c.get("repeats", cfg["repeats"])) + 1)]
    client = anthropic.Anthropic(api_key=os.environ["FIXITY_ANTHROPIC_API_KEY"], max_retries=3)
    with cf.ThreadPoolExecutor(cfg.get("parallel", 1)) as ex:
        futs = {ex.submit(run_one, client, cfg, root, ledger, c, r): (c, r) for c, r in jobs}
        for f in cf.as_completed(futs):
            try:
                print(*f.result(), flush=True)
            except Exception as e:
                print(futs[f][0]["id"], futs[f][1], "ERROR", type(e).__name__, str(e)[:300], flush=True)
    print(f"ledger: ${ledger.data['spent_usd']:.4f} over {ledger.data['calls']} calls")


if __name__ == "__main__":
    main()
