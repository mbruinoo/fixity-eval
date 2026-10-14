"""Draw a "messy" inventory sample from the Met Open Access CSV: a larger
share of the content that typing out tends to damage, as in many real
archival inventories.

Strata (default for 100 rows): long titles (over 100 characters) 33,
non-Latin or bilingual titles 17, uncertain dates ("?", "probably",
"possibly") 10, object numbers with ranges or lists ("–", ", .") 10, blank
titles 8, and the rest at random. No object is drawn twice, and objects in
the existing inventories (data/met_inventory_300*.tsv) are skipped. Rows are
sorted by title, like the other inventories. Columns: Object Date, Title,
Object Number, Link Resource.

Usage:
    python scripts/make_messy_sample.py MetObjects.csv data/met_inventory_e.tsv [--seed 7]
"""
import argparse
import csv
import glob
import random
import re

NON_LATIN = re.compile(r"[Ͱ-ϿЀ-ӿ֐-ۿ฀-๿぀-ヿ㐀-鿿가-힯]")
UNCERTAIN = re.compile(r"\?|\bprobably\b|\bpossibly\b", re.I)
ID_RANGE = re.compile(r"[–—]|, \.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    csv.field_size_limit(10**9)
    taken = set()
    for f in glob.glob("data/met_inventory_300*.tsv"):
        for r in list(csv.reader(open(f, encoding="utf-8"), delimiter="\t"))[1:]:
            taken.add(r[2])
    pools = {k: [] for k in ("long", "nonlatin", "uncertain", "idrange", "blank", "any")}
    for r in csv.DictReader(open(a.source, encoding="utf-8-sig")):
        row = (r["Object Date"].strip(), r["Title"].strip(), r["Object Number"].strip(), r["Link Resource"].strip())
        if not row[2] or not row[3] or row[2] in taken:
            continue
        t = row[1]
        if not t:
            pools["blank"].append(row)
        elif NON_LATIN.search(t):
            pools["nonlatin"].append(row)
        elif len(t) > 100:
            pools["long"].append(row)
        elif UNCERTAIN.search(row[0]):
            pools["uncertain"].append(row)
        elif ID_RANGE.search(row[2]):
            pools["idrange"].append(row)
        else:
            pools["any"].append(row)
    rng = random.Random(a.seed)
    want = {"long": 33, "nonlatin": 17, "uncertain": 10, "idrange": 10, "blank": 8, "any": 22}
    rows, seen = [], set()
    for k, n in want.items():
        pick = [r for r in rng.sample(pools[k], min(len(pools[k]), n * 3)) if r[2] not in seen][:n]
        seen.update(r[2] for r in pick)
        rows += pick
    rows.sort(key=lambda r: r[1])
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["Object Date", "Title", "Object Number", "Link Resource"])
        w.writerows(rows)
    print(len(rows), "rows;", {k: min(len(pools[k]), n) for k, n in want.items()})


if __name__ == "__main__":
    main()
