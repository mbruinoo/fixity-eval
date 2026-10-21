# Museum Inventory Standardizer

Here's a comprehensive Python script to standardize museum inventory spreadsheets:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer

Standardizes museum inventory TSV files with columns:
date, title, object_number, link
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
    """Standardizes museum inventory data."""

    def __init__(self, input_file: str, output_file: str = None, verbose: bool = False):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self._get_output_path()
        self.verbose = verbose
        self.errors = []
        self.warnings = []

    def _get_output_path(self) -> Path:
        """Generate output filename if not provided."""
        return self.input_file.parent / f"{self.input_file.stem}_standardized.tsv"

    def standardize_date(self, date_str: str) -> str:
        """
        Standardize dates to ISO 8601 format (YYYY-MM-DD).
        
        Args:
            date_str: Raw date string
            
        Returns:
            Standardized date or empty string if invalid
        """
        if not date_str or not date_str.strip():
            return ""

        date_str = date_str.strip()
        date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
            "%m-%d-%Y",
            "%d-%m-%Y",
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        self.warnings.append(f"Could not parse date: '{date_str}'")
        return date_str

    def standardize_title(self, title: str) -> str:
        """
        Standardize title formatting.
        
        Args:
            title: Raw title string
            
        Returns:
            Cleaned title
        """
        if not title:
            return ""

        # Strip whitespace
        title = title.strip()

        # Remove extra spaces
        title = re.sub(r'\s+', ' ', title)

        # Remove trailing punctuation if only punctuation
        title = re.sub(r'[,;:]*$', '', title)

        return title

    def standardize_object_number(self, obj_num: str) -> str:
        """
        Standardize object number format.
        Remove extra spaces, ensure consistent casing.
        
        Args:
            obj_num: Raw object number
            
        Returns:
            Standardized object number
        """
        if not obj_num:
            return ""

        # Remove extra spaces
        obj_num = re.sub(r'\s+', ' ', obj_num.strip())

        # Convert to uppercase
        obj_num = obj_num.upper()

        return obj_num

    def standardize_link(self, link: str) -> str:
        """
        Validate and standardize URL format.
        
        Args:
            link: Raw URL string
            
        Returns:
            Standardized URL or empty string if invalid
        """
        if not link or not link.strip():
            return ""

        link = link.strip()

        # Add protocol if missing
        if not re.match(r'^https?://', link):
            link = 'https://' + link

        # Validate URL structure
        try:
            result = urlparse(link)
            if not all([result.scheme, result.netloc]):
                self.warnings.append(f"Invalid URL structure: '{link}'")
                return ""
        except Exception as e:
            self.warnings.append(f"Error parsing URL '{link}': {str(e)}")
            return ""

        return link

    def validate_row(self, row: Dict[str, str], row_num: int) -> bool:
        """
        Validate required fields in a row.
        
        Args:
            row: Dictionary of row data
            row_num: Row number for error reporting
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['date', 'title', 'object_number', 'link']
        
        for field in required_fields:
            if field not in row:
                self.errors.append(f"Row {row_num}: Missing column '{field}'")
                return False

        # At least title or object number should exist
        if not row.get('title', '').strip() and not row.get('object_number', '').strip():
            self.warnings.append(f"Row {row_num}: Both title and object_number are empty")

        return True

    def process(self) -> Tuple[bool, int, int]:
        """
        Process the inventory file.
        
        Returns:
            Tuple of (success, rows_processed, rows_with_warnings)
        """
        if not self.input_file.exists():
            self.errors.append(f"Input file not found: {self.input_file}")
            return False, 0, 0

        try:
            rows = []
            row_count = 0
            warning_count = 0

            # Read input file
            with open(self.input_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile, delimiter='\t')
                
                # Validate headers
                if not reader.fieldnames:
                    self.errors.append("No headers found in file")
                    return False, 0, 0

                expected_fields = {'date', 'title', 'object_number', 'link'}
                actual_fields = set(reader.fieldnames)

                if not expected_fields.issubset(actual_fields):
                    missing = expected_fields - actual_fields
                    self.errors.append(f"Missing required columns: {missing}")
                    return False, 0, 0

                # Process each row
                for row_num, row in enumerate(reader, start=2):
                    if not self.validate_row(row, row_num):
                        continue

                    # Store warning count before processing
                    warnings_before = len(self.warnings)

                    # Standardize each field
                    standardized_row = {
                        'date': self.standardize_date(row.get('date', '')),
                        'title': self.standardize_title(row.get('title', '')),
                        'object_number': self.standardize_object_number(row.get('object_number', '')),
                        'link': self.standardize_link(row.get('link', '')),
                    }

                    # Add any extra columns
                    for key in row:
                        if key not in standardized_row:
                            standardized_row[key] = row[key]

                    rows.append(standardized_row)
                    row_count += 1

                    if len(self.warnings) > warnings_before:
                        warning_count += 1

            # Write output file
            if rows:
                fieldnames = ['date', 'title', 'object_number', 'link']
                # Add any extra columns from source
                extra_fields = set(rows[0].keys()) - set(fieldnames)
                fieldnames.extend(sorted(extra_fields))

                with open(self.output_file, 'w', encoding='utf-8', newline='') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')
                    writer.writeheader()
                    writer.writerows(rows)

                if self.verbose:
                    print(f"✓ Output written to: {self.output_file}")

                return True, row_count, warning_count
            else:
                self.errors.append("No valid rows found to process")
                return False, 0, 0

        except Exception as e:
            self.errors.append(f"Error processing file: {str(e)}")
            return False, 0, 0

    def print_report(self):
        """Print processing report."""
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more warnings")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory TSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python standardize_inventory.py inventory.tsv
  python standardize_inventory.py inventory.tsv -o output.tsv -v
  python standardize_inventory.py *.tsv
        '''
    )

    parser.add_argument('input_file', help='Input TSV file path')
    parser.add_argument('-o', '--output', help='Output TSV file path (optional)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    standardizer = InventoryStandardizer(
        args.input_file,
        args.output,
        args.verbose
    )

    success, rows, warnings = standardizer.process()

    standardizer.print_report()

    if success:
        print(f"\n✓ Successfully processed {rows} rows")
        if warnings:
            print(f"  ({warnings} rows had warnings)")
        sys.exit(0)
    else:
        print("\n✗ Processing failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## Sample Input File (`inventory.tsv`)

```tsv
date	title	object_number	link
1/15/2024	Ancient Vase	2024.001.A	www.museum.org/item/1
2024-02-20	Medieval Sword	2024.002.B	https://museum.org/item/2
March 10, 2024	Renaissance Painting		http://museum.org/item/3
2024/04/05	   Ceramic Bowl   	2024.004.D	museum.org/item/4
```

## Usage

```bash
# Basic usage
python standardize_inventory.py inventory.tsv

# With custom output file
python standardize_inventory.py inventory.tsv -o cleaned.tsv

# Verbose mode
python standardize_inventory.py inventory.tsv -v
```

## Features

✅ **Date Standardization**: Converts multiple date formats to ISO 8601 (YYYY-MM-DD)
✅ **Title Cleaning**: Removes extra spaces, trailing punctuation
✅ **Object Number Standardization**: Converts to uppercase, removes extra spaces
✅ **URL Validation**: Adds protocol, validates structure
✅ **Error Reporting**: Detailed error and warning messages
✅ **Flexible Input**: Handles various date and URL formats
✅ **Extra Columns**: Preserves any additional columns from source file

Would you like me to add additional features like duplicate detection, data backup, or batch processing?
