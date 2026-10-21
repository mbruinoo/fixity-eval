# Museum Inventory Standardizer

Here's a comprehensive script for standardizing museum inventory data:

```python
#!/usr/bin/env python3
"""
Standardize museum inventory spreadsheet (.tsv) with tracking of corrections/withdrawals.
Columns: date, title, object number, link
"""

import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Tuple
import re
from urllib.parse import urlparse


class InventoryEntry:
    """Represents a single inventory entry with validation."""
    
    def __init__(self, date: str, title: str, object_number: str, link: str, 
                 row_num: int = 0, status: str = "active"):
        self.date = date
        self.title = title
        self.object_number = object_number
        self.link = link
        self.row_num = row_num
        self.status = status  # 'active', 'corrected', 'withdrawn'
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def standardize(self) -> None:
        """Apply standardization rules to entry."""
        self._standardize_date()
        self._standardize_title()
        self._standardize_object_number()
        self._standardize_link()
    
    def _standardize_date(self) -> None:
        """Standardize date to YYYY-MM-DD format."""
        if not self.date or self.date.lower() == 'unknown':
            self.warnings.append("Missing date")
            return
        
        date_formats = [
            '%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y',
            '%B %d, %Y', '%b %d, %Y', '%Y', '%m/%d/%y'
        ]
        
        for fmt in date_formats:
            try:
                parsed = datetime.strptime(self.date.strip(), fmt)
                self.date = parsed.strftime('%Y-%m-%d')
                return
            except ValueError:
                continue
        
        self.errors.append(f"Invalid date format: {self.date}")
    
    def _standardize_title(self) -> None:
        """Standardize title: strip whitespace, title case validation."""
        self.title = self.title.strip()
        
        if not self.title:
            self.errors.append("Empty title")
            return
        
        if len(self.title) > 500:
            self.warnings.append(f"Title very long ({len(self.title)} chars)")
        
        # Remove excess whitespace
        self.title = ' '.join(self.title.split())
        
        # Check for all caps or all lowercase (potential issues)
        if self.title.isupper() and len(self.title.split()) > 1:
            self.warnings.append("Title is all uppercase")
        if self.title.islower():
            self.warnings.append("Title is all lowercase")
    
    def _standardize_object_number(self) -> None:
        """Standardize object number format."""
        self.object_number = self.object_number.strip().upper()
        
        if not self.object_number or self.object_number == 'UNKNOWN':
            self.errors.append("Missing or unknown object number")
            return
        
        # Remove common extra characters
        self.object_number = re.sub(r'\s+', ' ', self.object_number)
        
        # Check for duplicates later (in batch processing)
        if not re.match(r'^[\w\-./]+$', self.object_number):
            self.warnings.append(f"Unusual characters in object number: {self.object_number}")
    
    def _standardize_link(self) -> None:
        """Standardize and validate URL."""
        self.link = self.link.strip()
        
        if not self.link or self.link.lower() in ('unknown', 'n/a', ''):
            self.warnings.append("Missing link")
            return
        
        # Add protocol if missing
        if not self.link.startswith(('http://', 'https://')):
            self.link = 'https://' + self.link
            self.warnings.append("Added https:// protocol to link")
        
        # Validate URL structure
        try:
            result = urlparse(self.link)
            if not all([result.scheme, result.netloc]):
                self.errors.append(f"Invalid URL: {self.link}")
        except Exception as e:
            self.errors.append(f"URL parsing error: {e}")
    
    def is_valid(self) -> bool:
        """Return True if entry has no errors."""
        return len(self.errors) == 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'date': self.date,
            'title': self.title,
            'object_number': self.object_number,
            'link': self.link,
            'status': self.status
        }
    
    def __repr__(self) -> str:
        return f"InventoryEntry({self.object_number}, {self.title[:30]}...)"


class InventoryStandardizer:
    """Main standardization and validation engine."""
    
    def __init__(self, input_file: str, output_file: str = None):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self._get_output_path()
        self.entries: List[InventoryEntry] = []
        self.corrections: Dict[str, str] = {}  # object_number -> latest version
        self.withdrawn: Set[str] = set()  # withdrawn object numbers
        self.duplicates: Dict[str, List[int]] = {}  # object_number -> row_nums
        self.report = {
            'total_entries': 0,
            'valid_entries': 0,
            'entries_with_errors': 0,
            'entries_with_warnings': 0,
            'duplicates_found': 0,
            'withdrawn_entries': 0,
        }
    
    def _get_output_path(self) -> Path:
        """Generate output filename."""
        stem = self.input_file.stem
        return self.input_file.parent / f"{stem}_standardized.tsv"
    
    def load(self) -> bool:
        """Load and parse TSV file."""
        if not self.input_file.exists():
            print(f"Error: File not found: {self.input_file}", file=sys.stderr)
            return False
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    print("Error: Empty file", file=sys.stderr)
                    return False
                
                required_cols = {'date', 'title', 'object_number', 'link'}
                if not required_cols.issubset(set(reader.fieldnames)):
                    print(f"Error: Missing required columns. Found: {reader.fieldnames}", 
                          file=sys.stderr)
                    return False
                
                for row_num, row in enumerate(reader, start=2):  # start=2 (header is row 1)
                    entry = InventoryEntry(
                        date=row.get('date', ''),
                        title=row.get('title', ''),
                        object_number=row.get('object_number', ''),
                        link=row.get('link', ''),
                        row_num=row_num
                    )
                    self.entries.append(entry)
            
            self.report['total_entries'] = len(self.entries)
            return True
        
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return False
    
    def standardize(self) -> None:
        """Standardize all entries."""
        for entry in self.entries:
            entry.standardize()
    
    def detect_duplicates(self) -> None:
        """Identify duplicate object numbers (keeping latest by date)."""
        by_number = {}
        
        for entry in self.entries:
            key = entry.object_number
            if key not in by_number:
                by_number[key] = []
            by_number[key].append(entry)
        
        for key, dupes in by_number.items():
            if len(dupes) > 1:
                self.duplicates[key] = [e.row_num for e in dupes]
                self.report['duplicates_found'] += 1
                
                # Mark older entries as corrections (keep newest by date)
                dupes.sort(key=lambda x: x.date, reverse=True)
                for old_entry in dupes[1:]:
                    old_entry.status = 'corrected'
    
    def mark_withdrawn(self, object_numbers: List[str]) -> None:
        """Mark entries as withdrawn."""
        normalized = [num.upper().strip() for num in object_numbers]
        
        for entry in self.entries:
            if entry.object_number in normalized:
                entry.status = 'withdrawn'
                self.withdrawn.add(entry.object_number)
                self.report['withdrawn_entries'] += 1
    
    def validate(self) -> None:
        """Validate all entries and update report."""
        for entry in self.entries:
            if entry.is_valid():
                if entry.status == 'active':
                    self.report['valid_entries'] += 1
            else:
                self.report['entries_with_errors'] += 1
            
            if entry.warnings:
                self.report['entries_with_warnings'] += 1
    
    def save(self, include_status: bool = True, include_errors: bool = True) -> bool:
        """Save standardized inventory to file."""
        try:
            fieldnames = ['date', 'title', 'object_number', 'link']
            if include_status:
                fieldnames.append('status')
            if include_errors:
                fieldnames.extend(['errors', 'warnings'])
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                
                for entry in self.entries:
                    row = {
                        'date': entry.date,
                        'title': entry.title,
                        'object_number': entry.object_number,
                        'link': entry.link,
                    }
                    if include_status:
                        row['status'] = entry.status
                    if include_errors:
                        row['errors'] = '; '.join(entry.errors) if entry.errors else ''
                        row['warnings'] = '; '.join(entry.warnings) if entry.warnings else ''
                    
                    writer.writerow(row)
            
            print(f"✓ Standardized file saved: {self.output_file}")
            return True
        
        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            return False
    
    def save_error_report(self) -> bool:
        """Save detailed error report."""
        report_file = self.input_file.parent / f"{self.input_file.stem}_errors.tsv"
        
        try:
            error_entries = [e for e in self.entries if e.errors or e.warnings]
            
            if not error_entries:
                print("✓ No errors found - no report generated")
                return True
            
            with open(report_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f, 
                    fieldnames=['row', 'object_number', 'title', 'errors', 'warnings'],
                    delimiter='\t'
                )
                writer.writeheader()
                
                for entry in error_entries:
                    writer.writerow({
                        'row': entry.row_num,
                        'object_number': entry.object_number,
                        'title': entry.title[:50],
                        'errors': '; '.join(entry.errors),
                        'warnings': '; '.join(entry.warnings),
                    })
            
            print(f"✓ Error report saved: {report_file}")
            return True
        
        except Exception as e:
            print(f"Error writing report: {e}", file=sys.stderr)
            return False
    
    def save_duplicates_report(self) -> bool:
        """Save report of duplicate object numbers."""
        if not self.duplicates:
            print("✓ No duplicates found - no report generated")
            return True
        
        report_file = self.input_file.parent / f"{self.input_file.stem}_duplicates.tsv"
        
        try:
            with open(report_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(['object_number', 'rows_affected', 'count'])
                
                for obj_num, rows in sorted(self.duplicates.items()):
                    writer.writerow([obj_num, ', '.join(map(str, rows)), len(rows)])
            
            print(f"✓ Duplicates report saved: {report_file}")
            return True
        
        except Exception as e:
            print(f"Error writing duplicates report: {e}", file=sys.stderr)
            return False
    
    def print_summary(self) -> None:
        """Print validation summary."""
        print("\n" + "="*60)
        print("INVENTORY STANDARDIZATION SUMMARY")
        print("="*60)
        print(f"Total entries:           {self.report['total_entries']}")
        print(f"Valid entries:           {self.report['valid_entries']}")
        print(f"Entries with errors:     {self.report['entries_with_errors']}")
        print(f"Entries with warnings:   {self.report['entries_with_warnings']}")
        print(f"Duplicate object numbers:{self.report['duplicates_found']}")
        print(f"Withdrawn entries:       {self.report['withdrawn_entries']}")
        print("="*60 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory spreadsheet',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python standardize_inventory.py inventory.tsv
  python standardize_inventory.py inventory.tsv -o clean_inventory.tsv
  python standardize_inventory.py inventory.tsv -w withdrawn.txt --include-errors
        """
    )
    
    parser.add_argument('input', help='Input TSV file')
    parser.add_argument('-o', '--output', help='Output TSV file (default: input_standardized.tsv)')
    parser.add_argument('-w', '--withdrawn', 
                       help='File with object numbers to mark as withdrawn (one per line)')
    parser.add_argument('--include-errors', action='store_true',
                       help='Include error/warning columns in output')
    parser.add_argument('--error-report', action='store_true',
                       help='Generate separate error report')
    parser.add_argument('--duplicates-report', action='store_true',
                       help='Generate separate duplicates report')
    
    args = parser.parse_args()
    
    # Initialize standardizer
    standardizer = InventoryStandardizer(args.input, args.output)
    
    # Load file
    if not standardizer.load():
        sys.exit(1)
    
    print(f"Loaded {standardizer.report['total_entries']} entries from {args.input}")
    
    # Standardize
    standardizer.standardize()
    print("✓ Standardization complete")
    
    # Detect duplicates
    standardizer.detect_duplicates()
    if standardizer.duplicates:
        print(f"⚠ Found {len(standardizer.duplicates)} object numbers with duplicates")
    
    # Mark withdrawn entries
    if args.withdrawn:
        try:
            with open(args.withdrawn, 'r', encoding='utf-8') as f:
                withdrawn_list = [line.strip() for line in f if line.strip()]
            standardizer.mark_withdrawn(withdrawn_list)
            print(f"✓ Marked {len(withdrawn_list)} entries as withdrawn")
        except FileNotFoundError:
            print(f"Warning: Withdrawn file not found: {args.withdrawn}", file=sys.stderr)
    
    # Validate
    standardizer.validate()
    
    # Save outputs
    standardizer.save(
        include_status=True,
        include_errors=args.include_errors
    )
    
    if args.error_report:
        standardizer.save_error_report()
    
    if args.duplicates_report:
        standardizer.save_duplicates_report()
    
    # Print summary
    standardizer.print_summary()


if __name__ == '__main__':
    main()
```

## Usage Examples

### Basic usage:
```bash
python standardize_inventory.py museum_inventory.tsv
```

### With options:
```bash
# Specify output file
python standardize_inventory.py inventory.tsv -o cleaned.tsv

# Mark entries as withdrawn
python standardize_inventory.py inventory.tsv -w withdrawn_items.txt

# Generate detailed reports
python standardize_inventory.py inventory.tsv --error-report --duplicates-report --include-errors
```

### Withdrawn items file format (`withdrawn.txt`):
```
ACC-2021-001
ACC-2021-015
ACC-2022-003
```

## Features

✅ **Standardization:**
- Dates → YYYY-MM-DD format
- Object numbers → uppercase, normalized
- URLs → standardized with protocol
- Titles → whitespace normalized

✅ **Validation:**
- Format checking for all fields
- Duplicate detection (keeps latest by date)
- Withdrawn entry tracking
- Error and warning reporting

✅ **Output:**
- Standardized TSV with status column
- Separate error reports
- Duplicate detection reports
- Summary statistics
