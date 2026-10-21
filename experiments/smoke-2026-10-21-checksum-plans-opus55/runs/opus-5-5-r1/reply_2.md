# Adding Checksums to the Standardizer

The goal is to be able to prove, months later, three things:

1. **The source hasn't changed** since it was standardized.
2. **The output hasn't been altered** since it was produced.
3. **The output really came from that source**: re-running the same script with the same options gives byte-identical results, and every output row traces back to specific source rows.

## Design: three layers

| Layer | What's hashed | Answers |
|---|---|---|
| **File checksums** | SHA-256 of the raw source bytes, the standardized TSV, the provenance file and the report | "Has anything changed at all?" |
| **Row checksums** | SHA-256 of each source row and each output row, stored in a provenance file | "*Which* rows changed?" and "Where did output row 57 come from?" |
| **Manifest** | A JSON file recording all of the above, plus the options used, the script hash, the Python/Unicode versions and a timestamp | "Can I reproduce this exactly?" |

Some deliberate choices:

- **Source file hash uses raw bytes.** It's taken before decoding, so changes in encoding, BOM or line endings are all detected.
- **Row hashes use canonical JSON of the parsed fields**, e.g. `["1890","Vase","1985.12.3","https://…"]`. This is unambiguous: a tab inside a value can never be mistaken for a field boundary. It also makes rows comparable independently of their position in the file.
- **The output stays four columns.** Provenance goes in a sidecar file so the deliverable isn't cluttered.
- **Hashed content must be deterministic.** The timestamp lives only in the manifest. The report is excluded from the reproducibility check, because live link checks and the "future date" check depend on when the script runs.

## Code changes

### 1. New imports and helpers

Add these near the top of the script, after the existing imports:

```python
import hashlib
import json
import os
import platform
from datetime import datetime, timezone

SCRIPT_VERSION = "1.1.0"
MANIFEST_VERSION = 1

# Options that affect the standardized output (recorded so runs can be reproduced).
# --check-links is intentionally excluded: it only affects the report.
OPTION_KEYS = ["day_first", "range_sep", "object_sep", "ascii_quotes",
               "https", "drop_duplicates", "no_quote_parsing"]

PROV_HEADER = ["Output Row", "Source Row(s)", "Source Row SHA-256", "Output Row SHA-256"]
REPORT_HEADER = ["Source Row", "Column", "Original", "Standardized", "Note"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def row_digest(fields) -> str:
    """Canonical, unambiguous hash of a row's field values."""
    canon = json.dumps(list(fields), ensure_ascii=False, separators=(",", ":"))
    return sha256_bytes(canon.encode("utf-8"))


def render_tsv(header, rows) -> bytes:
    """Render a TSV to bytes in memory so the exact written bytes can be hashed."""
    buf = io.StringIO()
    w = csv.writer(buf, delimiter="\t", lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")
```

### 2. Replace `read_text` so the raw bytes are kept

```python
def read_source(path: str):
    data = sys.stdin.buffer.read() if path == "-" else Path(path).read_bytes()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return data, data.decode(enc), enc
        except UnicodeDecodeError:
            pass
    return data, data.decode("latin-1"), "latin-1"
```

### 3. Move the core logic into a reusable `process()`

The verify mode needs to re-run exactly the same logic, so the standardization moves out of `main()` into its own function. It now tracks source row numbers and row hashes for each record. When `--drop-duplicates` merges rows, the merged record keeps *all* contributing source rows, so nothing becomes untraceable.

```python
def process(text: str, opts):
    quoting = csv.QUOTE_NONE if opts.no_quote_parsing else csv.QUOTE_MINIMAL
    rows = list(csv.reader(io.StringIO(text, newline=""), delimiter="\t", quoting=quoting))
    if not rows:
        raise ValueError("Input file is empty.")

    mapping = detect_header(rows[0])
    has_header = mapping is not None
    start = 1 if has_header else 0
    if not has_header:
        mapping = {k: i for i, k in enumerate(KEYS)}

    records = []
    for row_no, row in enumerate(rows[start:], start=start + 1):
        if not any(c.strip() for c in row):
            continue
        get = lambda k: row[mapping[k]] if k in mapping and mapping[k] < len(row) else ""
        notes = []
        if not has_header and len(row) != 4:
            notes.append(("(row)", "", "", f"expected 4 columns, found {len(row)}"))

        results = [
            ("Date", get("date"), standardize_date(get("date"), opts.day_first, opts.range_sep)),
            ("Title", get("title"), standardize_title(get("title"), opts.ascii_quotes)),
            ("Object Number", get("object number"),
             standardize_object_number(get("object number"), opts.object_sep)),
            ("Link", get("link"), standardize_link(get("link"), opts.https)),
        ]
        values = []
        for col, orig, (new, issues) in results:
            values.append(new)
            for issue in issues:
                notes.append((col, orig, new, issue))
            if new != orig and not issues:
                notes.append((col, orig, new, "changed"))

        records.append({
            "lines": [row_no],
            "source_hashes": [row_digest(row)],
            "values": values,
            "notes": notes,
        })

    dropped = 0
    if opts.drop_duplicates:
        kept, index = [], {}
        for r in records:
            key = tuple(r["values"])
            if key in index:                      # merge, keeping provenance
                index[key]["lines"] += r["lines"]
                index[key]["source_hashes"] += r["source_hashes"]
                continue
            index[key] = r
            kept.append(r)
        dropped = len(records) - len(kept)
        records = kept

    counts = Counter(r["values"][2] for r in records if r["values"][2])
    for r in records:
        n = counts.get(r["values"][2], 0)
        if n > 1:
            r["notes"].append(("Object Number", r["values"][2], r["values"][2],
                               f"duplicate object number (appears {n} times)"))

    return {"rows": rows, "has_header": has_header, "mapping": mapping,
            "records": records, "dropped": dropped}
```

### 4. Build the manifest

```python
def build_manifest(manifest_path, source_path, source_bytes, encoding,
                   source_rows, outputs, opts):
    base = Path(manifest_path).resolve().parent
    rel = lambda p: os.path.relpath(Path(p).resolve(), base)
    return {
        "manifest_version": MANIFEST_VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool": {
            "name": "standardize_inventory.py",
            "version": SCRIPT_VERSION,
            "script_sha256": sha256_file(Path(__file__).resolve()),
            "python": platform.python_version(),
            "unicode_version": unicodedata.unidata_version,
        },
        "options": {k: getattr(opts, k) for k in OPTION_KEYS},
        "source": {
            "path": None if source_path == "-" else rel(source_path),
            "sha256": sha256_bytes(source_bytes),
            "bytes": len(source_bytes),
            "encoding": encoding,
            "rows": source_rows,
        },
        "outputs": {
            name: {"path": rel(path), "sha256": sha256_bytes(data),
                   "rows": data.count(b"\n") - 1}
            for name, (path, data) in outputs.items()
        },
    }
```

### 5. Verification mode

```python
def verify(manifest_path, source_override=None) -> bool:
    mpath = Path(manifest_path)
    base = mpath.parent
    m = json.loads(mpath.read_text(encoding="utf-8"))
    failures = 0

    def say(level, msg):
        nonlocal failures
        failures += level == "FAIL"
        print(f"[{level:<4}] {msg}")

    print(f"Manifest {mpath} (sha256 {sha256_file(mpath)})")
    print(f"Created {m['created_utc']} by {m['tool']['name']} v{m['tool']['version']}\n")

    # --- Environment: warn if reproduction may legitimately differ ---------
    if sha256_file(Path(__file__).resolve()) != m["tool"]["script_sha256"]:
        say("WARN", "this script differs from the one that produced the files")
    if unicodedata.unidata_version != m["tool"]["unicode_version"]:
        say("WARN", f"Unicode database {unicodedata.unidata_version} != "
                    f"{m['tool']['unicode_version']} (normalization may differ)")

    # --- Source file ---------------------------------------------------------
    if source_override:
        src = Path(source_override)
    elif m["source"]["path"]:
        src = base / m["source"]["path"]
    else:
        say("FAIL", "source was read from stdin; supply it with --source")
        return False
    if not src.exists():
        say("FAIL", f"source file not found: {src}")
        return False
    src_bytes = src.read_bytes()
    src_ok = sha256_bytes(src_bytes) == m["source"]["sha256"]
    say("OK" if src_ok else "FAIL",
        f"source {src}: " + ("unchanged" if src_ok else "CHANGED since standardization"))

    # --- Output files --------------------------------------------------------
    files, file_ok = {}, {}
    for name, info in m["outputs"].items():
        p = base / info["path"]
        if not p.exists():
            say("FAIL", f"{name} file missing: {p}")
            continue
        files[name] = p.read_bytes()
        file_ok[name] = sha256_bytes(files[name]) == info["sha256"]
        level = "OK" if file_ok[name] else ("WARN" if name == "report" else "FAIL")
        say(level, f"{name} {p}: " + ("unchanged" if file_ok[name] else "MODIFIED"))

    opts = argparse.Namespace(**m["options"])
    result = process(src_bytes.decode(m["source"]["encoding"], errors="replace"), opts)

    prov = []
    if "provenance" in files:
        prov = list(csv.reader(io.StringIO(files["provenance"].decode("utf-8"), newline=""),
                               delimiter="\t"))[1:]
        if not file_ok.get("provenance"):
            say("WARN", "provenance file was modified; row-level diagnostics are unreliable")

    # --- Row-level: which source rows changed? (position-independent) --------
    if not src_ok and prov:
        recorded = {h: line for _, lines, hashes, _ in prov
                    for line, h in zip(lines.split(";"), hashes.split(";"))}
        current = {h: line for r in result["records"]
                   for line, h in zip(r["lines"], r["source_hashes"])}
        gone = sorted((recorded[h] for h in recorded.keys() - current.keys()), key=int)
        new = sorted((str(current[h]) for h in current.keys() - recorded.keys()), key=int)
        if gone:
            say("INFO", f"originally-processed source rows modified/removed: {_short(gone)}")
        if new:
            say("INFO", f"current source rows not in the original run (new/edited): {_short(new)}")
        if not gone and not new:
            say("INFO", "all data rows intact; change is in the header, blank lines, or bytes "
                        "(encoding/line endings)")

    # --- Row-level: which output rows were edited? ---------------------------
    if "standardized" in files and not file_ok.get("standardized") and prov:
        cur = list(csv.reader(io.StringIO(files["standardized"].decode("utf-8"), newline=""),
                              delimiter="\t"))[1:]
        edited = [p[0] for row, p in zip(cur, prov) if row_digest(row) != p[3]]
        if len(cur) != len(prov):
            say("INFO", f"output has {len(cur)} data rows; provenance records {len(prov)}")
        if edited:
            say("INFO", f"output rows edited after standardization: {_short(edited)}")

    # --- Reproducibility: re-run and compare bytes ----------------------------
    if src_ok:
        regen = render_tsv(OUTPUT_HEADER, [r["values"] for r in result["records"]])
        same = sha256_bytes(regen) == m["outputs"]["standardized"]["sha256"]
        say("OK" if same else "FAIL",
            "re-running with recorded options reproduces the output exactly" if same else
            "re-running with recorded options produces DIFFERENT output")
    else:
        say("SKIP", "reproducibility check (source has changed)")

    print("\nVERIFIED" if failures == 0 else f"\n{failures} check(s) FAILED")
    return failures == 0


def _short(items, limit=20):
    items = list(items)
    return ", ".join(items[:limit]) + (f" … (+{len(items) - limit} more)" if len(items) > limit else "")
```

### 6. Updated `main()`

```python
def main():
    ap = argparse.ArgumentParser(description="Standardize a museum inventory TSV.")
    ap.add_argument("input", nargs="?", help="input .tsv file ('-' for stdin)")
    ap.add_argument("-o", "--output", help="output TSV (default: <input>_standardized.tsv)")
    ap.add_argument("--report", help="report TSV (default: <input>_report.tsv)")
    ap.add_argument("--provenance", help="row provenance TSV (default: <input>_provenance.tsv)")
    ap.add_argument("--manifest", help="checksum manifest (default: <input>_manifest.json)")
    ap.add_argument("--verify", metavar="MANIFEST", help="verify files against a manifest and exit")
    ap.add_argument("--source", help="with --verify: location of the source file if it moved")
    ap.add_argument("--day-first", action="store_true")
    ap.add_argument("--range-sep", default="–")
    ap.add_argument("--object-sep", metavar="SEP")
    ap.add_argument("--ascii-quotes", action="store_true")
    ap.add_argument("--https", action="store_true")
    ap.add_argument("--check-links", action="store_true")
    ap.add_argument("--drop-duplicates", action="store_true")
    ap.add_argument("--no-quote-parsing", action="store_true")
    args = ap.parse_args()

    if args.verify:
        sys.exit(0 if verify(args.verify, args.source) else 1)
    if not args.input:
        ap.error("input file is required unless --verify is used")

    stem = "stdin" if args.input == "-" else str(Path(args.input).with_suffix(""))
    paths = {
        "standardized": args.output or f"{stem}_standardized.tsv",
        "provenance": args.provenance or f"{stem}_provenance.tsv",
        "report": args.report or f"{stem}_report.tsv",
    }
    manifest_path = args.manifest or f"{stem}_manifest.json"

    src_bytes, text, encoding = read_source(args.input)
    try:
        result = process(text, args)
    except ValueError as e:
        sys.exit(str(e))
    records = result["records"]

    if not result["has_header"]:
        print("No header detected; assuming column order: " + ", ".join(OUTPUT_HEADER),
              file=sys.stderr)
    else:
        missing = [k for k in KEYS if k not in result["mapping"]]
        if missing:
            print(f"Warning: header has no column for: {', '.join(missing)}", file=sys.stderr)

    if args.check_links:
        urls = sorted({r["values"][3] for r in records
                       if r["values"][3].startswith(("http://", "https://"))})
        print(f"Checking {len(urls)} links...", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=8) as pool:
            status = dict(zip(urls, pool.map(check_link, urls)))
        for r in records:
            if status.get(r["values"][3]):
                r["notes"].append(("Link", r["values"][3], r["values"][3], status[r["values"][3]]))

    # Render everything to bytes first, so the hashes match exactly what's on disk.
    out_bytes = render_tsv(OUTPUT_HEADER, [r["values"] for r in records])
    prov_bytes = render_tsv(PROV_HEADER, [
        [i, ";".join(map(str, r["lines"])), ";".join(r["source_hashes"]), row_digest(r["values"])]
        for i, r in enumerate(records, start=1)
    ])
    report_rows, issue_counter, changed = [], Counter(), 0
    for r in records:
        for col, orig, new, note in r["notes"]:
            report_rows.append([r["lines"][0], col, orig, new, note])
            if note == "changed":
                changed += 1
            else:
                issue_counter[re.sub(r"\(appears \d+ times\)", "", note).strip()] += 1
    report_bytes = render_tsv(REPORT_HEADER, report_rows)

    data = {"standardized": out_bytes, "provenance": prov_bytes, "report": report_bytes}
    for name, b in data.items():
        Path(paths[name]).write_bytes(b)

    manifest = build_manifest(
        manifest_path, args.input, src_bytes, encoding,
        len(result["rows"]) - (1 if result["has_header"] else 0),
        {name: (paths[name], data[name]) for name in data}, args)
    Path(manifest_path).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                                   encoding="utf-8")

    # Also write a coreutils-style checksum file (verifiable with `sha256sum -c`).
    sums_path = Path(f"{stem}.sha256")
    lines = []
    if args.input != "-":
        lines.append(f"{manifest['source']['sha256']}  {os.path.relpath(args.input, sums_path.parent)}")
    for name in data:
        lines.append(f"{manifest['outputs'][name]['sha256']}  "
                     f"{os.path.relpath(paths[name], sums_path.parent)}")
    lines.append(f"{sha256_file(manifest_path)}  {os.path.relpath(manifest_path, sums_path.parent)}")
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nWrote {len(records)} rows -> {paths['standardized']}", file=sys.stderr)
    if result["dropped"]:
        print(f"Merged {result['dropped']} duplicate rows (provenance kept)", file=sys.stderr)
    print(f"Cells changed without issues: {changed}", file=sys.stderr)
    for note, n in issue_counter.most_common():
        print(f"  {n:6d}  {note}", file=sys.stderr)
    print(f"Manifest -> {manifest_path}  (sha256 {sha256_file(manifest_path)})", file=sys.stderr)
```

## What it produces

```
inventory.tsv                    ← source (untouched)
inventory_standardized.tsv       ← 4-column deliverable
inventory_provenance.tsv         ← row-level lineage + hashes
inventory_report.tsv             ← issues/changes
inventory_manifest.json          ← everything needed to verify/reproduce
inventory.sha256                 ← plain checksum list
```

**`inventory_provenance.tsv`**
```
Output Row	Source Row(s)	Source Row SHA-256	Output Row SHA-256
1	2	9f2c…e1a4	4b7d…0c93
2	3	a01e…77b2	e5f0…19d8
3	4;9	c3d9…5a10;c3d9…5a10	77aa…b2e1     ← merged duplicate rows
```

**`inventory_manifest.json`**
```json
{
  "manifest_version": 1,
  "created_utc": "2025-01-15T14:02:31+00:00",
  "tool": {
    "name": "standardize_inventory.py",
    "version": "1.1.0",
    "script_sha256": "5e8a…",
    "python": "3.12.1",
    "unicode_version": "15.0.0"
  },
  "options": {
    "day_first": false, "range_sep": "–", "object_sep": ".",
    "ascii_quotes": false, "https": false,
    "drop_duplicates": true, "no_quote_parsing": false
  },
  "source": {
    "path": "inventory.tsv", "sha256": "d41b…", "bytes": 48213,
    "encoding": "utf-8-sig", "rows": 1204
  },
  "outputs": {
    "standardized": {"path": "inventory_standardized.tsv", "sha256": "8c1f…", "rows": 1198},
    "provenance":   {"path": "inventory_provenance.tsv",   "sha256": "02ad…", "rows": 1198},
    "report":       {"path": "inventory_report.tsv",       "sha256": "b6e3…", "rows": 311}
  }
}
```

## Verifying later

```bash
python standardize_inventory.py --verify inventory_manifest.json
```

When everything is intact:
```
[OK  ] source inventory.tsv: unchanged
[OK  ] standardized inventory_standardized.tsv: unchanged
[OK  ] provenance inventory_provenance.tsv: unchanged
[OK  ] report inventory_report.tsv: unchanged
[OK  ] re-running with recorded options reproduces the output exactly

VERIFIED
```

When someone has edited things:
```
[FAIL] source inventory.tsv: CHANGED since standardization
[FAIL] standardized inventory_standardized.tsv: MODIFIED
[OK  ] provenance inventory_provenance.tsv: unchanged
[WARN] report inventory_report.tsv: MODIFIED
[INFO] originally-processed source rows modified/removed: 212, 640
[INFO] current source rows not in the original run (new/edited): 212, 640, 1205
[INFO] output rows edited after standardization: 57
[SKIP] reproducibility check (source has changed)

3 check(s) FAILED
```

Without Python, from the files' directory, you can still run:
```bash
sha256sum -c inventory.sha256
```

## Caveats

- **Checksums detect change, not tampering.** Anyone who edits the files can regenerate the manifest. If you need tamper evidence:
  - record the manifest's hash (printed at the end of each run) somewhere independent, such as your collections management system, a ticket or an email; or
  - sign it, e.g. `gpg --detach-sign inventory_manifest.json` or `minisign -Sm inventory_manifest.json`.
- **Reproducibility depends on the environment.** Unicode normalization can differ between Python/Unicode versions, which is why those versions are recorded. Any edit to the script changes `script_sha256`, so bump `SCRIPT_VERSION` deliberately. Keep the exact script version alongside the manifest, ideally in version control.
- **Row numbers are parsed rows, not physical lines.** A quoted field containing a newline counts as one row. The source-row comparison matches by hash rather than by position, so inserting a row near the top doesn't make every later row look changed.
- **The report is informational.** Its hash is recorded, but a mismatch is only a warning: people often annotate the report while reviewing, and its contents can vary between runs when `--check-links` is used.
