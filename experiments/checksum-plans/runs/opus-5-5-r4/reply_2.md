# Adding Checksums for Later Verification

You can't compare a hash of the output to a hash of the source, because standardization changes the values. The checksums need to answer three separate questions instead:

| Question | What to hash | Why |
|---|---|---|
| Is this the source file the output came from? | The raw **bytes** of the source file | Detects any change at all, including encoding and line endings |
| Which rows changed, and where did each output row come from? | Each source row's **parsed cells**, and each output row's cells | Pinpoints individual edits and keeps the source-to-output link even after sorting |
| Can I regenerate this exact output? | Script file, options, and Python/Unicode versions, plus the output bytes | Re-running the same transformation on the same source must produce the same hash |

All of this goes into a **sidecar manifest** (`inventory_manifest.json`) rather than an extra column. That keeps the output at four columns, so downstream systems aren't affected. The script also gets a `--verify` mode that checks everything in the manifest.

Below are the changes to the previous script. The `standardize_*` functions, `check_links`, and `natural_key` stay unchanged.

## 1. New imports and hashing helpers

```python
import hashlib
import json
import os
import platform
from collections import Counter
from datetime import datetime, timezone

SCRIPT_VERSION = "1.1.0"
MANIFEST_VERSION = 1
TRANSFORM_OPTIONS = ("dayfirst", "objnum_sep", "objnum_upper",
                     "ascii_quotes", "keep_http", "sort")
REPORT_HEADER = ["input line", "column", "original", "standardized", "note"]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path, chunk=1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def row_hash(cells) -> str:
    """Hash a row's cells unambiguously.

    JSON-encoding the list avoids collisions that naive joining would cause,
    e.g. ["a\\tb", "c"] vs ["a", "b\\tc"]. Values are hashed exactly as read:
    no trimming, no normalization.
    """
    canonical = json.dumps(list(cells), ensure_ascii=False, separators=(",", ":"))
    return sha256_bytes(canonical.encode("utf-8"))
```

## 2. Refactor `main()` into a deterministic pipeline

Reproducibility requires one function that maps (source text + options) to output, with no file I/O and no network calls inside it.

```python
def decode_bytes(data: bytes):
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return data.decode(enc), enc
        except UnicodeDecodeError:
            continue
    raise RuntimeError("Could not decode file")


def parse_records(text: str, skip_blank: bool = True):
    reader = csv.reader(io.StringIO(text, newline=""), delimiter="\t")
    records = [(reader.line_num, r) for r in reader]
    if skip_blank:
        records = [(n, r) for n, r in records if any(c.strip() for c in r)]
    return records


def detect_header(records):
    first = [norm_header(c) for c in records[0][1]]
    mapping = {}
    for idx, h in enumerate(first):
        for col, aliases in HEADER_ALIASES.items():
            if h in aliases and col not in mapping:
                mapping[col] = idx
                break
    if len(mapping) >= 2:
        missing = [c for c in COLUMNS if c not in mapping]
        if missing:
            sys.exit(f"Header found, but couldn't identify column(s): {', '.join(missing)}")
        return True, mapping
    return False, {c: i for i, c in enumerate(COLUMNS)}


def add_report(report, line, col, before, after, note=None):
    if before != after or note:
        report.append([line, col, before, after, note or "standardized"])


def sort_report(report):
    report.sort(key=lambda x: (x[0], COLUMNS.index(x[1]) if x[1] in COLUMNS else -1))


def run_pipeline(text: str, opts: dict):
    """Deterministic: same text + same opts + same script -> identical result."""
    records = parse_records(text)
    if not records:
        raise ValueError("Input file is empty.")
    has_header, mapping = detect_header(records)
    data = records[1:] if has_header else records

    report, out_rows = [], []
    for line, r in data:
        if not has_header and len(r) > 4 and any(c.strip() for c in r[4:]):
            add_report(report, line, "(row)", " | ".join(r[4:]), "",
                       f"{len(r)} cells found; cells after the 4th were dropped")

        raw = {c: (r[mapping[c]] if mapping[c] < len(r) else "") for c in COLUMNS}
        new = {}
        new["date"], n = standardize_date(raw["date"], opts["dayfirst"])
        add_report(report, line, "date", raw["date"], new["date"], n)
        new["title"], n = standardize_title(raw["title"], opts["ascii_quotes"])
        add_report(report, line, "title", raw["title"], new["title"], n)
        new["object_number"], n = standardize_objnum(raw["object_number"],
                                                     opts["objnum_sep"], opts["objnum_upper"])
        add_report(report, line, "object_number", raw["object_number"], new["object_number"], n)
        new["link"], n = standardize_link(raw["link"], force_https=not opts["keep_http"])
        add_report(report, line, "link", raw["link"], new["link"], n)

        out_rows.append((line, r, new))  # keep raw cells for the source row hash

    for col in ("object_number", "link"):
        groups = defaultdict(list)
        for line, _, rec in out_rows:
            if rec[col]:
                groups[rec[col].casefold()].append((line, rec[col]))
        for items in groups.values():
            if len(items) > 1:
                lines = [str(l) for l, _ in items]
                for l, val in items:
                    others = ", ".join(x for x in lines if x != str(l))
                    add_report(report, l, col, val, val,
                               f"duplicate {col.replace('_', ' ')} (also on line {others})")

    if opts["sort"] != "none":
        k = opts["sort"]
        out_rows.sort(key=lambda e: (e[2][k] == "", natural_key(e[2][k])))  # stable sort
    sort_report(report)
    return {"has_header": has_header,
            "header": records[0][1] if has_header else None,
            "out_rows": out_rows,
            "report": report}


def render_tsv(header, rows) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf, delimiter="\t", lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def render_output(out_rows) -> bytes:
    return render_tsv(OUTPUT_HEADER, ([rec[c] for c in COLUMNS] for _, _, rec in out_rows))
```

The output is rendered to bytes in memory and written with `write_bytes`. That way, the hash recorded in the manifest is guaranteed to match the file on disk, with no newline translation by the OS.

## 3. Build the manifest

```python
def build_manifest(paths, src_bytes, enc, opts, res, out_bytes, rep_bytes, check_links):
    man_dir = paths["manifest"].resolve().parent
    rel = lambda p: os.path.relpath(p.resolve(), man_dir)
    return {
        "manifest_version": MANIFEST_VERSION,
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool": {
            "name": "standardize_inventory.py",
            "version": SCRIPT_VERSION,
            "sha256": sha256_file(Path(__file__).resolve()),
            "python": platform.python_version(),
            "unicode_version": unicodedata.unidata_version,  # affects NFC/NFKC results
        },
        "options": opts,
        "source": {
            "path": rel(paths["input"]),
            "sha256": sha256_bytes(src_bytes),
            "bytes": len(src_bytes),
            "encoding": enc,
            "has_header": res["has_header"],
            "header": res["header"],
            "data_rows": len(res["out_rows"]),
        },
        "output": {"path": rel(paths["output"]), "sha256": sha256_bytes(out_bytes),
                   "rows": len(res["out_rows"])},
        "report": {"path": rel(paths["report"]), "sha256": sha256_bytes(rep_bytes),
                   "includes_link_check": check_links},
        # One entry per output row, in output order (so it survives --sort)
        "rows": [
            {"line": line,
             "source_sha256": row_hash(raw_cells),
             "output_sha256": row_hash([rec[c] for c in COLUMNS])}
            for line, raw_cells, rec in res["out_rows"]
        ],
    }
```

## 4. Verify mode

```python
def verify(manifest_path, source_override=None, output_override=None, reproduce=True):
    mpath = Path(manifest_path)
    m = json.loads(mpath.read_text(encoding="utf-8"))
    base = mpath.parent
    src_path = Path(source_override) if source_override else base / m["source"]["path"]
    out_path = Path(output_override) if output_override else base / m["output"]["path"]
    rep_path = base / m["report"]["path"]
    failures = 0

    def result(ok, label, details=()):
        nonlocal failures
        failures += not ok
        print(f"[{'OK  ' if ok else 'FAIL'}] {label}")
        for d in list(details)[:25]:
            print(f"         {d}")
        if len(details) > 25:
            print(f"         ... and {len(details) - 25} more")

    # 1. Source file
    src_bytes = src_path.read_bytes()
    src_ok = sha256_bytes(src_bytes) == m["source"]["sha256"]
    details = []
    if not src_ok:
        try:
            recs = parse_records(src_bytes.decode(m["source"]["encoding"]))
            recs = recs[1:] if m["source"]["has_header"] else recs
            current = [(line, row_hash(cells)) for line, cells in recs]
            expected = Counter(r["source_sha256"] for r in m["rows"])
            found = Counter(h for _, h in current)
            gone, new = expected - found, found - expected
            for r in sorted(m["rows"], key=lambda r: r["line"]):
                if gone[r["source_sha256"]] > 0:
                    gone[r["source_sha256"]] -= 1
                    details.append(f"source line {r['line']} (at standardization time) changed or removed")
            for line, h in current:
                if new[h] > 0:
                    new[h] -= 1
                    details.append(f"current source line {line} is new or modified")
            if not details:
                details.append("all data rows intact; difference is in header, blank lines, "
                               "line endings, or encoding")
        except UnicodeDecodeError:
            details.append(f"source no longer decodes as {m['source']['encoding']}")
    result(src_ok, f"source file matches manifest ({src_path.name})", details)

    # 2. Output file (position-based, so each edit maps back to its source line)
    out_bytes = out_path.read_bytes()
    out_ok = sha256_bytes(out_bytes) == m["output"]["sha256"]
    details = []
    if not out_ok:
        out_recs = parse_records(out_bytes.decode("utf-8", errors="replace"), skip_blank=False)[1:]
        for i, (meta, (_, cells)) in enumerate(zip(m["rows"], out_recs), 1):
            if row_hash(cells) != meta["output_sha256"]:
                details.append(f"output row {i} (from source line {meta['line']}) was edited")
        if len(out_recs) != len(m["rows"]):
            details.append(f"output has {len(out_recs)} rows; manifest expects {len(m['rows'])}")
    result(out_ok, f"output file matches manifest ({out_path.name})", details)

    # 3. Report file (tamper check only)
    if rep_path.exists():
        result(sha256_file(rep_path) == m["report"]["sha256"],
               f"report file matches manifest ({rep_path.name})")

    # 4. Reproduce the transformation
    if reproduce:
        if not src_ok:
            print("[SKIP] reproduction: source file has changed")
        else:
            tool = m["tool"]
            if sha256_file(Path(__file__).resolve()) != tool["sha256"]:
                print(f"[WARN] script differs from the one that made this manifest "
                      f"(v{tool['version']}); output may legitimately differ")
            if unicodedata.unidata_version != tool["unicode_version"]:
                print(f"[WARN] Unicode database {unicodedata.unidata_version} != "
                      f"{tool['unicode_version']}")
            res = run_pipeline(src_bytes.decode(m["source"]["encoding"]), m["options"])
            result(sha256_bytes(render_output(res["out_rows"])) == m["output"]["sha256"],
                   "re-running standardization reproduces the recorded output")
            if not m["report"]["includes_link_check"]:
                result(sha256_bytes(render_tsv(REPORT_HEADER, res["report"])) == m["report"]["sha256"],
                       "re-running standardization reproduces the recorded report")

    print("\nVerification", "PASSED" if failures == 0 else f"FAILED ({failures} check(s))")
    return 0 if failures == 0 else 1
```

## 5. New `main()` and CLI options

```python
def parse_args():
    p = argparse.ArgumentParser(description="Standardize a museum inventory TSV.")
    p.add_argument("input", nargs="?",
                   help="input .tsv (with --verify: optional override of the source path)")
    p.add_argument("-o", "--output")
    p.add_argument("-r", "--report")
    p.add_argument("-m", "--manifest", help="manifest path (default: <input>_manifest.json)")
    p.add_argument("--verify", metavar="MANIFEST", help="verify files against a manifest")
    p.add_argument("--no-reproduce", action="store_true",
                   help="with --verify, skip re-running the transformation")
    # ... existing options unchanged: --dayfirst, --objnum-sep, --objnum-upper,
    #     --ascii-quotes, --keep-http, --check-links, --timeout, --sort
    return p.parse_args()


def main():
    args = parse_args()
    if args.verify:
        sys.exit(verify(args.verify, args.input, args.output, not args.no_reproduce))
    if not args.input:
        sys.exit("An input file is required (or use --verify MANIFEST).")

    in_path = Path(args.input)
    stem = in_path.with_name(in_path.stem)
    paths = {
        "input": in_path,
        "output": Path(args.output or f"{stem}_standardized.tsv"),
        "report": Path(args.report or f"{stem}_report.tsv"),
        "manifest": Path(args.manifest or f"{stem}_manifest.json"),
    }

    src_bytes = in_path.read_bytes()
    text, enc = decode_bytes(src_bytes)
    opts = {k: getattr(args, k) for k in TRANSFORM_OPTIONS}
    res = run_pipeline(text, opts)

    # Network results go only into the report, never the output, so the
    # output stays reproducible.
    if args.check_links:
        urls = sorted({rec["link"] for _, _, rec in res["out_rows"] if rec["link"].startswith("http")})
        results = check_links(urls, timeout=args.timeout)
        for line, _, rec in res["out_rows"]:
            if results.get(rec["link"]):
                add_report(res["report"], line, "link", rec["link"], rec["link"], results[rec["link"]])
        sort_report(res["report"])

    out_bytes = render_output(res["out_rows"])
    rep_bytes = render_tsv(REPORT_HEADER, res["report"])
    paths["output"].write_bytes(out_bytes)
    paths["report"].write_bytes(rep_bytes)

    manifest = build_manifest(paths, src_bytes, enc, opts, res, out_bytes, rep_bytes, args.check_links)
    man_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    paths["manifest"].write_bytes(man_bytes)

    print(f"Read {len(res['out_rows'])} rows (encoding: {enc})")
    print(f"Output:   {paths['output']}  sha256={manifest['output']['sha256'][:16]}…")
    print(f"Report:   {paths['report']}")
    print(f"Manifest: {paths['manifest']}  sha256={sha256_bytes(man_bytes)}")
    print("Record the manifest hash somewhere separate (e.g., your collections system).")
```

## Example manifest

```json
{
  "manifest_version": 1,
  "created": "2025-01-14T16:02:11+00:00",
  "tool": { "name": "standardize_inventory.py", "version": "1.1.0",
            "sha256": "9f2c…", "python": "3.12.1", "unicode_version": "15.0.0" },
  "options": { "dayfirst": false, "objnum_sep": ".", "objnum_upper": false,
               "ascii_quotes": false, "keep_http": false, "sort": "object_number" },
  "source": { "path": "inventory.tsv", "sha256": "4b1e…", "bytes": 182344,
              "encoding": "cp1252", "has_header": true,
              "header": ["Date", "Title", "Accession No.", "URL"], "data_rows": 2210 },
  "output": { "path": "inventory_standardized.tsv", "sha256": "e07a…", "rows": 2210 },
  "report": { "path": "inventory_report.tsv", "sha256": "71cd…", "includes_link_check": false },
  "rows": [
    { "line": 2, "source_sha256": "a3f9…", "output_sha256": "0c4d…" },
    { "line": 3, "source_sha256": "5be2…", "output_sha256": "d81a…" }
  ]
}
```

## Example verification run

```
$ python standardize_inventory.py --verify inventory_manifest.json
[OK  ] source file matches manifest (inventory.tsv)
[FAIL] output file matches manifest (inventory_standardized.tsv)
         output row 412 (from source line 87) was edited
[OK  ] report file matches manifest (inventory_report.tsv)
[OK  ] re-running standardization reproduces the recorded output

Verification FAILED (1 check(s))
```

You can also verify a newly exported source file against the old manifest:

```
$ python standardize_inventory.py --verify inventory_manifest.json new_export.tsv
[FAIL] source file matches manifest (new_export.tsv)
         source line 87 (at standardization time) changed or removed
         current source line 88 is new or modified
```

## Design notes

- **Files are hashed as bytes; rows are hashed as parsed cells.** The file hash catches everything. The row hashes stay meaningful after a re-export changes line endings or shifts line numbers, so verification matches rows by hash instead of by position.
- **The output is reproducible by design.** The manifest records the script's own hash, the options, and the Unicode version, because a newer Python can change NFC/NFKC results. Link checking is kept out of the output so the network can't break reproducibility.
- **Sorting is safe.** Manifest rows are stored in output order, and each one carries its original source line.
- **Checksums detect change; they don't prevent forgery.** Someone who edits the output could also regenerate the manifest. For real tamper evidence:
  - Store the printed manifest hash somewhere independent, such as the collections management system or a ticket.
  - Or sign the manifest, e.g. `gpg --detach-sign inventory_manifest.json`.
- **Chaining.** If the standardized file later becomes the source for another step, that step's manifest records this output's hash. This gives you an auditable lineage from the original export to the final dataset.
- **Alternative: a checksum column.** You could add a 5th column with the source row hash, making each row self-verifying. That breaks the 4-column schema and pushes hashes into downstream systems, which is why a sidecar manifest is the better default.
