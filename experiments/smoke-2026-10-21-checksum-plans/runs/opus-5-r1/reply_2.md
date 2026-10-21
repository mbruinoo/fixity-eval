Checksums here are answering four genuinely different questions, and it's worth separating them because a single hash column answers only one:

| Question | What to hash |
|---|---|
| Has the source file changed since I processed it? | raw bytes of the input file |
| Has *this row* of the source changed? | the row's parsed cells, canonicalized |
| Has the cleaned output been edited/corrupted? | output bytes + per-row digest |
| Would re-running produce the same thing? | tool version + effective options ("ruleset digest") |

The last one is the one people skip, and it's the one that bites you: a year later the output differs from the source and you can't tell whether the data drifted or your date parser got smarter.

## Design decisions worth making explicitly

**Hash parsed cells, not raw lines, at row level.** If you hash the literal line, a re-export that switches from `QUOTE_MINIMAL` to `QUOTE_ALL`, or CRLF→LF, flags every row as changed. Hashing the list of parsed cells makes quoting and line endings invisible. File-level byte hashing still covers the byte-exact case.

**Compute two row digests: raw and canonical.** The raw digest is the cells exactly as `csv` returned them; the canonical digest applies NFC + invisible-stripping + whitespace collapse (`clean_text`). If raw differs but canonical matches, someone re-exported with trailing spaces or a BOM — cosmetic. If canonical differs, the data actually changed. That distinction is most of the practical value.

**Make the digest order-independent.** Hash sorted `name=value` pairs joined with `\x1f`, not positional concatenation, so a column reorder in the next export doesn't invalidate everything.

**A hash is not a key.** Identity is `object_number` (plus row ordinal as fallback for blanks/dupes); the digest is the integrity check attached to that identity. Using the content hash as the join key means any legitimate edit looks like a delete + insert.

**Add set and sequence digests.** Per-row hashes alone don't detect deleted or reordered rows. A digest over the *sorted* row hashes catches add/delete; a digest over them *in order* catches reordering.

**Truncate for legibility, not for adversaries.** 16 hex chars = 64 bits; collision risk is negligible at inventory scale. Never truncate if you need tamper-evidence against a motivated party — and note that unsigned hashes are tamper-*detecting*, not tamper-*proof*, since anyone editing the data can recompute the manifest.

**Keep the deliverable four columns.** Write fixity to a sidecar (`*.fixity.tsv` + `*.manifest.json`) by default; `--embed-checksums` adds a `source_sha` column for shops that pass one file around.

## Drop-in module

```python
# ---------------------------------------------------------------- fixity ---
import hashlib, json, os, platform
from datetime import datetime, timezone

TOOL_NAME, TOOL_VERSION = "standardize_inventory.py", "1.1"
US = "\x1f"
CANON_SPEC = "NFC + strip-invisibles + collapse-whitespace + trim"

def file_digest(path, chunk=1 << 20) -> Tuple[str, int]:
    h, n = hashlib.sha256(), 0
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block); n += len(block)
    return h.hexdigest(), n

def row_digest(mapping: Dict[str, str], canonical: bool, length: int = 16) -> str:
    """Order-independent digest of a row's field/value pairs."""
    parts = []
    for k in sorted(mapping):
        v = mapping[k] or ""
        parts.append(f"{k}={clean_text(v) if canonical else v}")
    return hashlib.sha256(US.join(parts).encode("utf-8")).hexdigest()[:length]

def sequence_digest(hashes: Sequence[str]) -> str:
    return hashlib.sha256("\n".join(hashes).encode("utf-8")).hexdigest()

def set_digest(hashes: Sequence[str]) -> str:
    return hashlib.sha256("\n".join(sorted(hashes)).encode("utf-8")).hexdigest()

RULESET_KEYS = ("date_style", "expand_dates", "untitled", "fix_caps",
                "curly_quotes", "upper_object_numbers", "link_template",
                "force_https", "dedupe", "sort", "hash_length")

def ruleset_digest(args) -> Tuple[str, dict]:
    opts = {k: getattr(args, k, None) for k in RULESET_KEYS}
    opts["century_starts_at_01"] = CENTURY_STARTS_AT_01
    opts["canonicalization"] = CANON_SPEC
    blob = json.dumps(opts, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16], opts

def tool_digest() -> str:
    try:
        return file_digest(os.path.abspath(__file__))[0][:16]
    except OSError:
        return ""
```

Capture the raw cells before cleaning, then record three digests per row:

```python
def fixity_for_row(rec: Record, source_cells: Dict[str, str], length: int) -> dict:
    return {
        "row": rec.row,
        "object_number": rec.values.get("object_number", ""),
        "source_raw":   row_digest(source_cells, canonical=False, length=length),
        "source_canon": row_digest(source_cells, canonical=True,  length=length),
        "output_canon": row_digest({k: rec.values.get(k, "") for k in CANONICAL_FIELDS},
                                   canonical=True, length=length),
    }
```

And the manifest, written *after* the output file exists so you can hash it (you can't put a file's own hash inside itself — that's the one unavoidable reason for a sidecar):

```python
def write_manifest(path, args, src_path, out_path, fixity_rows, header):
    src_sha, src_bytes = file_digest(src_path)
    out_sha, out_bytes = file_digest(out_path)
    rs_sha, opts = ruleset_digest(args)
    src_hashes = [r["source_canon"] for r in fixity_rows]
    out_hashes = [r["output_canon"] for r in fixity_rows]
    manifest = {
        "manifest_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION,
                 "sha256_16": tool_digest(),
                 "python": platform.python_version()},
        "ruleset": {"sha256_16": rs_sha, "options": opts},
        "hash": {"algorithm": "sha256", "row_digest_length": args.hash_length,
                 "canonicalization": CANON_SPEC,
                 "scope": "parsed cells, sorted name=value pairs joined with U+001F"},
        "source": {"path": str(src_path), "bytes": src_bytes, "sha256": src_sha,
                   "rows": len(fixity_rows), "header": header,
                   "sequence_digest": sequence_digest(src_hashes),
                   "set_digest": set_digest(src_hashes)},
        "output": {"path": str(out_path), "bytes": out_bytes, "sha256": out_sha,
                   "rows": len(fixity_rows),
                   "sequence_digest": sequence_digest(out_hashes),
                   "set_digest": set_digest(out_hashes)},
        "rows_sidecar": str(Path(out_path).with_suffix(".fixity.tsv")),
    }
    Path(path).write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest
```

## Verify mode

```python
def verify(manifest_path, source_path=None, output_path=None, delimiter="\t"):
    m = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    src = Path(source_path or m["source"]["path"])
    out = Path(output_path or m["output"]["path"])
    L = m["hash"]["row_digest_length"]
    findings, status = [], "OK"

    if file_digest(out)[0] != m["output"]["sha256"]:
        findings.append(("ERROR", "output.modified",
                         "standardized file no longer matches its manifest"))
        status = "FAIL"

    src_ok = file_digest(src)[0] == m["source"]["sha256"]
    if src_ok:
        return status, findings or [("INFO", "ok", "source and output both verified")]

    # Byte-level mismatch: diagnose row by row.
    recorded = {(r["row"], r["object_number"]): r for r in load_sidecar(m["rows_sidecar"])}
    current  = read_source_rows(src, delimiter)           # -> {(row, objnum): cells}

    for key, rec in recorded.items():
        cells = current.get(key)
        if cells is None:
            findings.append(("ERROR", "source.row_missing", f"row {key[0]} {key[1]} gone"))
            status = "FAIL"; continue
        if row_digest(cells, True, L) != rec["source_canon"]:
            findings.append(("ERROR", "source.modified",
                             f"row {key[0]} {key[1]}: content changed"))
            status = "FAIL"
        elif row_digest(cells, False, L) != rec["source_raw"]:
            findings.append(("INFO", "source.cosmetic",
                             f"row {key[0]} {key[1]}: formatting-only difference"))
            status = status if status == "FAIL" else "COSMETIC"
    for key in set(current) - set(recorded):
        findings.append(("WARN", "source.row_added", f"new row {key[0]} {key[1]}"))
        status = status if status == "FAIL" else "DRIFT"
    return status, findings
```

Exit codes: `0` verified, `1` cosmetic-only drift, `2` substantive drift, `3` output tampered/missing.

The strongest check is `--verify --rerun`: if the source hash still matches, re-run the full transform in memory and compare against `output.sha256`. That validates the *code path*, not just the data — if it fails while the source verifies, your ruleset changed, and the `ruleset.sha256_16` in the manifest tells you by how much.

## What this won't do

- **It won't tell you what changed**, only that something did. Keep the change report from the main script; the checksum is the alarm, the report is the diagnosis.
- **It can't survive an Excel round-trip innocently.** Opening the TSV in Excel and saving will strip leading zeros from object numbers like `0001.23`, coerce `1890-05` into a serial date, and re-quote fields. That's arguably the best argument *for* this: those silent mutations are exactly what fixity catches. Document "verify before and after any spreadsheet editing" in the workflow.
- **Unsigned hashes aren't tamper-proof.** Anyone who edits the data can regenerate the manifest. If you need non-repudiation, sign the manifest (`gpg --detach-sign`) or deposit the hash in a system of record outside the working directory.
- **If the source is a live database export rather than a file**, the "source" is a snapshot — record the export timestamp, system, and query in `source` alongside the hash, or the hash describes something you can never reproduce.

## Prior art worth aligning with

If your institution already does digital preservation, don't invent a format: **BagIt** (RFC 8493) is the standard wrapper in libraries and archives, and its `manifest-sha256.txt` plus `bag-info.txt` is a drop-in substitute for the manifest above — emit a bag and your repository tooling can validate it with no custom code. **PREMIS** supplies the vocabulary (`fixity`, `messageDigestAlgorithm`, `messageDigest`) if the checksums need to land in a preservation metadata record. **Frictionless Data Package** (`datapackage.json`) is the lighter-weight option if the consumer is a data pipeline rather than a repository, and it has slots for both the hash and the column schema.
