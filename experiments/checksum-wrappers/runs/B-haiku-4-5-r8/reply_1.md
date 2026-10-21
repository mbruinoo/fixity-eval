# Museum Inventory Standardizer

Here's a comprehensive Python script for standardizing museum inventory records:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer

Standardizes museum records from a TSV file by:
- Validating required fields
- Formatting dates consistently
- Normalizing object numbers
- Cleaning and validating URLs
- Generating standardized output
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
    
    REQUIRED_FIELDS = {'date', 'title', 'object_number', 'link'}
    DATE_FORMATS = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y',
        '%B %d, %Y',
        '%b %d, %Y',
    ]
    
    def __init__(self, input_file: str, output_file: str = None, verbose: bool = False):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file (optional)
            verbose: Enable verbose output
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self.input_file.with_stem(
            self.input_file.stem + '_standardized'
        )
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.records_processed = 0
        self.records_valid = 0
    
    def standardize_date(self, date_str: str) -> Tuple[str, bool]:
        """
        Standardize date to YYYY-MM-DD format.
        
        Args:
            date_str: Date string to standardize
            
        Returns:
            Tuple of (standardized_date, is_valid)
        """
        if not date_str or not date_str.strip():
            return '', False
        
        date_str = date_str.strip()
        
        # Try each format
        for fmt in self.DATE_FORMATS:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d'), True
            except ValueError:
                continue
        
        # If no format matches, return original with warning
        self.warnings.append(f"Could not parse date: '{date_str}'")
        return date_str, False
    
    def normalize_object_number(self, obj_num: str) -> str:
        """
        Normalize object number format.
        
        Removes extra whitespace and converts to uppercase.
        
        Args:
            obj_num: Object number to normalize
            
        Returns:
            Normalized object number
        """
        if not obj_num:
            return ''
        
        # Remove extra whitespace
        normalized = ' '.join(obj_num.split())
        # Convert to uppercase
        normalized = normalized.upper()
        
        return normalized
    
    def validate_url(self, url: str) -> Tuple[str, bool]:
        """
        Validate and normalize URL.
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (url, is_valid)
        """
        if not url or not url.strip():
            return '', False
        
        url = url.strip()
        
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            result = urlparse(url)
            # Basic validation
            if result.scheme and result.netloc:
                return url, True
            else:
                self.warnings.append(f"Invalid URL format: '{url}'")
                return url, False
        except Exception as e:
            self.warnings.append(f"Error parsing URL '{url}': {str(e)}")
            return url, False
    
    def clean_title(self, title: str) -> str:
        """
        Clean and standardize title.
        
        Args:
            title: Title to clean
            
        Returns:
            Cleaned title
        """
        if not title:
            return ''
        
        # Remove extra whitespace
        title = ' '.join(title.split())
        # Capitalize first letter
        title = title[0].upper() + title[1:] if title else ''
        
        return title
    
    def validate_record(self, record: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate a record has all required fields.
        
        Args:
            record: Record to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        field_names = set(k.lower() for k in record.keys())
        
        for required in self.REQUIRED_FIELDS:
            if required not in field_names:
                errors.append(f"Missing required field: '{required}'")
        
        return len(errors) == 0, errors
    
    def standardize_record(self, record: Dict[str, str], record_num: int) -> Tuple[Dict[str, str], bool]:
        """
        Standardize a single record.
        
        Args:
            record: Record to standardize
            record_num: Record number for error reporting
            
        Returns:
            Tuple of (standardized_record, is_valid)
        """
        # Validate required fields
        is_valid, validation_errors = self.validate_record(record)
        if not is_valid:
            for error in validation_errors:
                self.errors.append(f"Record {record_num}: {error}")
            return record, False
        
        # Get field names (case-insensitive)
        field_map = {k.lower(): k for k in record.keys()}
        
        standardized = {}
        
        # Standardize date
        date_field = field_map.get('date', 'date')
        date_str, date_valid = self.standardize_date(record.get(date_field, ''))
        standardized['date'] = date_str
        
        if not date_valid and record.get(date_field):
            self.errors.append(f"Record {record_num}: Invalid date format")
            is_valid = False
        
        # Clean and standardize title
        title_field = field_map.get('title', 'title')
        standardized['title'] = self.clean_title(record.get(title_field, ''))
        
        if not standardized['title']:
            self.errors.append(f"Record {record_num}: Empty title")
            is_valid = False
        
        # Normalize object number
        obj_field = field_map.get('object_number', 'object_number')
        standardized['object_number'] = self.normalize_object_number(record.get(obj_field, ''))
        
        if not standardized['object_number']:
            self.errors.append(f"Record {record_num}: Empty object number")
            is_valid = False
        
        # Validate URL
        link_field = field_map.get('link', 'link')
        link_str, link_valid = self.validate_url(record.get(link_field, ''))
        standardized['link'] = link_str
        
        if not link_valid and record.get(link_field):
            self.errors.append(f"Record {record_num}: Invalid URL")
            is_valid = False
        
        # Include any additional fields
        for key, value in record.items():
            lower_key = key.lower()
            if lower_key not in self.REQUIRED_FIELDS:
                standardized[key] = value
        
        return standardized, is_valid
    
    def process(self) -> bool:
        """
        Process the inventory file.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.input_file.exists():
            print(f"Error: Input file not found: {self.input_file}")
            return False
        
        try:
            records = []
            
            # Read input file
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    print("Error: Input file is empty or invalid")
                    return False
                
                for i, record in enumerate(reader, start=1):
                    self.records_processed += 1
                    standardized, is_valid = self.standardize_record(record, i)
                    records.append(standardized)
                    
                    if is_valid:
                        self.records_valid += 1
                    
                    if self.verbose:
                        status = "✓" if is_valid else "✗"
                        print(f"[{status}] Record {i}: {standardized.get('object_number', 'N/A')}")
            
            # Write output file
            if records:
                fieldnames = list(records[0].keys())
                # Ensure standard fields are first
                ordered_fields = []
                for field in ['date', 'title', 'object_number', 'link']:
                    if field in fieldnames:
                        ordered_fields.append(field)
                        fieldnames.remove(field)
                ordered_fields.extend(fieldnames)
                
                with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=ordered_fields, delimiter='\t')
                    writer.writeheader()
                    writer.writerows(records)
                
                if self.verbose:
                    print(f"\nOutput written to: {self.output_file}")
            
            return True
        
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return False
    
    def print_report(self):
        """Print a summary report of the standardization."""
        print("\n" + "=" * 60)
        print("STANDARDIZATION REPORT")
        print("=" * 60)
        print(f"Records processed: {self.records_processed}")
        print(f"Records valid:     {self.records_valid}")
        print(f"Records with issues: {self.records_processed - self.records_valid}")
        
        if self.warnings:
            print(f"\n{len(self.warnings)} Warning(s):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  ⚠ {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        if self.errors:
            print(f"\n{len(self.errors)} Error(s):")
            for error in self.errors[:10]:  # Show first 10
                print(f"  ✗ {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        
        if not self.warnings and not self.errors:
            print("\n✓ No issues found!")
        
        print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records from a TSV file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s inventory.tsv
  %(prog)s inventory.tsv -o standardized.tsv -v
        """
    )
    
    parser.add_argument('input', help='Input TSV file')
    parser.add_argument('-o', '--output', help='Output TSV file (default: input_standardized.tsv)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    standardizer = InventoryStandardizer(args.input, args.output, args.verbose)
    
    if standardizer.process():
        standardizer.print_report()
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## Sample Usage

**Example input file (inventory.tsv):**
```
date	title	object_number	link
1925-06-15	Portrait of Alice	1920.45.A	http://example.com/portrait1
06/20/1930	Vase with Blue Glaze	1930-120	example.com/vase
1850	ancient coin	coin_1850_04	https://example.com/coin1
2020/01/15	Modern Sculpture	2020.15.B	example.org/sculpture
	Empty Frame	1901.22.C	https://example.com/frame
```

**Run the script:**
```bash
# Basic usage
python3 standardize_inventory.py inventory.tsv

# With custom output file and verbose mode
python3 standardize_inventory.py inventory.tsv -o output.tsv -v

# Help
python3 standardize_inventory.py --help
```

## Features

- **Date standardization** to YYYY-MM-DD format
- **Object number normalization** (uppercase, consistent spacing)
- **URL validation** and normalization
- **Title cleaning** (whitespace, capitalization)
- **Comprehensive error reporting**
- **Validation of required fields**
- **Verbose mode** for detailed processing info
- **Summary report** with warnings and errors

The script preserves any additional fields beyond the standard four and outputs a clean, standardized TSV file.
