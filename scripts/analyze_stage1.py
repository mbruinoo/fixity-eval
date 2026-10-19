"""Stage 1's pre-registered analysis (analysis/preregistration.md).

Reads an experiment's hallucination_scores.json (hallu_score.py) and
fixity_eval.json (eval_fixity.py), one row per session, and compares the
three requests (decision record 17): "base", "fix", "fix-hint".

Main comparisons (fix vs base), each at a significance level of 2.5%:
  M1  error rate of the delivered sheet: two-sided Mann-Whitney U test
  M2  a correct checksum of the upload, computed by a tool in the session
      (input_checksum_computed): two-sided Fisher exact test
Secondary comparisons (fix-hint vs fix), each at 5%, reported as secondary:
  S1  real per-row checksums made by code (row_checksums_by_code > 0)
  S2  invented checksums of any kind
  S3  error rate
Described, not tested: each request's outcomes (record 11), how its sheets
were made, whether the code tool was found, and medians, ranges and 95%
Wilson intervals.

Sessions without a sheet are reported in the outcome table and left out of
the error-rate comparisons; every session counts for M2, S1 and S2.

Usage:
    python scripts/analyze_stage1.py experiments/<stage-1>
writes <experiment>/stage1_results.json and prints a plain table.
"""
import json
import math
import pathlib
import re
import statistics
import sys

REQUESTS = ("base", "fix", "fix-hint")


def mann_whitney(x, y):
    """Two-sided Mann-Whitney U test, normal approximation with a tie
    correction and a continuity correction. Returns (U for x, p)."""
    allv = sorted([(v, 0) for v in x] + [(v, 1) for v in y])
    n1, n2, n = len(x), len(y), len(x) + len(y)
    if not n1 or not n2:
        return None, None
    ranks, i, ties = [0.0] * n, 0, 0
    while i < n:
        j = i
        while j + 1 < n and allv[j + 1][0] == allv[i][0]:
            j += 1
        for k in range(i, j + 1):
            ranks[k] = (i + j) / 2 + 1
        ties += (j - i + 1) ** 3 - (j - i + 1)
        i = j + 1
    u = sum(r for r, (_, g) in zip(ranks, allv) if g == 0) - n1 * (n1 + 1) / 2
    sd = math.sqrt(n1 * n2 / 12 * ((n + 1) - ties / (n * (n - 1))))
    if sd == 0:
        return u, 1.0
    z = max(abs(u - n1 * n2 / 2) - 0.5, 0) / sd
    return u, math.erfc(z / math.sqrt(2))


def fisher(a, b, c, d):
    """Two-sided Fisher exact test on [[a, b], [c, d]]: the sum of the
    probabilities of all tables at most as likely as the one observed."""
    n, r1, c1 = a + b + c + d, a + b, a + c
    if n == 0:
        return None
    p = lambda x: math.comb(c1, x) * math.comb(n - c1, r1 - x) / math.comb(n, r1)
    p0 = p(a)
    return min(1.0, sum(p(x) for x in range(max(0, r1 - (n - c1)), min(r1, c1) + 1) if p(x) <= p0 * (1 + 1e-9)))


def wilson(k, n, z=1.96):
    """95% Wilson interval for k of n."""
    if n == 0:
        return None
    ph = k / n
    centre = (ph + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return round(max(0.0, centre - half), 3), round(min(1.0, centre + half), 3)


def code_tool_found(run_dir):
    reqs = sorted(run_dir.glob("request_[0-9]*.json"), key=lambda f: int(re.sub(r"\D", "", f.stem)))
    return bool(reqs) and "bash_tool" in [t.get("name") for t in json.loads(reqs[-1].read_text()).get("tools", [])]


def sessions(root):
    scores = {r["run"]: r for r in json.loads((root / "hallucination_scores.json").read_text())}
    fix = {r["run"]: r for r in json.loads((root / "fixity_eval.json").read_text())}
    out = []
    for run, s in sorted(scores.items()):
        g = fix.get(run, {})
        prov = g.get("checksum_provenance") or {}
        out.append({
            "run": run, "request": re.sub(r"-r\d+$", "", run), "outcome": s.get("outcome"),
            "error_rate": s.get("fixity_error_rate") if s.get("outcome") == "sheet" else None,
            "upload_checksum_computed": bool(g.get("input_checksum_computed")),
            "row_checksums_by_code": (g.get("row_checksums_by_code") or 0) > 0,
            "invented_checksums": bool(prov.get("invented") or prov.get("stale") or g.get("checksums_malformed")
                                       or s.get("added_cells_inaccurate")),
            "code_on_upload": bool(g.get("script_on_upload")),
            "code_tool_found": code_tool_found(root / "runs" / run),
        })
    return out


def describe(rows):
    rates = [r["error_rate"] for r in rows if r["error_rate"] is not None]
    count = lambda k: sum(r[k] for r in rows)
    outcomes = {}
    for r in rows:
        outcomes[r["outcome"]] = outcomes.get(r["outcome"], 0) + 1
    return {
        "sessions": len(rows), "outcomes": outcomes,
        "error_rate": {"n": len(rates), "median": statistics.median(rates) if rates else None,
                       "quartiles": statistics.quantiles(rates, n=4) if len(rates) >= 2 else None,
                       "min": min(rates, default=None), "max": max(rates, default=None)},
        **{k: {"k": count(k), "n": len(rows), "wilson_95": wilson(count(k), len(rows))}
           for k in ("upload_checksum_computed", "row_checksums_by_code", "invented_checksums",
                     "code_on_upload", "code_tool_found")},
    }


def compare_rates(a, b, alpha):
    u, p = mann_whitney([r["error_rate"] for r in a if r["error_rate"] is not None],
                        [r["error_rate"] for r in b if r["error_rate"] is not None])
    return {"test": "Mann-Whitney U, two-sided", "U": u, "p": p, "alpha": alpha,
            "significant": p is not None and p < alpha}


def compare_share(a, b, key, alpha):
    ka, kb = sum(r[key] for r in a), sum(r[key] for r in b)
    p = fisher(ka, len(a) - ka, kb, len(b) - kb)
    return {"test": "Fisher exact, two-sided", "a": f"{ka}/{len(a)}", "b": f"{kb}/{len(b)}", "p": p,
            "alpha": alpha, "significant": p is not None and p < alpha}


def analyze(rows):
    by = {q: [r for r in rows if r["request"] == q] for q in REQUESTS}
    return {
        "described": {q: describe(by[q]) for q in REQUESTS},
        "main (fix vs base)": {
            "M1 error rate": compare_rates(by["fix"], by["base"], 0.025),
            "M2 upload checksum computed": compare_share(by["fix"], by["base"], "upload_checksum_computed", 0.025),
        },
        "secondary (fix-hint vs fix)": {
            "S1 per-row checksums made by code": compare_share(by["fix-hint"], by["fix"], "row_checksums_by_code", 0.05),
            "S2 invented checksums": compare_share(by["fix-hint"], by["fix"], "invented_checksums", 0.05),
            "S3 error rate": compare_rates(by["fix-hint"], by["fix"], 0.05),
        },
    }


def main():
    root = pathlib.Path(sys.argv[1])
    rows = sessions(root)
    res = {"sessions": rows, **analyze(rows)}
    (root / "stage1_results.json").write_text(json.dumps(res, indent=1) + "\n")
    for q, d in res["described"].items():
        e = d["error_rate"]
        print(f"{q:9} n={d['sessions']:2} outcomes={d['outcomes']} error rate median={e['median']} "
              f"upload checksum={d['upload_checksum_computed']['k']}/{d['sessions']} "
              f"code={d['code_on_upload']['k']}/{d['sessions']} code tool found={d['code_tool_found']['k']}/{d['sessions']}")
    for part in ("main (fix vs base)", "secondary (fix-hint vs fix)"):
        print(part)
        for name, t in res[part].items():
            print(f"  {name}: p={t['p']} (alpha {t['alpha']}) {'yes' if t['significant'] else 'no'}")


if __name__ == "__main__":
    main()
