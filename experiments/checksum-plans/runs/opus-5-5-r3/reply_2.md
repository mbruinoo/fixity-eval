# Adding Checksums for Later Verification

## What checksums can prove

There are three different questions someone might ask later, and each needs a different kind of checksum:

| Question | Mechanism |
|---|---|
| "Have these files been changed since the run?" | **File hashes** (SHA-256 of the exact bytes) of the source, output, and reports, stored in a manifest |
| "Did the source data change, and which rows?" | **Row hashes** of each source row, plus a **lineage file** mapping each output row back to the source line and hash it came from |
| "Does this output really follow from this source?" | **Reproducibility**: the script is deterministic, so re-running it with the recorded options must produce byte-identical output |

File hashes alone aren't enough. If someone re-saves the source TSV in a different encoding, the bytes change but the data doesn't. That's why the design also uses a **content hash**: a hash computed over the parsed field values, which ignores encoding and line-ending differences.

## What a run produces

```
inventory_standardized.tsv   cleaned data (unchanged format)
inventory_issues.tsv         review report (now deterministic; see note below)
inventory_lineage.tsv        output line -> source line + row hashes
inventory_linkcheck.tsv      only with --check-links (kept separate: network results aren't reproducible)
inventory_manifest.json      hashes, options, tool version, environment
inventory_SHA256SUMS         same file hashes in `sha256sum -c` format, for checking without Python
```

## Code changes

The `standardize_*` functions, `detect_columns`, `read_tsv`, `natural_key`, and `check_link` are **unchanged**. The main logic moves into a `process()` function so the verifier can re-run exactly the same code. All files are rendered to bytes in memory first, so the bytes that get hashed are exactly the bytes that get written.

**1. New imports and helpers** (add near the top):

```python
import hashlib
import io
import json
import os
import platform
from datetime import datetime, timezone

SCRIPT_VERSION = "1.1.0"
ISSUES_HEADER = ["Line", "Column", "Original", "Standardized", "Issue"]
LINEAGE_HEADER = ["Output Line", "Source Line", "Source Row SHA-256",
                  "Output Row SHA-256", "Object Number"]

# Options that affect output. Recorded in the manifest so a re-run can use them.
DETERMINISTIC_OPTIONS = ("no_header", "day_first", "force_https",
                         "uppercase_object_numbers", "sort",
                         "drop_duplicates", "raw_quotes")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def row_hash(fields):
    """Hash a list of field values unambiguously.

    JSON encoding keeps field boundaries explicit, so ["a\\tb", "c"] and
    ["a", "b\\tc"] can never collide the way naive string-joining could.
    """
    payload = json.dumps(list(fields), ensure_ascii=False, separators=(",", ":"))
    return sha256_bytes(payload.encode("utf-8"))


def content_hash(row_hashes):
    """Order-sensitive fingerprint of a whole table, independent of file encoding."""
    h = hashlib.sha256()
    for rh in row_hashes:
        h.update(bytes.fromhex(rh))
    return h.hexdigest()


def render_tsv(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, delimiter="\t", lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")
```

**2. Core processing**, moved out of `main()`. It is now a pure function: rows plus options in, results out.

```python
def process(rows, opts):
    """Standardize parsed TSV rows. Deterministic: no I/O, no network."""
    fields = ["date", "title", "object_number", "link"]
    mapping = {} if opts.no_header else detect_columns(rows[0])
    if len(mapping) == 4:
        data, first_line = rows[1:], 2
        cols = [mapping[f] for f in fields]
    elif len(mapping) >= 2:
        missing = [f for f in fields if f not in mapping]
        raise ValueError(f"header row recognized but couldn't find column(s): "
                         f"{', '.join(missing)}. Header seen: {rows[0]}")
    else:
        data, first_line = rows, 1
        cols = [0, 1, 2, 3]

    issues, cleaned, source_rows = [], [], []

    def flag(line, column, original, value, problem):
        if problem:
            issues.append((line, column, original, value, problem))

    for line, row in enumerate(data, start=first_line):
        if not any(cell.strip() for cell in row):
            continue
        if len(row) < max(cols) + 1:
            flag(line, "(row)", "\t".join(row), "",
                 f"row has {len(row)} column(s); missing values padded")
            row = row + [""] * (max(cols) + 1 - len(row))
        elif not mapping and len(row) > 4 and any(c.strip() for c in row[4:]):
            flag(line, "(row)", "\t".join(row[4:]), "",
                 "row has extra columns; extra values ignored")

        raw = [row[i] for i in cols]        # exactly as read, before any cleaning
        src_hash = row_hash(raw)
        source_rows.append((line, src_hash))

        d, p = standardize_date(raw[0], opts.day_first)
        flag(line, "Date", raw[0], d, p)
        t, p = standardize_title(raw[1])
        flag(line, "Title", raw[1], t, p)
        o, p = standardize_object_number(raw[2], opts.uppercase_object_numbers)
        flag(line, "Object Number", raw[2], o, p)
        u, p = standardize_link(raw[3], opts.force_https)
        flag(line, "Link", raw[3], u, p)

        cleaned.append((line, [d, t, o, u], src_hash))

    if opts.drop_duplicates:
        seen, unique = set(), []
        for item in cleaned:
            key = tuple(item[1])
            if key in seen:
                flag(item[0], "(row)", "", "", "exact duplicate row dropped")
                continue
            seen.add(key)
            unique.append(item)
        cleaned = unique

    counts = Counter(rec[2].casefold() for _, rec, _ in cleaned if rec[2])
    for line, rec, _ in cleaned:
        n = counts[rec[2].casefold()] if rec[2] else 0
        if n > 1:
            flag(line, "Object Number", rec[2], rec[2],
                 f"duplicate object number ({n} rows)")

    if opts.sort == "object-number":
        cleaned.sort(key=lambda x: natural_key(x[1][2]))
    elif opts.sort == "title":
        cleaned.sort(key=lambda x: x[1][1].casefold())

    issues.sort(key=lambda x: x[0])
    return {"cleaned": cleaned, "issues": issues, "source_rows": source_rows}


def build_outputs(result):
    """Render all deterministic output files to bytes."""
    cleaned = result["cleaned"]
    return {
        "output": render_tsv(OUTPUT_HEADER, [rec for _, rec, _ in cleaned]),
        "issues": render_tsv(ISSUES_HEADER, result["issues"]),
        "lineage": render_tsv(LINEAGE_HEADER, [
            [out_line, src_line, src_hash, row_hash(rec), rec[2]]
            for out_line, (src_line, rec, src_hash) in enumerate(cleaned, start=2)
        ]),
    }
```

**3. Verification:**

```python
def diff_source(lineage_bytes, source_rows):
    """Use the lineage file to pinpoint which output rows are affected by source changes."""
    reader = csv.reader(io.StringIO(lineage_bytes.decode("utf-8")), delimiter="\t")
    next(reader)
    current_by_line = dict(source_rows)
    current_hashes = {h for _, h in source_rows}
    recorded_hashes, problems = set(), []

    for out_line, src_line, src_hash, _, obj in reader:
        recorded_hashes.add(src_hash)
        label = f"output line {out_line} ({obj or 'no object number'})"
        if current_by_line.get(int(src_line)) == src_hash:
            continue
        if src_hash in current_hashes:
            problems.append(f"{label}: source row unchanged but moved from line {src_line}")
        else:
            problems.append(f"{label}: source line {src_line} was changed or removed")

    new = [str(line) for line, h in source_rows if h not in recorded_hashes]
    if new:
        problems.append(f"{len(new)} source row(s) not in the standardized output: "
                        f"line(s) {', '.join(new[:20])}{' ...' if len(new) > 20 else ''}")
    return problems


def verify(manifest_path):
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    base = manifest_path.resolve().parent
    failures = 0

    def say(status, msg):
        nonlocal failures
        failures += status == "FAIL"
        print(f"[{status:4}] {msg}")

    # 1. Environment: differences here could legitimately change results
    if sha256_bytes(Path(__file__).read_bytes()) != m["tool"]["script_sha256"]:
        say("WARN", f"this script differs from the one that made the manifest "
                    f"(v{m['tool']['version']}); reproduction may not match")
    if unicodedata.unidata_version != m["environment"]["unicode_data"]:
        say("WARN", f"Unicode database differs ({unicodedata.unidata_version} vs "
                    f"{m['environment']['unicode_data']}); text normalization may differ")

    # 2. Integrity: are the produced files exactly as written?
    for key in ("output", "issues", "lineage", "link_check"):
        entry = m.get(key)
        if not entry:
            continue
        p = base / entry["path"]
        if not p.exists():
            say("FAIL", f"{key}: {p} is missing")
        elif sha256_file(p) != entry["sha256"]:
            say("FAIL", f"{key}: {p.name} has been modified since it was produced")
        else:
            say("OK", f"{key}: {p.name} unchanged")

    # 3. Source: same bytes? If not, same data?
    src = base / m["source"]["path"]
    if not src.exists():
        say("FAIL", f"source: {src} is missing")
        return False
    opts = argparse.Namespace(**m["options"])
    rows, _ = read_tsv(src, opts.raw_quotes)
    try:
        result = process(rows, opts)
    except ValueError as e:
        say("FAIL", f"source can no longer be processed: {e}")
        return False

    if sha256_file(src) == m["source"]["sha256"]:
        say("OK", "source: byte-for-byte identical")
    elif content_hash(h for _, h in result["source_rows"]) == m["source"]["content_sha256"]:
        say("OK", "source: file was re-saved/re-encoded, but the data is identical")
    else:
        say("FAIL", "source: data has changed since standardization")
        lineage = base / m["lineage"]["path"]
        if lineage.exists():
            for problem in diff_source(lineage.read_bytes(), result["source_rows"]):
                print(f"         - {problem}")
        return False                       # can't reproduce from changed data

    # 4. Reproducibility: re-run and compare
    for key, data in build_outputs(result).items():
        if sha256_bytes(data) == m[key]["sha256"]:
            say("OK", f"{key}: reproduced exactly from source")
        else:
            say("FAIL", f"{key}: re-running standardization gives a different result")

    print("\nVerification", "PASSED" if failures == 0 else f"FAILED ({failures} problem(s))")
    return failures == 0
```

**4. New `main()`.** Keep all existing arguments and change the `input` argument to optional:

```python
def main():
    ap = argparse.ArgumentParser(description="Standardize a museum inventory TSV.")
    ap.add_argument("input", type=Path, nargs="?", help="input .tsv file")
    # ... all existing arguments unchanged ...
    ap.add_argument("--manifest", type=Path,
                    help="manifest path (default: <input>_manifest.json)")
    ap.add_argument("--verify", type=Path, metavar="MANIFEST",
                    help="verify a previous run instead of standardizing")
    args = ap.parse_args()

    if args.verify:
        sys.exit(0 if verify(args.verify) else 1)
    if not args.input:
        ap.error("input is required unless --verify is used")
    if not args.input.exists():
        sys.exit(f"Error: {args.input} not found")

    stem = args.input.with_suffix("")
    paths = {
        "output": args.output or Path(f"{stem}_standardized.tsv"),
        "issues": args.issues or Path(f"{stem}_issues.tsv"),
        "lineage": Path(f"{stem}_lineage.tsv"),
    }
    manifest_path = args.manifest or Path(f"{stem}_manifest.json")
    base = manifest_path.resolve().parent

    src_bytes = args.input.read_bytes()
    rows, encoding = read_tsv(args.input, args.raw_quotes)
    if not rows:
        sys.exit("Error: input file is empty")
    try:
        result = process(rows, args)
    except ValueError as e:
        sys.exit(f"Error: {e}")

    files = build_outputs(result)

    # Network results are not reproducible, so they go in their own file
    if args.check_links:
        urls = sorted({rec[3] for _, rec, _ in result["cleaned"]
                       if rec[3].startswith("http")})
        print(f"Checking {len(urls)} unique link(s)...", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=8) as pool:
            res = dict(zip(urls, pool.map(lambda u: check_link(u, args.timeout), urls)))
        files["link_check"] = render_tsv(["Line", "Link", "Issue"], [
            [line, rec[3], res[rec[3]]]
            for line, rec, _ in result["cleaned"] if res.get(rec[3])])
        paths["link_check"] = Path(f"{stem}_linkcheck.tsv")

    for key, data in files.items():
        paths[key].write_bytes(data)

    def entry(path, data, **extra):
        rel = Path(os.path.relpath(path.resolve(), base)).as_posix()
        return {"path": rel, "sha256": sha256_bytes(data), "bytes": len(data), **extra}

    cleaned = result["cleaned"]
    manifest = {
        "manifest_version": 1,
        "tool": {"name": "standardize_inventory.py", "version": SCRIPT_VERSION,
                 "script_sha256": sha256_bytes(Path(__file__).read_bytes())},
        "environment": {"python": platform.python_version(),
                        "unicode_data": unicodedata.unidata_version},
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "options": {k: getattr(args, k) for k in DETERMINISTIC_OPTIONS},
        "source": entry(args.input, src_bytes, encoding=encoding,
                        rows=len(result["source_rows"]),
                        content_sha256=content_hash(h for _, h in result["source_rows"])),
        "output": entry(paths["output"], files["output"], rows=len(cleaned),
                        content_sha256=content_hash(row_hash(r) for _, r, _ in cleaned)),
        "issues": entry(paths["issues"], files["issues"], count=len(result["issues"])),
        "lineage": entry(paths["lineage"], files["lineage"]),
    }
    if "link_check" in files:
        manifest["link_check"] = entry(paths["link_check"], files["link_check"],
                                       reproducible=False)

    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    manifest_path.write_bytes(manifest_bytes)

    # Plain-text checksums, verifiable anywhere with: sha256sum -c <file>
    sums = [(manifest[k]["sha256"], manifest[k]["path"])
            for k in ("source", "output", "issues", "lineage", "link_check") if k in manifest]
    sums.append((sha256_bytes(manifest_bytes),
                 Path(os.path.relpath(manifest_path.resolve(), base)).as_posix()))
    Path(f"{stem}_SHA256SUMS").write_text(
        "".join(f"{h}  {p}\n" for h, p in sums), encoding="utf-8")

    print(f"Wrote {len(cleaned)} row(s) to {paths['output']}", file=sys.stderr)
    print(f"{len(result['issues'])} issue(s) -> {paths['issues']}", file=sys.stderr)
    print(f"Manifest -> {manifest_path}", file=sys.stderr)
```

## Example

**Manifest (`inventory_manifest.json`, hashes shortened):**
```json
{
  "manifest_version": 1,
  "tool": { "name": "standardize_inventory.py", "version": "1.1.0", "script_sha256": "9f2c…" },
  "environment": { "python": "3.12.2", "unicode_data": "15.0.0" },
  "created_utc": "2025-01-15T14:02:11+00:00",
  "options": { "no_header": false, "day_first": false, "force_https": false,
               "uppercase_object_numbers": false, "sort": "object-number",
               "drop_duplicates": false, "raw_quotes": false },
  "source":  { "path": "inventory.tsv", "sha256": "4b1e…", "bytes": 512,
               "encoding": "utf-8-sig", "rows": 6, "content_sha256": "c07a…" },
  "output":  { "path": "inventory_standardized.tsv", "sha256": "e3d9…", "bytes": 431,
               "rows": 6, "content_sha256": "88f0…" },
  "issues":  { "path": "inventory_issues.tsv", "sha256": "1a6b…", "bytes": 498, "count": 6 },
  "lineage": { "path": "inventory_lineage.tsv", "sha256": "d45c…", "bytes": 902 }
}
```

**Verifying later, after someone edited source line 4:**
```
$ python standardize_inventory.py --verify inventory_manifest.json
[OK  ] output: inventory_standardized.tsv unchanged
[OK  ] issues: inventory_issues.tsv unchanged
[OK  ] lineage: inventory_lineage.tsv unchanged
[FAIL] source: data has changed since standardization
         - output line 5 (1999.12.3): source line 4 was changed or removed
```

**Verifying a clean run:**
```
[OK  ] output: inventory_standardized.tsv unchanged
...
[OK  ] source: byte-for-byte identical
[OK  ] output: reproduced exactly from source
[OK  ] issues: reproduced exactly from source
[OK  ] lineage: reproduced exactly from source

Verification PASSED
```

The exit code is 0 or 1, so `--verify` can run in a scheduled job or CI pipeline.

## Design decisions and caveats

- **Row hashes use the raw field values before cleaning.** The lineage file therefore proves which original data each output row came from, not just which line number. Line numbers alone break as soon as someone inserts a row; the hash lets the verifier tell "row moved" apart from "row changed."
- **Only the four mapped columns are hashed.** These are the values that determine the output. If you'd rather have edits to *any* column, including ignored extra ones, flagged as source changes, hash the full `row` instead of `raw`.
- **Determinism is required for reproduction.** Three things can make a re-run differ legitimately: a changed script, different options, or a different Unicode database version. (Python's `unicodedata` changes between releases, which affects NFC/NFKC normalization.) The manifest records all three, and the verifier warns about mismatches rather than reporting a confusing failure.
- **Link checking is excluded from reproducibility.** Websites change, so link results go in a separate file that is integrity-checked but never re-derived. This means `--check-links` problems no longer appear in the main issues file.
- **Watch out for spreadsheet software.** If someone opens a TSV in Excel and saves it, the bytes change, and Excel may also silently convert object numbers such as `1-2` into dates or strip leading zeros. The content hash distinguishes the harmless case (re-encoding only) from real data damage, and the lineage diff tells you which rows were hit.
- **Checksums detect accidental changes, not deliberate ones.** Anyone who can edit the files can regenerate the manifest. For tamper evidence, store the manifest's hash (the last line of `SHA256SUMS`) somewhere separate, such as your collections management system or a ticket, or sign the manifest with `gpg --detach-sign inventory_manifest.json`.
