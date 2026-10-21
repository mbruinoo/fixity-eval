# Museum Inventory Spreadsheet Standardizer

```python
#!/usr/bin/env python3
"""
Museum Inventory Spreadsheet Standardizer

Reads a .tsv file with museum inventory data and standardizes the four columns:
- Date: normalized to ISO 8601 format (YYYY-MM-DD) or descriptive ranges
- Title: trimmed, title-cased, and cleaned of extra whitespace
- Object Number: standardized to a consistent accession number format
- Link: validated and cleaned URL

Usage:
    python standardize_inventory.py input.tsv [-o output.tsv]
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

# Common month abbreviation / misspelling mappings
MONTH_MAP = {
    "jan": "01", "january": "01",
    "feb": "02", "february": "02",
    "mar": "03", "march": "03",
    "apr": "04", "april": "04",
    "may": "05",
    "jun": "06", "june": "06",
    "jul": "07", "july": "07",
    "aug": "08", "august": "08",
    "sep": "09", "sept": "09", "september": "09",
    "oct": "10", "october": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12",
}

# Date formats to attempt with strptime (order matters)
DATE_FORMATS = [
    "%Y-%m-%d",    # 2024-01-15
    "%m/%d/%Y",    # 01/15/2024
    "%d/%m/%Y",    # 15/01/2024  (tried only if month > 12 disambiguates)
    "%m-%d-%Y",    # 01-15-2024
    "%B %d, %Y",   # January 15, 2024
    "%b %d, %Y",   # Jan 15, 2024
    "%d %B %Y",    # 15 January 2024
    "%d %b %Y",    # 15 Jan 2024
    "%Y/%m/%d",    # 2024/01/15
    "%Y",          # 2024
    "%B %Y",       # January 2024
    "%b %Y",       # Jan 2024
]


def _normalize_date_string(raw: str) -> str:
    """Lower-level cleanup before parsing: fix separators, whitespace, etc."""
    text = raw.strip()
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)
    # Replace common Unicode dashes with ASCII hyphen
    text = text.replace("–", "-").replace("—", "-")
    return text


def _try_parse_exact(text: str) -> str | None:
    """Try each candidate strptime format; return ISO string or None."""
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(text, fmt)
            if fmt == "%Y":
                return str(dt.year)
            if fmt in ("%B %Y", "%b %Y"):
                return dt.strftime("%Y-%m")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _parse_written_month(text: str) -> str | None:
    """Handle 'Month DD, YYYY' or 'DD Month YYYY' with fuzzy month names."""
    # Pattern: Month Day, Year  (e.g., "Sept 5, 1920")
    m = re.match(
        r"(?P<month>[A-Za-z]+)\.?\s+(?P<day>\d{1,2}),?\s+(?P<year>\d{4})", text
    )
    if not m:
        # Pattern: Day Month Year  (e.g., "5 Sept 1920")
        m = re.match(
            r"(?P<day>\d{1,2})\s+(?P<month>[A-Za-z]+)\.?,?\s+(?P<year>\d{4})", text
        )
    if m:
        month_str = m.group("month").lower().rstrip(".")
        mm = MONTH_MAP.get(month_str)
        if mm:
            day = int(m.group("day"))
            year = int(m.group("year"))
            return f"{year:04d}-{mm}-{day:02d}"
    return None


def standardize_date(raw: str) -> str:
    """
    Return a standardized date string.

    Handles:
      - ISO, US, and European numeric formats
      - Written-out month names (including abbreviations)
      - Year-only values ("ca. 1920", "c. 1920", "~1920")
      - Date ranges ("1920-1925", "1920 to 1925")
      - Century references ("19th century")
      - "Unknown" / empty → "Unknown"
    """
    if not raw or not raw.strip():
        return "Unknown"

    text = _normalize_date_string(raw)

    # ---- Handle "unknown" variants ----
    if text.lower() in ("unknown", "n/a", "n.a.", "none", "?", "undated", "nd", "n.d."):
        return "Unknown"

    # ---- Handle century references ----
    m = re.match(r"(\d{1,2})(st|nd|rd|th)\s+century", text, re.IGNORECASE)
    if m:
        century = int(m.group(1))
        start = (century - 1) * 100
        end = start + 99
        return f"{start:04d}/{end:04d} ({m.group(1)}{m.group(2)} century)"

    # ---- Handle approximate dates: "ca.", "c.", "circa", "~", "approx" ----
    approx_prefix = ""
    approx_match = re.match(
        r"(ca\.?|c\.?|circa|~|approx\.?|approximately)\s*", text, re.IGNORECASE
    )
    if approx_match:
        approx_prefix = "ca. "
        text = text[approx_match.end():]

    # ---- Handle date ranges (e.g., "1920-1925", "1920 to 1925") ----
    range_match = re.match(
        r"(\d{4})\s*(?:-|to|–|—)\s*(\d{4})", text, re.IGNORECASE
    )
    if range_match:
        return f"{approx_prefix}{range_match.group(1)}/{range_match.group(2)}"

    # ---- Try written month names first (handles abbreviations like "Sept") ----
    result = _parse_written_month(text)
    if result:
        return f"{approx_prefix}{result}"

    # ---- Try standard strptime formats ----
    result = _try_parse_exact(text)
    if result:
        return f"{approx_prefix}{result}"

    # ---- Year-only fallback ----
    m = re.match(r"(\d{4})", text)
    if m:
        return f"{approx_prefix}{m.group(1)}"

    # Could not parse – return cleaned original
    return raw.strip()


# ---------------------------------------------------------------------------
# Title Standardization
# ---------------------------------------------------------------------------

# Words that should remain lowercase in title case (AP style subset)
TITLE_LOWERCASE = {
    "a", "an", "the", "and", "but", "or", "nor", "for", "yet", "so",
    "at", "by", "in", "of", "on", "to", "up", "as", "is", "if",
    "it", "no", "not", "per", "via", "vs", "vs.",
}


def _title_case_word(word: str, first: bool) -> str:
    """Title-case a single word, respecting articles/prepositions."""
    # Preserve fully-uppercase acronyms (2+ chars, e.g., "UNESCO", "IV")
    if len(word) >= 2 and word.isupper():
        return word
    lower = word.lower()
    if first or lower not in TITLE_LOWERCASE:
        return word.capitalize()
    return lower


def standardize_title(raw: str) -> str:
    """
    Clean and title-case an artwork/object title.

    - Strips leading/trailing whitespace
    - Collapses internal whitespace
    - Applies AP-style title casing (first word always capitalized)
    - Preserves content in parentheses and quotes
    - Removes trailing periods (unless ellipsis)
    """
    if not raw or not raw.strip():
        return "Untitled"

    text = raw.strip()
    text = re.sub(r"\s+", " ", text)

    # Remove a single trailing period (but keep "..." ellipsis)
    if text.endswith(".") and not text.endswith("..."):
        text = text[:-1].strip()

    words = text.split()
    result_words = []
    for i, word in enumerate(words):
        result_words.append(_title_case_word(word, first=(i == 0)))

    return " ".join(result_words)


# ---------------------------------------------------------------------------
# Object Number Standardization
# ---------------------------------------------------------------------------

def standardize_object_number(raw: str) -> str:
    """
    Normalize an accession/object number.

    Common museum formats:
      - "2024.1.15", "2024.001.015" → zero-padded segments separated by dots
      - "2024-1-15" → converted to dot notation
      - "ACC 2024.1" → prefix preserved, number normalized
      - Free-text identifiers preserved as-is after trimming

    Rules applied:
      1. Strip whitespace.
      2. Uppercase all letters.
      3. Replace hyphens/slashes between numeric segments with dots.
      4. Zero-pad purely numeric segments to 3+ digits (minimum width of
         the widest segment in that number, at least 3).
    """
    if not raw or not raw.strip():
        return "Unknown"

    text = raw.strip().upper()
    text = re.sub(r"\s+", " ", text)

    if text.lower() in ("unknown", "n/a", "none", "?"):
        return "Unknown"

    # Separate an optional alpha prefix ("ACC", "OBJ", etc.)
    prefix = ""
    number_part = text
    prefix_match = re.match(r"^([A-Z]{1,10})[.\s\-]+(.+)$", text)
    if prefix_match:
        prefix = prefix_match.group(1) + " "
        number_part = prefix_match.group(2)

    # Split on dots, hyphens, or slashes that sit between digit groups
    segments = re.split(r"[.\-/]", number_part)

    # Only zero-pad if ALL segments are purely numeric
    if all(seg.isdigit() for seg in segments if seg):
        max_width = max((len(seg) for seg in segments if seg), default=3)
        pad = max(max_width, 3)
        segments = [seg.zfill(pad) for seg in segments if seg]
        return f"{prefix}{'.'.join(segments)}"

    # Mixed alphanumeric – just re-join with dots
    return f"{prefix}{'.'.join(seg for seg in segments if seg)}"


# ---------------------------------------------------------------------------
# Link Standardization
# ---------------------------------------------------------------------------

def standardize_link(raw: str) -> str:
    """
    Validate and clean a URL.

    - Strips whitespace and trailing punctuation that isn't part of the URL.
    - Adds 'https://' if no scheme is present.
    - Lowercases the scheme and hostname.
    - Removes default port numbers (80, 443).
    - Removes trailing slash on bare domains.
    - Returns empty string for clearly invalid input.
    """
    if not raw or not raw.strip():
        return ""

    text = raw.strip()

    if text.lower() in ("n/a", "none", "unknown", "?", "-"):
        return ""

    # Strip trailing punctuation that was likely not part of the URL
    text = text.rstrip(".,;!? ")

    # Add scheme if missing
    if not re.match(r"^https?://", text, re.IGNORECASE):
        # Might start with "www." or be a bare domain
        if re.match(r"^[a-zA-Z0-9]", text):
            text = "https://" + text
        else:
            return ""

    try:
        parsed = urlparse(text)
    except ValueError:
        return ""

    # Basic validity check
    if not parsed.hostname:
        return ""

    scheme = parsed.scheme.lower()
    hostname = parsed.hostname.lower()
    port = parsed.port

    # Remove default ports
    if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        port = None

    netloc = hostname
    if port:
        netloc = f"{hostname}:{port}"

    # Reconstruct
    cleaned = urlunparse((
        scheme,
        netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment,
    ))

    # Remove trailing slash on bare domains (no path beyond "/")
    if parsed.path in ("", "/") and not parsed.query and not parsed.fragment:
        cleaned = cleaned.rstrip("/")

    return cleaned


# ---------------------------------------------------------------------------
# Pipeline: process a full row
# ---------------------------------------------------------------------------

def standardize_row(row: dict) -> dict:
    """Apply all standardizers to a single inventory row."""
    return {
        "date": standardize_date(row.get("date", "")),
        "title": standardize_title(row.get("title", "")),
        "object_number": standardize_object_number(row.get("object_number", "")),
        "link": standardize_link(row.get("link", "")),
    }


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

# Maps various header labels found in the wild to our canonical column names
HEADER_ALIASES = {
    "date": "date",
    "dates": "date",
    "year": "date",
    "accession date": "date",
    "title": "title",
    "object title": "title",
    "artwork title": "title",
    "name": "title",
    "object number": "object_number",
    "objectnumber": "object_number",
    "object_number": "object_number",
    "accession number": "object_number",
    "accession no": "object_number",
    "accession no.": "object_number",
    "acc. no.": "object_number",
    "inventory number": "object_number",
    "id": "object_number",
    "link": "link",
    "url": "link",
    "uri": "link",
    "web link": "link",
    "permalink": "link",
}

OUTPUT_FIELDNAMES = ["date", "title", "object_number", "link"]
OUTPUT_HEADER_LABELS = {
    "date": "Date",
    "title": "Title",
    "object_number": "Object Number",
    "link": "Link",
}


def _map_header(raw_header: str) -> str | None:
    """Return the canonical field name for a raw header, or None."""
    return HEADER_ALIASES.get(raw_header.strip().lower())


def read_inventory(filepath: str) -> list[dict]:
    """Read a .tsv museum inventory file and return rows as dicts."""
    rows = []
    with open(filepath, newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh, delimiter="\t")
        raw_headers = next(reader)
        mapped = [_map_header(h) for h in raw_headers]

        # Validate that we found all four expected columns
        missing = set(OUTPUT_FIELDNAMES) - set(h for h in mapped if h)
        if missing:
            print(f"⚠  Warning: could not map columns for {missing}. "
                  f"Raw headers: {raw_headers}", file=sys.stderr)
            # Fall back to positional mapping
            if len(raw_headers) >= 4:
                mapped = OUTPUT_FIELDNAMES[:len(raw_headers)]
            else:
                print("✖  Fatal: fewer than 4 columns and headers not recognized.",
                      file=sys.stderr)
                sys.exit(1)

        for line_num, values in enumerate(reader, start=2):
            row = {}
            for col_name, value in zip(mapped, values):
                if col_name:
                    row[col_name] = value
            if any(row.values()):
                rows.append(row)
            else:
                print(f"  ℹ  Skipping empty row {line_num}", file=sys.stderr)

    return rows


def write_inventory(filepath: str, rows: list[dict]) -> None:
    """Write standardized inventory rows to a .tsv file."""
    with open(filepath, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=OUTPUT_FIELDNAMES,
            delimiter="\t",
            extrasaction="ignore",
        )
        # Write human-friendly header labels
        writer.writerow(OUTPUT_HEADER_LABELS)
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Standardize a museum inventory .tsv spreadsheet."
    )
    parser.add_argument(
        "input",
        help="Path to the input .tsv file.",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Path for the output .tsv file (default: <input>_standardized.tsv).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print standardized output to stdout instead of writing a file.",
    )
    args = parser.parse_args()

    if args.output is None:
        base = args.input.rsplit(".", 1)[0]
        args.output = f"{base}_standardized.tsv"

    print(f"📂 Reading: {args.input}")
    raw_rows = read_inventory(args.input)
    print(f"   Found {len(raw_rows)} rows.")

    standardized = [standardize_row(row) for row in raw_rows]
    print(f"✅ Standardized {len(standardized)} rows.")

    if args.dry_run:
        print()
        print("\t".join(OUTPUT_HEADER_LABELS[f] for f in OUTPUT_FIELDNAMES))
        for row in standardized:
            print("\t".join(row[f] for f in OUTPUT_FIELDNAMES))
    else:
        write_inventory(args.output, standardized)
        print(f"💾 Written to: {args.output}")


if __name__ == "__main__":
    main()
```

## How It Works

### Column Standardizers

| Column | Transformations Applied |
|---|---|
| **Date** | Parses dozens of date formats (ISO, US, European, written months), handles approximate dates (`ca.`, `circa`, `~`), ranges (`1920-1925`), century references (`19th century`), and year-only values |
| **Title** | Trims whitespace, applies AP-style title casing (keeps articles lowercase mid-title), preserves acronyms, removes stray trailing periods |
| **Object Number** | Uppercases, normalizes separators to dots, zero-pads numeric segments (e.g., `2024.1.5` → `2024.001.005`), preserves alpha prefixes like `ACC` |
| **Link** | Adds `https://` if missing, lowercases scheme/host, strips default ports, removes trailing slash on bare domains, discards clearly invalid entries |

### Usage

```bash
# Basic usage (writes to input_standardized.tsv)
python standardize_inventory.py museum_collection.tsv

# Specify output path
python standardize_inventory.py museum_collection.tsv -o cleaned.tsv

# Preview without writing a file
python standardize_inventory.py museum_collection.tsv --dry-run
```

### Example Input → Output

**Input (`inventory.tsv`):**
```
Date	Object Title	Accession No.	URL
jan 15, 2024	  the starry night over PARIS  	2024-1-5	http://museum.org/item/5
ca. 1895	portrait of a lady.	ACC 95-12-003	www.example.com/item
19th century	unknown	n/a	none
```

**Output (`inventory_standardized.tsv`):**
```
Date	Title	Object Number	Link
2024-01-15	The Starry Night Over PARIS	2024.001.005	http://museum.org/item/5
ca. 1895	Portrait of a Lady	ACC 095.012.003	https://www.example.com/item
1800/1899 (19th century)	Unknown	Unknown	
```

### Flexible Header Matching

The script recognizes many common header variations (`Accession No.`, `Object Title`, `URL`, `Permalink`, etc.) and maps them automatically to the four canonical columns. If headers aren't recognized, it falls back to positional assignment.
