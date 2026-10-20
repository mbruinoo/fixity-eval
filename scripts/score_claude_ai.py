"""Score the claude.ai check (decision record 24) with stage 1's scorer.

claude.ai's conversations are exported by hand (transcript.txt, a plain-text
copy), not saved call by call, so each session is scored from:
  - output_files/, the files the session produced, if any; else
  - the largest table in its replies (hallu_score's rule for a table in a
    reply), read from transcript.txt up to the debrief.
No tool calls are known, so no checksum counts as computed by a tool here;
whether code ran is judged from the transcript by the research coordinator.

Usage:
    python scripts/score_claude_ai.py experiments/claude-ai-check
writes <dir>/hallucination_scores.json and <dir>/changes.csv.
"""
import json
import pathlib
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import hallu_score as H  # noqa: E402

INPUT = pathlib.Path(__file__).parent.parent / "data" / "met_inventory_f.tsv"
DEBRIEF = "Thank you, that’s the end of the task"  # debrief_v4_claude_ai.txt's first words


def replies(transcript):
    """The conversation before the debrief. A plain-text copy loses the code
    fences that separate tables, so each run of consecutive tab-separated
    lines is fenced as its own block: two tables (or a table and the lines
    around it) aren't read as one."""
    text = transcript.read_text(encoding="utf-8").split(DEBRIEF)[0]
    out, in_table = [], False
    for ln in text.splitlines():
        if ("\t" in ln) != in_table:
            out.append("```")
            in_table = not in_table
        out.append(ln)
    return "\n".join(out) + "\n"


def main():
    root = pathlib.Path(sys.argv[1])
    report = []
    for d in sorted(p for p in root.iterdir() if p.is_dir() and (p / "transcript.txt").exists()):
        with tempfile.TemporaryDirectory() as tmp:
            run = pathlib.Path(tmp) / d.name
            run.mkdir()
            (run / "response.md").write_text(replies(d / "transcript.txt"), encoding="utf-8")
            if (d / "output_files").is_dir():
                shutil.copytree(d / "output_files", run / "output_files")
            res = H.score_run(run, INPUT, events=[])
        res["condition"] = {"base": "claude-ai-base", "tools": "claude-ai-fix-tools-loaded"}.get(
            d.name.split("-")[0], "claude-ai-fix")
        report.append(res)
        print(json.dumps({k: v for k, v in res.items() if k not in ("examples", "columns_found", "changes")},
                         ensure_ascii=False))
    H.write_changes(root / "changes.csv", report)
    for r in report:
        r.pop("changes", None)
    (root / "hallucination_scores.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
