# Museum Inventory Standardization Script

```python
#!/usr/bin/env python3
"""
Script to standardize museum inventory records from a TSV file.

Standardizes:
- Date formats (ISO 8601: YYYY-MM-DD)
- Title capitalization (Title Case)
- Object numbers (remove spaces, uppercase prefix)
- URLs (validate and normalize)
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import re


class InventoryStandardizer:
    """Standardizes museum inventory records."""
    
    def __init__(self, object_prefix="OBJ"):
        self.object_prefix = object_prefix
        self.errors = []
        self.warnings = []
    
    def standardize_date(self, date_str):
        """
        Standardize date to ISO 8601 format (YYYY-MM-DD).
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Standardized date string or None if invalid
        """
        if not date_str or date_str.strip() == "":
            self.warnings.append("Empty date field")
            return ""
        
        date_str = date_str.strip()
        
        # Common date formats to try
        formats = [
            "%Y-%m-%d",      # ISO 8601
            "%m/%d/%Y",      # US format
            "%d/%m/%Y",      # EU format
            "%Y/%m/%d",      # Alternative ISO
            "%B %d, %Y",     # Long format (January 01, 2020)
            "%b %d, %Y",     # Short format (Jan 01, 2020)
            "%Y",            # Year only
            "%m-%d-%Y",      # US with dashes
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        self.errors.append(f"Could not parse date: {date_str}")
        return date_str
    
    def standardize_title(self, title):
        """
        Standardize title to Title Case.
        
        Args:
            title: Title string
            
        Returns:
            Title case string
        """
        if not title or title.strip() == "":
            self.warnings.append("Empty title field")
            return ""
        
        # Convert to title case but preserve already-capitalized acronyms
        title = title.strip()
        
        # Words that should remain lowercase
        lowercase_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for',
                          'if', 'in', 'of', 'on', 'or', 'the', 'to', 'with'}
        
        words = title.split()
        standardized = []
        
        for i, word in enumerate(words):
            # First and last words always capitalized
            if i == 0 or i == len(words) - 1:
                standardized.append(word.capitalize())
            elif word.lower() in lowercase_words:
                standardized.append(word.lower())
            else:
                standardized.append(word.capitalize())
        
        return " ".join(standardized)
    
    def standardize_object_number(self, obj_num):
        """
        Standardize object number format.
        
        Removes spaces, converts to uppercase, ensures prefix.
        
        Args:
            obj_num: Object number string
            
        Returns:
            Standardized object number
        """
        if not obj_num or obj_num.strip() == "":
            self.errors.append("Empty object number")
            return ""
        
        obj_num = obj_num.strip().upper().replace(" ", "")
        
        # Add prefix if not present
        if not obj_num.startswith(self.object_prefix):
            obj_num = f"{self.object_prefix}.{obj_num}"
        
        # Ensure format is PREFIX.NNNNNN (where N is digit)
        match = re.match(r"([A-Z]+)\.?(\d+)", obj_num)
        if match:
            prefix, number = match.groups()
            # Pad number with leading zeros (6 digits)
            obj_num = f"{prefix}.{number.zfill(6)}"
        else:
            self.errors.append(f"Invalid object number format: {obj_num}")
        
        return obj_num
    
    def standardize_link(self, link):
        """
        Standardize and validate URL.
        
        Args:
            link: URL string
            
        Returns:
            Standardized URL or empty string if invalid
        """
        if not link or link.strip() == "":
            return ""
        
        link = link.strip()
        
        # Add scheme if missing
        if not link.startswith(("http://", "https://")):
            link = f"https://{link}"
        
        # Validate URL
        try:
            result = urlparse(link)
            if not all([result.scheme, result.netloc]):
                self.errors.append(f"Invalid URL: {link}")
                return link
        except Exception as e:
            self.errors.append(f"Error parsing URL {link}: {str(e)}")
            return link
        
        return link
    
    def standardize_record(self, record):
        """
        Standardize a single record.
        
        Args:
            record: Dictionary with keys: date, title, object_number, link
            
        Returns:
            Standardized record dictionary
        """
        self.errors = []
        self.warnings = []
        
        standardized = {
            'date': self.standardize_date(record.get('date', '')),
            'title': self.standardize_title(record.get('title', '')),
            'object_number': self.standardize_object_number(record.get('object_number', '')),
            'link': self.standardize_link(record.get('link', '')),
        }
        
        return standardized
    
    def process_file(self, input_file, output_file):
        """
        Process entire inventory file.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file
            
        Returns:
            Tuple of (success_count, error_count, warning_count)
        """
        success_count = 0
        error_count = 0
        warning_count = 0
        all_warnings = []
        all_errors = []
        
        try:
            with open(input_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile, delimiter='\t')
                
                # Validate header
                if not reader.fieldnames:
                    print("Error: Empty file or invalid TSV format", file=sys.stderr)
                    return 0, 1, 0
                
                required_fields = {'date', 'title', 'object_number', 'link'}
                if not required_fields.issubset(set(reader.fieldnames)):
                    print(f"Error: Missing required fields. Need: {required_fields}",
                          file=sys.stderr)
                    return 0, 1, 0
                
                records = list(reader)
            
            standardized_records = []
            for row_num, record in enumerate(records, start=2):  # Start at 2 (after header)
                self.errors = []
                self.warnings = []
                
                standardized = self.standardize_record(record)
                
                if self.errors:
                    error_count += len(self.errors)
                    for error in self.errors:
                        all_errors.append(f"Row {row_num}: {error}")
                
                if self.warnings:
                    warning_count += len(self.warnings)
                    for warning in self.warnings:
                        all_warnings.append(f"Row {row_num}: {warning}")
                
                if not self.errors:  # Only include if no critical errors
                    success_count += 1
                
                standardized_records.append(standardized)
            
            # Write standardized records
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                fieldnames = ['date', 'title', 'object_number', 'link']
                writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(standardized_records)
            
            # Print summary
            print(f"\n{'='*60}")
            print(f"Standardization Complete")
            print(f"{'='*60}")
            print(f"Records processed: {len(records)}")
            print(f"Records standardized successfully: {success_count}")
            print(f"Errors: {error_count}")
            print(f"Warnings: {warning_count}")
            print(f"Output file: {output_file}")
            
            if all_errors:
                print(f"\n{'='*60}")
                print("ERRORS:")
                for error in all_errors[:10]:  # Show first 10
                    print(f"  {error}")
                if len(all_errors) > 10:
                    print(f"  ... and {len(all_errors) - 10} more")
            
            if all_warnings:
                print(f"\n{'='*60}")
                print("WARNINGS:")
                for warning in all_warnings[:10]:  # Show first 10
                    print(f"  {warning}")
                if len(all_warnings) > 10:
                    print(f"  ... and {len(all_warnings) - 10} more")
            
            return success_count, error_count, warning_count
        
        except FileNotFoundError:
            print(f"Error: Input file not found: {input_file}", file=sys.stderr)
            return 0, 1, 0
        except Exception as e:
            print(f"Error processing file: {str(e)}", file=sys.stderr)
            return 0, 1, 0


def create_sample_file():
    """Create a sample TSV file for testing."""
    sample_data = [
        ["date", "title", "object_number", "link"],
        ["01/15/2020", "portrait of lady", "OBJ 001", "www.example.com/obj001"],
        ["2021-03-22", "ANCIENT VASE", "002", "https://museum.org/vase"],
        ["March 10, 2019", "the great painting", "OBJ003", "museum.org/painting"],
        ["2022", "sculpture", "    OBJ 004   ", "http://example.org/sculpture"],
        ["", "mystery object", "OBJ005", ""],
    ]
    
    with open("sample_inventory.tsv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(sample_data)
    
    print("Sample file created: sample_inventory.tsv")


def main():
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory records from TSV file"
    )
    parser.add_argument(
        "input_file",
        help="Input TSV file with inventory records"
    )
    parser.add_argument(
        "-o", "--output",
        default="standardized_inventory.tsv",
        help="Output file for standardized records (default: standardized_inventory.tsv)"
    )
    parser.add_argument(
        "-p", "--prefix",
        default="OBJ",
        help="Object number prefix (default: OBJ)"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Create a sample inventory file and exit"
    )
    
    args = parser.parse_args()
    
    if args.sample:
        create_sample_file()
        return
    
    if not Path(args.input_file).exists():
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    
    standardizer = InventoryStandardizer(object_prefix=args.prefix)
    success, errors, warnings = standardizer.process_file(
        args.input_file,
        args.output
    )
    
    sys.exit(0 if errors == 0 else 1)


if __name__ == "__main__":
    main()
```

## Usage

### Basic usage:
```bash
python standardize_inventory.py inventory.tsv
```

### Specify output file:
```bash
python standardize_inventory.py inventory.tsv -o output.tsv
```

### Custom object number prefix:
```bash
python standardize_inventory.py inventory.tsv -p "MUS"
```

### Create and test with sample file:
```bash
python standardize_inventory.py --sample
python standardize_inventory.py sample_inventory.tsv
```

## Features

- **Date standardization**: Converts multiple date formats to ISO 8601 (YYYY-MM-DD)
- **Title standardization**: Converts to Title Case with appropriate lowercase articles
- **Object number normalization**: Removes spaces, adds prefixes, zero-pads numbers
- **URL validation**: Adds schemes, validates format
- **Error reporting**: Detailed error and warning messages with row numbers
- **Flexible**: Customizable object number prefix

## Input Format

TSV file with columns:
```
date            title               object_number   link
01/15/2020      portrait of lady    OBJ 001        www.example.com/obj001
```
