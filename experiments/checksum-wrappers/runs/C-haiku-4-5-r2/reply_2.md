# Museum Inventory with Checksum Verification

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records with checksum verification.

Detects if source data has been modified since last processing.
Maintains checksums for individual records and the entire dataset.
"""

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
import re
from urllib.parse import urlparse


class ChecksumManager:
    """Manages checksums for data integrity verification."""
    
    HASH_ALGORITHM = 'sha256'
    
    def __init__(self, checksum_dir: Path = None):
        self.checksum_dir = checksum_dir or Path('.checksums')
        self.checksum_dir.mkdir(exist_ok=True)
    
    @staticmethod
    def compute_record_hash(record: Dict) -> str:
        """
        Compute hash of a single record.
        
        Normalizes record before hashing to ensure whitespace differences
        don't affect the hash.
        """
        # Create normalized copy for hashing
        normalized = {
            'date': record.get('date', '').strip(),
            'title': record.get('title', '').strip(),
            'object_number': record.get('object_number', '').strip(),
            'link': record.get('link', '').strip(),
        }
        
        # Use JSON for consistent serialization
        record_str = json.dumps(normalized, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(record_str.encode('utf-8')).hexdigest()
    
    @staticmethod
    def compute_file_hash(file_path: Path) -> str:
        """Compute hash of entire file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            raise IOError(f"Error computing file hash: {e}")
    
    def get_checksum_file(self, input_file: Path, suffix: str = '') -> Path:
        """Get path to checksum file for given input file."""
        filename = input_file.stem + suffix + '.json'
        return self.checksum_dir / filename
    
    def load_checksums(self, checksum_file: Path) -> Dict:
        """Load previously saved checksums."""
        if not checksum_file.exists():
            return {}
        
        try:
            with open(checksum_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load checksums: {e}", file=sys.stderr)
            return {}
    
    def save_checksums(self, checksum_file: Path, checksums: Dict) -> None:
        """Save checksums to file."""
        try:
            with open(checksum_file, 'w') as f:
                json.dump(checksums, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save checksums: {e}", file=sys.stderr)
    
    def verify_file_integrity(self, file_path: Path, 
                            previous_hash: Optional[str] = None) -> Tuple[str, bool]:
        """
        Verify file hasn't been modified.
        
        Returns:
            (current_hash, is_unchanged) tuple
        """
        current_hash = self.compute_file_hash(file_path)
        
        if previous_hash is None:
            return current_hash, True
        
        is_unchanged = current_hash == previous_hash
        return current_hash, is_unchanged


class InventoryRecord:
    """Represents a single museum inventory record with checksum support."""
    
    REQUIRED_FIELDS = {'date', 'title', 'object_number', 'link'}
    
    def __init__(self, date: str, title: str, object_number: str, link: str):
        self.original_date = date
        self.original_title = title
        self.original_object_number = object_number
        self.original_link = link
        
        self.is_withdrawn = False
        self.standardized_date = None
        self.standardized_title = None
        self.standardized_object_number = None
        self.standardized_link = None
        self.errors = []
        
        # Checksum tracking
        self.source_hash = None
        self.previous_hash = None
        self.has_changed = False
    
    def compute_source_hash(self) -> str:
        """Compute hash of original (source) data."""
        self.source_hash = ChecksumManager.compute_record_hash({
            'date': self.original_date,
            'title': self.original_title,
            'object_number': self.original_object_number,
            'link': self.original_link,
        })
        return self.source_hash
    
    def check_for_changes(self, previous_hash: Optional[str] = None) -> bool:
        """
        Check if record has changed since last processing.
        
        Returns True if data has changed.
        """
        self.previous_hash = previous_hash
        current_hash = self.compute_source_hash()
        
        if previous_hash is None:
            # No previous record, so no change detected
            self.has_changed = False
        else:
            self.has_changed = (current_hash != previous_hash)
        
        return self.has_changed
    
    def standardize(self) -> None:
        """Apply standardization rules to all fields."""
        self._standardize_date()
        self._standardize_title()
        self._standardize_object_number()
        self._standardize_link()
    
    def _standardize_date(self) -> None:
        """Convert date to ISO 8601 format (YYYY-MM-DD)."""
        if not self.original_date or self.original_date.strip() == '':
            self.errors.append("Date is empty")
            return
        
        date_str = self.original_date.strip()
        formats = [
            '%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%m-%d-%Y',
            '%d/%m/%Y', '%d-%m-%Y', '%B %d, %Y', '%b %d, %Y', '%Y',
        ]
        
        from datetime import datetime
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                self.standardized_date = dt.strftime('%Y-%m-%d')
                return
            except ValueError:
                continue
        
        self.errors.append(f"Could not parse date: {date_str}")
    
    def _standardize_title(self) -> None:
        """Standardize title formatting."""
        if not self.original_title or self.original_title.strip() == '':
            self.errors.append("Title is empty")
            return
        
        title = self.original_title.strip()
        title = ' '.join(title.split())
        title = self._title_case(title)
        self.standardized_title = title
    
    @staticmethod
    def _title_case(text: str) -> str:
        """Convert to title case, preserving acronyms."""
        words = text.split()
        result = []
        
        for i, word in enumerate(words):
            if i == 0:
                result.append(word[0].upper() + word[1:].lower() if word else word)
            elif word.lower() in ('a', 'an', 'the', 'and', 'or', 'in', 'of', 'to'):
                result.append(word.lower())
            elif i > 0 and words[i-1].endswith(':'):
                result.append(word[0].upper() + word[1:].lower() if word else word)
            elif word.isupper() and len(word) > 1:
                result.append(word)
            else:
                result.append(word[0].upper() + word[1:].lower() if word else word)
        
        return ' '.join(result)
    
    def _standardize_object_number(self) -> None:
        """Standardize object number format."""
        if not self.original_object_number or self.original_object_number.strip() == '':
            self.errors.append("Object number is empty")
            return
        
        obj_num = self.original_object_number.strip().upper()
        obj_num = re.sub(r'\s+', '', obj_num)
        
        match = re.match(r'^(\d{4})[.\-]?(\d+)$', obj_num)
        if match:
            year, num = match.groups()
            self.standardized_object_number = f"{year}.{num}"
        else:
            self.standardized_object_number = obj_num
            self.errors.append(f"Object number doesn't match expected format: {obj_num}")
    
    def _standardize_link(self) -> None:
        """Validate and standardize URLs."""
        if not self.original_link or self.original_link.strip() == '':
            self.errors.append("Link is empty")
            return
        
        link = self.original_link.strip()
        
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', link):
            link = 'https://' + link
        
        try:
            result = urlparse(link)
            if not all([result.scheme, result.netloc]):
                self.errors.append(f"Invalid URL structure: {link}")
                return
        except Exception as e:
            self.errors.append(f"URL parsing error: {e}")
            return
        
        self.standardized_link = link
    
    def to_dict(self) -> Dict:
        """Return standardized record as dictionary."""
        return {
            'date': self.standardized_date or '',
            'title': self.standardized_title or '',
            'object_number': self.standardized_object_number or '',
            'link': self.standardized_link or '',
            'withdrawn': 'yes' if self.is_withdrawn else 'no',
        }


class InventoryProcessor:
    """Process museum inventory records with checksum verification."""
    
    def __init__(self, input_file: Path, corrections_file: Optional[Path] = None,
                 checksum_dir: Optional[Path] = None, verify_only: bool = False):
        self.input_file = input_file
        self.corrections_file = corrections_file
        self.verify_only = verify_only
        
        self.checksum_manager = ChecksumManager(checksum_dir)
        self.records: Dict[str, InventoryRecord] = {}
        self.corrections: list = []
        
        # Checksum tracking
        self.input_file_hash = None
        self.previous_input_file_hash = None
        self.record_checksums = {}
        self.previous_record_checksums = {}
        self.changed_records = []
        self.new_records = []
        self.deleted_records = []
        
        self.statistics = {
            'total_records': 0,
            'withdrawn_records': 0,
            'records_with_errors': 0,
            'total_errors': 0,
            'changed_records': 0,
            'new_records': 0,
            'deleted_records': 0,
        }
    
    def load_previous_checksums(self) -> None:
        """Load checksums from previous run."""
        checksum_file = self.checksum_manager.get_checksum_file(
            self.input_file, '_records'
        )
        self.previous_record_checksums = self.checksum_manager.load_checksums(checksum_file)
        
        # Also load previous file hash
        file_checksum_file = self.checksum_manager.get_checksum_file(
            self.input_file, '_file'
        )
        file_checksums = self.checksum_manager.load_checksums(file_checksum_file)
        self.previous_input_file_hash = file_checksums.get('hash')
    
    def verify_input_file_integrity(self) -> bool:
        """
        Verify input file hasn't been modified.
        
        Returns True if file is unchanged or if this is the first run.
        """
        self.input_file_hash, is_unchanged = self.checksum_manager.verify_file_integrity(
            self.input_file,
            self.previous_input_file_hash
        )
        
        if not is_unchanged:
            print(f"⚠ Input file has changed since last processing", file=sys.stderr)
            print(f"  Previous hash: {self.previous_input_file_hash}", file=sys.stderr)
            print(f"  Current hash:  {self.input_file_hash}", file=sys.stderr)
            return False
        
        if self.previous_input_file_hash:
            print(f"✓ Input file unchanged since last processing")
        else:
            print(f"ℹ First time processing this file")
        
        return True
    
    def save_input_file_hash(self) -> None:
        """Save current input file hash for future verification."""
        checksum_file = self.checksum_manager.get_checksum_file(
            self.input_file, '_file'
        )
        self.checksum_manager.save_checksums(
            checksum_file,
            {'hash': self.input_file_hash, 'timestamp': datetime.now().isoformat()}
        )
    
    def load_records(self) -> None:
        """Load records from TSV file."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    print("Error: Empty TSV file", file=sys.stderr)
                    sys.exit(1)
                
                missing_fields = InventoryRecord.REQUIRED_FIELDS - set(reader.fieldnames or [])
                if missing_fields:
                    print(f"Error: Missing required fields: {missing_fields}", file=sys.stderr)
                    sys.exit(1)
                
                for row_num, row in enumerate(reader, start=2):
                    obj_num = row.get('object_number', '').strip()
                    if not obj_num:
                        print(f"Warning: Skipping row {row_num} with no object number", 
                              file=sys.stderr)
                        continue
                    
                    record = InventoryRecord(
                        date=row.get('date', ''),
                        title=row.get('title', ''),
                        object_number=obj_num,
                        link=row.get('link', ''),
                    )
                    self.records[obj_num] = record
                    self.statistics['total_records'] += 1
        
        except FileNotFoundError:
            print(f"Error: File not found: {self.input_file}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def detect_record_changes(self) -> None:
        """Detect which records have changed, been added, or deleted."""
        current_obj_nums = set(self.records.keys())
        previous_obj_nums = set(self.previous_record_checksums.keys())
        
        # Detect changed records
        for obj_num in current_obj_nums & previous_obj_nums:
            record = self.records[obj_num]
            previous_hash = self.previous_record_checksums[obj_num]
            
            if record.check_for_changes(previous_hash):
                self.changed_records.append(obj_num)
                self.statistics['changed_records'] += 1
                print(f"⚠ Record changed: {obj_num}")
        
        # Detect new records
        self.new_records = list(current_obj_nums - previous_obj_nums)
        self.statistics['new_records'] = len(self.new_records)
        for obj_num in self.new_records:
            print(f"✚ New record: {obj_num}")
        
        # Detect deleted records
        self.deleted_records = list(previous_obj_nums - current_obj_nums)
        self.statistics['deleted_records'] = len(self.deleted_records)
        for obj_num in self.deleted_records:
            print(f"✗ Deleted record: {obj_num}")
    
    def compute_record_checksums(self) -> None:
        """Compute checksums for all current records."""
        for obj_num, record in self.records.items():
            self.record_checksums[obj_num] = record.compute_source_hash()
    
    def save_record_checksums(self) -> None:
        """Save checksums for future verification."""
        checksum_file = self.checksum_manager.get_checksum_file(
            self.input_file, '_records'
        )
        checksums_with_metadata = {
            'timestamp': datetime.now().isoformat(),
            'total_records': len(self.records),
            'records': self.record_checksums,
        }
        self.checksum_manager.save_checksums(checksum_file, checksums_with_metadata)
    
    def load_corrections(self) -> None:
        """Load corrections from a TSV file."""
        if not self.corrections_file or not self.corrections_file.exists():
            return
        
        try:
            with open(self.corrections_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                required = {'object_number', 'action'}
                missing = required - set(reader.fieldnames or [])
                if missing:
                    print(f"Warning: Corrections file missing fields: {missing}", 
                          file=sys.stderr)
                    return
                
                for row in reader:
                    self.corrections.append(row)
        
        except Exception as e:
            print(f"Warning: Could not read corrections file: {e}", file=sys.stderr)
    
    def apply_corrections(self) -> None:
        """Apply corrections and withdrawals."""
        for correction in self.corrections:
            obj_num = correction.get('object_number', '').strip()
            action = correction.get('action', '').strip().lower()
            
            if obj_num not in self.records:
                print(f"Warning: Object number in corrections not found: {obj_num}", 
                      file=sys.stderr)
                continue
            
            record = self.records[obj_num]
            
            if action == 'withdraw':
                record.is_withdrawn = True
                self.statistics['withdrawn_records'] += 1
            elif action == 'correct':
                if 'date' in correction and correction['date'].strip():
                    record.original_date = correction['date']
                if 'title' in correction and correction['title'].strip():
                    record.original_title = correction['title']
                if 'link' in correction and correction['link'].strip():
                    record.original_link = correction['link']
            else:
                print(f"Warning: Unknown action '{action}' for {obj_num}", file=sys.stderr)
    
    def standardize_all(self) -> None:
        """Standardize all records."""
        for record in self.records.values():
            if not record.is_withdrawn:
                record.standardize()
                if record.errors:
                    self.statistics['records_with_errors'] += 1
                    self.statistics['total_errors'] += len(record.errors)
    
    def write_output(self, output_file: Path) -> None:
        """Write standardized records to TSV file."""
        if self.verify_only:
            print("(Skipping output in verify-only mode)")
            return
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['date', 'title', 'object_number', 'link', 'withdrawn']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                
                for record in sorted(self.records.values(), 
                                    key=lambda r: r.original_object_number):
                    writer.writerow(record.to_dict())
        
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def write_verification_report(self, report_file: Path) -> None:
        """Write detailed verification report."""
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("MUSEUM INVENTORY VERIFICATION REPORT\n")
                f.write("=" * 70 + "\n\n")
                
                f.write(f"Verification Date: {datetime.now().isoformat()}\n")
                f.write(f"Input File: {self.input_file}\n")
                f.write(f"Current File Hash: {self.input_file_hash}\n")
                if self.previous_input_file_hash:
                    f.write(f"Previous File Hash: {self.previous_input_file_hash}\n")
                    f.write(f"File Status: {'UNCHANGED' if self.input_file_hash == self.previous_input_file_hash else 'CHANGED'}\n")
                f.write("\n")
                
                f.write("STATISTICS\n")
                f.write("-" * 70 + "\n")
                for key, value in self.statistics.items():
                    f.write(f"{key.replace('_', ' ').title()}: {value}\n")
                f.write("\n")
                
                if self.changed_records:
                    f.write("CHANGED RECORDS\n")
                    f.write("-" * 70 + "\n")
                    for obj_num in sorted(self.changed_records):
                        record = self.records[obj_num]
                        f.write(f"\nObject Number: {obj_num}\n")
                        f.write(f"Previous Hash: {self.previous_record_checksums.get(obj_num)}\n")
                        f.write(f"Current Hash:  {self.record_checksums.get(obj_num)}\n")
                        f.write(f"Title: {record.original_title}\n")
                    f.write("\n")
                
                if self.new_records:
                    f.write("NEW RECORDS\n")
                    f.write("-" * 70 + "\n")
                    for obj_num in sorted(self.new_records):
                        record = self.records[obj_num]
                        f.write(f"  {obj_num}: {record.original_title}\n")
                    f.write("\n")
                
                if self.deleted_records:
                    f.write("DELETED RECORDS\n")
                    f.write("-" * 70 + "\n")
                    for obj_num in sorted(self.deleted_records):
                        f.write(f"  {obj_num}\n")
                    f.write("\n")
                
                # Records with errors
                error_records = {obj_num: rec for obj_num, rec in self.records.items()
                               if rec.errors and not rec.is_withdrawn}
                
                if error_records:
                    f.write("RECORDS WITH ERRORS\n")
                    f.write("-" * 70 + "\n")
                    for obj_num in sorted(error_records.keys()):
                        record = error_records[obj_num]
                        f.write(f"\nObject Number: {obj_num}\n")
                        f.write(f"Title: {record.original_title}\n")
                        for error in record.errors:
                            f.write(f"  - {error}\n")
        
        except Exception as e:
            print(f"Error writing report file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def print_summary(self) -> None:
        """Print processing summary to console."""
        print("\n" + "=" * 70)
        print("INVENTORY PROCESSING COMPLETE")
        print("=" * 70)
        print(f"Total records processed: {self.statistics['total_records']}")
        print(f"  - New records: {self.statistics['new_records']}")
        print(f"  - Changed records: {self.statistics['changed_records']}")
        print(f"  - Deleted records: {self.statistics['deleted_records']}")
        print(f"Withdrawn records: {self.statistics['withdrawn_records']}")
        print(f"Records with errors: {self.statistics['records_with_errors']}")
        print(f"Total errors: {self.statistics['total_errors']}")


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records with checksum verification'
    )
    parser.add_argument('input', type=Path, 
                       help='Input TSV file with inventory records')
    parser.add_argument('-o', '--output', type=Path, 
                       default=Path('inventory_standardized.tsv'),
                       help='Output TSV file (default: inventory_standardized.tsv)')
    parser.add_argument('-c', '--corrections', type=Path,
                       help='TSV file with corrections and withdrawals')
    parser.add_argument('-r', '--report', type=Path, 
                       default=Path('verification_report.txt'),
                       help='Output report file (default: verification_report.txt)')
    parser.add_argument('--checksum-dir', type=Path, default=Path('.checksums'),
                       help='Directory for storing checksums (default: .checksums)')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify checksums without processing (dry-run mode)')
    
    args = parser.parse_args()
    
    # Load previous checksums
    processor = InventoryProcessor(
        args.input,
        args.corrections,
        args.checksum_dir,
        args.verify_only
    )
    processor.load_previous_checksums()
    
    # Verify file integrity
    print("Verifying input file integrity...")
    if not processor.verify_input_file_integrity():
        print("⚠ Warning: Input file has been modified")
    
    print("\nLoading inventory records...")
    processor.load_records()
    
    print("Detecting changes...")
    processor.detect_record_changes()
    processor.compute_record_checksums()
    
    if not args.verify_only:
        print("\nLoading corrections...")
        processor.load_corrections()
        
        print("Applying corrections...")
        processor.apply_corrections()
        
        print("Standardizing records...")
        processor.standardize_all()
        
        print("Writing output...")
        processor.write_output(args.output)
    
    print("Writing verification report...")
    processor.write_verification_report(args.report)
    
    if not args.verify_only:
        print("Saving checksums...")
        processor.save_record_checksums()
        processor.save_input_file_hash()
    
    processor.print_summary()


if __name__ == '__main__':
    main()
```

## Key Features

### Checksum Verification:

1. **File-level checksums**: Detects if entire input file has changed
2. **Record-level checksums**: Tracks individual record modifications
3. **Change detection**: Identifies:
   - New records added
   - Existing records modified
   - Records deleted from source
4. **Persistent storage**: Checksums saved in `.checksums/` directory

### Usage Examples:

```bash
# First run - creates baseline checksums
python standardize_inventory.py inventory.tsv -o standardized.tsv

# Subsequent runs - detects changes
python standardize_inventory.py inventory.tsv -o standardized.tsv

# Verify-only mode (dry-run, no output)
python standardize_inventory.py inventory.tsv --verify-only

# Custom checksum directory
python standardize_inventory.py inventory.tsv --checksum-dir /path/to/checksums
```

### Output Structure:

```
.checksums/
├── inventory_file.json        # File-level hash
├── inventory_records.json     # Record-level hashes
└── verification_report.txt    # Detailed change report
```

### Checksum File Format:

```json
{
  "timestamp": "2024-01-15T10:30:00.123456",
  "total_records": 4,
  "records": {
    "2023.001": "a1b2c3d4...",
    "2023.002": "e5f6g7h8...",
    "2023.003": "i9j0k1l2..."
  }
}
```

### Benefits:

- **Data integrity**: Confirm source data hasn't been corrupted
- **Audit trail**: Track what changed between runs
- **Conflict detection**: Identify unexpected modifications
- **Reproducibility**: Re-run only on actual changes
- **Version control**: Complement git with content-based verification
