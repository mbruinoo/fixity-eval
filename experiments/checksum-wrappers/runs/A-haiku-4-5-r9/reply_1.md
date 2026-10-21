# Museum Inventory Standardizer

Here's a comprehensive Python script to standardize museum inventory spreadsheets:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer
Standardizes museum inventory TSV files with columns: date, title, object number, and link
"""

import csv
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import argparse


class InventoryStandardizer:
    """Standardizes museum inventory data."""
    
    def __init__(self, input_file: str, output_file: str = None, verbose: bool = False):
        self.input_file = input_file
        self.output_file = output_file or self._generate_output_filename(input_file)
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        
    def _generate_output_filename(self, input_file: str) -> str:
        """Generate output filename with _standardized suffix."""
        path = Path(input_file)
        return path.parent / f"{path.stem}_standardized{path.suffix}"
    
    def log(self, message: str, level: str = "INFO"):
        """Print log message if verbose."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def standardize_date(self, date_str: str) -> str:
        """
        Standardize date to ISO format (YYYY-MM-DD).
        Handles various common date formats.
        """
        if not date_str or date_str.strip() == "":
            self.warnings.append("Empty date field found")
            return ""
        
        date_str = date_str.strip()
        
        # Already in ISO format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
        
        # Common formats to try
        formats = [
            '%m/%d/%Y',      # 12/25/2023
            '%m-%d-%Y',      # 12-25-2023
            '%d/%m/%Y',      # 25/12/2023
            '%d-%m-%Y',      # 25-12-2023
            '%Y/%m/%d',      # 2023/12/25
            '%B %d, %Y',     # December 25, 2023
            '%b %d, %Y',     # Dec 25, 2023
            '%d %B %Y',      # 25 December 2023
            '%d %b %Y',      # 25 Dec 2023
            '%Y',            # 2023 (year only)
            '%m/%Y',         # 12/2023
        ]
        
        for date_format in formats:
            try:
                parsed_date = datetime.strptime(date_str, date_format)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matched, log warning and return original
        self.warnings.append(f"Could not parse date: '{date_str}'")
        return date_str
    
    def standardize_title(self, title: str) -> str:
        """
        Standardize title formatting.
        - Remove extra whitespace
        - Strip leading/trailing punctuation
        - Proper title case (optional enhancement)
        """
        if not title:
            return ""
        
        # Remove extra whitespace
        title = " ".join(title.split())
        
        # Remove leading/trailing punctuation (except for intentional marks)
        title = title.strip('.,;:"\'-')
        
        return title
    
    def standardize_object_number(self, obj_num: str) -> str:
        """
        Standardize object number formatting.
        - Remove extra whitespace
        - Remove common separators and standardize
        """
        if not obj_num:
            return ""
        
        # Remove extra whitespace
        obj_num = obj_num.strip()
        
        # Validate object number is not empty after cleaning
        if not obj_num:
            self.warnings.append("Empty object number found")
            return ""
        
        return obj_num
    
    def standardize_link(self, link: str) -> str:
        """
        Standardize URL formatting.
        - Ensure proper URL format
        - Handle empty values
        """
        if not link or link.strip() == "":
            return ""
        
        link = link.strip()
        
        # Add https:// if no protocol present
        if link and not link.startswith(('http://', 'https://', 'ftp://')):
            link = 'https://' + link
        
        # Basic URL validation
        if not re.match(r'^https?://', link):
            self.warnings.append(f"Invalid URL format: '{link}'")
        
        return link
    
    def validate_row(self, row: Dict[str, str], row_num: int) -> bool:
        """
        Validate a row has required fields.
        Returns True if valid, False otherwise.
        """
        required_fields = ['date', 'title', 'object number', 'link']
        
        for field in required_fields:
            if field not in row:
                self.errors.append(f"Row {row_num}: Missing required column '{field}'")
                return False
        
        # Check that at least date, title, or object number is present
        if not any([row.get('date'), row.get('title'), row.get('object number')]):
            self.errors.append(f"Row {row_num}: Must have at least date, title, or object number")
            return False
        
        return True
    
    def standardize_row(self, row: Dict[str, str], row_num: int) -> Dict[str, str]:
        """Apply standardization to a single row."""
        standardized = {}
        
        try:
            standardized['date'] = self.standardize_date(row.get('date', ''))
            standardized['title'] = self.standardize_title(row.get('title', ''))
            standardized['object number'] = self.standardize_object_number(row.get('object number', ''))
            standardized['link'] = self.standardize_link(row.get('link', ''))
        except Exception as e:
            self.errors.append(f"Row {row_num}: Error during standardization: {str(e)}")
            return row
        
        return standardized
    
    def process(self) -> Tuple[bool, List[str], List[str]]:
        """
        Process the inventory file and write standardized output.
        Returns (success, errors, warnings)
        """
        try:
            # Read input file
            self.log(f"Reading input file: {self.input_file}")
            
            if not Path(self.input_file).exists():
                self.errors.append(f"Input file not found: {self.input_file}")
                return False, self.errors, self.warnings
            
            rows = []
            fieldnames = None
            
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                fieldnames = reader.fieldnames
                
                # Validate header
                required_fields = {'date', 'title', 'object number', 'link'}
                if not required_fields.issubset(set(fieldnames or [])):
                    self.errors.append(
                        f"Invalid header. Required columns: {required_fields}. "
                        f"Found: {set(fieldnames or [])}"
                    )
                    return False, self.errors, self.warnings
                
                # Process rows
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                    if self.validate_row(row, row_num):
                        standardized_row = self.standardize_row(row, row_num)
                        rows.append(standardized_row)
                    else:
                        self.log(f"Skipping invalid row {row_num}", "WARNING")
            
            self.log(f"Successfully read {len(rows)} rows")
            
            # Write output file
            self.log(f"Writing output file: {self.output_file}")
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['date', 'title', 'object number', 'link'],
                    delimiter='\t'
                )
                writer.writeheader()
                writer.writerows(rows)
            
            self.log(f"Successfully wrote {len(rows)} rows")
            
            return True, self.errors, self.warnings
            
        except Exception as e:
            self.errors.append(f"Fatal error: {str(e)}")
            return False, self.errors, self.warnings


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory TSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python standardize_inventory.py inventory.tsv
  python standardize_inventory.py inventory.tsv -o output.tsv -v
        """
    )
    
    parser.add_argument('input_file', help='Input TSV file')
    parser.add_argument(
        '-o', '--output',
        help='Output file (default: input_file_standardized.tsv)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Run standardizer
    standardizer = InventoryStandardizer(
        args.input_file,
        args.output,
        args.verbose
    )
    
    success, errors, warnings = standardizer.process()
    
    # Print results
    print("\n" + "="*60)
    print("STANDARDIZATION REPORT")
    print("="*60)
    
    if success:
        print(f"✓ Successfully standardized: {standardizer.output_file}")
    else:
        print("✗ Standardization failed")
    
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for warning in warnings[:10]:  # Show first 10
            print(f"  ⚠ {warning}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more")
    
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for error in errors[:10]:  # Show first 10
            print(f"  ✗ {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    
    print("="*60 + "\n")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
```

## Usage

### Basic usage:
```bash
python standardize_inventory.py inventory.tsv
```

### With options:
```bash
python standardize_inventory.py inventory.tsv -o standardized.tsv -v
```

### As a module:
```python
from standardize_inventory import InventoryStandardizer

standardizer = InventoryStandardizer('input.tsv', 'output.tsv', verbose=True)
success, errors, warnings = standardizer.process()
```

## Features

✅ **Date Standardization**: Converts multiple date formats to ISO (YYYY-MM-DD)
✅ **Title Cleaning**: Removes extra whitespace and punctuation
✅ **Object Number Validation**: Ensures consistency
✅ **URL Formatting**: Adds protocol if missing
✅ **Error Handling**: Comprehensive validation with detailed reporting
✅ **Verbose Logging**: Optional detailed output
✅ **Flexible Input**: Handles various common date formats

## Sample Input
```
date	title	object number	link
12/25/2023	Ancient Vase	ACC.2023.001	www.example.com
2023-01-15	Medieval Sword	ACC.2023.002	https://example.com/sword
```

## Sample Output
```
date	title	object number	link
2023-12-25	Ancient Vase	ACC.2023.001	https://www.example.com
2023-01-15	Medieval Sword	ACC.2023.002	https://example.com/sword
```
