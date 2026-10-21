# Museum Inventory Standardizer

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records from a TSV file.

Records can be corrected or withdrawn over time. This script:
- Validates required fields
- Standardizes date formats
- Normalizes object numbers
- Handles corrections and withdrawals
- Generates a clean output file and audit report
"""

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class InventoryRecord:
    """Represents a single museum inventory record."""
    
    REQUIRED_FIELDS = {'date', 'title', 'object_number', 'link'}
    
    def __init__(self, row: Dict[str, str], row_num: int):
        self.row_num = row_num
        self.raw_data = row.copy()
        self.errors = []
        self.warnings = []
        
        # Store original values
        self.date_str = row.get('date', '').strip()
        self.title = row.get('title', '').strip()
        self.object_number = row.get('object_number', '').strip()
        self.link = row.get('link', '').strip()
        self.status = row.get('status', 'active').strip().lower()
        
        # Standardized values
        self.date_standardized = None
        self.object_number_standardized = None
    
    def validate(self) -> bool:
        """Validate required fields. Returns True if valid."""
        for field in self.REQUIRED_FIELDS:
            value = getattr(self, field.replace('object_number', 'object_number'))
            if not value:
                self.errors.append(f"Missing required field: {field}")
        
        # Validate status
        if self.status not in ('active', 'corrected', 'withdrawn'):
            self.errors.append(
                f"Invalid status '{self.status}'. Must be: active, corrected, or withdrawn"
            )
        
        # Validate URL format if not withdrawn
        if self.status != 'withdrawn' and self.link:
            if not self._is_valid_url(self.link):
                self.warnings.append(f"Link may be invalid: {self.link}")
        
        return len(self.errors) == 0
    
    def standardize(self) -> bool:
        """Standardize fields. Returns True if successful."""
        # Standardize date
        self.date_standardized = self._standardize_date(self.date_str)
        if self.date_standardized is None and self.date_str:
            self.errors.append(f"Could not parse date: {self.date_str}")
        
        # Standardize object number
        self.object_number_standardized = self._standardize_object_number(
            self.object_number
        )
        if self.object_number_standardized is None:
            self.errors.append(f"Could not standardize object number: {self.object_number}")
        
        # Validate title length
        if len(self.title) > 500:
            self.warnings.append(
                f"Title is very long ({len(self.title)} chars), may need review"
            )
        
        return len(self.errors) == 0
    
    @staticmethod
    def _standardize_date(date_str: str) -> Optional[str]:
        """
        Convert various date formats to ISO 8601 (YYYY-MM-DD).
        Returns None if parsing fails.
        """
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        # Already in ISO format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                return None
        
        # Try common formats
        formats = [
            '%m/%d/%Y',      # 01/15/2023
            '%d/%m/%Y',      # 15/01/2023
            '%Y/%m/%d',      # 2023/01/15
            '%B %d, %Y',     # January 15, 2023
            '%b %d, %Y',     # Jan 15, 2023
            '%d %B %Y',      # 15 January 2023
            '%d %b %Y',      # 15 Jan 2023
            '%m-%d-%Y',      # 01-15-2023
            '%d-%m-%Y',      # 15-01-2023
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def _standardize_object_number(obj_num: str) -> Optional[str]:
        """
        Standardize object number format.
        Removes extra whitespace and normalizes common patterns.
        """
        if not obj_num:
            return None
        
        # Remove leading/trailing whitespace
        obj_num = obj_num.strip()
        
        # Remove multiple spaces
        obj_num = re.sub(r'\s+', ' ', obj_num)
        
        # Remove hyphens between alphanumeric if inconsistent
        # Example: "2023 - 001" -> "2023-001"
        obj_num = re.sub(r'\s*-\s*', '-', obj_num)
        
        # Ensure at least some alphanumeric content
        if not re.search(r'[a-zA-Z0-9]', obj_num):
            return None
        
        return obj_num.upper()
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Basic URL validation."""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$',
            re.IGNORECASE
        )
        return bool(url_pattern.match(url))
    
    def to_dict(self) -> Dict:
        """Return standardized record as dictionary."""
        return {
            'date': self.date_standardized,
            'title': self.title,
            'object_number': self.object_number_standardized,
            'link': self.link,
            'status': self.status,
        }


class InventoryStandardizer:
    """Manages the standardization process."""
    
    def __init__(self, input_file: Path, output_dir: Path):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.records: List[InventoryRecord] = []
        self.valid_records: List[InventoryRecord] = []
        self.invalid_records: List[InventoryRecord] = []
    
    def read_input(self) -> bool:
        """Read and parse TSV file. Returns True if successful."""
        try:
            with open(self.input_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if reader.fieldnames is None:
                    print("Error: Empty TSV file", file=sys.stderr)
                    return False
                
                for row_num, row in enumerate(reader, start=2):  # start=2 (after header)
                    record = InventoryRecord(row, row_num)
                    self.records.append(record)
            
            print(f"✓ Loaded {len(self.records)} records")
            return True
        
        except FileNotFoundError:
            print(f"Error: File not found: {self.input_file}", file=sys.stderr)
            return False
        except csv.Error as e:
            print(f"Error reading TSV: {e}", file=sys.stderr)
            return False
    
    def process_records(self) -> None:
        """Validate and standardize all records."""
        print("\nProcessing records...")
        
        # Track corrections and withdrawals
        corrections: Dict[str, List[int]] = defaultdict(list)
        withdrawals: List[int] = []
        
        for record in self.records:
            if not record.validate():
                self.invalid_records.append(record)
                continue
            
            if not record.standardize():
                self.invalid_records.append(record)
                continue
            
            # Track status changes
            if record.status == 'corrected':
                corrections[record.object_number_standardized].append(record.row_num)
            elif record.status == 'withdrawn':
                withdrawals.append(record.row_num)
            
            self.valid_records.append(record)
        
        print(f"✓ Valid records: {len(self.valid_records)}")
        print(f"✓ Invalid records: {len(self.invalid_records)}")
    
    def handle_corrections_and_withdrawals(self) -> Tuple[List[InventoryRecord], Dict]:
        """
        Process corrections and withdrawals.
        Keep only the latest version of each object.
        Returns (active_records, audit_info).
        """
        # Group by object number
        by_object: Dict[str, List[InventoryRecord]] = defaultdict(list)
        for record in self.valid_records:
            by_object[record.object_number_standardized].append(record)
        
        active_records = []
        audit_info = {
            'corrections': 0,
            'withdrawn': 0,
            'duplicates_kept': 0,
        }
        
        for obj_num, versions in by_object.items():
            # Sort by row number to get latest version
            versions.sort(key=lambda r: r.row_num)
            latest = versions[-1]
            
            if latest.status == 'withdrawn':
                audit_info['withdrawn'] += 1
            else:
                active_records.append(latest)
                if latest.status == 'corrected':
                    audit_info['corrections'] += 1
            
            if len(versions) > 1:
                audit_info['duplicates_kept'] += 1
        
        return active_records, audit_info
    
    def write_output(self, active_records: List[InventoryRecord]) -> None:
        """Write standardized records to TSV file."""
        output_file = self.output_dir / 'inventory_standardized.tsv'
        
        fieldnames = ['date', 'title', 'object_number', 'link', 'status']
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                
                for record in sorted(active_records, key=lambda r: r.date_standardized or ''):
                    writer.writerow(record.to_dict())
            
            print(f"✓ Wrote {len(active_records)} records to {output_file.name}")
        
        except IOError as e:
            print(f"Error writing output: {e}", file=sys.stderr)
    
    def generate_audit_report(self, audit_info: Dict) -> None:
        """Generate detailed audit report."""
        report_file = self.output_dir / 'audit_report.txt'
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("MUSEUM INVENTORY STANDARDIZATION AUDIT REPORT\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"Input file: {self.input_file}\n")
                f.write(f"Processed: {datetime.now().isoformat()}\n\n")
                
                # Summary
                f.write("SUMMARY\n")
                f.write("-" * 60 + "\n")
                f.write(f"Total records read:        {len(self.records)}\n")
                f.write(f"Valid records:             {len(self.valid_records)}\n")
                f.write(f"Invalid records:           {len(self.invalid_records)}\n")
                f.write(f"Active records (output):   {len(self.valid_records) - audit_info['corrections'] - audit_info['withdrawn']}\n")
                f.write(f"\nCorrections applied:       {audit_info['corrections']}\n")
                f.write(f"Records withdrawn:         {audit_info['withdrawn']}\n")
                f.write(f"Duplicate handling:        {audit_info['duplicates_kept']} objects had multiple versions\n\n")
                
                # Errors
                if self.invalid_records:
                    f.write("ERRORS\n")
                    f.write("-" * 60 + "\n")
                    for record in self.invalid_records:
                        f.write(f"Row {record.row_num}:\n")
                        for error in record.errors:
                            f.write(f"  • {error}\n")
                        f.write("\n")
                
                # Warnings
                warnings_found = [r for r in self.valid_records if r.warnings]
                if warnings_found:
                    f.write("WARNINGS\n")
                    f.write("-" * 60 + "\n")
                    for record in warnings_found:
                        f.write(f"Row {record.row_num} ({record.object_number_standardized}):\n")
                        for warning in record.warnings:
                            f.write(f"  ⚠ {warning}\n")
                        f.write("\n")
            
            print(f"✓ Audit report written to {report_file.name}")
        
        except IOError as e:
            print(f"Error writing audit report: {e}", file=sys.stderr)
    
    def run(self) -> bool:
        """Execute the full standardization process."""
        print(f"Standardizing museum inventory from: {self.input_file}\n")
        
        if not self.read_input():
            return False
        
        self.process_records()
        active_records, audit_info = self.handle_corrections_and_withdrawals()
        
        self.write_output(active_records)
        self.generate_audit_report(audit_info)
        
        print("\n✓ Standardization complete!")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records from a TSV file'
    )
    parser.add_argument(
        'input',
        type=str,
        help='Input TSV file with inventory records'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='./standardized_inventory',
        help='Output directory (default: ./standardized_inventory)'
    )
    
    args = parser.parse_args()
    
    standardizer = InventoryStandardizer(args.input, args.output)
    success = standardizer.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Usage

**Basic usage:**
```bash
python standardize_inventory.py records.tsv
```

**Specify output directory:**
```bash
python standardize_inventory.py records.tsv -o /path/to/output
```

## Input TSV Format

The script expects a TSV file with these columns:

```
date	title	object_number	link	status
01/15/2023	Ancient Vase	2023-001	https://museum.org/objects/2023-001	active
2023-02-20	Painting (Corrected)	2023-002	https://museum.org/objects/2023-002	corrected
March 5, 2023	Sculpture (Withdrawn)	2023-003	https://museum.org/objects/2023-003	withdrawn
```

## Features

- **Validation**: Checks required fields and data integrity
- **Date standardization**: Converts multiple date formats to ISO 8601
- **Object number normalization**: Standardizes inconsistent numbering schemes
- **URL validation**: Basic format checking for links
- **Status tracking**: Handles `active`, `corrected`, and `withdrawn` states
- **Duplicate handling**: Keeps only the latest version of each object
- **Audit trail**: Generates detailed report of all changes and issues
- **Error reporting**: Lists validation errors and warnings

## Output Files

1. **inventory_standardized.tsv** - Clean, standardized records
2. **audit_report.txt** - Detailed processing report with errors and warnings
