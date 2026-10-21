## What the checksums have to prove

"Check against the source later" is really three different questions, and they want different hash inputs:

| Question | What you hash | Where it lives |
|---|---|---|
| *Is this output file still the one I produced?* | the output file's raw bytes | manifest (never in the file itself — self-reference) |
| *Did this row's upstream record change since the export?* | the **source** row's parsed field values | a column in the output + aggregate in manifest |
| *Did someone hand-edit a row in the clean file?* | the **normalized** field values | a column in the output + aggregate in manifest |
| *Would re-running the script reproduce this?* | source bytes + script version + every CLI flag | manifest |

That last one matters more than people expect: the output is a function of the input *and the options*, so `--fix-caps` or `--dayfirst` must be recorded or a future verification can't distinguish "data changed" from "flags changed."

## Design decisions worth stating explicitly

- **Hash parsed field values, not raw lines, for row-level digests.** If a registrar opens the source in Excel and re-saves it, the bytes change (CRLF, quoting style, BOM) but the records don't. Row digests over parsed fields survive that; the file-level digest correctly flags it.
- **Length-prefix each field** rather than joining with a separator, so no field content can forge a boundary (`"a\tb" + "c"` vs `"a" + "b\tc"`).
- **Version the digest scheme** (`mus-inv-digest/1`) and include it in the hash preimage, so a future change in canonicalization produces visibly different digests instead of silent mismatches.
- **Digest only the four canonical columns** for the record digest — not the derived `date_start`/`date_end` columns, which are a pure function of `date`. That way adding or dropping derived columns later doesn't invalidate every digest.
- **Two aggregates:** an order-dependent one and a sorted (order-independent) one. Sorting the spreadsheet by title then breaks only the first, which tells you "reordered, not altered." Use sorted concatenation, not XOR — XOR lets duplicate rows cancel in pairs.
- **Prefix the short digests** (`s1-…`, `n1-…`). A bare 16-char hex string that happens to be all digits will be silently converted to scientific notation by Excel and corrupted.

## Code to add

```python
# --------------------------------------------------------------------------
# Checksums
# --------------------------------------------------------------------------

import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

STANDARDIZER_VERSION = "1.0.0"   # bump when normalization RULES change
DIGEST_SCHEME = "mus-inv-digest/1"
SOURCE_PREFIX = "s1-"
RECORD_PREFIX = "n1-"
SHORT_LEN = 16                   # 64 bits; ~1e-10 collision risk at 100k rows

CANONICAL_FIELDS = ("date", "title", "object_number", "link")


def canonical_digest(scope: str, fields) -> str:
    """
    SHA-256 over length-prefixed UTF-8 field values.

    Canonicalization is deliberately minimal: values are hashed exactly as the
    CSV parser produced them (quoting, line endings and BOM already removed).
    No case folding, no whitespace collapsing, no Unicode re-normalization --
    the standardizer applies NFC itself, so the *record* digest covers
    post-NFC text while the *source-row* digest covers the file as written.
    """
    h = hashlib.sha256()
    h.update(DIGEST_SCHEME.encode("utf-8"))
    h.update(b"\x00" + scope.encode("utf-8") + b"\x00")
    for value in fields:
        b = (value or "").encode("utf-8")
        h.update(len(b).to_bytes(4, "big"))   # unambiguous framing
        h.update(b)
    return h.hexdigest()


def short_digest(hexdigest: str, prefix: str) -> str:
    return prefix + hexdigest[:SHORT_LEN]


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def aggregate_digests(hexdigests: list[str]) -> tuple[str, str]:
    """Return (order_dependent, order_independent) aggregates."""
    ordered = hashlib.sha256(DIGEST_SCHEME.encode() + b"\x00ordered\x00")
    for d in hexdigests:
        ordered.update(bytes.fromhex(d))
    unordered = hashlib.sha256(DIGEST_SCHEME.encode() + b"\x00unordered\x00")
    for d in sorted(hexdigests):
        unordered.update(bytes.fromhex(d))
    return ordered.hexdigest(), unordered.hexdigest()


def script_sha256() -> Optional[str]:
    try:
        return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except Exception:
        return None
```

Inside the row loop in `process()`, after the four fields are normalized:

```python
            source_hex = canonical_digest("source-row/v1", raw_row)
            record_hex = canonical_digest(
                "record/v1", [date_out, title_out, objnum_out, link_out])
            source_hexes.append(source_hex)
            record_hexes.append(record_hex)

            out_row = [date_out, title_out, objnum_out, link_out]
            if args.derived:
                out_row += [pd.start, pd.end, pd.qualifier]
            if args.checksums:
                out_row += [short_digest(source_hex, SOURCE_PREFIX),
                            short_digest(record_hex, RECORD_PREFIX)]
            out_row += [...extras...]
```

Note the ordering constraint: skipped duplicates must **not** contribute to the aggregates, so append to `source_hexes` / `record_hexes` only after the dedupe `continue`.

And the manifest, written after the output stream is closed:

```python
def write_manifest(args, stats, source_hexes, record_hexes,
                   source_header, output_header) -> dict:
    src_ordered, src_unordered = aggregate_digests(source_hexes)
    rec_ordered, rec_unordered = aggregate_digests(record_hexes)
    manifest = {
        "manifest_version": 1,
        "digest_scheme": DIGEST_SCHEME,
        "digest_algorithm": "sha256",
        "short_digest_chars": SHORT_LEN,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "standardizer": {
            "name": "standardize_inventory.py",
            "rules_version": STANDARDIZER_VERSION,
            "script_sha256": script_sha256(),
            "python": platform.python_version(),
        },
        # everything that affects the transform, so a rerun is reproducible
        "options": {k: v for k, v in sorted(vars(args).items())
                    if k not in ("report", "manifest", "quiet")},
        "source": {
            "path": args.input,
            "sha256": None if args.input == "-" else file_sha256(args.input),
            "bytes": None if args.input == "-" else os.path.getsize(args.input),
            "header": source_header,          # column order is part of the digest
            "row_digests_ordered": src_ordered,
            "row_digests_unordered": src_unordered,
        },
        "output": {
            "path": args.output,
            "sha256": None if args.output == "-" else file_sha256(args.output),
            "header": output_header,
            "hashed_columns": list(CANONICAL_FIELDS),
            "record_digests_ordered": rec_ordered,
            "record_digests_unordered": rec_unordered,
        },
        "counts": {
            "rows_read": stats.rows_in,
            "rows_written": stats.rows_out,
            "blank_rows_skipped": stats.blank_rows,
            "duplicates_dropped": stats.duplicates,
            "dates_unparsed": stats.dates_unparsed,
            "values_flagged": len(stats.issues),
        },
    }
    path = args.manifest or (args.output + ".manifest.json"
                             if args.output != "-" else None)
    if path:
        Path(path).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                              encoding="utf-8")
    return manifest
```

## The verify side

```python
def verify(args) -> int:
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    failures, warnings = [], []

    if manifest.get("digest_scheme") != DIGEST_SCHEME:
        warnings.append(f"manifest uses digest scheme {manifest.get('digest_scheme')!r}, "
                        f"this script implements {DIGEST_SCHEME!r}")
    if manifest["standardizer"]["rules_version"] != STANDARDIZER_VERSION:
        warnings.append(f"file produced by rules v{manifest['standardizer']['rules_version']}, "
                        f"this script is v{STANDARDIZER_VERSION}: digest differences may be "
                        f"rule changes rather than data changes")

    # 1. whole-file integrity
    expected = manifest["output"]["sha256"]
    actual = file_sha256(args.file)
    file_ok = (expected == actual)
    if not file_ok:
        warnings.append("output file digest differs from manifest; checking row by row")

    # 2. row-level: recompute record digests from the standardized file
    with open(args.file, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    recomputed, edited = [], []
    for n, row in enumerate(rows, start=2):
        hex_ = canonical_digest("record/v1", [row.get(c, "") for c in CANONICAL_FIELDS])
        recomputed.append(hex_)
        stored = row.get("record_digest")
        if stored and stored != short_digest(hex_, RECORD_PREFIX):
            edited.append((n, row.get("object_number", ""), stored))
    if edited:
        failures.append(f"{len(edited)} row(s) edited after standardization")
        for n, obj, _ in edited[:20]:
            print(f"  edited row {n}: {obj}", file=sys.stderr)

    ordered, unordered = aggregate_digests(recomputed)
    if unordered != manifest["output"]["record_digests_unordered"]:
        failures.append("record set does not match manifest (rows added, removed or changed)")
    elif ordered != manifest["output"]["record_digests_ordered"]:
        warnings.append("rows reordered, but content set is intact")
    elif file_ok:
        print("output matches manifest exactly", file=sys.stderr)

    # 3. optional: diff against a fresh export from the collection system
    if args.source:
        drift = diff_against_source(args.source, rows, manifest)
        for line in drift:
            print(line, file=sys.stderr)

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    for f in failures:
        print(f"FAIL: {f}", file=sys.stderr)
    return 1 if failures else 0


def diff_against_source(source_path, out_rows, manifest) -> list[str]:
    """Which upstream records changed since the export, keyed by object number."""
    with open(source_path, encoding="utf-8-sig", newline="") as fh:
        src = list(csv.reader(fh, delimiter="\t"))
    header, body = [clean_text(c) for c in src[0]], src[1:]
    if header != manifest["source"]["header"]:
        return ["source columns differ from the recorded export; digests not comparable"]

    colmap = map_columns(header)
    fresh = {}
    for row in body:
        if not any(clean_text(c) for c in row):
            continue
        idx = colmap["object_number"]
        objnum, _ = normalize_object_number(row[idx] if idx < len(row) else "")
        fresh[objnum.casefold()] = short_digest(
            canonical_digest("source-row/v1", row), SOURCE_PREFIX)

    recorded = {r["object_number"].casefold(): r.get("source_digest") for r in out_rows}
    changed = [k for k in recorded.keys() & fresh.keys() if recorded[k] != fresh[k]]
    out = [f"source drift: {len(fresh.keys() - recorded.keys())} new, "
           f"{len(recorded.keys() - fresh.keys())} withdrawn, {len(changed)} changed"]
    out += [f"  changed upstream: {k}" for k in sorted(changed)[:20]]
    return out
```

Wire it up with subcommands (`run` as the default so existing invocations keep working):

```bash
python3 standardize_inventory.py run in.tsv -o clean.tsv --checksums --report issues.tsv
python3 standardize_inventory.py verify clean.tsv --manifest clean.tsv.manifest.json
python3 standardize_inventory.py verify clean.tsv --manifest clean.tsv.manifest.json \
        --source 2026-03-export.tsv        # what moved upstream since last time
```

Output gains two columns:

```
date        title                 object_number  link   date_start … source_digest        record_digest
1893/1895~  The Gleaners at Dusk  1975.14.2a-b   https… 1893       … s1-4f1c9a0b7e23d558  n1-b02e7715cc9a41df
```

## Caveats to flag to whoever relies on this

- **Checksums detect accident, not an adversary.** Anyone who edits `clean.tsv` can rewrite `manifest.json` too. If the chain of custody needs to resist that, commit the manifest to a git repo (or sign it with `gpg --detach-sign` / minisign) and verify the signature, not just the hash.
- **Rules-version drift is the most common false alarm.** If you improve the century-parsing heuristic, every digest legitimately changes. That is why `rules_version` is in the manifest and why `verify` downgrades a mismatch to a warning when versions differ — the fix is to re-run and re-issue the manifest, with the old manifest retained as the record of what was true before.
- **The source digest is only as good as the export.** It proves the TSV row didn't change; it says nothing about whether the CMS record behind it changed in a field you didn't export. If that matters, export more columns — they're hashed into `source-row/v1` even though they pass through untouched.
- Hashing adds roughly one SHA-256 per row, so cost is negligible at any inventory size you'd keep in a spreadsheet.
