"""Check chat-mode spike runs (no tools) against the original spreadsheet.

A reply either contains the whole sheet as a CSV code block, or a Python
script for the user to run. For each run this script:

- Sheet in the reply: parses it and compares every cell with the original,
  and counts lines whose raw text differs outside the date field even though
  the values match (e.g. quotes added around a title).
- Script in the reply: runs the script on a fresh copy of the original in a
  throwaway folder, then checks that every non-date value survived and that
  the input file was left alone. If the output has a per-row checksum, it
  checks which hashing scheme reproduces it from the original rows.

Writes evaluation_results.json, date_comparison.csv (sheets returned in the
reply), and runs/<id>/script_check/ (each script's run).

Usage:
    python scripts/evaluate_chat.py experiments/spike-02/evaluation.json
"""
import csv
import hashlib
import io
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import zlib


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def csv_line(row, term):
    buf = io.StringIO()
    csv.writer(buf, lineterminator=term).writerow(row)
    return buf.getvalue()


# Ways a script might hash a row. Each maps a list of field values to a string.
SCHEMES = {
    "sha256 of json.dumps(row)": lambda r: sha(json.dumps(r, ensure_ascii=False)),
    "sha256 of compact json": lambda r: sha(json.dumps(r, ensure_ascii=False, separators=(",", ":"))),
    "sha256 of fields joined by \\x1f": lambda r: sha("\x1f".join(r)),
    "sha256 of fields joined by \\x1f, first 16 hex": lambda r: sha("\x1f".join(r))[:16],
    "crc32 of fields joined by \\x1f": lambda r: f"{zlib.crc32(chr(31).join(r).encode()):08x}",
    "sha256 of CSV line (CRLF)": lambda r: sha(csv_line(r, "\r\n")),
    "sha256 of CSV line (LF)": lambda r: sha(csv_line(r, "\n")),
}


def code_blocks(text, lang=None):
    blocks = re.findall(r"```(\w*)\n(.*?)```", text, re.S)
    return [b for l, b in blocks if lang is None or l == lang]


def date_field_end(line):
    """Index just past the first CSV field (and its comma) in a raw line."""
    if line.startswith('"'):
        return line.index('",') + 2
    return line.index(",") + 1


def check_sheet(reply, orig_lines, orig):
    blocks = [b for b in code_blocks(reply) if b.startswith(",".join(orig[0]))]
    if not blocks:
        return None, {"kind": "no sheet found"}
    body = blocks[0]
    rows = list(csv.reader(io.StringIO(body)))
    header, out = rows[0], rows[1:]
    out_lines = body.splitlines()[1:]
    res = {
        "kind": "sheet in reply",
        "rows": len(out),
        "header_same": header == orig[0],
        "same_row_order": [r[3] for r in out] == [r[3] for r in orig[1:]],
        "non_date_cells_changed": sum(
            o[c] != n[c] for o, n in zip(orig[1:], out) for c in range(1, len(header))
        ),
        "dates_changed": sum(o[0] != n[0] for o, n in zip(orig[1:], out)),
        "lines_with_raw_formatting_change": sum(
            a[date_field_end(a):] != b[date_field_end(b):]
            for a, b in zip(orig_lines[1:], out_lines)
        ),
    }
    return [r[0] for r in out], res


def check_script(reply, run, run_dir, cfg, orig):
    scripts = code_blocks(reply, "python")
    if not scripts:
        return {"kind": "no sheet or script found"}
    dest = run_dir / "script_check"
    if dest.exists():
        shutil.rmtree(dest)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="exec-", dir=cfg["work_parent"]))
    (tmp / "script.py").write_text(scripts[0], encoding="utf-8")
    shutil.copyfile(cfg["original"], tmp / "input.csv")
    proc = subprocess.run(
        [sys.executable, "-I", "script.py", *run["script_args"]],
        cwd=tmp, capture_output=True, text=True, timeout=120,
    )
    (tmp / "stdout.txt").write_text(proc.stdout)
    (tmp / "stderr.txt").write_text(proc.stderr)
    shutil.copytree(tmp, dest)
    shutil.rmtree(tmp)

    res = {
        "kind": "script in reply (run by evaluator)",
        "exit_code": proc.returncode,
        "input_left_unchanged": hashlib.sha256((dest / "input.csv").read_bytes()).hexdigest()
        == hashlib.sha256(pathlib.Path(cfg["original"]).read_bytes()).hexdigest(),
    }
    if proc.returncode != 0:
        return res
    rows = list(csv.DictReader(open(dest / run["script_output"], encoding="utf-8", newline="")))
    non_date = [c for c in orig[0] if c != "Object Date"]
    res["rows"] = len(rows)
    res["non_date_cells_changed"] = sum(
        o[orig[0].index(c)] != n.get(c) for o, n in zip(orig[1:], rows) for c in non_date
    )
    res["original_date_kept_in_column"] = next(
        (c for c in rows[0] if c != "Object Date"
         and all(n[c] == o[0] for o, n in zip(orig[1:], rows))), None
    )
    if "checksum" in run:
        path, col = run["checksum"]["file"], run["checksum"]["column"]
        vals = [r[col] for r in csv.DictReader(open(dest / path, encoding="utf-8"))]
        res["checksum_column"] = f"{path}: {col}"
        res["checksum_matches_original_rows"] = next(
            (f"{name} ({n}/{len(vals)})" for name, f in SCHEMES.items()
             if (n := sum(v == f(o) for v, o in zip(vals, orig[1:])))), "no known scheme"
        )
    return res


def main():
    cfg_path = pathlib.Path(sys.argv[1])
    cfg = json.loads(cfg_path.read_text())
    root = cfg_path.parent
    orig_text = pathlib.Path(cfg["original"]).read_text(encoding="utf-8")
    orig_lines = orig_text.splitlines()
    orig = list(csv.reader(io.StringIO(orig_text)))

    report, dates = [], {"Original": [r[0] for r in orig[1:]]}
    for run in cfg["runs"]:
        run_dir = root / "runs" / run["id"]
        reply = (run_dir / "response.md").read_text(encoding="utf-8")
        hexes = re.findall(r"\b[0-9a-f]{16,64}\b", reply)
        sheet_dates, res = check_sheet(reply, orig_lines, orig)
        if sheet_dates is not None:
            dates[run["id"]] = sheet_dates
        else:
            res = check_script(reply, run, run_dir, cfg, orig)
        res = {"run": run["id"], "hash_like_strings_in_reply": len(hexes), **res}
        report.append(res)
        print(json.dumps(res))

    with open(root / "date_comparison.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["Object Number"] + list(dates))
        for i, row in enumerate(orig[1:]):
            w.writerow([row[3]] + [d[i] for d in dates.values()])
    (root / "evaluation_results.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
