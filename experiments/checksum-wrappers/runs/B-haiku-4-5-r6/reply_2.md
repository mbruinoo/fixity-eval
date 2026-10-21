# Museum Inventory Standardizer with Checksums

Here's how to incorporate checksums for data integrity verification:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksum Verification

Standardizes museum inventory records from a TSV file.
Uses checksums to verify data integrity.
"""

import argparse
import sys
import re
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import csv


class ChecksumManager:
    """Manages checksums for data integrity verification."""
    
    CHECKSUM_FILE_SUFFIX = '.checksums'
    ALGORITHM = 'sha256'
    
    @staticmethod
    def calculate_record_checksum(record: Dict) -> str:
        """
        Calculate checksum for a single record.
        
        Args:
            record: Record dictionary
            
        Returns:
            Hex digest of record checksum
        """
        # Convert record to sorted JSON for consistent hashing
        record_json = json.dumps(record, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(record_json.encode()).hexdigest()
    
    @staticmethod
    def calculate_file_checksum(filepath: str, algorithm: str = 'sha256') -> str:
        """
        Calculate checksum for entire file.
        
        Args:
            filepath: Path to file
            algorithm: Hash algorithm to use
            
        Returns:
            Hex digest of file checksum
        """
        hash_obj = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    
    @staticmethod
    def create_checksum_map(records: List[Dict]) -> Dict[str, str]:
        """
        Create a map of object numbers to record checksums.
        
        Args:
            records: List of records
            
        Returns:
            Dictionary mapping object_number to checksum
        """
        checksum_map = {}
        for record in records:
            obj_num = record.get('object_number', '').strip()
            if obj_num:
                checksum_map[obj_num] = ChecksumManager.calculate_record_checksum(record)
        return checksum_map
    
    @staticmethod
    def save_checksums(
        checksums: Dict[str, str],
        filepath: str,
        file_checksum: str = '',
        metadata: Optional[Dict] = None
    ):
        """
        Save checksums to a file.
        
        Args:
            checksums: Dictionary of checksums
            filepath: Path to save checksums to
            file_checksum: Optional checksum of source file
            metadata: Optional metadata about the checksums
        """
        checksum_data = {
            'algorithm': ChecksumManager.ALGORITHM,
            'created': datetime.now().isoformat(),
            'file_checksum': file_checksum,
            'metadata': metadata or {},
            'checksums': checksums
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(checksum_data, f, indent=2)
    
    @staticmethod
    def load_checksums(filepath: str) -> Tuple[Dict[str, str], Dict]:
        """
        Load checksums from a file.
        
        Args:
            filepath: Path to checksums file
            
        Returns:
            Tuple of (checksums_dict, metadata_dict)
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                checksum_data = json.load(f)
            return checksum_data['checksums'], checksum_data
        except FileNotFoundError:
            raise FileNotFoundError(f"Checksums file not found: {filepath}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid checksums file format: {filepath}")
    
    @staticmethod
    def compare_checksums(
        stored_checksums: Dict[str, str],
        current_checksums: Dict[str, str]
    ) -> Tuple[Dict, List[str]]:
        """
        Compare stored and current checksums.
        
        Args:
            stored_checksums: Previously stored checksums
            current_checksums: Currently calculated checksums
            
        Returns:
            Tuple of (changes_dict, issues_list)
        """
        changes = {
            'unchanged': [],
            'modified': [],
            'added': [],
            'removed': []
        }
        issues = []
        
        all_objects = set(stored_checksums.keys()) | set(current_checksums.keys())
        
        for obj_num in all_objects:
            stored_chk = stored_checksums.get(obj_num)
            current_chk = current_checksums.get(obj_num)
            
            if stored_chk and current_chk:
                if stored_chk == current_chk:
                    changes['unchanged'].append(obj_num)
                else:
                    changes['modified'].append(obj_num)
                    issues.append(
                        f"Record {obj_num}: Data has changed "
                        f"(stored: {stored_chk[:8]}... current: {current_chk[:8]}...)"
                    )
            elif current_chk and not stored_chk:
                changes['added'].append(obj_num)
                issues.append(f"Record {obj_num}: Newly added")
            elif stored_chk and not current_chk:
                changes['removed'].append(obj_num)
                issues.append(f"Record {obj_num}: Removed from source data")
        
        return changes, issues


class MuseumInventoryStandardizer:
    """Standardizes museum inventory records with checksum verification."""
    
    OBJECT_NUMBER_PATTERN = r'^[A-Z]{2,4}\.\d{4}\.\d{3}$'
    URL_PATTERN = r'^https?://[^\s]+$'
    DATE_FORMATS = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%B %d, %Y',
        '%b %d, %Y',
    ]
    
    def __init__(self, strict_mode: bool = False, verify_checksums: bool = False):
        """
        Initialize the standardizer.
        
        Args:
            strict_mode: If True, reject records with any issues.
            verify_checksums: If True, verify data hasn't changed
        """
        self.strict_mode = strict_mode
        self.verify_checksums = verify_checksums
        self.warnings = []
        self.errors = []
        self.checksum_manager = ChecksumManager()
    
    def read_tsv(self, filepath: str) -> Tuple[List[str], List[Dict]]:
        """Read TSV file with inventory records."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                fieldnames = reader.fieldnames
                records = list(reader)
            return fieldnames, records
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def verify_source_data(self, filepath: str) -> Tuple[bool, List[str]]:
        """
        Verify that source data matches stored checksums.
        
        Args:
            filepath: Path to source TSV file
            
        Returns:
            Tuple of (is_valid, issues_list)
        """
        if not self.verify_checksums:
            return True, []
        
        # Find checksums file
        checksum_file = filepath + ChecksumManager.CHECKSUM_FILE_SUFFIX
        
        if not Path(checksum_file).exists():
            return True, [f"No checksum file found: {checksum_file}"]
        
        print(f"Verifying checksums against: {checksum_file}")
        
        try:
            # Load stored checksums
            stored_checksums, metadata = self.checksum_manager.load_checksums(checksum_file)
            
            # Read and calculate current checksums
            _, records = self.read_tsv(filepath)
            current_checksums = self.checksum_manager.create_checksum_map(records)
            
            # Compare
            changes, issues = self.checksum_manager.compare_checksums(
                stored_checksums,
                current_checksums
            )
            
            # Print summary
            print(f"\n{'='*60}")
            print("Checksum Verification Summary")
            print(f"{'='*60}")
            print(f"Unchanged records: {len(changes['unchanged'])}")
            print(f"Modified records:  {len(changes['modified'])}")
            print(f"Added records:     {len(changes['added'])}")
            print(f"Removed records:   {len(changes['removed'])}")
            
            if changes['modified']:
                print(f"\nWARNING: {len(changes['modified'])} record(s) have been modified:")
                for obj_num in changes['modified'][:5]:  # Show first 5
                    print(f"  - {obj_num}")
                if len(changes['modified']) > 5:
                    print(f"  ... and {len(changes['modified']) - 5} more")
            
            return len(changes['modified']) == 0, issues
            
        except (FileNotFoundError, ValueError) as e:
            return False, [f"Checksum verification failed: {e}"]
    
    def standardize_date(self, date_str: str, record_num: int) -> Tuple[str, bool]:
        """Standardize date to YYYY-MM-DD format."""
        if not date_str or not date_str.strip():
            self.errors.append(f"Record {record_num}: Date is empty")
            return '', False
        
        date_str = date_str.strip()
        
        for date_format in self.DATE_FORMATS:
            try:
                date_obj = datetime.strptime(date_str, date_format)
                return date_obj.strftime('%Y-%m-%d'), True
            except ValueError:
                continue
        
        self.errors.append(
            f"Record {record_num}: Invalid date format: '{date_str}'"
        )
        return date_str, False
    
    def standardize_title(self, title: str, record_num: int) -> Tuple[str, bool]:
        """Standardize title."""
        if not title or not title.strip():
            self.errors.append(f"Record {record_num}: Title is empty")
            return '', False
        
        title = title.strip()
        title = ' '.join(title.split())
        
        if len(title) < 3:
            self.errors.append(f"Record {record_num}: Title too short: '{title}'")
            return title, False
        
        return title, True
    
    def standardize_object_number(self, obj_num: str, record_num: int) -> Tuple[str, bool]:
        """Standardize object number."""
        if not obj_num or not obj_num.strip():
            self.errors.append(f"Record {record_num}: Object number is empty")
            return '', False
        
        obj_num = obj_num.strip().upper()
        
        if not re.match(self.OBJECT_NUMBER_PATTERN, obj_num):
            self.errors.append(
                f"Record {record_num}: Invalid object number format: '{obj_num}'"
            )
            return obj_num, False
        
        return obj_num, True
    
    def standardize_link(self, link: str, record_num: int) -> Tuple[str, bool]:
        """Standardize URL link."""
        if not link or not link.strip():
            self.warnings.append(f"Record {record_num}: Link is empty")
            return '', True
        
        link = link.strip()
        
        if not link.startswith(('http://', 'https://')):
            link = 'https://' + link
            self.warnings.append(f"Record {record_num}: Added https:// protocol")
        
        if not re.match(self.URL_PATTERN, link):
            self.errors.append(f"Record {record_num}: Invalid URL format: '{link}'")
            return link, False
        
        return link, True
    
    def standardize_record(self, record: Dict, record_num: int) -> Tuple[Dict, bool]:
        """Standardize a single record."""
        self.warnings.clear()
        self.errors.clear()
        
        standardized = {}
        all_valid = True
        
        date, valid = self.standardize_date(record.get('date', ''), record_num)
        standardized['date'] = date
        all_valid = all_valid and valid
        
        title, valid = self.standardize_title(record.get('title', ''), record_num)
        standardized['title'] = title
        all_valid = all_valid and valid
        
        obj_num, valid = self.standardize_object_number(
            record.get('object_number', ''), record_num
        )
        standardized['object_number'] = obj_num
        all_valid = all_valid and valid
        
        link, valid = self.standardize_link(record.get('link', ''), record_num)
        standardized['link'] = link
        all_valid = all_valid and valid
        
        if self.strict_mode and not all_valid:
            return standardized, False
        
        return standardized, True
    
    def standardize_records(self, records: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """Standardize multiple records."""
        standardized_records = []
        all_issues = []
        
        for i, record in enumerate(records, 1):
            std_record, is_valid = self.standardize_record(record, i)
            
            if is_valid or not self.strict_mode:
                standardized_records.append(std_record)
            
            all_issues.extend([f"ERROR: {e}" for e in self.errors])
            all_issues.extend([f"WARNING: {w}" for w in self.warnings])
        
        return standardized_records, all_issues
    
    def write_tsv(self, filepath: str, records: List[Dict], fieldnames: List[str]):
        """Write standardized records to TSV file."""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(records)
            print(f"✓ Successfully wrote {len(records)} records to {filepath}")
        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def save_checksums(
        self,
        input_file: str,
        records: List[Dict],
        output_file: str
    ):
        """
        Save checksums for records.
        
        Args:
            input_file: Path to input TSV file
            records: Records to create checksums for
            output_file: Path to save checksums to
        """
        # Calculate checksums
        checksums = self.checksum_manager.create_checksum_map(records)
        file_checksum = self.checksum_manager.calculate_file_checksum(input_file)
        
        # Create metadata
        metadata = {
            'source_file': input_file,
            'record_count': len(records),
            'checksum_count': len(checksums),
            'standardizer_version': '1.0'
        }
        
        # Save
        checksum_file = output_file + ChecksumManager.CHECKSUM_FILE_SUFFIX
        self.checksum_manager.save_checksums(
            checksums,
            checksum_file,
            file_checksum=file_checksum,
            metadata=metadata
        )
        
        print(f"✓ Checksums saved to: {checksum_file}")
        return checksum_file


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records with checksum verification'
    )
    parser.add_argument('input', help='Input TSV file')
    parser.add_argument(
        '-o', '--output',
        help='Output TSV file (default: input_standardized.tsv)'
    )
    parser.add_argument(
        '-s', '--strict',
        action='store_true',
        help='Strict mode: reject records with any issues'
    )
    parser.add_argument(
        '-v', '--verify',
        action='store_true',
        help='Verify checksums before standardizing'
    )
    parser.add_argument(
        '-c', '--create-checksums',
        action='store_true',
        help='Create checksums for the source data'
    )
    parser.add_argument(
        '-r', '--report',
        help='Write validation report to file'
    )
    
    args = parser.parse_args()
    
    # Set output filename
    if args.output:
        output_file = args.output
    else:
        input_path = Path(args.input)
        output_file = input_path.stem + '_standardized.tsv'
    
    print(f"Reading inventory from: {args.input}")
    
    # Initialize standardizer
    standardizer = MuseumInventoryStandardizer(
        strict_mode=args.strict,
        verify_checksums=args.verify
    )
    
    # Verify checksums if requested
    if args.verify:
        is_valid, checksum_issues = standardizer.verify_source_data(args.input)
        if not is_valid:
            print("\n⚠ Checksum verification detected issues!")
            for issue in checksum_issues:
                print(f"  - {issue}")
            if args.strict:
                print("Aborting due to strict mode.")
                sys.exit(1)
    
    # Read input
    fieldnames, records = standardizer.read_tsv(args.input)
    print(f"✓ Read {len(records)} records")
    
    # Standardize
    print("Standardizing records...")
    std_records, issues = standardizer.standardize_records(records)
    
    # Write output
    standardizer.write_tsv(output_file, std_records, fieldnames)
    
    # Create checksums if requested
    if args.create_checksums:
        print("\nCreating checksums...")
        standardizer.save_checksums(args.input, records, output_file)
    
    # Report issues
    if issues:
        print(f"\n{'='*60}")
        print(f"Issues found: {len(issues)}")
        print(f"{'='*60}")
        for issue in issues:
            print(issue)
        
        if args.report:
            with open(args.report, 'w') as f:
                f.write('\n'.join(issues))
            print(f"\n✓ Report written to: {args.report}")
    else:
        print("\n✓ No issues found!")
    
    print(f"\n✓ Standardization complete!")


if __name__ == '__main__':
    main()
```

## Usage Examples

### Create initial checksums:
```bash
python standardize_inventory.py inventory.tsv --create-checksums
```
This creates `inventory.tsv.checksums` containing SHA256 hashes for each record.

### Verify data hasn't changed before standardizing:
```bash
python standardize_inventory.py inventory.tsv --verify
```

### Verify + standardize + create new checksums for output:
```bash
python standardize_inventory.py inventory.tsv --verify -o standardized.tsv --create-checksums
```

### Strict mode with verification:
```bash
python standardize_inventory.py inventory.tsv --verify --strict
```

## Checksum File Format

The `.checksums` file looks like:
```json
{
  "algorithm": "sha256",
  "created": "2024-01-15T10:30:45.123456",
  "file_checksum": "abc123def456...",
  "metadata": {
    "source_file": "inventory.tsv",
    "record_count": 150,
    "checksum_count": 150,
    "standardizer_version": "1.0"
  },
  "checksums": {
    "MUS.2024.001": "a1b2c3d4e5f6...",
    "MUS.2024.002": "b2c3d4e5f6g7...",
    "MUS.2024.003": "c3d4e5f6g7h8..."
  }
}
```

## Key Features

- **SHA256 checksums** for both individual records and entire files
- **Detects modifications**: Identifies changed records
- **Tracks additions/removals**: Knows when records are added or deleted
- **Metadata tracking**: Stores context about checksums
- **Verification reports**: Shows which records changed
- **Strict mode integration**: Can fail if data has been modified
- **JSON format**: Easy to parse and audit

This approach ensures data integrity and provides an audit trail!
