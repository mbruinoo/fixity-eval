# Museum Inventory Standardization Script

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory records from a TSV file.

Validates, cleans, and standardizes records containing:
- Date
- Title
- Object Number
- Link
"""

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse


class InventoryStandardizer:
    """Standardizes museum inventory records."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []

    def standardize_date(self, date_str: str) -> Tuple[str, List[str]]:
        """
        Standardize date to ISO 8601 format (YYYY-MM-DD).
        Returns tuple of (standardized_date, issues_list).
        """
        issues = []

        if not date_str or not date_str.strip():
            return "", ["Missing date"]

        date_str = date_str.strip()

        # Try common date formats
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%B %Y",
            "%b %Y",
            "%Y",
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d"), issues
            except ValueError:
                continue

        # If no format matched, try to extract year
        year_match = re.search(r"\b(1[0-9]{3}|2[0-9]{3})\b", date_str)
        if year_match:
            issues.append(f"Ambiguous date format; extracted year {year_match.group(1)}")
            return f"{year_match.group(1)}-01-01", issues

        issues.append(f"Could not parse date: '{date_str}'")
        return date_str, issues

    def standardize_title(self, title: str) -> Tuple[str, List[str]]:
        """
        Standardize title formatting.
        Returns tuple of (standardized_title, issues_list).
        """
        issues = []

        if not title or not title.strip():
            issues.append("Missing title")
            return "", issues

        # Strip whitespace
        title = title.strip()

        # Normalize whitespace (remove multiple spaces)
        title = re.sub(r"\s+", " ", title)

        # Check for all caps (convert to title case if entire title is caps)
        if title.isupper() and len(title) > 1:
            issues.append("Title in all caps; converting to title case")
            title = title.title()

        # Check length
        if len(title) < 3:
            issues.append("Title very short (less than 3 characters)")
        elif len(title) > 500:
            issues.append("Title very long (over 500 characters)")

        return title, issues

    def standardize_object_number(self, obj_num: str) -> Tuple[str, List[str]]:
        """
        Standardize object number format.
        Returns tuple of (standardized_number, issues_list).
        """
        issues = []

        if not obj_num or not obj_num.strip():
            issues.append("Missing object number")
            return "", issues

        obj_num = obj_num.strip().upper()

        # Remove extra spaces
        obj_num = re.sub(r"\s+", " ", obj_num)

        # Check if it contains only alphanumeric, hyphens, and dots
        if not re.match(r"^[A-Z0-9\.\-\s]+$", obj_num):
            issues.append(
                f"Object number contains unusual characters: '{obj_num}'"
            )

        # Check for duplicates or near-duplicates would require context
        return obj_num, issues

    def validate_url(self, url: str) -> Tuple[str, List[str]]:
        """
        Validate and standardize URL format.
        Returns tuple of (standardized_url, issues_list).
        """
        issues = []

        if not url or not url.strip():
            issues.append("Missing link")
            return "", issues

        url = url.strip()

        # Add scheme if missing
        if not url.startswith(("http://", "https://")):
            issues.append("URL missing scheme; adding https://")
            url = "https://" + url

        # Validate URL structure
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                issues.append(f"Invalid URL structure: '{url}'")
                return url, issues
        except Exception as e:
            issues.append(f"URL parsing error: {str(e)}")

        return url, issues

    def process_record(
        self, record: Dict[str, str], row_num: int
    ) -> Tuple[Dict[str, str], List[Dict]]:
        """
        Process and standardize a single record.
        Returns tuple of (standardized_record, issues_list).
        """
        issues = []

        standardized = {}

        # Process each field
        date_val, date_issues = self.standardize_date(record.get("date", ""))
        standardized["date"] = date_val
        for issue in date_issues:
            issues.append({"row": row_num, "field": "date", "issue": issue})

        title_val, title_issues = self.standardize_title(record.get("title", ""))
        standardized["title"] = title_val
        for issue in title_issues:
            issues.append({"row": row_num, "field": "title", "issue": issue})

        obj_num_val, obj_num_issues = self.standardize_object_number(
            record.get("object_number", "")
        )
        standardized["object_number"] = obj_num_val
        for issue in obj_num_issues:
            issues.append({"row": row_num, "field": "object_number", "issue": issue})

        link_val, link_issues = self.validate_url(record.get("link", ""))
        standardized["link"] = link_val
        for issue in link_issues:
            issues.append({"row": row_num, "field": "link", "issue": issue})

        return standardized, issues

    def read_inventory(self, filepath: Path) -> List[Dict[str, str]]:
        """Read TSV inventory file."""
        records = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t")

                if not reader.fieldnames:
                    raise ValueError("Empty file or missing headers")

                required_fields = {"date", "title", "object_number", "link"}
                missing_fields = required_fields - set(
                    field.lower() for field in reader.fieldnames
                )
                if missing_fields:
                    raise ValueError(
                        f"Missing required columns: {', '.join(missing_fields)}"
                    )

                for row_num, row in enumerate(reader, start=2):  # start=2 (header is 1)
                    # Normalize field names to lowercase
                    normalized_row = {k.lower(): v for k, v in row.items()}
                    records.append((row_num, normalized_row))

        except FileNotFoundError:
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {str(e)}", file=sys.stderr)
            sys.exit(1)

        return records

    def standardize_inventory(self, filepath: Path) -> List[Tuple[Dict, List[Dict]]]:
        """
        Standardize all records in inventory file.
        Returns list of (record, issues) tuples.
        """
        records = self.read_inventory(filepath)
        results = []

        for row_num, record in records:
            standardized, issues = self.process_record(record, row_num)
            results.append((standardized, issues))

            if issues:
                self.warnings.extend(issues)

        return results

    def write_inventory(
        self, results: List[Tuple[Dict, List[Dict]]], output_path: Path
    ) -> None:
        """Write standardized inventory to TSV file."""
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["date", "title", "object_number", "link"]
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")

                writer.writeheader()
                for record, _ in results:
                    writer.writerow(record)

            print(f"✓ Standardized inventory written to: {output_path}")
        except Exception as e:
            print(f"Error writing output file: {str(e)}", file=sys.stderr)
            sys.exit(1)

    def generate_report(
        self, results: List[Tuple[Dict, List[Dict]]], output_path: Path
    ) -> None:
        """Generate a detailed report of issues found."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                # Summary
                total_records = len(results)
                records_with_issues = sum(1 for _, issues in results if issues)

                f.write("MUSEUM INVENTORY STANDARDIZATION REPORT\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Total records processed: {total_records}\n")
                f.write(f"Records with issues: {records_with_issues}\n")
                f.write(f"Issues found: {len(self.warnings)}\n\n")

                # Detailed issues
                if self.warnings:
                    f.write("ISSUES BY TYPE:\n")
                    f.write("-" * 60 + "\n")

                    by_field = {}
                    for issue in self.warnings:
                        field = issue["field"]
                        if field not in by_field:
                            by_field[field] = []
                        by_field[field].append(issue)

                    for field in sorted(by_field.keys()):
                        f.write(f"\n{field.upper()}:\n")
                        for issue in by_field[field]:
                            f.write(f"  Row {issue['row']}: {issue['issue']}\n")
                else:
                    f.write("No issues found!\n")

            print(f"✓ Report written to: {output_path}")

        except Exception as e:
            print(f"Error writing report: {str(e)}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory records from a TSV file"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input TSV file with inventory records",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output TSV file (default: input_standardized.tsv)",
    )
    parser.add_argument(
        "-r",
        "--report",
        type=Path,
        default=None,
        help="Output report file (default: standardization_report.txt)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print verbose output",
    )

    args = parser.parse_args()

    # Set default output paths
    if args.output is None:
        args.output = args.input.parent / f"{args.input.stem}_standardized.tsv"
    if args.report is None:
        args.report = args.input.parent / "standardization_report.txt"

    print(f"Reading inventory from: {args.input}")

    standardizer = InventoryStandardizer(verbose=args.verbose)
    results = standardizer.standardize_inventory(args.input)

    standardizer.write_inventory(results, args.output)
    standardizer.generate_report(results, args.report)

    print(f"\n✓ Standardization complete!")
    print(f"  Records processed: {len(results)}")
    print(f"  Issues found: {len(standardizer.warnings)}")


if __name__ == "__main__":
    main()
```

## Usage

```bash
# Basic usage
python standardize_inventory.py input.tsv

# Specify custom output files
python standardize_inventory.py input.tsv -o clean_inventory.tsv -r report.txt

# Verbose output
python standardize_inventory.py input.tsv -v
```

## Example Input TSV

```tsv
date	title	object_number	link
1987-05-15	THE BLUE VASE	ACC-1987-045	www.museum.org/objects/1
5/20/1992	Napoleon's Pocket Watch	ACC.1992.089	https://museum.org/objects/2
June 1950	Handwritten Letter	1950-LC-002	http://museum.org/obj/3
```

## Features

- **Date standardization**: Converts multiple date formats to ISO 8601 (YYYY-MM-DD)
- **Title cleaning**: Normalizes whitespace, converts all-caps titles
- **Object number validation**: Standardizes format and checks for unusual characters
- **URL validation**: Ensures valid URL format and adds https:// scheme if missing
- **Detailed reporting**: Generates a report of all issues found by field
- **Data preservation**: Original values preserved if standardization fails
- **Error handling**: Graceful handling of malformed files and invalid data
