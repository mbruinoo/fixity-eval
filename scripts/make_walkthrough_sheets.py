"""Each scored sheet in the walkthrough, lined up with the original file, for
the side-by-side view (original on the left, what came back on the right).

The sheet is the one the scorer graded (hallu_score.score_run): the delivered
file and parse named in the reviewed scores, or, for claude.ai, the largest
table in the replies (score_claude_ai.replies). Cells are as delivered; nothing
is cleaned.

Rows are lined up for display only, not for scoring: by link, then by object
number (the scorer's keys), then by a link or object number found in any cell,
so a row shifted one column still sits beside its original. Original rows with
no partner come at their place in the original order, with an empty right side;
rows that match nothing get an empty left side.

Columns: session ("original" for the input file), pair (0 = header), row (the
original row it lines up with, 1-100, or blank), cells (JSON list), map (header
only: for each output column, the original column it was graded as, or "").

Usage:
    python scripts/make_walkthrough_sheets.py analysis/walkthrough/fixity_sessions.csv \
        analysis/walkthrough/fixity_sheets.csv
"""
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import hallu_score as H  # noqa: E402
import score_claude_ai as CA  # noqa: E402

ROOT = pathlib.Path(__file__).parent.parent
INPUT = ROOT / "data/met_inventory_f.tsv"


def scored_sheet(session):
    """The rows (header first) the scorer graded for this session."""
    setting, run = session.split("/")
    if setting == "stage-1":
        rec = {r["run"]: r for r in json.loads((ROOT / "experiments/stage-1/hallucination_scores_reviewed.json").read_text())}[run]
        path = ROOT / "experiments/stage-1/runs" / run / "output_files" / rec["result_file"]
        return dict(H.parse_sheet(path))[rec["parse"]]
    d = ROOT / "experiments/claude-ai-check" / run
    if (d / "output_files").is_dir():
        raise SystemExit(f"{session}: delivered files; this script reads only tables in replies for claude.ai")
    return H.table_from_text(CA.replies(CA.transcript(d)))


def line_up(rows_in, rows):
    header, body = rows[0], [r for r in rows[1:] if any(c.strip() for c in r)]
    cols = H.columns(header)
    get = lambda r, c: r[cols[c]] if cols[c] is not None and cols[c] < len(r) else None
    by_link = {H.key_link(r[3]): i for i, r in enumerate(rows_in)}
    by_num = {H.key_num(r[2]): i for i, r in enumerate(rows_in)}
    used, pairs = set(), []
    for r in body:
        i = by_link.get(H.key_link(get(r, "Link Resource")))
        if i is None:
            i = by_num.get(H.key_num(get(r, "Object Number") or ""))
        if i is None:  # anywhere in the row (a row shifted one column)
            i = next((by_link.get(H.key_link(v)) for v in r if by_link.get(H.key_link(v)) is not None), None)
        if i is None:
            i = next((by_num.get(H.key_num(v)) for v in r if v.strip() and by_num.get(H.key_num(v)) is not None), None)
        if i in used:
            i = None
        if i is not None:
            used.add(i)
        pairs.append((i, r))
    out, done = [], set()
    for i, r in pairs:
        if i is not None:
            for k in range(i):  # originals with no partner, in their place
                if k not in used and k not in done:
                    out.append((k, None))
                    done.add(k)
        out.append((i, r))
    out += [(k, None) for k in range(len(rows_in)) if k not in used and k not in done]
    mapping = {v: c for c, v in cols.items() if v is not None}
    return header, [mapping.get(j, "") for j in range(len(header))], out


def main():
    h_in, rows_in = H.read_input(INPUT)
    sessions = [r["session"] for r in csv.DictReader(open(sys.argv[1], encoding="utf-8")) if r["error_rate"] != ""]
    with open(sys.argv[2], "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["session", "pair", "row", "cells", "map"])
        w.writerow(["original", 0, "", json.dumps(h_in, ensure_ascii=False), ""])
        for i, r in enumerate(rows_in, 1):
            w.writerow(["original", i, i, json.dumps(r, ensure_ascii=False), ""])
        for s in sessions:
            header, mapping, pairs = line_up(rows_in, scored_sheet(s))
            w.writerow([s, 0, "", json.dumps(header, ensure_ascii=False), json.dumps(mapping)])
            for n, (i, r) in enumerate(pairs, 1):
                w.writerow([s, n, "" if i is None else i + 1, "" if r is None else json.dumps(r, ensure_ascii=False), ""])


if __name__ == "__main__":
    main()
