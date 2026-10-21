# Museum Inventory Standardizer

```python
#!/usr/bin/env python3
"""
Standardize and validate museum inventory spreadsheet (.tsv).
Handles corrections, withdrawals, and data normalization.
"""

import csv
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Set
import argparse


class MuseumInventoryStandardizer:
    """Standardize and validate museum inventory data."""
    
    REQUIRED_COLUMNS = {'date', 'title', 'object_number', 'link'}
    WITHDRAWAL_MARKERS = {'withdrawn', 'deleted', 'removed', 'void'}
    
    def __init__(self, input_file: str, output_file: str = None, 
                 log_file: str = None, keep_history: bool = False):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input .tsv file
            output_file: Path to output .tsv file (default: input_standardized.tsv)
            log_file: Path to log file (default: standardization.log)
            keep_history: Keep all versions or only final (default: False)
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file or 
                               self.input_file.stem + "_standardized.tsv")
        self.log_file = Path(log_file or "standardization.log")
        self.keep_history = keep_history
        
        self.entries: Dict[str, Dict] = {}  # object_number -> entry
        self.history: Dict[str, List[Dict]] = {}  # object_number -> versions
        self.warnings: List[str] = []
        self.errors: List[str] = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log message to file and optionally console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {level}: {message}"
        print(log_message, file=sys.stderr)
        
        with open(self.log_file, 'a') as f:
            f.write(log_message + "\n")
    
    def standardize_date(self, date_str: str) -> str:
        """
        Standardize date to YYYY-MM-DD format.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Standardized date string or empty string if invalid
        """
        if not date_str or date_str.strip() == '':
            return ''
        
        date_str = date_str.strip()
        
        # Common formats to try
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%m-%d-%Y',
            '%d-%m-%Y',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%d %b %Y',
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        self.warnings.append(f"Could not parse date: {date_str}")
        return date_str
    
    def standardize_object_number(self, obj_num: str) -> str:
        """
        Standardize object number.
        Remove extra spaces, normalize separators.
        """
        if not obj_num:
            return ''
        
        obj_num = obj_num.strip()
        # Normalize separators (dots, hyphens, slashes)
        obj_num = re.sub(r'[\s]+', '', obj_num)
        
        return obj_num.upper()
    
    def standardize_title(self, title: str) -> str:
        """
        Standardize title: trim, normalize whitespace.
        """
        if not title:
            return ''
        
        title = title.strip()
        # Normalize multiple spaces to single space
        title = re.sub(r'\s+', ' ', title)
        
        return title
    
    def standardize_link(self, link: str) -> str:
        """
        Standardize URL: trim, validate basic format.
        """
        if not link:
            return ''
        
        link = link.strip()
        
        # Basic URL validation
        if link and not link.startswith(('http://', 'https://')):
            self.warnings.append(f"Link missing protocol: {link}")
        
        return link
    
    def is_withdrawal(self, entry: Dict) -> bool:
        """Check if entry is marked as withdrawn/deleted."""
        for field in entry.values():
            if isinstance(field, str):
                if any(marker in field.lower() for marker in self.WITHDRAWAL_MARKERS):
                    return True
        return False
    
    def read_input(self) -> List[Dict]:
        """Read TSV file and return list of entries."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        entries = []
        try:
            with open(self.input_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    raise ValueError("Empty file or unable to read headers")
                
                # Normalize column names
                reader.fieldnames = [col.lower().strip() for col in reader.fieldnames]
                
                for row_num, row in enumerate(reader, start=2):
                    entry = {k.lower(): v for k, v in row.items()}
                    entries.append(entry)
                    
        except Exception as e:
            self.log(f"Error reading input file: {e}", "ERROR")
            raise
        
        return entries
    
    def process_entries(self, entries: List[Dict]) -> None:
        """
        Process entries: standardize fields, handle corrections/withdrawals.
        Later entries with same object_number override earlier ones.
        """
        for row_num, entry in enumerate(entries, start=2):
            try:
                # Standardize fields
                standardized = {
                    'date': self.standardize_date(entry.get('date', '')),
                    'title': self.standardize_title(entry.get('title', '')),
                    'object_number': self.standardize_object_number(
                        entry.get('object_number', '')
                    ),
                    'link': self.standardize_link(entry.get('link', '')),
                }
                
                # Validate
                if not standardized['object_number']:
                    self.errors.append(
                        f"Row {row_num}: Missing object_number"
                    )
                    continue
                
                obj_num = standardized['object_number']
                
                # Track history if keeping it
                if self.keep_history:
                    if obj_num not in self.history:
                        self.history[obj_num] = []
                    self.history[obj_num].append(standardized)
                
                # Check for withdrawal
                if self.is_withdrawal(standardized):
                    if obj_num in self.entries:
                        self.log(
                            f"Withdrawal: {obj_num} - {self.entries[obj_num]['title']}",
                            "INFO"
                        )
                    del self.entries[obj_num]
                else:
                    # Check if updating existing entry
                    if obj_num in self.entries:
                        old_title = self.entries[obj_num]['title']
                        new_title = standardized['title']
                        if old_title != new_title:
                            self.log(
                                f"Updated: {obj_num} - '{old_title}' -> '{new_title}'",
                                "INFO"
                            )
                    
                    self.entries[obj_num] = standardized
                    
            except Exception as e:
                self.log(f"Error processing row {row_num}: {e}", "ERROR")
                self.errors.append(f"Row {row_num}: {e}")
    
    def validate_entries(self) -> None:
        """Validate processed entries."""
        for obj_num, entry in self.entries.items():
            # Check for empty required fields
            for field in ['date', 'title', 'object_number']:
                if not entry.get(field, '').strip():
                    self.warnings.append(
                        f"Object {obj_num}: Missing {field}"
                    )
            
            # Check date format
            if entry.get('date') and not self._is_valid_date_format(entry['date']):
                self.warnings.append(
                    f"Object {obj_num}: Invalid date format: {entry['date']}"
                )
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """Check if date matches YYYY-MM-DD format."""
        return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', date_str))
    
    def write_output(self) -> None:
        """Write standardized entries to output TSV file."""
        if not self.entries:
            self.log("No entries to write", "WARNING")
            return
        
        try:
            # Sort by object number for consistent output
            sorted_entries = sorted(
                self.entries.values(),
                key=lambda x: x['object_number']
            )
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['date', 'title', 'object_number', 'link'],
                    delimiter='\t'
                )
                writer.writeheader()
                writer.writerows(sorted_entries)
            
            self.log(
                f"Output written: {self.output_file} "
                f"({len(sorted_entries)} entries)",
                "INFO"
            )
        except Exception as e:
            self.log(f"Error writing output: {e}", "ERROR")
            raise
    
    def write_history(self) -> None:
        """Write entry history to separate file."""
        if not self.keep_history or not self.history:
            return
        
        history_file = self.output_file.stem + "_history.tsv"
        
        try:
            with open(history_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['object_number', 'version', 'date', 'title', 'link'],
                    delimiter='\t'
                )
                writer.writeheader()
                
                for obj_num in sorted(self.history.keys()):
                    for version, entry in enumerate(self.history[obj_num], 1):
                        row = {
                            'object_number': obj_num,
                            'version': version,
                            'date': entry['date'],
                            'title': entry['title'],
                            'link': entry['link'],
                        }
                        writer.writerow(row)
            
            self.log(f"History written: {history_file}", "INFO")
        except Exception as e:
            self.log(f"Error writing history: {e}", "ERROR")
    
    def print_report(self) -> None:
        """Print standardization report."""
        print("\n" + "="*60)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("="*60)
        print(f"\nInput file: {self.input_file}")
        print(f"Output file: {self.output_file}")
        print(f"Log file: {self.log_file}")
        print(f"\nEntries processed: {len(self.entries)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Errors: {len(self.errors)}")
        
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        if self.errors:
            print("\nErrors:")
            for error in self.errors[:10]:
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        
        print("\n" + "="*60 + "\n")
    
    def standardize(self) -> bool:
        """
        Main standardization process.
        
        Returns:
            True if successful, False if there were errors
        """
        try:
            self.log(f"Starting standardization of {self.input_file}", "INFO")
            
            # Clear log file
            self.log_file.write_text("")
            
            # Read and process
            entries = self.read_input()
            self.log(f"Read {len(entries)} entries", "INFO")
            
            self.process_entries(entries)
            self.validate_entries()
            self.write_output()
            
            if self.keep_history:
                self.write_history()
            
            self.print_report()
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.log(f"Standardization failed: {e}", "ERROR")
            return False


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory spreadsheet"
    )
    parser.add_argument('input_file', help="Input TSV file")
    parser.add_argument('-o', '--output', help="Output TSV file")
    parser.add_argument('-l', '--log', help="Log file path")
    parser.add_argument(
        '--keep-history',
        action='store_true',
        help="Keep revision history"
    )
    
    args = parser.parse_args()
    
    standardizer = MuseumInventoryStandardizer(
        input_file=args.input_file,
        output_file=args.output,
        log_file=args.log,
        keep_history=args.keep_history
    )
    
    success = standardizer.standardize()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Example Usage

```bash
# Basic usage
python standardize_inventory.py inventory.tsv

# Custom output and logging
python standardize_inventory.py inventory.tsv -o output.tsv -l errors.log

# Keep revision history
python standardize_inventory.py inventory.tsv --keep-history
```

## Example Input TSV

```
date	title	object_number	link
2023-01-15	Ancient Vase	POT-001	https://museum.org/pot-001
1/20/2023	Greek Sculpture	SCULPT-002	https://museum.org/sculpt-002
2023-01-25	Withdrawn	POT-001	withdrawn
2023-02-01	Roman Coin	COIN-003	https://museum.org/coin-003
```

## Features

- **Date standardization**: Parses multiple date formats → YYYY-MM-DD
- **Withdrawal handling**: Removes entries marked as withdrawn/deleted/removed
- **Correction tracking**: Later entries override earlier ones with same object number
- **Validation**: Checks for required fields, invalid formats
- **History tracking**: Optional revision history output
- **Comprehensive logging**: All changes logged to file
- **Duplicate normalization**: Standardizes object numbers, trims titles
- **URL validation**: Basic URL format checking
