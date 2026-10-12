"""Make a trimmed copy of a Met sample CSV that keeps only selected columns.

Columns come out in the order listed in COLUMNS. Values are copied exactly:
everything is read as text and nothing is filled in, so empty cells stay
empty and leading zeros etc. are kept.

Usage:
    python scripts/trim_sample.py data/met_sample_200.csv data/met_sample_200_trimmed.csv
"""
import argparse
import hashlib

import pandas as pd

COLUMNS = [
    "Object Date",
    "Title",
    "Artist Display Name",
    "Object Number",
    "Link Resource",
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source")
    p.add_argument("output")
    args = p.parse_args()

    df = pd.read_csv(args.source, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise SystemExit(f"missing columns in {args.source}: {missing}")
    df[COLUMNS].to_csv(args.output, index=False)

    print(f"source: {args.source} ({len(df)} rows, sha256 {sha256(args.source)})")
    print(f"output: {args.output} ({len(df)} rows, sha256 {sha256(args.output)})")


if __name__ == "__main__":
    main()
