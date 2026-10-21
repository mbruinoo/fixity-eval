# Adding Checksums for Verification and Provenance

## The design

To check the result against the source later, you need to answer four questions:

| Question | Mechanism |
|---|---|
| Is the source file exactly what we processed? | **File-level SHA-256** of the raw input bytes |
| If the source changed, *which records* changed? | **Row-level SHA-256** of each parsed source record, tied to its line number |
| Has the standardized output been edited since it was produced? | **File-level and row-level SHA-256** of the output |
| Does the output really follow from the source? | A **manifest** recording parameters and the script's own hash, so the run can be **re-executed and compared** |

Some design choices:

- **Use two levels of hashing.** File hashes are strict: any byte change counts, including line endings or a re-save in Excel. Row hashes are computed on *parsed field values*, so they pinpoint which records changed even if formatting noise also changed.
- **Use a canonical serialization for rows.** Each row is hashed as a compact JSON array of its field strings. This is unambiguous: `["a\tb", "c"]` and `["a", "b\tc"]` can't collide the way naive joining could.
- **Hash the full source row**, including extra columns, so nothing escapes verification.
- **Hash only the 4 standardized values for output rows.** Optional provenance columns don't affect verification.
- **Keep a sidecar manifest** (`*_manifest.json`) so the output stays a clean 4-column TSV. An optional `--provenance-columns` flag adds `source_line` and `source_sha256` directly to the output if you want each row to carry its own lineage.
- **Keep the output deterministic.** The run timestamp lives only in the manifest's metadata and is excluded from every digest, so re-running produces identical hashes.

## Code changes

Add these imports at the top of the script:

```python
import hashlib
import json
import os
from datetime import datetime, timezone
```

### 1. Hashing helpers (add after `clean_text`)

```python
# ---------------------------------------------------------------------------
# Checksums / provenance
# ---------------------------------------------------------------------------

TOOL_VERSION = "1.1.0"
MANIFEST_VERSION = 1


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_row_hash(values) -> str:
    """SHA-256 of a row's field values, serialized unambiguously as compact JSON."""
    payload = json.dumps(list(values), ensure_ascii=False, separators=(",", ":"))
    return sha256_hex(payload.encode("utf-8"))


def tool_fingerprint():
    """SHA-256 of this script, so we know exactly which logic produced an output."""
    try:
        return sha256_hex(Path(__file__).read_bytes())
    except OSError:
        return None


def rows_digest(rows):
    """One hash summarizing the whole source-line -> source-hash -> output-hash mapping."""
    lines = (f"{r['output_index']}:{r['source_line']}:{r['source_sha256']}:{r['output_sha256']}"
             for r in rows)
    return sha256_hex("\n".join(lines).encode("utf-8"))


def _relpath(path, start):
    try:
        return os.path.relpath(path, start)
    except ValueError:                      # different drive on Windows
        return str(Path(path).resolve())
```

### 2. Replace `read_tsv` (now returns the file hash and accepts a forced encoding)

```python
def read_tsv(path, use_quoting=True, encoding=None):
    data = Path(path).read_bytes()
    if encoding:
        text = data.decode(encoding)
    else:
        for encoding in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                text = data.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    reader = csv.reader(io.StringIO(text), delimiter="\t",
                        quoting=csv.QUOTE_MINIMAL if use_quoting else csv.QUOTE_NONE)
    rows = [(reader.line_num, row) for row in reader]
    return rows, encoding, sha256_hex(data), len(data)
```

### 3. Move the processing loop into a reusable function

The processing loop needs to be callable both for normal runs and for `--verify --rerun`, so it moves out of `main()`:

```python
def standardize_rows(rows, opts):
    """Standardize parsed rows. Pure function of (rows, opts) -> deterministic result."""
    mapping, has_header = detect_columns(rows[0][1])
    data_rows = rows[1:] if has_header else rows
    res = {
        "mapping": mapping, "has_header": has_header,
        "header_sha256": canonical_row_hash(rows[0][1]) if has_header else None,
        "output": [], "issues": [], "changed": Counter(),
        "sev_counts": defaultdict(Counter), "blank_lines": [], "dupes": set(),
    }

    def note(line, col, orig, new, notes):
        for severity, msg in notes:
            res["issues"].append((line, col, severity, clean_text(orig), new, msg))
            res["sev_counts"][col][severity] += 1

    for line, row in data_rows:
        if not any(c.strip() for c in row):
            res["blank_lines"].append(line)      # recorded so row counts reconcile
            continue
        get = lambda f: row[mapping[f]] if mapping[f] < len(row) else ""
        raw = {f: get(f) for f in OUTPUT_HEADER}

        date, n1 = standardize_date(raw["date"], opts.dayfirst)
        title, n2 = standardize_title(raw["title"], not opts.keep_caps, opts.straight_quotes)
        objnum, n3 = standardize_object_number(raw["object_number"], opts.object_separator)
        link, n4 = standardize_link(raw["link"], opts.force_https)

        for col, new, notes in (("date", date, n1), ("title", title, n2),
                                ("object_number", objnum, n3), ("link", link, n4)):
            note(line, col, raw[col], new, notes)
            if new != raw[col].strip():
                res["changed"][col] += 1

        extra = [c for i, c in enumerate(row) if i not in mapping.values() and c.strip()]
        if extra:
            note(line, "row", "\t".join(row), "",
                 [("warning", f"{len(extra)} extra non-empty column(s) ignored: "
                              f"{' | '.join(extra)[:120]}")])

        res["output"].append({
            "source_line": line,
            "source_sha256": canonical_row_hash(row),   # full raw row, incl. extra columns
            "values": [date, title, objnum, link],
        })

    counts = Counter(r["values"][2] for r in res["output"] if r["values"][2])
    res["dupes"] = {k for k, v in counts.items() if v > 1}
    for r in res["output"]:
        if r["values"][2] in res["dupes"]:
            note(r["source_line"], "object_number", r["values"][2], r["values"][2],
                 [("error", f"duplicate object number (appears {counts[r['values'][2]]} times)")])

    if opts.sort_by_object_number:
        res["output"].sort(key=lambda r: (r["values"][2] == "", natural_key(r["values"][2])))

    for i, r in enumerate(res["output"]):
        r["output_index"] = i
        r["output_sha256"] = canonical_row_hash(r["values"])
    return res


def render_output(output, provenance_columns=False):
    header = OUTPUT_HEADER + (["source_line", "source_sha256"] if provenance_columns else [])
    lines = ["\t".join(header)]
    for r in output:
        extra = [str(r["source_line"]), r["source_sha256"]] if provenance_columns else []
        lines.append("\t".join(r["values"] + extra))
    return "\n".join(lines) + "\n"


def render_report(issues):
    lines = ["line\tcolumn\tseverity\toriginal\tstandardized\tmessage"]
    for line, col, sev, orig, new, msg in sorted(issues, key=lambda x: (x[0], x[1])):
        lines.append("\t".join([str(line), col, sev, clean_text(orig), clean_text(new), msg]))
    return "\n".join(lines) + "\n"


PARAM_KEYS = ["dayfirst", "force_https", "object_separator", "keep_caps",
              "straight_quotes", "sort_by_object_number", "no_quoting", "provenance_columns"]
```

### 4. Manifest writing and verification

```python
def write_manifest(path, *, args, in_path, src_sha, src_bytes, encoding, res,
                   out_path, out_sha, report_path, report_sha):
    base = Path(path).resolve().parent
    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool": {"name": "standardize_inventory.py", "version": TOOL_VERSION,
                 "sha256": tool_fingerprint(), "python": sys.version.split()[0]},
        "parameters": {k: getattr(args, k) for k in PARAM_KEYS},
        "source": {
            "path": _relpath(in_path, base), "sha256": src_sha, "bytes": src_bytes,
            "encoding": encoding, "header_detected": res["has_header"],
            "header_sha256": res["header_sha256"], "column_mapping": res["mapping"],
            "data_rows": len(res["output"]), "blank_lines_skipped": res["blank_lines"],
        },
        "output": {"path": None if out_path == "-" else _relpath(out_path, base),
                   "sha256": out_sha, "rows": len(res["output"])},
        "report": ({"path": _relpath(report_path, base), "sha256": report_sha}
                   if report_path else None),
        "rows_digest": rows_digest(res["output"]),
        "rows": [{k: r[k] for k in ("output_index", "source_line", "source_sha256", "output_sha256")}
                 for r in res["output"]],
    }
    data = json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8")
    Path(path).write_bytes(data)
    return sha256_hex(data)


def verify(manifest_path, source_override=None, output_override=None, rerun=False, show=20):
    """Check source and output against a manifest. Returns a process exit code (0 = all OK)."""
    m = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    base = Path(manifest_path).resolve().parent
    failures = 0

    def ok(msg): print(f"  OK    {msg}")
    def warn(msg): print(f"  WARN  {msg}")
    def fail(msg):
        nonlocal failures
        failures += 1
        print(f"  FAIL  {msg}")

    print(f"Verifying against {manifest_path} (created {m['created_utc']})")

    # --- Tool ---------------------------------------------------------------
    if tool_fingerprint() == m["tool"]["sha256"]:
        ok("script is identical to the one that produced the output")
    else:
        warn("script differs from the one recorded in the manifest; --rerun results may differ")

    expected_rows = sorted(m["rows"], key=lambda r: r["output_index"])
    src_info = m["source"]
    params = argparse.Namespace(**m["parameters"])

    # --- Source -------------------------------------------------------------
    src_path = Path(source_override) if source_override else base / src_info["path"]
    src_rows = None
    if not src_path.exists():
        fail(f"source file not found: {src_path}")
    else:
        src_rows, _, src_sha, _ = read_tsv(src_path, not params.no_quoting, src_info["encoding"])
        if src_sha == src_info["sha256"]:
            ok(f"source file unchanged ({src_path.name}, sha256 {src_sha[:12]}…)")
        else:
            fail(f"source file hash differs ({src_sha[:12]}… vs {src_info['sha256'][:12]}…); "
                 "checking individual records")
            data = src_rows[1:] if src_info["header_detected"] else src_rows
            if src_info["header_detected"] and canonical_row_hash(src_rows[0][1]) != src_info["header_sha256"]:
                print("        header row changed")
            current = defaultdict(list)
            for line, row in data:
                if any(c.strip() for c in row):
                    current[canonical_row_hash(row)].append(line)
            expected = Counter(r["source_sha256"] for r in expected_rows)
            found = Counter({h: len(v) for h, v in current.items()})
            removed, added = expected - found, found - expected
            if not removed and not added:
                print("        all records identical; difference is formatting only "
                      "(line endings, quoting, blank lines, encoding)")
            else:
                gone = [r["source_line"] for r in expected_rows if r["source_sha256"] in removed]
                new = sorted(l for h in added for l in current[h][-added[h]:])
                print(f"        {sum(removed.values())} original record(s) missing or modified "
                      f"(original lines: {gone[:show]}{' …' if len(gone) > show else ''})")
                print(f"        {sum(added.values())} new or modified record(s) "
                      f"(current lines: {new[:show]}{' …' if len(new) > show else ''})")

    # --- Output -------------------------------------------------------------
    out_rel = m["output"]["path"]
    out_path = Path(output_override) if output_override else (base / out_rel if out_rel else None)
    if out_path is None:
        warn("output was written to stdout; pass --against-output to check a saved copy")
    elif not out_path.exists():
        fail(f"output file not found: {out_path}")
    else:
        data = out_path.read_bytes()
        if sha256_hex(data) == m["output"]["sha256"]:
            ok(f"output file unchanged ({out_path.name})")
        else:
            fail("output file hash differs; checking individual rows")
            lines = data.decode("utf-8-sig").splitlines()[1:]
            actual = [canonical_row_hash(l.split("\t")[:4]) for l in lines]
            if len(actual) != len(expected_rows):
                print(f"        row count changed: {len(actual)} now vs {len(expected_rows)} recorded")
            bad = [(i, r["source_line"]) for i, r in enumerate(expected_rows)
                   if i >= len(actual) or actual[i] != r["output_sha256"]]
            if bad:
                print(f"        {len(bad)} row(s) edited (output row #, source line): {bad[:show]}"
                      f"{' …' if len(bad) > show else ''}")

    # --- Reproducibility ------------------------------------------------------
    if rerun and src_rows:
        res = standardize_rows(src_rows, params)
        if rows_digest(res["output"]) == m["rows_digest"]:
            ok("re-running standardization on the source reproduces the recorded output exactly")
        else:
            regenerated = {r["source_sha256"]: r["output_sha256"] for r in res["output"]}
            diffs = [r["source_line"] for r in expected_rows
                     if regenerated.get(r["source_sha256"]) not in (None, r["output_sha256"])]
            fail(f"re-run does not reproduce recorded output; {len(diffs)} row(s) standardize "
                 f"differently (source lines: {diffs[:show]}{' …' if len(diffs) > show else ''})")

    print("RESULT:", "PASS" if failures == 0 else f"FAIL ({failures} check(s) failed)")
    return 0 if failures == 0 else 1
```

### 5. Replace `main()`

```python
def main():
    ap = argparse.ArgumentParser(description="Standardize a museum inventory TSV "
                                             "(date, title, object number, link).")
    ap.add_argument("input", nargs="?", help="input .tsv file")
    ap.add_argument("-o", "--output", help="output path (default: <input>_standardized.tsv; '-' for stdout)")
    ap.add_argument("-r", "--report", help="issues report path (default: <output>_issues.tsv; 'none' to disable)")
    ap.add_argument("-m", "--manifest", help="checksum manifest path (default: <output>_manifest.json; 'none' to disable)")
    ap.add_argument("--provenance-columns", action="store_true",
                    help="append source_line and source_sha256 columns to the output")
    ap.add_argument("--dayfirst", action="store_true", help="interpret ambiguous numeric dates as DD/MM/YYYY")
    ap.add_argument("--force-https", action="store_true", help="upgrade http:// links to https://")
    ap.add_argument("--object-separator", metavar="SEP", help="unify separators between digits in object numbers")
    ap.add_argument("--keep-caps", action="store_true", help="do not convert ALL-CAPS titles")
    ap.add_argument("--straight-quotes", action="store_true", help="convert curly quotes in titles")
    ap.add_argument("--sort-by-object-number", action="store_true", help="sort output by object number")
    ap.add_argument("--no-quoting", action="store_true", help="treat quote characters in the input literally")
    vg = ap.add_argument_group("verification")
    vg.add_argument("--verify", metavar="MANIFEST", help="verify source/output against a manifest and exit")
    vg.add_argument("--source", help="with --verify: source file to check (overrides manifest path)")
    vg.add_argument("--against-output", help="with --verify: output file to check (overrides manifest path)")
    vg.add_argument("--rerun", action="store_true", help="with --verify: re-run standardization and compare")
    args = ap.parse_args()

    if args.verify:
        sys.exit(verify(args.verify, args.source, args.against_output, args.rerun))
    if not args.input:
        ap.error("input is required unless --verify is used")

    in_path = Path(args.input)
    out_path = args.output or str(in_path.with_name(in_path.stem + "_standardized.tsv"))
    stem_base = in_path if out_path == "-" else Path(out_path)

    def side_path(opt, suffix):
        if opt:
            return None if opt.lower() == "none" else opt
        return str(stem_base.with_name(stem_base.stem + suffix))

    report_path = side_path(args.report, "_issues.tsv")
    manifest_path = side_path(args.manifest, "_manifest.json")

    rows, encoding, src_sha, src_bytes = read_tsv(in_path, use_quoting=not args.no_quoting)
    if not rows:
        sys.exit("Input file is empty.")

    res = standardize_rows(rows, args)

    # Render to bytes first so exactly the hashed bytes are written
    out_bytes = render_output(res["output"], args.provenance_columns).encode("utf-8")
    out_sha = sha256_hex(out_bytes)
    if out_path == "-":
        sys.stdout.buffer.write(out_bytes)
        sys.stdout.flush()
    else:
        Path(out_path).write_bytes(out_bytes)

    report_sha = None
    if report_path:
        report_bytes = render_report(res["issues"]).encode("utf-8")
        report_sha = sha256_hex(report_bytes)
        Path(report_path).write_bytes(report_bytes)

    manifest_sha = None
    if manifest_path:
        manifest_sha = write_manifest(
            manifest_path, args=args, in_path=in_path, src_sha=src_sha, src_bytes=src_bytes,
            encoding=encoding, res=res, out_path=out_path, out_sha=out_sha,
            report_path=report_path, report_sha=report_sha)

    # Summary
    err = sys.stderr
    print(f"Processed {len(res['output']):,} rows (encoding: {encoding}, header "
          f"{'detected' if res['has_header'] else 'not detected'})", file=err)
    for col in OUTPUT_HEADER + (["row"] if res["sev_counts"]["row"] else []):
        sc = res["sev_counts"][col]
        print(f"  {col:<14} {res['changed'][col]:>6,} changed  {sc['error']:>5,} errors  "
              f"{sc['warning']:>5,} warnings", file=err)
    if res["dupes"]:
        print(f"  {len(res['dupes']):,} object number(s) are duplicated", file=err)
    print(f"Source   sha256 {src_sha}", file=err)
    print(f"Output   sha256 {out_sha}  {'' if out_path == '-' else out_path}", file=err)
    if report_path:
        print(f"Issues   sha256 {report_sha}  {report_path}", file=err)
    if manifest_path:
        print(f"Manifest sha256 {manifest_sha}  {manifest_path}", file=err)
        print("Record the manifest hash somewhere independent (collections log, ticket, commit).", file=err)
```

## Usage

**Standardize the file and produce a manifest:**
```bash
python standardize_inventory.py inventory.tsv --force-https
```
```
Processed 6 rows (encoding: utf-8, header detected)
  ...
Source   sha256 9f2c41e0b7…
Output   sha256 4d81aa93c2…  inventory_standardized.tsv
Issues   sha256 07be5f1d44…  inventory_standardized_issues.tsv
Manifest sha256 b3e90c7a18…  inventory_standardized_manifest.json
```

**The manifest (abridged):**
```json
{
  "manifest_version": 1,
  "created_utc": "2025-01-15T14:02:11+00:00",
  "tool": {"name": "standardize_inventory.py", "version": "1.1.0", "sha256": "c0a4…", "python": "3.12.1"},
  "parameters": {"dayfirst": false, "force_https": true, "object_separator": null, ...},
  "source": {"path": "inventory.tsv", "sha256": "9f2c…", "bytes": 512, "encoding": "utf-8-sig",
             "header_detected": true, "column_mapping": {"date": 0, "title": 1, "object_number": 2, "link": 3},
             "data_rows": 6, "blank_lines_skipped": []},
  "output": {"path": "inventory_standardized.tsv", "sha256": "4d81…", "rows": 6},
  "report": {"path": "inventory_standardized_issues.tsv", "sha256": "07be…"},
  "rows_digest": "e61f…",
  "rows": [
    {"output_index": 0, "source_line": 2, "source_sha256": "a1b2…", "output_sha256": "5c6d…"},
    ...
  ]
}
```

**Verify later** (for example, before importing into a collections management system):
```bash
python standardize_inventory.py --verify inventory_standardized_manifest.json --rerun
```

All checks passing:
```
  OK    script is identical to the one that produced the output
  OK    source file unchanged (inventory.tsv, sha256 9f2c41e0b7a3…)
  OK    output file unchanged (inventory_standardized.tsv)
  OK    re-running standardization on the source reproduces the recorded output exactly
RESULT: PASS
```

Someone edited the source and hand-modified the output:
```
  FAIL  source file hash differs (1e77…  vs 9f2c…); checking individual records
        1 original record(s) missing or modified (original lines: [4])
        1 new or modified record(s) (current lines: [4])
  FAIL  output file hash differs; checking individual rows
        1 row(s) edited (output row #, source line): [(1, 3)]
RESULT: FAIL (2 check(s) failed)
```

Verify exits with `0` or `1`, so it can gate automated pipelines.

## Practical notes

- **Checksums show integrity, not correctness.** They prove the output came unaltered from a specific source via a specific procedure. The issues report is still what tells you whether a value was standardized *correctly*.
- **Store the manifest independently.** Anyone who can edit the output can also edit a manifest sitting next to it. For real tamper evidence:
  - record the manifest's SHA-256 in a separate system (collections log, ticket, git commit), or
  - sign it, e.g. `gpg --detach-sign inventory_standardized_manifest.json`, or add an HMAC with a key held by the registrar.
- **Archive the source file.** Verification and `--rerun` need the original bytes. Keep a read-only copy alongside the manifest.
- **Script changes are detected but don't fail verification.** If you improve the date parser, old manifests still verify file integrity. `--rerun` then shows exactly which rows would now standardize differently, which doubles as a regression test.
- **Use SHA-256, not MD5 or CRC.** MD5 and CRC aren't collision-resistant. SHA-256 is fast enough for any inventory size.
- **Downstream edits will break the output hash.** Once registrars correct flagged rows, the output is intentionally out of sync. At that point, run the corrected file through the script again (or hash it) to create a new manifest. Each manifest then links one version to the next, giving you a chain of custody across cleanup rounds.
