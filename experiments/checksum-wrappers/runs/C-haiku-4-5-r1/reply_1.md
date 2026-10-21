# Museum Inventory Standardization Script

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records from a TSV file.

Handles corrections, withdrawals, and standardization of dates, titles,
object numbers, and links.
"""

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse


class InventoryRecord:
    """Represents a single museum inventory record."""

    REQUIRED_FIELDS = {"date", "title", "object_number", "link"}

    def __init__(self, record_dict: Dict[str, str], row_number: int):
        """
        Initialize a record.

        Args:
            record_dict: Dictionary with keys matching REQUIRED_FIELDS
            row_number: Line number in source file (for error reporting)
        """
        self.row_number = row_number
        self.date = record_dict.get("date", "").strip()
        self.title = record_dict.get("title", "").strip()
        self.object_number = record_dict.get("object_number", "").strip()
        self.link = record_dict.get("link", "").strip()
        self.withdrawn = False
        self.errors = []

    def standardize_date(self) -> None:
        """
        Standardize date to ISO 8601 format (YYYY-MM-DD).

        Handles various common formats. Logs errors for unparseable dates.
        """
        if not self.date:
            self.errors.append("Missing date")
            return

        original = self.date

        # Try common date formats
        formats = [
            "%Y-%m-%d",  # Already ISO
            "%m/%d/%Y",  # US format
            "%d/%m/%Y",  # EU format
            "%Y/%m/%d",  # Alternative ISO
            "%B %d, %Y",  # January 15, 2020
            "%b %d, %Y",  # Jan 15, 2020
            "%d %B %Y",  # 15 January 2020
            "%d %b %Y",  # 15 Jan 2020
            "%Y",  # Year only
        ]

        for fmt in formats:
            try:
                parsed_date = datetime.strptime(original, fmt)
                self.date = parsed_date.strftime("%Y-%m-%d")
                return
            except ValueError:
                continue

        self.errors.append(f"Could not parse date: '{original}'")

    def standardize_title(self) -> None:
        """
        Standardize title formatting.

        - Remove leading/trailing whitespace
        - Normalize internal whitespace
        - Remove trailing punctuation inconsistencies
        """
        if not self.title:
            self.errors.append("Missing title")
            return

        # Normalize whitespace
        self.title = " ".join(self.title.split())

        # Strip common trailing punctuation, then add period consistently
        self.title = self.title.rstrip(".,;:")
        if self.title and not self.title.endswith("."):
            self.title += "."

    def standardize_object_number(self) -> None:
        """
        Standardize object number format.

        Expected format: YEAR.NUMBER or YEAR.NUMBER.SUBNUMBER
        Examples: 2020.15, 2020.15.1
        """
        if not self.object_number:
            self.errors.append("Missing object number")
            return

        original = self.object_number

        # Remove common separators and normalize
        normalized = original.replace("_", ".").replace("-", ".")
        normalized = re.sub(r"\.+", ".", normalized)  # Remove duplicate dots
        normalized = normalized.strip(".")

        # Validate format
        parts = normalized.split(".")
        if len(parts) < 2 or len(parts) > 3:
            self.errors.append(
                f"Object number '{original}' doesn't match expected format "
                "(YEAR.NUMBER or YEAR.NUMBER.SUBNUMBER)"
            )
            return

        # Validate year part
        try:
            year = int(parts[0])
            if year < 1800 or year > datetime.now().year + 1:
                self.errors.append(
                    f"Object number year '{year}' seems unrealistic"
                )
        except ValueError:
            self.errors.append(
                f"Object number year '{parts[0]}' is not numeric"
            )
            return

        # Validate numeric parts
        for i, part in enumerate(parts[1:], start=1):
            if not part.isdigit():
                self.errors.append(
                    f"Object number part {i+1} '{part}' is not numeric"
                )
                return

        self.object_number = normalized

    def standardize_link(self) -> None:
        """
        Standardize URL format.

        - Ensure protocol is present
        - Validate URL structure
        - Strip trailing slashes
        """
        if not self.link:
            self.errors.append("Missing link")
            return

        original = self.link

        # Add protocol if missing
        if not original.startswith(("http://", "https://")):
            self.link = "https://" + original

        # Strip trailing slashes
        self.link = self.link.rstrip("/")

        # Basic URL validation
        try:
            result = urlparse(self.link)
            if not result.netloc:
                self.errors.append(f"Invalid URL: '{original}'")
                self.link = original
        except Exception as e:
            self.errors.append(f"Could not parse URL '{original}': {e}")

    def standardize(self) -> None:
        """Run all standardization steps."""
        self.standardize_date()
        self.standardize_title()
        self.standardize_object_number()
        self.standardize_link()

    def to_dict(self) -> Dict[str, str]:
        """Return record as dictionary."""
        return {
            "date": self.date,
            "title": self.title,
            "object_number": self.object_number,
            "link": self.link,
        }

    def is_valid(self) -> bool:
        """Check if record has no errors."""
        return len(self.errors) == 0


class InventoryStandardizer:
    """Manages standardization of inventory records."""

    def __init__(self, input_file: str, corrections_file: str = None):
        """
        Initialize standardizer.

        Args:
            input_file: Path to input TSV file
            corrections_file: Optional TSV file with corrections/withdrawals
        """
        self.input_file = Path(input_file)
        self.corrections_file = Path(corrections_file) if corrections_file else None
        self.records: List[InventoryRecord] = []
        self.corrections: Dict[str, Dict] = {}
        self.withdrawals: set = set()

    def load_corrections(self) -> None:
        """
        Load corrections and withdrawals from corrections file.

        Expected format:
        object_number    action    date    title    link
        2020.15          update    2020-06-15    New Title    https://...
        2020.16          withdraw
        """
        if not self.corrections_file or not self.corrections_file.exists():
            return

        with open(self.corrections_file, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                obj_num = row.get("object_number", "").strip()
                action = row.get("action", "").strip().lower()

                if action == "withdraw":
                    self.withdrawals.add(obj_num)
                elif action == "update":
                    self.corrections[obj_num] = {
                        k: v.strip()
                        for k, v in row.items()
                        if k != "object_number" and k != "action" and v.strip()
                    }

    def load_records(self) -> None:
        """Load inventory records from TSV file."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")

        with open(self.input_file, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")

            if not reader.fieldnames:
                raise ValueError("Input file is empty or not a valid TSV")

            # Validate required fields
            missing_fields = (
                InventoryRecord.REQUIRED_FIELDS
                - set(reader.fieldnames)
            )
            if missing_fields:
                raise ValueError(
                    f"Missing required fields: {missing_fields}"
                )

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                record = InventoryRecord(row, row_num)
                self.records.append(record)

    def apply_corrections(self) -> None:
        """Apply corrections and mark withdrawals."""
        for record in self.records:
            # Check for withdrawal
            if record.object_number in self.withdrawals:
                record.withdrawn = True
                continue

            # Apply updates
            if record.object_number in self.corrections:
                corrections = self.corrections[record.object_number]
                for field, value in corrections.items():
                    if hasattr(record, field):
                        setattr(record, field, value)

    def standardize_all(self) -> None:
        """Standardize all active records."""
        for record in self.records:
            if not record.withdrawn:
                record.standardize()

    def get_report(self) -> Tuple[int, int, int, List[str]]:
        """
        Generate processing report.

        Returns:
            Tuple of (total, valid, withdrawn, error_messages)
        """
        total = len(self.records)
        withdrawn = sum(1 for r in self.records if r.withdrawn)
        valid = sum(1 for r in self.records if not r.withdrawn and r.is_valid())
        invalid = total - withdrawn - valid

        error_messages = []
        for record in self.records:
            if not record.withdrawn and record.errors:
                error_msg = (
                    f"Row {record.row_number} "
                    f"({record.object_number}): "
                    f"{'; '.join(record.errors)}"
                )
                error_messages.append(error_msg)

        return total, valid, invalid, withdrawn, error_messages

    def save(self, output_file: str, include_withdrawn: bool = False) -> None:
        """
        Save standardized records to TSV file.

        Args:
            output_file: Path to output TSV file
            include_withdrawn: Whether to include withdrawn records (marked)
        """
        output_path = Path(output_file)
        fieldnames = ["date", "title", "object_number", "link"]
        if include_withdrawn:
            fieldnames.append("status")

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()

            for record in self.records:
                if record.withdrawn and not include_withdrawn:
                    continue

                row = record.to_dict()
                if include_withdrawn:
                    row["status"] = "withdrawn" if record.withdrawn else "active"

                writer.writerow(row)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory records from TSV file."
    )
    parser.add_argument(
        "input",
        help="Input TSV file with inventory records"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="inventory_standardized.tsv",
        help="Output TSV file (default: inventory_standardized.tsv)"
    )
    parser.add_argument(
        "-c",
        "--corrections",
        help="TSV file with corrections and withdrawals"
    )
    parser.add_argument(
        "--include-withdrawn",
        action="store_true",
        help="Include withdrawn records in output (marked with status)"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print detailed report"
    )

    args = parser.parse_args()

    try:
        # Process inventory
        standardizer = InventoryStandardizer(args.input, args.corrections)
        standardizer.load_corrections()
        standardizer.load_records()
        standardizer.apply_corrections()
        standardizer.standardize_all()

        # Generate report
        total, valid, invalid, withdrawn, errors = standardizer.get_report()

        print(f"\n{'='*60}")
        print("INVENTORY STANDARDIZATION REPORT")
        print(f"{'='*60}")
        print(f"Total records:      {total}")
        print(f"Valid records:      {valid}")
        print(f"Invalid records:    {invalid}")
        print(f"Withdrawn records:  {withdrawn}")

        if errors and args.verbose:
            print(f"\n{'ERRORS':-^60}")
            for error in errors:
                print(f"  {error}")

        # Save standardized records
        standardizer.save(args.output, args.include_withdrawn)
        print(f"\nStandardized records saved to: {args.output}")
        print(f"{'='*60}\n")

        # Return appropriate exit code
        return 0 if invalid == 0 else 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

## Usage Examples

### Basic usage:
```bash
python standardize_inventory.py inventory.tsv -o standardized.tsv
```

### With corrections file and verbose output:
```bash
python standardize_inventory.py inventory.tsv \
  -c corrections.tsv \
  -o standardized.tsv \
  -v
```

### Include withdrawn records in output:
```bash
python standardize_inventory.py inventory.tsv \
  --include-withdrawn \
  -o standardized.tsv
```

## Input File Format (TSV)

```
date	title	object_number	link
01/15/2020	Ancient Vase	2020-15	www.example.com/objects/vase
2020/06/20	Painting Frame	2020.16.1	https://example.com/frame
```

## Corrections File Format (TSV)

```
object_number	action	date	title	link
2020.15	update	2020-06-15	Corrected Vase Title	https://example.com/vase-updated
2020.16	withdraw		
```

## Features

✓ **Date standardization** to ISO 8601  
✓ **Title normalization** (whitespace, punctuation)  
✓ **Object number validation** and formatting  
✓ **URL standardization** (protocol, validation)  
✓ **Corrections and withdrawals** support  
✓ **Error reporting** with row numbers  
✓ **Comprehensive validation**  
✓ **UTF-8 encoding** support
