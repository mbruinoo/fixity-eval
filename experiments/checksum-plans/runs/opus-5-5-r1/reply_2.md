I'd use checksums at three levels, each answering a different question later on:

| Level | What gets hashed | Question it answers |
|---|---|---|
| **File** | SHA-256 of the raw bytes of the source, standardized output, report, and lineage files | Has any file changed since the run? |
| **Row** | SHA-256 of each source row and each output row, linked in a lineage file | *Which* rows changed? Where did each output row come from? |
| **Process** | SHA-256 of the script itself, plus the exact options and environment | Can I regenerate the output from the source and get a byte-identical result? |

All of this goes into a **manifest** (a JSON file written after each run). A `--verify` mode reads the manifest and checks everything.

## Design decisions

1. **The output must be deterministic.** No timestamps or run-specific data go in the standardized file, only in the manifest. Given the same source, script, and options, the output bytes must always be identical. Otherwise reproducibility checks are meaningless.
2. **Hash exactly the bytes that were parsed.** The source is read once as bytes, hashed, and then decoded. This avoids any gap between "the file we hashed" and "the file we processed."
3. **Use an unambiguous row encoding.** Rows are hashed as JSON arrays, so `["a\tb"]` and `["a", "b"]` produce different hashes. Joining cells with tabs would make them identical.
4. **Use a separate lineage file instead of extra columns.** It maps each source row (line number and hash) to its output row (line number and hash), with a status: `kept`, `blank_removed`, `duplicate_removed`, or `header`. Every source row is accounted for, even dropped ones, and the inventory itself stays clean.
5. **Separate file hashes from content hashes.** If someone re-saves the source in Excel, the file hash changes but the row hashes may not. Verification can then tell you "the content is identical; only the encoding or line endings changed." That is very different from "row 47 was edited."
6. **Record the environment.** Unicode normalization (NFC) depends on Python's Unicode database version, so the manifest records it along with the script hash and version.

## Code changes

Add these imports at the top of the script:

```python
import hashlib
import io
import json
import os
import platform
```

Keep the configuration, helpers, and the four `normalize_*` functions exactly as they are. Then **replace everything from the `# I/O` section to the end of the file** with the following:

```python
# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

SCRIPT_VERSION = "1.1.0"
MANIFEST_VERSION = 1

OPTION_KEYS = ["no_header", "dayfirst", "unify_separators", "keep_http",
               "drop_duplicates", "sort", "header_style"]

OUTPUT_HEADERS = {
    "title": ["Date", "Title", "Object Number", "Link"],
    "snake": CANONICAL_HEADERS,
}
REPORT_FIELDS = ["line", "column", "original", "standardized", "note"]
LINEAGE_FIELDS = ["source_line", "source_row_sha256", "status",
                  "output_line", "output_row_sha256", "note"]


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def row_hash(cells):
    """Hash a row's cell values using an unambiguous JSON encoding."""
    canonical = json.dumps([str(c) for c in cells], ensure_ascii=False,
                           separators=(",", ":"))
    return sha256_bytes(canonical.encode("utf-8"))

# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def read_tsv(path):
    """Read bytes once, so the hash covers exactly what was parsed."""
    raw = Path(path).read_bytes()
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    rows = list(csv.reader(io.StringIO(text, newline=""), delimiter="\t"))
    return rows, encoding, raw


def render_tsv(header, rows):
    """Render to bytes in memory so we can hash before (or instead of) writing."""
    buf = io.StringIO()
    w = csv.writer(buf, delimiter="\t", lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def map_headers(header_row):
    mapping = {}
    for idx, h in enumerate(header_row):
        canon = HEADER_ALIASES.get(header_key(h))
        if canon and canon not in mapping:
            mapping[canon] = idx
    return mapping if len(mapping) >= 2 else None

# ---------------------------------------------------------------------------
# Pipeline (deterministic: same rows + same options -> same bytes)
# ---------------------------------------------------------------------------

def standardize(rows, opts):
    report, lineage, warnings = [], [], []
    out_header = OUTPUT_HEADERS[opts["header_style"]]

    if opts["no_header"]:
        col_map = {name: i for i, name in enumerate(CANONICAL_HEADERS)}
        data_rows, first_line = rows, 1
        src_header_line, src_header_hash = "", ""
    else:
        col_map = map_headers(rows[0]) if rows else None
        if col_map is None:
            warnings.append("headers not recognized; assuming column order "
                            "date, title, object number, link")
            col_map = {name: i for i, name in enumerate(CANONICAL_HEADERS)}
        for name in CANONICAL_HEADERS:
            if name not in col_map:
                warnings.append(f"no '{name}' column found; it will be left blank")
        data_rows, first_line = rows[1:], 2
        src_header_line, src_header_hash = 1, row_hash(rows[0])

    lineage.append({"source_line": src_header_line, "source_row_sha256": src_header_hash,
                    "status": "header", "output_line": 1,
                    "output_row_sha256": row_hash(out_header), "note": ""})

    normalizers = {
        "date": lambda v: normalize_date(v, dayfirst=opts["dayfirst"]),
        "title": normalize_title,
        "object_number": lambda v: normalize_object_number(v, opts["unify_separators"]),
        "link": lambda v: normalize_link(v, force_https=not opts["keep_http"]),
    }

    cleaned = []
    for offset, row in enumerate(data_rows):
        line_no = first_line + offset
        src_hash = row_hash(row)

        if not any(cell.strip() for cell in row):
            report.append((line_no, "", "", "", "blank row removed"))
            lineage.append({"source_line": line_no, "source_row_sha256": src_hash,
                            "status": "blank_removed", "output_line": "",
                            "output_row_sha256": "", "note": ""})
            continue

        expected = max(col_map.values()) + 1
        if len(row) > expected and any(c.strip() for c in row[expected:]):
            report.append((line_no, "", "\t".join(row), "",
                           f"row has {len(row)} fields; extra fields ignored"))

        record = {"_line": line_no, "_src_hash": src_hash}
        for name in CANONICAL_HEADERS:
            idx = col_map.get(name)
            original = row[idx] if idx is not None and idx < len(row) else ""
            value, issues = normalizers[name](original)
            record[name] = value
            if value != original:
                report.append((line_no, name, original, value, "changed"))
            for issue in issues:
                report.append((line_no, name, original, value, issue))
        cleaned.append(record)

    if opts["drop_duplicates"]:
        seen, unique = {}, []
        for rec in cleaned:
            key = tuple(rec[c] for c in CANONICAL_HEADERS)
            if key in seen:
                report.append((rec["_line"], "", "", "", "exact duplicate row removed"))
                lineage.append({"source_line": rec["_line"], "source_row_sha256": rec["_src_hash"],
                                "status": "duplicate_removed", "output_line": "",
                                "output_row_sha256": "",
                                "note": f"duplicate of source line {seen[key]}"})
            else:
                seen[key] = rec["_line"]
                unique.append(rec)
        cleaned = unique

    by_number = defaultdict(list)
    for rec in cleaned:
        if rec["object_number"]:
            by_number[rec["object_number"]].append(rec["_line"])
    for number, lines in by_number.items():
        if len(lines) > 1:
            for ln in lines:
                others = ", ".join(str(x) for x in lines if x != ln)
                report.append((ln, "object_number", number, number,
                               f"duplicate object number (also on line {others})"))

    # Python's sort is stable, so ties keep source order (deterministic).
    if opts["sort"] == "object":
        cleaned.sort(key=lambda r: natural_key(r["object_number"]))
    elif opts["sort"] == "title":
        cleaned.sort(key=lambda r: r["title"].lower())
    elif opts["sort"] == "date":
        def date_key(r):
            m = re.search(r"\d{3,4}", r["date"])
            return (0, int(m.group()), r["date"]) if m else (1, 0, r["date"])
        cleaned.sort(key=date_key)

    out_rows = []
    for out_line, rec in enumerate(cleaned, start=2):
        values = [rec[c] for c in CANONICAL_HEADERS]
        out_rows.append(values)
        lineage.append({"source_line": rec["_line"], "source_row_sha256": rec["_src_hash"],
                        "status": "kept", "output_line": out_line,
                        "output_row_sha256": row_hash(values), "note": ""})

    lineage.sort(key=lambda r: (r["source_line"] == "", r["source_line"] or 0))
    report.sort(key=lambda r: (r[0], r[1]))

    return {
        "standardized": render_tsv(out_header, out_rows),
        "report": render_tsv(REPORT_FIELDS, report),
        "lineage": render_tsv(LINEAGE_FIELDS, [[r[f] for f in LINEAGE_FIELDS] for r in lineage]),
        "n_data_rows": len(data_rows),
        "n_output_rows": len(out_rows),
        "report_rows": report,
        "warnings": warnings,
    }

# ---------------------------------------------------------------------------
# Run: standardize and write manifest
# ---------------------------------------------------------------------------

def relpath(path, base):
    try:
        return os.path.relpath(Path(path).resolve(), Path(base).resolve())
    except ValueError:                      # e.g. different drives on Windows
        return str(Path(path).resolve())


def run(args):
    opts = {k: getattr(args, k) for k in OPTION_KEYS}
    rows, encoding, raw = read_tsv(args.input)
    if not rows:
        sys.exit("Input file is empty.")

    result = standardize(rows, opts)
    for w in result["warnings"]:
        print(f"Warning: {w}", file=sys.stderr)

    stem = args.input.stem
    paths = {
        "standardized": args.output or args.input.with_name(f"{stem}_standardized.tsv"),
        "report": args.report or args.input.with_name(f"{stem}_report.tsv"),
        "lineage": args.lineage or args.input.with_name(f"{stem}_lineage.tsv"),
    }
    man_path = args.manifest or args.input.with_name(f"{stem}_manifest.json")

    for label, path in paths.items():
        path.write_bytes(result[label])

    base = man_path.parent
    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "tool": {
            "name": Path(__file__).name,
            "version": SCRIPT_VERSION,
            "sha256": sha256_file(Path(__file__)),
            "python": platform.python_version(),
            "unicode_data": unicodedata.unidata_version,
        },
        "options": opts,
        "source": {
            "path": relpath(args.input, base),
            "sha256": sha256_bytes(raw),
            "bytes": len(raw),
            "encoding": encoding,
            "data_rows": result["n_data_rows"],
        },
        "outputs": {
            label: {
                "path": relpath(path, base),
                "sha256": sha256_bytes(result[label]),
                "bytes": len(result[label]),
            }
            for label, path in paths.items()
        },
    }
    manifest["outputs"]["standardized"]["data_rows"] = result["n_output_rows"]
    man_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")

    notes = Counter("duplicate object number" if r[4].startswith("duplicate object") else r[4]
                    for r in result["report_rows"])
    print(f"Read {result['n_data_rows']} data rows ({encoding}); "
          f"wrote {result['n_output_rows']} rows to {paths['standardized']}")
    print(f"Report:   {paths['report']}\nLineage:  {paths['lineage']}\nManifest: {man_path}")
    for note, count in notes.most_common():
        print(f"  {count:>5}  {note}")

# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------

def diff_rows(path, lineage, line_key, hash_key):
    """Compare each row of a file against the hashes recorded in the lineage."""
    rows, _, _ = read_tsv(path)
    expected = {int(r[line_key]): r[hash_key] for r in lineage if r[line_key]}
    changed = [ln for ln, h in sorted(expected.items())
               if ln > len(rows) or row_hash(rows[ln - 1]) != h]
    return changed, max(expected, default=0), len(rows)


def verify(manifest_path):
    manifest_path = Path(manifest_path)
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    base = manifest_path.parent
    failures = 0

    def check(label, ok, msg):
        nonlocal failures
        print(f"[{'PASS' if ok else 'FAIL'}] {label}: {msg}")
        failures += 0 if ok else 1

    def warn(label, msg):
        print(f"[WARN] {label}: {msg}")

    # 1. Tool and environment
    tool = m["tool"]
    tool_changed = sha256_file(Path(__file__)) != tool["sha256"]
    if tool_changed:
        warn("tool", f"this script differs from the one that produced the files "
                     f"(manifest: v{tool['version']}, current: v{SCRIPT_VERSION})")
    if unicodedata.unidata_version != tool["unicode_data"]:
        warn("environment", f"Unicode data {unicodedata.unidata_version} vs "
                            f"{tool['unicode_data']} at creation; normalization may differ")

    # 2. File-level integrity
    entries = {"source": m["source"], **m["outputs"]}
    intact, paths = {}, {}
    for label, info in entries.items():
        p = base / info["path"]
        paths[label] = p
        if not p.exists():
            intact[label] = None
            check(label, False, f"file missing ({p})")
            continue
        actual = sha256_file(p)
        intact[label] = actual == info["sha256"]
        check(label, intact[label], "sha256 matches" if intact[label] else
              f"sha256 mismatch (expected {info['sha256'][:12]}…, got {actual[:12]}…)")

    # 3. Row-level diagnosis for any changed source/output file
    lineage = None
    if intact.get("lineage"):
        lrows, _, _ = read_tsv(paths["lineage"])
        lineage = [dict(zip(lrows[0], r)) for r in lrows[1:]]

    for label, line_key, hash_key in [("source", "source_line", "source_row_sha256"),
                                      ("standardized", "output_line", "output_row_sha256")]:
        if intact.get(label) is not False:
            continue
        if lineage is None:
            warn(label, "cannot locate changed rows: lineage file missing or altered")
            continue
        changed, expected_n, actual_n = diff_rows(paths[label], lineage, line_key, hash_key)
        if not changed and expected_n == actual_n:
            warn(label, "every row is identical; only encoding, line endings, "
                        "or quoting changed")
        else:
            shown = ", ".join(map(str, changed[:20])) + (" …" if len(changed) > 20 else "")
            print(f"       {len(changed)} changed row(s){': lines ' + shown if changed else ''}")
            if expected_n != actual_n:
                print(f"       row count changed: {expected_n} → {actual_n}")

    # 4. Reproducibility: re-run the pipeline on the source in memory
    if intact.get("source") is not None:
        rows, _, _ = read_tsv(paths["source"])
        result = standardize(rows, m["options"])
        for label in ("standardized", "report", "lineage"):
            same = sha256_bytes(result[label]) == m["outputs"][label]["sha256"]
            name = f"reproduce {label}"
            if same:
                check(name, True, "regenerated from source; byte-identical")
            elif not intact["source"]:
                warn(name, "differs (expected, since the source has changed)")
            elif tool_changed:
                warn(name, "differs, probably because the script has changed")
            else:
                check(name, False, "differs even though the source and script are unchanged")

    print(f"\n{'VERIFIED' if failures == 0 else f'FAILED ({failures} problem(s))'}")
    return failures == 0

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Standardize a museum inventory TSV.")
    ap.add_argument("input", type=Path, nargs="?")
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("-r", "--report", type=Path)
    ap.add_argument("--lineage", type=Path, help="row lineage TSV (default: <input>_lineage.tsv)")
    ap.add_argument("--manifest", type=Path, help="checksum manifest (default: <input>_manifest.json)")
    ap.add_argument("--verify", type=Path, metavar="MANIFEST",
                    help="verify files against a manifest instead of standardizing")
    ap.add_argument("--no-header", action="store_true")
    ap.add_argument("--dayfirst", action="store_true")
    ap.add_argument("--unify-separators", action="store_true")
    ap.add_argument("--keep-http", action="store_true")
    ap.add_argument("--drop-duplicates", action="store_true")
    ap.add_argument("--sort", choices=["none", "object", "date", "title"], default="none")
    ap.add_argument("--header-style", choices=["snake", "title"], default="title")
    args = ap.parse_args()

    if args.verify:
        sys.exit(0 if verify(args.verify) else 1)
    if not args.input:
        ap.error("input is required unless --verify is used")
    run(args)


if __name__ == "__main__":
    main()
```

## Usage

```bash
# Standardize; writes the output, report, lineage, and manifest
python standardize_inventory.py inventory.tsv --sort object

# Later, check everything (exit code 0 = verified, 1 = problems)
python standardize_inventory.py --verify inventory_manifest.json
```

**Manifest (`inventory_manifest.json`):**
```json
{
  "manifest_version": 1,
  "created_utc": "2025-01-15T14:02:11+00:00",
  "tool": {
    "name": "standardize_inventory.py",
    "version": "1.1.0",
    "sha256": "9f2c4e…",
    "python": "3.12.1",
    "unicode_data": "15.0.0"
  },
  "options": { "no_header": false, "dayfirst": false, "unify_separators": false,
               "keep_http": false, "drop_duplicates": false, "sort": "object",
               "header_style": "title" },
  "source": { "path": "inventory.tsv", "sha256": "3a7bd3…", "bytes": 512,
              "encoding": "utf-8-sig", "data_rows": 6 },
  "outputs": {
    "standardized": { "path": "inventory_standardized.tsv", "sha256": "c01f88…", "bytes": 431, "data_rows": 6 },
    "report":       { "path": "inventory_report.tsv",       "sha256": "e4d909…", "bytes": 1290 },
    "lineage":      { "path": "inventory_lineage.tsv",      "sha256": "71a6f2…", "bytes": 1105 }
  }
}
```

**Lineage (`inventory_lineage.tsv`):**
```
source_line  source_row_sha256  status  output_line  output_row_sha256  note
1            5e88…              header  1            aa31…
2            b4c1…              kept    2            0d7e…
3            19fa…              kept    3            c2b8…
4            7d02…              kept    7            f81a…
...
```

**Verifying after someone edited the output by hand:**
```
[PASS] source: sha256 matches
[FAIL] standardized: sha256 mismatch (expected c01f88a2b3d4…, got 8e1d07c9f2a1…)
       1 changed row(s): lines 4
[PASS] report: sha256 matches
[PASS] lineage: sha256 matches
[PASS] reproduce standardized: regenerated from source; byte-identical
[PASS] reproduce report: regenerated from source; byte-identical
[PASS] reproduce lineage: regenerated from source; byte-identical

FAILED (1 problem(s))
```

This tells you the source is fine, the pipeline still reproduces the original result, and line 4 of the output was changed after the run. You can restore that row by re-running, or treat the edit as a deliberate correction and document it.

## Practical considerations

- **Checksums detect changes; they don't prove who made them.** Anyone who can edit the files can also regenerate the manifest. For real tamper evidence:
  - Store the manifest somewhere separate and write-protected, such as your collections management system or a records repository.
  - Or sign it, e.g. `gpg --detach-sign inventory_manifest.json`.
  - Or commit everything to version control, which gives you a hash-chained history for free.
- **Watch line-ending conversion.** Git's `autocrlf`, email, and some sync tools silently convert `\n` to `\r\n`, which breaks file hashes. In Git, add `*.tsv binary` (or `*.tsv -text`) to `.gitattributes`. The row-level check will still identify this as a formatting-only change rather than a content change.
- **Keep the source file.** Verification and reproduction require the original. Archive it alongside the outputs, ideally read-only.
- **Use SHA-256, not MD5 or SHA-1.** Both older algorithms have practical collision attacks.
- **For archival packaging,** consider wrapping the source, outputs, and manifest in a [BagIt](https://datatracker.ietf.org/doc/html/rfc8493) bag. It's the standard checksum-manifest format in libraries and archives, and many digital preservation systems can validate it directly. Python's `bagit` package handles this.
- **Bump `SCRIPT_VERSION`** whenever you change the normalization rules. The script hash catches any change anyway, but a readable version number makes the manifest easier to interpret.
