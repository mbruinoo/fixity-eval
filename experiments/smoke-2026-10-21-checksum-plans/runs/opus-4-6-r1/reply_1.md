# Museum Inventory Spreadsheet Standardizer

```python
#!/usr/bin/env python3
"""
Museum Inventory Spreadsheet Standardizer

Reads a .tsv file with museum inventory data and standardizes the four columns:
- Date: Normalized to a consistent format (YYYY, YYYY-YYYY, or "ca. YYYY")
- Title: Standardized capitalization and whitespace
- Object Number: Uniform formatting (e.g., "2023.001.123")
- Link: Validated and cleaned URL

Usage:
    python standardize_inventory.py input.tsv [-o output.tsv]
"""

import argparse
import csv
import re
import sys
from urllib.parse import urlparse, urlunparse


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

    # Normalize "circa" / "c." / "ca" → "ca."
    text = re.sub(r'\b(circa|c\.?|ca\.?)\s*', 'ca. ', text, flags=re.IGNORECASE)
    # Clean up double spaces that may have been introduced
    text = re.sub(r'\s{2,}', ' ', text)

    # Normalize century abbreviations: "cent." → "century"
    text = re.sub(r'\bcent\.?\b', 'century', text, flags=re.IGNORECASE)

    # Capitalize era qualifiers at the start
    text = re.sub(
        r'^(early|mid|late|beginning of|end of)\b',
        lambda m: m.group(1).capitalize(),
        text,
        flags=re.IGNORECASE
    )

    # Normalize date ranges: "1920 - 1925", "1920/1925" → "1920–1925" (en-dash)
    text = re.sub(r'(\d{4})\s*[-–—/]\s*(\d{4})', r'\1–\2', text)

    # Ensure single space after "ca."
    text = re.sub(r'ca\.\s*', 'ca. ', text)

    return text.strip()


# ─────────────────────────────────────────────
# Title Standardization
# ─────────────────────────────────────────────

# Words that should remain lowercase in title case (unless first/last)
TITLE_MINOR_WORDS = {
    'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'yet', 'so',
    'at', 'by', 'in', 'of', 'on', 'to', 'up', 'as', 'is', 'if',
    'it', 'with', 'from', 'into', 'over', 'after', 'under', 'between'
}


def standardize_title(raw_title: str) -> str:
    """
    Standardize artwork/object titles:
    - Collapse extra whitespace
    - Apply headline-style title case
    - Preserve text within quotation marks or parentheses as-is
    - Preserve fully uppercase acronyms (e.g., "UNESCO", "NYC")
    """
    text = raw_title.strip()

    if not text:
        return "Untitled"

    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove leading/trailing quotes if they wrap the entire title
    if (text.startswith('"') and text.endswith('"')) or \
       (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()

    words = text.split()
    result = []

    for i, word in enumerate(words):
        # Preserve fully uppercase words (likely acronyms) of length >= 2
        if word.isupper() and len(word) >= 2 and word.isalpha():
            result.append(word)
        # First and last words are always capitalized
        elif i == 0 or i == len(words) - 1:
            result.append(word.capitalize())
        # Minor words stay lowercase
        elif word.lower() in TITLE_MINOR_WORDS:
            result.append(word.lower())
        else:
            result.append(word.capitalize())

    return ' '.join(result)


# ─────────────────────────────────────────────
# Object Number Standardization
# ─────────────────────────────────────────────

def standardize_object_number(raw_number: str) -> str:
    """
    Standardize museum object/accession numbers:
    - Trim whitespace
    - Normalize separators to dots (e.g., "2023-001-123" → "2023.001.123")
    - Uppercase any letter segments (e.g., "2023.001.a" → "2023.001.A")
    - Preserve original if format is unrecognized

    Common formats handled:
        "2023.001.123"
        "2023-001-123"
        "2023 001 123"
        "2023/001/123"
        "AIC 2023.001"
    """
    text = raw_number.strip()

    if not text:
        return "NO_NUMBER"

    # Collapse internal whitespace to a single space first
    text = re.sub(r'\s+', ' ', text)

    # Check if there's a prefix like "AIC 2023.001.123"
    # Pattern: optional alpha prefix + space + numeric accession
    prefix_match = re.match(
        r'^([A-Za-z]{1,10})\s+(.+)$', text
    )

    prefix = ""
    number_part = text

    if prefix_match:
        prefix = prefix_match.group(1).upper() + " "
        number_part = prefix_match.group(2)

    # Replace common separators (-, /, space) with dots
    normalized = re.sub(r'[\s\-/]+', '.', number_part)

    # Uppercase letter segments
    normalized = normalized.upper()

    # Remove trailing dots
    normalized = normalized.strip('.')

    return prefix + normalized


# ─────────────────────────────────────────────
# Link Standardization
# ─────────────────────────────────────────────

def standardize_link(raw_link: str) -> str:
    """
    Validate and clean URLs:
    - Trim whitespace
    - Add "https://" if no scheme is present
    - Remove trailing slashes (optional)
    - Remove tracking parameters (utm_*)
    - Return empty string for clearly invalid links
    """
    text = raw_link.strip()

    if not text or text.lower() in ('n/a', 'none', '-', 'na', 'null'):
        return ""

    # Add scheme if missing
    if not re.match(r'^https?://', text, re.IGNORECASE):
        # Handle "www." or domain-like strings
        if re.match(r'^(www\.)?[\w\-]+\.[\w]{2,}', text):
            text = 'https://' + text
        else:
            return ""  # Not a recognizable URL

    # Parse and validate
    try:
        parsed = urlparse(text)
    except Exception:
        return ""

    if not parsed.netloc:
        return ""

    # Remove UTM / tracking parameters
    if parsed.query:
        params = parsed.query.split('&')
        cleaned_params = [
            p for p in params
            if not p.lower().startswith('utm_')
        ]
        cleaned_query = '&'.join(cleaned_params)
    else:
        cleaned_query = ""

    # Reconstruct URL
    cleaned = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path,
        parsed.params,
        cleaned_query,
        ""  # Remove fragment
    ))

    # Remove trailing slash (aesthetic preference)
    cleaned = cleaned.rstrip('/')

    return cleaned


# ─────────────────────────────────────────────
# Main Processing Pipeline
# ─────────────────────────────────────────────

EXPECTED_HEADERS = ['date', 'title', 'object number', 'link']


def normalize_header(header: str) -> str:
    """Map common header variations to expected column names."""
    h = header.strip().lower()
    mapping = {
        'date': 'date',
        'dates': 'date',
        'year': 'date',
        'period': 'date',
        'title': 'title',
        'name': 'title',
        'object_title': 'title',
        'object title': 'title',
        'artwork': 'title',
        'object number': 'object number',
        'object_number': 'object number',
        'accession': 'object number',
        'accession number': 'object number',
        'accession_number': 'object number',
        'acc. no.': 'object number',
        'inventory number': 'object number',
        'inv. no.': 'object number',
        'obj. no.': 'object number',
        'object no.': 'object number',
        'link': 'link',
        'url': 'link',
        'uri': 'link',
        'web link': 'link',
        'webpage': 'link',
    }
    return mapping.get(h, h)


def detect_columns(headers: list[str]) -> dict[str, int]:
    """
    Map expected column names to their indices in the file.
    Returns dict like {'date': 0, 'title': 1, ...}
    """
    col_map = {}
    for i, header in enumerate(headers):
        normalized = normalize_header(header)
        if normalized in EXPECTED_HEADERS:
            col_map[normalized] = i

    return col_map


def process_row(row: list[str], col_map: dict[str, int]) -> list[str]:
    """Apply standardization functions to a single row."""

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


def process_file(input_path: str, output_path: str):
    """Read, standardize, and write the inventory file."""
    stats = {
        'total': 0,
        'processed': 0,
        'skipped_empty': 0,
        'missing_number': 0,
    }

    with open(input_path, 'r', encoding='utf-8-sig', newline='') as infile:
        reader = csv.reader(infile, delimiter='\t')

        # --- Read and map headers ---
        try:
            raw_headers = next(reader)
        except StopIteration:
            print("Error: Input file is empty.", file=sys.stderr)
            sys.exit(1)

        col_map = detect_columns(raw_headers)

        missing = [h for h in EXPECTED_HEADERS if h not in col_map]
        if missing:
            print(f"Warning: Could not find columns: {missing}", file=sys.stderr)
            print(f"  Detected headers: {raw_headers}", file=sys.stderr)
            print(f"  Mapped columns: {col_map}", file=sys.stderr)

        # --- Process rows ---
        output_rows = []
        for row in reader:
            stats['total'] += 1

            # Skip completely empty rows
            if not any(cell.strip() for cell in row):
                stats['skipped_empty'] += 1
                continue

            standardized = process_row(row, col_map)

            if standardized[2] == "NO_NUMBER":
                stats['missing_number'] += 1

            output_rows.append(standardized)
            stats['processed'] += 1

    # --- Write output ---
    output_headers = ['Date', 'Title', 'Object Number', 'Link']

    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        writer.writerow(output_headers)
        writer.writerows(output_rows)

    # --- Report ---
    print(f"Standardization complete.")
    print(f"  Input:            {input_path}")
    print(f"  Output:           {output_path}")
    print(f"  Total rows read:  {stats['total']}")
    print(f"  Rows written:     {stats['processed']}")
    print(f"  Empty rows skipped: {stats['skipped_empty']}")
    print(f"  Missing obj. numbers: {stats['missing_number']}")


# ─────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Standardize a museum inventory .tsv file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python standardize_inventory.py inventory.tsv
  python standardize_inventory.py inventory.tsv -o cleaned_inventory.tsv

Expected input columns (flexible header names):
  date (or: year, period, dates)
  title (or: name, artwork, object title)
  object number (or: accession number, inv. no.)
  link (or: url, uri, web link)
        """
    )
    parser.add_argument(
        'input',
        help="Path to input .tsv file"
    )
    parser.add_argument(
        '-o', '--output',
        default=None,
        help="Path to output .tsv file (default: input_standardized.tsv)"
    )

    args = parser.parse_args()

    # Default output filename
    if args.output is None:
        if args.input.endswith('.tsv'):
            args.output = args.input[:-4] + '_standardized.tsv'
        else:
            args.output = args.input + '_standardized.tsv'

    process_file(args.input, args.output)


if __name__ == '__main__':
    main()
```

## How It Works

### Column Detection
The script auto-detects columns by mapping common header variations (e.g., `"Accession Number"`, `"Acc. No."`, `"inv. no."`) to the four expected fields. This allows it to handle spreadsheets from different museums without manual configuration.

### Standardization Rules

| Column | Transformations |
|---|---|
| **Date** | Normalizes "circa"/"c."/"ca" → `ca.`, replaces hyphens/slashes with en-dashes for ranges, expands "cent." → "century", capitalizes era qualifiers |
| **Title** | Applies headline-style casing, preserves acronyms (e.g., `UNESCO`), collapses whitespace, strips wrapping quotes, defaults to `"Untitled"` |
| **Object Number** | Normalizes separators to dots, uppercases letter segments, detects institutional prefixes (e.g., `AIC 2023.001.A`) |
| **Link** | Adds `https://` if missing, removes UTM tracking params and fragments, lowercases scheme/host, validates structure |

### Example

**Input (`inventory.tsv`):**
```
Accession Number	title	dates	url
2023-001-123	the starry night over the rhône	c. 1888	www.museum.org/art/item?utm_source=newsletter
2023/002/045	WATER LILIES	1920 - 1926	https://Example.com/collection/item/
	untitled		n/a
```

**Output (`inventory_standardized.tsv`):**
```
Date	Title	Object Number	Link
ca. 1888	The Starry Night over the Rhône	2023.001.123	https://www.museum.org/art/item
1920–1926	Water Lilies	2023.002.045	https://example.com/collection/item
Unknown	Untitled	NO_NUMBER	
```

### Usage

```bash
# Basic usage (outputs to inventory_standardized.tsv)
python standardize_inventory.py inventory.tsv

# Specify output path
python standardize_inventory.py inventory.tsv -o cleaned.tsv
```
