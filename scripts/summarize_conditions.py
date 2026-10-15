"""Per-session outcomes and per-request totals for a many-session spike
(e.g. spike-32), from the files the scorers leave (run eval_fixity.py first).

Per session:
  bash_loaded       a tool_search loaded bash_tool
  code_on_upload    a bash command or script read uploads/ (eval_fixity's script_on_upload)
  overwrote_source  a bash command wrote over the uploaded file itself (e.g. a retyped copy)
  result            a result file other than a byte-identical copy of the source, or
                    "identical" when the only sheet is byte-identical to the source
  rate              fixity error rate of the result (0.0 when identical)
  real_checksums    a correct checksum of the source appears, computed (seen in a tool result)
  invented          checksum-like values that match no file, plus malformed row-hash columns,
                    plus labelled placeholders
  cost_usd

Writes summary.json and prints a table per request.

Usage:
    python scripts/summarize_conditions.py experiments/spike-32
"""
import json
import pathlib
import re
import statistics
import sys

PLACEHOLDER = re.compile(r"\[placeholder|placeholder\]|placeholder -|to be (?:calculated|computed)", re.I)


def session(run_dir, g):
    meta = json.loads((run_dir / "meta.json").read_text())
    calls = meta["tool_calls"]
    bash_loaded = any(t["tool"] == "tool_search" and "bash_tool" in (t.get("found") or []) for t in calls)
    cmds = [t.get("command", "") for t in calls if t["tool"] == "bash_tool"]
    src = re.escape("/mnt/user-data/uploads/" + meta["condition"]["filename"])
    overwrote = any(re.search(r"(?:>|cp\s+\S+\s+|tee\s+|mv\s+\S+\s+)\s*" + src + r"(?:\s|$|')", c) for c in cmds)
    identical = g.get("before_identical") and not g.get("result_file")
    rate = 0.0 if identical else g.get("result_rate")
    out = run_dir / "output_files"
    text = " ".join(f.read_text(encoding="utf-8", errors="replace") for f in out.rglob("*")
                    if f.is_file() and f.suffix in {".txt", ".md", ".json", ".sha256", ".md5"}) if out.exists() else ""
    prov = g.get("checksum_provenance", {})
    invented = prov.get("invented", 0) + (1 if g.get("row_checksums_malformed") else 0) \
        + (1 if PLACEHOLDER.search(text) else 0)
    return {"run": run_dir.name, "bash_loaded": bash_loaded, "code_on_upload": bool(g.get("script_on_upload")),
            "overwrote_source": overwrote,
            "result": "identical" if identical else ("yes" if g.get("result_file") else "none"),
            "rate": rate, "real_checksums": bool(g.get("input_checksum")) and prov.get("computed", 0) > 0,
            "invented": invented, "cost_usd": meta.get("cost_usd")}


def main():
    root = pathlib.Path(sys.argv[1])
    evals = {g["run"]: g for g in json.loads((root / "fixity_eval.json").read_text())}
    cfg = json.loads((root / "config.json").read_text())
    rows = [session(root / "runs" / r, g) for r, g in sorted(evals.items()) if (root / "runs" / r / "meta.json").exists()]
    summary = {}
    for c in cfg["conditions"]:
        rs = [r for r in rows if r["run"].startswith(c["id"] + "-r")]
        if not rs:
            continue
        rates = [r["rate"] for r in rs if r["rate"] is not None]
        summary[c["id"]] = {
            "prompt": c["prompt"], "sessions": len(rs),
            "bash_loaded": sum(r["bash_loaded"] for r in rs),
            "code_on_upload": sum(r["code_on_upload"] for r in rs),
            "overwrote_source": sum(r["overwrote_source"] for r in rs),
            "no_result": sum(r["result"] == "none" for r in rs),
            "real_checksums": sum(r["real_checksums"] for r in rs),
            "sessions_with_invented": sum(r["invented"] > 0 for r in rs),
            "rate_median": statistics.median(rates) if rates else None,
            "rate_mean": round(statistics.mean(rates), 4) if rates else None,
            "rates": rates, "cost_usd": round(sum(r["cost_usd"] or 0 for r in rs), 4)}
    (root / "summary.json").write_text(json.dumps({"sessions": rows, "by_request": summary}, indent=1, ensure_ascii=False))
    for k, v in summary.items():
        print(f"{k:26} n={v['sessions']:2} bash={v['bash_loaded']:2} code_on_upload={v['code_on_upload']:2} "
              f"real_ck={v['real_checksums']:2} invented={v['sessions_with_invented']:2} "
              f"overwrote={v['overwrote_source']} no_result={v['no_result']} "
              f"rate median={v['rate_median']} mean={v['rate_mean']} ${v['cost_usd']}")


if __name__ == "__main__":
    main()
