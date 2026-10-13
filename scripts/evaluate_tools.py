"""Score files written by run_tools.py runs against the input TSV.

For each output file: rows in/out, titles that aren't in the input (made up),
input titles missing from the output, duplicated titles, rows whose other
cells changed (by column), and how the years column changed. Rows are
matched on the title; a made-up title can't be matched, so its row counts
as added.

Writes <experiment>/evaluation_results.json.

Usage:
    python scripts/evaluate_tools.py experiments/spike-04/config.json
"""
import collections
import csv
import difflib
import json
import pathlib
import re
import sys


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        rows = [ln.rstrip("\n").split("\t") for ln in f if ln.strip()]
    return rows[0], rows[1:]


def norm_years(s):
    """The expected standardized form of a years cell: hyphen, no spaces."""
    s = s.strip()
    m = re.fullmatch(r"(\d{4})\s*(?:-|–|to)\s*(\d{4}|present)", s)
    return f"{m.group(1)}-{m.group(2)}" if m else s


def main():
    cfg_path = pathlib.Path(sys.argv[1])
    cfg = json.loads(cfg_path.read_text())
    root = cfg_path.parent
    report = []
    for run_dir in sorted((root / "runs").iterdir()):
        meta_p = run_dir / "meta.json"
        if not meta_p.exists():
            continue
        meta = json.loads(meta_p.read_text())
        cond = meta["condition"]
        h_in, rows_in = read_tsv(cfg["inputs"][cond["input"]])
        res = {"run": run_dir.name, "condition": cond["id"], "cost_usd": meta["cost_usd"],
               "tool_calls": [t["tool"] + (f" {t.get('view_range')}" if t["tool"] == "view" else "")
                              for t in meta["tool_calls"]]}
        outs = sorted((run_dir / "output_files").glob("*.[tc]sv")) if (run_dir / "output_files").exists() else []
        if not outs:
            made = sorted(p.name for p in (run_dir / "output_files").glob("*")) if (run_dir / "output_files").exists() else []
            res["outcome"] = f"no data file created (files: {made})" if made else "no file created"
            report.append(res)
            print(json.dumps(res))
            continue
        h_out, rows_out = read_tsv(outs[-1])
        key = lambda h: re.sub(r"[\s_]+", " ", h.strip().lower())
        low = [key(h) for h in h_out]
        ti = low.index("title") if "title" in low else 1
        # Match renamed headers ("link_resource" for "Link Resource") to the input's.
        h_out = [next((x for x in h_in if key(x) == key(h)), h) for h in h_out]
        in_titles = collections.Counter(r[1] for r in rows_in)
        out_titles = collections.Counter(r[ti] if len(r) > ti else "" for r in rows_out)
        made_up = [t for t in out_titles if t not in in_titles]
        res.update({
            "outcome": f"file {outs[-1].name}",
            "header_out": h_out,
            "rows_in": len(rows_in), "rows_out": len(rows_out),
            "titles_made_up": len(made_up),
            "titles_missing": sum(1 for t in in_titles if t not in out_titles),
            "titles_duplicated": sum(max(0, out_titles[t] - in_titles.get(t, 0)) for t in out_titles if t in in_titles),
            "made_up_examples": [{"title": t, "closest_input_title": (difflib.get_close_matches(t, list(in_titles), 1, 0) or [""])[0]}
                                 for t in made_up[:12]],
            "same_row_order": [r[ti] for r in rows_out if len(r) > ti] == [r[1] for r in rows_in],
        })
        by_title = {}
        for r in rows_in:
            by_title.setdefault(r[1], []).append(r)
        changes = collections.Counter()
        years_wrong = []
        for r in rows_out:
            if len(r) <= ti or r[ti] not in by_title:
                continue
            o = by_title[r[ti]].pop(0) if by_title[r[ti]] else None
            if o is None:
                continue
            for j, name in enumerate(h_in):
                if name.lower() == "title" or name not in h_out:
                    continue
                new = r[h_out.index(name)] if h_out.index(name) < len(r) else ""
                if name == "coverage_years":
                    if new != norm_years(o[j]):
                        years_wrong.append({"title": o[1], "was": o[j], "now": new})
                elif new != o[j]:
                    changes[name] += 1
        res["other_cells_changed_by_column"] = dict(changes)
        res["years_not_as_expected"] = len(years_wrong)
        res["years_examples"] = years_wrong[:10]
        report.append(res)
        print(json.dumps({k: v for k, v in res.items() if k not in ("made_up_examples", "years_examples", "header_out")}))
    (root / "evaluation_results.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
