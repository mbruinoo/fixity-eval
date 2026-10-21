# Museum Inventory Standardizer

```python
#!/usr/bin/env python3
"""
Standardize museum inventory spreadsheet (.tsv) with handling for corrections and withdrawals.
Columns: date, title, object_number, link
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class InventoryEntry:
    """Represents a standardized inventory entry."""
    date: str
    title: str
    object_number: str
    link: str
    status: str = "active"  # active, corrected, withdrawn
    notes: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'date': self.date,
            'title': self.title,
            'object_number': self.object_number,
            'link': self.link,
            'status': self.status,
            'notes': self.notes
        }


class InventoryStandardizer:
    """Standardizes and deduplicates museum inventory records."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.entries: Dict[str, InventoryEntry] = {}  # keyed by object_number
        self.history: List[Tuple[str, str]] = []  # (action, object_number)

    def log(self, message: str):
        """Print verbose output."""
        if self.verbose:
            print(f"[INFO] {message}", file=sys.stderr)

    def validate_date(self, date_str: str) -> str:
        """Validate and standardize date to ISO 8601 format (YYYY-MM-DD)."""
        if not date_str or not date_str.strip():
            raise ValueError("Date cannot be empty")

        date_str = date_str.strip()

        # Try parsing common formats
        formats = [
            "%Y-%m-%d",      # 2024-01-15
            "%Y/%m/%d",      # 2024/01/15
            "%m/%d/%Y",      # 01/15/2024
            "%m-%d-%Y",      # 01-15-2024
            "%d/%m/%Y",      # 15/01/2024
            "%d-%m-%Y",      # 15-01-2024
            "%Y%m%d",        # 20240115
            "%b %d, %Y",     # Jan 15, 2024
            "%B %d, %Y",     # January 15, 2024
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue

        raise ValueError(f"Could not parse date: {date_str}")

    def validate_object_number(self, obj_num: str) -> str:
        """Validate and standardize object number."""
        if not obj_num or not obj_num.strip():
            raise ValueError("Object number cannot be empty")

        # Remove extra whitespace and normalize
        normalized = " ".join(obj_num.strip().split())

        # Basic validation: should contain alphanumeric characters
        if not any(c.isalnum() for c in normalized):
            raise ValueError(f"Invalid object number: {obj_num}")

        return normalized

    def validate_title(self, title: str) -> str:
        """Validate and standardize title."""
        if not title or not title.strip():
            return "[Untitled]"

        # Remove extra whitespace
        normalized = " ".join(title.strip().split())

        # Capitalize first letter (but preserve intentional case)
        if normalized:
            normalized = normalized[0].upper() + normalized[1:]

        return normalized

    def validate_link(self, link: str) -> str:
        """Validate and standardize link."""
        if not link or not link.strip():
            return ""

        link = link.strip()

        # Add http:// if missing
        if link and not link.startswith(('http://', 'https://', 'ftp://')):
            link = 'https://' + link

        return link

    def process_row(self, row: Dict[str, str], row_num: int) -> Tuple[InventoryEntry, List[str]]:
        """
        Process a single row and return standardized entry and list of warnings.
        """
        warnings = []

        try:
            date = self.validate_date(row.get('date', '').strip())
        except ValueError as e:
            warnings.append(f"Row {row_num}: {e}")
            date = None

        try:
            object_number = self.validate_object_number(row.get('object_number', ''))
        except ValueError as e:
            warnings.append(f"Row {row_num}: {e}")
            return None, warnings

        try:
            title = self.validate_title(row.get('title', ''))
        except ValueError as e:
            warnings.append(f"Row {row_num}: {e}")
            title = "[Invalid Title]"

        link = self.validate_link(row.get('link', ''))

        entry = InventoryEntry(
            date=date or datetime.now().strftime("%Y-%m-%d"),
            title=title,
            object_number=object_number,
            link=link
        )

        return entry, warnings

    def load_tsv(self, filepath: Path) -> List[str]:
        """Load and process TSV file. Returns list of warnings."""
        warnings = []
        required_columns = {'date', 'title', 'object_number', 'link'}

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')

            # Validate columns
            if not reader.fieldnames:
                raise ValueError("Empty file")

            missing = required_columns - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f"Missing required columns: {missing}")

            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                entry, row_warnings = self.process_row(row, row_num)
                warnings.extend(row_warnings)

                if entry is None:
                    continue

                # Check for duplicates and corrections
                if entry.object_number in self.entries:
                    existing = self.entries[entry.object_number]

                    if entry.date > existing.date:
                        # Newer entry - this is a correction
                        self.log(f"Correction detected for {entry.object_number} (date: {entry.date})")
                        existing.status = "corrected"
                        existing.notes = f"Superseded by entry from {entry.date}"
                        self.entries[entry.object_number] = entry
                        entry.notes = f"Corrected from {existing.date}"
                        self.history.append(("corrected", entry.object_number))
                    else:
                        # Older entry - skip as duplicate
                        self.log(f"Duplicate (older) entry for {entry.object_number} - skipping")
                        warnings.append(f"Row {row_num}: Duplicate object number {entry.object_number} - keeping newer entry")
                else:
                    self.entries[entry.object_number] = entry
                    self.history.append(("added", entry.object_number))

        return warnings

    def mark_withdrawn(self, object_numbers: List[str]):
        """Mark entries as withdrawn."""
        for obj_num in object_numbers:
            if obj_num in self.entries:
                self.entries[obj_num].status = "withdrawn"
                self.entries[obj_num].notes = "Withdrawn from collection"
                self.log(f"Marked {obj_num} as withdrawn")
                self.history.append(("withdrawn", obj_num))
            else:
                self.log(f"Warning: Object number {obj_num} not found for withdrawal")

    def get_active_entries(self) -> List[InventoryEntry]:
        """Get only active (non-withdrawn, current) entries."""
        return [e for e in self.entries.values() if e.status == "active"]

    def get_all_entries(self) -> List[InventoryEntry]:
        """Get all entries including corrected and withdrawn."""
        return list(self.entries.values())

    def save_tsv(self, filepath: Path, include_all: bool = False):
        """Save standardized inventory to TSV file."""
        entries = self.get_all_entries() if include_all else self.get_active_entries()

        # Sort by date, then by object number
        entries.sort(key=lambda e: (e.date, e.object_number))

        fieldnames = ['date', 'title', 'object_number', 'link', 'status', 'notes']

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            for entry in entries:
                writer.writerow(entry.to_dict())

        self.log(f"Saved {len(entries)} entries to {filepath}")

    def generate_report(self) -> str:
        """Generate a standardization report."""
        total_entries = len(self.entries)
        active_entries = len(self.get_active_entries())
        corrected = sum(1 for e in self.entries.values() if e.status == "corrected")
        withdrawn = sum(1 for e in self.entries.values() if e.status == "withdrawn")

        report = f"""
INVENTORY STANDARDIZATION REPORT
================================
Total unique entries:  {total_entries}
Active entries:        {active_entries}
Corrected entries:     {corrected}
Withdrawn entries:     {withdrawn}

Processing history:
"""
        action_counts = defaultdict(int)
        for action, _ in self.history:
            action_counts[action] += 1

        for action, count in sorted(action_counts.items()):
            report += f"  {action}: {count}\n"

        return report


def main():
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory spreadsheet (.tsv)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.tsv -o output.tsv
  %(prog)s input.tsv -o output.tsv -w withdrawn.txt -v
  %(prog)s input.tsv -o output.tsv --include-all
        """
    )

    parser.add_argument('input', type=Path, help='Input TSV file')
    parser.add_argument('-o', '--output', type=Path, default=None,
                        help='Output TSV file (default: input_standardized.tsv)')
    parser.add_argument('-w', '--withdrawals', type=Path, default=None,
                        help='File listing object numbers to mark as withdrawn (one per line)')
    parser.add_argument('--include-all', action='store_true',
                        help='Include corrected and withdrawn entries in output')
    parser.add_argument('-r', '--report', type=Path, default=None,
                        help='Save standardization report to file')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()

    # Validate input file
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Set output path
    output_path = args.output or args.input.parent / f"{args.input.stem}_standardized.tsv"

    # Initialize standardizer
    standardizer = InventoryStandardizer(verbose=args.verbose)

    try:
        # Load and process input
        print(f"Loading {args.input}...", file=sys.stderr)
        warnings = standardizer.load_tsv(args.input)

        # Load withdrawals if provided
        if args.withdrawals and args.withdrawals.exists():
            print(f"Loading withdrawals from {args.withdrawals}...", file=sys.stderr)
            with open(args.withdrawals, 'r', encoding='utf-8') as f:
                withdrawn = [line.strip() for line in f if line.strip()]
            standardizer.mark_withdrawn(withdrawn)

        # Print warnings
        if warnings:
            print(f"\nWarnings ({len(warnings)}):", file=sys.stderr)
            for warning in warnings[:10]:  # Show first 10
                print(f"  {warning}", file=sys.stderr)
            if len(warnings) > 10:
                print(f"  ... and {len(warnings) - 10} more", file=sys.stderr)

        # Save output
        print(f"Saving to {output_path}...", file=sys.stderr)
        standardizer.save_tsv(output_path, include_all=args.include_all)

        # Save report if requested
        if args.report:
            report = standardizer.generate_report()
            with open(args.report, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to {args.report}", file=sys.stderr)
        else:
            print(standardizer.generate_report(), file=sys.stderr)

        print("Done!", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## Usage Examples

### Basic standardization:
```bash
python standardize_inventory.py museum_data.tsv -o cleaned_inventory.tsv
```

### With withdrawals file:
```bash
# withdrawals.txt contains object numbers (one per line):
# OBJ-2024-001
# OBJ-2024-042

python standardize_inventory.py museum_data.tsv -o cleaned_inventory.tsv -w withdrawals.txt
```

### Verbose output with report:
```bash
python standardize_inventory.py museum_data.tsv \
  -o cleaned_inventory.tsv \
  -r standardization_report.txt \
  -v
```

### Include all entries (including corrections/withdrawals):
```bash
python standardize_inventory.py museum_data.tsv \
  -o full_inventory.tsv \
  --include-all
```

## Features

✅ **Date standardization** - Converts multiple date formats to ISO 8601 (YYYY-MM-DD)  
✅ **Deduplication** - Identifies and handles duplicate entries  
✅ **Correction tracking** - Newer entries automatically supersede older ones  
✅ **Withdrawals** - Mark entries as withdrawn from collection  
✅ **Data validation** - Normalizes titles, links, and object numbers  
✅ **Detailed reporting** - Processing history and statistics  
✅ **Warning collection** - Reports data quality issues without stopping
