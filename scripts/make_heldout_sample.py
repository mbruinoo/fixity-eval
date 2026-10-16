"""Canaries and a held-out inventory.

1. spec/canaries.json: the significant-property rules (spec/
   met_inventory_significant_properties.md) as detection patterns, with the
   rows that carry each in every inventory file in data/.
2. data/met_inventory_f.tsv: a new 100-row sample from the Met Open Access
   CSV, stratified so each canary is well represented, with no object from
   any earlier file. It is held out: no prompt wording is tuned on it.
   Its SHA-256 is recorded in spec/canaries.json.

    python scripts/make_heldout_sample.py MetObjects.csv            # writes both
    python scripts/make_heldout_sample.py MetObjects.csv --stats    # convention counts only
"""
import argparse
import collections
import csv
import glob
import hashlib
import json
import pathlib
import random
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
NONLATIN = re.compile(r"[Ͱ-ϿЀ-ӿ֐-ۿ฀-๿぀-ヿ㐀-鿿가-힯]")
CANARIES = {
    "supplied_title": {"column": "Title", "rule": "title wholly in [ ]",
                       "test": lambda d, t, n: t.startswith("[") and t.endswith("]")},
    "original_script": {"column": "Title", "rule": "non-Latin script in the title (often 'original|English')",
                        "test": lambda d, t, n: bool(NONLATIN.search(t))},
    "date_question": {"column": "Object Date", "rule": "'(?)' or '?' in the date",
                      "test": lambda d, t, n: "?" in d},
    "date_probably_possibly": {"column": "Object Date", "rule": "'probably' or 'possibly' in the date",
                               "test": lambda d, t, n: bool(re.search(r"\b(probably|possibly)\b", d, re.I))},
    "date_qualifier": {"column": "Object Date", "rule": "a parenthetical in the date",
                       "test": lambda d, t, n: "(" in d or "[" in d},
    "blank_title": {"column": "Title", "rule": "title is blank",
                    "test": lambda d, t, n: not t.strip()},
    "embedded_quotes": {"column": "Title", "rule": "quotation marks inside the title",
                        "test": lambda d, t, n: '"' in t or "“" in t},
    "id_range": {"column": "Object Number", "rule": "range or list in the accession number",
                 "test": lambda d, t, n: bool(re.search(r"[–—]|, ", n))},
}
WANT = {"supplied_title": 12, "original_script": 12, "date_question": 10, "date_probably_possibly": 8,
        "date_qualifier": 10, "blank_title": 10, "embedded_quotes": 8, "id_range": 8}


def file_canaries(path):
    rows = list(csv.reader(open(path, encoding="utf-8"), delimiter="\t"))[1:]
    out = {}
    for k, c in CANARIES.items():
        out[k] = [r[2] for r in rows if len(r) >= 4 and c["test"](r[0], r[1], r[2])]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()
    csv.field_size_limit(10**9)
    taken = set()
    for f in glob.glob(str(ROOT / "data" / "met_*.tsv")):
        for r in list(csv.reader(open(f, encoding="utf-8"), delimiter="\t"))[1:]:
            if len(r) > 2:
                taken.add(r[2])
    pools = collections.defaultdict(list)
    counts = collections.Counter()
    for r in csv.DictReader(open(a.source, encoding="utf-8-sig")):
        row = (r["Object Date"].strip(), r["Title"].strip(), r["Object Number"].strip(), r["Link Resource"].strip())
        hits = [k for k, c in CANARIES.items() if c["test"](*row[:3])]
        counts.update(hits)
        counts["objects"] += 1
        if not row[2] or not row[3] or row[2] in taken:
            continue
        for k in hits:
            pools[k].append(row)
        if not hits:
            pools["plain"].append(row)
    if a.stats:
        print(dict(counts))
        return
    rng = random.Random(a.seed)
    rows, seen = [], set()
    for k, n in list(WANT.items()) + [("plain", 100 - sum(WANT.values()))]:
        cand = [r for r in rng.sample(pools[k], min(len(pools[k]), n * 5)) if r[2] not in seen][:n]
        seen.update(r[2] for r in cand)
        rows += cand
    rows.sort(key=lambda r: r[1])
    out = ROOT / "data" / "met_inventory_f.tsv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["Object Date", "Title", "Object Number", "Link Resource"])
        w.writerows(rows)
    spec = {"version": 1, "rules": {k: {"column": c["column"], "rule": c["rule"]} for k, c in CANARIES.items()},
            "dataset_counts": dict(counts), "files": {},
            "held_out": {"file": "data/met_inventory_f.tsv", "seed": a.seed,
                         "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
                         "note": "Held out: no prompt wording may be tuned on this file."}}
    for f in sorted(glob.glob(str(ROOT / "data" / "met_inventory_*.tsv"))):
        spec["files"][pathlib.Path(f).name] = file_canaries(f)
    (ROOT / "spec" / "canaries.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False))
    print(len(rows), "rows;", {k: len(v) for k, v in spec["files"]["met_inventory_f.tsv"].items()})


if __name__ == "__main__":
    main()
