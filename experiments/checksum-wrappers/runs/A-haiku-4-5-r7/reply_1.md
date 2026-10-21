# Museum Inventory Standardizer

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory spreadsheets (.tsv format).
Validates and cleans: date, title, object number, and link columns.
"""

import sys
import csv
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import re


class InventoryStandardizer:
    """Standardizes museum inventory data."""
    
    REQUIRED_COLUMNS = ['date', 'title', 'object_number', 'link']
    
    def __init__(self, input_file, output_file=None, strict=False):
        """
        Initialize standardizer.
        
        Args:
            input_file: Path to input .tsv file
            output_file: Path to output .tsv file (default: input_standardized.tsv)
            strict: If True, skip invalid rows instead of attempting fixes
        """
        self.input_file = Path(input_file)
        self.strict = strict
        
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        if output_file is None:
            output_file = self.input_file.stem + "_standardized.tsv"
        
        self.output_file = Path(output_file)
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_rows': 0,
            'valid_rows': 0,
            'skipped_rows': 0,
            'fixed_rows': 0
        }
    
    def standardize_date(self, date_str, row_num):
        """
        Standardize date to ISO format (YYYY-MM-DD).
        
        Args:
            date_str: Date string in various formats
            row_num: Row number for error reporting
            
        Returns:
            Standardized date string or None if invalid
        """
        if not date_str or date_str.strip() == '':
            self.warnings.append(f"Row {row_num}: Empty date field")
            return None
        
        date_str = date_str.strip()
        
        # Try common date formats
        formats = [
            '%Y-%m-%d',      # ISO format
            '%m/%d/%Y',      # US format
            '%d/%m/%Y',      # EU format
            '%Y/%m/%d',      # Alternative ISO
            '%B %d, %Y',     # Full month name
            '%b %d, %Y',     # Abbreviated month
            '%Y-%m',         # Year-month only
            '%Y',            # Year only
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        self.errors.append(f"Row {row_num}: Invalid date format: '{date_str}'")
        return None
    
    def standardize_title(self, title, row_num):
        """
        Standardize title (trim whitespace, normalize spacing).
        
        Args:
            title: Title string
            row_num: Row number for error reporting
            
        Returns:
            Standardized title string
        """
        if not title or title.strip() == '':
            self.errors.append(f"Row {row_num}: Empty title field")
            return None
        
        # Clean up whitespace
        title = ' '.join(title.split())
        
        # Basic validation
        if len(title) < 3:
            self.errors.append(f"Row {row_num}: Title too short: '{title}'")
            return None
        
        if len(title) > 500:
            self.warnings.append(f"Row {row_num}: Title exceeds 500 chars, truncating")
            title = title[:500]
        
        return title
    
    def standardize_object_number(self, obj_num, row_num):
        """
        Standardize object number (remove extra whitespace, validate format).
        
        Args:
            obj_num: Object number string
            row_num: Row number for error reporting
            
        Returns:
            Standardized object number or None if invalid
        """
        if not obj_num or obj_num.strip() == '':
            self.errors.append(f"Row {row_num}: Empty object number field")
            return None
        
        obj_num = obj_num.strip().upper()
        
        # Remove extra spaces
        obj_num = re.sub(r'\s+', ' ', obj_num)
        
        # Validate format (alphanumeric, spaces, hyphens, periods)
        if not re.match(r'^[A-Z0-9\s\.\-]+$', obj_num):
            self.errors.append(
                f"Row {row_num}: Invalid object number format: '{obj_num}'"
            )
            return None
        
        return obj_num
    
    def standardize_link(self, link, row_num):
        """
        Standardize link (validate URL format).
        
        Args:
            link: URL string
            row_num: Row number for error reporting
            
        Returns:
            Standardized URL or empty string if invalid
        """
        if not link or link.strip() == '':
            self.warnings.append(f"Row {row_num}: Empty link field")
            return ''
        
        link = link.strip()
        
        # Add protocol if missing
        if not link.startswith(('http://', 'https://')):
            link = 'https://' + link
        
        # Validate URL structure
        try:
            result = urlparse(link)
            if not all([result.scheme, result.netloc]):
                self.errors.append(f"Row {row_num}: Invalid URL: '{link}'")
                return None
        except Exception as e:
            self.errors.append(f"Row {row_num}: URL parsing error: {e}")
            return None
        
        return link
    
    def process_row(self, row, row_num):
        """
        Process and standardize a single row.
        
        Args:
            row: Dictionary with row data
            row_num: Row number for error reporting
            
        Returns:
            Standardized row dictionary or None if invalid
        """
        self.stats['total_rows'] += 1
        
        try:
            standardized = {}
            
            # Process each field
            standardized['date'] = self.standardize_date(row.get('date', ''), row_num)
            standardized['title'] = self.standardize_title(row.get('title', ''), row_num)
            standardized['object_number'] = self.standardize_object_number(
                row.get('object_number', ''), row_num
            )
            standardized['link'] = self.standardize_link(row.get('link', ''), row_num)
            
            # Check for critical errors
            if None in standardized.values():
                if self.strict:
                    self.stats['skipped_rows'] += 1
                    return None
                else:
                    # Fill None values with empty strings
                    standardized = {k: v if v is not None else '' for k, v in standardized.items()}
                    self.stats['fixed_rows'] += 1
            else:
                self.stats['valid_rows'] += 1
            
            return standardized
        
        except Exception as e:
            self.errors.append(f"Row {row_num}: Unexpected error: {e}")
            self.stats['skipped_rows'] += 1
            return None
    
    def run(self):
        """Process the inventory file and write standardized output."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile, delimiter='\t')
                
                # Validate column headers
                if not reader.fieldnames:
                    raise ValueError("Empty file or invalid format")
                
                missing_cols = set(self.REQUIRED_COLUMNS) - set(reader.fieldnames or [])
                if missing_cols:
                    raise ValueError(f"Missing required columns: {missing_cols}")
                
                # Process rows
                standardized_rows = []
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                    standardized_row = self.process_row(row, row_num)
                    if standardized_row:
                        standardized_rows.append(standardized_row)
            
            # Write output
            with open(self.output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(
                    outfile,
                    fieldnames=self.REQUIRED_COLUMNS,
                    delimiter='\t'
                )
                writer.writeheader()
                writer.writerows(standardized_rows)
            
            self.print_report()
            return True
        
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return False
    
    def print_report(self):
        """Print standardization report."""
        print("\n" + "="*60)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("="*60)
        print(f"Input file:  {self.input_file}")
        print(f"Output file: {self.output_file}")
        print("-"*60)
        print(f"Total rows processed:    {self.stats['total_rows']}")
        print(f"Valid rows:              {self.stats['valid_rows']}")
        print(f"Fixed rows:              {self.stats['fixed_rows']}")
        print(f"Skipped rows:            {self.stats['skipped_rows']}")
        print("-"*60)
        
        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  • {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        if self.errors:
            print(f"\nERRORS ({len(self.errors)}):")
            for error in self.errors[:10]:  # Show first 10
                print(f"  • {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        
        print("="*60 + "\n")


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file.tsv> [output_file.tsv] [--strict]")
        print("\nOptions:")
        print("  --strict    Skip invalid rows instead of attempting fixes")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    strict = '--strict' in sys.argv
    
    standardizer = InventoryStandardizer(input_file, output_file, strict=strict)
    success = standardizer.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Usage

### Basic usage:
```bash
python standardizer.py inventory.tsv
```

### Specify output file:
```bash
python standardizer.py inventory.tsv inventory_clean.tsv
```

### Strict mode (skip invalid rows):
```bash
python standardizer.py inventory.tsv --strict
```

## Features

- **Date standardization**: Converts multiple date formats to ISO (YYYY-MM-DD)
- **Title cleaning**: Trims whitespace, validates length (3-500 chars)
- **Object number validation**: Enforces alphanumeric format with hyphens/periods
- **URL validation**: Checks format and adds https:// if missing
- **Error reporting**: Detailed warnings and errors with row numbers
- **Statistics**: Summary of processed rows
- **Flexible**: Fixes minor issues by default, strict mode available

## Example Input

```
date	title	object_number	link
01/15/2023	Ancient Vase	ARK-2023-001	www.museum.org/item/1
2023-02-20	Roman Coin	COIN.2023.002	https://example.com/coin
```

## Example Output

```
date	title	object_number	link
2023-01-15	Ancient Vase	ARK-2023-001	https://www.museum.org/item/1
2023-02-20	Roman Coin	COIN.2023.002	https://example.com/coin
```
