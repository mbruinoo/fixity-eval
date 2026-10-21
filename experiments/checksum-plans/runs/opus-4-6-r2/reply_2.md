Great question. Checksums create an **audit trail** — you can always verify that a standardized record traces back to a specific, unaltered source row. Here's how I'd approach it architecturally, followed by the implementation.

## Design Decisions

### What to checksum

| Checksum | Purpose |
|---|---|
| **`source_row_hash`** | SHA-256 of the **original raw row** (joined fields). Proves what the input looked like before any transformation. |
| **`standardized_row_hash`** | SHA-256 of the **standardized row**. Detects if the output file has been tampered with after generation. |

### Why both?

- `source_row_hash` alone tells you "this output came from this input," but if someone edits the output file, you can't tell.
- `standardized_row_hash` alone tells you the output is intact, but you lose provenance.
- **Together**, you get a complete chain: `raw → transformation → result`, all verifiable.

### Additional metadata

A separate **manifest file** (JSON) stores run-level metadata: timestamp, input file hash, script version, and the per-row checksums. This keeps the TSV clean while preserving full auditability.

---

## Implementation

```python
#!/usr/bin/env python3
"""
Museum Inventory TSV Standardizer — with Audit Checksums
=========================================================
Produces:
  1. A standardized .tsv output file
  2. A .manifest.json audit file with per-row and file-level checksums

Usage:
    python standardize_inventory.py input.tsv -o output.tsv
    python standardize_inventory.py --verify output.tsv --manifest output.manifest.json
"""

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse


SCRIPT_VERSION = "2.0.0"
STANDARD_HEADERS = ["date", "title", "object_number", "link"]

# ---------------------------------------------------------------------------
# Hashing utilities
# ---------------------------------------------------------------------------

def hash_string(s: str) -> str:
    """Return the hex SHA-256 digest of a UTF-8 string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def hash_row(fields: list[str], delimiter: str = "\t") -> str:
    """Join fields with the delimiter and hash the result."""
    return hash_string(delimiter.join(fields))


def hash_file(path: str) -> str:
    """Return the hex SHA-256 digest of an entire file's contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Column-level standardizers (same as before, condensed for clarity)
# ---------------------------------------------------------------------------

def standardize_date(raw: str) -> str:
    cleaned = raw.strip()
    if not cleaned:
        return ""

    circa_match = re.match(r'^(?:c\.?a?\.?\s*|circa\s+)(\d{4})$', cleaned, re.IGNORECASE)
    if circa_match:
        return f"ca. {circa_match.group(1)}"

    range_match = re.match(r'^(\d{4})\s*[-–—]|to\s*(\d{4})$', cleaned)
    if range_match:
        years = re.findall(r'\d{4}', cleaned)
        if len(years) == 2:
            return f"{years[0]}/{years[1]}"

    if re.match(r'^\d{4}$', cleaned):
        return cleaned

    century_match = re.match(r'^(\d{1,2})(?:st|nd|rd|th)\s+century$', cleaned, re.IGNORECASE)
    if century_match:
        return f"{int(century_match.group(1))}th century"

    date_formats = [
        "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y", "%b %d, %Y",
        "%d %B %Y", "%d %b %Y", "%Y/%m/%d", "%m-%d-%Y", "%d-%m-%Y",
        "%Y.%m.%d", "%B %Y", "%b %Y",
    ]
    for fmt in date_formats:
        try:
            parsed = datetime.strptime(cleaned, fmt)
            if fmt in ("%B %Y", "%b %Y"):
                return parsed.strftime("%Y-%m")
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    print(f"  ⚠  Could not parse date: '{raw.strip()}'", file=sys.stderr)
    return cleaned


def standardize_title(raw: str) -> str:
    cleaned = raw.strip()
    if not cleaned:
        return ""
    cleaned = re.sub(r'\s+', ' ', cleaned)
    if (cleaned.startswith('"') and cleaned.endswith('"')) or \
       (cleaned.startswith("'") and cleaned.endswith("'")):
        cleaned = cleaned[1:-1].strip()
    minor_words = {
        'a','an','the','and','but','or','for','nor','on','at',
        'to','by','in','of','up','as','is','it','with','from','into','over'
    }
    words = cleaned.split()
    result = []
    for i, word in enumerate(words):
        if i == 0 or i == len(words) - 1:
            result.append(word.capitalize())
        elif word.lower() in minor_words:
            result.append(word.lower())
        else:
            result.append(word.capitalize())
    return ' '.join(result)


def standardize_object_number(raw: str) -> str:
    cleaned = raw.strip()
    if not cleaned:
        return ""
    cleaned = cleaned.upper()
    cleaned = re.sub(r'\s*\.\s*', '.', cleaned)
    cleaned = re.sub(r'\s*-\s*', '-', cleaned)
    cleaned = re.sub(r'\s*/\s*', '/', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned


def standardize_link(raw: str) -> str:
    cleaned = raw.strip()
    if not cleaned:
        return ""
    cleaned = re.sub(r'^<|>$', '', cleaned)
    if not re.match(r'^https?://', cleaned, re.IGNORECASE):
        if re.match(r'^[\w.-]+\.\w{2,}', cleaned):
            cleaned = 'https://' + cleaned
        else:
            print(f"  ⚠  Value does not look like a URL: '{raw.strip()}'", file=sys.stderr)
            return cleaned
    parsed = urlparse(cleaned)
    if not parsed.netloc:
        print(f"  ⚠  Invalid URL: '{raw.strip()}'", file=sys.stderr)
        return cleaned
    return parsed.geturl()


STANDARDIZERS = [standardize_date, standardize_title, standardize_object_number, standardize_link]


# ---------------------------------------------------------------------------
# Column detection & row processing
# ---------------------------------------------------------------------------

def detect_column_order(headers: list[str]) -> list[int]:
    patterns = {
        0: re.compile(r'date|year|period|created', re.I),
        1: re.compile(r'title|name|description|object\s*name', re.I),
        2: re.compile(r'object|accession|number|id|inventory', re.I),
        3: re.compile(r'link|url|uri|href|web', re.I),
    }
    mapping = {}
    for canonical_idx, pattern in patterns.items():
        for col_idx, header in enumerate(headers):
            if pattern.search(header) and col_idx not in mapping.values():
                mapping[canonical_idx] = col_idx
                break
    if len(mapping) == 4:
        return [mapping[i] for i in range(4)]
    print("  ℹ  Could not auto-detect columns; assuming positional order.", file=sys.stderr)
    return list(range(min(4, len(headers))))


def process_row(row: list[str], col_order: list[int]) -> list[str]:
    output = []
    for canonical_idx in range(4):
        source_idx = col_order[canonical_idx] if canonical_idx < len(col_order) else None
        raw_value = row[source_idx].strip() if (
            source_idx is not None and source_idx < len(row)
        ) else ""
        output.append(STANDARDIZERS[canonical_idx](raw_value))
    return output


# ---------------------------------------------------------------------------
# Manifest (audit trail)
# ---------------------------------------------------------------------------

def build_manifest(
    input_path: str,
    output_path: str,
    row_records: list[dict],
    skipped: int,
) -> dict:
    """
    Build the full audit manifest dictionary.

    Each row_record contains:
        - row_number        (1-based, relative to data rows)
        - source_row_hash   (SHA-256 of the raw tab-joined row)
        - standard_row_hash (SHA-256 of the standardized tab-joined row)
    """
    return {
        "schema_version": "1.0",
        "script_version": SCRIPT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_file": {
            "path": os.path.abspath(input_path),
            "sha256": hash_file(input_path),
        },
        "output_file": {
            "path": os.path.abspath(output_path) if output_path else None,
            "sha256": hash_file(output_path) if output_path and os.path.exists(output_path) else None,
        },
        "statistics": {
            "total_rows_processed": len(row_records),
            "rows_skipped_empty": skipped,
        },
        "rows": row_records,
    }


def write_manifest(manifest: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"  Manifest written to: {path}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Verification mode
# ---------------------------------------------------------------------------

def verify(output_path: str, manifest_path: str) -> bool:
    """
    Re-read the output .tsv and the manifest, then:
      1. Verify the output file-level SHA-256.
      2. Verify each row's standardized_row_hash.

    Returns True if everything matches.
    """
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # --- File-level check ---
    expected_file_hash = manifest["output_file"]["sha256"]
    actual_file_hash = hash_file(output_path)

    if expected_file_hash != actual_file_hash:
        print(
            f"✖ FILE-LEVEL MISMATCH\n"
            f"  Expected: {expected_file_hash}\n"
            f"  Actual:   {actual_file_hash}",
            file=sys.stderr,
        )
        return False

    print("  ✔ File-level checksum matches.", file=sys.stderr)

    # --- Row-level checks ---
    with open(output_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)  # skip header
        data_rows = list(reader)

    row_records = manifest["rows"]
    mismatches = 0

    if len(data_rows) != len(row_records):
        print(
            f"  ⚠ Row count mismatch: file has {len(data_rows)}, "
            f"manifest has {len(row_records)}.",
            file=sys.stderr,
        )
        return False

    for record, row in zip(row_records, data_rows):
        actual_hash = hash_row(row)
        if actual_hash != record["standardized_row_hash"]:
            mismatches += 1
            print(
                f"  ✖ Row {record['row_number']}: hash mismatch\n"
                f"      Expected: {record['standardized_row_hash']}\n"
                f"      Actual:   {actual_hash}",
                file=sys.stderr,
            )

    if mismatches:
        print(f"\n✖ {mismatches} row(s) failed verification.", file=sys.stderr)
        return False

    print(f"  ✔ All {len(data_rows)} row checksums verified.", file=sys.stderr)
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Standardize a museum inventory TSV, with audit checksums."
    )
    subparsers = parser.add_subparsers(dest="command")

    # ---- Standardize sub-command (default when no sub-command given) ----
    std_parser = subparsers.add_parser("standardize", help="Standardize a TSV file.")
    std_parser.add_argument("input", help="Path to input .tsv")
    std_parser.add_argument("-o", "--output", required=True, help="Path to output .tsv")
    std_parser.add_argument("--no-header", action="store_true")
    std_parser.add_argument("--delimiter", default="\t")
    std_parser.add_argument(
        "--manifest",
        default=None,
        help="Path to manifest file (default: <output>.manifest.json)"
    )

    # ---- Verify sub-command ----
    ver_parser = subparsers.add_parser("verify", help="Verify output against manifest.")
    ver_parser.add_argument("output", help="Path to the standardized .tsv")
    ver_parser.add_argument("--manifest", required=True, help="Path to the manifest JSON")

    args = parser.parse_args()

    # Handle no subcommand (backward compat): treat as "standardize"
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # ---- VERIFY ----
    if args.command == "verify":
        ok = verify(args.output, args.manifest)
        sys.exit(0 if ok else 1)

    # ---- STANDARDIZE ----
    with open(args.input, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=args.delimiter)
        rows = list(reader)

    if not rows:
        print("Error: input file is empty.", file=sys.stderr)
        sys.exit(1)

    if args.no_header:
        col_order = list(range(min(4, len(rows[0]))))
        data_rows = rows
    else:
        col_order = detect_column_order(rows[0])
        data_rows = rows[1:]

    standardized: list[list[str]] = []
    row_records: list[dict] = []
    skipped = 0

    for line_num, row in enumerate(data_rows, start=1):
        if not any(cell.strip() for cell in row):
            skipped += 1
            continue

        if len(row) < 4:
            print(
                f"  ⚠  Line {line_num}: expected ≥4 columns, got {len(row)}. Padding.",
                file=sys.stderr,
            )
            row.extend([""] * (4 - len(row)))

        source_hash = hash_row(row)
        std_row = process_row(row, col_order)
        std_hash = hash_row(std_row)

        standardized.append(std_row)
        row_records.append({
            "row_number": line_num,
            "source_row_hash": source_hash,
            "standardized_row_hash": std_hash,
        })

    # Write output TSV
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(STANDARD_HEADERS)
        writer.writerows(standardized)

    # Build & write manifest
    manifest_path = args.manifest or args.output + ".manifest.json"
    manifest = build_manifest(args.input, args.output, row_records, skipped)
    write_manifest(manifest, manifest_path)

    print(
        f"\n✔ Processed {len(standardized)} records ({skipped} empty rows skipped).",
        file=sys.stderr,
    )
    print(f"  Output: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
```

## Usage

```bash
# Standardize and generate checksums
python standardize_inventory.py standardize raw.tsv -o clean.tsv

# Verify integrity later
python standardize_inventory.py verify clean.tsv --manifest clean.tsv.manifest.json
```

## What the Manifest Looks Like

```json
{
  "schema_version": "1.0",
  "script_version": "2.0.0",
  "generated_at": "2025-01-12T18:30:00+00:00",
  "input_file": {
    "path": "/data/raw.tsv",
    "sha256": "a1b2c3d4e5f6..."
  },
  "output_file": {
    "path": "/data/clean.tsv",
    "sha256": "f6e5d4c3b2a1..."
  },
  "statistics": {
    "total_rows_processed": 1523,
    "rows_skipped_empty": 4
  },
  "rows": [
    {
      "row_number": 1,
      "source_row_hash": "8f14e45f...",
      "standardized_row_hash": "3c59dc04..."
    },
    {
      "row_number": 2,
      "source_row_hash": "c74d97b0...",
      "standardized_row_hash": "e4da3b7f..."
    }
  ]
}
```

## How Verification Works

```
                    ┌──────────────────────────┐
                    │      SOURCE FILE         │
                    │   (original raw .tsv)    │
                    │                          │
                    │  file-level SHA-256 ──────────► manifest.input_file.sha256
                    │                          │
                    │  row 1 ──► SHA-256 ──────────► manifest.rows[0].source_row_hash
                    │  row 2 ──► SHA-256 ──────────► manifest.rows[1].source_row_hash
                    └────────────┬─────────────┘
                                 │
                        standardization
                                 │
                    ┌────────────▼─────────────┐
                    │      OUTPUT FILE         │
                    │  (standardized .tsv)     │
                    │                          │
                    │  file-level SHA-256 ──────────► manifest.output_file.sha256
                    │                          │
                    │  row 1 ──► SHA-256 ──────────► manifest.rows[0].standardized_row_hash
                    │  row 2 ──► SHA-256 ──────────► manifest.rows[1].standardized_row_hash
                    └──────────────────────────┘
```

The `verify` subcommand re-hashes the output file and every row, then compares against the stored manifest values. Any single-character change in any cell will cause a mismatch. And because the **source hashes** are preserved, you can always go back to the original file and confirm which raw row produced which standardized row — even years later.
