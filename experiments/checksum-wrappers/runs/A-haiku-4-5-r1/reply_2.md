# Museum Inventory Standardizer with Checksum Verification

Here's an enhanced version that incorporates checksums for data integrity verification:

```python
#!/usr/bin/env python3
"""
Museum Inventory Spreadsheet Standardizer with Checksum Verification

Standardizes TSV files and maintains checksums to detect source data changes.
"""

import sys
import csv
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import argparse


class ChecksumManager:
    """Manages checksums for data integrity verification."""
    
    def __init__(self, checksum_dir: Path = None):
        """
        Initialize checksum manager.
        
        Args:
            checksum_dir: Directory to store checksum files (default: .checksums)
        """
        self.checksum_dir = checksum_dir or Path('.checksums')
        self.checksum_dir.mkdir(exist_ok=True)
    
    def compute_file_checksum(self, file_path: Path, algorithm: str = 'sha256') -> str:
        """
        Compute checksum of entire file.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm ('md5', 'sha1', 'sha256')
            
        Returns:
            Hex digest of file
        """
        hash_func = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    def compute_row_checksum(self, row: Dict[str, str], algorithm: str = 'sha256') -> str:
        """
        Compute checksum of a data row.
        
        Checksums raw, unmodified row data to detect source changes.
        
        Args:
            row: Dictionary of row data
            algorithm: Hash algorithm
            
        Returns:
            Hex digest of row
        """
        # Sort keys for consistent ordering
        sorted_row = json.dumps(row, sort_keys=True, separators=(',', ':'))
        
        hash_func = hashlib.new(algorithm)
        hash_func.update(sorted_row.encode('utf-8'))
        
        return hash_func.hexdigest()
    
    def get_checksum_file(self, source_file: Path) -> Path:
        """
        Get path to checksum file for a source file.
        
        Args:
            source_file: Original source file
            
        Returns:
            Path to checksum metadata file
        """
        return self.checksum_dir / f"{source_file.name}.checksums.json"
    
    def save_checksums(self, source_file: Path, checksums: Dict) -> None:
        """
        Save checksums to file.
        
        Args:
            source_file: Original source file
            checksums: Dictionary of checksums
        """
        checksum_file = self.get_checksum_file(source_file)
        
        with open(checksum_file, 'w', encoding='utf-8') as f:
            json.dump(checksums, f, indent=2)
    
    def load_checksums(self, source_file: Path) -> Optional[Dict]:
        """
        Load previously saved checksums.
        
        Args:
            source_file: Original source file
            
        Returns:
            Dictionary of checksums or None if file doesn't exist
        """
        checksum_file = self.get_checksum_file(source_file)
        
        if not checksum_file.exists():
            return None
        
        with open(checksum_file, 'r', encoding='utf-8') as f:
            return json.load(f)


class IntegrityChecker:
    """Checks data integrity and detects changes."""
    
    def __init__(self, checksum_manager: ChecksumManager):
        """
        Initialize integrity checker.
        
        Args:
            checksum_manager: ChecksumManager instance
        """
        self.checksum_manager = checksum_manager
        self.integrity_report = {
            'file_changed': False,
            'row_changes': [],
            'new_rows': [],
            'deleted_rows': [],
            'modified_rows': [],
            'status': 'CLEAN'
        }
    
    def verify_source_file(self, file_path: Path) -> Tuple[bool, str]:
        """
        Verify that source file hasn't changed since last run.
        
        Args:
            file_path: Path to source file
            
        Returns:
            Tuple of (file_unchanged, message)
        """
        previous_checksums = self.checksum_manager.load_checksums(file_path)
        
        if previous_checksums is None:
            return True, "First run - no previous checksum to compare"
        
        current_file_hash = self.checksum_manager.compute_file_checksum(file_path)
        previous_file_hash = previous_checksums.get('file_hash')
        
        if current_file_hash == previous_file_hash:
            return True, "File unchanged"
        else:
            return False, f"File has changed since last run"
    
    def verify_row(self, row: Dict[str, str], row_num: int, 
                   previous_checksums: Optional[Dict]) -> Tuple[str, str]:
        """
        Verify that a row hasn't changed.
        
        Args:
            row: Current row data
            row_num: Row number
            previous_checksums: Previous checksums dictionary
            
        Returns:
            Tuple of (checksum, status_message)
        """
        current_checksum = self.checksum_manager.compute_row_checksum(row)
        
        if previous_checksums is None:
            return current_checksum, 'NEW'
        
        row_checksums = previous_checksums.get('row_checksums', {})
        previous_checksum = row_checksums.get(str(row_num))
        
        if previous_checksum is None:
            return current_checksum, 'NEW'
        elif current_checksum == previous_checksum:
            return current_checksum, 'UNCHANGED'
        else:
            return current_checksum, 'MODIFIED'
    
    def compare_datasets(self, current_rows: List[Dict[str, str]], 
                        previous_checksums: Optional[Dict]) -> None:
        """
        Compare current and previous datasets.
        
        Args:
            current_rows: Current row data
            previous_checksums: Previous checksums
        """
        if previous_checksums is None:
            self.integrity_report['status'] = 'INITIAL_RUN'
            return
        
        previous_count = previous_checksums.get('total_rows', 0)
        current_count = len(current_rows)
        
        if current_count > previous_count:
            self.integrity_report['new_rows'] = list(
                range(previous_count + 2, current_count + 2)  # +2 for 1-indexed and header
            )
        elif current_count < previous_count:
            self.integrity_report['deleted_rows'] = list(
                range(current_count + 2, previous_count + 2)
            )
        
        if not self.integrity_report['new_rows'] and \
           not self.integrity_report['deleted_rows'] and \
           not self.integrity_report['modified_rows']:
            self.integrity_report['status'] = 'CLEAN'
        else:
            self.integrity_report['status'] = 'CHANGES_DETECTED'
            self.integrity_report['file_changed'] = True


class InventoryStandardizer:
    """Standardizes museum inventory data with checksum verification."""
    
    REQUIRED_COLUMNS = ['date', 'title', 'object number', 'link']
    
    def __init__(self, input_file: str, output_file: str = None, 
                 strict: bool = False, verify_checksums: bool = True,
                 checksum_dir: str = None):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file
            strict: If True, skip rows with errors
            verify_checksums: If True, verify source data integrity
            checksum_dir: Directory for checksum files
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self._get_output_path()
        self.strict = strict
        self.verify_checksums = verify_checksums
        
        # Initialize checksum and integrity components
        self.checksum_manager = ChecksumManager(Path(checksum_dir) if checksum_dir else None)
        self.integrity_checker = IntegrityChecker(self.checksum_manager)
        
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_rows': 0,
            'valid_rows': 0,
            'skipped_rows': 0,
            'warnings': 0
        }
    
    def _get_output_path(self) -> Path:
        """Generate output filename."""
        stem = self.input_file.stem
        return self.input_file.parent / f"standardized_{stem}.tsv"
    
    def standardize_date(self, date_str: str) -> Tuple[str, str]:
        """Standardize date to YYYY-MM-DD format."""
        if not date_str or date_str.strip() == '':
            warning = "Missing date"
            self.warnings.append(warning)
            return '', warning
        
        date_str = date_str.strip()
        
        formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
            '%B %d, %Y', '%b %d, %Y', '%d %B %Y', '%d %b %Y', '%Y',
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                if fmt == '%Y':
                    return parsed_date.strftime('%Y-01-01'), \
                           f"Year only: assumed {parsed_date.strftime('%Y-01-01')}"
                return parsed_date.strftime('%Y-%m-%d'), ''
            except ValueError:
                continue
        
        warning = f"Could not parse date: {date_str}"
        self.warnings.append(warning)
        return date_str, warning
    
    def standardize_title(self, title: str) -> Tuple[str, str]:
        """Standardize title formatting."""
        if not title or title.strip() == '':
            warning = "Missing title"
            self.warnings.append(warning)
            return '', warning
        
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)
        
        small_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words = title.split()
        
        if words:
            standardized = [words[0].capitalize()]
            for word in words[1:]:
                standardized.append(word.lower() if word.lower() in small_words else word.capitalize())
            title = ' '.join(standardized)
        
        return title, ''
    
    def standardize_object_number(self, obj_num: str) -> Tuple[str, str]:
        """Standardize object number."""
        if not obj_num or obj_num.strip() == '':
            warning = "Missing object number"
            self.warnings.append(warning)
            return '', warning
        
        obj_num = obj_num.strip()
        obj_num = re.sub(r'\s+', ' ', obj_num)
        obj_num = obj_num.strip('.-')
        
        return obj_num, ''
    
    def standardize_link(self, link: str) -> Tuple[str, str]:
        """Standardize and validate URL."""
        if not link or link.strip() == '':
            return '', ''
        
        link = link.strip()
        
        if not link.startswith(('http://', 'https://', 'ftp://')):
            link = 'https://' + link
            warning = f"Added https:// protocol"
            self.warnings.append(warning)
        
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, link):
            warning = f"Invalid URL format: {link}"
            self.warnings.append(warning)
        
        return link, ''
    
    def validate_row(self, row: Dict[str, str], row_num: int) -> bool:
        """Validate a data row."""
        for col in self.REQUIRED_COLUMNS:
            if col not in row:
                self.errors.append(f"Row {row_num}: Missing column '{col}'")
                return False
        
        if not row.get('date', '').strip() and not row.get('title', '').strip():
            self.errors.append(f"Row {row_num}: Missing both date and title")
            return False
        
        return True
    
    def process_row(self, row: Dict[str, str], row_num: int) -> Tuple[Dict[str, str], bool]:
        """Process and standardize a single row."""
        if not self.validate_row(row, row_num):
            return {}, False
        
        processed = {}
        row_valid = True
        
        processed['date'], date_warning = self.standardize_date(row.get('date', ''))
        if date_warning and self.strict:
            self.errors.append(f"Row {row_num}: {date_warning}")
            row_valid = False
        
        processed['title'], title_warning = self.standardize_title(row.get('title', ''))
        if title_warning and self.strict:
            self.errors.append(f"Row {row_num}: {title_warning}")
            row_valid = False
        
        processed['object number'], obj_warning = self.standardize_object_number(
            row.get('object number', '')
        )
        if obj_warning and self.strict:
            self.errors.append(f"Row {row_num}: {obj_warning}")
            row_valid = False
        
        processed['link'], link_warning = self.standardize_link(row.get('link', ''))
        if link_warning and self.strict:
            self.errors.append(f"Row {row_num}: {link_warning}")
            row_valid = False
        
        return processed, row_valid
    
    def read_input(self) -> List[Dict[str, str]]:
        """Read and parse input TSV file."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        rows = []
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if reader.fieldnames is None:
                    raise ValueError("File appears to be empty")
                
                for row in reader:
                    normalized_row = {k.lower().strip(): v for k, v in row.items()}
                    rows.append(normalized_row)
            
            self.stats['total_rows'] = len(rows)
            return rows
        
        except csv.Error as e:
            raise ValueError(f"Error reading TSV file: {e}")
    
    def write_output(self, rows: List[Dict[str, str]]) -> None:
        """Write standardized data to output file."""
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=self.REQUIRED_COLUMNS,
                delimiter='\t'
            )
            writer.writeheader()
            writer.writerows(rows)
    
    def run(self) -> bool:
        """Run the standardization process."""
        try:
            print(f"Reading from: {self.input_file}")
            rows = self.read_input()
            
            # Check for source file changes
            if self.verify_checksums:
                print("\n[INTEGRITY CHECK]")
                file_unchanged, message = self.integrity_checker.verify_source_file(self.input_file)
                print(f"Source file status: {message}")
                
                if not file_unchanged:
                    print("⚠️  SOURCE DATA HAS CHANGED since last standardization")
                    response = input("Continue? (y/n): ").lower()
                    if response != 'y':
                        print("Aborted.")
                        return False
            
            print(f"\nProcessing {len(rows)} rows...")
            
            # Load previous checksums for comparison
            previous_checksums = None
            if self.verify_checksums:
                previous_checksums = self.checksum_manager.load_checksums(self.input_file)
            
            standardized_rows = []
            current_checksums = {
                'timestamp': datetime.now().isoformat(),
                'file_hash': self.checksum_manager.compute_file_checksum(self.input_file),
                'total_rows': len(rows),
                'row_checksums': {},
                'row_statuses': {}
            }
            
            for i, row in enumerate(rows, start=2):
                # Verify row integrity
                if self.verify_checksums:
                    checksum, status = self.integrity_checker.verify_row(
                        row, i, previous_checksums
                    )
                    current_checksums['row_checksums'][str(i)] = checksum
                    current_checksums['row_statuses'][str(i)] = status
                
                # Process row
                processed_row, is_valid = self.process_row(row, i)
                
                if is_valid:
                    standardized_rows.append(processed_row)
                    self.stats['valid_rows'] += 1
                else:
                    self.stats['skipped_rows'] += 1
            
            # Compare datasets
            if self.verify_checksums:
                self.integrity_checker.compare_datasets(rows, previous_checksums)
            
            self.stats['warnings'] = len(self.warnings)
            
            print(f"Writing to: {self.output_file}")
            self.write_output(standardized_rows)
            
            # Save checksums for next run
            if self.verify_checksums:
                self.checksum_manager.save_checksums(self.input_file, current_checksums)
                print(f"Checksums saved to: {self.checksum_manager.get_checksum_file(self.input_file)}")
            
            self._print_report()
            return True
        
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return False
    
    def _print_report(self) -> None:
        """Print processing report."""
        print("\n" + "="*70)
        print("STANDARDIZATION REPORT")
        print("="*70)
        print(f"Total rows processed:  {self.stats['total_rows']}")
        print(f"Valid rows:            {self.stats['valid_rows']}")
        print(f"Skipped rows:          {self.stats['skipped_rows']}")
        print(f"Warnings:              {self.stats['warnings']}")
        
        # Integrity report
        if self.verify_checksums:
            print("\n[INTEGRITY REPORT]")
            print(f"Status:                {self.integrity_checker.integrity_report['status']}")
            
            if self.integrity_checker.integrity_report['file_changed']:
                print("⚠️  File has changed since last run")
            
            if self.integrity_checker.integrity_report['new_rows']:
                print(f"New rows:              {len(self.integrity_checker.integrity_report['new_rows'])}")
            
            if self.integrity_checker.integrity_report['deleted_rows']:
                print(f"Deleted rows:          {len(self.integrity_checker.integrity_report['deleted_rows'])}")
            
            if self.integrity_checker.integrity_report['modified_rows']:
                print(f"Modified rows:         {len(self.integrity_checker.integrity_report['modified_rows'])}")
        
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        print("="*70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory TSV files with checksum verification'
    )
    parser.add_argument('input', help='Input TSV file')
    parser.add_argument('-o', '--output', help='Output TSV file', default=None)
    parser.add_argument('-s', '--strict', action='store_true',
                       help='Strict mode: skip rows with errors')
    parser.add_argument('--no-checksums', action='store_true',
                       help='Disable checksum verification')
    parser.add_argument('--checksum-dir', help='Directory for checksum files',
                       default=None)
    
    args = parser.parse_args()
    
    standardizer = InventoryStandardizer(
        args.input,
        args.output,
        args.strict,
        verify_checksums=not args.no_checksums,
        checksum_dir=args.checksum_dir
    )
    
    success = standardizer.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Usage Examples

```bash
# Standard run with checksum verification
python standardizer.py inventory.tsv

# First run (creates checksums)
python standardizer.py inventory.tsv -o cleaned.tsv

# Second run (detects changes)
python standardizer.py inventory.tsv

# Disable checksum verification
python standardizer.py inventory.tsv --no-checksums

# Custom checksum directory
python standardizer.py inventory.tsv --checksum-dir ./checksums
```

## Checksum File Output

`.checksums/inventory.tsv.checksums.json`:
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "file_hash": "a1b2c3d4e5f6...",
  "total_rows": 150,
  "row_checksums": {
    "2": "f7e8d9c0b1a2...",
    "3": "c3d4e5f6a7b8...",
    "4": "b8c9d0e1f2a3..."
  },
  "row_statuses": {
    "2": "UNCHANGED",
    "3": "MODIFIED",
    "4": "NEW"
  }
}
```

## Key Features

✅ **File-level checksums** - SHA256 hash of entire file  
✅ **Row-level checksums** - Individual row integrity verification  
✅ **Change detection** - Identifies new, modified, or deleted rows  
✅ **Persistent storage** - Saves checksums for future comparisons  
✅ **User notifications** - Alerts when source data changes  
✅ **Audit trail** - Timestamps for all runs  
✅ **Flexible configuration** - Custom checksum directories  

This approach ensures data integrity and provides an audit trail of changes!
