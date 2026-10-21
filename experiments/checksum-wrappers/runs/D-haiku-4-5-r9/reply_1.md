# Museum Inventory Standardizer

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory spreadsheets (.tsv format).

Handles corrections and withdrawals of entries.
Columns: date, title, object_number, link
"""

import csv
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import re


class InventoryEntry:
    """Represents a single inventory entry."""
    
    def __init__(self, date: str, title: str, object_number: str, link: str):
        self.date = self._standardize_date(date)
        self.title = self._standardize_title(title)
        self.object_number = self._standardize_object_number(object_number)
        self.link = self._standardize_link(link)
        self.is_withdrawn = False
    
    @staticmethod
    def _standardize_date(date: str) -> str:
        """Convert date to ISO format (YYYY-MM-DD)."""
        date = date.strip()
        if not date:
            return ""
        
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
                parsed = datetime.strptime(date, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # If no format matches, return original and log warning
        print(f"Warning: Could not parse date '{date}'. Using original.", file=sys.stderr)
        return date
    
    @staticmethod
    def _standardize_title(title: str) -> str:
        """Clean and normalize title."""
        title = title.strip()
        # Remove extra whitespace
        title = re.sub(r'\s+', ' ', title)
        return title
    
    @staticmethod
    def _standardize_object_number(obj_num: str) -> str:
        """Standardize object number format."""
        obj_num = obj_num.strip().upper()
        # Remove extra spaces but preserve structure
        obj_num = re.sub(r'\s+', ' ', obj_num)
        return obj_num
    
    @staticmethod
    def _standardize_link(link: str) -> str:
        """Validate and clean URL."""
        link = link.strip()
        if not link:
            return ""
        
        # Add protocol if missing
        if link and not link.startswith(('http://', 'https://', 'ftp://')):
            link = 'https://' + link
        
        return link
    
    def to_dict(self) -> Dict:
        """Convert entry to dictionary."""
        return {
            'date': self.date,
            'title': self.title,
            'object_number': self.object_number,
            'link': self.link,
        }
    
    def __repr__(self) -> str:
        status = " [WITHDRAWN]" if self.is_withdrawn else ""
        return f"Entry({self.object_number}, {self.title}){status}"


class InventoryManager:
    """Manages museum inventory with support for corrections and withdrawals."""
    
    def __init__(self):
        self.entries: Dict[str, InventoryEntry] = {}  # Key: object_number
        self.history: List[Tuple[str, str, str]] = []  # (action, object_num, timestamp)
    
    def add_entry(self, entry: InventoryEntry) -> None:
        """Add or update an entry."""
        self.entries[entry.object_number] = entry
        self.history.append(('ADD', entry.object_number, datetime.now().isoformat()))
    
    def correct_entry(self, object_number: str, **kwargs) -> bool:
        """
        Correct an existing entry.
        
        Args:
            object_number: The object number to correct
            **kwargs: Fields to update (date, title, link)
        
        Returns:
            True if correction successful, False if entry not found
        """
        if object_number not in self.entries:
            print(f"Error: Object number '{object_number}' not found.", file=sys.stderr)
            return False
        
        entry = self.entries[object_number]
        
        for field, value in kwargs.items():
            if field == 'date':
                entry.date = entry._standardize_date(value)
            elif field == 'title':
                entry.title = entry._standardize_title(value)
            elif field == 'link':
                entry.link = entry._standardize_link(value)
            else:
                print(f"Warning: Unknown field '{field}'", file=sys.stderr)
        
        self.history.append(('CORRECT', object_number, datetime.now().isoformat()))
        return True
    
    def withdraw_entry(self, object_number: str, reason: str = "") -> bool:
        """
        Mark an entry as withdrawn.
        
        Args:
            object_number: The object number to withdraw
            reason: Optional reason for withdrawal
        
        Returns:
            True if withdrawal successful, False if entry not found
        """
        if object_number not in self.entries:
            print(f"Error: Object number '{object_number}' not found.", file=sys.stderr)
            return False
        
        self.entries[object_number].is_withdrawn = True
        note = f" ({reason})" if reason else ""
        self.history.append(('WITHDRAW', object_number, datetime.now().isoformat()))
        return True
    
    def load_from_tsv(self, filepath: Path) -> int:
        """
        Load entries from TSV file.
        
        Returns:
            Number of entries loaded
        """
        count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            # Validate headers
            expected_headers = {'date', 'title', 'object_number', 'link'}
            if reader.fieldnames and not expected_headers.issubset(set(reader.fieldnames)):
                raise ValueError(f"Invalid headers. Expected: {expected_headers}")
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    entry = InventoryEntry(
                        date=row.get('date', ''),
                        title=row.get('title', ''),
                        object_number=row.get('object_number', ''),
                        link=row.get('link', '')
                    )
                    
                    # Check for withdrawal marker (optional column)
                    if row.get('status', '').lower() == 'withdrawn':
                        entry.is_withdrawn = True
                    
                    self.add_entry(entry)
                    count += 1
                
                except Exception as e:
                    print(f"Error on row {row_num}: {e}", file=sys.stderr)
        
        return count
    
    def save_to_tsv(self, filepath: Path, include_withdrawn: bool = False) -> int:
        """
        Save entries to standardized TSV file.
        
        Args:
            filepath: Output file path
            include_withdrawn: Whether to include withdrawn entries
        
        Returns:
            Number of entries saved
        """
        entries_to_save = [
            entry for entry in self.entries.values()
            if include_withdrawn or not entry.is_withdrawn
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['date', 'title', 'object_number', 'link', 'status']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            
            writer.writeheader()
            for entry in sorted(entries_to_save, key=lambda e: e.date or ''):
                row = entry.to_dict()
                row['status'] = 'withdrawn' if entry.is_withdrawn else 'active'
                writer.writerow(row)
        
        return len(entries_to_save)
    
    def get_report(self) -> str:
        """Generate a summary report."""
        total = len(self.entries)
        withdrawn = sum(1 for e in self.entries.values() if e.is_withdrawn)
        active = total - withdrawn
        
        report = f"""
Inventory Report
================
Total entries: {total}
Active entries: {active}
Withdrawn entries: {withdrawn}

Recent changes:
"""
        for action, obj_num, timestamp in self.history[-10:]:
            report += f"  [{timestamp}] {action}: {obj_num}\n"
        
        return report
    
    def validate(self) -> List[str]:
        """Check for common issues."""
        issues = []
        
        for obj_num, entry in self.entries.items():
            if not entry.date:
                issues.append(f"{obj_num}: Missing date")
            if not entry.title:
                issues.append(f"{obj_num}: Missing title")
            if not entry.object_number:
                issues.append(f"{obj_num}: Missing object number")
            if entry.link and not entry.link.startswith(('http://', 'https://', 'ftp://')):
                issues.append(f"{obj_num}: Invalid URL format")
        
        return issues


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory spreadsheets'
    )
    parser.add_argument('input', type=Path, help='Input TSV file')
    parser.add_argument('-o', '--output', type=Path, help='Output TSV file')
    parser.add_argument('-r', '--report', action='store_true', help='Show report')
    parser.add_argument('-v', '--validate', action='store_true', help='Validate entries')
    parser.add_argument('--withdraw', metavar='OBJECT_NUM', help='Withdraw an entry')
    parser.add_argument('--correct', metavar='OBJECT_NUM', help='Correct an entry')
    parser.add_argument('--title', metavar='TITLE', help='New title (use with --correct)')
    parser.add_argument('--date', metavar='DATE', help='New date (use with --correct)')
    parser.add_argument('--link', metavar='LINK', help='New link (use with --correct)')
    parser.add_argument('--include-withdrawn', action='store_true',
                       help='Include withdrawn entries in output')
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = InventoryManager()
    
    # Load inventory
    print(f"Loading inventory from {args.input}...")
    count = manager.load_from_tsv(args.input)
    print(f"Loaded {count} entries.")
    
    # Handle corrections
    if args.correct:
        corrections = {}
        if args.title:
            corrections['title'] = args.title
        if args.date:
            corrections['date'] = args.date
        if args.link:
            corrections['link'] = args.link
        
        if corrections:
            if manager.correct_entry(args.correct, **corrections):
                print(f"Corrected {args.correct}")
        else:
            print("Error: No corrections specified", file=sys.stderr)
    
    # Handle withdrawals
    if args.withdraw:
        if manager.withdraw_entry(args.withdraw):
            print(f"Withdrawn {args.withdraw}")
    
    # Validate
    if args.validate:
        issues = manager.validate()
        if issues:
            print("\nValidation issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("No validation issues found.")
    
    # Show report
    if args.report:
        print(manager.get_report())
    
    # Save output
    output_path = args.output or args.input.parent / f"{args.input.stem}_standardized.tsv"
    count = manager.save_to_tsv(output_path, include_withdrawn=args.include_withdrawn)
    print(f"\nSaved {count} entries to {output_path}")


if __name__ == '__main__':
    main()
```

## Usage Examples

```bash
# Standardize a file
python museum_inventory.py inventory.tsv -o inventory_standardized.tsv

# Show report and validate
python museum_inventory.py inventory.tsv -r -v

# Correct an entry
python museum_inventory.py inventory.tsv -o output.tsv \
    --correct "OBJ-2024-001" --title "Updated Title" --date "2024-01-15"

# Withdraw an entry
python museum_inventory.py inventory.tsv -o output.tsv --withdraw "OBJ-2024-002"

# Include withdrawn entries in output
python museum_inventory.py inventory.tsv --include-withdrawn -o output.tsv
```

## Sample Input File (inventory.tsv)

```tsv
date	title	object_number	link
1/15/2024	Ancient Vase	OBJ-2024-001	www.museum.org/vase
2024/02/20	Medieval Sword	OBJ-2024-002	https://museum.org/sword
15-03-2024	Renaissance Painting	OBJ-2024-003	museum.org/painting
```

## Features

- ✅ Standardizes dates to ISO format (YYYY-MM-DD)
- ✅ Cleans whitespace and formats titles
- ✅ Normalizes object numbers
- ✅ Validates and fixes URLs
- ✅ Track entry corrections
- ✅ Mark entries as withdrawn
- ✅ Validation reporting
- ✅ History tracking
- ✅ Flexible CLI interface
