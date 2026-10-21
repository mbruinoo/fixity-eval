Great question. Here's how I'd incorporate checksums to create a verifiable audit trail between source and standardized data.

## Design Rationale

The core idea is to capture **two checksums per row**:

1. **`source_hash`** — a hash of the original, unmodified row (proving what the input was)
2. **`standard_hash`** — a hash of the standardized row (proving what the output was)

This lets you answer several questions later:

- **"Was this row actually in the original file?"** → look up the `source_hash`
- **"Has the standardized data been tampered with after processing?"** → recompute and compare `standard_hash`
- **"Which rows actually changed?"** → compare `source_hash` to `standard_hash`; if they differ, standardization modified something
- **"Can I trace this standardized row back to its source?"** → join on `source_hash`

A separate **manifest file** stores the mappings so the main output stays clean.

```python
#!/usr/bin/env python3
"""
Museum Inventory TSV Standardizer — with Checksum Audit Trail

Produces:
  1. A standardized .tsv (same as before, optionally with hash columns appended)
  2. A manifest .json log mapping every source row to its standardized counterpart
     via cryptographic checksums.

Verification mode (--verify) re-reads both files and confirms integrity.
"""

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urlunparse


# ──────────────────────────────────────────────────────────────────────
# Checksum helpers
# ──────────────────────────────────────────────────────────────────────

HASH_ALGORITHM = "sha256"


def hash_row(fields: list[str], algorithm: str = HASH_ALGORITHM) -> str:
    """Compute a deterministic hash for an ordered list of field values.

    The fields are joined with a null byte (\\x00) separator so that
    ('a\\tb', 'c') and ('a', 'b\\tc') produce different hashes.
    The input is encoded as UTF-8 before hashing.
    """
    h = hashlib.new(algorithm)
    joined = "\x00".join(fields)
    h.update(joined.encode("utf-8"))
    return h.hexdigest()


def hash_file(path: str, algorithm: str = HASH_ALGORITHM) -> str:
    """Compute a whole-file hash for top-level integrity checking."""
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ──────────────────────────────────────────────────────────────────────
# Manifest dataclass-like helpers
# ──────────────────────────────────────────────────────────────────────

def create_manifest_entry(
    row_num: int,
    source_fields: list[str],
    standard_fields: list[str],
) -> dict:
    """Build one row-level manifest entry."""
    src_hash = hash_row(source_fields)
    std_hash = hash_row(standard_fields)
    return {
        "row": row_num,
        "source_hash": src_hash,
        "standard_hash": std_hash,
        "changed": src_hash != std_hash,
        # Store originals so the manifest is fully self-contained for audit
        "source_fields": source_fields,
        "standard_fields": standard_fields,
    }


def create_manifest(
    entries: list[dict],
    input_path: str,
    output_path: str,
) -> dict:
    """Build the top-level manifest document."""
    return {
        "schema_version": "1.0",
        "hash_algorithm": HASH_ALGORITHM,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "input_file": str(input_path),
        "output_file": str(output_path),
        # Whole-file checksums (filled in after files are written)
        "input_file_hash": None,
        "output_file_hash": None,
        "total_rows": len(entries),
        "rows_changed": sum(1 for e in entries if e["changed"]),
        "rows_unchanged": sum(1 for e in entries if not e["changed"]),
        "entries": entries,
    }


# ──────────────────────────────────────────────────────────────────────
# Standardization functions (same logic as before, condensed)
# ──────────────────────────────────────────────────────────────────────

DATE_FORMATS = [
    "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y", "%b %d, %Y",
    "%d %B %Y", "%d %b %Y", "%Y/%m/%d", "%Y.%m.%d", "%m-%d-%Y",
    "%B %Y", "%b %Y", "%Y-%m", "%m/%Y",
]
CIRCA_RE = re.compile(r"^(circa|ca?\.?|approx\.?)\s*", re.I)
RANGE_RE = re.compile(r"^(.+?)\s*(?:–|—|-|to|through)\s*(.+)$", re.I)
YEAR_RE = re.compile(r"^\d{4}$")
YEAR_RANGE_RE = re.compile(r"^(\d{4})\s*(?:–|—|-|to|through)\s*(\d{4})$", re.I)
TITLE_SMALL = {
    "a","an","the","and","but","or","nor","for","yet","so","at","by",
    "in","of","on","to","up","as","is","it","if","no","not","with",
    "from","into","over","upon",
}


def _parse_date(s):
    s = s.strip()
    if not s:
        return None
    if YEAR_RE.match(s):
        return s
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            if fmt in ("%B %Y", "%b %Y", "%Y-%m", "%m/%Y"):
                return dt.strftime("%Y-%m")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def standardize_date(raw):
    t = raw.strip()
    if not t:
        return ""
    circa = bool(CIRCA_RE.match(t))
    if circa:
        t = CIRCA_RE.sub("", t).strip()
    yrm = YEAR_RANGE_RE.match(t)
    if yrm:
        r = f"{yrm.group(1)}/{yrm.group(2)}"
        return f"ca. {r}" if circa else r
    rm = RANGE_RE.match(t)
    if rm:
        a, b = _parse_date(rm.group(1)), _parse_date(rm.group(2))
        if a and b:
            r = f"{a}/{b}"
            return f"ca. {r}" if circa else r
    p = _parse_date(t)
    if p:
        return f"ca. {p}" if circa else p
    return raw.strip()


def standardize_title(raw):
    t = re.sub(r"\s+", " ", raw.strip())
    if not t:
        return ""
    words = t.split()
    out = []
    for i, w in enumerate(words):
        if w.isupper() and len(w) > 1:
            out.append(w)
        elif i == 0 or i == len(words) - 1:
            out.append(w.capitalize())
        elif w.lower() in TITLE_SMALL:
            out.append(w.lower())
        else:
            out.append(w.capitalize())
    return " ".join(out)


def standardize_object_number(raw):
    t = raw.strip()
    if not t:
        return ""
    t = t.upper()
    t = re.sub(r"[\s_/\\]+", ".", t)
    t = re.sub(r"\.{2,}", ".", t)
    return t.strip(".")


def standardize_link(raw):
    t = raw.strip()
    if not t:
        return ""
    if not re.match(r"^https?://", t, re.I):
        t = "https://" + t
    p = urlparse(t)
    path = p.path.rstrip("/") if p.path != "/" else p.path
    query = "&".join(
        x for x in p.query.split("&") if not x.lower().startswith("utm_")
    ) if p.query else ""
    return urlunparse((p.scheme.lower(), p.netloc.lower(), path, p.params, query, p.fragment))


STANDARDIZERS = [standardize_date, standardize_title,
                 standardize_object_number, standardize_link]
EXPECTED_HEADERS = {"date", "title", "object number", "link"}


def standardize_row(row):
    return [
        STANDARDIZERS[i](f) if i < len(STANDARDIZERS) else f.strip()
        for i, f in enumerate(row)
    ]


def looks_like_header(row):
    return sum(c.strip().lower() in EXPECTED_HEADERS for c in row) >= 2


# ──────────────────────────────────────────────────────────────────────
# Core processing
# ──────────────────────────────────────────────────────────────────────

def process_file(
    infile,
    outfile,
    has_header: bool = True,
    embed_hashes: bool = False,
) -> list[dict]:
    """Standardize rows and collect manifest entries."""

    reader = csv.reader(infile, delimiter="\t")
    writer = csv.writer(outfile, delimiter="\t", lineterminator="\n")
    entries = []

    for row_num, row in enumerate(reader, start=1):
        if not row or all(c.strip() == "" for c in row):
            continue

        # Header row
        if row_num == 1 and has_header and looks_like_header(row):
            header = [c.strip().title() for c in row]
            if embed_hashes:
                header += ["Source_Hash", "Standard_Hash"]
            writer.writerow(header)
            continue

        # Pad short rows
        if len(row) < 4:
            row.extend([""] * (4 - len(row)))

        source_fields = list(row)          # snapshot before changes
        standard_fields = standardize_row(row)

        entry = create_manifest_entry(row_num, source_fields, standard_fields)
        entries.append(entry)

        out_row = standard_fields
        if embed_hashes:
            out_row = standard_fields + [entry["source_hash"],
                                         entry["standard_hash"]]
        writer.writerow(out_row)

    return entries


# ──────────────────────────────────────────────────────────────────────
# Verification
# ──────────────────────────────────────────────────────────────────────

def verify(manifest_path: str) -> bool:
    """Re-read a manifest and verify every checksum.

    Checks:
      1. Whole-file hashes for both input and output files.
      2. Per-row source_hash matches recomputed hash of stored source_fields.
      3. Per-row standard_hash matches recomputed hash of stored standard_fields.
      4. Re-standardizing source_fields produces the same standard_fields
         (determinism check).
    """
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    algo = manifest.get("hash_algorithm", HASH_ALGORITHM)
    errors = []

    # 1. Whole-file checks
    for key in ("input_file", "output_file"):
        fpath = manifest.get(key)
        expected = manifest.get(f"{key}_hash")
        if fpath and expected and Path(fpath).exists():
            actual = hash_file(fpath, algo)
            if actual != expected:
                errors.append(
                    f"File hash mismatch for {fpath}: "
                    f"expected {expected[:16]}…, got {actual[:16]}…"
                )
        elif fpath and expected:
            errors.append(f"File not found for verification: {fpath}")

    # 2–4. Per-row checks
    for entry in manifest["entries"]:
        row = entry["row"]
        src_fields = entry["source_fields"]
        std_fields = entry["standard_fields"]

        # Recompute hashes from stored fields
        src_recomputed = hash_row(src_fields, algo)
        std_recomputed = hash_row(std_fields, algo)

        if src_recomputed != entry["source_hash"]:
            errors.append(
                f"Row {row}: source_hash mismatch "
                f"(stored {entry['source_hash'][:16]}…, "
                f"recomputed {src_recomputed[:16]}…)"
            )

        if std_recomputed != entry["standard_hash"]:
            errors.append(
                f"Row {row}: standard_hash mismatch "
                f"(stored {entry['standard_hash'][:16]}…, "
                f"recomputed {std_recomputed[:16]}…)"
            )

        # Determinism: re-standardize and compare
        re_standardized = standardize_row(src_fields)
        if re_standardized != std_fields:
            errors.append(
                f"Row {row}: re-standardization produced different results "
                f"(non-deterministic transform)"
            )

    # Report
    if errors:
        print(f"VERIFICATION FAILED — {len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        return False
    else:
        n = len(manifest["entries"])
        print(
            f"VERIFICATION PASSED — {n} rows, "
            f"all checksums valid.",
            file=sys.stderr,
        )
        return True


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Standardize a museum inventory TSV with checksum audit trail."
    )
    sub = parser.add_subparsers(dest="command")

    # ── standardize ──
    std_p = sub.add_parser("standardize", help="Standardize a TSV file.")
    std_p.add_argument("input", help="Input .tsv path (or '-' for stdin).")
    std_p.add_argument("-o", "--output", default="-",
                       help="Output .tsv path (default: stdout).")
    std_p.add_argument("-m", "--manifest",
                       help="Path for the JSON manifest/audit log.")
    std_p.add_argument("--embed-hashes", action="store_true",
                       help="Append source_hash and standard_hash columns "
                            "to each output row.")
    std_p.add_argument("--no-header", action="store_true")

    # ── verify ──
    ver_p = sub.add_parser("verify",
                           help="Verify a previously generated manifest.")
    ver_p.add_argument("manifest", help="Path to the manifest .json file.")

    args = parser.parse_args()

    if args.command == "verify":
        ok = verify(args.manifest)
        sys.exit(0 if ok else 1)

    if args.command != "standardize":
        parser.print_help()
        sys.exit(1)

    # Open files
    in_is_stdin = args.input == "-"
    out_is_stdout = args.output == "-"
    infile = sys.stdin if in_is_stdin else open(
        args.input, "r", encoding="utf-8", newline="")
    outfile = sys.stdout if out_is_stdout else open(
        args.output, "w", encoding="utf-8", newline="")

    try:
        entries = process_file(
            infile, outfile,
            has_header=not args.no_header,
            embed_hashes=args.embed_hashes,
        )
    finally:
        if not in_is_stdin:
            infile.close()
        if not out_is_stdout:
            outfile.close()

    # Build and write manifest
    if args.manifest:
        manifest = create_manifest(entries, args.input, args.output)

        # Compute whole-file hashes (only for real files)
        if not in_is_stdin and Path(args.input).exists():
            manifest["input_file_hash"] = hash_file(args.input)
        if not out_is_stdout and Path(args.output).exists():
            manifest["output_file_hash"] = hash_file(args.output)

        with open(args.manifest, "w", encoding="utf-8") as mf:
            json.dump(manifest, mf, indent=2, ensure_ascii=False)

        print(f"Manifest written to {args.manifest}", file=sys.stderr)

    changed = sum(1 for e in entries if e["changed"])
    print(
        f"Done. {len(entries)} rows processed, {changed} changed.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
```

## How the Checksums Work

### Architecture

```
┌──────────────┐       standardize        ┌──────────────────┐
│  input.tsv   │ ──────────────────────►  │   output.tsv     │
│ (source data)│                          │ (clean data)     │
└──────┬───────┘                          └──────┬───────────┘
       │  SHA-256 (whole file)                   │  SHA-256 (whole file)
       ▼                                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    manifest.json                            │
│                                                             │
│  input_file_hash:  a3f8…                                    │
│  output_file_hash: 91b2…                                    │
│                                                             │
│  entries: [                                                 │
│    { row: 2,                                                │
│      source_hash:   "d4e5…"  ← hash(original fields)       │
│      standard_hash: "f6a7…"  ← hash(standardized fields)   │
│      changed: true,                                         │
│      source_fields:   ["Jan 15, 2023", ...],                │
│      standard_fields: ["2023-01-15", ...]                   │
│    }, ...                                                   │
│  ]                                                          │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Reasoning |
|---|---|
| **SHA-256** | Cryptographic strength — tamper-evident, not just error-detecting. Overkill for accidental corruption, appropriate if the audit trail has legal/compliance value. |
| **Null-byte field separator** | Joining fields with `\x00` before hashing prevents ambiguity. Without it, `["a\tb", "c"]` and `["a", "b\tc"]` would collide. |
| **Separate manifest file** | Keeps the output TSV clean and importable by other tools. The `--embed-hashes` flag is available when you want the hashes inline. |
| **Storing original fields in the manifest** | Makes the manifest fully self-contained — you can verify checksums even if the original file is lost. |
| **Whole-file hashes** | Catches any byte-level change (row reordering, encoding changes, trailing newlines) that row-level hashes wouldn't detect. |
| **Determinism check in verify** | Re-runs standardization on stored source fields and compares. This catches bugs introduced by code changes between the original run and verification. |

### Usage

```bash
# Standardize with full audit trail
python standardize_inventory.py standardize input.tsv \
    -o output.tsv \
    -m manifest.json

# Verify later
python standardize_inventory.py verify manifest.json
# → VERIFICATION PASSED — 847 rows, all checksums valid.

# Or embed hashes directly into the output TSV
python standardize_inventory.py standardize input.tsv \
    -o output.tsv \
    -m manifest.json \
    --embed-hashes
```

### Sample Manifest

```json
{
  "schema_version": "1.0",
  "hash_algorithm": "sha256",
  "created_utc": "2025-01-15T14:30:00+00:00",
  "input_file": "inventory.tsv",
  "output_file": "clean_inventory.tsv",
  "input_file_hash": "a3f8c9...full 64-char hex...",
  "output_file_hash": "91b2d4...full 64-char hex...",
  "total_rows": 3,
  "rows_changed": 3,
  "rows_unchanged": 0,
  "entries": [
    {
      "row": 2,
      "source_hash": "d4e5f6...",
      "standard_hash": "f6a7b8...",
      "changed": true,
      "source_fields": ["Jan 15, 2023", "the STARRY night", "2023/15/001", "HTTP://Example.com/art/001/"],
      "standard_fields": ["2023-01-15", "The Starry Night", "2023.15.001", "http://example.com/art/001"]
    }
  ]
}
```
