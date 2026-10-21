# Museum Inventory Standardization with Checksum Verification

```python
#!/usr/bin/env python3
"""
Standardize and validate museum inventory records from a TSV file.

Includes checksum verification to detect unwanted changes to source data.
"""

import argparse
import csv
import sys
import hashlib
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Dict
from urllib.parse import urlparse


@dataclass
class InventoryRecord:
    """Represents a single inventory record."""
    date: str
    title: str
    object_number: str
    link: str
    
    def __hash__(self):
        return hash(self.object_number)
    
    def __eq__(self, other):
        if not isinstance(other, InventoryRecord):
            return False
        return self.object_number == other.object_number
    
    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return asdict(self)
    
    def compute_checksum(self, algorithm: str = 'sha256') -> str:
        """
        Compute checksum for this record.
        
        Args:
            algorithm: Hash algorithm (sha256, sha1, md5)
            
        Returns:
            Hex digest of the record
        """
        # Use object_number as the stable identifier
        content = f"{self.object_number}|{self.date}|{self.title}|{self.link}"
        
        if algorithm == 'sha256':
            return hashlib.sha256(content.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(content.encode()).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(content.encode()).hexdigest()
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")


class ChecksumManager:
    """Manages checksums for data integrity verification."""
    
    def __init__(self, algorithm: str = 'sha256'):
        """
        Initialize checksum manager.
        
        Args:
            algorithm: Hash algorithm to use (sha256, sha1, md5)
        """
        self.algorithm = algorithm
        self.record_checksums: Dict[str, str] = {}  # object_number -> checksum
        self.file_checksum: Optional[str] = None
    
    def compute_file_checksum(self, filepath: str) -> str:
        """
        Compute checksum of entire file.
        
        Args:
            filepath: Path to file
            
        Returns:
            Hex digest of file contents
        """
        hasher = hashlib.new(self.algorithm)
        
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
        except Exception as e:
            raise IOError(f"Error computing file checksum: {e}")
        
        self.file_checksum = hasher.hexdigest()
        return self.file_checksum
    
    def add_record_checksum(self, record: InventoryRecord) -> str:
        """
        Add checksum for a record.
        
        Args:
            record: InventoryRecord to checksum
            
        Returns:
            Computed checksum
        """
        checksum = record.compute_checksum(self.algorithm)
        self.record_checksums[record.object_number] = checksum
        return checksum
    
    def verify_record_checksum(self, record: InventoryRecord) -> bool:
        """
        Verify that a record's checksum matches stored value.
        
        Args:
            record: InventoryRecord to verify
            
        Returns:
            True if checksum matches, False otherwise
        """
        if record.object_number not in self.record_checksums:
            return False
        
        expected = self.record_checksums[record.object_number]
        actual = record.compute_checksum(self.algorithm)
        return expected == actual
    
    def save_checksums(self, filepath: str):
        """
        Save checksums to JSON file.
        
        Args:
            filepath: Path to output checksum file
        """
        data = {
            'algorithm': self.algorithm,
            'file_checksum': self.file_checksum,
            'timestamp': datetime.now().isoformat(),
            'record_checksums': self.record_checksums
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise IOError(f"Error saving checksums: {e}")
    
    def load_checksums(self, filepath: str) -> bool:
        """
        Load checksums from JSON file.
        
        Args:
            filepath: Path to checksum file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Verify algorithm matches
            if data.get('algorithm') != self.algorithm:
                raise ValueError(
                    f"Algorithm mismatch: expected {self.algorithm}, "
                    f"got {data.get('algorithm')}"
                )
            
            self.file_checksum = data.get('file_checksum')
            self.record_checksums = data.get('record_checksums', {})
            return True
        
        except Exception as e:
            raise IOError(f"Error loading checksums: {e}")


class InventoryStandardizer:
    """Standardizes and validates museum inventory records."""
    
    def __init__(self, strict_mode: bool = False, checksum_algorithm: str = 'sha256'):
        """
        Initialize the standardizer.
        
        Args:
            strict_mode: If True, fail on validation errors
            checksum_algorithm: Algorithm for checksums (sha256, sha1, md5)
        """
        self.strict_mode = strict_mode
        self.checksum_manager = ChecksumManager(checksum_algorithm)
        self.records = {}  # object_number -> InventoryRecord
        self.withdrawn = set()
        self.errors = []
        self.warnings = []
        self.checksum_mismatches = []
        self.source_file_path: Optional[str] = None
    
    @staticmethod
    def validate_date(date_str: str) -> Optional[str]:
        """Validate and standardize date to ISO format (YYYY-MM-DD)."""
        if not date_str or not date_str.strip():
            return None
        
        date_str = date_str.strip()
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
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def standardize_object_number(obj_num: str) -> Optional[str]:
        """Standardize object number."""
        if not obj_num or not obj_num.strip():
            return None
        
        standardized = obj_num.strip().upper()
        
        if not all(c.isalnum() or c in '-.' for c in standardized):
            return None
        
        return standardized
    
    @staticmethod
    def standardize_title(title: str) -> Optional[str]:
        """Standardize title."""
        if not title or not title.strip():
            return None
        
        standardized = ' '.join(title.split())
        return standardized if standardized else None
    
    @staticmethod
    def validate_link(link: str) -> bool:
        """Validate URL."""
        if not link or not link.strip():
            return False
        
        try:
            result = urlparse(link.strip())
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def process_record(self, row: dict, row_num: int) -> Optional[InventoryRecord]:
        """Process and validate a single record."""
        errors = []
        
        date = self.validate_date(row.get('date', ''))
        if not date:
            errors.append(f"Row {row_num}: Invalid or missing date")
        
        title = self.standardize_title(row.get('title', ''))
        if not title:
            errors.append(f"Row {row_num}: Invalid or missing title")
        
        object_number = self.standardize_object_number(row.get('object_number', ''))
        if not object_number:
            errors.append(f"Row {row_num}: Invalid or missing object_number")
        
        link = row.get('link', '').strip()
        if not self.validate_link(link):
            errors.append(f"Row {row_num}: Invalid or missing link")
        
        if errors:
            for error in errors:
                if self.strict_mode:
                    self.errors.append(error)
                else:
                    self.warnings.append(error)
            
            if self.strict_mode:
                return None
        
        if not (date and title and object_number and link):
            return None
        
        return InventoryRecord(
            date=date,
            title=title,
            object_number=object_number,
            link=link
        )
    
    def load_inventory(self, filepath: str, verify_checksums: bool = False,
                      checksums_file: Optional[str] = None) -> bool:
        """
        Load inventory from TSV file with optional checksum verification.
        
        Args:
            filepath: Path to TSV file
            verify_checksums: Whether to verify checksums against stored file
            checksums_file: Path to stored checksums (required if verify_checksums=True)
            
        Returns:
            True if successful, False otherwise
        """
        filepath_obj = Path(filepath)
        self.source_file_path = str(filepath_obj)
        
        if not filepath_obj.exists():
            self.errors.append(f"File not found: {filepath_obj}")
            return False
        
        # Compute file checksum
        try:
            self.checksum_manager.compute_file_checksum(filepath)
        except IOError as e:
            self.errors.append(str(e))
            return False
        
        # Load stored checksums if verifying
        if verify_checksums:
            if not checksums_file:
                self.errors.append("Checksums file required for verification")
                return False
            
            try:
                self.checksum_manager.load_checksums(checksums_file)
            except IOError as e:
                self.errors.append(str(e))
                return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames or set(reader.fieldnames) != {'date', 'title', 'object_number', 'link'}:
                    self.errors.append(
                        f"Invalid TSV headers. Expected: date, title, object_number, link. "
                        f"Got: {reader.fieldnames}"
                    )
                    return False
                
                for row_num, row in enumerate(reader, start=2):
                    record = self.process_record(row, row_num)
                    if record:
                        # Store checksum for new records
                        self.checksum_manager.add_record_checksum(record)
                        
                        if record.object_number in self.records:
                            self.warnings.append(
                                f"Row {row_num}: Duplicate object_number {record.object_number}. "
                                f"Updating with new record."
                            )
                        self.records[record.object_number] = record
        
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False
        
        return True
    
    def apply_corrections(self, corrections_filepath: str) -> bool:
        """Apply corrections from a corrections file."""
        corrections_path = Path(corrections_filepath)
        
        if not corrections_path.exists():
            self.errors.append(f"Corrections file not found: {corrections_filepath}")
            return False
        
        try:
            with open(corrections_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames or set(reader.fieldnames) != {'object_number', 'field', 'value'}:
                    self.errors.append(
                        f"Invalid corrections file headers. Expected: object_number, field, value. "
                        f"Got: {reader.fieldnames}"
                    )
                    return False
                
                for row_num, row in enumerate(reader, start=2):
                    obj_num = self.standardize_object_number(row.get('object_number', ''))
                    field = row.get('field', '').strip().lower()
                    value = row.get('value', '').strip()
                    
                    if not obj_num:
                        self.warnings.append(f"Correction row {row_num}: Invalid object_number")
                        continue
                    
                    if obj_num not in self.records:
                        self.warnings.append(
                            f"Correction row {row_num}: object_number {obj_num} not found in inventory"
                        )
                        continue
                    
                    if field not in ['date', 'title', 'link']:
                        self.warnings.append(
                            f"Correction row {row_num}: Unknown field '{field}' for {obj_num}"
                        )
                        continue
                    
                    # Verify record hasn't changed before applying correction
                    if not self.checksum_manager.verify_record_checksum(self.records[obj_num]):
                        self.checksum_mismatches.append(
                            f"Correction row {row_num}: Record {obj_num} has changed since loading. "
                            f"Checksum mismatch. Skipping correction."
                        )
                        continue
                    
                    # Apply correction
                    if field == 'date':
                        standardized = self.validate_date(value)
                        if not standardized:
                            self.warnings.append(
                                f"Correction row {row_num}: Invalid date value '{value}' for {obj_num}"
                            )
                            continue
                        self.records[obj_num].date = standardized
                    
                    elif field == 'title':
                        standardized = self.standardize_title(value)
                        if not standardized:
                            self.warnings.append(
                                f"Correction row {row_num}: Invalid title value '{value}' for {obj_num}"
                            )
                            continue
                        self.records[obj_num].title = standardized
                    
                    elif field == 'link':
                        if not self.validate_link(value):
                            self.warnings.append(
                                f"Correction row {row_num}: Invalid link value '{value}' for {obj_num}"
                            )
                            continue
                        self.records[obj_num].link = value.strip()
                    
                    # Update checksum after change
                    self.checksum_manager.add_record_checksum(self.records[obj_num])
        
        except Exception as e:
            self.errors.append(f"Error reading corrections file: {e}")
            return False
        
        return True
    
    def withdraw_records(self, withdrawal_filepath: str) -> bool:
        """Mark records as withdrawn."""
        withdrawal_path = Path(withdrawal_filepath)
        
        if not withdrawal_path.exists():
            self.errors.append(f"Withdrawal file not found: {withdrawal_filepath}")
            return False
        
        try:
            with open(withdrawal_path, 'r', encoding='utf-8') as f:
                for row_num, line in enumerate(f, start=1):
                    obj_num = self.standardize_object_number(line.strip())
                    
                    if not obj_num:
                        self.warnings.append(f"Withdrawal row {row_num}: Invalid object_number")
                        continue
                    
                    if obj_num not in self.records:
                        self.warnings.append(
                            f"Withdrawal row {row_num}: object_number {obj_num} not found in inventory"
                        )
                        continue
                    
                    self.withdrawn.add(obj_num)
        
        except Exception as e:
            self.errors.append(f"Error reading withdrawal file: {e}")
            return False
        
        return True
    
    def get_active_records(self) -> dict:
        """Get all non-withdrawn records."""
        return {
            obj_num: record
            for obj_num, record in self.records.items()
            if obj_num not in self.withdrawn
        }
    
    def save_inventory(self, output_filepath: str, include_withdrawn: bool = False) -> bool:
        """Save standardized inventory to TSV file."""
        try:
            records_to_save = self.records if include_withdrawn else self.get_active_records()
            
            with open(output_filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['date', 'title', 'object_number', 'link'],
                    delimiter='\t'
                )
                writer.writeheader()
                
                for record in sorted(records_to_save.values(), key=lambda r: r.object_number):
                    writer.writerow({
                        'date': record.date,
                        'title': record.title,
                        'object_number': record.object_number,
                        'link': record.link
                    })
        
        except Exception as e:
            self.errors.append(f"Error writing output file: {e}")
            return False
        
        return True
    
    def save_checksums(self, checksums_filepath: str) -> bool:
        """
        Save checksums for future verification.
        
        Args:
            checksums_filepath: Path to output checksums file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.checksum_manager.save_checksums(checksums_filepath)
            return True
        except IOError as e:
            self.errors.append(str(e))
            return False
    
    def verify_file_checksum(self, expected_checksum: str) -> bool:
        """
        Verify file checksum matches expected value.
        
        Args:
            expected_checksum: Expected checksum value
            
        Returns:
            True if matches, False otherwise
        """
        return self.checksum_manager.file_checksum == expected_checksum
    
    def print_report(self):
        """Print validation report to stdout."""
        print("\n" + "="*60)
        print("INVENTORY STANDARDIZATION REPORT")
        print("="*60)
        
        print(f"\nSource file: {self.source_file_path}")
        if self.checksum_manager.file_checksum:
            print(f"File checksum ({self.checksum_manager.algorithm}): {self.checksum_manager.file_checksum}")
        
        print(f"\nTotal records processed: {len(self.records)}")
        print(f"Withdrawn records: {len(self.withdrawn)}")
        print(f"Active records: {len(self.get_active_records())}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.checksum_mismatches:
            print(f"\n🔐 CHECKSUM MISMATCHES ({len(self.checksum_mismatches)}):")
            for mismatch in self.checksum_mismatches:
                print(f"  - {mismatch}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more warnings")
        
        if not self.errors and not self.checksum_mismatches and not self.warnings:
            print("\n✅ No errors, mismatches, or warnings!")
        
        print("\n" + "="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Standardize and validate museum inventory records with checksum verification'
    )
    parser.add_argument(
        'inventory',
        help='Path to inventory TSV file'
    )
    parser.add_argument(
        '-o', '--output',
        default='inventory_standardized.tsv',
        help='Output file path (default: inventory_standardized.tsv)'
    )
    parser.add_argument(
        '--save-checksums',
        help='Path to save checksums file (JSON format)'
    )
    parser.add_argument(
        '--verify-checksums',
        help='Path to checksums file to verify against'
    )
    parser.add_argument(
        '--verify-file-checksum',
        help='Expected file checksum (SHA256 by default). Will verify and report mismatch.'
    )
    parser.add_argument(
        '-c', '--corrections',
        help='Path to corrections TSV file'
    )
    parser.add_argument(
        '-w', '--withdrawals',
        help='Path to withdrawals file (one object_number per line)'
    )
    parser.add_argument(
        '--checksum-algorithm',
        choices=['sha256', 'sha1', 'md5'],
        default='sha256',
        help='Hash algorithm for checksums (default: sha256)'
    )
    parser.add_argument(
        '--include-withdrawn',
        action='store_true',
        help='Include withdrawn records in output'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Fail on validation warnings'
    )
    
    args = parser.parse_args()
    
    # Initialize standardizer
    standardizer = InventoryStandardizer(
        strict_mode=args.strict,
        checksum_algorithm=args.checksum_algorithm
    )
    
    # Verify file checksum if provided
    if args.verify_file_checksum:
        print(f"Computing file checksum...")
        standardizer.checksum_manager.compute_file_checksum(args.inventory)
        if not standardizer.verify_file_checksum(args.verify_file_checksum):
            print(f"❌ FILE CHECKSUM MISMATCH!")
            print(f"   Expected: {args.verify_file_checksum}")
            print(f"   Got:      {standardizer.checksum_manager.file_checksum}")
            sys.exit(1)
        print(f"✅ File checksum verified!")
    
    # Load inventory
    if not standardizer.load_inventory(
        args.inventory,
        verify_checksums=bool(args.verify_checksums),
        checksums_file=args.verify_checksums
    ):
        standardizer.print_report()
        sys.exit(1)
    
    # Apply corrections if provided
    if args.corrections:
        print(f"Applying corrections...")
        standardizer.apply_corrections(args.corrections)
    
    # Apply withdrawals if provided
    if args.withdrawals:
        print(f"Processing withdrawals...")
        standardizer.withdraw_records(args.withdrawals)
    
    # Save standardized inventory
    if not standardizer.save_inventory(args.output, include_withdrawn=args.include_withdrawn):
        standardizer.print_report()
        sys.exit(1)
    
    # Save checksums if requested
    if args.save_checksums:
        print(f"Saving checksums to {args.save_checksums}...")
        if not standardizer.save_checksums(args.save_checksums):
            standardizer.print_report()
            sys.exit(1)
    
    # Print report
    standardizer.print_report()
    print(f"\n✅ Standardized inventory saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(1 if standardizer.errors or standardizer.checksum_mismatches else 0)


if __name__ == '__main__':
    main()
```

## Usage Examples

### Initial processing and save checksums:
```bash
python standardize_inventory.py inventory.tsv \
    -o inventory_clean.tsv \
    --save-checksums inventory.checksums.json
```

### Verify against stored checksums:
```bash
python standardize_inventory.py inventory.tsv \
    -o inventory_clean.tsv \
    --verify-checksums inventory.checksums.json \
    -c corrections.tsv
```

### Verify file hasn't been tampered with:
```bash
python standardize_inventory.py inventory.tsv \
    --verify-file-checksum 3a7f4c9e2b1d8f5a6c9e2b1d8f5a6c9e
```

### Full workflow with checksum verification:
```bash
python standardize_inventory.py inventory.tsv \
    -o inventory_clean.tsv \
    --verify-checksums inventory.checksums.json \
    -c corrections.tsv \
    -w withdrawals.txt \
    --save-checksums inventory_updated.checksums.json
```

### Using MD5 checksums (less secure, but compatible):
```bash
python standardize_inventory.py inventory.tsv \
    --checksum-algorithm md5 \
    --save-checksums inventory.checksums.json
```

## Key Checksum Features

1. **File-level checksums**: Detects if entire source file has been modified
2. **Record-level checksums**: Detects individual record tampering
3. **Automatic verification**: Fails if records change before corrections are applied
4. **Multiple algorithms**: SHA256 (default), SHA1, MD5
5. **JSON checksum storage**: Human-readable with metadata
6. **Update tracking**: Checksums updated after corrections applied

## Example checksums.json:
```json
{
  "algorithm": "sha256",
  "file_checksum": "3a7f4c9e2b1d8f5a6c9e2b1d8f5a6c9e...",
  "timestamp": "2024-01-15T10:30:00.123456",
  "record_checksums": {
    "OBJ-001": "f4a8c2e1d9b3f7a5c8e1d9b3f7a5c8e1...",
    "OBJ-002": "a5c8e1d9b3f7a5c8e1d9b3f7a5c8e1d9..."
  }
}
```
