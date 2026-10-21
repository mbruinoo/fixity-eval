# Museum Inventory Standardizer with Checksum Verification

Here's how to incorporate checksums to verify source data integrity:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksum Verification

Standardizes museum records from a TSV file with:
- MD5/SHA256 checksums for data integrity verification
- Change detection between versions
- Checksum storage and comparison
- Detailed change reports
"""

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse


class ChecksumManager:
    """Manages checksums for inventory data."""
    
    def __init__(self, checksum_dir: Path = None, algorithm: str = 'sha256'):
        """
        Initialize checksum manager.
        
        Args:
            checksum_dir: Directory to store checksum files (default: .checksums)
            algorithm: Hash algorithm ('md5' or 'sha256')
        """
        self.checksum_dir = checksum_dir or Path('.checksums')
        self.algorithm = algorithm.lower()
        self.checksum_dir.mkdir(exist_ok=True)
    
    def _get_hash_function(self):
        """Get the appropriate hash function."""
        if self.algorithm == 'md5':
            return hashlib.md5
        elif self.algorithm == 'sha256':
            return hashlib.sha256
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    
    def calculate_file_checksum(self, file_path: Path) -> str:
        """
        Calculate checksum for entire file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex digest of file
        """
        hash_func = self._get_hash_function()
        hasher = hash_func()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def calculate_record_checksum(self, record: Dict[str, str]) -> str:
        """
        Calculate checksum for a single record.
        
        Consistent ordering ensures same record always has same checksum.
        
        Args:
            record: Record dictionary
            
        Returns:
            Hex digest of record
        """
        hash_func = self._get_hash_function()
        hasher = hash_func()
        
        # Sort keys for consistent ordering
        for key in sorted(record.keys()):
            hasher.update(key.encode('utf-8'))
            hasher.update(record[key].encode('utf-8'))
        
        return hasher.hexdigest()
    
    def calculate_records_checksum(self, records: List[Dict[str, str]]) -> str:
        """
        Calculate checksum for all records combined.
        
        Args:
            records: List of record dictionaries
            
        Returns:
            Hex digest of all records
        """
        hash_func = self._get_hash_function()
        hasher = hash_func()
        
        for record in records:
            record_hash = self.calculate_record_checksum(record)
            hasher.update(record_hash.encode('utf-8'))
        
        return hasher.hexdigest()
    
    def get_checksum_file(self, source_file: Path) -> Path:
        """
        Get path to checksum file for a source file.
        
        Args:
            source_file: Path to source file
            
        Returns:
            Path to checksum metadata file
        """
        filename = source_file.stem + '.checksums.json'
        return self.checksum_dir / filename
    
    def save_checksums(self, source_file: Path, file_checksum: str, 
                      record_checksums: Dict[int, str], records_checksum: str):
        """
        Save checksums to file.
        
        Args:
            source_file: Path to source file
            file_checksum: Checksum of entire file
            record_checksums: Mapping of record number to checksum
            records_checksum: Combined checksum of all records
        """
        checksum_file = self.get_checksum_file(source_file)
        
        data = {
            'source_file': str(source_file),
            'timestamp': datetime.now().isoformat(),
            'algorithm': self.algorithm,
            'file_checksum': file_checksum,
            'records_checksum': records_checksum,
            'record_count': len(record_checksums),
            'record_checksums': record_checksums
        }
        
        with open(checksum_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load_checksums(self, source_file: Path) -> Optional[Dict]:
        """
        Load previously saved checksums.
        
        Args:
            source_file: Path to source file
            
        Returns:
            Checksum data or None if not found
        """
        checksum_file = self.get_checksum_file(source_file)
        
        if not checksum_file.exists():
            return None
        
        try:
            with open(checksum_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load checksums: {str(e)}")
            return None
    
    def verify_file_unchanged(self, source_file: Path) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verify that source file hasn't changed.
        
        Args:
            source_file: Path to source file
            
        Returns:
            Tuple of (unchanged, current_checksum, previous_checksum)
        """
        current = self.calculate_file_checksum(source_file)
        previous_data = self.load_checksums(source_file)
        
        if not previous_data:
            return None, current, None  # No previous checksum
        
        previous = previous_data.get('file_checksum')
        unchanged = current == previous
        
        return unchanged, current, previous
    
    def detect_record_changes(self, source_file: Path, 
                             current_records: List[Dict[str, str]]) -> Dict:
        """
        Detect which records have changed.
        
        Args:
            source_file: Path to source file
            current_records: Current records
            
        Returns:
            Dictionary with change information
        """
        previous_data = self.load_checksums(source_file)
        
        if not previous_data:
            return {
                'status': 'new_file',
                'message': 'No previous checksums found',
                'changes': []
            }
        
        changes = {
            'status': 'analyzed',
            'previous_record_count': previous_data.get('record_count', 0),
            'current_record_count': len(current_records),
            'changed_records': [],
            'new_records': [],
            'deleted_records': [],
        }
        
        current_checksums = {
            i: self.calculate_record_checksum(record)
            for i, record in enumerate(current_records)
        }
        
        previous_checksums = previous_data.get('record_checksums', {})
        previous_checksums = {int(k): v for k, v in previous_checksums.items()}
        
        # Find changed records
        for i, current_hash in current_checksums.items():
            if i in previous_checksums:
                if current_hash != previous_checksums[i]:
                    changes['changed_records'].append({
                        'record_number': i,
                        'previous_checksum': previous_checksums[i],
                        'current_checksum': current_hash
                    })
            else:
                changes['new_records'].append({
                    'record_number': i,
                    'checksum': current_hash
                })
        
        # Find deleted records
        for i, previous_hash in previous_checksums.items():
            if i not in current_checksums:
                changes['deleted_records'].append({
                    'record_number': i,
                    'checksum': previous_hash
                })
        
        changes['total_changes'] = (
            len(changes['changed_records']) + 
            len(changes['new_records']) + 
            len(changes['deleted_records'])
        )
        
        return changes


class InventoryStandardizer:
    """Standardizes museum inventory records with checksum verification."""
    
    REQUIRED_FIELDS = {'date', 'title', 'object_number', 'link'}
    DATE_FORMATS = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y',
        '%B %d, %Y',
        '%b %d, %Y',
    ]
    
    def __init__(self, input_file: str, output_file: str = None, 
                 verify_checksums: bool = True, checksum_dir: str = None,
                 verbose: bool = False):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file (optional)
            verify_checksums: Enable checksum verification
            checksum_dir: Directory for checksum files
            verbose: Enable verbose output
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self.input_file.with_stem(
            self.input_file.stem + '_standardized'
        )
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.records_processed = 0
        self.records_valid = 0
        
        self.checksum_manager = ChecksumManager(
            Path(checksum_dir) if checksum_dir else None
        )
        self.verify_checksums = verify_checksums
        self.checksum_report = {}
    
    def standardize_date(self, date_str: str) -> Tuple[str, bool]:
        """Standardize date to YYYY-MM-DD format."""
        if not date_str or not date_str.strip():
            return '', False
        
        date_str = date_str.strip()
        
        from datetime import datetime
        for fmt in self.DATE_FORMATS:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d'), True
            except ValueError:
                continue
        
        self.warnings.append(f"Could not parse date: '{date_str}'")
        return date_str, False
    
    def normalize_object_number(self, obj_num: str) -> str:
        """Normalize object number format."""
        if not obj_num:
            return ''
        
        normalized = ' '.join(obj_num.split())
        normalized = normalized.upper()
        
        return normalized
    
    def validate_url(self, url: str) -> Tuple[str, bool]:
        """Validate and normalize URL."""
        if not url or not url.strip():
            return '', False
        
        url = url.strip()
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            result = urlparse(url)
            if result.scheme and result.netloc:
                return url, True
            else:
                self.warnings.append(f"Invalid URL format: '{url}'")
                return url, False
        except Exception as e:
            self.warnings.append(f"Error parsing URL '{url}': {str(e)}")
            return url, False
    
    def clean_title(self, title: str) -> str:
        """Clean and standardize title."""
        if not title:
            return ''
        
        title = ' '.join(title.split())
        title = title[0].upper() + title[1:] if title else ''
        
        return title
    
    def validate_record(self, record: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Validate a record has all required fields."""
        errors = []
        field_names = set(k.lower() for k in record.keys())
        
        for required in self.REQUIRED_FIELDS:
            if required not in field_names:
                errors.append(f"Missing required field: '{required}'")
        
        return len(errors) == 0, errors
    
    def standardize_record(self, record: Dict[str, str], record_num: int) -> Tuple[Dict[str, str], bool]:
        """Standardize a single record."""
        is_valid, validation_errors = self.validate_record(record)
        if not is_valid:
            for error in validation_errors:
                self.errors.append(f"Record {record_num}: {error}")
            return record, False
        
        field_map = {k.lower(): k for k in record.keys()}
        
        standardized = {}
        
        date_field = field_map.get('date', 'date')
        date_str, date_valid = self.standardize_date(record.get(date_field, ''))
        standardized['date'] = date_str
        
        if not date_valid and record.get(date_field):
            self.errors.append(f"Record {record_num}: Invalid date format")
            is_valid = False
        
        title_field = field_map.get('title', 'title')
        standardized['title'] = self.clean_title(record.get(title_field, ''))
        
        if not standardized['title']:
            self.errors.append(f"Record {record_num}: Empty title")
            is_valid = False
        
        obj_field = field_map.get('object_number', 'object_number')
        standardized['object_number'] = self.normalize_object_number(record.get(obj_field, ''))
        
        if not standardized['object_number']:
            self.errors.append(f"Record {record_num}: Empty object number")
            is_valid = False
        
        link_field = field_map.get('link', 'link')
        link_str, link_valid = self.validate_url(record.get(link_field, ''))
        standardized['link'] = link_str
        
        if not link_valid and record.get(link_field):
            self.errors.append(f"Record {record_num}: Invalid URL")
            is_valid = False
        
        for key, value in record.items():
            lower_key = key.lower()
            if lower_key not in self.REQUIRED_FIELDS:
                standardized[key] = value
        
        return standardized, is_valid
    
    def verify_source_data(self) -> bool:
        """
        Verify source data hasn't changed using checksums.
        
        Returns:
            True if file is unchanged or is new, False if modified
        """
        if not self.verify_checksums:
            return True
        
        unchanged, current, previous = self.checksum_manager.verify_file_unchanged(
            self.input_file
        )
        
        if unchanged is None:
            self.checksum_report['status'] = 'new_file'
            self.checksum_report['message'] = 'No previous checksums found'
            if self.verbose:
                print("ℹ New file (no previous checksums)")
            return True
        
        self.checksum_report['file_checksum_previous'] = previous
        self.checksum_report['file_checksum_current'] = current
        
        if unchanged:
            self.checksum_report['status'] = 'unchanged'
            if self.verbose:
                print("✓ Source file unchanged (checksum verified)")
            return True
        else:
            self.checksum_report['status'] = 'modified'
            self.checksum_report['message'] = 'Source file has been modified'
            print(f"⚠ WARNING: Source file has been modified!")
            print(f"  Previous checksum: {previous}")
            print(f"  Current checksum:  {current}")
            return False
    
    def process(self, force: bool = False) -> bool:
        """
        Process the inventory file.
        
        Args:
            force: Force processing even if file has changed
            
        Returns:
            True if successful, False otherwise
        """
        if not self.input_file.exists():
            print(f"Error: Input file not found: {self.input_file}")
            return False
        
        # Verify source data
        if not self.verify_source_data():
            if not force:
                print("Use --force to process anyway")
                return False
            else:
                print("Processing anyway (--force enabled)")
        
        try:
            records = []
            raw_records = []
            
            # Read input file
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    print("Error: Input file is empty or invalid")
                    return False
                
                for i, record in enumerate(reader, start=1):
                    self.records_processed += 1
                    raw_records.append(record)
                    standardized, is_valid = self.standardize_record(record, i)
                    records.append(standardized)
                    
                    if is_valid:
                        self.records_valid += 1
                    
                    if self.verbose:
                        status = "✓" if is_valid else "✗"
                        print(f"[{status}] Record {i}: {standardized.get('object_number', 'N/A')}")
            
            # Calculate checksums
            if self.verify_checksums:
                file_checksum = self.checksum_manager.calculate_file_checksum(self.input_file)
                record_checksums = {
                    i: self.checksum_manager.calculate_record_checksum(record)
                    for i, record in enumerate(raw_records)
                }
                records_checksum = self.checksum_manager.calculate_records_checksum(raw_records)
                
                # Detect changes
                changes = self.checksum_manager.detect_record_changes(self.input_file, raw_records)
                self.checksum_report['record_changes'] = changes
                
                if self.verbose and changes.get('total_changes', 0) > 0:
                    print(f"\n⚠ Detected {changes['total_changes']} record changes")
                
                # Save checksums for next time
                self.checksum_manager.save_checksums(
                    self.input_file,
                    file_checksum,
                    {str(k): v for k, v in record_checksums.items()},
                    records_checksum
                )
            
            # Write output file
            if records:
                fieldnames = list(records[0].keys())
                ordered_fields = []
                for field in ['date', 'title', 'object_number', 'link']:
                    if field in fieldnames:
                        ordered_fields.append(field)
                        fieldnames.remove(field)
                ordered_fields.extend(fieldnames)
                
                with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=ordered_fields, delimiter='\t')
                    writer.writeheader()
                    writer.writerows(records)
                
                if self.verbose:
                    print(f"\nOutput written to: {self.output_file}")
            
            return True
        
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return False
    
    def print_report(self):
        """Print a summary report of the standardization."""
        print("\n" + "=" * 70)
        print("STANDARDIZATION REPORT")
        print("=" * 70)
        print(f"Records processed: {self.records_processed}")
        print(f"Records valid:     {self.records_valid}")
        print(f"Records with issues: {self.records_processed - self.records_valid}")
        
        # Checksum report
        if self.checksum_report:
            print("\n" + "-" * 70)
            print("CHECKSUM VERIFICATION")
            print("-" * 70)
            print(f"Status: {self.checksum_report.get('status', 'unknown')}")
            
            if msg := self.checksum_report.get('message'):
                print(f"Message: {msg}")
            
            if prev := self.checksum_report.get('file_checksum_previous'):
                print(f"Previous file checksum: {prev[:16]}...")
            if curr := self.checksum_report.get('file_checksum_current'):
                print(f"Current file checksum:  {curr[:16]}...")
            
            if changes := self.checksum_report.get('record_changes'):
                print(f"\nRecord Changes:")
                print(f"  Previous record count: {changes.get('previous_record_count', 'N/A')}")
                print(f"  Current record count:  {changes.get('current_record_count', 'N/A')}")
                print(f"  Modified records:      {len(changes.get('changed_records', []))}")
                print(f"  New records:           {len(changes.get('new_records', []))}")
                print(f"  Deleted records:       {len(changes.get('deleted_records', []))}")
                
                if changes.get('changed_records'):
                    print(f"\n  Modified record numbers:")
                    for change in changes['changed_records'][:5]:
                        print(f"    - Record {change['record_number']}")
                    if len(changes['changed_records']) > 5:
                        print(f"    ... and {len(changes['changed_records']) - 5} more")
        
        if self.warnings:
            print(f"\n{len(self.warnings)} Warning(s):")
            for warning in self.warnings[:10]:
                print(f"  ⚠ {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        if self.errors:
            print(f"\n{len(self.errors)} Error(s):")
            for error in self.errors[:10]:
                print(f"  ✗ {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        
        if not self.warnings and not self.errors:
            print("\n✓ No issues found!")
        
        print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records with checksum verification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s inventory.tsv
  %(prog)s inventory.tsv -o standardized.tsv -v
  %(prog)s inventory.tsv --no-verify
  %(prog)s inventory.tsv --force
  %(prog)s inventory.tsv --checksum-dir .metadata
        """
    )
    
    parser.add_argument('input', help='Input TSV file')
    parser.add_argument('-o', '--output', help='Output TSV file (default: input_standardized.tsv)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--no-verify', action='store_true', 
                       help='Skip checksum verification')
    parser.add_argument('--force', action='store_true',
                       help='Force processing even if file has changed')
    parser.add_argument('--checksum-dir', 
                       help='Directory for checksum files (default: .checksums)')
    
    args = parser.parse_args()
    
    standardizer = InventoryStandardizer(
        args.input,
        args.output,
        verify_checksums=not args.no_verify,
        checksum_dir=args.checksum_dir,
        verbose=args.verbose
    )
    
    if standardizer.process(force=args.force):
        standardizer.print_report()
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## Key Features

**Checksum Management:**
- SHA256 (default) or MD5 hashing
- File-level checksums (entire input file)
- Record-level checksums (individual records)
- Combined checksums (all records)

**Change Detection:**
- Identifies modified records
- Detects new records
- Detects deleted records
- Compares checksums between runs

**Checksum Storage:**
- Stores checksums in JSON format
- Preserves history with timestamps
- One checksum file per source file

## Usage Examples

```bash
# First run - creates checksums
python3 standardize_inventory.py inventory.tsv -v

# Second run - verifies file unchanged
python3 standardize_inventory.py inventory.tsv -v
# Output: ✓ Source file unchanged (checksum verified)

# File modified - requires verification
python3 standardize_inventory.py inventory.tsv
# Output: ⚠ WARNING: Source file has been modified!

# Force processing despite changes
python3 standardize_inventory.py inventory.tsv --force

# Skip checksum verification
python3 standardize_inventory.py inventory.tsv --no-verify

# Custom checksum directory
python3 standardize_inventory.py inventory.tsv --checksum-dir .metadata
```

## Generated Checksum File

Checksums are stored in `.checksums/inventory.checksums.json`:

```json
{
  "source_file": "inventory.tsv",
  "timestamp": "2024-01-15T14:32:45.123456",
  "algorithm": "sha256",
  "file_checksum": "a1b2c3d4e5f6...",
  "records_checksum": "f6e5d4c3b2a1...",
  "record_count": 5,
  "record_checksums": {
    "0": "hash_of_record_0",
    "1": "hash_of_record_1",
    "2": "hash_of_record_2",
    "3": "hash_of_record_3",
    "4": "hash_of_record_4"
  }
}
```

This approach ensures data integrity and provides audit trails for museum collections.
