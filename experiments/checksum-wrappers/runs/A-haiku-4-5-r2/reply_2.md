# Museum Inventory Standardizer with Checksum Verification

Here's the enhanced script with comprehensive checksum support:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksum Verification
Standardizes museum inventory TSV files with data integrity verification
"""

import csv
import sys
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse


class ChecksumManager:
    """Manages checksums for data integrity verification."""
    
    CHECKSUM_ALGORITHMS = {
        'md5': hashlib.md5,
        'sha256': hashlib.sha256,
        'sha1': hashlib.sha1,
    }
    
    def __init__(self, algorithm: str = 'sha256'):
        """
        Initialize checksum manager.
        
        Args:
            algorithm: Hash algorithm ('md5', 'sha1', 'sha256')
        """
        if algorithm not in self.CHECKSUM_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        self.algorithm = algorithm
        self.hash_func = self.CHECKSUM_ALGORITHMS[algorithm]
    
    def hash_file(self, filepath: str) -> str:
        """
        Calculate file-level checksum.
        
        Args:
            filepath: Path to file
            
        Returns:
            Hex digest of file hash
        """
        hasher = self.hash_func()
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def hash_row(self, row: Dict[str, str]) -> str:
        """
        Calculate checksum for a single row.
        
        Args:
            row: Dictionary representing a row
            
        Returns:
            Hex digest of row hash
        """
        # Create canonical JSON representation for consistent hashing
        canonical = json.dumps(row, sort_keys=True, separators=(',', ':'))
        hasher = self.hash_func()
        hasher.update(canonical.encode('utf-8'))
        return hasher.hexdigest()
    
    def hash_field(self, value: str) -> str:
        """
        Calculate checksum for a single field.
        
        Args:
            value: Field value
            
        Returns:
            Hex digest of field hash
        """
        hasher = self.hash_func()
        hasher.update(value.encode('utf-8'))
        return hasher.hexdigest()


class ChecksumStore:
    """Manages checksum storage and retrieval."""
    
    def __init__(self, filepath: str, algorithm: str = 'sha256'):
        """
        Initialize checksum store.
        
        Args:
            filepath: Path to checksum store file (.json)
            algorithm: Hash algorithm to use
        """
        self.filepath = filepath
        self.algorithm = algorithm
        self.data = self._load()
    
    def _load(self) -> Dict:
        """Load checksum data from file."""
        if Path(self.filepath).exists():
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._create_empty()
        return self._create_empty()
    
    @staticmethod
    def _create_empty() -> Dict:
        """Create empty checksum structure."""
        return {
            'metadata': {
                'created': datetime.now().isoformat(),
                'updated': datetime.now().isoformat(),
            },
            'files': {},
            'rows': {},
        }
    
    def save(self):
        """Save checksum data to file."""
        self.data['metadata']['updated'] = datetime.now().isoformat()
        
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def get_file_checksum(self, filename: str) -> Optional[str]:
        """Get stored checksum for file."""
        return self.data['files'].get(filename, {}).get('checksum')
    
    def set_file_checksum(self, filename: str, checksum: str, size: int = None):
        """Store checksum for file."""
        self.data['files'][filename] = {
            'checksum': checksum,
            'algorithm': self.algorithm,
            'timestamp': datetime.now().isoformat(),
        }
        if size:
            self.data['files'][filename]['size'] = size
    
    def get_row_checksum(self, object_number: str) -> Optional[str]:
        """Get stored checksum for row (by object number)."""
        return self.data['rows'].get(object_number, {}).get('checksum')
    
    def set_row_checksum(self, object_number: str, checksum: str, original_data: Dict = None):
        """Store checksum for row."""
        self.data['rows'][object_number] = {
            'checksum': checksum,
            'algorithm': self.algorithm,
            'timestamp': datetime.now().isoformat(),
        }
        if original_data:
            self.data['rows'][object_number]['original_data'] = original_data
    
    def verify_file_changed(self, filename: str, new_checksum: str) -> Tuple[bool, Optional[str]]:
        """
        Verify if file has changed.
        
        Args:
            filename: Name of file
            new_checksum: New checksum to verify
            
        Returns:
            Tuple of (has_changed, previous_checksum)
        """
        previous = self.get_file_checksum(filename)
        
        if previous is None:
            return False, None  # No previous record
        
        has_changed = previous != new_checksum
        return has_changed, previous
    
    def verify_row_changed(self, object_number: str, new_checksum: str) -> Tuple[bool, Optional[str]]:
        """
        Verify if row data has changed.
        
        Args:
            object_number: Object number (unique identifier)
            new_checksum: New checksum to verify
            
        Returns:
            Tuple of (has_changed, previous_checksum)
        """
        previous = self.get_row_checksum(object_number)
        
        if previous is None:
            return False, None  # No previous record
        
        has_changed = previous != new_checksum
        return has_changed, previous


class InventoryStandardizer:
    """Standardizes museum inventory data with checksum verification."""
    
    def __init__(
        self,
        input_file: str,
        output_file: str = None,
        verbose: bool = False,
        checksum_file: str = None,
        algorithm: str = 'sha256',
        track_changes: bool = False
    ):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file
            verbose: Enable verbose output
            checksum_file: Path to checksum store file (.json)
            algorithm: Hash algorithm ('md5', 'sha1', 'sha256')
            track_changes: Track which rows have changed
        """
        self.input_file = input_file
        self.output_file = output_file or self._generate_output_filename(input_file)
        self.verbose = verbose
        self.track_changes = track_changes
        
        # Checksum management
        self.checksum_file = checksum_file or self._generate_checksum_filename(input_file)
        self.checksum_manager = ChecksumManager(algorithm=algorithm)
        self.checksum_store = ChecksumStore(self.checksum_file, algorithm=algorithm)
        
        # Statistics and tracking
        self.errors = []
        self.warnings = []
        self.changed_rows = []
        self.new_rows = []
        self.stats = {
            'total_rows': 0,
            'standardized_rows': 0,
            'rows_with_errors': 0,
            'rows_with_warnings': 0,
            'rows_changed': 0,
            'rows_unchanged': 0,
            'new_rows': 0,
        }
    
    @staticmethod
    def _generate_output_filename(input_file: str) -> str:
        """Generate output filename from input filename."""
        path = Path(input_file)
        return str(path.parent / f"{path.stem}_standardized.tsv")
    
    @staticmethod
    def _generate_checksum_filename(input_file: str) -> str:
        """Generate checksum filename from input filename."""
        path = Path(input_file)
        return str(path.parent / f"{path.stem}.checksums.json")
    
    def verify_input_file(self) -> bool:
        """
        Verify input file hasn't been modified.
        
        Returns:
            True if file is unchanged or first time processing
        """
        input_path = Path(self.input_file)
        
        if not input_path.exists():
            self.errors.append(f"Input file not found: {self.input_file}")
            return False
        
        # Calculate current file checksum
        current_checksum = self.checksum_manager.hash_file(self.input_file)
        file_size = input_path.stat().st_size
        
        # Check if this is a known file
        has_changed, previous = self.checksum_store.verify_file_changed(
            input_path.name,
            current_checksum
        )
        
        if has_changed:
            self.warnings.append(
                f"⚠️  SOURCE FILE HAS CHANGED\n"
                f"   Previous checksum: {previous}\n"
                f"   Current checksum:  {current_checksum}\n"
                f"   File size: {file_size} bytes"
            )
            if self.verbose:
                print(self.warnings[-1])
            return True  # Continue processing but flag the change
        
        # Store current checksum
        self.checksum_store.set_file_checksum(input_path.name, current_checksum, file_size)
        
        return True
    
    def standardize_date(self, date_str: str) -> Tuple[str, List[str]]:
        """Standardize date to ISO 8601 format (YYYY-MM-DD)."""
        warnings = []
        
        if not date_str or not date_str.strip():
            warnings.append("Missing date")
            return "", warnings
        
        date_str = date_str.strip()
        
        formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d",
            "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y",
            "%Y", "%m/%Y",
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                standardized = parsed_date.strftime("%Y-%m-%d")
                if fmt == "%Y":
                    warnings.append("Date contains only year; assuming January 1")
                    standardized = parsed_date.strftime("%Y-01-01")
                elif fmt == "%m/%Y":
                    warnings.append("Date contains only month/year; assuming first of month")
                    standardized = parsed_date.strftime("%Y-%m-01")
                return standardized, warnings
            except ValueError:
                continue
        
        warnings.append(f"Could not parse date: '{date_str}'")
        return date_str, warnings
    
    def standardize_title(self, title: str) -> Tuple[str, List[str]]:
        """Standardize title."""
        warnings = []
        
        if not title or not title.strip():
            warnings.append("Missing title")
            return "", warnings
        
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)
        
        if title.isupper() and len(title) > 3:
            warnings.append("Title is in all caps; consider title case")
        
        if len(title) > 255:
            warnings.append(f"Title exceeds 255 characters ({len(title)})")
        
        return title, warnings
    
    def standardize_object_number(self, obj_num: str) -> Tuple[str, List[str]]:
        """Standardize object number format."""
        warnings = []
        
        if not obj_num or not obj_num.strip():
            warnings.append("Missing object number")
            return "", warnings
        
        obj_num = obj_num.strip()
        obj_num = re.sub(r'\s+', ' ', obj_num)
        
        if not re.search(r'[a-zA-Z0-9]', obj_num):
            warnings.append("Object number contains no alphanumeric characters")
        
        if len(obj_num) > 50:
            warnings.append(f"Object number is very long ({len(obj_num)} chars)")
        
        return obj_num, warnings
    
    def standardize_link(self, link: str) -> Tuple[str, List[str]]:
        """Standardize URL/link format."""
        warnings = []
        
        if not link or not link.strip():
            warnings.append("Missing link")
            return "", warnings
        
        link = link.strip()
        
        url_pattern = r'^https?://'
        
        if link and not re.match(url_pattern, link):
            if link.startswith('www.'):
                warnings.append("URL missing protocol; prepending 'https://'")
                link = f"https://{link}"
            elif '.' in link and '/' in link:
                warnings.append("URL missing protocol; prepending 'https://'")
                link = f"https://{link}"
            else:
                warnings.append(f"Invalid URL format: '{link}'")
        
        return link, warnings
    
    def standardize_row(
        self,
        row: Dict[str, str],
        row_num: int
    ) -> Tuple[Dict[str, str], List[str], str]:
        """
        Standardize a single row and calculate checksum.
        
        Args:
            row: Dictionary with keys: date, title, object number, link
            row_num: Row number (for error reporting)
            
        Returns:
            Tuple of (standardized_row, list_of_warnings, row_checksum)
        """
        all_warnings = []
        standardized_row = {}
        
        # Standardize each field
        date, date_warnings = self.standardize_date(row.get('date', ''))
        standardized_row['date'] = date
        all_warnings.extend([f"Row {row_num} - Date: {w}" for w in date_warnings])
        
        title, title_warnings = self.standardize_title(row.get('title', ''))
        standardized_row['title'] = title
        all_warnings.extend([f"Row {row_num} - Title: {w}" for w in title_warnings])
        
        obj_num, obj_num_warnings = self.standardize_object_number(row.get('object number', ''))
        standardized_row['object number'] = obj_num
        all_warnings.extend([f"Row {row_num} - Object Number: {w}" for w in obj_num_warnings])
        
        link, link_warnings = self.standardize_link(row.get('link', ''))
        standardized_row['link'] = link
        all_warnings.extend([f"Row {row_num} - Link: {w}" for w in link_warnings])
        
        # Calculate row checksum
        row_checksum = self.checksum_manager.hash_row(standardized_row)
        
        return standardized_row, all_warnings, row_checksum
    
    def check_row_changes(
        self,
        object_number: str,
        row_checksum: str,
        original_data: Dict
    ) -> bool:
        """
        Check if row has changed from previous processing.
        
        Args:
            object_number: Object number (unique identifier)
            row_checksum: New row checksum
            original_data: Original row data before standardization
            
        Returns:
            True if row has changed
        """
        has_changed, previous_checksum = self.checksum_store.verify_row_changed(
            object_number,
            row_checksum
        )
        
        if has_changed:
            self.stats['rows_changed'] += 1
            self.changed_rows.append({
                'object_number': object_number,
                'previous_checksum': previous_checksum,
                'new_checksum': row_checksum,
            })
            if self.verbose:
                print(f"  Changed: {object_number}")
            return True
        elif previous_checksum is None:
            self.stats['new_rows'] += 1
            self.new_rows.append({
                'object_number': object_number,
                'checksum': row_checksum,
            })
            if self.verbose:
                print(f"  New: {object_number}")
            return False
        else:
            self.stats['rows_unchanged'] += 1
            if self.verbose:
                print(f"  Unchanged: {object_number}")
            return False
    
    def validate_headers(self, headers: List[str]) -> bool:
        """Validate that required headers are present."""
        required = {'date', 'title', 'object number', 'link'}
        headers_lower = {h.lower().strip() for h in headers}
        
        if not required.issubset(headers_lower):
            missing = required - headers_lower
            self.errors.append(f"Missing required columns: {', '.join(missing)}")
            return False
        
        return True
    
    def process(self) -> bool:
        """
        Process the inventory file with checksum verification.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify input file
            if not self.verify_input_file():
                return False
            
            print(f"Processing {self.input_file}...")
            if self.track_changes:
                print("Change tracking enabled\n")
            
            # Read input file
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    self.errors.append("File is empty or invalid")
                    return False
                
                # Normalize header names
                fieldnames = [h.lower().strip() for h in reader.fieldnames]
                
                if not self.validate_headers(fieldnames):
                    return False
                
                rows = []
                for row_num, row in enumerate(reader, start=2):
                    self.stats['total_rows'] += 1
                    
                    # Normalize row keys to lowercase
                    normalized_row = {k.lower().strip(): v for k, v in row.items()}
                    
                    # Standardize row and get checksum
                    standardized_row, warnings, row_checksum = self.standardize_row(
                        normalized_row,
                        row_num
                    )
                    
                    object_number = standardized_row.get('object number', '')
                    
                    if warnings:
                        self.stats['rows_with_warnings'] += 1
                        self.warnings.extend(warnings)
                    
                    # Check for changes if tracking enabled
                    if self.track_changes and object_number:
                        self.check_row_changes(
                            object_number,
                            row_checksum,
                            normalized_row
                        )
                    
                    # Store row checksum
                    if object_number:
                        self.checksum_store.set_row_checksum(
                            object_number,
                            row_checksum,
                            original_data=normalized_row
                        )
                    
                    rows.append((standardized_row, row_checksum))
                    self.stats['standardized_rows'] += 1
            
            # Write output file
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['date', 'title', 'object number', 'link']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                for row, _ in rows:
                    writer.writerow(row)
            
            # Update output file checksum
            output_checksum = self.checksum_manager.hash_file(self.output_file)
            output_path = Path(self.output_file)
            self.checksum_store.set_file_checksum(
                output_path.name,
                output_checksum,
                output_path.stat().st_size
            )
            
            # Save checksum store
            self.checksum_store.save()
            
            return True
        
        except FileNotFoundError as e:
            self.errors.append(f"File not found: {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"Error processing file: {str(e)}")
            return False
    
    def print_report(self):
        """Print processing report with checksum information."""
        print("\n" + "="*70)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("="*70)
        
        print(f"\nInput file:      {self.input_file}")
        print(f"Output file:     {self.output_file}")
        print(f"Checksum store:  {self.checksum_file}")
        print(f"Algorithm:       {self.checksum_manager.algorithm.upper()}")
        
        print("\n" + "-"*70)
        print("STATISTICS")
        print("-"*70)
        print(f"Total rows processed:    {self.stats['total_rows']}")
        print(f"Rows standardized:       {self.stats['standardized_rows']}")
        print(f"Rows with warnings:      {self.stats['rows_with_warnings']}")
        
        if self.track_changes:
            print(f"\nChange Tracking:")
            print(f"  Rows unchanged:        {self.stats['rows_unchanged']}")
            print(f"  Rows changed:          {self.stats['rows_changed']}")
            print(f"  New rows:              {self.stats['new_rows']}")
            
            if self.changed_rows:
                print(f"\n  Changed rows:")
                for row in self.changed_rows[:5]:
                    print(f"    - {row['object_number']}")
                if len(self.changed_rows) > 5:
                    print(f"    ... and {len(self.changed_rows) - 5} more")
            
            if self.new_rows:
                print(f"\n  New rows:")
                for row in self.new_rows[:5]:
                    print(f"    - {row['object_number']}")
                if len(self.new_rows) > 5:
                    print(f"    ... and {len(self.new_rows) - 5} more")
        
        print("\n" + "-"*70)
        if self.errors:
            print("❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("✓ No errors")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)} total)")
            if self.verbose:
                for warning in self.warnings[:20]:
                    print(f"  - {warning}")
                if len(self.warnings) > 20:
                    print(f"  ... and {len(self.warnings) - 20} more")
            else:
                print("  (use -v for details)")
        
        print("\n" + "="*70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory TSV files with checksum verification"
    )
    parser.add_argument(
        'input_file',
        help='Input TSV file path'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output TSV file path (default: input_file_standardized.tsv)',
        default=None
    )
    parser.add_argument(
        '-c', '--checksums',
        help='Checksum store file path (default: input_file.checksums.json)',
        default=None
    )
    parser.add_argument(
        '-a', '--algorithm',
        choices=['md5', 'sha1', 'sha256'],
        default='sha256',
        help='Hash algorithm (default: sha256)'
    )
    parser.add_argument(
        '-t', '--track-changes',
        action='store_true',
        help='Track which rows have changed since last run'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show all warnings and detailed change tracking'
    )
    
    args = parser.parse_args()
    
    # Create and run standardizer
    standardizer = InventoryStandardizer(
        input_file=args.input_file,
        output_file=args.output,
        checksum_file=args.checksums,
        algorithm=args.algorithm,
        track_changes=args.track_changes,
        verbose=args.verbose
    )
    
    success = standardizer.process()
    standardizer.print_report()
    
    sys.exit(0 if success and not standardizer.errors else 1)


if __name__ == '__main__':
    main()
```

## Usage Examples

```bash
# Basic usage with checksums
python standardizer.py inventory.tsv

# Track changes between runs
python standardizer.py inventory.tsv -t

# Verbose change tracking
python standardizer.py inventory.tsv -t -v

# Use different algorithm
python standardizer.py inventory.tsv -a sha256

# Specify custom checksum file
python standardizer.py inventory.tsv -c my_checksums.json

# Complete example
python standardizer.py inventory.tsv \
  -o standardized.tsv \
  -c checksums.json \
  -a sha256 \
  -t -v
```

## Checksum Store Format

The `.checksums.json` file stores checksums:

```json
{
  "metadata": {
    "created": "2024-01-15T10:30:00.123456",
    "updated": "2024-01-15T10:35:00.654321"
  },
  "files": {
    "inventory.tsv": {
      "checksum": "abc123def456...",
      "algorithm": "sha256",
      "size": 45678,
      "timestamp": "2024-01-15T10:35:00.654321"
    }
  },
  "rows": {
    "2020.001.A": {
      "checksum": "xyz789...",
      "algorithm": "sha256",
      "timestamp": "2024-01-15T10:35:00.654321",
      "original_data": {...}
    }
  }
}
```

## Key Features

✅ **File-level Checksums**: Detect if source file has changed
✅ **Row-level Checksums**: Track individual row changes
✅ **Field-level Checksums**: Verify individual field integrity
✅ **Change Tracking**: Identify new/changed/unchanged rows
✅ **Multiple Algorithms**: MD5, SHA1, SHA256 support
✅ **Persistent Storage**: JSON checksum store for historical tracking
✅ **Detailed Reporting**: Shows what changed and when
✅ **Canonical Hashing**: Consistent hashing regardless of row order

## Benefits

- **Data Integrity**: Detect unauthorized modifications
- **Audit Trail**: Historical record of changes
- **Incremental Updates**: Identify only changed rows
- **Verification**: Confirm data hasn't been corrupted
- **Reproducibility**: Can re-verify standardization
