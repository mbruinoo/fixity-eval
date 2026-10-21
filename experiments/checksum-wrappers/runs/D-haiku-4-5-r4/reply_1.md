# Museum Inventory Standardizer

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory spreadsheet (.tsv) with handling for corrections and withdrawals.
Columns: date, title, object number, link
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re


class InventoryStandardizer:
    """Standardizes and validates museum inventory entries."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.warnings = []
        self.errors = []
        self.processed_count = 0
        self.withdrawn_count = 0

    def log(self, message: str, level: str = "INFO"):
        """Log messages based on verbosity."""
        if self.verbose or level != "DEBUG":
            print(f"[{level}] {message}", file=sys.stderr)

    def standardize_date(self, date_str: str) -> Optional[str]:
        """
        Standardize date to ISO format (YYYY-MM-DD).
        Returns None if date is invalid or empty.
        """
        if not date_str or date_str.strip() == "":
            return None

        date_str = date_str.strip()
        
        # Common date formats to try
        formats = [
            "%Y-%m-%d",      # ISO format
            "%Y/%m/%d",
            "%m/%d/%Y",      # US format
            "%d/%m/%Y",      # EU format
            "%m-%d-%Y",
            "%d-%m-%Y",
            "%B %d, %Y",     # January 01, 2023
            "%b %d, %Y",     # Jan 01, 2023
            "%Y",            # Year only
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue

        self.warnings.append(f"Could not parse date: {date_str}")
        return date_str  # Return as-is if unparseable

    def standardize_title(self, title: str) -> str:
        """
        Standardize title: strip whitespace, normalize quotes and punctuation.
        """
        if not title:
            return ""

        title = title.strip()
        
        # Normalize whitespace
        title = " ".join(title.split())
        
        # Normalize quotes
        title = title.replace('"', '"').replace(''', "'").replace(''', "'")
        
        # Remove trailing commas and periods (but keep internal ones)
        title = re.sub(r'[,.\s]+$', '', title)
        
        return title

    def standardize_object_number(self, obj_num: str) -> str:
        """
        Standardize object number: uppercase, remove extra spaces, validate format.
        """
        if not obj_num:
            return ""

        obj_num = obj_num.strip().upper()
        
        # Remove extra internal spaces
        obj_num = re.sub(r'\s+', ' ', obj_num)
        
        # Check for common patterns
        if not re.match(r'^[A-Z0-9\-\.\s]+$', obj_num):
            self.warnings.append(f"Unusual object number format: {obj_num}")
        
        return obj_num

    def standardize_link(self, link: str) -> Optional[str]:
        """
        Standardize URL: validate format, ensure http/https.
        Returns None if link is empty or invalid.
        """
        if not link or link.strip() == "":
            return None

        link = link.strip()
        
        # Add https if no protocol
        if not link.startswith(('http://', 'https://')):
            link = 'https://' + link
        
        # Basic URL validation
        if not re.match(r'^https?://', link):
            self.warnings.append(f"Invalid URL format: {link}")
            return None
        
        return link

    def is_withdrawn(self, title: str, object_number: str) -> bool:
        """Check if entry is marked as withdrawn."""
        withdrawn_markers = ['withdrawn', 'removed', 'deleted', 'deaccessioned']
        combined = f"{title} {object_number}".lower()
        return any(marker in combined for marker in withdrawn_markers)

    def process_entry(self, row_num: int, row: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Process and standardize a single inventory entry.
        Returns standardized dict or None if withdrawn.
        """
        try:
            # Check for withdrawal
            if self.is_withdrawn(row.get('title', ''), row.get('object number', '')):
                self.log(f"Row {row_num}: Withdrawn entry - {row.get('object number', 'unknown')}")
                self.withdrawn_count += 1
                return None

            standardized = {
                'date': self.standardize_date(row.get('date', '')) or '',
                'title': self.standardize_title(row.get('title', '')),
                'object number': self.standardize_object_number(row.get('object number', '')),
                'link': self.standardize_link(row.get('link', '')) or '',
            }

            # Validation
            if not standardized['object number']:
                self.errors.append(f"Row {row_num}: Missing object number")
                return None

            if not standardized['title']:
                self.warnings.append(f"Row {row_num}: Missing title")

            self.processed_count += 1
            return standardized

        except Exception as e:
            self.errors.append(f"Row {row_num}: {str(e)}")
            return None

    def deduplicate_entries(
        self, 
        entries: List[Dict[str, str]], 
        keep: str = 'first'
    ) -> List[Dict[str, str]]:
        """
        Remove duplicate entries based on object number.
        keep: 'first', 'last', or 'newest' (by date)
        """
        seen = {}
        deduplicated = []

        for entry in entries:
            obj_num = entry['object number']
            
            if obj_num not in seen:
                seen[obj_num] = entry
                deduplicated.append(entry)
            else:
                # Handle duplicates based on keep strategy
                if keep == 'last':
                    # Replace previous entry
                    idx = deduplicated.index(seen[obj_num])
                    deduplicated[idx] = entry
                    seen[obj_num] = entry
                    self.log(f"Duplicate {obj_num}: keeping newer entry", "DEBUG")
                
                elif keep == 'newest':
                    old_date = seen[obj_num]['date'] or ''
                    new_date = entry['date'] or ''
                    
                    if new_date > old_date:
                        idx = deduplicated.index(seen[obj_num])
                        deduplicated[idx] = entry
                        seen[obj_num] = entry
                        self.log(f"Duplicate {obj_num}: keeping by date", "DEBUG")
                
                else:  # keep == 'first'
                    self.log(f"Duplicate {obj_num}: keeping first entry", "DEBUG")
        
        return deduplicated

    def process_file(
        self,
        input_path: str,
        output_path: str,
        handle_duplicates: str = 'last'
    ) -> bool:
        """
        Process entire inventory file.
        handle_duplicates: 'first', 'last', or 'newest'
        """
        try:
            input_file = Path(input_path)
            if not input_file.exists():
                self.errors.append(f"Input file not found: {input_path}")
                return False

            # Read input
            self.log(f"Reading from {input_path}")
            entries = []
            
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    self.errors.append("Empty input file")
                    return False
                
                # Validate headers
                expected = {'date', 'title', 'object number', 'link'}
                actual = set(reader.fieldnames)
                if not expected.issubset(actual):
                    self.errors.append(
                        f"Missing columns. Expected: {expected}, Got: {actual}"
                    )
                    return False
                
                for row_num, row in enumerate(entries, 1):
                    standardized = self.process_entry(row_num, row)
                    if standardized:
                        entries.append(standardized)

            # Read again properly
            entries = []
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row_num, row in enumerate(reader, 2):  # +2 for header and 1-indexing
                    standardized = self.process_entry(row_num, row)
                    if standardized:
                        entries.append(standardized)

            self.log(f"Processed {self.processed_count} entries, withdrawn {self.withdrawn_count}")

            # Handle duplicates
            entries = self.deduplicate_entries(entries, keep=handle_duplicates)

            # Write output
            self.log(f"Writing to {output_path}")
            output_file = Path(output_path)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['date', 'title', 'object number', 'link'],
                    delimiter='\t'
                )
                writer.writeheader()
                writer.writerows(entries)

            self.log(f"Successfully wrote {len(entries)} entries")
            return True

        except Exception as e:
            self.errors.append(f"Fatal error: {str(e)}")
            return False

    def print_report(self):
        """Print processing report."""
        print("\n=== Processing Report ===", file=sys.stderr)
        print(f"Processed: {self.processed_count}", file=sys.stderr)
        print(f"Withdrawn: {self.withdrawn_count}", file=sys.stderr)
        
        if self.warnings:
            print(f"\n⚠ Warnings ({len(self.warnings)}):", file=sys.stderr)
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  - {warning}", file=sys.stderr)
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more", file=sys.stderr)
        
        if self.errors:
            print(f"\n✗ Errors ({len(self.errors)}):", file=sys.stderr)
            for error in self.errors[:10]:
                print(f"  - {error}", file=sys.stderr)
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory spreadsheet (.tsv)'
    )
    parser.add_argument('input', help='Input TSV file')
    parser.add_argument(
        '-o', '--output',
        default='inventory_standardized.tsv',
        help='Output TSV file (default: inventory_standardized.tsv)'
    )
    parser.add_argument(
        '-d', '--duplicates',
        choices=['first', 'last', 'newest'],
        default='last',
        help='How to handle duplicate object numbers (default: last)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    standardizer = InventoryStandardizer(verbose=args.verbose)
    success = standardizer.process_file(
        args.input,
        args.output,
        handle_duplicates=args.duplicates
    )
    standardizer.print_report()

    sys.exit(0 if success and not standardizer.errors else 1)


if __name__ == '__main__':
    main()
```

## Usage

```bash
# Basic usage
python3 standardize_inventory.py input.tsv

# With custom output and keep last duplicate
python3 standardize_inventory.py input.tsv -o output.tsv -d last

# Verbose mode
python3 standardize_inventory.py input.tsv -v

# Keep oldest version of duplicates
python3 standardize_inventory.py input.tsv -d first

# Keep by date (most recent)
python3 standardize_inventory.py input.tsv -d newest
```

## Features

- **Date standardization**: Multiple input formats → ISO 8601 (YYYY-MM-DD)
- **Title normalization**: Whitespace, quotes, punctuation
- **Object number**: Uppercase, validation, whitespace normalization
- **URL standardization**: Protocol validation, format checking
- **Withdrawal handling**: Detects and removes withdrawn entries
- **Deduplication**: Multiple strategies for handling corrections
- **Error reporting**: Detailed warnings and errors
- **TSV format**: Tab-separated for spreadsheet compatibility

This handles typical museum workflow where entries are corrected or withdrawn over time.
