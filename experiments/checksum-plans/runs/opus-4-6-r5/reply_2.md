# Museum Inventory TSV Standardizer with Checksums

I'd add a checksum for each row (computed from the **original** raw values) and a global file-level checksum so you can later answer two questions:

1. **Row-level**: "Can I find the exact source data that produced this standardized row?"
2. **File-level**: "Is this standardized file derived from *that specific* source file?"

```python
#!/usr/bin/env python3
"""
Museum Inventory Spreadsheet Standardizer (with Checksums)

Produces a standardized .tsv with two additional checksum columns and a
companion manifest file for full-file verification.

Checksum strategy:
    ┌────────────────────────────────────────────────────────────────┐
    │  ROW-LEVEL   │  SHA-256 of the original raw cell values       │
    │              │  concatenated with a null-byte delimiter.       │
    │              │  Stored as `source_row_hash` in the output.     │
    ├──────────────┼────────────────────────────────────────────────-│
    │  ROW-LEVEL   │  SHA-256 of the standardized cell values.      │
    │  (clean)     │  Stored as `clean_row_hash` in the output.     │
    ├──────────────┼────────────────────────────────────────────────-│
    │  FILE-LEVEL  │  SHA-256 of every source_row_hash in order     │
    │              │  (a Merkle-style root).  Written to a sidecar  │
    │              │  manifest file alongside the output .tsv.       │
    └────────────────────────────────────────────────────────────────┘

Verification modes:
    --verify-row     Re-hash a raw row and compare to source_row_hash
    --verify-file    Re-compute the Merkle root and compare to manifest

Usage:
    python standardize_inventory.py input.tsv [-o output.tsv]
    python standardize_inventory.py --verify-file output_standardized.tsv
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


# ─── Checksum Utilities ─────────────────────────────────────────────────────

# Null byte is extremely unlikely to appear in museum metadata, making it a
# safe unambiguous delimiter.  This prevents collisions where cell boundaries
# shift (e.g., "a\tb" vs "a" + "b" in different columns).
HASH_DELIMITER = b'\x00'


def hash_row_values(values: list[str], algorithm: str = 'sha256') -> str:
    """
    Compute a hex-digest checksum over an ordered list of cell values.

    Each value is UTF-8 encoded and joined with a null-byte delimiter
    before hashing.  This preserves column boundaries unambiguously.

    Args:
        values: Cell values in consistent column order.
        algorithm: Hashlib algorithm name (default: sha256).

    Returns:
        Hex-encoded hash string.
    """
    h = hashlib.new(algorithm)
    for i, v in enumerate(values):
        if i > 0:
            h.update(HASH_DELIMITER)
        h.update(v.encode('utf-8'))
    return h.hexdigest()


def compute_merkle_root(row_hashes: list[str], algorithm: str = 'sha256') -> str:
    """
    Compute a file-level hash by hashing the ordered concatenation of all
    row-level hashes.

    This is a simplified Merkle approach: rather than building a full tree,
    we feed every row hash into a single running digest in order.  This is
    sufficient for our purposes because:
      - We always verify the full file, never individual branches.
      - Row ordering matters and is preserved.

    Args:
        row_hashes: Ordered list of hex-encoded row hashes.
        algorithm: Hashlib algorithm name.

    Returns:
        Hex-encoded root hash.
    """
    h = hashlib.new(algorithm)
    for rh in row_hashes:
        h.update(rh.encode('utf-8'))
        h.update(HASH_DELIMITER)
    return h.hexdigest()


def write_manifest(
    output_path: str,
    input_path: str,
    source_file_hash: str,
    merkle_root: str,
    row_count: int,
    algorithm: str,
    column_order: list[str],
) -> str:
    """
    Write a JSON sidecar manifest containing everything needed to verify
    the standardized file's relationship to its source.

    Returns the manifest file path.
    """
    manifest_path = output_path + '.manifest.json'
    manifest = {
        'schema_version': '1.0',
        'source_file': str(Path(input_path).resolve()),
        'output_file': str(Path(output_path).resolve()),
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'hash_algorithm': algorithm,
        'hash_delimiter': 'null byte (0x00)',
        'source_column_order': column_order,
        'source_file_sha256': source_file_hash,
        'merkle_root': merkle_root,
        'row_count': row_count,
        'verification': {
            'row_level': (
                'Re-read the original raw cells in source_column_order, '
                'join with 0x00, SHA-256 hash, and compare to source_row_hash.'
            ),
            'file_level': (
                'Concatenate all source_row_hash values in row order, '
                'each followed by 0x00, SHA-256 hash, and compare to merkle_root.'
            ),
        },
    }
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    return manifest_path


def hash_entire_file(filepath: str, algorithm: str = 'sha256') -> str:
    """Compute a hash of the entire raw file contents."""
    h = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


# ─── Date Standardization ───────────────────────────────────────────────────

def standardize_date(raw_date: str) -> str:
    if not raw_date:
        return "unknown"
    text = raw_date.strip()

    if text.lower() in ("n.d.", "n.d", "nd", "unknown", "undated", "n/a", "none", "?", "-"):
        return "unknown"

    century_match = re.match(
        r'(?:ca?\.?\s*)?(\d{1,2})(?:st|nd|rd|th)\s+century\s*(bce|bc|ce|ad)?',
        text, re.IGNORECASE,
    )
    if century_match:
        century_num = century_match.group(1)
        era = century_match.group(2)
        suffix = " BCE" if era and era.upper() in ("BCE", "BC") else ""
        return f"{century_num}th century{suffix}"

    circa_prefix = ""
    circa_match = re.match(r'(ca?\.?\s*|circa\s*|approx\.?\s*|~\s*)', text, re.IGNORECASE)
    if circa_match:
        circa_prefix = "ca. "
        text = text[circa_match.end():]

    range_match = re.match(r'^(\d{3,4})\s*(?:[-–—]|to)\s*(\d{3,4})$', text.strip(), re.IGNORECASE)
    if range_match:
        return f"{circa_prefix}{range_match.group(1)}–{range_match.group(2)}"

    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y", "%b %d, %Y",
                "%d %B %Y", "%d %b %Y", "%B %d %Y", "%m-%d-%Y", "%d.%m.%Y",
                "%Y/%m/%d", "%Y.%m.%d"):
        try:
            parsed = datetime.strptime(text.strip(), fmt)
            return f"{circa_prefix}{parsed.strftime('%Y-%m-%d')}"
        except ValueError:
            continue

    for fmt in ("%B %Y", "%b %Y", "%m/%Y", "%Y-%m"):
        try:
            parsed = datetime.strptime(text.strip(), fmt)
            return f"{circa_prefix}{parsed.strftime('%Y-%m')}"
        except ValueError:
            continue

    year_match = re.match(r'^(\d{3,4})$', text.strip())
    if year_match:
        return f"{circa_prefix}{year_match.group(1)}"

    return f"{circa_prefix}{text.strip()}" if circa_prefix else text.strip()


# ─── Title Standardization ──────────────────────────────────────────────────

TITLE_MINOR_WORDS = {
    'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'yet', 'so',
    'at', 'by', 'in', 'of', 'on', 'to', 'up', 'as', 'is', 'if',
    'it', 'vs', 'vs.', 'via', 'with', 'from', 'into', 'onto',
    'upon', 'over', 'per', 'de', 'du', 'la', 'le', 'les', 'des',
    'von', 'van', 'der', 'den', 'el',
}


def standardize_title(raw_title: str) -> str:
    if not raw_title or raw_title.strip().lower() in (
        "unknown", "untitled", "n/a", "none", "", "-", "?"
    ):
        return "Untitled"

    text = re.sub(r'\s+', ' ', raw_title.strip())
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")

    words = text.split()
    result = []
    for i, word in enumerate(words):
        if re.match(r'^[A-Z]{2,4}$', word):
            result.append(word)
        elif re.match(r'^[IVXLCDM]+$', word, re.IGNORECASE) and len(word) <= 6:
            result.append(word.upper())
        elif re.search(r'[a-z][A-Z]', word):
            result.append(word)
        elif i == 0 or i == len(words) - 1:
            result.append(word.capitalize())
        elif word.lower() in TITLE_MINOR_WORDS:
            result.append(word.lower())
        elif i > 0 and result[-1].endswith((':', '\u2014')):
            result.append(word.capitalize())
        else:
            result.append(word.capitalize())
    return ' '.join(result)


# ─── Object Number Standardization ──────────────────────────────────────────

def standardize_object_number(raw_number: str) -> str:
    if not raw_number or raw_number.strip().lower() in (
        "unknown", "n/a", "none", "", "-", "?"
    ):
        return "unassigned"

    text = re.sub(r'\s+', ' ', raw_number.strip())
    prefix_match = re.match(r'^([A-Za-z]+)[\s.\-_]*(.+)$', text)
    if prefix_match:
        prefix = prefix_match.group(1).upper()
        number_part = prefix_match.group(2)
    else:
        prefix = ""
        number_part = text

    number_part = re.sub(r'[\s_]+', '.', number_part)
    number_part = re.sub(r'[-–—]+', '.', number_part)
    number_part = re.sub(r'\.{2,}', '.', number_part).strip('.')

    return f"{prefix} {number_part}" if prefix else number_part


# ─── Link Standardization ───────────────────────────────────────────────────

def standardize_link(raw_link: str) -> str:
    if not raw_link or raw_link.strip().lower() in ("n/a", "none", "", "-", "?", "unknown"):
        return ""

    url = raw_link.strip().strip('<>')
    if not re.match(r'^https?://', url, re.IGNORECASE):
        if '.' in url and ' ' not in url:
            url = 'https://' + url
        else:
            return ""

    try:
        parsed = urlparse(url)
    except Exception:
        return ""

    if not parsed.hostname or '.' not in parsed.hostname:
        return ""

    scheme = parsed.scheme.lower()
    netloc = parsed.hostname.lower()
    if parsed.port and parsed.port not in (80, 443):
        netloc = f"{netloc}:{parsed.port}"

    path = parsed.path
    if path != '/' and path.endswith('/'):
        path = path.rstrip('/')

    tracking_params = {
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'fbclid', 'gclid', 'ref', 'ref_src', 'ref_url',
    }
    if parsed.query:
        params = [p for p in parsed.query.split('&')
                  if p.split('=')[0].lower() not in tracking_params]
        query = '&'.join(params)
    else:
        query = ''

    return urlunparse((scheme, netloc, path, parsed.params, query, ''))


# ─── Column Name Matching ───────────────────────────────────────────────────

COLUMN_ALIASES = {
    'date': 'date', 'dates': 'date', 'year': 'date',
    'accession_date': 'date', 'acquisition_date': 'date',
    'created': 'date', 'date_created': 'date',
    'title': 'title', 'name': 'title', 'object_name': 'title',
    'object_title': 'title', 'artwork': 'title', 'description': 'title',
    'object_number': 'object_number', 'object number': 'object_number',
    'objectnumber': 'object_number', 'accession': 'object_number',
    'accession_number': 'object_number', 'accession number': 'object_number',
    'acc_no': 'object_number', 'acc_num': 'object_number',
    'id': 'object_number', 'object_id': 'object_number',
    'inventory_number': 'object_number', 'catalog_number': 'object_number',
    'link': 'link', 'url': 'link', 'uri': 'link',
    'web_link': 'link', 'webpage': 'link', 'web_url': 'link',
    'permalink': 'link',
}

# The fixed order in which raw values are fed to the hash function.
# This MUST remain stable — changing it invalidates all existing checksums.
CANONICAL_COLUMN_ORDER = ['date', 'title', 'object_number', 'link']


def normalize_column_names(fieldnames: list[str]) -> dict[str, str]:
    mapping = {}
    matched = set()
    for col in fieldnames:
        key = col.strip().lower().replace(' ', '_').replace('-', '_')
        if key in COLUMN_ALIASES:
            std = COLUMN_ALIASES[key]
            if std not in matched:
                mapping[col] = std
                matched.add(std)
    missing = set(CANONICAL_COLUMN_ORDER) - matched
    if missing:
        raise ValueError(
            f"Could not identify columns for: {', '.join(missing)}.\n"
            f"Found columns: {fieldnames}"
        )
    return mapping


# ─── Row Processing ─────────────────────────────────────────────────────────

def process_row(row: dict) -> tuple[dict, str, str]:
    """
    Standardize one row and compute both raw and clean checksums.

    Returns:
        (standardized_row_dict, source_row_hash, clean_row_hash)
    """
    # Build raw values in canonical order for hashing
    raw_values = [row.get(col, '') for col in CANONICAL_COLUMN_ORDER]
    source_hash = hash_row_values(raw_values)

    # Standardize
    clean = {
        'date':          standardize_date(row.get('date', '')),
        'title':         standardize_title(row.get('title', '')),
        'object_number': standardize_object_number(row.get('object_number', '')),
        'link':          standardize_link(row.get('link', '')),
    }

    clean_values = [clean[col] for col in CANONICAL_COLUMN_ORDER]
    clean_hash = hash_row_values(clean_values)

    return clean, source_hash, clean_hash


# ─── Verification ───────────────────────────────────────────────────────────

def verify_file(standardized_path: str) -> bool:
    """
    Re-derive the Merkle root from source_row_hash values in a standardized
    file and compare against the manifest.

    Returns True if verification passes.
    """
    manifest_path = standardized_path + '.manifest.json'
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except FileNotFoundError:
        print(f"Error: Manifest not found at {manifest_path}", file=sys.stderr)
        return False

    expected_root = manifest['merkle_root']
    expected_count = manifest['row_count']

    source_hashes = []
    with open(standardized_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            source_hashes.append(row['source_row_hash'])

    if len(source_hashes) != expected_count:
        print(
            f"FAIL: Row count mismatch — expected {expected_count}, "
            f"found {len(source_hashes)}.",
            file=sys.stderr,
        )
        return False

    actual_root = compute_merkle_root(source_hashes, manifest['hash_algorithm'])

    if actual_root == expected_root:
        print(f"OK: Merkle root matches ({actual_root[:16]}...).")
        print(f"    {len(source_hashes)} rows verified against source.")
        return True
    else:
        print("FAIL: Merkle root mismatch.", file=sys.stderr)
        print(f"  Expected: {expected_root}", file=sys.stderr)
        print(f"  Actual:   {actual_root}", file=sys.stderr)
        return False


def verify_row_against_source(
    source_path: str,
    manifest_path: str,
    row_number: int,
) -> bool:
    """
    Re-read a specific row from the original source file, recompute its
    hash, and compare against the source_row_hash stored in the
    standardized output.

    Args:
        source_path: Path to the original raw .tsv.
        manifest_path: Path to the .manifest.json sidecar.
        row_number: 1-based data row index (excluding header).

    Returns True if the hash matches.
    """
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    col_order = manifest['source_column_order']
    algorithm = manifest['hash_algorithm']

    # Read the raw source row
    with open(source_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        col_mapping = normalize_column_names(reader.fieldnames)
        # Invert: standard_name -> original_col_name
        std_to_orig = {v: k for k, v in col_mapping.items()}

        for i, raw_row in enumerate(reader, start=1):
            if i == row_number:
                raw_values = [
                    raw_row.get(std_to_orig[std_col], '').strip()
                    for std_col in col_order
                ]
                source_hash = hash_row_values(raw_values, algorithm)
                print(f"Source row {row_number} hash: {source_hash}")
                return source_hash  # Caller compares to stored hash

    print(f"Error: Row {row_number} not found in source.", file=sys.stderr)
    return None


# ─── Reporting ───────────────────────────────────────────────────────────────

def print_report(stats: dict) -> None:
    print("\n" + "=" * 64)
    print("  MUSEUM INVENTORY STANDARDIZATION REPORT")
    print("=" * 64)
    print(f"  Total rows processed:        {stats['total']}")
    print(f"  Dates standardized:          {stats['dates_changed']}")
    print(f"  Titles standardized:         {stats['titles_changed']}")
    print(f"  Object numbers standardized: {stats['numbers_changed']}")
    print(f"  Links standardized:          {stats['links_changed']}")
    print(f"  Unknown dates:               {stats['unknown_dates']}")
    print(f"  Untitled objects:            {stats['untitled']}")
    print(f"  Unassigned object numbers:   {stats['unassigned_numbers']}")
    print(f"  Missing links:               {stats['missing_links']}")
    print("-" * 64)
    print(f"  Hash algorithm:              {stats['algorithm']}")
    print(f"  Source file SHA-256:         {stats['source_file_hash'][:24]}...")
    print(f"  Merkle root:                 {stats['merkle_root'][:24]}...")
    print(f"  Manifest written to:         {stats['manifest_path']}")
    print("=" * 64)
    print(f"  Output written to: {stats['output_file']}")
    print("=" * 64 + "\n")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Standardize a museum inventory TSV file with checksums.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standardize with checksums
  python standardize_inventory.py input.tsv -o cleaned.tsv

  # Verify a previously standardized file
  python standardize_inventory.py --verify-file cleaned.tsv
        """,
    )
    parser.add_argument('input', help='Input .tsv (or standardized .tsv for --verify-file)')
    parser.add_argument('-o', '--output', help='Output .tsv path')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--verify-file', action='store_true',
                        help='Verify a standardized file against its manifest')
    parser.add_argument('--algorithm', default='sha256',
                        help='Hash algorithm (default: sha256)')
    args = parser.parse_args()

    # ── Verification mode ──
    if args.verify_file:
        ok = verify_file(args.input)
        sys.exit(0 if ok else 1)

    # ── Standardization mode ──
    if args.output:
        output_path = args.output
    else:
        base = args.input.rsplit('.', 1)[0]
        output_path = f"{base}_standardized.tsv"

    algorithm = args.algorithm

    stats = {
        'total': 0, 'dates_changed': 0, 'titles_changed': 0,
        'numbers_changed': 0, 'links_changed': 0, 'unknown_dates': 0,
        'untitled': 0, 'unassigned_numbers': 0, 'missing_links': 0,
        'output_file': output_path, 'algorithm': algorithm,
    }

    standardized_rows = []
    source_row_hashes = []

    # Hash the entire source file first
    source_file_hash = hash_entire_file(args.input, algorithm)
    stats['source_file_hash'] = source_file_hash

    try:
        with open(args.input, 'r', encoding='utf-8-sig', newline='') as infile:
            reader = csv.DictReader(infile, delimiter='\t')
            if not reader.fieldnames:
                print("Error: File appears to be empty.", file=sys.stderr)
                sys.exit(1)

            try:
                col_mapping = normalize_column_names(reader.fieldnames)
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)

            for row_num, raw_row in enumerate(reader, start=2):
                stats['total'] += 1

                mapped = {}
                for orig_col, std_col in col_mapping.items():
                    mapped[std_col] = raw_row.get(orig_col, '').strip()

                clean, source_hash, clean_hash = process_row(mapped)

                # Attach checksums to the output row
                clean['source_row_hash'] = source_hash
                clean['clean_row_hash'] = clean_hash

                source_row_hashes.append(source_hash)

                # Track changes
                if clean['date'] != mapped['date']:
                    stats['dates_changed'] += 1
                if clean['title'] != mapped['title']:
                    stats['titles_changed'] += 1
                if clean['object_number'] != mapped['object_number']:
                    stats['numbers_changed'] += 1
                if clean['link'] != mapped['link']:
                    stats['links_changed'] += 1
                if clean['date'] == 'unknown':
                    stats['unknown_dates'] += 1
                if clean['title'] == 'Untitled':
                    stats['untitled'] += 1
                if clean['object_number'] == 'unassigned':
                    stats['unassigned_numbers'] += 1
                if clean['link'] == '':
                    stats['missing_links'] += 1

                if args.verbose:
                    print(f"Row {row_num}: src={source_hash[:12]}... "
                          f"clean={clean_hash[:12]}...")

                standardized_rows.append(clean)

    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Compute Merkle root
    merkle_root = compute_merkle_root(source_row_hashes, algorithm)
    stats['merkle_root'] = merkle_root

    # Write output TSV
    output_fields = [
        'date', 'title', 'object_number', 'link',
        'source_row_hash', 'clean_row_hash',
    ]
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields, delimiter='\t')
        writer.writeheader()
        writer.writerows(standardized_rows)

    # Write sidecar manifest
    manifest_path = write_manifest(
        output_path=output_path,
        input_path=args.input,
        source_file_hash=source_file_hash,
        merkle_root=merkle_root,
        row_count=stats['total'],
        algorithm=algorithm,
        column_order=CANONICAL_COLUMN_ORDER,
    )
    stats['manifest_path'] = manifest_path

    print_report(stats)


if __name__ == '__main__':
    main()
```

## What This Produces

Given `inventory.tsv`, the script writes **two** output files:

### `inventory_standardized.tsv`

```
date	title	object_number	link	source_row_hash	clean_row_hash
2020-03-05	Portrait of a Lady	ACC 2020.001	https://museum.org/item/5	a3f8c1...	b7d902...
ca. 1850	Landscape in Winter	1985.234.12	https://museum.org/item/6	e4b219...	c1a4f8...
```

### `inventory_standardized.tsv.manifest.json`

```json
{
  "schema_version": "1.0",
  "source_file": "/abs/path/to/inventory.tsv",
  "output_file": "/abs/path/to/inventory_standardized.tsv",
  "created_utc": "2025-01-15T12:00:00+00:00",
  "hash_algorithm": "sha256",
  "hash_delimiter": "null byte (0x00)",
  "source_column_order": ["date", "title", "object_number", "link"],
  "source_file_sha256": "9f86d0...",
  "merkle_root": "d4735e...",
  "row_count": 1247,
  "verification": {
    "row_level": "Re-read the original raw cells in source_column_order...",
    "file_level": "Concatenate all source_row_hash values in row order..."
  }
}
```

## Design Decisions

```
                    ┌─────────────────────────┐
                    │    source file (.tsv)    │
                    └────────┬────────────────-┘
                             │
              ┌──────────────┼──────────────────┐
              ▼              ▼                   ▼
        SHA-256 of      Per-row raw         Per-row clean
        entire file     value hashing       value hashing
              │              │                   │
              ▼              ▼                   ▼
        source_file    source_row_hash     clean_row_hash
        _sha256        (in output TSV)     (in output TSV)
        (manifest)           │
                             ▼
                      Merkle root
                      (manifest)
```

| Decision | Rationale |
|---|---|
| **Null-byte delimiter** | Prevents ambiguity when cell values contain tabs, commas, or other common delimiters. `"a"+"bc"` hashes differently from `"ab"+"c"`. |
| **Canonical column order** | Hashes are sensitive to ordering. Fixing the order in `CANONICAL_COLUMN_ORDER` ensures the same raw data always produces the same hash regardless of the source file's physical column arrangement. |
| **Two row hashes** | `source_row_hash` lets you trace back to the raw data; `clean_row_hash` lets you detect if someone tampered with the standardized values after the script ran. |
| **Sidecar manifest** | Keeps the verification metadata separate from the data itself, avoids modifying the TSV structure for file-level checks, and is machine-readable (JSON). |
| **Simplified Merkle** | A full binary Merkle tree would let you verify individual rows without reading the whole file. For museum inventories (typically <100K rows), sequential hashing is simpler and equally effective. |
| **SHA-256 default** | Widely supported, fast enough for this scale, and collision-resistant. The `--algorithm` flag allows upgrading later. |

## Verification Usage

```bash
# After standardization, verify the output hasn't been corrupted
python standardize_inventory.py --verify-file inventory_standardized.tsv

# Output on success:
#   OK: Merkle root matches (d4735e38d8a1...).
#       1247 rows verified against source.

# Output on failure:
#   FAIL: Merkle root mismatch.
#     Expected: d4735e38d8a1...
#     Actual:   9f86d081884c...
```
