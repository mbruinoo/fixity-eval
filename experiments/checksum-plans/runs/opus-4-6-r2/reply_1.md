# Museum Inventory TSV Standardizer

```python
#!/usr/bin/env python3
"""
Museum Inventory TSV Standardizer
==================================
Standardizes a museum inventory spreadsheet (.tsv) with 4 columns:
  - date
  - title
  - object number
  - link

Usage:
    python standardize_inventory.py input.tsv -o output.tsv
"""

import argparse
import csv
import re
import sys
from datetime import datetime
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Column‑level standardizers
# ---------------------------------------------------------------------------

def standardize_date(raw: str) -> str:
    """
    Attempt to parse a wide variety of date formats and return ISO 8601
    (YYYY-MM-DD).  If only a year is provided, return "YYYY".  If the date
    is a range (e.g. "1920-1925" or "c. 1920"), preserve it in a
    normalized form.  Unparseable values are returned as-is with a warning.
    """
    cleaned = raw.strip()

    if not cleaned:
        return ""

    # ---- Handle "circa" dates: c.1920, ca. 1920, circa 1920 ----
    circa_match = re.match(
        r'^(?:c\.?a?\.?\s*|circa\s+)(\d{4})$', cleaned, re.IGNORECASE
    )
    if circa_match:
        return f"ca. {circa_match.group(1)}"

    # ---- Handle year ranges: 1920-1925, 1920–1925, 1920 to 1925 ----
    range_match = re.match(
        r'^(\d{4})\s*[-–—]|to\s*(\d{4})$', cleaned
    )
    if range_match:
        years = re.findall(r'\d{4}', cleaned)
        if len(years) == 2:
            return f"{years[0]}/{years[1]}"

    # ---- Handle bare year ----
    if re.match(r'^\d{4}$', cleaned):
        return cleaned

    # ---- Handle century notations: "19th century" ----
    century_match = re.match(
        r'^(\d{1,2})(?:st|nd|rd|th)\s+century$', cleaned, re.IGNORECASE
    )
    if century_match:
        century = int(century_match.group(1))
        return f"{century}th century"

    # ---- Try common full‑date formats ----
    date_formats = [
        "%Y-%m-%d",         # 2024-01-15
        "%m/%d/%Y",         # 01/15/2024
        "%d/%m/%Y",         # 15/01/2024  (tried second)
        "%B %d, %Y",        # January 15, 2024
        "%b %d, %Y",        # Jan 15, 2024
        "%d %B %Y",         # 15 January 2024
        "%d %b %Y",         # 15 Jan 2024
        "%Y/%m/%d",         # 2024/01/15
        "%m-%d-%Y",         # 01-15-2024
        "%d-%m-%Y",         # 15-01-2024
        "%Y.%m.%d",         # 2024.01.15
        "%B %Y",            # January 2024
        "%b %Y",            # Jan 2024
    ]

    for fmt in date_formats:
        try:
            parsed = datetime.strptime(cleaned, fmt)
            # If the format had no day component, return YYYY-MM
            if fmt in ("%B %Y", "%b %Y"):
                return parsed.strftime("%Y-%m")
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # ---- Fallback: return original with warning ----
    print(f"  ⚠  Could not parse date: '{raw.strip()}'", file=sys.stderr)
    return cleaned


def standardize_title(raw: str) -> str:
    """
    Normalize whitespace, convert to title case (with common article/
    preposition handling), and strip leading/trailing punctuation debris.
    """
    cleaned = raw.strip()

    if not cleaned:
        return ""

    # Collapse multiple spaces / tabs
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # Remove wrapping quotes if present
    if (cleaned.startswith('"') and cleaned.endswith('"')) or \
       (cleaned.startswith("'") and cleaned.endswith("'")):
        cleaned = cleaned[1:-1].strip()

    # Title‑case with exceptions
    minor_words = {
        'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor',
        'on', 'at', 'to', 'by', 'in', 'of', 'up', 'as', 'is',
        'it', 'with', 'from', 'into', 'over'
    }

    words = cleaned.split()
    result = []
    for i, word in enumerate(words):
        lower = word.lower()
        # Always capitalize first and last word
        if i == 0 or i == len(words) - 1:
            result.append(word.capitalize())
        elif lower in minor_words:
            result.append(lower)
        else:
            result.append(word.capitalize())

    return ' '.join(result)


def standardize_object_number(raw: str) -> str:
    """
    Normalize an accession / object number:
      - Strip whitespace
      - Upper‑case all letters
      - Normalize separators (replace spaces around dots/dashes with
        a consistent format: e.g. "2024 . 15 . 3" → "2024.15.3")
    """
    cleaned = raw.strip()

    if not cleaned:
        return ""

    # Uppercase
    cleaned = cleaned.upper()

    # Remove spaces around common separators (. - /)
    cleaned = re.sub(r'\s*\.\s*', '.', cleaned)
    cleaned = re.sub(r'\s*-\s*', '-', cleaned)
    cleaned = re.sub(r'\s*/\s*', '/', cleaned)

    # Collapse any remaining multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)

    return cleaned


def standardize_link(raw: str) -> str:
    """
    Validate and normalize a URL:
      - Strip whitespace
      - Ensure it has a scheme (default to https://)
      - Basic validation via urlparse
      - Return empty string for clearly invalid values
    """
    cleaned = raw.strip()

    if not cleaned:
        return ""

    # Remove angle brackets sometimes used in data: <http://...>
    cleaned = re.sub(r'^<|>$', '', cleaned)

    # Add scheme if missing
    if not re.match(r'^https?://', cleaned, re.IGNORECASE):
        # If it looks like a domain, prepend https://
        if re.match(r'^[\w.-]+\.\w{2,}', cleaned):
            cleaned = 'https://' + cleaned
        else:
            print(
                f"  ⚠  Value does not look like a URL: '{raw.strip()}'",
                file=sys.stderr
            )
            return cleaned

    # Validate with urlparse
    parsed = urlparse(cleaned)
    if not parsed.netloc:
        print(
            f"  ⚠  Invalid URL: '{raw.strip()}'",
            file=sys.stderr
        )
        return cleaned

    # Rebuild to ensure consistent formatting
    return parsed.geturl()


# ---------------------------------------------------------------------------
# Row processor
# ---------------------------------------------------------------------------

STANDARDIZERS = [
    standardize_date,
    standardize_title,
    standardize_object_number,
    standardize_link,
]

STANDARD_HEADERS = ["date", "title", "object_number", "link"]


def detect_column_order(headers: list[str]) -> list[int]:
    """
    Try to map the input header row to the expected 4 columns by keyword
    matching.  Returns a list of indices into the original row, in the
    canonical order [date, title, object_number, link].
    Falls back to positional order if matching fails.
    """
    patterns = {
        0: re.compile(r'date|year|period|created', re.I),
        1: re.compile(r'title|name|description|object\s*name', re.I),
        2: re.compile(r'object|accession|number|id|inventory', re.I),
        3: re.compile(r'link|url|uri|href|web', re.I),
    }

    mapping: dict[int, int] = {}

    for canonical_idx, pattern in patterns.items():
        for col_idx, header in enumerate(headers):
            if pattern.search(header) and col_idx not in mapping.values():
                mapping[canonical_idx] = col_idx
                break

    if len(mapping) == 4:
        return [mapping[i] for i in range(4)]

    # Fallback: assume positional
    print(
        "  ℹ  Could not auto-detect columns from headers; "
        "assuming positional order.",
        file=sys.stderr
    )
    return list(range(min(4, len(headers))))


def process_row(row: list[str], col_order: list[int]) -> list[str]:
    """Apply standardizers to a single data row."""
    output = []
    for canonical_idx in range(4):
        source_idx = col_order[canonical_idx] if canonical_idx < len(col_order) else None
        raw_value = row[source_idx].strip() if (
            source_idx is not None and source_idx < len(row)
        ) else ""
        output.append(STANDARDIZERS[canonical_idx](raw_value))
    return output


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Standardize a museum inventory TSV file."
    )
    parser.add_argument(
        "input",
        help="Path to the input .tsv file"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Path to the output .tsv file (default: stdout)"
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Input file has no header row; assume positional columns"
    )
    parser.add_argument(
        "--delimiter",
        default="\t",
        help="Field delimiter (default: tab)"
    )
    args = parser.parse_args()

    # ---- Read input ----
    with open(args.input, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=args.delimiter)
        rows = list(reader)

    if not rows:
        print("Error: input file is empty.", file=sys.stderr)
        sys.exit(1)

    # ---- Determine column order ----
    if args.no_header:
        col_order = list(range(min(4, len(rows[0]))))
        data_rows = rows
    else:
        col_order = detect_column_order(rows[0])
        data_rows = rows[1:]

    # ---- Process ----
    standardized: list[list[str]] = []
    skipped = 0

    for line_num, row in enumerate(data_rows, start=2 if not args.no_header else 1):
        # Skip completely empty rows
        if not any(cell.strip() for cell in row):
            skipped += 1
            continue

        # Warn on rows with unexpected column count
        if len(row) < 4:
            print(
                f"  ⚠  Line {line_num}: expected ≥4 columns, got {len(row)}. "
                f"Padding with empty values.",
                file=sys.stderr
            )
            row.extend([""] * (4 - len(row)))

        standardized.append(process_row(row, col_order))

    # ---- Write output ----
    out_file = open(args.output, 'w', newline='', encoding='utf-8') \
        if args.output else sys.stdout

    try:
        writer = csv.writer(out_file, delimiter='\t', lineterminator='\n')
        writer.writerow(STANDARD_HEADERS)
        writer.writerows(standardized)
    finally:
        if out_file is not sys.stdout:
            out_file.close()

    # ---- Summary ----
    print(
        f"\n✔ Processed {len(standardized)} records "
        f"({skipped} empty rows skipped).",
        file=sys.stderr
    )
    if args.output:
        print(f"  Output written to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
```

## What It Does

### Column Detection
The script **auto-detects** which input column maps to which field by matching header keywords (e.g., a column called `"Accession Number"` maps to `object_number`). Falls back to positional order if headers aren't recognized.

### Standardization Rules

| Column | Transformations |
|---|---|
| **Date** | Parses dozens of formats → **ISO 8601** (`YYYY-MM-DD`); preserves "circa" dates as `ca. YYYY`; normalizes year ranges to `YYYY/YYYY`; bare years and centuries kept as-is |
| **Title** | Collapses whitespace, strips wrapping quotes, applies **title case** with minor-word exceptions (*a, an, the, of, in…*) |
| **Object Number** | Uppercases letters, removes stray spaces around separators (`.` `-` `/`), e.g. `2024 . 15 . 3a` → `2024.15.3A` |
| **Link** | Strips angle brackets, adds `https://` if scheme is missing, validates via `urlparse` |

### Usage Examples

```bash
# Basic — output to stdout
python standardize_inventory.py inventory_raw.tsv

# Write to a new file
python standardize_inventory.py inventory_raw.tsv -o inventory_clean.tsv

# Input has no header row
python standardize_inventory.py inventory_raw.tsv --no-header -o clean.tsv
```

### Sample Input → Output

**Input (`raw.tsv`)**:
```
Date Acquired	Object Title	Accession No	URL
January 15, 2024	"the starry night over   the rhône"	2024 . 1 . 15a	museum.org/objects/12345
c.1920	portrait of a YOUNG WOMAN	 MET-1920-42 	<http://example.com/item/42>
1850	  untitled	55.3.7	
```

**Output**:
```
date	title	object_number	link
2024-01-15	The Starry Night over the Rhône	2024.1.15A	https://museum.org/objects/12345
ca. 1920	Portrait of a Young Woman	MET-1920-42	http://example.com/item/42
1850	Untitled	55.3.7	
```
