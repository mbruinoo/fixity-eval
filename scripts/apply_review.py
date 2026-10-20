"""Apply the research coordinator's review of unverified added-column values
(decision record 03, c) to copies of an experiment's scores.

Reads <experiment>/review.json, changes.csv and hallucination_scores.json;
cells ruled "inaccurate" count as invented (Tier 1, every character), cells
ruled "accurate" are dropped, and each session's error rate is recomputed
with hallu_score.fixity_error_rate. review.json may also hold "outcomes":
the coordinator's ruling on what a session ended with (decision record 11),
e.g. a sample table in a reply that isn't the sheet; such a session has no
error rate and its changes are left out. Writes changes_reviewed.csv and
hallucination_scores_reviewed.json; the scorer's own files are unchanged.

Usage:
    python scripts/apply_review.py experiments/stage-1
    python scripts/analyze_stage1.py experiments/stage-1 --scores hallucination_scores_reviewed.json \
        --out stage1_results_reviewed.json
"""
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from hallu_score import fixity_error_rate  # noqa: E402


def ruling(row, rulings):
    for r in rulings:
        if r["run"] == row["run"] and r["column"] == row["column"] and \
                ("object_numbers" not in r or row["object_number"] in r["object_numbers"]):
            return r["ruling"]
    return None


def main():
    root = pathlib.Path(sys.argv[1])
    review = json.loads((root / "review.json").read_text())
    rulings = review["rulings"]
    outcomes = {o["run"]: o for o in review.get("outcomes", [])}
    rows = list(csv.DictReader(open(root / "changes.csv", encoding="utf-8")))
    out = []
    for row in rows:
        if row["run"] in outcomes:
            continue
        if row["kind"] == "extra_unverified":
            r = ruling(row, rulings)
            if r == "accurate":
                continue
            if r == "inaccurate":
                row = {**row, "kind": "extra_column", "tier": "1"}
        out.append(row)
    with open(root / "changes_reviewed.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(out)
    scores = json.loads((root / "hallucination_scores.json").read_text())
    for i, s in enumerate(scores):
        if s["run"] in outcomes:
            o = outcomes[s["run"]]
            scores[i] = {"run": s["run"], "output": f"{s['output']}, ruled {o['outcome']} by the coordinator",
                         "input_rows": s.get("input_rows"), "outcome": o["outcome"], "ruling": o["reason"],
                         **{k: s[k] for k in ("condition", "cost_usd", "calls", "user_turns") if k in s}}
            continue
        if "input_chars" not in s:
            continue
        ch = [{"column": c["column"], "kind": c["kind"], "tier": int(c["tier"]) if c["tier"] else None,
               "lost_chars": int(c["lost_chars"]), "fabricated_chars": int(c["fabricated_chars"])}
              for c in out if c["run"] == s["run"]]
        s["fixity_error_rate"] = fixity_error_rate(ch, s["input_chars"])
        s["added_cells_inaccurate"] = sum(1 for c in ch if c["kind"] == "extra_column")
        s["added_cells_unverified"] = sum(1 for c in ch if c["kind"] == "extra_unverified")
    (root / "hallucination_scores_reviewed.json").write_text(json.dumps(scores, indent=2, ensure_ascii=False) + "\n")
    print(f"{sum(1 for r in rows if r['kind'] == 'extra_unverified')} unverified cells; "
          f"{sum(1 for r in out if r['kind'] == 'extra_unverified')} left unverified after review")


if __name__ == "__main__":
    main()
