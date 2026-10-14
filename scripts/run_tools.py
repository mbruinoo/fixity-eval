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

A condition's "followups" are sent, in order, once the model has delivered a
file or table and stopped (after any "nudges"); the earlier files move to
output_files_before_followup<N>/ so output_files/ holds the final answer.

With "bash": true the model also gets a bash_tool, like a chat app's. Its
commands run on this machine in a throwaway folder standing in for
/mnt/user-data (uploads/ holds the full file; paths are rewritten), with no
network (unshare -n), a 60-second limit and output cut at 30,000 characters.
Commands and outputs are logged to bash_log.md.

With "inline": "full" (or "middle") the file's text also goes into the first
message, in a <document> block, as a chat app can attach an uploaded file.

"system_file" puts a file (e.g. claude.ai's published system prompt) before
the file note; "failing_docs_tool": true adds a document connector whose
every call fails with the error a claude.ai session got (DOCS_ERROR).
"defer_tools": [names] lists those tools by name only in the system prompt;
the model must call tool_search to load them before they appear as tools.
"upload_notice": false leaves out the <uploaded_files> notice and the upload
folder from the system note (the file is still on disk for bash, and in the
message if "inline"). "connector_stubs": true adds CONNECTOR_STUBS, 24 inert
connector tools like a typical claude.ai account's.

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
import shutil
import subprocess
import sys
import tempfile

import anthropic

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from run_api import Ledger, has_table, now  # noqa: E402

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
BASH_TOOL = {"name": "bash_tool", "description": "Run a bash command in the container.",
             "input_schema": {"type": "object", "properties": {
                 "command": {"type": "string", "description": "Bash command to run."},
                 "description": {"type": "string", "description": "Why I'm running this command."}},
                 "required": ["command"]}}
BASH_OUTPUT_LIMIT = 30000


def run_bash(command, box):
    """Run a model's command in a throwaway folder that stands in for
    /mnt/user-data (paths are rewritten), with no network and a time limit."""
    cmd = command.replace("/mnt/user-data", str(box))
    try:
        p = subprocess.run(["unshare", "-n", "bash", "-c", cmd], cwd=box, capture_output=True, text=True,
                           timeout=60, env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(box), "LANG": "C.UTF-8"})
        out = (p.stdout + (("\n" + p.stderr) if p.stderr else "")).replace(str(box), "/mnt/user-data")
        out = out if out.strip() else f"(no output, exit code {p.returncode})"
    except subprocess.TimeoutExpired:
        out = "Error: command timed out after 60 seconds."
    if len(out) > BASH_OUTPUT_LIMIT:
        out = out[:BASH_OUTPUT_LIMIT] + f"\n[Output truncated: {len(out)} characters, showing the first {BASH_OUTPUT_LIMIT}.]"
    return out


# A document connector that always fails, with the error a claude.ai session
# got from its Claude Docs connector (experiments/claude-ai/haiku45-300b-r1).
DOCS_TOOL = {"name": "claude_docs_create", "description": "Claude Docs: Create doc, tab, or comment.",
             "input_schema": {"type": "object", "properties": {
                 "object": {"type": "string", "description": "What to create: doc, tab, comment or file."},
                 "payload": {"type": "object", "description": "Content: title, mime type, body."}},
                 "required": ["object"]}}
DOCS_ERROR = ('{"verdict":"deny","reason":"bad_request","detail":"container:required — a tab, its contents, a comment '
              'or an upload is addressed together with its doc: add container {\\"kind\\":\\"project\\",\\"id\\":'
              '\\"<doc uuid>\\"} — the doc\'s own id (from its link, or the read that listed its files), never a tab\'s '
              'or its contents\'; an id that IS the doc reads as ref {\\"object\\":\\"project\\",\\"id\\":\\"<doc uuid>'
              '\\"} with no container","data":{"code":"bad_request","problem":"required","at":["container"],'
              '"expected":{"kind":"project","id":"<doc uuid>"},"was":"intent_shape"}}')

def _stub(name, desc, props):
    return {"name": name, "description": desc, "input_schema": {"type": "object", "properties": {
        k: {"type": "string", "description": v} for k, v in props.items()}}}


# A chat app's connector tools (names and descriptions modelled on a typical
# claude.ai account with Gmail, Calendar, Drive, Slack and Claude Docs). They
# do nothing: every call returns CONNECTOR_STUB_RESULT.
CONNECTOR_STUBS = [
    _stub("gmail_search_threads", "Gmail: search email threads.", {"query": "Gmail search query"}),
    _stub("gmail_get_thread", "Gmail: read a thread.", {"thread_id": "Thread id"}),
    _stub("gmail_create_draft", "Gmail: create a draft email.", {"to": "Recipient", "subject": "Subject", "body": "Body"}),
    _stub("gmail_list_labels", "Gmail: list labels.", {}),
    _stub("gcal_list_events", "Google Calendar: list events.", {"time_min": "Start", "time_max": "End"}),
    _stub("gcal_create_event", "Google Calendar: create an event.", {"summary": "Title", "start": "Start", "end": "End"}),
    _stub("gcal_suggest_time", "Google Calendar: suggest a meeting time.", {"attendees": "Emails", "duration": "Minutes"}),
    _stub("gdrive_search_files", "Google Drive: search files.", {"query": "Search text"}),
    _stub("gdrive_read_file_content", "Google Drive: read a file's content.", {"file_id": "File id"}),
    _stub("gdrive_create_file", "Google Drive: create a file (Docs, Sheets or upload).", {"name": "File name", "mime_type": "MIME type", "content": "Content"}),
    _stub("gdrive_update_file", "Google Drive: update a file.", {"file_id": "File id", "content": "Content"}),
    _stub("gdrive_share_file", "Google Drive: share a file.", {"file_id": "File id", "email": "Email"}),
    _stub("slack_search_public", "Slack: search public channels.", {"query": "Search text"}),
    _stub("slack_send_message", "Slack: send a message.", {"channel": "Channel", "text": "Message"}),
    _stub("slack_read_channel", "Slack: read a channel.", {"channel": "Channel"}),
    _stub("slack_create_canvas", "Slack: create a canvas.", {"title": "Title", "content": "Markdown content"}),
    _stub("claude_docs_read", "Claude Docs: read a doc.", {"doc_id": "Doc id"}),
    _stub("claude_docs_query", "Claude Docs: list or search docs.", {"query": "Search text"}),
    _stub("claude_docs_update", "Claude Docs: edit a tab's contents.", {"doc_id": "Doc id", "content": "Content"}),
    _stub("claude_docs_export", "Claude Docs: export a doc.", {"doc_id": "Doc id", "format": "Format"}),
    _stub("web_search", "Search the web.", {"query": "Search query"}),
    _stub("web_fetch", "Fetch a web page.", {"url": "URL"}),
    _stub("conversation_search", "Search past chats.", {"query": "Search text"}),
    _stub("recent_chats", "List recent chats.", {}),
]
CONNECTOR_STUB_RESULT = "Error: this connector is not authorized for this conversation."

SEARCH_TOOL = {"name": "tool_search", "description": (
    "Load deferred tools so they can be called. Deferred tools are listed by name only; until loaded, "
    "their parameters are unknown and calling them fails. Pass the tool names to load."),
    "input_schema": {"type": "object", "properties": {
        "names": {"type": "array", "items": {"type": "string"}, "description": "Names of deferred tools to load."}},
        "required": ["names"]}}

SYSTEM = ("You are Claude, a helpful assistant. Files the user uploads are in "
          f"{UPLOADS}. To give the user a file, create it in {OUTPUTS}; they can download it from there.")
# Without the upload location: only where to put files for the user.
SYSTEM_NO_UPLOADS = f"You are Claude, a helpful assistant. To give the user a file, create it in {OUTPUTS}; they can download it from there."


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


def collect_outputs(box, d, stage=0, seen={}):
    """Copy what is in the sandbox's outputs/ folder (written by create_file
    or by bash) into the run's output_files/. Return the files that are new or
    changed since the last follow-up was sent (stage), so a file from before a
    follow-up doesn't count as the answer to it."""
    key = (str(d), stage)
    files = {str(f.relative_to(box / "outputs")): f.stat().st_mtime_ns
             for f in (box / "outputs").rglob("*") if f.is_file()}
    if key not in seen:
        seen[key] = files if stage else {}
    for rel in [r for r, t in files.items() if seen[key].get(r) != t]:
        out = d / "output_files" / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(box / "outputs" / rel, out)
    return [rel for rel, t in files.items() if seen[key].get(rel) != t]


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
    box = None
    if cond.get("bash"):
        box = pathlib.Path(tempfile.mkdtemp(prefix="fixity-box-"))
        (box / "uploads").mkdir()
        (box / "outputs").mkdir()
        shutil.copy(src, box / "uploads" / cond["filename"])
    # Chat apps tell the model where an upload is; so does this.
    notice = f"<uploaded_files>\n{UPLOADS}{cond['filename']}\n</uploaded_files>"
    content = [{"type": "text", "text": notice}] if cond.get("upload_notice", True) else []
    if cond.get("inline"):
        # The file's text in the first message, the way a chat app can attach
        # an uploaded text file ("full", or "middle": start and end with the
        # middle replaced by "...", as view_middle_cut does).
        body = files[UPLOADS + cond["filename"]]
        if cond["inline"] == "middle":
            body = "\n".join(x.split("\t", 1)[1] if x != "..." else x
                             for x in view_middle_cut(body, cond.get("view_limit", 16000)).split("\n"))
        content.insert(0, {"type": "text", "text": (
            f"<documents>\n<document index=\"1\">\n<source>{cond['filename']}</source>\n"
            f"<document_content>{body}</document_content>\n</document>\n</documents>")})
    content.append({"type": "text", "text": cond["prompt"]})
    messages = [{"role": "user", "content": content}]
    meta = {"run": run_id, "condition": cond, "started": now(), "calls": [], "tool_calls": []}
    text = []
    nudges = list(cond.get("nudges", []))
    followups, stage = list(cond.get("followups", [])), 0
    loaded = set()  # deferred tools the model has loaded
    for i in range(1, cfg.get("max_calls_per_run", 8) + 1):
        note = SYSTEM if cond.get("upload_notice", True) else SYSTEM_NO_UPLOADS
        system = note
        if cond.get("system_file"):  # e.g. claude.ai's published prompt, then the file note
            system = (pathlib.Path(cond["system_file"]).read_text(encoding="utf-8")
                      .replace("{{currentDateTime}}", cond.get("current_date", "")) + "\n\n" + note)
        extra = ([BASH_TOOL] if box else []) + ([DOCS_TOOL] if cond.get("failing_docs_tool") else [])
        if cond.get("defer_tools"):  # listed by name only, loaded on request with tool_search
            deferred = [t for t in extra if t["name"] in cond["defer_tools"]]
            system += ("\n\nThe following deferred tools are available. Their names are known but their schemas are "
                       "not loaded; call tool_search with their names before using them:\n"
                       + "\n".join(t["name"] for t in deferred))
            extra = [t for t in extra if t["name"] not in cond["defer_tools"] or t["name"] in loaded] + [SEARCH_TOOL]
        tools = TOOLS + extra + (CONNECTOR_STUBS if cond.get("connector_stubs") else [])
        params = {"model": cond["model"], "max_tokens": cond.get("max_tokens", cfg["max_tokens"]),
                  "system": system, "tools": tools, "messages": messages}
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
        if cfg.get("live"):  # one line per step, for watching a run as it happens
            say = text[-1].strip().replace("\n", " ")
            print(f"[{run_id} call {i}] ${cost:.3f} {msg.stop_reason}" + (f" | says: {say[:300]}" if say else ""), flush=True)
            for b in msg.content:
                if b.type == "tool_use":
                    arg = b.input.get("command") or b.input.get("path", "")
                    extra = f" range={b.input.get('view_range')}" if b.input.get("view_range") else ""
                    extra += f" ({len(b.input.get('file_text', ''))} chars)" if b.name == "create_file" else ""
                    print(f"    -> {b.name}: {str(arg)[:300]}{extra}", flush=True)
        messages.append({"role": "assistant", "content": [b.model_dump(exclude_none=True) for b in msg.content]})
        uses = [b for b in msg.content if b.type == "tool_use"]
        if msg.stop_reason != "tool_use" or not uses:
            # The reply asked a question instead of giving the file: answer as a
            # user would ("Yes, thank you", then "Yes, please continue").
            last = max([n for n, t in enumerate(meta["tool_calls"]) if t["tool"] == "-- followup --"], default=-1)
            made_file = any(t["tool"] == "create_file" for t in meta["tool_calls"][last + 1:])
            if box:  # files written with bash count too
                made_file = made_file or bool(collect_outputs(box, d, stage))
            if not made_file and not has_table(text[-1]) and nudges and msg.stop_reason == "end_turn":
                messages.append({"role": "user", "content": nudges.pop(0)})
                continue
            # The file (or table) arrived: send the next follow-up, if any. What
            # came before is kept in output_files_turn<N>/ so only the answer to
            # the last follow-up is scored.
            if followups and msg.stop_reason == "end_turn" and (made_file or has_table(text[-1])):
                stage += 1
                if box:  # snapshot: only files changed after this follow-up count as its answer
                    collect_outputs(box, d, stage)
                if (d / "output_files").exists():
                    (d / "output_files").rename(d / f"output_files_before_followup{stage}")
                (d / f"response_before_followup{stage}.md").write_text("\n\n".join(t for t in text if t), encoding="utf-8")
                meta.setdefault("followups_sent", []).append({"before_call": i + 1, "text": followups[0]})
                meta["tool_calls"].append({"call": i, "tool": "-- followup --"})
                if cfg.get("live"):
                    print(f"[{run_id}] >>> follow-up sent: {followups[0][:120]}", flush=True)
                messages.append({"role": "user", "content": followups.pop(0)})
                nudges = list(cond.get("nudges", []))
                continue
            break
        results = []
        for u in uses:
            inp = u.input
            if box and u.name == "view" and inp.get("path", "") not in files:
                f = pathlib.Path(inp.get("path", "").replace("/mnt/user-data", str(box)))
                if f.is_file():
                    files[inp["path"]] = f.read_text(encoding="utf-8", errors="replace")
            if u.name == "tool_search":
                names = [n for n in (inp.get("names") or []) if n in (cond.get("defer_tools") or [])]
                loaded.update(names)
                defs = [t for t in [BASH_TOOL, DOCS_TOOL] if t["name"] in names]
                out = ("Loaded: " + ", ".join(names) + "\n" + json.dumps(defs, ensure_ascii=False)) if names else \
                    "No matching deferred tools. Available: " + ", ".join(cond.get("defer_tools") or [])
                meta["tool_calls"].append({"call": i, "tool": "tool_search", "names": inp.get("names")})
                results.append({"type": "tool_result", "tool_use_id": u.id, "content": out})
                continue
            if u.name in (cond.get("defer_tools") or []) and u.name not in loaded:
                out = f"Error: {u.name} is a deferred tool and is not loaded. Call tool_search first."
                meta["tool_calls"].append({"call": i, "tool": u.name + " (not loaded)"})
                results.append({"type": "tool_result", "tool_use_id": u.id, "content": out, "is_error": True})
                continue
            if u.name in {t["name"] for t in CONNECTOR_STUBS}:
                out = CONNECTOR_STUB_RESULT
                meta["tool_calls"].append({"call": i, "tool": u.name, "input": inp})
                results.append({"type": "tool_result", "tool_use_id": u.id, "content": out, "is_error": True})
                continue
            if u.name == "claude_docs_create":
                out = DOCS_ERROR
                meta["tool_calls"].append({"call": i, "tool": "claude_docs_create", "input": inp})
                results.append({"type": "tool_result", "tool_use_id": u.id, "content": out, "is_error": True})
                continue
            if u.name == "bash_tool" and box:
                out = run_bash(inp.get("command", ""), box)
                meta["tool_calls"].append({"call": i, "tool": "bash_tool", "command": inp.get("command", ""),
                                           "chars_returned": len(out)})
                (d / "bash_log.md").open("a", encoding="utf-8").write(
                    f"## call {i}\n\n```\n{inp.get('command', '')}\n```\n\n```\n{out[:5000]}\n```\n\n")
            elif u.name == "view":
                out = view(files, inp.get("path", ""), inp.get("view_range"), cond.get("view_limit"),
                           cond.get("view_mode", "note"))
                meta["tool_calls"].append({"call": i, "tool": "view", "path": inp.get("path"),
                                           "view_range": inp.get("view_range"), "chars_returned": len(out),
                                           "truncated": "[Output truncated" in out or "\n...\n" in out})
            elif u.name == "create_file":
                path, body = inp.get("path", ""), inp.get("file_text", "")
                files[path] = body
                if box and path.startswith("/mnt/user-data/"):
                    f = pathlib.Path(path.replace("/mnt/user-data", str(box)))
                    f.parent.mkdir(parents=True, exist_ok=True)
                    f.write_text(body, encoding="utf-8")
                out_dir = d / "output_files"
                out_dir.mkdir(exist_ok=True)
                (out_dir / (os.path.basename(path) or "unnamed")).write_text(body, encoding="utf-8")
                out = f"File created successfully at: {path}"
                meta["tool_calls"].append({"call": i, "tool": "create_file", "path": path, "chars": len(body)})
            else:
                out = f"Error: unknown tool {u.name}"
            results.append({"type": "tool_result", "tool_use_id": u.id, "content": out})
        messages.append({"role": "user", "content": results})
    if box:
        collect_outputs(box, d, stage)
        shutil.rmtree(box, ignore_errors=True)
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
