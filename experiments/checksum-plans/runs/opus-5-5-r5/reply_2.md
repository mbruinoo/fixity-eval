## Approach

Checksums can answer three different questions later. Each needs something different recorded at standardization time:

| Question | What to record |
|---|---|
| **Integrity:** Has the source or the output been altered since standardization? | SHA-256 of each file's exact bytes |
| **Traceability:** Which source row produced this output row, and has that row changed? | A per-row ledger linking a hash of each source row to a hash of its output row |
| **Reproducibility:** Would re-running the script on the source give the same output? | The script's own hash, its version, and every option that affects output |

These go into two sidecar files written next to the output:

- **`*.ledger.tsv`**: one line per source record. It accounts for every record, including blank rows that were skipped and duplicates that were dropped.
- **`*.manifest.json`**: file hashes, the script hash, the options used, row counts, and the ledger's hash. This is the one file you need to keep safe.

The standardized TSV itself stays clean, so it can still be imported into a collections management system. Embedding hashes in it is optional, covered at the end.

## Design details

1. **Hash rows in a canonical form.** Joining cells with tabs is ambiguous: `["a\tb", "c"]` and `["a", "b\tc"]` produce the same string. Instead, hash a JSON array of the cells.
2. **Hash source rows as raw cells.** Use the cells exactly as read, before any cleaning, so the hash describes the source and not the script's interpretation of it.
3. **Hash output rows as written.** Use the exact string values written to the file, including the year columns if they're enabled.
4. **Use record numbers, not physical line numbers.** A quoted cell can contain a line break, so "line 5" is ambiguous. The ledger uses `source_record` instead.
5. **Make output deterministic.** Use a fixed encoding and line endings, a stable sort, and no timestamps inside the TSV. This is what makes reproduction possible. The timestamp goes in the manifest.
6. **Add an order-independent digest.** A hash of the sorted row hashes verifies the content even if someone re-sorts the output file.

## Code changes

### 1. Hash helpers (add near the top)

```python
import hashlib
import json
import os
import platform
from argparse import Namespace
from datetime import timezone

SCRIPT_VERSION = "1.1.0"

# Options that affect output content; recorded so a run can be reproduced exactly.
OUTPUT_AFFECTING_OPTIONS = ["no_header", "dayfirst", "range_sep", "add_year_columns",
                            "fix_caps", "upper_object_numbers", "force_https",
                            "drop_duplicate_rows", "sort_by", "bom"]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def row_hash(cells):
    """Unambiguous hash of a list of cell strings."""
    canon = json.dumps([str(c) for c in cells], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def content_digest(row_hashes):
    """Order-independent digest of a dataset's rows."""
    return sha256_bytes("\n".join(sorted(row_hashes)).encode("ascii"))
```

### 2. Refactor `main()` so processing is reusable

Verification needs to re-run the standardization in memory without writing files. To allow that, split `main()` into three parts:

- `process()`: standardizes rows and builds the ledger.
- `render()`: turns the result into the exact bytes that will be written.
- `main()`: writes the files.

`read_tsv` also needs to return the raw bytes:

```python
def read_tsv(path, encoding=None):
    with open(path, "rb") as f:
        data = f.read()
    encodings = [encoding] if encoding else ["utf-8-sig", "cp1252", "latin-1"]
    for enc in encodings:
        try:
            text = data.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    rows = list(csv.reader(io.StringIO(text, newline=""), delimiter="\t"))
    return rows, enc, data


def process(rows, args):
    """Standardize rows. Returns (header, table, issues, ledger, meta)."""
    mapping = None if args.no_header else map_header(rows[0])
    if mapping:
        header_row, data_rows, start_record = rows[0], rows[1:], 2
    else:
        mapping = {c: i for i, c in enumerate(CANONICAL)}
        header_row, data_rows, start_record = None, rows, 1

    issues, ledger, out_rows = [], [], []

    for offset, row in enumerate(data_rows):
        rec = start_record + offset
        src_hash = row_hash(row)                     # hash raw cells, before cleaning

        if not any(cell.strip() for cell in row):
            ledger.append({"source_record": rec, "status": "skipped_blank",
                           "source_row_sha256": src_hash,
                           "output_row": "", "output_row_sha256": ""})
            continue

        # ... existing standardization code (unchanged) producing date_val, lo, hi,
        #     title_val, obj_val, link_val and logging issues ...

        out_rows.append({"line": rec, "src_hash": src_hash,
                         "date": date_val, "title": title_val,
                         "object_number": obj_val, "link": link_val,
                         "lo": lo, "hi": hi})

    if args.drop_duplicate_rows:
        seen, deduped = {}, []
        for r in out_rows:
            key = tuple(r[c] for c in CANONICAL)
            if key in seen:
                ledger.append({"source_record": r["line"],
                               "status": f"dropped_duplicate_of_{seen[key]}",
                               "source_row_sha256": r["src_hash"],
                               "output_row": "", "output_row_sha256": ""})
                continue
            seen[key] = r["line"]
            deduped.append(r)
        out_rows = deduped

    # ... existing duplicate-object-number check and sorting (unchanged) ...

    header = [OUTPUT_HEADERS[c] for c in CANONICAL]
    if args.add_year_columns:
        header += ["Earliest Year", "Latest Year"]

    table = []
    for i, r in enumerate(out_rows, start=1):        # after sorting: final positions
        vals = [r[c] for c in CANONICAL]
        if args.add_year_columns:
            vals += [r["lo"], r["hi"]]
        vals = ["" if v is None else str(v) for v in vals]
        table.append(vals)
        ledger.append({"source_record": r["line"], "status": "kept",
                       "source_row_sha256": r["src_hash"],
                       "output_row": i, "output_row_sha256": row_hash(vals)})

    ledger.sort(key=lambda e: e["source_record"])
    meta = {"header_sha256": row_hash(header_row) if header_row else None,
            "start_record": start_record,
            "data_records": len(data_rows)}
    return header, table, issues, ledger, meta


def render(header, table, bom=False):
    """Exact bytes of the output file, so its hash can be computed without writing."""
    buf = io.StringIO(newline="")
    w = csv.writer(buf, delimiter="\t", lineterminator="\n")
    w.writerow(header)
    w.writerows(table)
    return buf.getvalue().encode("utf-8-sig" if bom else "utf-8")
```

### 3. Write the output, ledger, and manifest

```python
LEDGER_FIELDS = ["source_record", "status", "source_row_sha256",
                 "output_row", "output_row_sha256"]


def write_outputs(args):
    rows, encoding, raw = read_tsv(args.input)
    header, table, issues, ledger, meta = process(rows, args)

    out_path = args.output or re.sub(r"(\.tsv|\.txt)?$", "_standardized.tsv",
                                     args.input, count=1, flags=re.I)
    ledger_path = args.ledger or re.sub(r"\.tsv$", "", out_path) + ".ledger.tsv"
    manifest_path = args.manifest or re.sub(r"\.tsv$", "", out_path) + ".manifest.json"

    out_bytes = render(header, table, args.bom)
    with open(out_path, "wb") as f:
        f.write(out_bytes)

    with open(ledger_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(ledger)

    # ... existing report writing / console summary ...

    mdir = os.path.dirname(os.path.abspath(manifest_path))
    rel = lambda p: os.path.relpath(os.path.abspath(p), mdir)   # portable if folder moves
    kept = [e["output_row_sha256"] for e in ledger if e["status"] == "kept"]

    manifest = {
        "manifest_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "hash_algorithm": "sha256",
        "row_hash_method": "sha256 of compact JSON array of cell strings (UTF-8)",
        "script": {"name": os.path.basename(__file__), "version": SCRIPT_VERSION,
                   "sha256": sha256_file(__file__)},
        "python": platform.python_version(),
        "options": {k: getattr(args, k) for k in OUTPUT_AFFECTING_OPTIONS},
        "source": {"path": rel(args.input), "sha256": sha256_bytes(raw),
                   "bytes": len(raw), "encoding": encoding,
                   "header_sha256": meta["header_sha256"],
                   "start_record": meta["start_record"],
                   "data_records": meta["data_records"]},
        "output": {"path": rel(out_path), "sha256": sha256_bytes(out_bytes),
                   "rows": len(table), "content_digest": content_digest(kept)},
        "ledger": {"path": rel(ledger_path), "sha256": sha256_file(ledger_path)},
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Manifest: {manifest_path}", file=sys.stderr)
```

### 4. Verification mode

When a whole-file hash fails, verification drops to row level. It reports which rows changed, rather than just that the file is different.

```python
def load_ledger(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def verify(manifest_path, source=None, output=None, reproduce=False):
    with open(manifest_path, encoding="utf-8") as f:
        m = json.load(f)
    base = os.path.dirname(os.path.abspath(manifest_path))
    resolve = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    ok = True

    def check(label, path, expected):
        nonlocal ok
        if not os.path.exists(path):
            print(f"[MISSING] {label}: {path}")
            ok = False
            return False
        if sha256_file(path) == expected:
            print(f"[OK]      {label}: {path}")
            return True
        print(f"[CHANGED] {label}: {path}")
        ok = False
        return False

    # 1. Ledger: if it was altered, row-level checks can't be trusted.
    ledger_path = resolve(m["ledger"]["path"])
    ledger_ok = check("ledger", ledger_path, m["ledger"]["sha256"])
    ledger = load_ledger(ledger_path) if os.path.exists(ledger_path) else []

    # 2. Output file, with row-level diff on failure.
    out_path = output or resolve(m["output"]["path"])
    if not check("output", out_path, m["output"]["sha256"]) and ledger_ok and os.path.exists(out_path):
        with open(out_path, encoding="utf-8-sig", newline="") as f:
            current = list(csv.reader(f, delimiter="\t"))[1:]
        expected = {int(e["output_row"]): e for e in ledger if e["status"] == "kept"}
        cur_hashes = [row_hash(r) for r in current]
        if content_digest(cur_hashes) == m["output"]["content_digest"]:
            print("          rows are identical but reordered/reformatted (content digest matches)")
        else:
            for i, r in enumerate(current, start=1):
                e = expected.get(i)
                if e is None:
                    print(f"          output row {i}: extra row not in ledger")
                elif row_hash(r) != e["output_row_sha256"]:
                    print(f"          output row {i}: edited (from source record {e['source_record']})")
            for i in sorted(set(expected) - set(range(1, len(current) + 1))):
                print(f"          output row {i}: missing (from source record {expected[i]['source_record']})")

    # 3. Source file, with record-level diff on failure.
    src_path = source or resolve(m["source"]["path"])
    if not check("source", src_path, m["source"]["sha256"]) and ledger_ok and os.path.exists(src_path):
        rows, _, _ = read_tsv(src_path, m["source"]["encoding"])
        start = m["source"]["start_record"]
        if start == 2 and row_hash(rows[0]) != m["source"]["header_sha256"]:
            print("          header row changed")
        data = rows[start - 1:]
        by_rec = {int(e["source_record"]): e for e in ledger}
        for offset, row in enumerate(data):
            rec = start + offset
            e = by_rec.get(rec)
            if e is None:
                print(f"          source record {rec}: new record")
            elif row_hash(row) != e["source_row_sha256"]:
                out = f" -> output row {e['output_row']}" if e["output_row"] else ""
                print(f"          source record {rec}: changed{out}")
        last = start + len(data) - 1
        for rec in sorted(r for r in by_rec if r > last):
            print(f"          source record {rec}: removed")

    # 4. Reproduction: re-run with recorded options and compare output bytes.
    if reproduce:
        if sha256_file(__file__) != m["script"]["sha256"]:
            print(f"[WARN]    script differs from version used ({m['script']['version']}); "
                  "a mismatch may reflect code changes, not data changes")
        rows, _, _ = read_tsv(src_path, m["source"]["encoding"])
        header, table, *_ = process(rows, Namespace(**m["options"]))
        if sha256_bytes(render(header, table, m["options"]["bom"])) == m["output"]["sha256"]:
            print("[OK]      reproduction: re-running yields byte-identical output")
        else:
            print("[FAIL]    reproduction: re-running yields different output")
            ok = False

    print("VERIFIED" if ok else "VERIFICATION FAILED")
    return ok
```

### 5. CLI wiring

```python
ap.add_argument("input", nargs="?", help="Input .tsv file")
ap.add_argument("--ledger", help="Ledger path (default: <output>.ledger.tsv)")
ap.add_argument("--manifest", help="Manifest path (default: <output>.manifest.json)")
ap.add_argument("--verify", metavar="MANIFEST", help="Verify files against a manifest")
ap.add_argument("--verify-source", help="Override source path during verification")
ap.add_argument("--verify-output", help="Override output path during verification")
ap.add_argument("--reproduce", action="store_true",
                help="With --verify: re-run standardization and compare byte-for-byte")
args = ap.parse_args()

if args.verify:
    sys.exit(0 if verify(args.verify, args.verify_source, args.verify_output, args.reproduce) else 1)
if not args.input:
    ap.error("input is required unless --verify is used")
write_outputs(args)
```

## Usage

```bash
# Standardize: writes clean.tsv, clean.ledger.tsv, clean.manifest.json
python standardize_inventory.py inventory.tsv -o clean.tsv --add-year-columns --sort-by object_number

# Later: verify. Exit code 0/1 makes it usable in scripts or scheduled checks.
python standardize_inventory.py --verify clean.manifest.json --reproduce
```

Example output after someone has edited both files:

```
[OK]      ledger: ./clean.ledger.tsv
[CHANGED] output: ./clean.tsv
          output row 14: edited (from source record 37)
[CHANGED] source: ./inventory.tsv
          source record 52: changed -> output row 3
          source record 210: new record
[WARN]    script differs from version used (1.1.0); a mismatch may reflect code changes, not data changes
[FAIL]    reproduction: re-running yields different output
VERIFICATION FAILED
```

## Caveats and options

- **Checksums detect change, not tampering.** Anyone who can edit the data can also regenerate the manifest. For tamper evidence, store the manifest's hash somewhere independent: a git commit, the accession file, a ticket, or an email. Or sign it with `gpg --detach-sign clean.manifest.json`.
- **Intentional edits will show as "edited."** If curators later correct the standardized file, that's expected. Treat the manifest as a baseline. Verification shows exactly which rows have diverged, and you can re-baseline by writing a new manifest.
- **Reproduction depends on the script version.** Changing the parsing rules changes the output, so the manifest records the script's hash. Keep old script versions, for example in git, if you need to reproduce old runs exactly.
- **Embedding a hash column is optional.** If the output will be imported into a system and the sidecar files might get separated from it, add a `Source Row SHA-256` column via a flag. Exclude that column when computing the output row hash, or the hash would depend on itself. The trade-off is clutter in the imported data.
- **SHA-256 over MD5 or CRC32.** The cost is negligible for spreadsheet-sized files, and MD5 and CRC32 are unsuitable for anything resembling evidence.
