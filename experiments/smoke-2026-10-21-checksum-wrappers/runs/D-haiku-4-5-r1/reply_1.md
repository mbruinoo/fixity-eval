# Museum Inventory Standardizer

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory TSV files with support for corrections and withdrawals.

Expected format:
    date | title | object_number | link

Handles:
    - Duplicate entries (keeps latest)
    - Corrections (lines with "CORRECTED" or prefixed with ↑)
    - Withdrawals (lines with "WITHDRAWN")
    - Formatting inconsistencies
"""

import argparse
import csv
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict


class InventoryRecord:
    """Represents a single inventory record."""
    
    def __init__(self, date: str, title: str, object_number: str, link: str, 
                 line_num: int = 0, status: str = "active"):
        self.date = date.strip() if date else ""
        self.title = title.strip() if title else ""
        self.object_number = object_number.strip() if object_number else ""
        self.link = link.strip() if link else ""
        self.line_num = line_num
        self.status = status  # "active", "withdrawn", "corrected"
    
    def is_valid(self) -> bool:
        """Check if record has minimum required fields."""
        return bool(self.object_number)  # Object number is mandatory
    
    def is_withdrawn(self) -> bool:
        """Check if this record is marked as withdrawn."""
        return self.status == "withdrawn"
    
    def is_correction(self) -> bool:
        """Check if this record is marked as a correction."""
        return self.status == "corrected"
    
    def __eq__(self, other):
        """Records are equal if they have the same object number."""
        if not isinstance(other, InventoryRecord):
            return False
        return self.object_number == other.object_number
    
    def __hash__(self):
        return hash(self.object_number)
    
    def __repr__(self):
        return (f"InventoryRecord(date={self.date}, title={self.title}, "
                f"object_number={self.object_number}, status={self.status})")


class InventoryStandardizer:
    """Standardizes and deduplicates museum inventory records."""
    
    def __init__(self, verbose: bool = False):
        self.records: Dict[str, InventoryRecord] = {}
        self.withdrawn: set = set()
        self.verbose = verbose
        self.warnings: List[str] = []
    
    def _parse_status(self, title: str, date: str) -> Tuple[str, str]:
        """
        Extract status markers from title or date field.
        Returns (cleaned_title, status)
        """
        status = "active"
        cleaned_title = title
        
        # Check for withdrawal marker
        if "WITHDRAWN" in cleaned_title.upper():
            status = "withdrawn"
            cleaned_title = cleaned_title.replace("WITHDRAWN", "").strip()
        elif "WITHDRAWN" in date.upper():
            status = "withdrawn"
        
        # Check for correction marker
        if "CORRECTED" in cleaned_title.upper() or "↑" in cleaned_title:
            status = "corrected"
            cleaned_title = cleaned_title.replace("CORRECTED", "").replace("↑", "").strip()
        
        return cleaned_title, status
    
    def add_record(self, date: str, title: str, object_number: str, 
                   link: str, line_num: int = 0) -> None:
        """Add or update a record in the inventory."""
        cleaned_title, status = self._parse_status(title, date)
        
        record = InventoryRecord(date, cleaned_title, object_number, link, 
                                line_num, status)
        
        if not record.is_valid():
            self.warnings.append(
                f"Line {line_num}: Missing object number. Skipping: {title[:50]}"
            )
            return
        
        key = record.object_number
        
        # Handle withdrawals
        if record.is_withdrawn():
            self.withdrawn.add(key)
            if key in self.records:
                del self.records[key]
            if self.verbose:
                print(f"Marked withdrawn: {key}")
            return
        
        # Handle corrections and duplicates
        if key in self.records:
            old_record = self.records[key]
            
            # Determine which record to keep
            if record.is_correction():
                if self.verbose:
                    print(f"Correcting {key}: '{old_record.title}' → '{record.title}'")
                self.records[key] = record
            else:
                # Keep newer record (higher line number)
                if line_num > old_record.line_num:
                    if self.verbose:
                        print(f"Updating {key} (line {old_record.line_num} → {line_num})")
                    self.records[key] = record
                else:
                    if self.verbose:
                        print(f"Keeping earlier record for {key}")
                    self.warnings.append(
                        f"Line {line_num}: Duplicate {key}, keeping earlier version"
                    )
        else:
            self.records[key] = record
    
    def load_tsv(self, filepath: str) -> int:
        """
        Load records from TSV file.
        Returns number of records loaded.
        """
        count = 0
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                
                # Skip header if present
                header = next(reader, None)
                if header and len(header) == 4:
                    if all(h.lower() in ['date', 'title', 'object number', 
                                         'object_number', 'link'] for h in header):
                        if self.verbose:
                            print(f"Header: {header}")
                    else:
                        # Header looks like data, process it
                        self.add_record(*header, line_num=1)
                        count += 1
                
                # Process remaining lines
                for line_num, row in enumerate(reader, start=2):
                    if not row or all(not field.strip() for field in row):
                        continue  # Skip empty lines
                    
                    if len(row) < 4:
                        self.warnings.append(
                            f"Line {line_num}: Incomplete row (expected 4 columns, got {len(row)})"
                        )
                        continue
                    
                    self.add_record(row[0], row[1], row[2], row[3], line_num)
                    count += 1
        
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
        
        return count
    
    def save_tsv(self, filepath: str, include_header: bool = True) -> None:
        """Save standardized records to TSV file."""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter='\t')
                
                if include_header:
                    writer.writerow(['date', 'title', 'object_number', 'link'])
                
                # Sort by object number for consistency
                for record in sorted(self.records.values(), 
                                    key=lambda r: r.object_number):
                    writer.writerow([
                        record.date,
                        record.title,
                        record.object_number,
                        record.link
                    ])
        
        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def get_report(self) -> str:
        """Generate a standardization report."""
        report = []
        report.append("\n" + "="*60)
        report.append("INVENTORY STANDARDIZATION REPORT")
        report.append("="*60)
        report.append(f"Total active records: {len(self.records)}")
        report.append(f"Withdrawn records: {len(self.withdrawn)}")
        report.append(f"Warnings/Issues: {len(self.warnings)}")
        
        if self.warnings:
            report.append("\n--- WARNINGS ---")
            for warning in self.warnings[:20]:  # Show first 20
                report.append(f"  • {warning}")
            if len(self.warnings) > 20:
                report.append(f"  ... and {len(self.warnings) - 20} more")
        
        # Data quality checks
        report.append("\n--- DATA QUALITY ---")
        missing_date = sum(1 for r in self.records.values() if not r.date)
        missing_title = sum(1 for r in self.records.values() if not r.title)
        missing_link = sum(1 for r in self.records.values() if not r.link)
        
        if missing_date:
            report.append(f"  • Records missing date: {missing_date}")
        if missing_title:
            report.append(f"  • Records missing title: {missing_title}")
        if missing_link:
            report.append(f"  • Records missing link: {missing_link}")
        
        if not (missing_date or missing_title or missing_link):
            report.append("  ✓ All required fields present")
        
        report.append("="*60 + "\n")
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory TSV files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python standardizer.py inventory.tsv -o standardized.tsv
  
  # Verbose output with report
  python standardizer.py inventory.tsv -o standardized.tsv -v --report
  
  # Print to stdout
  python standardizer.py inventory.tsv
        """
    )
    
    parser.add_argument('input', help='Input TSV file')
    parser.add_argument('-o', '--output', help='Output TSV file (default: stdout)')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Verbose output')
    parser.add_argument('--report', action='store_true', 
                       help='Print standardization report')
    parser.add_argument('--no-header', action='store_true',
                       help='Do not include header in output')
    
    args = parser.parse_args()
    
    # Process inventory
    standardizer = InventoryStandardizer(verbose=args.verbose)
    
    print(f"Loading {args.input}...", file=sys.stderr)
    count = standardizer.load_tsv(args.input)
    print(f"Loaded {count} records", file=sys.stderr)
    
    # Output
    if args.output:
        standardizer.save_tsv(args.output, include_header=not args.no_header)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        # Print to stdout
        with open(args.output or sys.stdout.fileno(), 'w', newline='', 
                 encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            if not args.no_header:
                writer.writerow(['date', 'title', 'object_number', 'link'])
            for record in sorted(standardizer.records.values(),
                                key=lambda r: r.object_number):
                writer.writerow([record.date, record.title, 
                                record.object_number, record.link])
    
    # Report
    if args.report:
        print(standardizer.get_report(), file=sys.stderr)


if __name__ == '__main__':
    main()
```

## Usage

```bash
# Basic usage
python standardizer.py inventory.tsv -o standardized.tsv

# Verbose with report
python standardizer.py inventory.tsv -o standardized.tsv -v --report

# Print to stdout
python standardizer.py inventory.tsv
```

## Example Input

```tsv
date	title	object_number	link
2024-01-15	Ancient Vase	OBJ-001	https://museum.org/obj1
2024-01-16	Ancient Vase (CORRECTED)	OBJ-001	https://museum.org/obj1-v2
2024-01-17	Duplicate Entry	OBJ-002	https://museum.org/obj2
2024-01-18	Duplicate Entry	OBJ-002	https://museum.org/obj2
2024-01-19	Medieval Sword WITHDRAWN	OBJ-003	https://museum.org/obj3
```

## Features

- ✅ Removes duplicates (keeps latest)
- ✅ Handles corrections (marked with "CORRECTED" or "↑")
- ✅ Processes withdrawals (marked with "WITHDRAWN")
- ✅ Data validation and quality reporting
- ✅ Sorted output by object number
- ✅ Comprehensive warning system
- ✅ Verbose mode for debugging
