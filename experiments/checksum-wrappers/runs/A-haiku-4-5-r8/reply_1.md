# Museum Inventory Standardizer

Here's a comprehensive Python script to standardize a museum inventory TSV file:

```python
#!/usr/bin/env python3
"""
Museum Inventory Spreadsheet Standardizer
Standardizes TSV files with: date, title, object number, and link columns
"""

import argparse
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict
import csv


class InventoryStandardizer:
    """Standardizes museum inventory spreadsheets."""
    
    # Expected columns in order
    EXPECTED_COLUMNS = ['date', 'title', 'object_number', 'link']
    
    def __init__(self, input_file: str, output_file: str = None, strict: bool = False):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file (defaults to input_file with _standardized suffix)
            strict: If True, fail on any issues; if False, warn and continue
        """
        self.input_file = Path(input_file)
        self.strict = strict
        self.errors = []
        self.warnings = []
        
        if output_file is None:
            self.output_file = self.input_file.parent / f"{self.input_file.stem}_standardized.tsv"
        else:
            self.output_file = Path(output_file)
    
    def validate_file_exists(self) -> bool:
        """Check if input file exists."""
        if not self.input_file.exists():
            self.errors.append(f"Input file not found: {self.input_file}")
            return False
        return True
    
    def read_file(self) -> Tuple[List[str], List[Dict]]:
        """
        Read TSV file and return headers and rows.
        
        Returns:
            Tuple of (headers, rows)
        """
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                headers = reader.fieldnames
                rows = list(reader)
            return headers, rows
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return None, None
    
    def standardize_column_names(self, headers: List[str]) -> List[str]:
        """
        Standardize column names to lowercase with underscores.
        Maps common variations to standard names.
        """
        mapping = {
            'date': ['date', 'acquisition date', 'date acquired', 'accession date'],
            'title': ['title', 'name', 'object name', 'description'],
            'object_number': ['object number', 'object_number', 'accession number', 'catalog number', 'id', 'object id'],
            'link': ['link', 'url', 'reference', 'webpage', 'web link']
        }
        
        standardized = []
        found_columns = {col: False for col in self.EXPECTED_COLUMNS}
        
        for header in headers:
            header_lower = header.lower().strip()
            matched = False
            
            for standard_name, variations in mapping.items():
                if header_lower in variations:
                    standardized.append(standard_name)
                    found_columns[standard_name] = True
                    matched = True
                    if header != standard_name:
                        self.warnings.append(f"Renamed column '{header}' -> '{standard_name}'")
                    break
            
            if not matched:
                self.warnings.append(f"Unknown column '{header}' - will be preserved")
                standardized.append(header_lower.replace(' ', '_'))
        
        # Check for missing required columns
        missing = [col for col in self.EXPECTED_COLUMNS if not found_columns[col]]
        if missing:
            msg = f"Missing required columns: {', '.join(missing)}"
            if self.strict:
                self.errors.append(msg)
            else:
                self.warnings.append(msg)
        
        return standardized
    
    def standardize_date(self, date_str: str) -> str:
        """
        Standardize date to YYYY-MM-DD format.
        Attempts to parse various date formats.
        """
        if not date_str or not date_str.strip():
            return ""
        
        date_str = date_str.strip()
        
        # Try common date formats
        formats = [
            '%Y-%m-%d',      # 2023-01-15
            '%m/%d/%Y',      # 01/15/2023
            '%d/%m/%Y',      # 15/01/2023
            '%Y/%m/%d',      # 2023/01/15
            '%m-%d-%Y',      # 01-15-2023
            '%d-%m-%Y',      # 15-01-2023
            '%B %d, %Y',     # January 15, 2023
            '%b %d, %Y',     # Jan 15, 2023
            '%Y',            # 2023
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matched, keep original and warn
        self.warnings.append(f"Could not parse date '{date_str}' - keeping original")
        return date_str
    
    def standardize_title(self, title: str) -> str:
        """
        Standardize title: trim whitespace, proper capitalization.
        """
        if not title:
            return ""
        
        title = title.strip()
        # Title case (capitalize each word)
        title = ' '.join(word.capitalize() for word in title.split())
        return title
    
    def standardize_object_number(self, obj_num: str) -> str:
        """
        Standardize object number: remove extra spaces, uppercase.
        """
        if not obj_num:
            return ""
        
        # Remove extra whitespace
        obj_num = ' '.join(obj_num.split()).strip()
        return obj_num
    
    def standardize_link(self, link: str) -> str:
        """
        Standardize link: trim whitespace, validate URL format.
        """
        if not link:
            return ""
        
        link = link.strip()
        
        # Basic URL validation
        if link and not link.startswith(('http://', 'https://', 'ftp://')):
            self.warnings.append(f"Link missing protocol: '{link}'")
            # Don't modify - let user decide
        
        return link
    
    def standardize_row(self, row: Dict, headers: List[str]) -> Dict:
        """
        Standardize a single row of data.
        """
        standardized = {}
        
        for header in headers:
            value = row.get(header, "")
            
            if header == 'date':
                standardized[header] = self.standardize_date(value)
            elif header == 'title':
                standardized[header] = self.standardize_title(value)
            elif header == 'object_number':
                standardized[header] = self.standardize_object_number(value)
            elif header == 'link':
                standardized[header] = self.standardize_link(value)
            else:
                standardized[header] = value.strip() if isinstance(value, str) else value
        
        return standardized
    
    def remove_duplicates(self, rows: List[Dict]) -> Tuple[List[Dict], int]:
        """
        Remove duplicate rows based on object_number.
        Returns cleaned rows and number of duplicates removed.
        """
        seen = set()
        cleaned = []
        duplicates = 0
        
        for row in rows:
            obj_num = row.get('object_number', '')
            if obj_num and obj_num in seen:
                duplicates += 1
                self.warnings.append(f"Duplicate object_number removed: '{obj_num}'")
            else:
                if obj_num:
                    seen.add(obj_num)
                cleaned.append(row)
        
        return cleaned, duplicates
    
    def validate_rows(self, rows: List[Dict]) -> int:
        """
        Validate rows for missing required fields.
        Returns number of validation errors.
        """
        errors_found = 0
        
        for i, row in enumerate(rows, 1):
            # Check for missing object_number (unique identifier)
            if not row.get('object_number', '').strip():
                msg = f"Row {i}: Missing object_number"
                errors_found += 1
                if self.strict:
                    self.errors.append(msg)
                else:
                    self.warnings.append(msg)
        
        return errors_found
    
    def write_file(self, rows: List[Dict], headers: List[str]) -> bool:
        """Write standardized data to output file."""
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers, delimiter='\t')
                writer.writeheader()
                writer.writerows(rows)
            return True
        except Exception as e:
            self.errors.append(f"Error writing output file: {e}")
            return False
    
    def run(self) -> bool:
        """
        Execute the standardization process.
        Returns True if successful, False otherwise.
        """
        # Validate input file exists
        if not self.validate_file_exists():
            return False
        
        # Read file
        headers, rows = self.read_file()
        if headers is None:
            return False
        
        print(f"Read {len(rows)} rows from {self.input_file}")
        
        # Standardize column names
        headers = self.standardize_column_names(headers)
        
        # Standardize each row
        standardized_rows = [self.standardize_row(row, headers) for row in rows]
        
        # Remove duplicates
        standardized_rows, duplicates_removed = self.remove_duplicates(standardized_rows)
        
        # Validate rows
        validation_errors = self.validate_rows(standardized_rows)
        
        # Write output
        if not self.write_file(standardized_rows, headers):
            return False
        
        print(f"Successfully standardized {len(standardized_rows)} rows")
        if duplicates_removed:
            print(f"Removed {duplicates_removed} duplicate entries")
        
        return True
    
    def print_report(self):
        """Print standardization report."""
        print("\n" + "="*60)
        print("STANDARDIZATION REPORT")
        print("="*60)
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  • {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if not self.warnings and not self.errors:
            print("\n✅ No issues found!")
        
        print(f"\nOutput file: {self.output_file}")
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory TSV files'
    )
    parser.add_argument(
        'input',
        help='Input TSV file path'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output TSV file path (default: input_standardized.tsv)'
    )
    parser.add_argument(
        '-s', '--strict',
        action='store_true',
        help='Fail on any issues (not just warnings)'
    )
    
    args = parser.parse_args()
    
    standardizer = InventoryStandardizer(args.input, args.output, args.strict)
    success = standardizer.run()
    standardizer.print_report()
    
    sys.exit(0 if success and not (args.strict and standardizer.errors) else 1)


if __name__ == '__main__':
    main()
```

## Usage Examples

**Basic usage:**
```bash
python standardizer.py inventory.tsv
```

**With custom output:**
```bash
python standardizer.py inventory.tsv -o clean_inventory.tsv
```

**Strict mode (fail on any issues):**
```bash
python standardizer.py inventory.tsv --strict
```

## Features

✅ **Column standardization** - Maps common variations to standard names  
✅ **Date parsing** - Converts multiple date formats to YYYY-MM-DD  
✅ **Title formatting** - Proper capitalization and whitespace cleanup  
✅ **Object number normalization** - Consistent spacing  
✅ **URL validation** - Checks for missing protocols  
✅ **Duplicate detection** - Removes entries with duplicate object numbers  
✅ **Comprehensive reporting** - Detailed warnings and error messages  
✅ **Error handling** - Graceful handling of malformed data

Would you like me to add additional features like data validation, logging, or batch processing?
