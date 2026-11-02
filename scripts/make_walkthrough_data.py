"""The data behind the scroll-story walkthrough: one row per session, Claude
Haiku 4.5 with the plain request and with the fixity line, in stage 1's test
setting (the 20 tested sessions per request, as pre-registered) and in the
claude.ai check (session-1 to -5 and base-1 to -5). Read from the reviewed
scores; nothing is recomputed.

Columns: session, setting, request, error_rate (0-1, blank where no sheet came
back), error_pct (as shown), checksum ("real": a checksum of the upload
computed by a tool; "made up": invented or a placeholder; "none").

Usage:
    python scripts/make_walkthrough_data.py analysis/walkthrough/fixity_sessions.csv
"""
import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent.parent


def main():
    s1 = {r["run"]: r for r in json.loads((ROOT / "experiments/stage-1/hallucination_scores_reviewed.json").read_text())}
    f1 = {r["run"]: r for r in json.loads((ROOT / "experiments/stage-1/fixity_eval.json").read_text())}
    ca = {r["run"]: r for r in json.loads((ROOT / "experiments/claude-ai-check/hallucination_scores_reviewed.json").read_text())}
    rows = []
    for run, r in s1.items():
        cond = re.sub(r"-r\d+$", "", run)
        if cond not in ("base", "fix") or r.get("outcome") == "setup_fault":  # replaced sessions are left out
            continue
        f = f1.get(run, {})
        invented = (f.get("checksum_provenance") or {}).get("invented", 0) or f.get("checksums_malformed")
        ck = "real" if f.get("input_checksum_computed") else ("made up" if invented else "none")
        rows.append(("stage-1/" + run, "Test setting", cond == "fix", r, ck))
    for run, r in ca.items():
        if re.fullmatch(r"(base|session)-\d", run):
            fix = run.startswith("session")
            rows.append(("claude-ai-check/" + run, "claude.ai", fix, r, "made up" if fix else "none"))
    rows.sort(key=lambda t: (t[1] != "Test setting", t[2], int(re.findall(r"\d+", t[0])[-1])))
    with open(sys.argv[1], "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["session", "setting", "request", "error_rate", "error_pct", "checksum"])
        for sid, setting, fix, r, ck in rows:
            rate = r.get("fixity_error_rate") if r.get("outcome") == "sheet" else None
            w.writerow([sid, setting, "With the fixity line" if fix else "Without the fixity line",
                        "" if rate is None else f"{rate:.4f}", "No sheet" if rate is None else f"{rate * 100:.1f}%", ck])


if __name__ == "__main__":
    main()
