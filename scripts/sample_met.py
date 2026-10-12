"""Draw a reproducible, representative sample of rows from the Met Museum
Open Access dataset (MetObjects.csv).

Sampling is stratified by Department with proportional allocation (largest
remainder method), then rows are drawn at random within each department.
This keeps the department mix matching the full collection while staying
random within each stratum. Output rows are shuffled so departments are
interleaved, and all original columns/values are preserved verbatim.

Usage:
    python scripts/sample_met.py MetObjects.csv data/met_sample_200.csv [--n 200] [--seed 42]
"""
import argparse
import hashlib

import pandas as pd


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def allocate(counts, n):
    """Proportional allocation using the largest remainder method."""
    total = counts.sum()
    quotas = counts * n / total
    alloc = quotas.astype(int)
    remainder = n - alloc.sum()
    order = (quotas - alloc).sort_values(ascending=False).index
    alloc[order[:remainder]] += 1
    return alloc


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source")
    p.add_argument("output")
    p.add_argument("--n", type=int, default=200)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    df = pd.read_csv(args.source, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    alloc = allocate(df["Department"].value_counts(), args.n)

    parts = [
        df[df["Department"] == dept].sample(k, random_state=args.seed)
        for dept, k in alloc.items()
        if k > 0
    ]
    sample = pd.concat(parts).sample(frac=1, random_state=args.seed)
    sample.to_csv(args.output, index=False)

    print(f"source: {args.source} ({len(df)} rows, sha256 {sha256(args.source)})")
    print(f"output: {args.output} ({len(sample)} rows, sha256 {sha256(args.output)})")
    print(alloc[alloc > 0].to_string())


if __name__ == "__main__":
    main()
