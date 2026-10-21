"""Compare a model's output TSV with the input, by Object Number.

Prints how many input rows are missing, how many output rows aren't in the
input at all (invented), and how many kept rows had a title changed, with
examples of each.

Usage:
    python scripts/compare_tsv.py data/met_random_300.tsv path/to/output.tsv
"""
import csv
import sys


def load(path):
    """Return a list of (object number, title) rows."""
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    norm = [h.strip().strip('"').lower().replace("_", " ") for h in rows[0]]
    num, title = norm.index("object number"), norm.index("title")
    return [(r[num], r[title]) for r in rows[1:] if len(r) > max(num, title)]


def main():
    src, out = load(sys.argv[1]), load(sys.argv[2])
    src_title = dict(src)
    out_nums = {n for n, _ in out}
    invented = [(n, t) for n, t in out if n not in src_title]
    missing = [n for n, _ in src if n not in out_nums]
    changed = [(n, t) for n, t in out if n in src_title and t != src_title[n]]
    print(f"input rows: {len(src)}   output rows: {len(out)}")
    print(f"input rows missing from output: {len(missing)}")
    print(f"output rows not in input (invented): {len(invented)}")
    for n, t in invented[:15]:
        print(f"    {n or '(no number)'}\t{t}")
    print(f"kept rows whose title changed: {len(changed)}")
    for n, t in changed[:10]:
        print(f"    {n}\t{src_title[n]!r} -> {t!r}")


if __name__ == "__main__":
    main()
