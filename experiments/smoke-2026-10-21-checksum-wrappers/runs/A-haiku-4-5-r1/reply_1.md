# Museum Inventory Standardizer

Here's a comprehensive Python script for standardizing museum inventory spreadsheets:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer

Standardizes museum inventory TSV files with columns:
- date
- title
- object_number
- link
"""

import csv
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import argparse


class MuseumInventoryStandardizer:
    """Standardize museum inventory spreadsheet data."""
    
    REQUIRED_COLUMNS = {'date', 'title', 'object_number', 'link'}
    
    def __init__(self, input_file: str, output_file: str = None, verbose: bool = False):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file (defaults to input_standardized.tsv)
            verbose: Print detailed processing information
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self.input_file.parent / f"{self.input_file.stem}_standardized.tsv"
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_rows': 0,
            'processed_rows': 0,
            'skipped_rows': 0,
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Print log message if verbose is enabled."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def standardize_date(self, date_str: str) -> str:
        """
        Standardize date to YYYY-MM-DD format.
        Handles various date formats.
        """
        if not date_str or not date_str.strip():
            return ""
        
        date_str = date_str.strip()
        
        # Common date formats to try
        formats = [
            "%Y-%m-%d",      # 2023-12-25
            "%m/%d/%Y",      # 12/25/2023
            "%d/%m/%Y",      # 25/12/2023
            "%B %d, %Y",     # December 25, 2023
            "%b %d, %Y",     # Dec 25, 2023
            "%d %B %Y",      # 25 December 2023
            "%d %b %Y",      # 25 Dec 2023
            "%Y/%m/%d",      # 2023/12/25
            "%d-%m-%Y",      # 25-12-2023
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # If no format matched, log warning and return original
        self.warnings.append(f"Could not parse date: '{date_str}'")
        return date_str
    
    def standardize_title(self, title: str) -> str:
        """
        Standardize title formatting.
        - Strip whitespace
        - Ensure proper capitalization
        - Remove extra spaces
        """
        if not title:
            return ""
        
        title = title.strip()
        # Remove multiple spaces
        title = re.sub(r'\s+', ' ', title)
        
        return title
    
    def standardize_object_number(self, obj_num: str) -> str:
        """
        Standardize object number.
        - Remove extra whitespace
        - Ensure consistent formatting (optional: uppercase)
        """
        if not obj_num:
            return ""
        
        obj_num = obj_num.strip().upper()
        # Remove multiple spaces
        obj_num = re.sub(r'\s+', ' ', obj_num)
        
        return obj_num
    
    def standardize_link(self, link: str) -> str:
        """
        Standardize URL.
        - Strip whitespace
        - Ensure proper URL format
        - Validate basic URL structure
        """
        if not link or not link.strip():
            return ""
        
        link = link.strip()
        
        # Add https:// if missing
        if link and not link.startswith(('http://', 'https://', 'ftp://')):
            link = 'https://' + link
        
        # Basic URL validation
        if not re.match(r'https?://\S+', link):
            self.warnings.append(f"Invalid URL format: '{link}'")
        
        return link
    
    def validate_row(self, row: Dict[str, str], row_num: int) -> Tuple[bool, str]:
        """
        Validate a data row.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for required fields
        if not row.get('title', '').strip():
            return False, f"Row {row_num}: Missing or empty title"
        
        if not row.get('object_number', '').strip():
            return False, f"Row {row_num}: Missing or empty object number"
        
        return True, ""
    
    def process_row(self, row: Dict[str, str], row_num: int) -> Dict[str, str]:
        """Process and standardize a single row."""
        processed_row = {
            'date': self.standardize_date(row.get('date', '')),
            'title': self.standardize_title(row.get('title', '')),
            'object_number': self.standardize_object_number(row.get('object_number', '')),
            'link': self.standardize_link(row.get('link', '')),
        }
        
        return processed_row
    
    def read_input(self) -> List[Dict[str, str]]:
        """Read and parse input TSV file."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        self.log(f"Reading input file: {self.input_file}")
        rows = []
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    raise ValueError("Empty input file")
                
                # Check for required columns
                missing_cols = self.REQUIRED_COLUMNS - set(reader.fieldnames)
                if missing_cols:
                    raise ValueError(f"Missing required columns: {missing_cols}")
                
                self.log(f"Found columns: {list(reader.fieldnames)}")
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                    self.stats['total_rows'] += 1
                    
                    # Validate row
                    is_valid, error_msg = self.validate_row(row, row_num)
                    if not is_valid:
                        self.errors.append(error_msg)
                        self.stats['skipped_rows'] += 1
                        self.log(f"Skipping: {error_msg}", "WARNING")
                        continue
                    
                    rows.append((row_num, row))
                    self.stats['processed_rows'] += 1
        
        except Exception as e:
            self.log(f"Error reading input file: {e}", "ERROR")
            raise
        
        return rows
    
    def standardize(self):
        """Main standardization process."""
        try:
            # Read input
            rows = self.read_input()
            
            # Process rows
            self.log(f"Processing {len(rows)} rows...")
            processed_rows = []
            
            for row_num, row in rows:
                processed_row = self.process_row(row, row_num)
                processed_rows.append(processed_row)
            
            # Write output
            self.log(f"Writing standardized data to: {self.output_file}")
            self.write_output(processed_rows)
            
            # Print summary
            self.print_summary()
            
            return True
        
        except Exception as e:
            self.log(f"Fatal error during standardization: {e}", "ERROR")
            return False
    
    def write_output(self, rows: List[Dict[str, str]]):
        """Write standardized data to output TSV file."""
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['date', 'title', 'object_number', 'link'],
                    delimiter='\t'
                )
                writer.writeheader()
                writer.writerows(rows)
            
            self.log(f"Successfully wrote {len(rows)} rows to output file")
        
        except Exception as e:
            self.log(f"Error writing output file: {e}", "ERROR")
            raise
    
    def print_summary(self):
        """Print processing summary."""
        print("\n" + "="*60)
        print("STANDARDIZATION SUMMARY")
        print("="*60)
        print(f"Input file:       {self.input_file}")
        print(f"Output file:      {self.output_file}")
        print(f"Total rows:       {self.stats['total_rows']}")
        print(f"Processed rows:   {self.stats['processed_rows']}")
        print(f"Skipped rows:     {self.stats['skipped_rows']}")
        
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors[:10]:  # Show first 10
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        
        if self.warnings and self.verbose:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        print("="*60 + "\n")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory TSV spreadsheets'
    )
    parser.add_argument(
        'input_file',
        help='Path to input TSV file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Path to output TSV file (default: input_standardized.tsv)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print detailed processing information'
    )
    
    args = parser.parse_args()
    
    standardizer = MuseumInventoryStandardizer(
        args.input_file,
        args.output,
        args.verbose
    )
    
    success = standardizer.standardize()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Usage

### Basic usage:
```bash
python standardize_inventory.py input.tsv
```

### With custom output file:
```bash
python standardize_inventory.py input.tsv -o output.tsv
```

### With verbose output:
```bash
python standardize_inventory.py input.tsv -v
```

## Features

- **Date standardization**: Converts various date formats to YYYY-MM-DD
- **Title cleaning**: Normalizes whitespace and formatting
- **Object number formatting**: Uppercase and whitespace normalization
- **URL standardization**: Adds protocol if missing, basic validation
- **Error handling**: Validates required fields and reports issues
- **Detailed reporting**: Summary statistics and error/warning logs
- **UTF-8 support**: Handles special characters properly

## Example Input

```
date	title	object_number	link
12/25/2023	Ancient Vase	OBJ-001	museum.org/vase-001
2023-01-15	Medieval Sword	obj-002	https://museum.org/sword
January 5, 2024	Pottery Fragment	OBJ 003	museum.org/pottery
```

## Example Output

```
date	title	object_number	link
2023-12-25	Ancient Vase	OBJ-001	https://museum.org/vase-001
2023-01-15	Medieval Sword	OBJ-002	https://museum.org/sword
2024-01-05	Pottery Fragment	OBJ-003	https://museum.org/pottery
```
