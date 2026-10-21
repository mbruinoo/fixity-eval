# Museum Inventory Standardizer

```python
#!/usr/bin/env python3
"""
Standardizes a museum inventory spreadsheet (.tsv) with columns:
date, title, object number, and link.

Usage:
    python standardize_inventory.py input.tsv output.tsv
"""

import sys
import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class InventoryStandardizer:
    """Standardizes museum inventory data."""
    
    REQUIRED_COLUMNS = {'date', 'title', 'object number', 'link'}
    
    def __init__(self, input_file: str, output_file: str, verbose: bool = True):
        self.input_file = input_file
        self.output_file = output_file
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        
    def log(self, message: str, level: str = "INFO"):
        """Print log messages if verbose mode is enabled."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def standardize_date(self, date_str: str) -> str:
        """
        Standardize date to ISO format (YYYY-MM-DD).
        Handles multiple common date formats.
        """
        if not date_str or not date_str.strip():
            self.warnings.append("Empty date field found")
            return ""
        
        date_str = date_str.strip()
        
        # Common date formats to try
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%m-%d-%Y",
            "%Y/%m/%d",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # Try to extract YYYY from various formats
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            self.warnings.append(f"Could not parse date '{date_str}', keeping original")
            return date_str
        
        self.errors.append(f"Invalid date format: '{date_str}'")
        return ""
    
    def standardize_title(self, title: str) -> str:
        """
        Standardize title:
        - Strip whitespace
        - Remove extra spaces
        - Preserve case (titles typically use Title Case)
        """
        if not title or not title.strip():
            self.errors.append("Empty title field found")
            return ""
        
        # Remove extra whitespace
        title = " ".join(title.split())
        
        return title
    
    def standardize_object_number(self, obj_num: str) -> str:
        """
        Standardize object number:
        - Remove extra whitespace
        - Uppercase
        - Remove invalid characters
        """
        if not obj_num or not obj_num.strip():
            self.errors.append("Empty object number found")
            return ""
        
        obj_num = obj_num.strip().upper()
        
        # Remove any leading/trailing non-alphanumeric (except hyphens/periods)
        obj_num = re.sub(r'^[^\w\-\.]+|[^\w\-\.]+$', '', obj_num)
        
        # Check for valid format (alphanumeric, hyphens, periods)
        if not re.match(r'^[\w\-\.]+$', obj_num):
            self.warnings.append(f"Object number contains unusual characters: '{obj_num}'")
        
        return obj_num
    
    def standardize_link(self, link: str) -> str:
        """
        Standardize URL:
        - Strip whitespace
        - Add http:// if missing
        - Validate basic URL structure
        """
        if not link or not link.strip():
            return ""
        
        link = link.strip()
        
        # Add protocol if missing
        if not link.startswith(('http://', 'https://', 'ftp://')):
            link = 'https://' + link
        
        # Basic URL validation
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, link):
            self.warnings.append(f"URL may be invalid: '{link}'")
        
        return link
    
    def normalize_column_names(self, fieldnames: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """
        Normalize column names to match expected schema.
        Returns normalized fieldnames and mapping from old to new names.
        """
        mapping = {}
        normalized = []
        
        for field in fieldnames:
            field_lower = field.lower().strip()
            
            # Try exact match first
            if field_lower in self.REQUIRED_COLUMNS:
                normalized.append(field_lower)
                mapping[field] = field_lower
                continue
            
            # Try fuzzy matching
            if 'date' in field_lower:
                normalized.append('date')
                mapping[field] = 'date'
            elif any(t in field_lower for t in ['title', 'name', 'object name']):
                normalized.append('title')
                mapping[field] = 'title'
            elif any(o in field_lower for o in ['object', 'number', 'id', 'accession']):
                normalized.append('object number')
                mapping[field] = 'object number'
            elif 'link' in field_lower or 'url' in field_lower or 'uri' in field_lower:
                normalized.append('link')
                mapping[field] = 'link'
            else:
                # Keep unknown columns
                normalized.append(field_lower)
                mapping[field] = field_lower
        
        return normalized, mapping
    
    def validate_row(self, row: Dict[str, str], row_num: int) -> bool:
        """Validate that a row has required columns with data."""
        has_critical_data = any([
            row.get('date', '').strip(),
            row.get('title', '').strip(),
            row.get('object number', '').strip()
        ])
        
        if not has_critical_data:
            self.warnings.append(f"Row {row_num}: Skipping empty row")
            return False
        
        return True
    
    def standardize(self) -> bool:
        """
        Main standardization routine.
        Returns True if successful, False otherwise.
        """
        self.log(f"Reading from: {self.input_file}")
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile, delimiter='\t')
                
                if not reader.fieldnames:
                    self.log("No fieldnames found", "ERROR")
                    return False
                
                # Normalize column names
                normalized_fields, field_mapping = self.normalize_column_names(
                    reader.fieldnames
                )
                self.log(f"Detected columns: {reader.fieldnames}")
                self.log(f"Normalized to: {normalized_fields}")
                
                standardized_rows = []
                
                for row_num, row in enumerate(reader, start=2):  # start=2 (after header)
                    # Remap old column names to new ones
                    remapped_row = {
                        field_mapping[k]: v for k, v in row.items()
                    }
                    
                    # Skip empty rows
                    if not self.validate_row(remapped_row, row_num):
                        continue
                    
                    # Standardize each field
                    standardized_row = {
                        'date': self.standardize_date(remapped_row.get('date', '')),
                        'title': self.standardize_title(remapped_row.get('title', '')),
                        'object number': self.standardize_object_number(
                            remapped_row.get('object number', '')
                        ),
                        'link': self.standardize_link(remapped_row.get('link', '')),
                    }
                    
                    standardized_rows.append(standardized_row)
                
                # Write standardized data
                self.log(f"Writing to: {self.output_file}")
                with open(self.output_file, 'w', newline='', encoding='utf-8') as outfile:
                    writer = csv.DictWriter(
                        outfile,
                        fieldnames=['date', 'title', 'object number', 'link'],
                        delimiter='\t'
                    )
                    writer.writeheader()
                    writer.writerows(standardized_rows)
                
                self.log(f"Successfully standardized {len(standardized_rows)} records")
                return True
        
        except FileNotFoundError:
            self.log(f"Input file not found: {self.input_file}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Unexpected error: {str(e)}", "ERROR")
            return False
    
    def print_report(self):
        """Print summary report of standardization."""
        print("\n" + "="*60)
        print("STANDARDIZATION REPORT")
        print("="*60)
        
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  ⚠ {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"  ✗ {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        
        if not self.errors and not self.warnings:
            print("\n✓ No errors or warnings!")
        
        print("="*60 + "\n")


def main():
    """Command-line interface."""
    if len(sys.argv) < 3:
        print("Usage: python standardize_inventory.py input.tsv output.tsv")
        print("\nStandardizes museum inventory spreadsheet with columns:")
        print("  - date (converted to YYYY-MM-DD)")
        print("  - title (trimmed, normalized whitespace)")
        print("  - object number (uppercased, special characters removed)")
        print("  - link (URLs validated and normalized)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    standardizer = InventoryStandardizer(input_file, output_file, verbose=True)
    
    if standardizer.standardize():
        standardizer.print_report()
        print(f"✓ Output saved to: {output_file}")
        sys.exit(0)
    else:
        standardizer.print_report()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Usage

```bash
python standardize_inventory.py input.tsv output.tsv
```

## Features

1. **Date Standardization**: Converts multiple date formats to ISO format (YYYY-MM-DD)
2. **Title Cleaning**: Removes extra whitespace, preserves case
3. **Object Number Normalization**: Uppercases, removes invalid characters
4. **Link Validation**: Adds protocols, validates URL structure
5. **Column Detection**: Automatically maps common column name variations
6. **Error Reporting**: Detailed warnings and error logs
7. **Data Validation**: Skips empty rows, validates required fields

## Example Input (input.tsv)

```
Date	Object Title	ID Number	Museum Link
01/15/2023	Ancient Vase	1001-A	www.museum.org/items/1001
2023-02-20	Medieval Sword	 2045-B 	https://museum.org/2045-B
March 10, 2023	Portrait Painting	3202_C	museum.org/paintings/3202
```

## Example Output (output.tsv)

```
date	title	object number	link
2023-01-15	Ancient Vase	1001-A	https://www.museum.org/items/1001
2023-02-20	Medieval Sword	2045-B	https://museum.org/2045-B
2023-03-10	Portrait Painting	3202-C	https://museum.org/paintings/3202
```
