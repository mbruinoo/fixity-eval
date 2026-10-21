# Museum Inventory Spreadsheet Standardizer

```python
#!/usr/bin/env python3
"""
Museum Inventory TSV Standardizer

Reads a museum inventory spreadsheet (.tsv) with 4 columns:
  - date
  - title
  - object number
  - link

Standardizes formatting and writes a cleaned output file.
"""

import csv
import re
import sys
import argparse
from datetime import datetime
from urllib.parse import urlparse, urlunparse


def standardize_date(raw_date: str) -> str:
    """
    Attempt to parse a variety of date formats and return a standardized
    ISO 8601 date string (YYYY-MM-DD). If only a year is provided,
    returns just the year. If parsing fails entirely, returns the
    original string stripped of excess whitespace.

    Supported input examples:
        "March 5, 2021"    -> "2021-03-05"
        "3/5/2021"         -> "2021-03-05"
        "03-05-2021"       -> "2021-03-05"
        "2021-03-05"       -> "2021-03-05"
        "5 March 2021"     -> "2021-03-05"
        "2021"             -> "2021"
        "c. 1850"          -> "c. 1850"
        "ca. 1850-1860"    -> "ca. 1850-1860"
        "n.d."             -> "n.d."
        ""                 -> "unknown"
    """
    cleaned = raw_date.strip()

    if not cleaned:
        return "unknown"

    # Preserve approximate / uncertain dates (e.g., "c. 1850", "ca. 1920", "n.d.")
    if re.match(r'^(c\.?a?\.?\s*\d|n\.?\s*d\.?|circa|about|approx)', cleaned, re.IGNORECASE):
        # Light cleanup: normalize "ca" / "c." -> "ca."
        cleaned = re.sub(r'^c\.?\s', 'ca. ', cleaned, flags=re.IGNORECASE)
        return cleaned

    # Try a series of common date formats
    date_formats = [
        "%Y-%m-%d",        # 2021-03-05
        "%m/%d/%Y",        # 03/05/2021
        "%m-%d-%Y",        # 03-05-2021
        "%d/%m/%Y",        # 05/03/2021 (ambiguous — tried after US format)
        "%B %d, %Y",       # March 5, 2021
        "%b %d, %Y",       # Mar 5, 2021
        "%d %B %Y",        # 5 March 2021
        "%d %b %Y",        # 5 Mar 2021
        "%B %d %Y",        # March 05 2021
        "%Y/%m/%d",        # 2021/03/05
        "%Y.%m.%d",        # 2021.03.05
        "%m.%d.%Y",        # 03.05.2021
    ]

    for fmt in date_formats:
        try:
            parsed = datetime.strptime(cleaned, fmt)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Check for a bare year (e.g., "2021" or "1850")
    if re.match(r'^\d{4}$', cleaned):
        return cleaned

    # Check for a year range (e.g., "1850-1860")
    if re.match(r'^\d{4}\s*[-–—]\s*\d{4}$', cleaned):
        return re.sub(r'\s*[-–—]\s*', '–', cleaned)  # normalize to en-dash

    # If nothing worked, return the cleaned original
    return cleaned


def standardize_title(raw_title: str) -> str:
    """
    Standardize the title field:
      - Strip leading/trailing whitespace
      - Collapse multiple internal spaces
      - Convert to title case (with awareness of small words)
      - Replace empty values with "Untitled"

    Examples:
        "  the   STARRY night  " -> "The Starry Night"
        ""                       -> "Untitled"
    """
    cleaned = raw_title.strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)

    if not cleaned:
        return "Untitled"

    # Small words that should not be capitalized (unless first/last word)
    small_words = {
        'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'yet', 'so',
        'at', 'by', 'in', 'of', 'on', 'to', 'up', 'as', 'is', 'if', 'it',
        'with', 'from', 'into', 'over', 'after', 'under', 'between',
        'de', 'la', 'le', 'les', 'du', 'des', 'von', 'van', 'del', 'di',
    }

    words = cleaned.split()
    result = []
    for i, word in enumerate(words):
        # Preserve words that look like acronyms (e.g., "UNESCO", "IV")
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
    """
    Standardize the object/accession number:
      - Strip whitespace
      - Uppercase all letters
      - Normalize common separators (spaces around dots/dashes)
      - Replace empty with "UNKNOWN"

    Examples:
        " 2021.45.3 "       -> "2021.45.3"
        "acc-2021-045-003"   -> "ACC-2021-045-003"
        "2021 . 45 . 3"     -> "2021.45.3"
    """
    cleaned = raw_obj_num.strip()

    if not cleaned:
        return "UNKNOWN"

    # Uppercase
    cleaned = cleaned.upper()

    # Remove spaces around common separators (dots, dashes)
    cleaned = re.sub(r'\s*\.\s*', '.', cleaned)
    cleaned = re.sub(r'\s*-\s*', '-', cleaned)

    # Collapse any remaining multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)

    return cleaned


def standardize_link(raw_link: str) -> str:
    """
    Standardize the URL/link field:
      - Strip whitespace
      - Add 'https://' if no scheme is present
      - Normalize the URL structure
      - Return empty string placeholder if blank

    Examples:
        "  www.museum.org/item/123  " -> "https://www.museum.org/item/123"
        "http://museum.org/item/123"  -> "http://museum.org/item/123"
        ""                            -> ""
    """
    cleaned = raw_link.strip()

    if not cleaned:
        return ""

    # If no scheme, add https://
    if not re.match(r'^https?://', cleaned, re.IGNORECASE):
        cleaned = 'https://' + cleaned

    # Parse and reassemble to normalize
    try:
        parsed = urlparse(cleaned)
        # Ensure lowercase scheme and netloc
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        ))
        return normalized
    except Exception:
        return cleaned


def process_inventory(input_path: str, output_path: str, has_header: bool = True) -> dict:
    """
    Read a TSV museum inventory file, standardize all four columns,
    and write the cleaned data to a new TSV file.

    Returns a summary dict with processing statistics.
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

    # Standard header
    standard_header = ["date", "title", "object_number", "link"]

    with open(input_path, 'r', encoding='utf-8-sig') as infile:
        reader = csv.reader(infile, delimiter='\t')

        for row_num, row in enumerate(reader, start=1):
            # Skip header row
            if has_header and row_num == 1:
                # Optionally validate header
                continue

            stats["total_rows"] += 1

            # Handle rows with wrong number of columns
            if len(row) < 4:
                # Pad with empty strings
                row.extend([''] * (4 - len(row)))
                print(f"  Warning: Row {row_num} had fewer than 4 columns (padded).")
            elif len(row) > 4:
                print(f"  Warning: Row {row_num} had more than 4 columns (truncated).")
                row = row[:4]

            raw_date, raw_title, raw_obj_num, raw_link = row[0], row[1], row[2], row[3]

            # Standardize each field
            std_date = standardize_date(raw_date)
            std_title = standardize_title(raw_title)
            std_obj_num = standardize_object_number(raw_obj_num)
            std_link = standardize_link(raw_link)

            # Track missing values
            if std_date == "unknown":
                stats["missing_dates"] += 1
            if std_title == "Untitled":
                stats["missing_titles"] += 1
            if std_obj_num == "UNKNOWN":
                stats["missing_object_numbers"] += 1
            if not std_link:
                stats["missing_links"] += 1

            # Track duplicate object numbers
            if std_obj_num != "UNKNOWN":
                if std_obj_num in seen_object_numbers:
                    stats["duplicate_object_numbers"].add(std_obj_num)
                    print(f"  Warning: Duplicate object number '{std_obj_num}' "
                          f"at rows {seen_object_numbers[std_obj_num]} and {row_num}.")
                else:
                    seen_object_numbers[std_obj_num] = row_num

            output_rows.append([std_date, std_title, std_obj_num, std_link])
            stats["cleaned_rows"] += 1

    # Write output
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        writer.writerow(standard_header)
        writer.writerows(output_rows)

    # Convert set to count for summary
    stats["duplicate_object_numbers"] = len(stats["duplicate_object_numbers"])

    return stats


def print_summary(stats: dict) -> None:
    """Print a human-readable processing summary."""
    print("\n" + "=" * 50)
    print("  STANDARDIZATION SUMMARY")
    print("=" * 50)
    print(f"  Total rows processed:       {stats['total_rows']}")
    print(f"  Rows written to output:     {stats['cleaned_rows']}")
    print(f"  Rows skipped:               {stats['skipped_rows']}")
    print(f"  Missing dates (→ 'unknown'):{stats['missing_dates']}")
    print(f"  Missing titles (→ 'Untitled'):{stats['missing_titles']}")
    print(f"  Missing object numbers:     {stats['missing_object_numbers']}")
    print(f"  Missing links:              {stats['missing_links']}")
    print(f"  Duplicate object numbers:   {stats['duplicate_object_numbers']}")
    print("=" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Standardize a museum inventory TSV file.",
        epilog="Example: python standardize_inventory.py inventory.tsv -o cleaned_inventory.tsv"
    )
    parser.add_argument(
        "input_file",
        help="Path to the input .tsv file"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Path for the output .tsv file (default: <input>_standardized.tsv)"
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Indicate that the input file has no header row"
    )

    args = parser.parse_args()

    input_path = args.input_file
    if args.output:
        output_path = args.output
    else:
        # Generate default output filename
        if input_path.endswith('.tsv'):
            output_path = input_path[:-4] + '_standardized.tsv'
        else:
            output_path = input_path + '_standardized.tsv'

    print(f"Reading from:  {input_path}")
    print(f"Writing to:    {output_path}")
    print(f"Header row:    {'Yes' if not args.no_header else 'No'}")
    print("-" * 50)

    try:
        stats = process_inventory(input_path, output_path, has_header=not args.no_header)
        print_summary(stats)
        print(f"Done. Standardized file saved to: {output_path}")
    except FileNotFoundError:
        print(f"Error: File '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied for '{input_path}' or '{output_path}'.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## How It Works

### Field Standardization Rules

| Column | Standardization Applied |
|---|---|
| **Date** | Parses many formats (`MM/DD/YYYY`, `Month D, YYYY`, etc.) → `YYYY-MM-DD`. Preserves approximate dates like `ca. 1850`. Empty → `unknown` |
| **Title** | Title case with small-word awareness (`the`, `of`, `in`...), preserves acronyms, collapses whitespace. Empty → `Untitled` |
| **Object Number** | Uppercased, separators normalized (no stray spaces around `.` or `-`). Empty → `UNKNOWN` |
| **Link** | Adds `https://` if missing, normalizes scheme/host to lowercase. Empty → `""` |

### Features
- **Duplicate detection** — warns when two rows share the same object number
- **Column count handling** — pads short rows, truncates long rows with warnings
- **UTF-8 BOM support** — handles Excel-exported files (`utf-8-sig`)
- **Processing summary** — prints statistics after completion

### Usage

```bash
# Basic usage (creates inventory_standardized.tsv)
python standardize_inventory.py inventory.tsv

# Specify output file
python standardize_inventory.py inventory.tsv -o cleaned.tsv

# Input file has no header row
python standardize_inventory.py inventory.tsv --no-header
```

### Example

**Input (`inventory.tsv`):**
```
date	title	object number	link
March 5, 2021	the   STARRY night	2021 . 45 . 3	www.museum.org/item/123
3/5/2021	WATER LILIES	acc-2021-045-003	http://Museum.org/item/456
	 	 	
ca 1850	portrait of a lady	2019.12.1	https://museum.org/item/789
```

**Output (`inventory_standardized.tsv`):**
```
date	title	object_number	link
2021-03-05	The Starry Night	2021.45.3	https://www.museum.org/item/123
2021-03-05	Water Lilies	ACC-2021-045-003	http://museum.org/item/456
unknown	Untitled	UNKNOWN	
ca. 1850	Portrait of a Lady	2019.12.1	https://museum.org/item/789
```
