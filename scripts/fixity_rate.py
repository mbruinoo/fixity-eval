"""Recompute the fixity error rate from saved change records, with any weights.

hallu_score.py saves every difference it finds to <experiment>/changes.csv
(tier, characters lost, characters fabricated, input and output text). This
script reweights those records without re-running anything.

Tier 1 (content loss or fabrication) always weighs 1. --w2 and --w3 say how
bad a Tier 2 (slight loss, e.g. accents) or Tier 3 (reformat only) character
is compared with a Tier 1 one, from 0 to 1. The rate is bounded 0-1; see
hallu_score.fixity_error_rate. Links are saved but not graded unless
--include-links is given.

Usage:
    python scripts/fixity_rate.py experiments/spike-07 [--w2 0.25] [--w3 0] [--include-links]
"""
import argparse
import csv
import json
import pathlib
import re
import sys
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from hallu_score import ALL_COLUMNS, CHAR_COLUMNS, fixity_error_rate  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("experiment")
    ap.add_argument("--w2", type=float, default=0.25)
    ap.add_argument("--w3", type=float, default=0.0)
    ap.add_argument("--include-links", action="store_true",
                    help="also grade Link Resource (left out by default)")
    a = ap.parse_args()
    if not (0 <= a.w2 <= 1 and 0 <= a.w3 <= 1):
        sys.exit("weights must be between 0 and 1 (relative to Tier 1)")
    root = pathlib.Path(a.experiment)
    runs = {r["run"]: r for r in json.loads((root / "hallucination_scores.json").read_text()) if "input_chars" in r}
    changes = defaultdict(list)
    for c in csv.DictReader(open(root / "changes.csv", encoding="utf-8")):
        # an unverified cell in an added column has no tier and is never counted
        changes[c["run"]].append({"column": c["column"], "kind": c.get("kind", ""),
                                  "tier": int(c["tier"]) if c["tier"] else None,
                                  "lost_chars": int(c["lost_chars"]), "fabricated_chars": int(c["fabricated_chars"])})
    by_cond = defaultdict(list)
    columns = ALL_COLUMNS if a.include_links else CHAR_COLUMNS
    print(f"weights: Tier 1 = 1, Tier 2 = {a.w2}, Tier 3 = {a.w3}; columns: {', '.join(columns)}")
    for name, r in runs.items():
        input_chars = sum(r["input_chars_by_column"][c] for c in columns)
        rate = fixity_error_rate(changes[name], input_chars, a.w2, a.w3, columns)
        by_cond[re.sub(r"-r\d+$", "", name)].append(rate)
        print(f"  {name:28} {rate:.4f}")
    print("mean by condition:")
    for cond, rates in by_cond.items():
        print(f"  {cond:28} {sum(rates) / len(rates):.4f}")


if __name__ == "__main__":
    main()
