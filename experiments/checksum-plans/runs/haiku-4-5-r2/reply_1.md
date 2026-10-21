# Museum Inventory Standardizer

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory spreadsheets (.tsv format).
Columns: date, title, object number, and link
"""

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


class InventoryStandardizer:
    """Standardizes museum inventory data."""
    
    REQUIRED_COLUMNS = ["date", "title", "object_number", "link"]
    
    def __init__(self, input_file, output_file=None):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self.input_file.with_stem(
            self.input_file.stem + "_standardized"
        )
        self.errors = []
        self.warnings = []
    
    def standardize_date(self, date_str):
        """
        Standardize date to ISO format (YYYY-MM-DD).
        Handles common formats.
        """
        if not date_str or not date_str.strip():
            self.warnings.append("Empty date field")
            return ""
        
        date_str = date_str.strip()
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%m-%d-%Y",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%Y",
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        self.warnings.append(f"Could not parse date: {date_str}")
        return date_str
    
    def standardize_title(self, title):
        """
        Standardize title: trim whitespace, fix capitalization.
        """
        if not title:
            self.warnings.append("Empty title field")
            return ""
        
        title = title.strip()
        # Remove extra spaces
        title = " ".join(title.split())
        # Title case (preserve existing capitals)
        return title
    
    def standardize_object_number(self, obj_num):
        """
        Standardize object number: trim, uppercase, remove extra spaces.
        Format: CATEGORY-YEAR-NUMBER
        """
        if not obj_num:
            self.warnings.append("Empty object number")
            return ""
        
        obj_num = obj_num.strip().upper()
        # Remove extra spaces
        obj_num = " ".join(obj_num.split())
        
        # Validate format (allows flexibility)
        if not re.match(r"^[A-Z0-9\-\.]+$", obj_num):
            self.warnings.append(f"Invalid object number format: {obj_num}")
        
        return obj_num
    
    def standardize_link(self, link):
        """
        Standardize link: validate URL format, ensure protocol.
        """
        if not link or not link.strip():
            return ""
        
        link = link.strip()
        
        # Add protocol if missing
        if not link.startswith(("http://", "https://", "ftp://")):
            link = "https://" + link
        
        # Validate URL
        try:
            result = urlparse(link)
            if not result.scheme or not result.netloc:
                self.warnings.append(f"Invalid URL: {link}")
                return link
        except Exception as e:
            self.warnings.append(f"URL parsing error: {link} ({e})")
        
        return link
    
    def read_input(self):
        """Read the input TSV file."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    self.errors.append("Empty file")
                    return None
                
                # Normalize column names
                fieldnames = [name.lower().replace(" ", "_") for name in reader.fieldnames]
                rows = []
                
                for i, row in enumerate(reader, start=2):
                    normalized_row = {fieldnames[j]: v for j, v in enumerate(row.values())}
                    rows.append((i, normalized_row))
                
                return fieldnames, rows
        except FileNotFoundError:
            self.errors.append(f"File not found: {self.input_file}")
            return None
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return None
    
    def validate_row(self, row_num, row):
        """Validate that a row has all required columns."""
        missing = [col for col in self.REQUIRED_COLUMNS if col not in row]
        if missing:
            self.errors.append(f"Row {row_num}: Missing columns: {', '.join(missing)}")
            return False
        return True
    
    def process_rows(self, fieldnames, rows):
        """Process and standardize all rows."""
        processed_rows = []
        
        for row_num, row in rows:
            if not self.validate_row(row_num, row):
                continue
            
            try:
                processed_row = {
                    "date": self.standardize_date(row.get("date", "")),
                    "title": self.standardize_title(row.get("title", "")),
                    "object_number": self.standardize_object_number(row.get("object_number", "")),
                    "link": self.standardize_link(row.get("link", "")),
                }
                
                # Add extra columns if they exist
                for col in fieldnames:
                    if col not in self.REQUIRED_COLUMNS:
                        processed_row[col] = row.get(col, "")
                
                processed_rows.append(processed_row)
            except Exception as e:
                self.errors.append(f"Row {row_num}: Error processing - {e}")
        
        return processed_rows
    
    def write_output(self, rows):
        """Write standardized data to output file."""
        if not rows:
            self.errors.append("No valid rows to write")
            return False
        
        try:
            # Determine fieldnames
            fieldnames = self.REQUIRED_COLUMNS + [
                k for k in rows[0].keys() if k not in self.REQUIRED_COLUMNS
            ]
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(rows)
            
            return True
        except Exception as e:
            self.errors.append(f"Error writing output file: {e}")
            return False
    
    def standardize(self):
        """Main standardization workflow."""
        result = self.read_input()
        if result is None:
            return False
        
        fieldnames, rows = result
        processed_rows = self.process_rows(fieldnames, rows)
        success = self.write_output(processed_rows)
        
        return success
    
    def report(self):
        """Print standardization report."""
        print("\n" + "="*60)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"   • {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more")
        
        if not self.errors:
            print(f"\n✅ Successfully standardized to: {self.output_file}")
        
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory spreadsheet (.tsv)"
    )
    parser.add_argument("input", help="Input TSV file")
    parser.add_argument(
        "-o", "--output",
        help="Output TSV file (default: input_standardized.tsv)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    standardizer = InventoryStandardizer(args.input, args.output)
    success = standardizer.standardize()
    standardizer.report()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
```

## Usage

```bash
# Basic usage
python standardize_inventory.py inventory.tsv

# Specify output file
python standardize_inventory.py inventory.tsv -o standardized.tsv

# Verbose output
python standardize_inventory.py inventory.tsv -v
```

## Features

- **Date Standardization**: Converts multiple date formats to ISO (YYYY-MM-DD)
- **Title Cleaning**: Trims whitespace, normalizes spacing
- **Object Number**: Standardizes to uppercase, validates format
- **URL Validation**: Ensures valid URLs with proper protocol
- **Error Reporting**: Detailed error and warning messages
- **Column Flexibility**: Preserves extra columns beyond the 4 required ones
- **UTF-8 Support**: Handles special characters properly

## Example Input

```
date	title	object_number	link
1/15/2023	Ancient Vase	ART-2023-001	www.museum.org/vase
2023-03-20	Medieval Sword	ARMOR-2023-002	https://museum.org/sword
```

## Example Output

```
date	title	object_number	link
2023-01-15	Ancient Vase	ART-2023-001	https://www.museum.org/vase
2023-03-20	Medieval Sword	ARMOR-2023-002	https://museum.org/sword
```
