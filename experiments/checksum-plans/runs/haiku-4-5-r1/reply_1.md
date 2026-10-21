# Museum Inventory Standardizer

Here's a comprehensive Python script that standardizes museum inventory spreadsheets:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer
Standardizes museum inventory .tsv files with columns:
date, title, object_number, and link
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
    
    REQUIRED_COLUMNS = {'date', 'title', 'object_number', 'link'}
    
    def __init__(self, input_file: str, output_file: str = None, verbose: bool = False):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input .tsv file
            output_file: Path to output .tsv file (default: input_standardized.tsv)
            verbose: Print detailed processing information
        """
        self.input_file = Path(input_file)
        self.verbose = verbose
        
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        if output_file is None:
            self.output_file = self.input_file.parent / f"{self.input_file.stem}_standardized.tsv"
        else:
            self.output_file = Path(output_file)
        
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_rows': 0,
            'valid_rows': 0,
            'invalid_rows': 0,
            'standardized_dates': 0,
            'fixed_links': 0,
            'trimmed_titles': 0,
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Print log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def read_inventory(self) -> Tuple[List[str], List[Dict]]:
        """
        Read the TSV inventory file.
        
        Returns:
            Tuple of (fieldnames, rows)
        """
        self.log(f"Reading inventory from {self.input_file}")
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                fieldnames = reader.fieldnames or []
                rows = list(reader)
            
            self.stats['total_rows'] = len(rows)
            self.log(f"Found {len(rows)} rows with columns: {', '.join(fieldnames)}")
            return fieldnames, rows
        
        except Exception as e:
            raise Exception(f"Error reading file: {e}")
    
    def validate_columns(self, fieldnames: List[str]) -> bool:
        """
        Validate that all required columns are present.
        
        Args:
            fieldnames: List of column names from the file
        
        Returns:
            True if valid, False otherwise
        """
        fieldnames_lower = {f.lower().strip() for f in fieldnames}
        missing = self.REQUIRED_COLUMNS - fieldnames_lower
        
        if missing:
            self.errors.append(f"Missing required columns: {', '.join(missing)}")
            return False
        
        self.log("All required columns found")
        return True
    
    def standardize_date(self, date_str: str) -> Tuple[str, bool]:
        """
        Standardize date format to YYYY-MM-DD.
        
        Args:
            date_str: Original date string
        
        Returns:
            Tuple of (standardized_date, was_modified)
        """
        if not date_str or not date_str.strip():
            return "", False
        
        date_str = date_str.strip()
        
        # Common date formats to try
        formats = [
            '%Y-%m-%d',      # Already standard
            '%m/%d/%Y',      # US format
            '%d/%m/%Y',      # EU format
            '%m-%d-%Y',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%B %d, %Y',     # January 1, 2020
            '%b %d, %Y',     # Jan 1, 2020
            '%Y',             # Year only
            '%m/%Y',         # Month/Year
            '%m-%Y',
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                # Return year-only if input was year-only
                if len(date_str) == 4:
                    return parsed.strftime('%Y'), date_str != parsed.strftime('%Y')
                return parsed.strftime('%Y-%m-%d'), date_str != parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matched, keep original and warn
        self.warnings.append(f"Could not parse date: '{date_str}'")
        return date_str, False
    
    def standardize_object_number(self, obj_num: str) -> str:
        """
        Standardize object number format.
        
        Args:
            obj_num: Original object number
        
        Returns:
            Standardized object number
        """
        if not obj_num:
            return ""
        
        # Remove extra whitespace
        obj_num = obj_num.strip()
        
        # Normalize hyphens and separators
        obj_num = re.sub(r'\s+', ' ', obj_num)
        obj_num = re.sub(r'–|—', '-', obj_num)
        
        return obj_num
    
    def standardize_title(self, title: str) -> Tuple[str, bool]:
        """
        Standardize title format.
        
        Args:
            title: Original title
        
        Returns:
            Tuple of (standardized_title, was_modified)
        """
        if not title:
            return "", False
        
        original = title
        
        # Strip whitespace
        title = title.strip()
        
        # Remove multiple spaces
        title = re.sub(r'\s+', ' ', title)
        
        # Standardize quotes
        title = title.replace('"', '"').replace('"', '"')
        title = title.replace(''', "'").replace(''', "'")
        
        was_modified = original != title
        return title, was_modified
    
    def standardize_link(self, link: str) -> Tuple[str, bool]:
        """
        Standardize URL format.
        
        Args:
            link: Original URL/link
        
        Returns:
            Tuple of (standardized_link, was_modified)
        """
        if not link:
            return "", False
        
        original = link
        link = link.strip()
        
        # Add http(s) if missing
        if link and not link.startswith(('http://', 'https://', 'ftp://')):
            if link.startswith('www.'):
                link = 'https://' + link
            elif '.' in link:  # Likely a domain
                link = 'https://' + link
        
        was_modified = original != link
        return link, was_modified
    
    def standardize_row(self, row: Dict, fieldnames: List[str]) -> Dict:
        """
        Standardize a single row of data.
        
        Args:
            row: Dictionary of row data
            fieldnames: List of column names
        
        Returns:
            Standardized row dictionary
        """
        # Find actual column names (case-insensitive)
        col_map = {}
        fieldnames_lower = {f.lower(): f for f in fieldnames}
        
        for req_col in self.REQUIRED_COLUMNS:
            col_map[req_col] = fieldnames_lower.get(req_col.lower(), req_col)
        
        standardized = {}
        
        # Standardize each column
        # Date
        date_col = col_map['date']
        date_val, modified = self.standardize_date(row.get(date_col, ''))
        standardized['date'] = date_val
        if modified:
            self.stats['standardized_dates'] += 1
        
        # Title
        title_col = col_map['title']
        title_val, modified = self.standardize_title(row.get(title_col, ''))
        standardized['title'] = title_val
        if modified:
            self.stats['trimmed_titles'] += 1
        
        # Object Number
        obj_col = col_map['object_number']
        standardized['object_number'] = self.standardize_object_number(
            row.get(obj_col, '')
        )
        
        # Link
        link_col = col_map['link']
        link_val, modified = self.standardize_link(row.get(link_col, ''))
        standardized['link'] = link_val
        if modified:
            self.stats['fixed_links'] += 1
        
        return standardized
    
    def validate_row(self, row: Dict) -> bool:
        """
        Validate that a row has minimum required data.
        
        Args:
            row: Standardized row dictionary
        
        Returns:
            True if valid, False otherwise
        """
        # At minimum, title and object_number should be present
        if not row.get('title', '').strip():
            return False
        if not row.get('object_number', '').strip():
            return False
        
        return True
    
    def process(self) -> bool:
        """
        Process the inventory file and create standardized output.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read file
            fieldnames, rows = self.read_inventory()
            
            # Validate columns
            if not self.validate_columns(fieldnames):
                return False
            
            # Standardize rows
            standardized_rows = []
            for i, row in enumerate(rows, 1):
                try:
                    standardized = self.standardize_row(row, fieldnames)
                    
                    if self.validate_row(standardized):
                        standardized_rows.append(standardized)
                        self.stats['valid_rows'] += 1
                    else:
                        self.stats['invalid_rows'] += 1
                        self.log(f"Row {i}: Skipped invalid row", "WARNING")
                
                except Exception as e:
                    self.stats['invalid_rows'] += 1
                    self.log(f"Row {i}: {e}", "ERROR")
            
            # Write output file
            self.write_inventory(standardized_rows)
            return True
        
        except Exception as e:
            self.errors.append(str(e))
            return False
    
    def write_inventory(self, rows: List[Dict]) -> None:
        """
        Write standardized inventory to output file.
        
        Args:
            rows: List of standardized row dictionaries
        """
        self.log(f"Writing standardized inventory to {self.output_file}")
        
        fieldnames = ['date', 'title', 'object_number', 'link']
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            writer.writerows(rows)
        
        self.log(f"Successfully wrote {len(rows)} rows")
    
    def print_report(self) -> None:
        """Print standardization report."""
        print("\n" + "="*60)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("="*60)
        print(f"\nInput file:  {self.input_file}")
        print(f"Output file: {self.output_file}")
        print(f"\nStatistics:")
        print(f"  Total rows processed:     {self.stats['total_rows']}")
        print(f"  Valid rows:               {self.stats['valid_rows']}")
        print(f"  Invalid rows (skipped):   {self.stats['invalid_rows']}")
        print(f"  Standardized dates:       {self.stats['standardized_dates']}")
        print(f"  Fixed URLs:               {self.stats['fixed_links']}")
        print(f"  Trimmed titles:           {self.stats['trimmed_titles']}")
        
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        print("\n" + "="*60 + "\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory spreadsheets (.tsv)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python standardizer.py inventory.tsv
  python standardizer.py inventory.tsv -o standardized.tsv -v
        """
    )
    
    parser.add_argument('input_file', help='Input .tsv file path')
    parser.add_argument('-o', '--output', dest='output_file', 
                       help='Output .tsv file path (default: input_standardized.tsv)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Print detailed processing information')
    
    args = parser.parse_args()
    
    try:
        standardizer = InventoryStandardizer(
            input_file=args.input_file,
            output_file=args.output_file,
            verbose=args.verbose
        )
        
        success = standardizer.process()
        standardizer.print_report()
        
        sys.exit(0 if success else 1)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## Usage

```bash
# Basic usage
python standardizer.py inventory.tsv

# With custom output file
python standardizer.py inventory.tsv -o output.tsv

# Verbose mode for detailed output
python standardizer.py inventory.tsv -v

# Get help
python standardizer.py --help
```

## Features

- **Date Standardization**: Converts various date formats to YYYY-MM-DD
- **Title Cleaning**: Removes extra whitespace, normalizes quotes
- **Object Number Formatting**: Standardizes separators and spacing
- **URL Validation**: Adds protocol if missing, cleans formatting
- **Error Handling**: Skips invalid rows while reporting issues
- **Detailed Reporting**: Shows statistics and warnings
- **Case-Insensitive**: Works with any capitalization of column headers

## Sample Input

```tsv
Date	Title	Object Number	Link
1/15/2023	Ancient Vase	2023.001.A	www.museum.org/item1
2023-02-20	Medieval Sword	2023-002-B	https://museum.org/item2
03/10/2022	Modern Sculpture	2022.003.C	museum.org/item3
```

## Sample Output

```tsv
date	title	object_number	link
2023-01-15	Ancient Vase	2023.001.A	https://www.museum.org/item1
2023-02-20	Medieval Sword	2023-002-B	https://museum.org/item2
2022-03-10	Modern Sculpture	2022.003.C	https://museum.org/item3
```
