Great question. Here's how I'd approach it and why.

## Design Rationale

Checksums serve two purposes here:

1. **Traceability** — Prove that a standardized row originated from a specific source row
2. **Integrity** — Detect if either the source or standardized file has been silently modified after processing

This means we want checksums on **both** the raw and standardized data, stored alongside the output so that verification can happen independently later, without re-running the full standardization.

I'd add three columns to the output:

| Column | What it hashes | Purpose |
|---|---|---|
| `source_row_hash` | The original raw fields, verbatim | "This cleaned row came from *that* raw row" |
| `standardized_row_hash` | The four cleaned fields | "This cleaned row hasn't been tampered with since processing" |
| `row_id` | Sequential row number from source | Locate the original row for manual audit |

And I'd write a **manifest file** alongside the output containing a whole-file checksum for both input and output files.

## Updated Script

```python
#!/usr/bin/env python3
"""
Museum Inventory TSV Standardizer (with checksums)

Reads a museum inventory spreadsheet (.tsv) with 4 columns:
  - date, title, object number, link

Standardizes formatting, appends per-row checksums, and writes
a cleaned output file plus a verification manifest.
"""

import csv
import re
import sys
import json
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urlunparse


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------

HASH_ALGORITHM = "sha256"


def hash_fields(fields: list[str], algorithm: str = HASH_ALGORITHM) -> str:
    """
    Produce a hex-digest checksum of an ordered list of field values.

    Fields are joined with a null byte separator to avoid ambiguity
    (e.g., ["a", "bc"] vs ["ab", "c"] produce different hashes).
    """
    h = hashlib.new(algorithm)
    joined = '\x00'.join(fields)
    h.update(joined.encode('utf-8'))
    return h.hexdigest()


def hash_file(filepath: str, algorithm: str = HASH_ALGORITHM) -> str:
    """
    Produce a hex-digest checksum of an entire file's contents,
    read in binary mode to capture the exact bytes on disk.
    """
    h = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Field standardizers (unchanged logic, condensed for focus on checksums)
# ---------------------------------------------------------------------------

def standardize_date(raw_date: str) -> str:
    cleaned = raw_date.strip()

    if not cleaned:
        return "unknown"

    if re.match(
        r'^(c\.?a?\.?\s*\d|n\.?\s*d\.?|circa|about|approx)',
        cleaned,
        re.IGNORECASE,
    ):
        cleaned = re.sub(r'^c\.?\s', 'ca. ', cleaned, flags=re.IGNORECASE)
        return cleaned

    date_formats = [
        "%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y",
        "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y",
        "%B %d %Y", "%Y/%m/%d", "%Y.%m.%d", "%m.%d.%Y",
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(cleaned, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    if re.match(r'^\d{4}$', cleaned):
        return cleaned

    if re.match(r'^\d{4}\s*[-–—]\s*\d{4}$', cleaned):
        return re.sub(r'\s*[-–—]\s*', '–', cleaned)

    return cleaned


def standardize_title(raw_title: str) -> str:
    cleaned = re.sub(r'\s+', ' ', raw_title.strip())

    if not cleaned:
        return "Untitled"

    small_words = {
        'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'yet', 'so',
        'at', 'by', 'in', 'of', 'on', 'to', 'up', 'as', 'is', 'if', 'it',
        'with', 'from', 'into', 'over', 'after', 'under', 'between',
        'de', 'la', 'le', 'les', 'du', 'des', 'von', 'van', 'del', 'di',
    }

    words = cleaned.split()
    result = []
    for i, word in enumerate(words):
        if word.isupper() and len(word) >= 2:
            result.append(word)
        elif i == 0 or i == len(words) - 1:
            result.append(word.capitalize())
        elif word.lower() in small_words:
            result.append(word.lower())
        else:
            result.append(word.capitalize())

    return ' '.join(result)


def standardize_object_number(raw_obj_num: str) -> str:
    cleaned = raw_obj_num.strip()
    if not cleaned:
        return "UNKNOWN"
    cleaned = cleaned.upper()
    cleaned = re.sub(r'\s*\.\s*', '.', cleaned)
    cleaned = re.sub(r'\s*-\s*', '-', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned


def standardize_link(raw_link: str) -> str:
    cleaned = raw_link.strip()
    if not cleaned:
        return ""
    if not re.match(r'^https?://', cleaned, re.IGNORECASE):
        cleaned = 'https://' + cleaned
    try:
        parsed = urlparse(cleaned)
        return urlunparse((
            parsed.scheme.lower(), parsed.netloc.lower(),
            parsed.path, parsed.params, parsed.query, parsed.fragment,
        ))
    except Exception:
        return cleaned


# ---------------------------------------------------------------------------
# Core processing
# ---------------------------------------------------------------------------

def process_inventory(
    input_path: str,
    output_path: str,
    has_header: bool = True,
) -> dict:
    """
    Read → standardize → write, attaching per-row checksums.

    Output columns:
        row_id | date | title | object_number | link
               | source_row_hash | standardized_row_hash
    """
    stats = {
        "total_rows": 0,
        "cleaned_rows": 0,
        "skipped_rows": 0,
        "missing_dates": 0,
        "missing_titles": 0,
        "missing_object_numbers": 0,
        "missing_links": 0,
        "duplicate_object_numbers": set(),
    }

    seen_object_numbers = {}
    output_rows = []

    standard_header = [
        "row_id",
        "date",
        "title",
        "object_number",
        "link",
        "source_row_hash",
        "standardized_row_hash",
    ]

    with open(input_path, 'r', encoding='utf-8-sig') as infile:
        reader = csv.reader(infile, delimiter='\t')

        for row_num, row in enumerate(reader, start=1):
            if has_header and row_num == 1:
                continue

            stats["total_rows"] += 1

            # ---- pad / truncate ----
            if len(row) < 4:
                row.extend([''] * (4 - len(row)))
                print(f"  Warning: Row {row_num} had < 4 columns (padded).")
            elif len(row) > 4:
                print(f"  Warning: Row {row_num} had > 4 columns (truncated).")
                row = row[:4]

            raw_date, raw_title, raw_obj_num, raw_link = row[:4]

            # ---- hash the raw fields BEFORE any cleaning ----
            source_hash = hash_fields([raw_date, raw_title, raw_obj_num, raw_link])

            # ---- standardize ----
            std_date = standardize_date(raw_date)
            std_title = standardize_title(raw_title)
            std_obj_num = standardize_object_number(raw_obj_num)
            std_link = standardize_link(raw_link)

            # ---- hash the cleaned fields ----
            standardized_hash = hash_fields([std_date, std_title, std_obj_num, std_link])

            # ---- bookkeeping ----
            if std_date == "unknown":
                stats["missing_dates"] += 1
            if std_title == "Untitled":
                stats["missing_titles"] += 1
            if std_obj_num == "UNKNOWN":
                stats["missing_object_numbers"] += 1
            if not std_link:
                stats["missing_links"] += 1

            if std_obj_num != "UNKNOWN":
                if std_obj_num in seen_object_numbers:
                    stats["duplicate_object_numbers"].add(std_obj_num)
                    print(
                        f"  Warning: Duplicate object number '{std_obj_num}' "
                        f"at rows {seen_object_numbers[std_obj_num]} and {row_num}."
                    )
                else:
                    seen_object_numbers[std_obj_num] = row_num

            output_rows.append([
                str(row_num),
                std_date,
                std_title,
                std_obj_num,
                std_link,
                source_hash,
                standardized_hash,
            ])
            stats["cleaned_rows"] += 1

    # ---- write standardized TSV ----
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        writer.writerow(standard_header)
        writer.writerows(output_rows)

    stats["duplicate_object_numbers"] = len(stats["duplicate_object_numbers"])
    return stats


# ---------------------------------------------------------------------------
# Manifest generation & verification
# ---------------------------------------------------------------------------

def write_manifest(
    input_path: str,
    output_path: str,
    stats: dict,
) -> str:
    """
    Write a JSON manifest containing:
      - whole-file checksums for input and output
      - processing statistics
      - algorithm used

    Returns the manifest file path.
    """
    manifest_path = output_path + '.manifest.json'

    manifest = {
        "algorithm": HASH_ALGORITHM,
        "source_file": {
            "path": str(Path(input_path).resolve()),
            "checksum": hash_file(input_path),
        },
        "output_file": {
            "path": str(Path(output_path).resolve()),
            "checksum": hash_file(output_path),
        },
        "stats": stats,
        "generated_by": "museum_inventory_standardizer",
    }

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    return manifest_path


def verify(output_path: str) -> bool:
    """
    Read a standardized TSV and its manifest, then check:
      1. The output file's whole-file hash matches the manifest.
      2. Every row's standardized_row_hash matches a fresh hash
         of that row's four data columns.

    Returns True if everything checks out.
    """
    manifest_path = output_path + '.manifest.json'

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    algorithm = manifest.get("algorithm", HASH_ALGORITHM)
    errors = []

    # ---- whole-file integrity ----
    expected_hash = manifest["output_file"]["checksum"]
    actual_hash = hash_file(output_path, algorithm)

    if actual_hash != expected_hash:
        errors.append(
            f"Output file checksum mismatch.\n"
            f"  Expected: {expected_hash}\n"
            f"  Actual:   {actual_hash}"
        )

    # ---- per-row integrity ----
    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for line_num, row in enumerate(reader, start=2):
            fields = [
                row["date"],
                row["title"],
                row["object_number"],
                row["link"],
            ]
            recomputed = hash_fields(fields, algorithm)

            if recomputed != row["standardized_row_hash"]:
                errors.append(
                    f"Row {row['row_id']} (line {line_num}): "
                    f"standardized_row_hash mismatch.\n"
                    f"  Stored:     {row['standardized_row_hash']}\n"
                    f"  Recomputed: {recomputed}"
                )

    if errors:
        print("VERIFICATION FAILED:")
        for err in errors:
            print(f"  ✗ {err}")
        return False

    print("VERIFICATION PASSED ✓")
    print(f"  File hash:  {actual_hash}")
    print(f"  Row hashes: all match")
    return True


def retrace(output_path: str, source_path: str) -> bool:
    """
    Given a standardized file and the original source file, verify
    that every source_row_hash in the output matches the corresponding
    row in the source (identified by row_id).

    This proves the standardized data actually came from that source.
    """
    algorithm = HASH_ALGORITHM

    # Try to read algorithm from manifest if present
    manifest_path = output_path + '.manifest.json'
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            algorithm = manifest.get("algorithm", HASH_ALGORITHM)
    except FileNotFoundError:
        pass

    # ---- build a lookup of raw row hashes by row number ----
    source_hashes = {}
    with open(source_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter='\t')
        for row_num, row in enumerate(reader, start=1):
            if len(row) < 4:
                row.extend([''] * (4 - len(row)))
            raw_fields = row[:4]
            source_hashes[str(row_num)] = hash_fields(raw_fields, algorithm)

    # ---- check each output row against the source ----
    errors = []
    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            row_id = row["row_id"]
            stored_source_hash = row["source_row_hash"]
            actual_source_hash = source_hashes.get(row_id)

            if actual_source_hash is None:
                errors.append(f"Row {row_id}: not found in source file.")
            elif stored_source_hash != actual_source_hash:
                errors.append(
                    f"Row {row_id}: source_row_hash mismatch.\n"
                    f"  In output: {stored_source_hash}\n"
                    f"  In source: {actual_source_hash}"
                )

    if errors:
        print("RETRACE FAILED:")
        for err in errors:
            print(f"  ✗ {err}")
        return False

    print("RETRACE PASSED ✓")
    print(f"  All source_row_hash values match the original file.")
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_summary(stats: dict) -> None:
    print("\n" + "=" * 55)
    print("  STANDARDIZATION SUMMARY")
    print("=" * 55)
    print(f"  Total rows processed:          {stats['total_rows']}")
    print(f"  Rows written to output:        {stats['cleaned_rows']}")
    print(f"  Missing dates (→ 'unknown'):   {stats['missing_dates']}")
    print(f"  Missing titles (→ 'Untitled'): {stats['missing_titles']}")
    print(f"  Missing object numbers:        {stats['missing_object_numbers']}")
    print(f"  Missing links:                 {stats['missing_links']}")
    print(f"  Duplicate object numbers:      {stats['duplicate_object_numbers']}")
    print("=" * 55 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Standardize a museum inventory TSV file (with checksums).",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ---- standardize ----
    sp_std = subparsers.add_parser("standardize", help="Standardize a TSV file")
    sp_std.add_argument("input_file", help="Path to the input .tsv file")
    sp_std.add_argument("-o", "--output", default=None,
                        help="Output .tsv path (default: <input>_standardized.tsv)")
    sp_std.add_argument("--no-header", action="store_true",
                        help="Input file has no header row")

    # ---- verify ----
    sp_ver = subparsers.add_parser(
        "verify",
        help="Verify integrity of a standardized file using its manifest",
    )
    sp_ver.add_argument("output_file", help="Path to the standardized .tsv file")

    # ---- retrace ----
    sp_ret = subparsers.add_parser(
        "retrace",
        help="Confirm standardized data traces back to a source file",
    )
    sp_ret.add_argument("output_file", help="Standardized .tsv file")
    sp_ret.add_argument("source_file", help="Original source .tsv file")

    args = parser.parse_args()

    if args.command == "standardize":
        input_path = args.input_file
        output_path = args.output or (
            input_path[:-4] + '_standardized.tsv'
            if input_path.endswith('.tsv')
            else input_path + '_standardized.tsv'
        )

        print(f"Reading from:  {input_path}")
        print(f"Writing to:    {output_path}")
        print(f"Hash algorithm:{HASH_ALGORITHM}")

        try:
            stats = process_inventory(input_path, output_path,
                                      has_header=not args.no_header)
            manifest_path = write_manifest(input_path, output_path, stats)
            print_summary(stats)
            print(f"Standardized file: {output_path}")
            print(f"Manifest file:     {manifest_path}")
        except FileNotFoundError:
            print(f"Error: File '{input_path}' not found.", file=sys.stderr)
            sys.exit(1)

    elif args.command == "verify":
        success = verify(args.output_file)
        sys.exit(0 if success else 1)

    elif args.command == "retrace":
        success = retrace(args.output_file, args.source_file)
        sys.exit(0 if success else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## How the Checksums Work

### Per-Row (inside the TSV)

```
Source row:  "March 5, 2021" | "the STARRY night" | "2021 . 45 . 3" | "www.museum.org/..."
                  │                                                          │
                  ▼                                                          ▼
         sha256("March 5, 2021\x00the STARRY night\x00...")   ← source_row_hash
                                                                (hashes RAW values)
                  │
          [ standardize ]
                  │
                  ▼
Clean row:  "2021-03-05" | "The Starry Night" | "2021.45.3" | "https://www.museum.org/..."
                  │
                  ▼
         sha256("2021-03-05\x00The Starry Night\x00...")      ← standardized_row_hash
                                                                (hashes CLEAN values)
```

The **null byte separator** (`\x00`) prevents field-boundary ambiguity — without it, shifting a character between adjacent fields could produce the same hash.

### Per-File (in the manifest)

```json
{
  "algorithm": "sha256",
  "source_file": {
    "path": "/abs/path/to/inventory.tsv",
    "checksum": "a3f2b8..."
  },
  "output_file": {
    "path": "/abs/path/to/inventory_standardized.tsv",
    "checksum": "d91c4e..."
  },
  "stats": { "..." }
}
```

### Three CLI Commands

```bash
# 1. Standardize (produces .tsv + .manifest.json)
python standardize_inventory.py standardize inventory.tsv

# 2. Verify output integrity (checks file hash + every row hash)
python standardize_inventory.py verify inventory_standardized.tsv

# 3. Retrace to source (proves each cleaned row came from the original)
python standardize_inventory.py retrace inventory_standardized.tsv inventory.tsv
```

### What Each Check Catches

| Scenario | Caught by |
|---|---|
| Someone edits a cell in the output file | `verify` — row hash mismatch |
| Output file is swapped entirely | `verify` — file hash mismatch |
| Source file was modified after processing | `retrace` — source hash mismatch |
| A row was deleted from the output | `verify` — file hash mismatch |
| A row was inserted into the output | `verify` — file hash mismatch |
| Claim that output came from a different source | `retrace` — source hash mismatch |
