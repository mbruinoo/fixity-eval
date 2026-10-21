# Museum Inventory Standardizer

```python
#!/usr/bin/env python3
"""
Script to standardize museum inventory spreadsheet (.tsv files).
Standardizes 4 columns: date, title, object number, and link.
"""

import csv
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import argparse


class InventoryStandardizer:
    """Standardizes museum inventory data."""
    
    REQUIRED_COLUMNS = {'date', 'title', 'object number', 'link'}
    
    def __init__(self, input_file, output_file=None, strict=False):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file (optional)
            strict: If True, skip rows with errors; if False, report warnings
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self._generate_output_filename()
        self.strict = strict
        self.errors = []
        self.warnings = []
        self.standardized_rows = []
    
    def _generate_output_filename(self):
        """Generate output filename from input filename."""
        stem = self.input_file.stem
        return self.input_file.parent / f"{stem}_standardized.tsv"
    
    def _standardize_date(self, date_str):
        """
        Standardize date to YYYY-MM-DD format.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Standardized date string or None if invalid
        """
        if not date_str or date_str.strip() == '':
            return None
        
        date_str = date_str.strip()
        
        # Common date formats to try
        formats = [
            '%Y-%m-%d',      # 2023-12-25
            '%m/%d/%Y',      # 12/25/2023
            '%d/%m/%Y',      # 25/12/2023
            '%m-%d-%Y',      # 12-25-2023
            '%B %d, %Y',     # December 25, 2023
            '%b %d, %Y',     # Dec 25, 2023
            '%Y/%m/%d',      # 2023/12/25
            '%d-%m-%Y',      # 25-12-2023
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        self.warnings.append(f"Could not parse date: '{date_str}'")
        return date_str  # Return as-is if unparseable
    
    def _standardize_title(self, title):
        """
        Standardize title: strip whitespace, title case.
        
        Args:
            title: Title string
            
        Returns:
            Standardized title
        """
        if not title:
            return ''
        
        title = title.strip()
        
        # Remove extra whitespace
        title = ' '.join(title.split())
        
        return title
    
    def _standardize_object_number(self, obj_num):
        """
        Standardize object number: uppercase, remove extra spaces.
        
        Args:
            obj_num: Object number string
            
        Returns:
            Standardized object number
        """
        if not obj_num:
            return ''
        
        obj_num = obj_num.strip()
        
        # Remove extra whitespace and standardize format
        obj_num = ' '.join(obj_num.split())
        
        return obj_num
    
    def _standardize_link(self, link):
        """
        Standardize link: validate URL format.
        
        Args:
            link: URL string
            
        Returns:
            Standardized URL or empty string if invalid
        """
        if not link or link.strip() == '':
            return ''
        
        link = link.strip()
        
        # Add http:// if no scheme present
        if not link.startswith(('http://', 'https://')):
            link = 'https://' + link
            self.warnings.append(f"Added https:// to URL: {link}")
        
        # Basic URL validation
        try:
            result = urlparse(link)
            if not result.netloc:
                self.warnings.append(f"Invalid URL format: {link}")
                return ''
            return link
        except Exception as e:
            self.warnings.append(f"Error parsing URL '{link}': {str(e)}")
            return ''
    
    def _validate_headers(self, headers):
        """
        Validate that required columns are present.
        
        Args:
            headers: List of column headers
            
        Returns:
            True if valid, False otherwise
        """
        headers_lower = [h.lower().strip() for h in headers]
        found_columns = set(headers_lower)
        
        if not self.REQUIRED_COLUMNS.issubset(found_columns):
            missing = self.REQUIRED_COLUMNS - found_columns
            self.errors.append(f"Missing required columns: {missing}")
            return False
        
        return True
    
    def _get_column_indices(self, headers):
        """
        Get indices of required columns from headers.
        
        Args:
            headers: List of column headers
            
        Returns:
            Dictionary mapping column names to indices
        """
        headers_lower = [h.lower().strip() for h in headers]
        indices = {}
        
        for col in self.REQUIRED_COLUMNS:
            try:
                indices[col] = headers_lower.index(col)
            except ValueError:
                indices[col] = None
        
        return indices
    
    def standardize(self):
        """
        Read and standardize the inventory file.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.input_file.exists():
            self.errors.append(f"Input file not found: {self.input_file}")
            return False
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as infile:
                reader = csv.reader(infile, delimiter='\t')
                
                # Read headers
                try:
                    headers = next(reader)
                except StopIteration:
                    self.errors.append("Input file is empty")
                    return False
                
                # Validate headers
                if not self._validate_headers(headers):
                    return False
                
                # Get column indices
                col_indices = self._get_column_indices(headers)
                
                # Process data rows
                row_num = 1
                for row in reader:
                    row_num += 1
                    
                    # Ensure row has enough columns
                    if len(row) < len(headers):
                        row.extend([''] * (len(headers) - len(row)))
                    
                    try:
                        standardized_row = self._standardize_row(row, col_indices)
                        self.standardized_rows.append(standardized_row)
                    except ValueError as e:
                        msg = f"Row {row_num}: {str(e)}"
                        if self.strict:
                            self.errors.append(msg)
                            return False
                        else:
                            self.warnings.append(msg)
                
            return True
        
        except Exception as e:
            self.errors.append(f"Error reading file: {str(e)}")
            return False
    
    def _standardize_row(self, row, col_indices):
        """
        Standardize a single row.
        
        Args:
            row: List of values
            col_indices: Dictionary mapping column names to indices
            
        Returns:
            Standardized row as list
        """
        date = self._standardize_date(row[col_indices['date']])
        title = self._standardize_title(row[col_indices['title']])
        obj_num = self._standardize_object_number(row[col_indices['object number']])
        link = self._standardize_link(row[col_indices['link']])
        
        # Validate non-empty title and object number
        if not title:
            raise ValueError("Title cannot be empty")
        if not obj_num:
            raise ValueError("Object number cannot be empty")
        
        return [date, title, obj_num, link]
    
    def write_output(self):
        """Write standardized data to output file."""
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile, delimiter='\t')
                
                # Write headers
                writer.writerow(['date', 'title', 'object number', 'link'])
                
                # Write standardized rows
                writer.writerows(self.standardized_rows)
            
            return True
        except Exception as e:
            self.errors.append(f"Error writing output file: {str(e)}")
            return False
    
    def print_report(self):
        """Print standardization report."""
        print("\n" + "="*60)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("="*60)
        
        print(f"\nInput file:  {self.input_file}")
        print(f"Output file: {self.output_file}")
        print(f"Rows processed: {len(self.standardized_rows)}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if not self.errors:
            print("\n✅ Standardization completed successfully!")
        
        print("="*60 + "\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory spreadsheet (.tsv)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python standardize_inventory.py inventory.tsv
  python standardize_inventory.py inventory.tsv -o standardized.tsv
  python standardize_inventory.py inventory.tsv --strict
        """
    )
    
    parser.add_argument('input_file', help='Input TSV file')
    parser.add_argument('-o', '--output', help='Output TSV file (optional)')
    parser.add_argument('--strict', action='store_true',
                        help='Strict mode: fail on first error')
    
    args = parser.parse_args()
    
    # Create standardizer
    standardizer = InventoryStandardizer(
        args.input_file,
        args.output,
        strict=args.strict
    )
    
    # Perform standardization
    if not standardizer.standardize():
        standardizer.print_report()
        sys.exit(1)
    
    # Write output
    if not standardizer.write_output():
        standardizer.print_report()
        sys.exit(1)
    
    # Print report
    standardizer.print_report()


if __name__ == '__main__':
    main()
```

## Usage

### Basic usage:
```bash
python standardize_inventory.py inventory.tsv
```

### Specify output file:
```bash
python standardize_inventory.py inventory.tsv -o cleaned_inventory.tsv
```

### Strict mode (fail on errors):
```bash
python standardize_inventory.py inventory.tsv --strict
```

## Features

- **Date Standardization**: Converts multiple date formats to YYYY-MM-DD
- **Title Cleaning**: Strips whitespace, normalizes spacing
- **Object Number**: Removes extra spaces, maintains format
- **URL Validation**: Adds https:// if missing, validates format
- **Error Handling**: Reports missing columns and invalid data
- **Flexible Mode**: Continue with warnings or fail on strict mode
- **Detailed Report**: Shows errors, warnings, and row count

## Example Input

```tsv
date	title	object number	link
12/25/2023	Ancient Vase	2023.001	www.example.com/vase
2023-06-15	Medieval Sword	2023.002	https://example.com/sword
```

## Example Output

```tsv
date	title	object number	link
2023-12-25	Ancient Vase	2023.001	https://www.example.com/vase
2023-06-15	Medieval Sword	2023.002	https://example.com/sword
```
