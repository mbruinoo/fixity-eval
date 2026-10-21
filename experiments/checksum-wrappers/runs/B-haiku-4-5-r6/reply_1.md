# Museum Inventory Standardizer

Here's a comprehensive Python script for standardizing museum inventory records:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer

Standardizes museum inventory records from a TSV file.
Validates, cleans, and reformats object records.
"""

import argparse
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import csv


class MuseumInventoryStandardizer:
    """Standardizes museum inventory records."""
    
    # Standards for object numbers (customize as needed)
    OBJECT_NUMBER_PATTERN = r'^[A-Z]{2,4}\.\d{4}\.\d{3}$'
    
    # URL validation pattern
    URL_PATTERN = r'^https?://[^\s]+$'
    
    # Valid date formats to try
    DATE_FORMATS = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%B %d, %Y',
        '%b %d, %Y',
    ]
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize the standardizer.
        
        Args:
            strict_mode: If True, reject records with any issues.
                        If False, attempt to fix issues.
        """
        self.strict_mode = strict_mode
        self.warnings = []
        self.errors = []
        
    def read_tsv(self, filepath: str) -> Tuple[List[str], List[Dict]]:
        """
        Read TSV file with inventory records.
        
        Args:
            filepath: Path to TSV file
            
        Returns:
            Tuple of (fieldnames, records)
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                fieldnames = reader.fieldnames
                records = list(reader)
            return fieldnames, records
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def standardize_date(self, date_str: str, record_num: int) -> Tuple[str, bool]:
        """
        Standardize date to YYYY-MM-DD format.
        
        Args:
            date_str: Date string to standardize
            record_num: Record number for error reporting
            
        Returns:
            Tuple of (standardized_date, is_valid)
        """
        if not date_str or not date_str.strip():
            self.errors.append(f"Record {record_num}: Date is empty")
            return '', False
        
        date_str = date_str.strip()
        
        # Try each format
        for date_format in self.DATE_FORMATS:
            try:
                date_obj = datetime.strptime(date_str, date_format)
                return date_obj.strftime('%Y-%m-%d'), True
            except ValueError:
                continue
        
        # If no format matched
        self.errors.append(
            f"Record {record_num}: Invalid date format: '{date_str}'. "
            f"Expected one of: {', '.join(self.DATE_FORMATS)}"
        )
        return date_str, False
    
    def standardize_title(self, title: str, record_num: int) -> Tuple[str, bool]:
        """
        Standardize title.
        
        Args:
            title: Title string to standardize
            record_num: Record number for error reporting
            
        Returns:
            Tuple of (standardized_title, is_valid)
        """
        if not title or not title.strip():
            self.errors.append(f"Record {record_num}: Title is empty")
            return '', False
        
        title = title.strip()
        
        # Remove extra whitespace
        title = ' '.join(title.split())
        
        # Check for minimum length
        if len(title) < 3:
            self.errors.append(
                f"Record {record_num}: Title too short: '{title}'"
            )
            return title, False
        
        return title, True
    
    def standardize_object_number(self, obj_num: str, record_num: int) -> Tuple[str, bool]:
        """
        Standardize object number.
        
        Args:
            obj_num: Object number to standardize
            record_num: Record number for error reporting
            
        Returns:
            Tuple of (standardized_number, is_valid)
        """
        if not obj_num or not obj_num.strip():
            self.errors.append(f"Record {record_num}: Object number is empty")
            return '', False
        
        obj_num = obj_num.strip().upper()
        
        # Check against pattern
        if not re.match(self.OBJECT_NUMBER_PATTERN, obj_num):
            self.errors.append(
                f"Record {record_num}: Invalid object number format: '{obj_num}'. "
                f"Expected format like: MUS.2024.001"
            )
            return obj_num, False
        
        return obj_num, True
    
    def standardize_link(self, link: str, record_num: int) -> Tuple[str, bool]:
        """
        Standardize URL link.
        
        Args:
            link: URL to standardize
            record_num: Record number for error reporting
            
        Returns:
            Tuple of (standardized_link, is_valid)
        """
        if not link or not link.strip():
            self.warnings.append(f"Record {record_num}: Link is empty")
            return '', True
        
        link = link.strip()
        
        # Ensure protocol
        if not link.startswith(('http://', 'https://')):
            link = 'https://' + link
            self.warnings.append(
                f"Record {record_num}: Added https:// protocol to link"
            )
        
        # Validate URL format
        if not re.match(self.URL_PATTERN, link):
            self.errors.append(
                f"Record {record_num}: Invalid URL format: '{link}'"
            )
            return link, False
        
        return link, True
    
    def standardize_record(self, record: Dict, record_num: int) -> Tuple[Dict, bool]:
        """
        Standardize a single record.
        
        Args:
            record: Record dictionary
            record_num: Record number for error reporting
            
        Returns:
            Tuple of (standardized_record, is_valid)
        """
        self.warnings.clear()
        self.errors.clear()
        
        standardized = {}
        all_valid = True
        
        # Standardize each field
        date, valid = self.standardize_date(record.get('date', ''), record_num)
        standardized['date'] = date
        all_valid = all_valid and valid
        
        title, valid = self.standardize_title(record.get('title', ''), record_num)
        standardized['title'] = title
        all_valid = all_valid and valid
        
        obj_num, valid = self.standardize_object_number(
            record.get('object_number', ''), record_num
        )
        standardized['object_number'] = obj_num
        all_valid = all_valid and valid
        
        link, valid = self.standardize_link(record.get('link', ''), record_num)
        standardized['link'] = link
        all_valid = all_valid and valid
        
        if self.strict_mode and not all_valid:
            return standardized, False
        
        return standardized, True
    
    def standardize_records(self, records: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """
        Standardize multiple records.
        
        Args:
            records: List of record dictionaries
            
        Returns:
            Tuple of (standardized_records, issues_list)
        """
        standardized_records = []
        all_issues = []
        
        for i, record in enumerate(records, 1):
            std_record, is_valid = self.standardize_record(record, i)
            
            if is_valid or not self.strict_mode:
                standardized_records.append(std_record)
            
            # Collect issues
            all_issues.extend([f"ERROR: {e}" for e in self.errors])
            all_issues.extend([f"WARNING: {w}" for w in self.warnings])
        
        return standardized_records, all_issues
    
    def write_tsv(self, filepath: str, records: List[Dict], fieldnames: List[str]):
        """
        Write standardized records to TSV file.
        
        Args:
            filepath: Output file path
            records: Records to write
            fieldnames: Field names for TSV
        """
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(records)
            print(f"✓ Successfully wrote {len(records)} records to {filepath}")
        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records from a TSV file'
    )
    parser.add_argument('input', help='Input TSV file')
    parser.add_argument(
        '-o', '--output',
        help='Output TSV file (default: input_standardized.tsv)'
    )
    parser.add_argument(
        '-s', '--strict',
        action='store_true',
        help='Strict mode: reject records with any issues'
    )
    parser.add_argument(
        '-r', '--report',
        help='Write validation report to file'
    )
    
    args = parser.parse_args()
    
    # Set output filename
    if args.output:
        output_file = args.output
    else:
        input_path = Path(args.input)
        output_file = input_path.stem + '_standardized.tsv'
    
    print(f"Reading inventory from: {args.input}")
    
    # Initialize standardizer
    standardizer = MuseumInventoryStandardizer(strict_mode=args.strict)
    
    # Read input
    fieldnames, records = standardizer.read_tsv(args.input)
    print(f"✓ Read {len(records)} records")
    
    # Standardize
    print("Standardizing records...")
    std_records, issues = standardizer.standardize_records(records)
    
    # Write output
    standardizer.write_tsv(output_file, std_records, fieldnames)
    
    # Report issues
    if issues:
        print(f"\n{'='*60}")
        print(f"Issues found: {len(issues)}")
        print(f"{'='*60}")
        for issue in issues:
            print(issue)
        
        # Write report if requested
        if args.report:
            with open(args.report, 'w') as f:
                f.write('\n'.join(issues))
            print(f"\n✓ Report written to: {args.report}")
    else:
        print("\n✓ No issues found!")
    
    print(f"\n✓ Standardization complete!")


if __name__ == '__main__':
    main()
```

## Usage

### Basic usage:
```bash
python standardize_inventory.py inventory.tsv
```

### With custom output:
```bash
python standardize_inventory.py inventory.tsv -o standardized.tsv
```

### Strict mode (reject any invalid records):
```bash
python standardize_inventory.py inventory.tsv -s
```

### Generate validation report:
```bash
python standardize_inventory.py inventory.tsv -r report.txt
```

## Example TSV Input

```
date	title	object_number	link
01/15/2024	Ancient Vase	mus.2024.001	https://museum.org/vase
2024-02-20	Painting	MUS.2024.002	museum.org/painting
```

## Features

- **Date standardization**: Converts multiple date formats to YYYY-MM-DD
- **Title cleaning**: Removes extra whitespace, validates length
- **Object number validation**: Checks format (e.g., MUS.2024.001)
- **URL standardization**: Adds protocol if missing, validates format
- **Error reporting**: Detailed feedback on issues
- **Strict mode**: Option to reject problematic records
- **Validation report**: Optional output file with all issues

You can customize the `OBJECT_NUMBER_PATTERN` and `DATE_FORMATS` to match your museum's standards!
