# Museum Inventory Standardization Script

```python
#!/usr/bin/env python3
"""
Script to standardize museum inventory records from a TSV file.

Expected TSV format:
- Columns: date, title, object_number, link
- Tab-separated values
"""

import csv
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import argparse


class InventoryStandardizer:
    """Standardizes museum inventory records."""

    def __init__(self, input_file: str, output_file: str = None):
        """
        Initialize the standardizer.

        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file (defaults to input_standardized.tsv)
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file or self._default_output_name())
        self.records = []
        self.errors = []

    def _default_output_name(self) -> str:
        """Generate default output filename."""
        stem = self.input_file.stem
        return f"{stem}_standardized.tsv"

    def read_inventory(self) -> bool:
        """
        Read inventory from TSV file.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')

                if reader.fieldnames is None:
                    self.errors.append("Empty file or unable to read headers")
                    return False

                required_fields = {'date', 'title', 'object_number', 'link'}
                if not required_fields.issubset(set(reader.fieldnames or [])):
                    self.errors.append(
                        f"Missing required columns. Expected: {required_fields}"
                    )
                    return False

                for row_num, row in enumerate(reader, start=2):
                    self.records.append((row_num, row))

            return True

        except FileNotFoundError:
            self.errors.append(f"File not found: {self.input_file}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading file: {str(e)}")
            return False

    @staticmethod
    def standardize_date(date_str: str) -> Tuple[str, str]:
        """
        Standardize date to ISO 8601 format (YYYY-MM-DD).

        Args:
            date_str: Date string in various formats

        Returns:
            Tuple of (standardized_date, error_message or empty string)
        """
        date_str = date_str.strip()

        if not date_str or date_str.lower() in ('unknown', 'n/a', 'none'):
            return '', "Missing date"

        # Try common date formats
        formats = [
            '%Y-%m-%d',  # 2023-01-15
            '%m/%d/%Y',  # 01/15/2023
            '%d/%m/%Y',  # 15/01/2023
            '%Y/%m/%d',  # 2023/01/15
            '%B %d, %Y',  # January 15, 2023
            '%b %d, %Y',  # Jan 15, 2023
            '%d %B %Y',  # 15 January 2023
            '%d %b %Y',  # 15 Jan 2023
            '%Y',  # 2023
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime('%Y-%m-%d'), ''
            except ValueError:
                continue

        # If no format matched, try to extract year
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            return f"{year_match.group()}-01-01", f"Partial date (year only): {date_str}"

        return '', f"Unable to parse date: {date_str}"

    @staticmethod
    def standardize_title(title: str) -> Tuple[str, str]:
        """
        Standardize title (trim, normalize whitespace, title case).

        Args:
            title: Title string

        Returns:
            Tuple of (standardized_title, error_message or empty string)
        """
        title = title.strip()

        if not title or title.lower() in ('unknown', 'n/a', 'none', 'untitled'):
            return '', "Missing title"

        # Normalize whitespace
        title = ' '.join(title.split())

        # Capitalize appropriately (preserve intentional case)
        # For mixed case titles, keep as-is; for all-caps, convert to title case
        if title.isupper() and len(title) > 1:
            title = title.title()

        return title, ''

    @staticmethod
    def standardize_object_number(obj_num: str) -> Tuple[str, str]:
        """
        Standardize object number (remove extra spaces, validate format).

        Args:
            obj_num: Object number string

        Returns:
            Tuple of (standardized_object_number, error_message or empty string)
        """
        obj_num = obj_num.strip()

        if not obj_num or obj_num.lower() in ('unknown', 'n/a', 'none'):
            return '', "Missing object number"

        # Remove extra spaces but preserve structure
        obj_num = ' '.join(obj_num.split())

        # Check for reasonable format (alphanumeric with common separators)
        if not re.match(r'^[A-Za-z0-9\.\-/]+$', obj_num):
            return obj_num, f"Unusual characters in object number: {obj_num}"

        return obj_num, ''

    @staticmethod
    def standardize_link(link: str) -> Tuple[str, str]:
        """
        Standardize link (validate URL format).

        Args:
            link: URL string

        Returns:
            Tuple of (standardized_link, error_message or empty string)
        """
        link = link.strip()

        if not link or link.lower() in ('unknown', 'n/a', 'none', ''):
            return '', "Missing link"

        # Add https:// if no protocol specified
        if not re.match(r'^https?://', link):
            link = 'https://' + link

        # Basic URL validation
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, link):
            return link, f"Invalid URL format: {link}"

        return link, ''

    def standardize_record(self, record: Dict) -> Tuple[Dict, List[str]]:
        """
        Standardize a single record.

        Args:
            record: Dictionary with date, title, object_number, link

        Returns:
            Tuple of (standardized_record, list_of_warnings)
        """
        warnings = []

        date, date_warn = self.standardize_date(record.get('date', ''))
        if date_warn:
            warnings.append(date_warn)

        title, title_warn = self.standardize_title(record.get('title', ''))
        if title_warn:
            warnings.append(title_warn)

        obj_num, obj_num_warn = self.standardize_object_number(
            record.get('object_number', '')
        )
        if obj_num_warn:
            warnings.append(obj_num_warn)

        link, link_warn = self.standardize_link(record.get('link', ''))
        if link_warn:
            warnings.append(link_warn)

        standardized = {
            'date': date,
            'title': title,
            'object_number': obj_num,
            'link': link
        }

        return standardized, warnings

    def process_inventory(self) -> bool:
        """
        Process and standardize all inventory records.

        Returns:
            bool: True if processing completed
        """
        print(f"Processing {len(self.records)} records...")

        standardized_records = []
        all_warnings = []

        for row_num, record in self.records:
            standardized, warnings = self.standardize_record(record)
            standardized_records.append(standardized)

            for warning in warnings:
                all_warnings.append((row_num, warning))

        self.records = standardized_records

        # Print warnings
        if all_warnings:
            print(f"\n⚠️  Found {len(all_warnings)} issues:")
            for row_num, warning in all_warnings:
                print(f"  Row {row_num}: {warning}")

        return True

    def write_inventory(self) -> bool:
        """
        Write standardized inventory to TSV file.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            fieldnames = ['date', 'title', 'object_number', 'link']

            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(self.records)

            print(f"\n✓ Standardized inventory written to: {self.output_file}")
            return True

        except Exception as e:
            self.errors.append(f"Error writing file: {str(e)}")
            return False

    def print_errors(self):
        """Print any errors encountered."""
        if self.errors:
            print("\n❌ Errors:", file=sys.stderr)
            for error in self.errors:
                print(f"  {error}", file=sys.stderr)

    def run(self) -> bool:
        """
        Execute the standardization pipeline.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.read_inventory():
            self.print_errors()
            return False

        if not self.process_inventory():
            self.print_errors()
            return False

        if not self.write_inventory():
            self.print_errors()
            return False

        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records from a TSV file'
    )
    parser.add_argument('input', help='Input TSV file path')
    parser.add_argument(
        '-o', '--output',
        help='Output TSV file path (default: input_standardized.tsv)'
    )

    args = parser.parse_args()

    standardizer = InventoryStandardizer(args.input, args.output)

    if standardizer.run():
        print("\n✓ Standardization complete!")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## Usage

### Basic usage:
```bash
python standardize_inventory.py inventory.tsv
```

### With custom output file:
```bash
python standardize_inventory.py inventory.tsv -o standardized_records.tsv
```

## Features

- **Date standardization**: Converts various date formats to ISO 8601 (YYYY-MM-DD)
- **Title normalization**: Trims whitespace, normalizes capitalization
- **Object number validation**: Ensures proper formatting, checks for unusual characters
- **Link validation**: Validates URLs, adds protocol if missing
- **Error reporting**: Identifies and reports issues during standardization
- **Comprehensive logging**: Tracks warnings and errors by row number

## Example Input (inventory.tsv)

```
date	title	object_number	link
01/15/2023	ANCIENT GREEK VASE	1952.4.10	www.example.com/vases/001
2023-03-20	Medieval Sword	MS-1847-002	https://museum.org/artifacts/ms1847002
1995	Portrait of Unknown Subject	1995.45.3a	museum.org/collections/1995.45.3a
```

## Example Output

The script creates a `_standardized.tsv` file with normalized records and displays warnings for any data quality issues.
