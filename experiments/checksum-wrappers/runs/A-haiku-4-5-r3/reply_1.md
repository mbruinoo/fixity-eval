# Museum Inventory Standardizer

Here's a comprehensive Python script to standardize museum inventory spreadsheets:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer
Standardizes museum inventory TSV files with columns: date, title, object number, link
"""

import csv
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict
import argparse


class InventoryStandardizer:
    """Standardizes museum inventory data"""
    
    REQUIRED_COLUMNS = ['date', 'title', 'object number', 'link']
    
    def __init__(self, input_file: str, output_file: str = None, verbose: bool = False):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self.input_file.with_stem(
            self.input_file.stem + '_standardized'
        )
        self.verbose = verbose
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
        self.data: List[Dict] = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages if verbose mode is enabled"""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def standardize_date(self, date_str: str) -> Tuple[str, bool]:
        """
        Standardize date to ISO format (YYYY-MM-DD)
        Returns: (standardized_date, is_valid)
        """
        if not date_str or not date_str.strip():
            return "", False
        
        date_str = date_str.strip()
        
        # Common date formats to try
        formats = [
            "%Y-%m-%d",      # 2023-01-15
            "%Y/%m/%d",      # 2023/01/15
            "%m/%d/%Y",      # 01/15/2023
            "%m-%d-%Y",      # 01-15-2023
            "%d/%m/%Y",      # 15/01/2023
            "%d-%m-%Y",      # 15-01-2023
            "%B %d, %Y",     # January 15, 2023
            "%b %d, %Y",     # Jan 15, 2023
            "%Y",            # 2023
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d"), True
            except ValueError:
                continue
        
        return date_str, False
    
    def standardize_title(self, title: str) -> str:
        """
        Standardize title formatting
        - Strip whitespace
        - Remove extra spaces
        - Title case (preserve existing case for proper nouns)
        """
        if not title:
            return ""
        
        title = title.strip()
        # Remove multiple spaces
        title = re.sub(r'\s+', ' ', title)
        return title
    
    def standardize_object_number(self, obj_num: str) -> Tuple[str, bool]:
        """
        Standardize object number
        - Remove extra spaces
        - Ensure consistent formatting
        Returns: (standardized_number, is_valid)
        """
        if not obj_num or not obj_num.strip():
            return "", False
        
        obj_num = obj_num.strip()
        obj_num = re.sub(r'\s+', ' ', obj_num)
        
        # Check if it's empty after cleaning
        if not obj_num:
            return "", False
        
        return obj_num, True
    
    def standardize_link(self, link: str) -> Tuple[str, bool]:
        """
        Standardize URL
        - Strip whitespace
        - Ensure proper format
        Returns: (standardized_link, is_valid)
        """
        if not link or not link.strip():
            return "", False
        
        link = link.strip()
        
        # Basic URL validation
        url_pattern = r'^https?://.+'
        is_valid = bool(re.match(url_pattern, link))
        
        if not link.startswith(('http://', 'https://')):
            self.warnings.append({
                'row': None,
                'column': 'link',
                'value': link,
                'issue': 'URL does not start with http:// or https://'
            })
        
        return link, is_valid
    
    def read_input(self) -> List[Dict]:
        """Read and parse the input TSV file"""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        self.log(f"Reading input file: {self.input_file}")
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if reader.fieldnames is None:
                    raise ValueError("TSV file is empty")
                
                # Normalize column names to lowercase
                fieldnames = [col.strip().lower() for col in reader.fieldnames]
                
                # Check for required columns
                missing_cols = set(self.REQUIRED_COLUMNS) - set(fieldnames)
                if missing_cols:
                    raise ValueError(f"Missing required columns: {missing_cols}")
                
                # Read all rows
                raw_data = []
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                    normalized_row = {k.strip().lower(): v for k, v in row.items()}
                    normalized_row['_row_number'] = row_num
                    raw_data.append(normalized_row)
                
                self.log(f"Successfully read {len(raw_data)} rows")
                return raw_data
                
        except Exception as e:
            raise Exception(f"Error reading input file: {str(e)}")
    
    def standardize_records(self, raw_data: List[Dict]) -> List[Dict]:
        """Standardize all records"""
        self.log("Standardizing records...")
        standardized = []
        
        for row in raw_data:
            row_num = row.get('_row_number')
            standardized_row = {'_row_number': row_num}
            
            # Standardize date
            date_val, date_valid = self.standardize_date(row.get('date', ''))
            standardized_row['date'] = date_val
            if not date_valid and date_val:
                self.warnings.append({
                    'row': row_num,
                    'column': 'date',
                    'value': row.get('date'),
                    'issue': 'Date format not recognized, kept as-is'
                })
            if not date_val:
                self.errors.append({
                    'row': row_num,
                    'column': 'date',
                    'value': row.get('date'),
                    'issue': 'Date is missing or empty'
                })
            
            # Standardize title
            title_val = self.standardize_title(row.get('title', ''))
            standardized_row['title'] = title_val
            if not title_val:
                self.errors.append({
                    'row': row_num,
                    'column': 'title',
                    'value': row.get('title'),
                    'issue': 'Title is missing or empty'
                })
            
            # Standardize object number
            obj_num_val, obj_num_valid = self.standardize_object_number(row.get('object number', ''))
            standardized_row['object number'] = obj_num_val
            if not obj_num_valid:
                self.errors.append({
                    'row': row_num,
                    'column': 'object number',
                    'value': row.get('object number'),
                    'issue': 'Object number is missing or invalid'
                })
            
            # Standardize link
            link_val, link_valid = self.standardize_link(row.get('link', ''))
            standardized_row['link'] = link_val
            if not link_valid and link_val:
                self.warnings.append({
                    'row': row_num,
                    'column': 'link',
                    'value': row.get('link'),
                    'issue': 'Link format may be invalid'
                })
            if not link_val:
                self.warnings.append({
                    'row': row_num,
                    'column': 'link',
                    'value': row.get('link'),
                    'issue': 'Link is missing or empty'
                })
            
            standardized.append(standardized_row)
        
        self.log(f"Standardized {len(standardized)} records")
        return standardized
    
    def write_output(self, standardized_data: List[Dict]):
        """Write standardized data to output file"""
        self.log(f"Writing output to: {self.output_file}")
        
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['date', 'title', 'object number', 'link']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                
                writer.writeheader()
                for row in standardized_data:
                    output_row = {field: row.get(field, '') for field in fieldnames}
                    writer.writerow(output_row)
            
            self.log(f"Successfully wrote output file")
        except Exception as e:
            raise Exception(f"Error writing output file: {str(e)}")
    
    def generate_report(self) -> str:
        """Generate a validation report"""
        report = []
        report.append("=" * 60)
        report.append("MUSEUM INVENTORY STANDARDIZATION REPORT")
        report.append("=" * 60)
        report.append(f"Input file: {self.input_file}")
        report.append(f"Output file: {self.output_file}")
        report.append(f"Total records processed: {len(self.data)}")
        report.append("")
        
        if self.errors:
            report.append(f"ERRORS ({len(self.errors)}):")
            report.append("-" * 60)
            for error in self.errors:
                report.append(f"  Row {error['row']}, Column '{error['column']}':")
                report.append(f"    Value: {error['value']}")
                report.append(f"    Issue: {error['issue']}")
                report.append("")
        else:
            report.append("✓ No errors found")
            report.append("")
        
        if self.warnings:
            report.append(f"WARNINGS ({len(self.warnings)}):")
            report.append("-" * 60)
            for warning in self.warnings:
                report.append(f"  Row {warning['row']}, Column '{warning['column']}':")
                report.append(f"    Value: {warning['value']}")
                report.append(f"    Issue: {warning['issue']}")
                report.append("")
        else:
            report.append("✓ No warnings found")
            report.append("")
        
        report.append("=" * 60)
        return "\n".join(report)
    
    def run(self):
        """Run the standardization process"""
        try:
            # Read input
            raw_data = self.read_input()
            
            # Standardize records
            standardized_data = self.standardize_records(raw_data)
            self.data = standardized_data
            
            # Write output
            self.write_output(standardized_data)
            
            # Generate and print report
            report = self.generate_report()
            print(report)
            
            # Save report to file
            report_file = self.output_file.with_suffix('.report.txt')
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            self.log(f"Report saved to: {report_file}")
            
            return True
            
        except Exception as e:
            print(f"ERROR: {str(e)}", file=sys.stderr)
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory TSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python standardize_inventory.py input.tsv
  python standardize_inventory.py input.tsv -o output.tsv -v
        """
    )
    
    parser.add_argument('input_file', help='Input TSV file')
    parser.add_argument('-o', '--output', help='Output TSV file (default: input_standardized.tsv)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    standardizer = InventoryStandardizer(
        args.input_file,
        args.output,
        args.verbose
    )
    
    success = standardizer.run()
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
python standardize_inventory.py input.tsv -o cleaned_inventory.tsv
```

### Verbose mode:
```bash
python standardize_inventory.py input.tsv -v
```

## Features

✓ **Date standardization**: Converts multiple formats to ISO format (YYYY-MM-DD)
✓ **Title cleaning**: Removes extra whitespace, normalizes formatting
✓ **Object number validation**: Ensures consistency and detects empty values
✓ **URL validation**: Checks for proper HTTP/HTTPS format
✓ **Error reporting**: Detailed error and warning logs
✓ **CSV output**: Generates standardized TSV file
✓ **Report generation**: Creates a summary report of all issues

## Output Files

- `*_standardized.tsv` - Cleaned inventory data
- `*.report.txt` - Validation report with errors and warnings
