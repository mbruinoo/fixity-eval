# Museum Inventory Standardizer

```python
#!/usr/bin/env python3
"""
Script to standardize museum inventory spreadsheet (.tsv files).
Handles: date formatting, title normalization, object number validation, and link verification.
"""

import csv
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
from urllib.parse import urlparse


class MuseumInventoryStandardizer:
    """Standardize museum inventory data from TSV files."""
    
    REQUIRED_COLUMNS = ['date', 'title', 'object number', 'link']
    DATE_FORMATS = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%B %d, %Y',
        '%b %d, %Y',
    ]
    
    def __init__(self, input_file: str, output_file: str = None, strict: bool = False):
        """
        Initialize standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file (default: input_file_standardized.tsv)
            strict: If True, skip rows with errors; if False, attempt repairs
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else \
                          self.input_file.parent / f"{self.input_file.stem}_standardized.tsv"
        self.strict = strict
        self.errors = []
        self.warnings = []
        self.skipped_rows = []
        
    def standardize_date(self, date_str: str) -> Tuple[str, str]:
        """
        Standardize date to YYYY-MM-DD format.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Tuple of (standardized_date, status_message)
        """
        if not date_str or date_str.strip() == '':
            return '', 'WARNING: Empty date field'
        
        date_str = date_str.strip()
        
        # Try standard formats
        for fmt in self.DATE_FORMATS:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y-%m-%d'), 'OK'
            except ValueError:
                continue
        
        # Try parsing year only
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            msg = f'WARNING: Partial date parsed as year only: {year_match.group()}'
            return year_match.group(), msg
        
        return '', f'ERROR: Could not parse date: {date_str}'
    
    def standardize_title(self, title: str) -> Tuple[str, str]:
        """
        Standardize title: trim, normalize whitespace, title case.
        
        Args:
            title: Raw title string
            
        Returns:
            Tuple of (standardized_title, status_message)
        """
        if not title or title.strip() == '':
            return '', 'WARNING: Empty title field'
        
        # Trim and normalize whitespace
        title = ' '.join(title.split())
        
        # Remove extra punctuation
        title = re.sub(r'\s+([,.;:])', r'\1', title)
        
        return title, 'OK'
    
    def standardize_object_number(self, obj_num: str) -> Tuple[str, str]:
        """
        Standardize object number: uppercase, remove extra spaces.
        
        Args:
            obj_num: Raw object number
            
        Returns:
            Tuple of (standardized_number, status_message)
        """
        if not obj_num or obj_num.strip() == '':
            return '', 'WARNING: Empty object number'
        
        # Normalize: trim, uppercase, remove extra spaces
        obj_num = ' '.join(obj_num.split()).upper()
        
        # Check for common issues
        if not re.search(r'[A-Z0-9]', obj_num):
            return obj_num, 'WARNING: Object number contains no alphanumeric characters'
        
        return obj_num, 'OK'
    
    def standardize_link(self, link: str) -> Tuple[str, str]:
        """
        Standardize link: validate URL format, ensure HTTPS.
        
        Args:
            link: Raw link string
            
        Returns:
            Tuple of (standardized_link, status_message)
        """
        if not link or link.strip() == '':
            return '', 'WARNING: Empty link field'
        
        link = link.strip()
        
        # Check if URL is valid
        try:
            result = urlparse(link)
            
            # Add protocol if missing
            if not result.scheme:
                link = 'https://' + link
                return link, 'WARNING: Protocol added (assumed HTTPS)'
            
            # Validate scheme
            if result.scheme not in ['http', 'https']:
                return '', f'ERROR: Invalid protocol: {result.scheme}'
            
            # Prefer HTTPS
            if result.scheme == 'http' and result.netloc:
                link = 'https://' + result.netloc + (result.path or '') + \
                       (('?' + result.query) if result.query else '')
                return link, 'WARNING: Converted HTTP to HTTPS'
            
            return link, 'OK'
            
        except Exception as e:
            return '', f'ERROR: Invalid URL: {str(e)}'
    
    def process_row(self, row: Dict[str, str], row_num: int) -> Tuple[Dict[str, str], bool]:
        """
        Process and standardize a single row.
        
        Args:
            row: Dictionary with column data
            row_num: Row number for error reporting
            
        Returns:
            Tuple of (processed_row, is_valid)
        """
        standardized = {}
        row_valid = True
        
        # Process date
        date, date_msg = self.standardize_date(row.get('date', ''))
        standardized['date'] = date
        if 'WARNING' in date_msg:
            self.warnings.append(f"Row {row_num}: {date_msg}")
        elif 'ERROR' in date_msg:
            self.errors.append(f"Row {row_num}: {date_msg}")
            row_valid = False
        
        # Process title
        title, title_msg = self.standardize_title(row.get('title', ''))
        standardized['title'] = title
        if 'WARNING' in title_msg:
            self.warnings.append(f"Row {row_num}: {title_msg}")
        elif 'ERROR' in title_msg:
            self.errors.append(f"Row {row_num}: {title_msg}")
            row_valid = False
        
        # Process object number
        obj_num, obj_msg = self.standardize_object_number(row.get('object number', ''))
        standardized['object number'] = obj_num
        if 'WARNING' in obj_msg:
            self.warnings.append(f"Row {row_num}: {obj_msg}")
        elif 'ERROR' in obj_msg:
            self.errors.append(f"Row {row_num}: {obj_msg}")
            row_valid = False
        
        # Process link
        link, link_msg = self.standardize_link(row.get('link', ''))
        standardized['link'] = link
        if 'WARNING' in link_msg:
            self.warnings.append(f"Row {row_num}: {link_msg}")
        elif 'ERROR' in link_msg:
            self.errors.append(f"Row {row_num}: {link_msg}")
            row_valid = False
        
        return standardized, row_valid
    
    def validate_columns(self, fieldnames: List[str]) -> bool:
        """
        Validate that all required columns are present (case-insensitive).
        
        Args:
            fieldnames: List of column names from TSV
            
        Returns:
            True if all required columns present, False otherwise
        """
        fieldnames_lower = [f.lower() for f in fieldnames]
        missing = []
        
        for required in self.REQUIRED_COLUMNS:
            if required.lower() not in fieldnames_lower:
                missing.append(required)
        
        if missing:
            self.errors.append(f"Missing required columns: {', '.join(missing)}")
            return False
        
        return True
    
    def run(self) -> bool:
        """
        Execute the standardization process.
        
        Returns:
            True if successful, False otherwise
        """
        # Check input file exists
        if not self.input_file.exists():
            print(f"ERROR: Input file not found: {self.input_file}")
            return False
        
        print(f"Processing: {self.input_file}")
        
        try:
            # Read input file
            with open(self.input_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile, delimiter='\t')
                
                # Validate columns
                if not self.validate_columns(reader.fieldnames):
                    print("ERROR: Column validation failed")
                    return False
                
                # Normalize column names to lowercase
                fieldnames = [f.lower() for f in reader.fieldnames]
                
                rows = []
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                    # Normalize keys to lowercase
                    row_lower = {k.lower(): v for k, v in row.items()}
                    
                    standardized, is_valid = self.process_row(row_lower, row_num)
                    
                    if is_valid or not self.strict:
                        rows.append(standardized)
                    else:
                        self.skipped_rows.append(row_num)
                
                # Write output file
                with open(self.output_file, 'w', newline='', encoding='utf-8') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=self.REQUIRED_COLUMNS, 
                                          delimiter='\t')
                    writer.writeheader()
                    writer.writerows(rows)
                
                # Print summary
                self.print_summary(len(rows))
                
                return True
                
        except Exception as e:
            print(f"ERROR: {str(e)}")
            return False
    
    def print_summary(self, processed_count: int):
        """Print processing summary."""
        print(f"\n{'='*60}")
        print(f"STANDARDIZATION COMPLETE")
        print(f"{'='*60}")
        print(f"Input file:     {self.input_file}")
        print(f"Output file:    {self.output_file}")
        print(f"Rows processed: {processed_count}")
        
        if self.errors:
            print(f"\nERRORS ({len(self.errors)}):")
            for error in self.errors[:10]:  # Show first 10
                print(f"  • {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        
        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  • {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        if self.skipped_rows:
            print(f"\nSKIPPED ROWS ({len(self.skipped_rows)}): {self.skipped_rows}")
        
        if not self.errors:
            print("\n✓ No errors found!")


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: python standardize_inventory.py <input.tsv> [output.tsv] [--strict]")
        print("\nExamples:")
        print("  python standardize_inventory.py inventory.tsv")
        print("  python standardize_inventory.py inventory.tsv standardized.tsv")
        print("  python standardize_inventory.py inventory.tsv --strict")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    strict = '--strict' in sys.argv
    
    standardizer = MuseumInventoryStandardizer(input_file, output_file, strict)
    success = standardizer.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Sample Input TSV

```tsv
date	title	object number	link
2023-01-15	Ancient Greek Vase	1994.86.1	https://example.com/vase
1/20/2023	roman coin  	1995.45.2	example.com/coin
15-02-2023	Medieval Manuscript	  1996-12-003  	http://example.com/manuscript
2023	Egyptian Statue	1997.23.4	example.com/statue
```

## Usage

```bash
# Basic usage (creates input_standardized.tsv)
python standardize_inventory.py inventory.tsv

# Specify output file
python standardize_inventory.py inventory.tsv output.tsv

# Strict mode (skip rows with errors)
python standardize_inventory.py inventory.tsv --strict
```

## Features

✓ **Date Standardization**: Multiple format detection, converts to YYYY-MM-DD  
✓ **Title Normalization**: Trims whitespace, fixes punctuation  
✓ **Object Number Validation**: Uppercase conversion, format checking  
✓ **Link Validation**: URL parsing, HTTPS conversion, protocol addition  
✓ **Error Reporting**: Detailed error/warning logs with row numbers  
✓ **Flexible Processing**: Strict or lenient mode for handling errors  
✓ **Case-Insensitive**: Handles column names regardless of case
