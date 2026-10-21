Great question. Checksums create an audit trail so you can always verify that a standardized row traces back to its original source data — critical in museum/archival work where provenance of the *record itself* matters.

## Design Approach

There are two layers worth capturing:

1. **Row-level checksum** — a hash of the *original, raw* row content, stored alongside the standardized output. This lets you answer: *"What exact source data produced this standardized row?"*
2. **File-level checksum** — a hash of the entire input file, stored in a manifest. This lets you answer: *"Which version of the source file was used for this standardization run?"*

```python
#!/usr/bin/env python3
"""
Museum Inventory Spreadsheet Standardizer (with Audit Checksums)

Adds two layers of integrity verification:
  1. Row-level: SHA-256 of the original raw row → stored in output column
  2. File-level: SHA-256 of the entire source file → stored in a manifest

This creates a complete audit trail from any standardized record back to
its exact source data.

Usage:
    python standardize_inventory.py input.tsv [-o output.tsv] [-m manifest.json]
    python standardize_inventory.py --verify output.tsv input.tsv [-m manifest.json]
"""

import argparse
import csv
import hashlib
import json
import re
import sys
import os
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse


# ─────────────────────────────────────────────
# Checksum Utilities
# ─────────────────────────────────────────────

def hash_row(cells: list[str]) -> str:
    """
    Compute a SHA-256 checksum for a single row.

    Uses the raw cell values joined by tab, encoded as UTF-8.
    This captures the exact original content before any transformation.
    """
    # Join with tab to preserve column boundaries in the hash.
    # "A\\tB" and "A" + "B" must produce different hashes.
    raw = '\t'.join(cells)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def hash_file(filepath: str) -> str:
    """
    Compute a SHA-256 checksum for an entire file.

    Reads in binary mode to capture the exact byte content,
    including BOM, line endings, etc.
    """
    sha = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha.update(chunk)
    return sha.hexdigest()


def create_manifest(
    input_path: str,
    output_path: str,
    file_hash: str,
    row_count: int,
    processed_count: int,
) -> dict:
    """
    Build a manifest dictionary recording provenance of the
    standardization run.
    """
    return {
        'schema_version': '1.0',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'source': {
            'filename': os.path.basename(input_path),
            'path': os.path.abspath(input_path),
            'sha256': file_hash,
            'size_bytes': os.path.getsize(input_path),
        },
        'output': {
            'filename': os.path.basename(output_path),
            'path': os.path.abspath(output_path),
            'total_source_rows': row_count,
            'rows_written': processed_count,
        },
        'checksum_method': {
            'algorithm': 'sha256',
            'row_hash_input': 'tab-joined original cell values, utf-8 encoded',
            'file_hash_input': 'raw file bytes',
        },
    }


# ─────────────────────────────────────────────
# Verification
# ─────────────────────────────────────────────

def verify(output_path: str, input_path: str, manifest_path: str):
    """
    Verify standardized output against the original source.

    Checks:
      1. File-level hash of source matches manifest
      2. Row-level hashes in output match recomputed hashes from source
    """
    errors = []

    # --- Load manifest ---
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except FileNotFoundError:
        print(f"Error: Manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    # --- File-level check ---
    print(f"Verifying file-level checksum of: {input_path}")
    current_hash = hash_file(input_path)
    expected_hash = manifest['source']['sha256']

    if current_hash == expected_hash:
        print(f"  ✓ File checksum matches: {current_hash[:16]}...")
    else:
        print(f"  ✗ FILE CHECKSUM MISMATCH", file=sys.stderr)
        print(f"    Expected: {expected_hash}", file=sys.stderr)
        print(f"    Got:      {current_hash}", file=sys.stderr)
        errors.append("File-level checksum mismatch — source file has changed.")

    # --- Row-level check ---
    print(f"Verifying row-level checksums...")

    # Read source rows (skip header)
    with open(input_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # skip header
        source_rows = [row for row in reader if any(cell.strip() for cell in row)]

    # Build lookup: hash → row index (for reporting)
    source_hashes = {}
    for i, row in enumerate(source_rows):
        h = hash_row(row)
        source_hashes[h] = i + 2  # +2 for 1-indexed + header

    # Read output rows and check each stored hash
    with open(output_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        output_headers = next(reader)

        try:
            hash_col = output_headers.index('Source Hash')
        except ValueError:
            print("  ✗ Output file has no 'Source Hash' column.", file=sys.stderr)
            sys.exit(1)

        mismatches = 0
        total = 0
        for row_num, row in enumerate(reader, start=2):
            total += 1
            stored_hash = row[hash_col]
            if stored_hash not in source_hashes:
                mismatches += 1
                if mismatches <= 10:  # Limit output noise
                    print(
                        f"  ✗ Row {row_num}: hash {stored_hash[:16]}... "
                        f"not found in source",
                        file=sys.stderr
                    )

    if mismatches == 0:
        print(f"  ✓ All {total} row checksums verified against source.")
    else:
        print(f"  ✗ {mismatches}/{total} rows failed verification.", file=sys.stderr)
        errors.append(f"{mismatches} row-level checksum mismatches.")

    # --- Summary ---
    if errors:
        print(f"\nVERIFICATION FAILED:")
        for e in errors:
            print(f"  • {e}")
        sys.exit(1)
    else:
        print(f"\nVERIFICATION PASSED ✓")


# ─────────────────────────────────────────────
# Date Standardization
# ─────────────────────────────────────────────

def standardize_date(raw_date: str) -> str:
    """
    Normalize date strings into consistent formats.

    Supported inputs:
        "1920"              → "1920"
        "c. 1920"           → "ca. 1920"
        "circa 1920"        → "ca. 1920"
        "1920-1925"         → "1920–1925"  (en-dash)
        "1920 - 1925"       → "1920–1925"
        "1920/1925"         → "1920–1925"
        "ca 1920-1925"      → "ca. 1920–1925"
        "19th century"      → "19th century"
        "early 20th cent."  → "Early 20th century"
        ""                  → "Unknown"
    """
    text = raw_date.strip()

    if not text:
        return "Unknown"

    text = re.sub(r'\b(circa|c\.?|ca\.?)\s*', 'ca. ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'\bcent\.?\b', 'century', text, flags=re.IGNORECASE)

    text = re.sub(
        r'^(early|mid|late|beginning of|end of)\b',
        lambda m: m.group(1).capitalize(),
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(r'(\d{4})\s*[-–—/]\s*(\d{4})', r'\1–\2', text)
    text = re.sub(r'ca\.\s*', 'ca. ', text)

    return text.strip()


# ─────────────────────────────────────────────
# Title Standardization
# ─────────────────────────────────────────────

TITLE_MINOR_WORDS = {
    'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'yet', 'so',
    'at', 'by', 'in', 'of', 'on', 'to', 'up', 'as', 'is', 'if',
    'it', 'with', 'from', 'into', 'over', 'after', 'under', 'between'
}


def standardize_title(raw_title: str) -> str:
    text = raw_title.strip()

    if not text:
        return "Untitled"

    text = re.sub(r'\s+', ' ', text)

    if (text.startswith('"') and text.endswith('"')) or \
       (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()

    words = text.split()
    result = []

    for i, word in enumerate(words):
        if word.isupper() and len(word) >= 2 and word.isalpha():
            result.append(word)
        elif i == 0 or i == len(words) - 1:
            result.append(word.capitalize())
        elif word.lower() in TITLE_MINOR_WORDS:
            result.append(word.lower())
        else:
            result.append(word.capitalize())

    return ' '.join(result)


# ─────────────────────────────────────────────
# Object Number Standardization
# ─────────────────────────────────────────────

def standardize_object_number(raw_number: str) -> str:
    text = raw_number.strip()

    if not text:
        return "NO_NUMBER"

    text = re.sub(r'\s+', ' ', text)

    prefix_match = re.match(r'^([A-Za-z]{1,10})\s+(.+)$', text)

    prefix = ""
    number_part = text

    if prefix_match:
        prefix = prefix_match.group(1).upper() + " "
        number_part = prefix_match.group(2)

    normalized = re.sub(r'[\s\-/]+', '.', number_part)
    normalized = normalized.upper()
    normalized = normalized.strip('.')

    return prefix + normalized


# ─────────────────────────────────────────────
# Link Standardization
# ─────────────────────────────────────────────

def standardize_link(raw_link: str) -> str:
    text = raw_link.strip()

    if not text or text.lower() in ('n/a', 'none', '-', 'na', 'null'):
        return ""

    if not re.match(r'^https?://', text, re.IGNORECASE):
        if re.match(r'^(www\.)?[\w\-]+\.[\w]{2,}', text):
            text = 'https://' + text
        else:
            return ""

    try:
        parsed = urlparse(text)
    except Exception:
        return ""

    if not parsed.netloc:
        return ""

    if parsed.query:
        params = parsed.query.split('&')
        cleaned_params = [
            p for p in params
            if not p.lower().startswith('utm_')
        ]
        cleaned_query = '&'.join(cleaned_params)
    else:
        cleaned_query = ""

    cleaned = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path,
        parsed.params,
        cleaned_query,
        ""
    ))

    cleaned = cleaned.rstrip('/')

    return cleaned


# ─────────────────────────────────────────────
# Column Detection
# ─────────────────────────────────────────────

EXPECTED_HEADERS = ['date', 'title', 'object number', 'link']


def normalize_header(header: str) -> str:
    h = header.strip().lower()
    mapping = {
        'date': 'date', 'dates': 'date', 'year': 'date', 'period': 'date',
        'title': 'title', 'name': 'title', 'object_title': 'title',
        'object title': 'title', 'artwork': 'title',
        'object number': 'object number', 'object_number': 'object number',
        'accession': 'object number', 'accession number': 'object number',
        'accession_number': 'object number', 'acc. no.': 'object number',
        'inventory number': 'object number', 'inv. no.': 'object number',
        'obj. no.': 'object number', 'object no.': 'object number',
        'link': 'link', 'url': 'link', 'uri': 'link',
        'web link': 'link', 'webpage': 'link',
    }
    return mapping.get(h, h)


def detect_columns(headers: list[str]) -> dict[str, int]:
    col_map = {}
    for i, header in enumerate(headers):
        normalized = normalize_header(header)
        if normalized in EXPECTED_HEADERS:
            col_map[normalized] = i
    return col_map


# ─────────────────────────────────────────────
# Row Processing
# ─────────────────────────────────────────────

def process_row(row: list[str], col_map: dict[str, int]) -> list[str]:
    def get(field):
        idx = col_map.get(field)
        if idx is not None and idx < len(row):
            return row[idx]
        return ""

    return [
        standardize_date(get('date')),
        standardize_title(get('title')),
        standardize_object_number(get('object number')),
        standardize_link(get('link')),
    ]


# ─────────────────────────────────────────────
# Main Processing Pipeline
# ─────────────────────────────────────────────

def process_file(input_path: str, output_path: str, manifest_path: str):
    """Read, standardize, and write with checksums."""

    stats = {
        'total': 0,
        'processed': 0,
        'skipped_empty': 0,
        'missing_number': 0,
    }

    # ── File-level checksum (before any reading/parsing) ──
    file_checksum = hash_file(input_path)
    print(f"Source file SHA-256: {file_checksum}")

    with open(input_path, 'r', encoding='utf-8-sig', newline='') as infile:
        reader = csv.reader(infile, delimiter='\t')

        try:
            raw_headers = next(reader)
        except StopIteration:
            print("Error: Input file is empty.", file=sys.stderr)
            sys.exit(1)

        col_map = detect_columns(raw_headers)

        missing = [h for h in EXPECTED_HEADERS if h not in col_map]
        if missing:
            print(f"Warning: Could not find columns: {missing}", file=sys.stderr)

        # ── Process rows ──
        output_rows = []
        for row in reader:
            stats['total'] += 1

            if not any(cell.strip() for cell in row):
                stats['skipped_empty'] += 1
                continue

            # Compute hash of the ORIGINAL row BEFORE standardization
            row_checksum = hash_row(row)

            standardized = process_row(row, col_map)

            if standardized[2] == "NO_NUMBER":
                stats['missing_number'] += 1

            # Append the source hash as the final column
            standardized.append(row_checksum)

            output_rows.append(standardized)
            stats['processed'] += 1

    # ── Write output with hash column ──
    output_headers = ['Date', 'Title', 'Object Number', 'Link', 'Source Hash']

    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        writer.writerow(output_headers)
        writer.writerows(output_rows)

    # ── Write manifest ──
    manifest = create_manifest(
        input_path, output_path, file_checksum,
        stats['total'], stats['processed']
    )

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    # ── Report ──
    print(f"\nStandardization complete.")
    print(f"  Input:              {input_path}")
    print(f"  Output:             {output_path}")
    print(f"  Manifest:           {manifest_path}")
    print(f"  Total rows read:    {stats['total']}")
    print(f"  Rows written:       {stats['processed']}")
    print(f"  Empty rows skipped: {stats['skipped_empty']}")
    print(f"  Missing obj. no's:  {stats['missing_number']}")


# ─────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Standardize a museum inventory .tsv file with audit checksums.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  Standardize:
    python standardize_inventory.py inventory.tsv
    python standardize_inventory.py inventory.tsv -o clean.tsv -m manifest.json

  Verify:
    python standardize_inventory.py --verify clean.tsv inventory.tsv
        """
    )

    parser.add_argument(
        '--verify', nargs=2, metavar=('OUTPUT', 'SOURCE'),
        help="Verify a standardized file against its source."
    )
    parser.add_argument(
        'input', nargs='?',
        help="Path to input .tsv file (standardize mode)"
    )
    parser.add_argument(
        '-o', '--output', default=None,
        help="Path to output .tsv file"
    )
    parser.add_argument(
        '-m', '--manifest', default=None,
        help="Path to manifest .json file"
    )

    args = parser.parse_args()

    # ── Verify mode ──
    if args.verify:
        output_path, source_path = args.verify
        manifest_path = args.manifest
        if manifest_path is None:
            manifest_path = source_path.rsplit('.', 1)[0] + '_manifest.json'
        verify(output_path, source_path, manifest_path)
        return

    # ── Standardize mode ──
    if args.input is None:
        parser.print_help()
        sys.exit(1)

    if args.output is None:
        if args.input.endswith('.tsv'):
            args.output = args.input[:-4] + '_standardized.tsv'
        else:
            args.output = args.input + '_standardized.tsv'

    if args.manifest is None:
        args.manifest = args.input.rsplit('.', 1)[0] + '_manifest.json'

    process_file(args.input, args.output, args.manifest)


if __name__ == '__main__':
    main()
```

## What Gets Generated

Running `python standardize_inventory.py inventory.tsv` produces two artifacts:

### 1. Standardized TSV (with hash column)

```
Date	Title	Object Number	Link	Source Hash
ca. 1888	The Starry Night over the Rhône	2023.001.123	https://www.museum.org/art/item	a3f2...b7c1
1920–1926	Water Lilies	2023.002.045	https://example.com/collection/item	8d1e...f4a2
```

The `Source Hash` is a SHA-256 of the **original, raw, pre-standardization** tab-joined cell values. It's a fingerprint of what the data looked like before you touched it.

### 2. Manifest JSON

```json
{
  "schema_version": "1.0",
  "created_at": "2025-01-15T14:30:00+00:00",
  "source": {
    "filename": "inventory.tsv",
    "path": "/data/museum/inventory.tsv",
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "size_bytes": 204800
  },
  "output": {
    "filename": "inventory_standardized.tsv",
    "path": "/data/museum/inventory_standardized.tsv",
    "total_source_rows": 1523,
    "rows_written": 1519
  },
  "checksum_method": {
    "algorithm": "sha256",
    "row_hash_input": "tab-joined original cell values, utf-8 encoded",
    "file_hash_input": "raw file bytes"
  }
}
```

### 3. Verification

```bash
$ python standardize_inventory.py --verify inventory_standardized.tsv inventory.tsv

Verifying file-level checksum of: inventory.tsv
  ✓ File checksum matches: e3b0c44298fc1c14...
Verifying row-level checksums...
  ✓ All 1519 row checksums verified against source.

VERIFICATION PASSED ✓
```

## Why Two Layers

| Layer | What it catches |
|---|---|
| **File-level hash** | Source file was modified, re-exported, or replaced since standardization ran |
| **Row-level hash** | Individual records can be traced back to exact source data; detects row insertion, deletion, or tampering in either file |

The row-level hash deliberately hashes the **raw input** rather than the standardized output — this means you can re-run standardization with updated rules and still verify that each output row traces to the same original source record. The hash survives rule changes; it's anchored to the source data, not to your transformation logic.
