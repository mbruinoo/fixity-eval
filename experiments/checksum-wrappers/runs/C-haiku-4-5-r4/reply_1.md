# Museum Inventory Standardization Script

```python
#!/usr/bin/env python3
"""
Standardize and validate museum inventory records from a TSV file.

Handles corrections, withdrawals, and standardization of object records.
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


@dataclass
class InventoryRecord:
    """Represents a single inventory record."""
    date: str
    title: str
    object_number: str
    link: str
    
    def __hash__(self):
        return hash(self.object_number)
    
    def __eq__(self, other):
        if not isinstance(other, InventoryRecord):
            return False
        return self.object_number == other.object_number


class InventoryStandardizer:
    """Standardizes and validates museum inventory records."""
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize the standardizer.
        
        Args:
            strict_mode: If True, fail on validation errors. If False, log warnings.
        """
        self.strict_mode = strict_mode
        self.records = {}  # object_number -> InventoryRecord
        self.withdrawn = set()  # Set of withdrawn object_numbers
        self.errors = []
        self.warnings = []
    
    @staticmethod
    def validate_date(date_str: str) -> Optional[str]:
        """
        Validate and standardize date to ISO format (YYYY-MM-DD).
        
        Args:
            date_str: Input date string
            
        Returns:
            Standardized date string or None if invalid
        """
        if not date_str or not date_str.strip():
            return None
        
        date_str = date_str.strip()
        
        # Try common formats
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d-%m-%Y",
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def standardize_object_number(obj_num: str) -> Optional[str]:
        """
        Standardize object number (uppercase, stripped whitespace).
        
        Args:
            obj_num: Object number string
            
        Returns:
            Standardized object number or None if invalid
        """
        if not obj_num or not obj_num.strip():
            return None
        
        standardized = obj_num.strip().upper()
        
        # Remove invalid characters (allow alphanumeric, hyphens, periods)
        if not all(c.isalnum() or c in '-.' for c in standardized):
            return None
        
        return standardized
    
    @staticmethod
    def standardize_title(title: str) -> Optional[str]:
        """
        Standardize title (strip whitespace, verify non-empty).
        
        Args:
            title: Title string
            
        Returns:
            Standardized title or None if invalid
        """
        if not title or not title.strip():
            return None
        
        # Clean up whitespace
        standardized = ' '.join(title.split())
        return standardized if standardized else None
    
    @staticmethod
    def validate_link(link: str) -> bool:
        """
        Validate that link is a proper URL.
        
        Args:
            link: URL string
            
        Returns:
            True if valid URL, False otherwise
        """
        if not link or not link.strip():
            return False
        
        try:
            result = urlparse(link.strip())
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def process_record(self, row: dict, row_num: int) -> Optional[InventoryRecord]:
        """
        Process and validate a single record.
        
        Args:
            row: Dictionary with keys: date, title, object_number, link
            row_num: Row number in source file (for error reporting)
            
        Returns:
            Standardized InventoryRecord or None if invalid
        """
        errors = []
        
        # Validate and standardize each field
        date = self.validate_date(row.get('date', ''))
        if not date:
            errors.append(f"Row {row_num}: Invalid or missing date")
        
        title = self.standardize_title(row.get('title', ''))
        if not title:
            errors.append(f"Row {row_num}: Invalid or missing title")
        
        object_number = self.standardize_object_number(row.get('object_number', ''))
        if not object_number:
            errors.append(f"Row {row_num}: Invalid or missing object_number")
        
        link = row.get('link', '').strip()
        if not self.validate_link(link):
            errors.append(f"Row {row_num}: Invalid or missing link")
        
        # Handle errors
        if errors:
            for error in errors:
                if self.strict_mode:
                    self.errors.append(error)
                else:
                    self.warnings.append(error)
            
            if self.strict_mode:
                return None
        
        if not (date and title and object_number and link):
            return None
        
        return InventoryRecord(
            date=date,
            title=title,
            object_number=object_number,
            link=link
        )
    
    def load_inventory(self, filepath: str) -> bool:
        """
        Load inventory from TSV file.
        
        Args:
            filepath: Path to TSV file
            
        Returns:
            True if successful, False otherwise
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            self.errors.append(f"File not found: {filepath}")
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames or set(reader.fieldnames) != {'date', 'title', 'object_number', 'link'}:
                    self.errors.append(
                        f"Invalid TSV headers. Expected: date, title, object_number, link. "
                        f"Got: {reader.fieldnames}"
                    )
                    return False
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                    record = self.process_record(row, row_num)
                    if record:
                        if record.object_number in self.records:
                            self.warnings.append(
                                f"Row {row_num}: Duplicate object_number {record.object_number}. "
                                f"Updating with new record."
                            )
                        self.records[record.object_number] = record
        
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False
        
        return True
    
    def apply_corrections(self, corrections_filepath: str) -> bool:
        """
        Apply corrections from a corrections file.
        
        Corrections file format (TSV):
        object_number\tfield\tvalue
        
        Fields: date, title, link
        
        Args:
            corrections_filepath: Path to corrections TSV file
            
        Returns:
            True if successful, False otherwise
        """
        corrections_path = Path(corrections_filepath)
        
        if not corrections_path.exists():
            self.errors.append(f"Corrections file not found: {corrections_filepath}")
            return False
        
        try:
            with open(corrections_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames or set(reader.fieldnames) != {'object_number', 'field', 'value'}:
                    self.errors.append(
                        f"Invalid corrections file headers. Expected: object_number, field, value. "
                        f"Got: {reader.fieldnames}"
                    )
                    return False
                
                for row_num, row in enumerate(reader, start=2):
                    obj_num = self.standardize_object_number(row.get('object_number', ''))
                    field = row.get('field', '').strip().lower()
                    value = row.get('value', '').strip()
                    
                    if not obj_num:
                        self.warnings.append(f"Correction row {row_num}: Invalid object_number")
                        continue
                    
                    if obj_num not in self.records:
                        self.warnings.append(
                            f"Correction row {row_num}: object_number {obj_num} not found in inventory"
                        )
                        continue
                    
                    if field not in ['date', 'title', 'link']:
                        self.warnings.append(
                            f"Correction row {row_num}: Unknown field '{field}' for {obj_num}"
                        )
                        continue
                    
                    # Validate and apply correction
                    if field == 'date':
                        standardized = self.validate_date(value)
                        if not standardized:
                            self.warnings.append(
                                f"Correction row {row_num}: Invalid date value '{value}' for {obj_num}"
                            )
                            continue
                        self.records[obj_num].date = standardized
                    
                    elif field == 'title':
                        standardized = self.standardize_title(value)
                        if not standardized:
                            self.warnings.append(
                                f"Correction row {row_num}: Invalid title value '{value}' for {obj_num}"
                            )
                            continue
                        self.records[obj_num].title = standardized
                    
                    elif field == 'link':
                        if not self.validate_link(value):
                            self.warnings.append(
                                f"Correction row {row_num}: Invalid link value '{value}' for {obj_num}"
                            )
                            continue
                        self.records[obj_num].link = value.strip()
        
        except Exception as e:
            self.errors.append(f"Error reading corrections file: {e}")
            return False
        
        return True
    
    def withdraw_records(self, withdrawal_filepath: str) -> bool:
        """
        Mark records as withdrawn.
        
        Withdrawal file format: one object_number per line
        
        Args:
            withdrawal_filepath: Path to withdrawal file
            
        Returns:
            True if successful, False otherwise
        """
        withdrawal_path = Path(withdrawal_filepath)
        
        if not withdrawal_path.exists():
            self.errors.append(f"Withdrawal file not found: {withdrawal_filepath}")
            return False
        
        try:
            with open(withdrawal_path, 'r', encoding='utf-8') as f:
                for row_num, line in enumerate(f, start=1):
                    obj_num = self.standardize_object_number(line.strip())
                    
                    if not obj_num:
                        self.warnings.append(f"Withdrawal row {row_num}: Invalid object_number")
                        continue
                    
                    if obj_num not in self.records:
                        self.warnings.append(
                            f"Withdrawal row {row_num}: object_number {obj_num} not found in inventory"
                        )
                        continue
                    
                    self.withdrawn.add(obj_num)
        
        except Exception as e:
            self.errors.append(f"Error reading withdrawal file: {e}")
            return False
        
        return True
    
    def get_active_records(self) -> dict:
        """
        Get all non-withdrawn records.
        
        Returns:
            Dictionary of object_number -> InventoryRecord
        """
        return {
            obj_num: record
            for obj_num, record in self.records.items()
            if obj_num not in self.withdrawn
        }
    
    def save_inventory(self, output_filepath: str, include_withdrawn: bool = False) -> bool:
        """
        Save standardized inventory to TSV file.
        
        Args:
            output_filepath: Path to output TSV file
            include_withdrawn: Whether to include withdrawn records
            
        Returns:
            True if successful, False otherwise
        """
        try:
            records_to_save = self.records if include_withdrawn else self.get_active_records()
            
            with open(output_filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['date', 'title', 'object_number', 'link'],
                    delimiter='\t'
                )
                writer.writeheader()
                
                for record in sorted(records_to_save.values(), key=lambda r: r.object_number):
                    writer.writerow({
                        'date': record.date,
                        'title': record.title,
                        'object_number': record.object_number,
                        'link': record.link
                    })
        
        except Exception as e:
            self.errors.append(f"Error writing output file: {e}")
            return False
        
        return True
    
    def print_report(self):
        """Print validation report to stdout."""
        print("\n" + "="*60)
        print("INVENTORY STANDARDIZATION REPORT")
        print("="*60)
        
        print(f"\nTotal records processed: {len(self.records)}")
        print(f"Withdrawn records: {len(self.withdrawn)}")
        print(f"Active records: {len(self.get_active_records())}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more warnings")
        
        if not self.errors and not self.warnings:
            print("\n✅ No errors or warnings!")
        
        print("\n" + "="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Standardize and validate museum inventory records'
    )
    parser.add_argument(
        'inventory',
        help='Path to inventory TSV file'
    )
    parser.add_argument(
        '-o', '--output',
        default='inventory_standardized.tsv',
        help='Output file path (default: inventory_standardized.tsv)'
    )
    parser.add_argument(
        '-c', '--corrections',
        help='Path to corrections TSV file'
    )
    parser.add_argument(
        '-w', '--withdrawals',
        help='Path to withdrawals file (one object_number per line)'
    )
    parser.add_argument(
        '--include-withdrawn',
        action='store_true',
        help='Include withdrawn records in output'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Fail on validation warnings (not just errors)'
    )
    
    args = parser.parse_args()
    
    # Initialize standardizer
    standardizer = InventoryStandardizer(strict_mode=args.strict)
    
    # Load inventory
    if not standardizer.load_inventory(args.inventory):
        standardizer.print_report()
        sys.exit(1)
    
    # Apply corrections if provided
    if args.corrections:
        standardizer.apply_corrections(args.corrections)
    
    # Apply withdrawals if provided
    if args.withdrawals:
        standardizer.withdraw_records(args.withdrawals)
    
    # Save standardized inventory
    if not standardizer.save_inventory(args.output, include_withdrawn=args.include_withdrawn):
        standardizer.print_report()
        sys.exit(1)
    
    # Print report
    standardizer.print_report()
    print(f"\n✅ Standardized inventory saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(1 if standardizer.errors else 0)


if __name__ == '__main__':
    main()
```

## Usage Examples

### Basic standardization:
```bash
python standardize_inventory.py inventory.tsv -o inventory_clean.tsv
```

### With corrections:
```bash
python standardize_inventory.py inventory.tsv \
    -o inventory_clean.tsv \
    -c corrections.tsv
```

### With withdrawals:
```bash
python standardize_inventory.py inventory.tsv \
    -o inventory_clean.tsv \
    -w withdrawals.txt
```

### Full workflow:
```bash
python standardize_inventory.py inventory.tsv \
    -o inventory_clean.tsv \
    -c corrections.tsv \
    -w withdrawals.txt
```

### Strict validation mode:
```bash
python standardize_inventory.py inventory.tsv --strict
```

## Example File Formats

**inventory.tsv:**
```
date	title	object_number	link
2023-01-15	Ancient Vase	OBJ-001	https://museum.example.com/obj001
1/20/2023	Medieval Manuscript	OBJ-002	https://museum.example.com/obj002
```

**corrections.tsv:**
```
object_number	field	value
OBJ-001	title	Ancient Greek Vase
OBJ-002	date	2023-01-20
```

**withdrawals.txt:**
```
OBJ-003
OBJ-005
```

This script provides comprehensive validation, flexible input handling, and detailed reporting!
