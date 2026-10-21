# Museum Inventory TSV Standardizer

```python
#!/usr/bin/env python3
"""
Museum Inventory Spreadsheet Standardizer

Reads a .tsv file with museum inventory data and standardizes the four columns:
- Date: Normalized to ISO 8601 format (YYYY-MM-DD or ranges/circa notations)
- Title: Cleaned and title-cased consistently
- Object Number: Standardized to a consistent accession number format
- Link: Validated and cleaned URLs

Usage:
    python standardize_inventory.py input.tsv [-o output.tsv]
"""

import argparse
import csv
import re
import sys
from datetime import datetime
from urllib.parse import urlparse, urlunparse


# ─── Date Standardization ───────────────────────────────────────────────────

def standardize_date(raw_date: str) -> str:
    """
    Standardize a wide variety of date formats into a consistent representation.

    Handles:
        - Common formats: "March 5, 2020", "5/3/2020", "2020-03-05", "05.03.2020"
        - Partial dates: "March 2020", "2020", "ca. 1850"
        - Ranges: "1850-1860", "1850–1860", "1850 to 1860"
        - Circa / approximate: "c. 1900", "ca 1900", "circa 1900", "~1900"
        - Century references: "19th century", "2nd century BCE"
        - Unknown / missing: "n.d.", "unknown", ""
    """
    if not raw_date:
        return "unknown"

    text = raw_date.strip()

    # ── Handle explicit unknowns ──
    if text.lower() in ("n.d.", "n.d", "nd", "unknown", "undated", "n/a", "none", "?", "-"):
        return "unknown"

    # ── Handle century references ──
    century_match = re.match(
        r'(?:ca?\.?\s*)?(\d{1,2})(?:st|nd|rd|th)\s+century\s*(bce|bc|ce|ad)?',
        text, re.IGNORECASE
    )
    if century_match:
        century_num = century_match.group(1)
        era = century_match.group(2)
        suffix = ""
        if era and era.upper() in ("BCE", "BC"):
            suffix = " BCE"
        return f"{century_num}th century{suffix}"

    # ── Detect and preserve circa prefix ──
    circa_prefix = ""
    circa_match = re.match(r'(ca?\.?\s*|circa\s*|approx\.?\s*|~\s*)', text, re.IGNORECASE)
    if circa_match:
        circa_prefix = "ca. "
        text = text[circa_match.end():]

    # ── Handle date ranges (e.g., "1850-1860", "1850 to 1860") ──
    range_match = re.match(
        r'(\d{3,4})\s*[-–—]|to\s*(\d{3,4})$', text, re.IGNORECASE
    )
    # More robust range detection
    range_match = re.match(
        r'^(\d{3,4})\s*(?:[-–—]|to)\s*(\d{3,4})$', text.strip(), re.IGNORECASE
    )
    if range_match:
        start_year = range_match.group(1)
        end_year = range_match.group(2)
        return f"{circa_prefix}{start_year}–{end_year}"

    # ── Try parsing full dates with common formats ──
    date_formats = [
        "%Y-%m-%d",       # 2020-03-05
        "%m/%d/%Y",       # 03/05/2020
        "%d/%m/%Y",       # 05/03/2020 (ambiguous, tried second)
        "%B %d, %Y",      # March 5, 2020
        "%b %d, %Y",      # Mar 5, 2020
        "%d %B %Y",       # 5 March 2020
        "%d %b %Y",       # 5 Mar 2020
        "%B %d %Y",       # March 5 2020
        "%m-%d-%Y",       # 03-05-2020
        "%d.%m.%Y",       # 05.03.2020
        "%Y/%m/%d",       # 2020/03/05
        "%Y.%m.%d",       # 2020.03.05
    ]

    for fmt in date_formats:
        try:
            parsed = datetime.strptime(text.strip(), fmt)
            return f"{circa_prefix}{parsed.strftime('%Y-%m-%d')}"
        except ValueError:
            continue

    # ── Handle month + year (e.g., "March 2020", "03/2020") ──
    month_year_formats = [
        "%B %Y",    # March 2020
        "%b %Y",    # Mar 2020
        "%m/%Y",    # 03/2020
        "%Y-%m",    # 2020-03
    ]
    for fmt in month_year_formats:
        try:
            parsed = datetime.strptime(text.strip(), fmt)
            return f"{circa_prefix}{parsed.strftime('%Y-%m')}"
        except ValueError:
            continue

    # ── Handle bare year ──
    year_match = re.match(r'^(\d{3,4})$', text.strip())
    if year_match:
        return f"{circa_prefix}{year_match.group(1)}"

    # ── Fallback: return cleaned original with circa if detected ──
    return f"{circa_prefix}{text.strip()}" if circa_prefix else text.strip()


# ─── Title Standardization ──────────────────────────────────────────────────

# Words that should remain lowercase in titles (AP/Chicago style)
TITLE_MINOR_WORDS = {
    'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'yet', 'so',
    'at', 'by', 'in', 'of', 'on', 'to', 'up', 'as', 'is', 'if',
    'it', 'vs', 'vs.', 'via', 'with', 'from', 'into', 'onto',
    'upon', 'over', 'per', 'de', 'du', 'la', 'le', 'les', 'des',
    'von', 'van', 'der', 'den', 'el',
}


def standardize_title(raw_title: str) -> str:
    """
    Clean and consistently format an artwork/object title.

    Rules:
        - Strip leading/trailing whitespace and collapse internal whitespace.
        - Apply title-case with minor words kept lowercase (except first/last).
        - Preserve text inside quotation marks or parentheses as-is.
        - Normalize quotes to standard double quotes.
        - Handle "Untitled" / "Unknown" consistently.
        - Preserve intentional ALL CAPS acronyms (2–4 consecutive capitals).
    """
    if not raw_title or raw_title.strip().lower() in (
        "unknown", "untitled", "n/a", "none", "", "-", "?"
    ):
        return "Untitled"

    text = raw_title.strip()

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Normalize quotation marks
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    text = text.replace('``', '"').replace("''", '"')

    # Apply title case with rules
    words = text.split()
    result = []

    for i, word in enumerate(words):
        # Preserve words that look like acronyms (2-4 uppercase letters)
        if re.match(r'^[A-Z]{2,4}$', word):
            result.append(word)
        # Preserve Roman numerals
        elif re.match(r'^[IVXLCDM]+$', word, re.IGNORECASE) and len(word) <= 6:
            result.append(word.upper())
        # Preserve words with internal caps (e.g., "iPhone", "McCoy")
        elif re.search(r'[a-z][A-Z]', word):
            result.append(word)
        # First and last words always capitalized
        elif i == 0 or i == len(words) - 1:
            result.append(word.capitalize())
        # Minor words stay lowercase
        elif word.lower() in TITLE_MINOR_WORDS:
            result.append(word.lower())
        # Capitalize after colon or em-dash
        elif i > 0 and result[-1].endswith((':',  '—')):
            result.append(word.capitalize())
        else:
            result.append(word.capitalize())

    return ' '.join(result)


# ─── Object Number Standardization ──────────────────────────────────────────

def standardize_object_number(raw_number: str) -> str:
    """
    Standardize museum accession/object numbers to a consistent format.

    Common patterns and their standardized forms:
        - "2020.123.4"   → "2020.123.4"      (dot-separated, already standard)
        - "2020-123-4"   → "2020.123.4"       (dash to dot)
        - "2020 123 4"   → "2020.123.4"       (space to dot)
        - "ACC2020.45"   → "ACC 2020.45"      (ensure space after prefix)
        - "RMA-2020-001" → "RMA 2020.001"     (prefix + normalize separators)
        - Leading zeros in segments are preserved (meaningful in accession numbers)
    """
    if not raw_number or raw_number.strip().lower() in (
        "unknown", "n/a", "none", "", "-", "?"
    ):
        return "unassigned"

    text = raw_number.strip()

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Detect alphabetic prefix like "ACC", "RMA", "OBJ", etc.
    prefix_match = re.match(r'^([A-Za-z]+)[\s.\-_]*(.+)$', text)

    if prefix_match:
        prefix = prefix_match.group(1).upper()
        number_part = prefix_match.group(2)
    else:
        prefix = ""
        number_part = text

    # Normalize separators in the number part: dashes, spaces, underscores → dots
    # But be careful not to merge things like "1a" letter suffixes
    number_part = re.sub(r'[\s_]+', '.', number_part)
    number_part = re.sub(r'[-–—]+', '.', number_part)

    # Collapse multiple dots
    number_part = re.sub(r'\.{2,}', '.', number_part)

    # Remove trailing/leading dots
    number_part = number_part.strip('.')

    if prefix:
        return f"{prefix} {number_part}"
    return number_part


# ─── Link Standardization ───────────────────────────────────────────────────

def standardize_link(raw_link: str) -> str:
    """
    Validate and clean a URL.

    Rules:
        - Add "https://" if no scheme is present.
        - Remove trailing slashes (unless it's just the domain root).
        - Remove common tracking parameters (utm_*, fbclid, etc.).
        - Lowercase the scheme and hostname.
        - Return empty string for clearly invalid URLs.
    """
    if not raw_link or raw_link.strip().lower() in (
        "n/a", "none", "", "-", "?", "unknown"
    ):
        return ""

    url = raw_link.strip()

    # Remove angle brackets sometimes used around URLs
    url = url.strip('<>').strip()

    # Add scheme if missing
    if not re.match(r'^https?://', url, re.IGNORECASE):
        # Check if it looks like a URL
        if '.' in url and ' ' not in url:
            url = 'https://' + url
        else:
            return ""  # Doesn't look like a valid URL

    try:
        parsed = urlparse(url)
    except Exception:
        return ""

    # Validate minimum structure
    if not parsed.hostname or '.' not in parsed.hostname:
        return ""

    # Lowercase scheme and hostname
    scheme = parsed.scheme.lower()
    hostname = parsed.hostname.lower()

    # Reconstruct port if present
    netloc = hostname
    if parsed.port and parsed.port not in (80, 443):
        netloc = f"{hostname}:{parsed.port}"

    # Clean path: remove trailing slash unless path is just "/"
    path = parsed.path
    if path != '/' and path.endswith('/'):
        path = path.rstrip('/')

    # Remove tracking query parameters
    tracking_params = {
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'fbclid', 'gclid', 'ref', 'ref_src', 'ref_url',
    }

    if parsed.query:
        params = parsed.query.split('&')
        cleaned_params = []
        for param in params:
            key = param.split('=')[0].lower()
            if key not in tracking_params:
                cleaned_params.append(param)
        query = '&'.join(cleaned_params)
    else:
        query = ''

    # Reconstruct
    cleaned = urlunparse((scheme, netloc, path, parsed.params, query, ''))

    return cleaned


# ─── Row Processing ─────────────────────────────────────────────────────────

def process_row(row: dict) -> dict:
    """Apply all standardization functions to a single inventory row."""
    return {
        'date':          standardize_date(row.get('date', '')),
        'title':         standardize_title(row.get('title', '')),
        'object_number': standardize_object_number(row.get('object_number', '')),
        'link':          standardize_link(row.get('link', '')),
    }


# ─── Column Name Matching ───────────────────────────────────────────────────

# Maps common variant column names to our standard internal names
COLUMN_ALIASES = {
    'date':            'date',
    'dates':           'date',
    'year':            'date',
    'accession_date':  'date',
    'acquisition_date':'date',
    'created':         'date',
    'date_created':    'date',

    'title':           'title',
    'name':            'title',
    'object_name':     'title',
    'object_title':    'title',
    'artwork':         'title',
    'description':     'title',

    'object_number':   'object_number',
    'object number':   'object_number',
    'objectnumber':    'object_number',
    'accession':       'object_number',
    'accession_number':'object_number',
    'accession number':'object_number',
    'acc_no':          'object_number',
    'acc_num':         'object_number',
    'id':              'object_number',
    'object_id':       'object_number',
    'inventory_number':'object_number',
    'catalog_number':  'object_number',

    'link':            'link',
    'url':             'link',
    'uri':             'link',
    'web_link':        'link',
    'webpage':         'link',
    'web_url':         'link',
    'permalink':       'link',
}


def normalize_column_names(fieldnames: list[str]) -> dict[str, str]:
    """
    Map the actual column names found in the TSV to our standard names.

    Returns a dict: {original_column_name: standard_name}
    Raises ValueError if required columns cannot be identified.
    """
    mapping = {}
    matched_standards = set()

    for col in fieldnames:
        normalized = col.strip().lower().replace(' ', '_').replace('-', '_')
        if normalized in COLUMN_ALIASES:
            standard = COLUMN_ALIASES[normalized]
            if standard not in matched_standards:
                mapping[col] = standard
                matched_standards.add(standard)

    required = {'date', 'title', 'object_number', 'link'}
    missing = required - matched_standards
    if missing:
        raise ValueError(
            f"Could not identify columns for: {', '.join(missing)}.\n"
            f"Found columns: {fieldnames}\n"
            f"Please rename columns to: date, title, object_number, link"
        )

    return mapping


# ─── Reporting ───────────────────────────────────────────────────────────────

def print_report(stats: dict) -> None:
    """Print a summary report of the standardization process."""
    print("\n" + "=" * 60)
    print("  MUSEUM INVENTORY STANDARDIZATION REPORT")
    print("=" * 60)
    print(f"  Total rows processed:        {stats['total']}")
    print(f"  Dates standardized:          {stats['dates_changed']}")
    print(f"  Titles standardized:         {stats['titles_changed']}")
    print(f"  Object numbers standardized: {stats['numbers_changed']}")
    print(f"  Links standardized:          {stats['links_changed']}")
    print(f"  Unknown dates:               {stats['unknown_dates']}")
    print(f"  Untitled objects:            {stats['untitled']}")
    print(f"  Unassigned object numbers:   {stats['unassigned_numbers']}")
    print(f"  Missing links:               {stats['missing_links']}")
    print("=" * 60)
    print(f"  Output written to: {stats['output_file']}")
    print("=" * 60 + "\n")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Standardize a museum inventory TSV file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python standardize_inventory.py inventory.tsv
  python standardize_inventory.py inventory.tsv -o cleaned_inventory.tsv
  python standardize_inventory.py inventory.tsv --verbose
        """
    )
    parser.add_argument('input', help='Path to the input .tsv file')
    parser.add_argument('-o', '--output', help='Path to the output .tsv file (default: input_standardized.tsv)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print each row change')
    args = parser.parse_args()

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        base = args.input.rsplit('.', 1)[0]
        output_path = f"{base}_standardized.tsv"

    # Statistics tracking
    stats = {
        'total': 0,
        'dates_changed': 0,
        'titles_changed': 0,
        'numbers_changed': 0,
        'links_changed': 0,
        'unknown_dates': 0,
        'untitled': 0,
        'unassigned_numbers': 0,
        'missing_links': 0,
        'output_file': output_path,
    }

    standardized_rows = []

    # Read input
    try:
        with open(args.input, 'r', encoding='utf-8-sig', newline='') as infile:
            reader = csv.DictReader(infile, delimiter='\t')
            if not reader.fieldnames:
                print("Error: File appears to be empty.", file=sys.stderr)
                sys.exit(1)

            # Map column names
            try:
                col_mapping = normalize_column_names(reader.fieldnames)
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)

            if args.verbose:
                print(f"Column mapping: {col_mapping}\n")

            for row_num, raw_row in enumerate(reader, start=2):  # start=2 because row 1 is header
                stats['total'] += 1

                # Remap columns to standard names
                mapped_row = {}
                for orig_col, std_col in col_mapping.items():
                    mapped_row[std_col] = raw_row.get(orig_col, '').strip()

                # Apply standardization
                clean_row = process_row(mapped_row)

                # Track changes
                if clean_row['date'] != mapped_row['date']:
                    stats['dates_changed'] += 1
                if clean_row['title'] != mapped_row['title']:
                    stats['titles_changed'] += 1
                if clean_row['object_number'] != mapped_row['object_number']:
                    stats['numbers_changed'] += 1
                if clean_row['link'] != mapped_row['link']:
                    stats['links_changed'] += 1

                # Track special values
                if clean_row['date'] == 'unknown':
                    stats['unknown_dates'] += 1
                if clean_row['title'] == 'Untitled':
                    stats['untitled'] += 1
                if clean_row['object_number'] == 'unassigned':
                    stats['unassigned_numbers'] += 1
                if clean_row['link'] == '':
                    stats['missing_links'] += 1

                if args.verbose:
                    changes = []
                    if clean_row['date'] != mapped_row['date']:
                        changes.append(f"  date: '{mapped_row['date']}' → '{clean_row['date']}'")
                    if clean_row['title'] != mapped_row['title']:
                        changes.append(f"  title: '{mapped_row['title']}' → '{clean_row['title']}'")
                    if clean_row['object_number'] != mapped_row['object_number']:
                        changes.append(f"  object_number: '{mapped_row['object_number']}' → '{clean_row['object_number']}'")
                    if clean_row['link'] != mapped_row['link']:
                        changes.append(f"  link: '{mapped_row['link']}' → '{clean_row['link']}'")
                    if changes:
                        print(f"Row {row_num}:")
                        print('\n'.join(changes))
                        print()

                standardized_rows.append(clean_row)

    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Write output
    output_fieldnames = ['date', 'title', 'object_number', 'link']

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames, delimiter='\t')
            writer.writeheader()
            writer.writerows(standardized_rows)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

    print_report(stats)


if __name__ == '__main__':
    main()
```

## How It Works

### Column Detection
The script automatically recognizes common column name variants (e.g., `Accession Number`, `acc_no`, `Object ID` → `object_number`) so you don't need to rename columns manually before running it.

### Standardization Rules

| Column | Input Examples | Standardized Output |
|---|---|---|
| **Date** | `March 5, 2020`, `5/3/2020`, `ca. 1850` | `2020-03-05`, `2020-03-05`, `ca. 1850` |
| **Date** | `1850-1860`, `19th century`, `n.d.` | `1850–1860`, `19th century`, `unknown` |
| **Title** | `portrait of a lady`, `UNTITLED` | `Portrait of a Lady`, `Untitled` |
| **Object Number** | `RMA-2020-001`, `2020 123 4` | `RMA 2020.001`, `2020.123.4` |
| **Link** | `museum.org/item/5?utm_source=x` | `https://museum.org/item/5` |

### Usage

```bash
# Basic usage (outputs to inventory_standardized.tsv)
python standardize_inventory.py inventory.tsv

# Specify output file
python standardize_inventory.py inventory.tsv -o cleaned.tsv

# See every change made
python standardize_inventory.py inventory.tsv --verbose
```

### Sample Report Output

```
============================================================
  MUSEUM INVENTORY STANDARDIZATION REPORT
============================================================
  Total rows processed:        1,247
  Dates standardized:          893
  Titles standardized:         421
  Object numbers standardized: 156
  Links standardized:          734
  Unknown dates:               32
  Untitled objects:            15
  Unassigned object numbers:   3
  Missing links:               88
============================================================
  Output written to: inventory_standardized.tsv
============================================================
```
