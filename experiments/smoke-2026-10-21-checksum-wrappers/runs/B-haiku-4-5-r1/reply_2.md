# Museum Inventory Standardization with Checksum Verification

```python
#!/usr/bin/env python3
"""
Script to standardize museum inventory records with checksum verification.

Includes checksums to detect if source data has changed between runs.
"""

import csv
import sys
import re
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import argparse


class ChecksumManager:
    """Manages checksums for inventory records."""

    CHECKSUM_FILE_SUFFIX = '.checksums.json'

    def __init__(self, inventory_file: str):
        """
        Initialize checksum manager.

        Args:
            inventory_file: Path to the inventory TSV file
        """
        self.inventory_file = Path(inventory_file)
        self.checksum_file = Path(
            str(self.inventory_file) + self.CHECKSUM_FILE_SUFFIX
        )
        self.checksums = {}
        self.load_checksums()

    def _compute_record_hash(self, record: Dict) -> str:
        """
        Compute SHA-256 hash of a record.

        Args:
            record: Dictionary with date, title, object_number, link

        Returns:
            Hexadecimal hash string
        """
        # Create a canonical string representation
        canonical = json.dumps(record, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA-256 hash of entire file.

        Args:
            file_path: Path to file

        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b''):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def load_checksums(self) -> bool:
        """
        Load checksums from file if it exists.

        Returns:
            bool: True if loaded successfully
        """
        if not self.checksum_file.exists():
            return False

        try:
            with open(self.checksum_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.checksums = data
            return True
        except Exception as e:
            print(f"Warning: Could not load checksums: {e}", file=sys.stderr)
            return False

    def save_checksums(self) -> bool:
        """
        Save checksums to file.

        Returns:
            bool: True if successful
        """
        try:
            with open(self.checksum_file, 'w', encoding='utf-8') as f:
                json.dump(self.checksums, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving checksums: {e}", file=sys.stderr)
            return False

    def verify_file_integrity(self) -> Tuple[bool, Optional[str]]:
        """
        Verify that the source file hasn't been modified.

        Returns:
            Tuple of (is_valid, message)
        """
        if 'file_hash' not in self.checksums:
            return True, "No previous file hash found (first run)"

        current_hash = self._compute_file_hash(self.inventory_file)
        previous_hash = self.checksums['file_hash']

        if current_hash == previous_hash:
            return True, "Source file unchanged"
        else:
            return False, "Source file has been modified since last run"

    def verify_record_integrity(self, record_num: int, record: Dict) -> Tuple[bool, str]:
        """
        Verify that a specific record hasn't been modified.

        Args:
            record_num: Record number (1-indexed)
            record: Record dictionary

        Returns:
            Tuple of (is_unchanged, message)
        """
        current_hash = self._compute_record_hash(record)
        record_key = f'record_{record_num}'

        if record_key not in self.checksums:
            return True, "New record"

        previous_hash = self.checksums[record_key]

        if current_hash == previous_hash:
            return True, "Unchanged"
        else:
            return False, "Modified since last run"

    def update_checksums(self, records: List[Dict]) -> None:
        """
        Update checksums for all records and file.

        Args:
            records: List of record dictionaries
        """
        # Update record checksums
        for i, record in enumerate(records, 1):
            record_key = f'record_{i}'
            self.checksums[record_key] = self._compute_record_hash(record)

        # Update file hash
        self.checksums['file_hash'] = self._compute_file_hash(self.inventory_file)

        # Add metadata
        self.checksums['_metadata'] = {
            'last_updated': datetime.now().isoformat(),
            'total_records': len(records),
            'inventory_file': str(self.inventory_file)
        }

    def get_record_change_report(self, records: List[Dict]) -> List[Tuple[int, str]]:
        """
        Get report of which records have changed.

        Args:
            records: List of record dictionaries

        Returns:
            List of (record_num, change_status) tuples
        """
        changes = []
        for i, record in enumerate(records, 1):
            is_unchanged, message = self.verify_record_integrity(i, record)
            if not is_unchanged:
                changes.append((i, message))
        return changes


class InventoryStandardizer:
    """Standardizes museum inventory records with checksum verification."""

    def __init__(self, input_file: str, output_file: str = None,
                 verify_checksums: bool = True):
        """
        Initialize the standardizer.

        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file
            verify_checksums: Whether to verify source data checksums
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file or self._default_output_name())
        self.verify_checksums = verify_checksums
        self.checksum_manager = ChecksumManager(str(self.input_file))
        self.records = []
        self.original_records = []
        self.errors = []
        self.warnings = []

    def _default_output_name(self) -> str:
        """Generate default output filename."""
        stem = self.input_file.stem
        return f"{stem}_standardized.tsv"

    def read_inventory(self) -> bool:
        """
        Read inventory from TSV file.

        Returns:
            bool: True if successful
        """
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')

                if reader.fieldnames is None:
                    self.errors.append("Empty file or unable to read headers")
                    return False

                required_fields = {'date', 'title', 'object_number', 'link'}
                if not required_fields.issubset(set(reader.fieldnames or [])):
                    self.errors.append(
                        f"Missing required columns. Expected: {required_fields}"
                    )
                    return False

                for row in reader:
                    self.records.append(row)
                    # Keep copy of original for comparison
                    self.original_records.append(row.copy())

            return True

        except FileNotFoundError:
            self.errors.append(f"File not found: {self.input_file}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading file: {str(e)}")
            return False

    def verify_source_integrity(self) -> bool:
        """
        Verify source data hasn't changed using checksums.

        Returns:
            bool: True if verification passed or skipped
        """
        if not self.verify_checksums:
            return True

        print("Verifying source data integrity...")

        # Check file-level integrity
        is_valid, message = self.checksum_manager.verify_file_integrity()
        print(f"  File hash: {message}")

        if not is_valid:
            self.warnings.append(
                "⚠️  Source file has been modified since last standardization"
            )
            return True  # Still proceed, but warn user

        # Check record-level changes
        changes = self.checksum_manager.get_record_change_report(self.records)
        if changes:
            print(f"\n  ⚠️  {len(changes)} record(s) modified:")
            for record_num, change_msg in changes[:5]:  # Show first 5
                print(f"     Row {record_num}: {change_msg}")
            if len(changes) > 5:
                print(f"     ... and {len(changes) - 5} more")

        return True

    @staticmethod
    def standardize_date(date_str: str) -> Tuple[str, str]:
        """Standardize date to ISO 8601 format."""
        date_str = date_str.strip()

        if not date_str or date_str.lower() in ('unknown', 'n/a', 'none'):
            return '', "Missing date"

        formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
            '%B %d, %Y', '%b %d, %Y', '%d %B %Y', '%d %b %Y', '%Y',
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime('%Y-%m-%d'), ''
            except ValueError:
                continue

        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            return f"{year_match.group()}-01-01", f"Partial date: {date_str}"

        return '', f"Unable to parse date: {date_str}"

    @staticmethod
    def standardize_title(title: str) -> Tuple[str, str]:
        """Standardize title."""
        title = title.strip()

        if not title or title.lower() in ('unknown', 'n/a', 'none', 'untitled'):
            return '', "Missing title"

        title = ' '.join(title.split())

        if title.isupper() and len(title) > 1:
            title = title.title()

        return title, ''

    @staticmethod
    def standardize_object_number(obj_num: str) -> Tuple[str, str]:
        """Standardize object number."""
        obj_num = obj_num.strip()

        if not obj_num or obj_num.lower() in ('unknown', 'n/a', 'none'):
            return '', "Missing object number"

        obj_num = ' '.join(obj_num.split())

        if not re.match(r'^[A-Za-z0-9\.\-/]+$', obj_num):
            return obj_num, f"Unusual characters: {obj_num}"

        return obj_num, ''

    @staticmethod
    def standardize_link(link: str) -> Tuple[str, str]:
        """Standardize link."""
        link = link.strip()

        if not link or link.lower() in ('unknown', 'n/a', 'none', ''):
            return '', "Missing link"

        if not re.match(r'^https?://', link):
            link = 'https://' + link

        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, link):
            return link, f"Invalid URL format: {link}"

        return link, ''

    def standardize_record(self, record: Dict) -> Tuple[Dict, List[str]]:
        """Standardize a single record."""
        warnings = []

        date, date_warn = self.standardize_date(record.get('date', ''))
        if date_warn:
            warnings.append(date_warn)

        title, title_warn = self.standardize_title(record.get('title', ''))
        if title_warn:
            warnings.append(title_warn)

        obj_num, obj_num_warn = self.standardize_object_number(
            record.get('object_number', '')
        )
        if obj_num_warn:
            warnings.append(obj_num_warn)

        link, link_warn = self.standardize_link(record.get('link', ''))
        if link_warn:
            warnings.append(link_warn)

        standardized = {
            'date': date,
            'title': title,
            'object_number': obj_num,
            'link': link
        }

        return standardized, warnings

    def process_inventory(self) -> bool:
        """Process and standardize all inventory records."""
        print(f"Processing {len(self.records)} records...")

        standardized_records = []
        all_warnings = []

        for row_num, record in enumerate(self.records, start=1):
            standardized, warnings = self.standardize_record(record)
            standardized_records.append(standardized)

            for warning in warnings:
                all_warnings.append((row_num, warning))

        self.records = standardized_records

        # Print warnings
        if all_warnings:
            print(f"\n⚠️  Found {len(all_warnings)} data quality issues:")
            for row_num, warning in all_warnings[:10]:  # Show first 10
                print(f"  Row {row_num}: {warning}")
            if len(all_warnings) > 10:
                print(f"  ... and {len(all_warnings) - 10} more")

        return True

    def write_inventory(self) -> bool:
        """Write standardized inventory to TSV file."""
        try:
            fieldnames = ['date', 'title', 'object_number', 'link']

            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(self.records)

            print(f"\n✓ Standardized inventory written to: {self.output_file}")
            return True

        except Exception as e:
            self.errors.append(f"Error writing file: {str(e)}")
            return False

    def update_and_save_checksums(self) -> bool:
        """Update checksums and save them."""
        try:
            self.checksum_manager.update_checksums(self.original_records)
            self.checksum_manager.save_checksums()
            print(f"✓ Checksums saved to: {self.checksum_manager.checksum_file}")
            return True
        except Exception as e:
            self.errors.append(f"Error saving checksums: {str(e)}")
            return False

    def print_errors(self):
        """Print any errors encountered."""
        if self.errors:
            print("\n❌ Errors:", file=sys.stderr)
            for error in self.errors:
                print(f"  {error}", file=sys.stderr)

    def print_warnings(self):
        """Print any warnings."""
        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  {warning}")

    def run(self) -> bool:
        """Execute the standardization pipeline."""
        if not self.read_inventory():
            self.print_errors()
            return False

        if not self.verify_source_integrity():
            self.print_errors()
            return False

        if not self.process_inventory():
            self.print_errors()
            return False

        if not self.write_inventory():
            self.print_errors()
            return False

        if not self.update_and_save_checksums():
            self.print_errors()
            return False

        self.print_warnings()
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records with checksum verification'
    )
    parser.add_argument('input', help='Input TSV file path')
    parser.add_argument(
        '-o', '--output',
        help='Output TSV file path (default: input_standardized.tsv)'
    )
    parser.add_argument(
        '--skip-checksum-verify',
        action='store_true',
        help='Skip checksum verification of source data'
    )
    parser.add_argument(
        '--show-checksums',
        action='store_true',
        help='Display stored checksums and exit'
    )

    args = parser.parse_args()

    # Handle --show-checksums option
    if args.show_checksums:
        manager = ChecksumManager(args.input)
        if manager.checksums:
            print(json.dumps(manager.checksums, indent=2))
        else:
            print("No checksums found")
        return

    standardizer = InventoryStandardizer(
        args.input,
        args.output,
        verify_checksums=not args.skip_checksum_verify
    )

    if standardizer.run():
        print("\n✓ Standardization complete!")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## Key Checksum Features

### 1. **File-Level Checksum**
```python
# Detects if the entire source file has changed
file_hash = SHA-256(inventory.tsv)
```

### 2. **Record-Level Checksums**
```python
# Detects changes to individual records
record_1_hash = SHA-256(json.dumps({"date": "2023-01-15", ...}))
```

### 3. **Checksum Storage**
Stores checksums in `inventory.checksums.json`:
```json
{
  "file_hash": "a1b2c3d4...",
  "record_1": "hash_of_record_1",
  "record_2": "hash_of_record_2",
  "_metadata": {
    "last_updated": "2024-01-15T10:30:00",
    "total_records": 150,
    "inventory_file": "inventory.tsv"
  }
}
```

## Usage

### Standard run with checksum verification:
```bash
python standardize_inventory.py inventory.tsv
```

### Skip checksum verification:
```bash
python standardize_inventory.py inventory.tsv --skip-checksum-verify
```

### View stored checksums:
```bash
python standardize_inventory.py inventory.tsv --show-checksums
```

## How It Works

1. **First Run**: Creates checksums for all records and the file
2. **Subsequent Runs**: 
   - Verifies file hasn't changed since last run
   - Detects which records were modified
   - Warns user if source data changed
   - Updates and saves new checksums

This approach ensures data integrity and helps track when source inventory data has been modified!
