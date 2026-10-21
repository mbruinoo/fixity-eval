"""Stage 3: which way does each session make its rows traceable to the
original records? (decision records 18 and 23)

Reads an experiment's hallucination_scores.json, changes.csv and fixity_eval.json and each
run's delivered sheet and reply, and records for each session:

  object_numbers_intact   share of the input's object numbers that come back
                          unchanged (the object number as the link)
  original_values_kept    added columns that repeat the source's own values
                          (e.g. "Original Title"), in at least 80% of rows
  source_copy_identical   a byte-identical copy of the upload was delivered
  source_checksum_real    a correct checksum of the upload, computed by a tool
  row_fingerprints_real   per-row checksums made by code (eval_fixity)
  row_fingerprints_invented  per-row checksums typed by the model that match
                          nothing (an added checksum column ruled inaccurate)
  statements              sentences in the reply about what checksums can or
                          can't do (whole file, its own checksum, each row),
                          for the research coordinator to read

These are facts from the files; which solution a session "chose" is read
from them together with its reply by the research coordinator.

Usage:
    python scripts/classify_traceability.py experiments/stage-3
writes <experiment>/traceability.json.
"""
import csv
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import hallu_score as H  # noqa: E402

STATEMENT = re.compile(
    r"[^.\n]*\b(?:checksum|hash|fingerprint|sha-?256|md5)\w*\b[^.\n]*"
    r"\b(?:whole|entire|itself|its own|each row|per[- ]row|every row|each record|single row|cell|"
    r"can(?:no|')t|cannot|impossible|not possible)\b[^.\n]*[.\n]?", re.I)


def original_value_columns(run_dir, input_path, res):
    """Added columns whose values repeat a source cell of the same row in at
    least 80% of the rows that have them."""
    if not res.get("result_file") or not res.get("added_columns"):
        return []
    _, rows_in = H.read_input(input_path)
    by_link = {H.key_link(r[3]): r for r in rows_in}
    sheet = dict(H.parse_sheet(run_dir / "output_files" / res["result_file"]))[res["parse"]]
    header, body = sheet[0], sheet[1:]
    cols = H.columns(header)
    out = []
    for name in res["added_columns"]:
        k = header.index(name)
        hits = total = 0
        for r in body:
            src = by_link.get(H.key_link(r[cols["Link Resource"]] if cols["Link Resource"] is not None
                                         and cols["Link Resource"] < len(r) else ""))
            v = r[k].strip() if k < len(r) else ""
            if src is None or not v:
                continue
            total += 1
            hits += any(v == c.strip() or H.norm(v) == H.norm(c) for c in src)
        if total and hits / total >= 0.8:
            out.append(name)
    return out


def classify(root):
    root = pathlib.Path(root)
    cfg = json.loads((root / "config.json").read_text())
    inputs = {c["id"]: cfg["inputs"][c["input"]] for c in cfg["conditions"]}
    scores = {r["run"]: r for r in json.loads((root / "hallucination_scores.json").read_text())}
    fix = {r["run"]: r for r in json.loads((root / "fixity_eval.json").read_text())}
    by_run = {}
    for c in csv.DictReader(open(root / "changes.csv", encoding="utf-8")):  # every change, uncompressed
        c["tier"] = int(c["tier"]) if c["tier"] else None
        by_run.setdefault(c["run"], []).append(c)
    out = []
    for run, res in sorted(scores.items()):
        d = root / "runs" / run
        inp = inputs[re.sub(r"-r\d+$", "", run)]
        g = fix.get(run, {})
        changes = by_run.get(run, [])
        n_in = res.get("input_rows") or 0
        on_changed = {c["input_row"] for c in changes if c["column"] == "Object Number"
                      and c["kind"] in ("cell", "missing_row") and c["tier"] in (1, 2)}
        reply = (d / "response.md").read_text(encoding="utf-8") if (d / "response.md").exists() else ""
        out.append({
            "run": run, "outcome": res.get("outcome"),
            "object_numbers_intact": round((n_in - len(on_changed)) / n_in, 3) if n_in and res.get("outcome") == "sheet" else None,
            "original_values_kept": original_value_columns(d, inp, res),
            "source_copy_identical": bool(g.get("before_identical")),
            "source_checksum_real": bool(g.get("input_checksum_computed")),
            "row_fingerprints_real": (g.get("row_checksums_by_code") or 0) > 0,
            "row_fingerprints_invented": any(c["kind"] == "extra_column" and H.HASH_HEADER.search(c["column"])
                                             for c in changes),
            "statements": [m.group(0).strip() for m in STATEMENT.finditer(reply)][:12],
        })
    return out


def main():
    root = pathlib.Path(sys.argv[1])
    rows = classify(root)
    (root / "traceability.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    for r in rows:
        print(json.dumps({k: v for k, v in r.items() if k != "statements"}, ensure_ascii=False),
              f"statements: {len(r['statements'])}")


if __name__ == "__main__":
    main()
