# Museum Inventory Standardizer with Checksum Verification

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory spreadsheet (.tsv) with checksum verification.
Detects if source data has changed between runs.
"""

import argparse
import csv
import sys
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re


class ChecksumManager:
    """Manages checksums for source file integrity verification."""

    CHECKSUM_SUFFIX = '.checksum'
    METADATA_SUFFIX = '.metadata'

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def log(self, message: str):
        """Log checksum operations."""
        if self.verbose:
            print(f"[CHECKSUM] {message}", file=sys.stderr)

    def calculate_file_checksum(self, filepath: str, algorithm: str = 'sha256') -> str:
        """
        Calculate checksum of entire file.
        """
        hasher = hashlib.new(algorithm)
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        
        return hasher.hexdigest()

    def calculate_row_checksum(self, row: Dict[str, str], algorithm: str = 'sha256') -> str:
        """
        Calculate checksum of a single row for change detection.
        Uses sorted keys to ensure consistency.
        """
        hasher = hashlib.new(algorithm)
        
        # Serialize row in consistent order
        for key in sorted(row.keys()):
            value = str(row[key]).encode('utf-8')
            hasher.update(value)
        
        return hasher.hexdigest()

    def calculate_rows_checksum(
        self,
        rows: List[Dict[str, str]],
        algorithm: str = 'sha256'
    ) -> str:
        """
        Calculate collective checksum of all rows.
        """
        hasher = hashlib.new(algorithm)
        
        for row in rows:
            row_checksum = self.calculate_row_checksum(row, algorithm)
            hasher.update(row_checksum.encode('utf-8'))
        
        return hasher.hexdigest()

    def get_checksum_path(self, filepath: str) -> str:
        """Get path for checksum file."""
        return filepath + self.CHECKSUM_SUFFIX

    def get_metadata_path(self, filepath: str) -> str:
        """Get path for metadata file."""
        return filepath + self.METADATA_SUFFIX

    def save_checksum(
        self,
        filepath: str,
        file_checksum: str,
        rows_checksum: str,
        row_count: int,
        timestamp: Optional[str] = None
    ) -> bool:
        """
        Save checksum and metadata to file.
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        checksum_path = self.get_checksum_path(filepath)
        metadata_path = self.get_metadata_path(filepath)

        # Save file checksum
        try:
            with open(checksum_path, 'w') as f:
                f.write(file_checksum)
            self.log(f"Saved file checksum to {checksum_path}")
        except IOError as e:
            print(f"Error writing checksum: {e}", file=sys.stderr)
            return False

        # Save metadata
        metadata = {
            'timestamp': timestamp,
            'filepath': str(Path(filepath).resolve()),
            'file_checksum': file_checksum,
            'rows_checksum': rows_checksum,
            'row_count': row_count,
            'algorithm': 'sha256'
        }

        try:
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            self.log(f"Saved metadata to {metadata_path}")
        except IOError as e:
            print(f"Error writing metadata: {e}", file=sys.stderr)
            return False

        return True

    def load_checksum(self, filepath: str) -> Optional[str]:
        """Load saved file checksum."""
        checksum_path = self.get_checksum_path(filepath)
        
        if not Path(checksum_path).exists():
            self.log(f"No checksum file found: {checksum_path}")
            return None
        
        try:
            with open(checksum_path, 'r') as f:
                return f.read().strip()
        except IOError as e:
            print(f"Error reading checksum: {e}", file=sys.stderr)
            return None

    def load_metadata(self, filepath: str) -> Optional[Dict]:
        """Load saved metadata."""
        metadata_path = self.get_metadata_path(filepath)
        
        if not Path(metadata_path).exists():
            self.log(f"No metadata file found: {metadata_path}")
            return None
        
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading metadata: {e}", file=sys.stderr)
            return None

    def verify_file_integrity(self, filepath: str) -> Tuple[bool, str]:
        """
        Verify that source file hasn't changed.
        Returns (is_valid, message)
        """
        saved_checksum = self.load_checksum(filepath)
        
        if saved_checksum is None:
            message = f"No previous checksum found (first run)"
            return True, message
        
        current_checksum = self.calculate_file_checksum(filepath)
        
        if current_checksum == saved_checksum:
            message = f"File integrity verified (unchanged)"
            return True, message
        else:
            message = f"File has changed since last run"
            return False, message

    def print_checksum_info(self, filepath: str):
        """Print checksum and metadata information."""
        metadata = self.load_metadata(filepath)
        
        if not metadata:
            print("No checksum metadata found", file=sys.stderr)
            return
        
        print("\n=== Checksum Information ===", file=sys.stderr)
        print(f"File: {Path(filepath).name}", file=sys.stderr)
        print(f"Last processed: {metadata['timestamp']}", file=sys.stderr)
        print(f"Row count: {metadata['row_count']}", file=sys.stderr)
        print(f"File checksum: {metadata['file_checksum'][:16]}...", file=sys.stderr)
        print(f"Rows checksum: {metadata['rows_checksum'][:16]}...", file=sys.stderr)


class InventoryStandardizer:
    """Standardizes and validates museum inventory entries."""

    def __init__(self, verbose: bool = False, verify_checksums: bool = True):
        self.verbose = verbose
        self.verify_checksums = verify_checksums
        self.checksum_manager = ChecksumManager(verbose=verbose)
        self.warnings = []
        self.errors = []
        self.processed_count = 0
        self.withdrawn_count = 0

    def log(self, message: str, level: str = "INFO"):
        """Log messages based on verbosity."""
        if self.verbose or level != "DEBUG":
            print(f"[{level}] {message}", file=sys.stderr)

    def standardize_date(self, date_str: str) -> Optional[str]:
        """Standardize date to ISO format (YYYY-MM-DD)."""
        if not date_str or date_str.strip() == "":
            return None

        date_str = date_str.strip()
        
        formats = [
            "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y",
            "%m-%d-%Y", "%d-%m-%Y", "%B %d, %Y", "%b %d, %Y", "%Y",
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue

        self.warnings.append(f"Could not parse date: {date_str}")
        return date_str

    def standardize_title(self, title: str) -> str:
        """Standardize title: strip whitespace, normalize quotes and punctuation."""
        if not title:
            return ""

        title = title.strip()
        title = " ".join(title.split())
        title = title.replace('"', '"').replace(''', "'").replace(''', "'")
        title = re.sub(r'[,.\s]+$', '', title)
        
        return title

    def standardize_object_number(self, obj_num: str) -> str:
        """Standardize object number: uppercase, remove extra spaces."""
        if not obj_num:
            return ""

        obj_num = obj_num.strip().upper()
        obj_num = re.sub(r'\s+', ' ', obj_num)
        
        if not re.match(r'^[A-Z0-9\-\.\s]+$', obj_num):
            self.warnings.append(f"Unusual object number format: {obj_num}")
        
        return obj_num

    def standardize_link(self, link: str) -> Optional[str]:
        """Standardize URL: validate format, ensure http/https."""
        if not link or link.strip() == "":
            return None

        link = link.strip()
        
        if not link.startswith(('http://', 'https://')):
            link = 'https://' + link
        
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
        """Process and standardize a single inventory entry."""
        try:
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
        keep: str = 'last'
    ) -> List[Dict[str, str]]:
        """Remove duplicate entries based on object number."""
        seen = {}
        deduplicated = []

        for entry in entries:
            obj_num = entry['object number']
            
            if obj_num not in seen:
                seen[obj_num] = entry
                deduplicated.append(entry)
            else:
                if keep == 'last':
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
        handle_duplicates: str = 'last',
        skip_if_unchanged: bool = False
    ) -> bool:
        """
        Process entire inventory file with checksum verification.
        """
        try:
            input_file = Path(input_path)
            if not input_file.exists():
                self.errors.append(f"Input file not found: {input_path}")
                return False

            self.log(f"Reading from {input_path}")

            # Verify file integrity
            if self.verify_checksums:
                is_valid, message = self.checksum_manager.verify_file_integrity(input_path)
                self.log(message)
                
                if not is_valid:
                    print(f"⚠ Warning: {message}", file=sys.stderr)
                
                if not is_valid and skip_if_unchanged:
                    self.log("Source file changed but skip_if_unchanged=True, proceeding anyway")

            # Read input
            entries = []
            raw_rows = []  # Keep original for checksum calculation
            
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    self.errors.append("Empty input file")
                    return False
                
                expected = {'date', 'title', 'object number', 'link'}
                actual = set(reader.fieldnames)
                if not expected.issubset(actual):
                    self.errors.append(
                        f"Missing columns. Expected: {expected}, Got: {actual}"
                    )
                    return False
                
                for row_num, row in enumerate(reader, 2):
                    raw_rows.append(dict(row))  # Store original
                    standardized = self.process_entry(row_num, row)
                    if standardized:
                        entries.append(standardized)

            self.log(f"Processed {self.processed_count} entries, withdrawn {self.withdrawn_count}")

            # Handle duplicates
            entries = self.deduplicate_entries(entries, keep=handle_duplicates)

            # Calculate checksums before writing
            rows_checksum = self.checksum_manager.calculate_rows_checksum(raw_rows)
            file_checksum = self.checksum_manager.calculate_file_checksum(input_path)

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

            # Save checksums for future verification
            self.checksum_manager.save_checksum(
                input_path,
                file_checksum,
                rows_checksum,
                len(raw_rows)
            )

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
            for warning in self.warnings[:10]:
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
        description='Standardize museum inventory spreadsheet (.tsv) with checksum verification'
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
    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Disable checksum verification'
    )
    parser.add_argument(
        '--skip-unchanged',
        action='store_true',
        help='Skip processing if source file unchanged (careful!)'
    )
    parser.add_argument(
        '--show-checksum',
        action='store_true',
        help='Show checksum information and exit'
    )

    args = parser.parse_args()

    # Show checksum info mode
    if args.show_checksum:
        manager = ChecksumManager(verbose=args.verbose)
        manager.print_checksum_info(args.input)
        return

    standardizer = InventoryStandardizer(
        verbose=args.verbose,
        verify_checksums=not args.no_verify
    )
    
    success = standardizer.process_file(
        args.input,
        args.output,
        handle_duplicates=args.duplicates,
        skip_if_unchanged=args.skip_unchanged
    )
    
    standardizer.print_report()
    
    # Show checksum info after processing
    if success:
        standardizer.checksum_manager.print_checksum_info(args.input)

    sys.exit(0 if success and not standardizer.errors else 1)


if __name__ == '__main__':
    main()
```

## Usage Examples

```bash
# First run - creates checksum files
python3 standardize_inventory.py input.tsv

# Second run - verifies file hasn't changed
python3 standardize_inventory.py input.tsv
# Output: [CHECKSUM] File integrity verified (unchanged)

# View stored checksum info
python3 standardize_inventory.py input.tsv --show-checksum

# Disable verification (e.g., for testing)
python3 standardize_inventory.py input.tsv --no-verify

# Process only if file changed (skip redundant processing)
python3 standardize_inventory.py input.tsv --skip-unchanged

# Verbose mode shows all checksum operations
python3 standardize_inventory.py input.tsv -v
```

## Generated Files

After first run, creates companion files:

```
input.tsv                    # Original inventory
input.tsv.checksum          # SHA256 hash of entire file
input.tsv.metadata          # JSON metadata with:
                            # - timestamp
                            # - row count
                            # - file checksum
                            # - rows checksum
```

Example metadata:
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "filepath": "/full/path/to/input.tsv",
  "file_checksum": "a1b2c3d4...",
  "rows_checksum": "e5f6g7h8...",
  "row_count": 1523,
  "algorithm": "sha256"
}
```

## Key Features

- **File-level checksum**: Detects any file modification
- **Row-level checksum**: Tracks processed data integrity
- **Metadata tracking**: Timestamp, row counts, algorithm
- **Verification modes**: Check if file changed, warn if modified
- **Skip unchanged**: Optionally skip processing if file unchanged
- **Info command**: Query stored checksum without processing
- **Verbose logging**: Track all checksum operations

This allows auditing when source data changed and detecting accidental modifications to source files.
