"""Run each prompt in a fresh headless Claude Code session and record the results.

Each run gets its own random folder outside the repo (no git history, no notes,
nothing that hints at what is being tested). When the session finishes, the
whole folder and the full transcript are copied into the experiment directory.

Two modes, set by "mode" in the config:
- "agent" (default): the folder holds only the input spreadsheet under a
  neutral name, the model has Claude Code's normal tools, and it is sent the
  prompt plus one line naming the file.
- "chat": no tools, no system prompt, no skills or MCP servers. The model is
  sent the prompt, a blank line, then the spreadsheet's text, and its reply
  is saved as response.md.

"repeats" in the config runs every prompt that many times (ids get -r1, -r2...).

Usage:
    python scripts/run_spike.py experiments/spike-01/config.json
"""
import concurrent.futures
import datetime
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def parse_line(line):
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return {}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def run_one(cfg, run, out_root):
    out = out_root / run["id"]
    if out.exists():
        raise SystemExit(f"{out} already exists; refusing to overwrite")
    out.mkdir(parents=True)

    mode = cfg.get("mode", "agent")
    work = pathlib.Path(tempfile.mkdtemp(prefix="work-", dir=cfg["work_parent"]))
    cmd = [
        "claude", "-p", None,
        "--model", cfg["model"],
        "--effort", cfg["effort"],
        "--output-format", "stream-json",
        "--verbose",
    ]
    if mode == "agent":
        shutil.copyfile(cfg["input"], work / cfg["input_name"])
        message = f"{run['prompt']}\n\nThe spreadsheet is {cfg['input_name']}."
        cmd += ["--permission-mode", "bypassPermissions"]
    elif mode == "chat":
        text = pathlib.Path(cfg["input"]).read_text(encoding="utf-8")
        message = f"{run['prompt']}\n\n{text}"
        cmd += ["--tools", "", "--system-prompt", "", "--strict-mcp-config",
                "--disable-slash-commands"]
    else:
        raise SystemExit(f"unknown mode {mode!r}")
    cmd[2] = message
    meta = {
        "id": run["id"],
        "mode": mode,
        "prompt": run["prompt"],
        "message_sent": message,
        "model": cfg["model"],
        "effort": cfg["effort"],
        "claude_cli_version": subprocess.run(
            ["claude", "--version"], capture_output=True, text=True
        ).stdout.strip(),
        "input": cfg["input"],
        "input_name": cfg.get("input_name"),
        "input_sha256": sha256(cfg["input"]),
        "started": now(),
    }
    with open(out / "transcript.jsonl", "w") as t:
        proc = subprocess.run(
            cmd, cwd=work, stdin=subprocess.DEVNULL, stdout=t,
            stderr=subprocess.STDOUT, timeout=cfg.get("timeout_s", 1800),
        )
    meta["finished"] = now()
    meta["exit_code"] = proc.returncode

    shutil.copytree(work, out / "workdir")
    shutil.rmtree(work)
    # Claude Code also gives each session a scratchpad outside its folder,
    # named after the folder. Models put scripts and backups there.
    mangled = str(work).replace("/", "-").replace("_", "-")
    for pad in pathlib.Path("/tmp/claude-0").glob(f"{mangled}/*/scratchpad"):
        shutil.copytree(pad, out / "scratchpad", dirs_exist_ok=True)
    meta["workdir_files"] = {
        str(p.relative_to(out / "workdir")): sha256(p)
        for p in sorted((out / "workdir").rglob("*")) if p.is_file()
    }
    meta["models_served"] = sorted({
        e["message"]["model"]
        for e in map(parse_line, (out / "transcript.jsonl").read_text().splitlines())
        if e.get("type") == "assistant"
    })
    if mode == "chat":
        results = [
            e for e in map(parse_line, (out / "transcript.jsonl").read_text().splitlines())
            if e.get("type") == "result"
        ]
        if results:
            (out / "response.md").write_text(results[-1].get("result") or "", encoding="utf-8")
            meta["usage"] = results[-1].get("usage")
            meta["cost_usd"] = results[-1].get("total_cost_usd")
    (out / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    return run["id"], proc.returncode


def main():
    cfg_path = pathlib.Path(sys.argv[1])
    cfg = json.loads(cfg_path.read_text())
    out_root = cfg_path.parent / "runs"
    repeats = cfg.get("repeats", 1)
    runs = [
        {**r, "id": f"{r['id']}-r{k}" if repeats > 1 else r["id"]}
        for r in cfg["runs"] for k in range(1, repeats + 1)
    ]
    workers = min(len(runs), cfg.get("parallel", 4))
    with concurrent.futures.ThreadPoolExecutor(workers) as ex:
        for run_id, code in ex.map(lambda r: run_one(cfg, r, out_root), runs):
            print(f"{run_id}: exit {code}")


if __name__ == "__main__":
    main()
