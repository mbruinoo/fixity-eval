# Museum Inventory TSV Standardizer

```python
#!/usr/bin/env python3
"""
Museum Inventory TSV Standardizer

Reads a museum inventory spreadsheet (.tsv) and standardizes the four columns:
  - Date: normalized to ISO 8601 format (YYYY-MM-DD), with support for
          partial dates (YYYY or YYYY-MM), date ranges, and circa dates.
  - Title: trimmed, normalized whitespace, and converted to title case.
  - Object Number: trimmed, uppercased, with separators standardized to dots.
  - Link: trimmed, lowercased scheme/host, and ensured to have https:// prefix.

Usage:
    python standardize_inventory.py input.tsv -o output.tsv
    cat input.tsv | python standardize_inventory.py - > output.tsv
"""

import argparse
import csv
import re
import sys
from datetime import datetime
from urllib.parse import urlparse, urlunparse


# ---------------------------------------------------------------------------
# Date Standardization
# ---------------------------------------------------------------------------

# Common date formats to try when parsing a full date string
DATE_FORMATS = [
    "%Y-%m-%d",       # 2023-01-15
    "%m/%d/%Y",       # 01/15/2023
    "%d/%m/%Y",       # 15/01/2023 (tried after m/d/Y; ambiguous cases default to m/d/Y)
    "%B %d, %Y",      # January 15, 2023
    "%b %d, %Y",      # Jan 15, 2023
    "%d %B %Y",       # 15 January 2023
    "%d %b %Y",       # 15 Jan 2023
    "%Y/%m/%d",       # 2023/01/15
    "%Y.%m.%d",       # 2023.01.15
    "%m-%d-%Y",       # 01-15-2023
    "%B %Y",          # January 2023
    "%b %Y",          # Jan 2023
    "%Y-%m",          # 2023-01
    "%m/%Y",          # 01/2023
]

# Pattern to detect "circa" prefixes
CIRCA_PATTERN = re.compile(
    r"^(circa|ca?\.?|approx\.?)\s*", re.IGNORECASE
)

# Pattern to detect date ranges separated by common delimiters
RANGE_PATTERN = re.compile(
    r"^(.+?)\s*(?:–|—|-|to|through)\s*(.+)$", re.IGNORECASE
)

# Pattern for bare years or year ranges
YEAR_PATTERN = re.compile(r"^\d{4}$")
YEAR_RANGE_PATTERN = re.compile(r"^(\d{4})\s*(?:–|—|-|to|through)\s*(\d{4})$", re.IGNORECASE)


def parse_single_date(date_str: str) -> str | None:
    """Attempt to parse a single date string into ISO 8601 format.

    Returns:
        A string like 'YYYY-MM-DD', 'YYYY-MM', or 'YYYY', or None if
        the string cannot be parsed.
    """
    cleaned = date_str.strip()

    if not cleaned:
        return None

    # Bare year
    if YEAR_PATTERN.match(cleaned):
        return cleaned

    # Try each known format
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(cleaned, fmt)
            # Determine precision from the format
            if fmt in ("%B %Y", "%b %Y", "%Y-%m", "%m/%Y"):
                return dt.strftime("%Y-%m")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def standardize_date(raw: str) -> str:
    """Standardize a date field.

    Handles:
      - Standard dates in many formats → YYYY-MM-DD
      - Partial dates → YYYY-MM or YYYY
      - Circa / approximate prefixes → 'ca. YYYY-MM-DD'
      - Date ranges → 'YYYY-MM-DD/YYYY-MM-DD' (ISO 8601 interval)
      - Unrecognized strings are returned stripped but unchanged.
    """
    text = raw.strip()
    if not text:
        return ""

    # Detect and strip circa prefix
    circa = False
    circa_match = CIRCA_PATTERN.match(text)
    if circa_match:
        circa = True
        text = text[circa_match.end():].strip()

    # Check for year ranges first (e.g., "1920-1925")
    yr_match = YEAR_RANGE_PATTERN.match(text)
    if yr_match:
        start, end = yr_match.group(1).strip(), yr_match.group(2).strip()
        result = f"{start}/{end}"
        return f"ca. {result}" if circa else result

    # Check for general date ranges
    range_match = RANGE_PATTERN.match(text)
    if range_match:
        start_raw, end_raw = range_match.group(1).strip(), range_match.group(2).strip()
        start_parsed = parse_single_date(start_raw)
        end_parsed = parse_single_date(end_raw)
        if start_parsed and end_parsed:
            result = f"{start_parsed}/{end_parsed}"
            return f"ca. {result}" if circa else result

    # Single date
    parsed = parse_single_date(text)
    if parsed:
        return f"ca. {parsed}" if circa else parsed

    # Fallback: return the original (stripped) value so data is not lost
    return raw.strip()


# ---------------------------------------------------------------------------
# Title Standardization
# ---------------------------------------------------------------------------

# Short words that should not be capitalized in titles (English)
TITLE_LOWERCASE_WORDS = {
    "a", "an", "the", "and", "but", "or", "nor", "for", "yet", "so",
    "at", "by", "in", "of", "on", "to", "up", "as", "is", "it",
    "if", "no", "not", "with", "from", "into", "over", "upon",
}


def smart_title_case(text: str) -> str:
    """Convert text to title case following English conventions.

    - First and last words are always capitalized.
    - Short prepositions, articles, and conjunctions are lowercase
      unless they are the first or last word.
    - Words that are fully uppercase and longer than 1 character
      (likely acronyms) are left unchanged.
    """
    words = text.split()
    result = []
    for i, word in enumerate(words):
        # Preserve likely acronyms (e.g., "UNESCO", "IV")
        if word.isupper() and len(word) > 1:
            result.append(word)
        elif i == 0 or i == len(words) - 1:
            result.append(word.capitalize())
        elif word.lower() in TITLE_LOWERCASE_WORDS:
            result.append(word.lower())
        else:
            result.append(word.capitalize())
    return " ".join(result)


def standardize_title(raw: str) -> str:
    """Standardize a title field.

    - Strip leading/trailing whitespace.
    - Collapse internal runs of whitespace to a single space.
    - Apply smart title-case rules.
    """
    text = raw.strip()
    if not text:
        return ""
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return smart_title_case(text)


# ---------------------------------------------------------------------------
# Object Number Standardization
# ---------------------------------------------------------------------------

def standardize_object_number(raw: str) -> str:
    """Standardize a museum object/accession number.

    Rules applied:
      - Strip whitespace.
      - Convert to uppercase.
      - Replace common separators (spaces, underscores, slashes) with dots.
      - Collapse multiple dots into one.
      - Remove trailing dots.
    """
    text = raw.strip()
    if not text:
        return ""

    text = text.upper()
    # Standardize separators to dots
    text = re.sub(r"[\s_/\\]+", ".", text)
    # Collapse multiple dots
    text = re.sub(r"\.{2,}", ".", text)
    # Remove leading/trailing dots
    text = text.strip(".")
    return text


# ---------------------------------------------------------------------------
# Link Standardization
# ---------------------------------------------------------------------------

def standardize_link(raw: str) -> str:
    """Standardize a URL/link field.

    - Strip whitespace.
    - Ensure the URL has a scheme (default to https://).
    - Lowercase the scheme and hostname.
    - Remove trailing slashes from the path (unless the path is just '/').
    - Remove common tracking parameters (utm_*).
    """
    text = raw.strip()
    if not text:
        return ""

    # Add scheme if missing
    if not re.match(r"^https?://", text, re.IGNORECASE):
        text = "https://" + text

    parsed = urlparse(text)

    # Lowercase scheme and netloc
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # Clean path: remove trailing slash unless path is exactly "/"
    path = parsed.path
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    # Remove utm_ tracking query parameters
    if parsed.query:
        params = parsed.query.split("&")
        cleaned_params = [
            p for p in params if not p.lower().startswith("utm_")
        ]
        query = "&".join(cleaned_params)
    else:
        query = ""

    return urlunparse((scheme, netloc, path, parsed.params, query, parsed.fragment))


# ---------------------------------------------------------------------------
# Row Processing
# ---------------------------------------------------------------------------

STANDARDIZERS = [
    standardize_date,
    standardize_title,
    standardize_object_number,
    standardize_link,
]

EXPECTED_HEADERS = ["date", "title", "object number", "link"]


def standardize_row(row: list[str]) -> list[str]:
    """Apply the appropriate standardizer to each field in a row."""
    return [
        STANDARDIZERS[i](field) if i < len(STANDARDIZERS) else field.strip()
        for i, field in enumerate(row)
    ]


def looks_like_header(row: list[str]) -> bool:
    """Heuristic check: does this row look like a header row?"""
    normalized = [cell.strip().lower() for cell in row]
    matches = sum(1 for cell in normalized if cell in EXPECTED_HEADERS)
    return matches >= 2  # at least half the columns match known headers


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def process_file(infile, outfile, has_header: bool = True) -> dict:
    """Read a TSV from *infile*, standardize it, and write to *outfile*.

    Returns a dict with processing statistics.
    """
    reader = csv.reader(infile, delimiter="\t")
    writer = csv.writer(outfile, delimiter="\t", lineterminator="\n")

    stats = {
        "total_rows": 0,
        "standardized_rows": 0,
        "skipped_empty": 0,
        "errors": 0,
    }

    for row_num, row in enumerate(reader, start=1):
        # Skip completely empty rows
        if not row or all(cell.strip() == "" for cell in row):
            stats["skipped_empty"] += 1
            continue

        stats["total_rows"] += 1

        # Handle header row
        if row_num == 1 and has_header and looks_like_header(row):
            # Normalize header names
            header = [cell.strip().title() for cell in row]
            writer.writerow(header)
            continue

        # Validate column count
        if len(row) < 4:
            # Pad with empty strings so standardizers don't fail
            row.extend([""] * (4 - len(row)))
            print(
                f"Warning: Row {row_num} has fewer than 4 columns; "
                f"padded with empty values.",
                file=sys.stderr,
            )
        elif len(row) > 4:
            print(
                f"Warning: Row {row_num} has {len(row)} columns; "
                f"extra columns will be preserved but not standardized.",
                file=sys.stderr,
            )

        try:
            standardized = standardize_row(row)
            writer.writerow(standardized)
            stats["standardized_rows"] += 1
        except Exception as exc:
            print(
                f"Error processing row {row_num}: {exc}",
                file=sys.stderr,
            )
            writer.writerow(row)  # write original row on failure
            stats["errors"] += 1

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Standardize a museum inventory TSV file."
    )
    parser.add_argument(
        "input",
        help="Path to input .tsv file (use '-' for stdin).",
    )
    parser.add_argument(
        "-o", "--output",
        default="-",
        help="Path to output .tsv file (default: stdout).",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Indicate that the input file has no header row.",
    )
    args = parser.parse_args()

    # Open input
    if args.input == "-":
        infile = sys.stdin
    else:
        infile = open(args.input, "r", encoding="utf-8", newline="")

    # Open output
    if args.output == "-":
        outfile = sys.stdout
    else:
        outfile = open(args.output, "w", encoding="utf-8", newline="")

    try:
        stats = process_file(infile, outfile, has_header=not args.no_header)
    finally:
        if infile is not sys.stdin:
            infile.close()
        if outfile is not sys.stdout:
            outfile.close()

    # Print summary to stderr
    print(
        f"\nDone. "
        f"Rows processed: {stats['total_rows']}, "
        f"Standardized: {stats['standardized_rows']}, "
        f"Empty/skipped: {stats['skipped_empty']}, "
        f"Errors: {stats['errors']}.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
```

## How It Works

### Column-by-Column Standardization

| Column | Transformations |
|---|---|
| **Date** | Parses dozens of common date formats → ISO 8601 (`YYYY-MM-DD`). Handles partial dates (`YYYY`, `YYYY-MM`), date ranges (`→ YYYY/YYYY`), and `circa` / `ca.` prefixes. Unrecognizable dates are passed through unchanged. |
| **Title** | Trims whitespace, collapses internal whitespace, applies smart title-case (preserves acronyms, lowercases articles/prepositions except at start/end). |
| **Object Number** | Uppercases, normalizes separators (spaces, underscores, slashes → dots), collapses repeated dots. |
| **Link** | Ensures `https://` scheme, lowercases scheme + host, strips trailing slashes, removes `utm_*` tracking parameters. |

### Example

**Input (`inventory.tsv`):**
```
date	title	object number	link
Jan 15, 2023	the STARRY night painting	2023/15/001	HTTP://Example.com/art/001/?utm_source=google
circa 1920	 portrait of a   lady 	inv_2020__45	example.com/art/002/
1880 - 1885	VASE	ACC 2019 100	https://EXAMPLE.COM/art/003
```

**Command:**
```bash
python standardize_inventory.py inventory.tsv -o clean_inventory.tsv
```

**Output (`clean_inventory.tsv`):**
```
Date	Title	Object Number	Link
2023-01-15	The Starry Night Painting	2023.15.001	http://example.com/art/001
ca. 1920	Portrait of a Lady	INV.2020.45	https://example.com/art/002
1880/1885	VASE	ACC.2019.100	https://example.com/art/003
```
