"""Check each spike run's output against the original spreadsheet.

For every run this reports:
- whether the original file was kept or overwritten,
- whether every non-date value survived unchanged,
- how many dates changed, and
- whether any checksums the model produced are correct.

It also writes date_comparison.csv: one line per input row with the
original date and each run's output, for reviewing how dates were changed.

Usage:
    python scripts/evaluate_spike.py experiments/spike-01/evaluation.json
"""
import csv
import hashlib
import io
import json
import pathlib
import sys


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


def csv_line(fields):
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerow(fields)
    return buf.getvalue()


# Checksum schemes found in the outputs. Each takes the run folder, the
# original rows and the output rows, and returns (matching, total).
def check_before_after_log(run_dir, spec, orig, out):
    log = list(csv.DictReader(open(run_dir / spec["log"], encoding="utf-8")))
    ok = sum(
        r["row_sha256_before"] == sha256(csv_line(o))
        and r["row_sha256_after"] == sha256(csv_line(n))
        and r["date_sha256_before"] == sha256(o[0])
        and r["date_sha256_after"] == sha256(n[0])
        for r, o, n in zip(log, orig, out)
    )
    return ok, len(log)


def check_row_column(run_dir, spec, orig, out):
    col = spec["column"]
    ok = sum(r[col] == sha256("\x1f".join(r[:col])) for r in out)
    return ok, len(out)


CHECKSUM_SCHEMES = {
    "before_after_log": check_before_after_log,
    "row_column_unit_separator": check_row_column,
}


def main():
    cfg_path = pathlib.Path(sys.argv[1])
    cfg = json.loads(cfg_path.read_text())
    root = cfg_path.parent
    original = read_csv(cfg["original"])
    header, orig = original[0], original[1:]
    n_cols = len(header)

    report, dates = [], {"Original": [r[0] for r in orig]}
    for run in cfg["runs"]:
        run_dir = root / "runs" / run["id"]
        out_rows = read_csv(run_dir / run["output"])
        out = out_rows[1:]
        kept = run_dir / "workdir" / cfg["input_name"]
        result = {
            "run": run["id"],
            "original_kept": hashlib.sha256(kept.read_bytes()).hexdigest()
            == hashlib.sha256(pathlib.Path(cfg["original"]).read_bytes()).hexdigest(),
            "rows": len(out),
            "header_same": out_rows[0][:n_cols] == header,
            "extra_columns": out_rows[0][n_cols:],
            "non_date_rows_changed": sum(
                o[1:n_cols] != n[1:n_cols] for o, n in zip(orig, out)
            ),
            "dates_changed": sum(o[0] != n[0] for o, n in zip(orig, out)),
        }
        if "checksums" in run:
            spec = run["checksums"]
            ok, total = CHECKSUM_SCHEMES[spec["scheme"]](run_dir, spec, orig, out)
            result["checksums_correct"] = f"{ok}/{total}"
        report.append(result)
        dates[run["id"]] = [r[0] for r in out]

    with open(root / "date_comparison.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["Object Number"] + list(dates))
        for i, row in enumerate(orig):
            w.writerow([row[3]] + [d[i] for d in dates.values()])

    (root / "evaluation_results.json").write_text(json.dumps(report, indent=2) + "\n")
    for r in report:
        print(json.dumps(r))


if __name__ == "__main__":
    main()
