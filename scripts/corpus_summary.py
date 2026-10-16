"""Summarise analysis/corpus/ (from mine_corpus.py): verification theatre and
survival of cataloguing conventions, by how the answer was produced.

Conventions are found in the *input* cells, so each has a denominator:
  supplied_title   Title contains "[" (the Met brackets titles it supplied)
  original_script  Title contains non-Latin script (e.g. Chinese, Japanese)
  uncertainty      Date or Title has "?", "probably", "possibly", "ca." ...
  date_qualifier   Date contains "(" or "[" (e.g. "1929 (published 1929)")
  blank_title      Title is empty (risk: a placeholder is invented)
A convention "survives" in an answer if its row is present and none of that
row's changes carry a tag that breaks it (LOSS_TAGS).

Writes analysis/corpus/summary.json and prints the tables.

Usage:
    python scripts/corpus_summary.py
"""
import collections
import csv
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "analysis" / "corpus"
NONLATIN = re.compile(r"[Ͱ-ϿЀ-ӿ֐-ۿ฀-๿぀-ヿ㐀-鿿가-힯]")
UNCERTAIN = re.compile(r"\(\?\)|\?|\bprobably\b|\bpossibly\b|\bca\.|\bcirca\b|\bperhaps\b", re.I)
FEATURES = {
    "supplied_title": lambda r: "[" in r[1],
    "original_script": lambda r: bool(NONLATIN.search(r[1])),
    "uncertainty": lambda r: bool(UNCERTAIN.search(r[0]) or UNCERTAIN.search(r[1])),
    "date_qualifier": lambda r: "(" in r[0] or "[" in r[0],
    "blank_title": lambda r: not r[1].strip(),
}
LOSS_TAGS = {
    "supplied_title": {"brackets_removed", "emptied"},
    "original_script": {"original_script_removed", "emptied"},
    "uncertainty": {"uncertainty_removed", "uncertainty_reworded"},
    "date_qualifier": {"parenthetical_removed", "date_rewritten", "uncertainty_removed", "truncated"},
    "blank_title": {"placeholder_filled", "content_added_to_blank"},
}
FEATURE_COL = {"supplied_title": "Title", "original_script": "Title", "uncertainty": None,
               "date_qualifier": "Object Date", "blank_title": "Title"}


def read_input(path):
    rows = list(csv.reader(open(ROOT / path, encoding="utf-8"), delimiter="\t"))[1:]
    return [r + [""] * (4 - len(r)) for r in rows]


def pct(a, b):
    return round(100 * a / b, 1) if b else None


def main():
    answers = list(csv.DictReader(open(D / "answers.csv", encoding="utf-8")))
    claims = list(csv.DictReader(open(D / "claims.csv", encoding="utf-8")))
    losses = list(csv.DictReader(open(D / "losses.csv", encoding="utf-8")))
    by_answer = collections.defaultdict(list)
    for l in losses:
        by_answer[(l["spike"], l["run"], l["stage"])].append(l)
    inputs = {}
    out = {"answers": len(answers)}

    # --- how answers were made
    hw = collections.Counter(a["how"] for a in answers)
    out["how"] = dict(hw)

    # --- verification theatre
    def T(rows, key):
        return sum(1 for a in rows if a[key] == "True")
    groups = collections.defaultdict(list)
    for a in answers:
        groups[a["how"]].append(a)
    groups["all"] = answers
    th = {}
    for g, rows in groups.items():
        claimers = [a for a in rows if int(a["claims"]) > 0]
        ck = [a for a in rows if int(a["ck_computed"]) + int(a["ck_typed_correct"]) + int(a["ck_stale"])
              + int(a["ck_invented"]) > 0 or a["ck_malformed_column"] == "True" or a["placeholder_hash"] == "True"]
        fake = [a for a in ck if int(a["ck_invented"]) + int(a["ck_stale"]) > 0 or a["ck_malformed_column"] == "True"
                or a["placeholder_hash"] == "True"]
        real_only = [a for a in ck if a not in fake and int(a["ck_computed"]) > 0]
        th[g] = {"answers": len(rows),
                 "with_integrity_claims": len(claimers),
                 "with_false_claims": sum(1 for a in rows if int(a["false_claims"]) > 0),
                 "pct_claimers_with_a_false_claim": pct(sum(1 for a in claimers if int(a["false_claims"]) > 0), len(claimers)),
                 "showing_checksums": len(ck), "checksums_any_fake": len(fake), "checksums_all_real": len(real_only),
                 "theatre": T(rows, "theatre"), "pct_theatre": pct(T(rows, "theatre"), len(rows)),
                 "retyped_source_copy": T(rows, "retyped_source_copy")}
    out["theatre_by_how"] = th
    ck = collections.Counter()
    for c in claims:
        ck[(c["kind"], c["how"], c["true"])] += 1
    out["claims"] = {f"{k}|{h}": {"true": ck[(k, h, "True")], "false": ck[(k, h, "False")]}
                     for k, h in sorted({(k, h) for k, h, _ in ck})}

    # --- convention survival
    surv = collections.defaultdict(lambda: [0, 0])  # (feature, how) -> [survived, present]
    examples = collections.defaultdict(list)
    for a in answers:
        if a["how"] == "none" or a["output"] in ("no sheet", None, ""):
            continue
        rows = inputs.setdefault(a["input"], read_input(a["input"]))
        ls = by_answer[(a["spike"], a["run"], a["stage"])]
        missing = {l["object_number"] for l in ls if l["tag"] == "missing_row"}
        tagged = collections.defaultdict(set)
        for l in ls:
            tagged[l["object_number"]].add((l["column"], l["tag"]))
            tagged[l["object_number"]].add((None, l["tag"]))
        for r in rows:
            for f, has in FEATURES.items():
                if not has(r):
                    continue
                col = FEATURE_COL[f]
                lost = r[2] in missing or any((col, t) in tagged[r[2]] for t in LOSS_TAGS[f])
                for g in (a["how"], "all"):
                    surv[(f, g)][1] += 1
                    surv[(f, g)][0] += 0 if lost else 1
                if lost and len(examples[f]) < 8 and r[2] not in missing:
                    lo = [l for l in ls if l["object_number"] == r[2] and l["tag"] in LOSS_TAGS[f]]
                    if lo:
                        examples[f].append({"input": lo[0]["input"], "output": lo[0]["output"], "how": a["how"]})
    out["survival"] = {f"{f}|{g}": {"survived": s, "present": n, "pct": pct(s, n)} for (f, g), (s, n) in sorted(surv.items())}
    out["loss_examples"] = examples

    # --- fixity error by how
    fx = collections.defaultdict(list)
    for a in answers:
        if a["fixity_error_rate"] not in ("", "None"):
            fx[a["how"]].append(float(a["fixity_error_rate"]))
    out["fixity_error_median_by_how"] = {h: sorted(v)[len(v) // 2] for h, v in fx.items()}

    (D / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print("answers by how:", dict(hw))
    print("\nTHEATRE")
    for g, v in th.items():
        print(f"  {g:15} {v}")
    print("\nCLAIMS (kind|how: true/false)")
    for k, v in out["claims"].items():
        print(f"  {k:32} {v}")
    print("\nSURVIVAL of conventions (% of cells where it survived)")
    for f in FEATURES:
        print(f"  {f:16}", {g: out['survival'].get(f'{f}|{g}', {}).get('pct') for g in ('typed', 'code_on_upload', 'code_on_copy', 'all')},
              "n:", {g: out['survival'].get(f'{f}|{g}', {}).get('present') for g in ('typed', 'code_on_upload', 'code_on_copy')})
    print("\nmedian fixity error by how:", out["fixity_error_median_by_how"])


if __name__ == "__main__":
    main()
