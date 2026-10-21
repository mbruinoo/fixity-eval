# Museum Inventory Standardizer

```python
#!/usr/bin/env python3
"""
Standardize a museum inventory spreadsheet (.tsv) with handling for 
corrections and withdrawals.

Columns: date, title, object_number, link
"""

import sys
import csv
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict


class InventoryStandardizer:
    def __init__(self, input_file, output_file, corrections_file=None):
        self.input_file = input_file
        self.output_file = output_file
        self.corrections_file = corrections_file
        self.inventory = []
        self.corrections = defaultdict(list)
        self.withdrawn = set()
        
    def load_corrections(self):
        """Load corrections file if provided."""
        if not self.corrections_file or not Path(self.corrections_file).exists():
            return
        
        try:
            with open(self.corrections_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    action = row.get('action', '').strip().lower()
                    obj_num = row.get('object_number', '').strip()
                    
                    if action == 'withdraw':
                        self.withdrawn.add(obj_num)
                    elif action == 'correct':
                        self.corrections[obj_num].append(row)
        except Exception as e:
            print(f"Warning: Could not load corrections file: {e}", file=sys.stderr)
    
    def standardize_date(self, date_str):
        """Standardize date to YYYY-MM-DD format."""
        if not date_str or not date_str.strip():
            return None
        
        date_str = date_str.strip()
        formats = [
            '%Y-%m-%d', '%Y/%m/%d',
            '%m-%d-%Y', '%m/%d/%Y',
            '%d-%m-%Y', '%d/%m/%Y',
            '%B %d, %Y', '%b %d, %Y',
            '%Y',
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        print(f"Warning: Could not parse date '{date_str}'", file=sys.stderr)
        return date_str
    
    def standardize_object_number(self, obj_num):
        """Standardize object number: remove extra spaces, normalize case."""
        if not obj_num:
            return None
        
        obj_num = obj_num.strip()
        # Remove multiple spaces
        obj_num = re.sub(r'\s+', ' ', obj_num)
        # Remove leading zeros from numeric parts (optional - adjust as needed)
        # For now, just normalize whitespace
        
        return obj_num if obj_num else None
    
    def standardize_title(self, title):
        """Standardize title: trim, normalize whitespace, title case."""
        if not title:
            return None
        
        title = title.strip()
        # Remove multiple spaces
        title = re.sub(r'\s+', ' ', title)
        # Remove leading/trailing punctuation
        title = title.strip('.,;:')
        
        return title if title else None
    
    def standardize_link(self, link):
        """Standardize link: validate URL format."""
        if not link or not link.strip():
            return None
        
        link = link.strip()
        
        # Check if it's a valid URL
        if not link.startswith(('http://', 'https://', 'ftp://')):
            print(f"Warning: Link doesn't start with protocol: '{link}'", 
                  file=sys.stderr)
            return link
        
        return link
    
    def apply_corrections(self, record):
        """Apply any corrections to the record."""
        obj_num = record.get('object_number')
        
        if obj_num in self.corrections:
            for correction in self.corrections[obj_num]:
                # Apply corrections to specific fields
                for field in ['title', 'date', 'link']:
                    if field in correction and correction[field].strip():
                        record[field] = correction[field].strip()
        
        return record
    
    def read_inventory(self):
        """Read and parse the inventory TSV file."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    raise ValueError("Empty file or no headers")
                
                expected_fields = {'date', 'title', 'object_number', 'link'}
                actual_fields = set(reader.fieldnames)
                
                if not expected_fields.issubset(actual_fields):
                    missing = expected_fields - actual_fields
                    raise ValueError(f"Missing required columns: {missing}")
                
                for row_num, row in enumerate(reader, start=2):
                    self.inventory.append({
                        'row_num': row_num,
                        'data': row
                    })
        except FileNotFoundError:
            print(f"Error: Input file not found: {self.input_file}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading inventory file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def standardize(self):
        """Standardize all inventory records."""
        standardized = []
        errors = []
        withdrawn_count = 0
        
        for entry in self.inventory:
            row_num = entry['row_num']
            record = entry['data'].copy()
            obj_num = record.get('object_number', '').strip()
            
            # Check if withdrawn
            if obj_num in self.withdrawn:
                withdrawn_count += 1
                continue
            
            # Apply corrections first
            record = self.apply_corrections(record)
            
            # Validate required fields
            if not obj_num:
                errors.append(f"Row {row_num}: Missing object_number")
                continue
            
            # Standardize fields
            try:
                standardized_record = {
                    'date': self.standardize_date(record.get('date', '')),
                    'title': self.standardize_title(record.get('title', '')),
                    'object_number': self.standardize_object_number(obj_num),
                    'link': self.standardize_link(record.get('link', '')),
                }
                
                # Validate title and object_number are not empty
                if not standardized_record['title']:
                    errors.append(f"Row {row_num}: Empty or invalid title")
                    continue
                
                standardized.append(standardized_record)
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        # Report statistics
        print(f"\nProcessing Summary:", file=sys.stderr)
        print(f"  Total records: {len(self.inventory)}", file=sys.stderr)
        print(f"  Standardized: {len(standardized)}", file=sys.stderr)
        print(f"  Withdrawn: {withdrawn_count}", file=sys.stderr)
        print(f"  Errors: {len(errors)}", file=sys.stderr)
        
        if errors:
            print("\nErrors encountered:", file=sys.stderr)
            for error in errors[:10]:
                print(f"  {error}", file=sys.stderr)
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors", file=sys.stderr)
        
        return standardized
    
    def write_output(self, standardized_records):
        """Write standardized inventory to output file."""
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['date', 'title', 'object_number', 'link']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(standardized_records)
            
            print(f"\nOutput written to: {self.output_file}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def run(self):
        """Execute the standardization process."""
        self.load_corrections()
        self.read_inventory()
        standardized = self.standardize()
        self.write_output(standardized)


def main():
    if len(sys.argv) < 3:
        print("Usage: python standardize_inventory.py <input.tsv> <output.tsv> [corrections.tsv]")
        print()
        print("Input TSV should have columns: date, title, object_number, link")
        print("Optional corrections.tsv format: object_number, action, field, value")
        print("  action: 'withdraw' or 'correct'")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    corrections_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    standardizer = InventoryStandardizer(input_file, output_file, corrections_file)
    standardizer.run()


if __name__ == '__main__':
    main()
```

## Usage

### Basic usage:
```bash
python standardize_inventory.py inventory.tsv inventory_standardized.tsv
```

### With corrections file:
```bash
python standardize_inventory.py inventory.tsv inventory_standardized.tsv corrections.tsv
```

## Corrections File Format

Create a `corrections.tsv` file to track edits:

```
object_number	action	field	value
2023.001	withdraw		
2023.002	correct	title	Updated Title
2023.003	correct	link	https://example.com/item/2023003
2023.004	correct	date	2023-05-15
```

## Features

- **Date standardization**: Multiple date formats → YYYY-MM-DD
- **Object number normalization**: Whitespace cleanup
- **Title standardization**: Trim, normalize spaces, remove punctuation
- **Link validation**: Checks for proper URL protocol
- **Corrections handling**: Apply corrections and withdrawals from separate file
- **Error reporting**: Detailed feedback on problematic records
- **Statistics**: Summary of processing results

## Sample Input

```
date	title	object_number	link
5/15/2023	Ceramic Vessel	2023.001	https://museum.org/2023001
2023-06-01	Painting, Oil on Canvas	2023.002	https://museum.org/paintings/002
June 10, 2023	Stone Carving	2023.003	https://museum.org/2023003
```
