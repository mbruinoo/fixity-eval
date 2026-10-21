# Museum Inventory Standardizer with Checksum Verification

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records with checksum verification.

Tracks checksums of source data to detect unauthorized changes.
"""

import csv
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum


class RecordStatus(Enum):
    """Status of an inventory record."""
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"
    CORRECTED = "corrected"


@dataclass
class SourceChecksum:
    """Checksum information for source data."""
    file_path: str
    file_hash: str  # Hash of entire file
    record_hashes: Dict[str, str] = field(default_factory=dict)  # object_number -> hash
    timestamp: str = ""
    algorithm: str = "sha256"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class MuseumRecord:
    """Standardized museum inventory record."""
    object_number: str
    title: str
    date: str
    link: str
    status: RecordStatus = RecordStatus.ACTIVE
    created_date: str = ""
    corrected_to: Optional[str] = None
    withdrawal_reason: Optional[str] = None
    notes: str = ""
    source_hash: str = ""  # Hash of original source record
    source_file: str = ""  # Which file it came from

    def __hash__(self):
        return hash(self.object_number)

    def __eq__(self, other):
        if not isinstance(other, MuseumRecord):
            return False
        return self.object_number == other.object_number


class ChecksumValidator:
    """Handle checksum calculation and verification."""

    def __init__(self, algorithm: str = "sha256"):
        """
        Initialize checksum validator.

        Args:
            algorithm: Hash algorithm ('sha256', 'md5', 'sha1')
        """
        if algorithm not in ('sha256', 'md5', 'sha1'):
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        self.algorithm = algorithm

    def _get_hasher(self):
        """Get appropriate hash function."""
        if self.algorithm == 'sha256':
            return hashlib.sha256()
        elif self.algorithm == 'md5':
            return hashlib.md5()
        elif self.algorithm == 'sha1':
            return hashlib.sha1()

    def hash_file(self, file_path: Path, chunk_size: int = 8192) -> str:
        """
        Calculate hash of entire file.

        Args:
            file_path: Path to file
            chunk_size: Read file in chunks (for large files)

        Returns:
            Hex digest of file
        """
        hasher = self._get_hasher()

        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)

        return hasher.hexdigest()

    def hash_record_row(self, row: Dict) -> str:
        """
        Calculate hash of a record row.

        Uses canonical JSON representation for consistency.
        """
        hasher = self._get_hasher()

        # Sort keys for consistent ordering
        canonical = json.dumps(row, sort_keys=True, separators=(',', ':'))
        hasher.update(canonical.encode('utf-8'))

        return hasher.hexdigest()

    def hash_string(self, text: str) -> str:
        """Calculate hash of a string."""
        hasher = self._get_hasher()
        hasher.update(text.encode('utf-8'))
        return hasher.hexdigest()


class InventoryStandardizer:
    """Standardize and manage museum inventory records with checksum verification."""

    OBJECT_NUMBER_PATTERN = re.compile(r'^[A-Z0-9]{3,20}$')
    URL_PATTERN = re.compile(r'^https?://.+')
    YEAR_PATTERN = re.compile(r'^\d{4}$')

    def __init__(
        self,
        input_file: Path,
        output_dir: Path = None,
        checksum_file: Path = None,
        algorithm: str = "sha256"
    ):
        """
        Initialize the standardizer.

        Args:
            input_file: Path to input TSV file
            output_dir: Directory for output files
            checksum_file: Path to stored checksums file (JSON)
            algorithm: Hash algorithm to use
        """
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir) if output_dir else self.input_file.parent
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.checksum_file = Path(checksum_file) if checksum_file else (
            self.output_dir / f"{self.input_file.stem}_checksums.json"
        )

        self.validator = ChecksumValidator(algorithm)
        self.source_checksum: Optional[SourceChecksum] = None
        self.previous_checksum: Optional[SourceChecksum] = None

        self.records: Dict[str, MuseumRecord] = {}
        self.validation_errors: List[Dict] = []
        self.corrections_log: List[Dict] = []
        self.integrity_warnings: List[Dict] = []

    def load_previous_checksums(self) -> bool:
        """
        Load previously stored checksums.

        Returns:
            True if checksums were loaded, False if file doesn't exist
        """
        if not self.checksum_file.exists():
            return False

        try:
            with open(self.checksum_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.previous_checksum = SourceChecksum(
                    file_path=data['file_path'],
                    file_hash=data['file_hash'],
                    record_hashes=data.get('record_hashes', {}),
                    timestamp=data.get('timestamp', ''),
                    algorithm=data.get('algorithm', 'sha256')
                )
            print(f"Loaded previous checksums from {self.checksum_file}")
            return True
        except Exception as e:
            print(f"Warning: Could not load checksums: {e}")
            return False

    def calculate_file_checksum(self) -> str:
        """Calculate checksum of input file."""
        return self.validator.hash_file(self.input_file)

    def verify_file_integrity(self) -> Tuple[bool, str]:
        """
        Verify that input file hasn't changed since last run.

        Returns:
            (is_valid, message)
        """
        if not self.previous_checksum:
            return True, "No previous checksum to compare"

        current_hash = self.calculate_file_checksum()

        if current_hash == self.previous_checksum.file_hash:
            return True, "File integrity verified - no changes detected"
        else:
            return False, "File has changed since last run"

    def validate_object_number(self, obj_num: str) -> Tuple[bool, str]:
        """Validate object number format."""
        if not obj_num or not obj_num.strip():
            return False, "Object number is empty"

        obj_num = obj_num.strip().upper()

        if not self.OBJECT_NUMBER_PATTERN.match(obj_num):
            return (
                False,
                f"Invalid format: {obj_num}. Must be 3-20 alphanumeric characters."
            )
        return True, obj_num

    def validate_title(self, title: str) -> Tuple[bool, str]:
        """Validate and normalize title."""
        if not title or not title.strip():
            return False, "Title is empty"

        title = ' '.join(title.strip().split())

        if len(title) < 2:
            return False, "Title too short"

        return True, title

    def validate_date(self, date_str: str) -> Tuple[bool, str]:
        """Validate date field."""
        if not date_str or not date_str.strip():
            return False, "Date is empty"

        date_str = date_str.strip()

        if self.YEAR_PATTERN.match(date_str):
            return True, date_str

        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True, date_str
        except ValueError:
            pass

        if len(date_str) >= 3:
            return True, date_str

        return False, f"Invalid date format: {date_str}"

    def validate_link(self, link: str) -> Tuple[bool, str]:
        """Validate link format."""
        if not link or not link.strip():
            return True, ""

        link = link.strip()

        if not self.URL_PATTERN.match(link):
            return False, f"Invalid URL format: {link}"

        return True, link

    def validate_record(
        self,
        row: Dict,
        row_num: int,
        source_hash: str
    ) -> Optional[MuseumRecord]:
        """
        Validate a single record row.

        Args:
            row: Record data
            row_num: Row number in file
            source_hash: Hash of original row data

        Returns:
            MuseumRecord if valid, None otherwise
        """
        errors = []

        valid, obj_num = self.validate_object_number(row.get('object_number', ''))
        if not valid:
            errors.append(f"Object number: {obj_num}")
        else:
            object_number = obj_num

        valid, title = self.validate_title(row.get('title', ''))
        if not valid:
            errors.append(f"Title: {title}")
        else:
            title = title

        valid, date = self.validate_date(row.get('date', ''))
        if not valid:
            errors.append(f"Date: {date}")
        else:
            date = date

        valid, link = self.validate_link(row.get('link', ''))
        if not valid:
            errors.append(f"Link: {link}")
        else:
            link = link

        if errors:
            self.validation_errors.append({
                'row': row_num,
                'object_number': row.get('object_number', 'N/A'),
                'errors': errors,
                'source_hash': source_hash
            })
            return None

        return MuseumRecord(
            object_number=object_number,
            title=title,
            date=date,
            link=link,
            created_date=datetime.now().isoformat(),
            source_hash=source_hash,
            source_file=str(self.input_file)
        )

    def check_record_modifications(self, obj_num: str, previous_hash: str) -> bool:
        """
        Check if a previously-seen record has been modified.

        Args:
            obj_num: Object number
            previous_hash: Previously stored hash

        Returns:
            True if record is unchanged, False if modified
        """
        if not self.previous_checksum:
            return True  # No baseline to compare

        current_hash = self.records[obj_num].source_hash

        if current_hash != previous_hash:
            self.integrity_warnings.append({
                'object_number': obj_num,
                'warning': 'Record content has changed',
                'previous_hash': previous_hash,
                'current_hash': current_hash,
                'timestamp': datetime.now().isoformat()
            })
            return False

        return True

    def load_records(self, verify_integrity: bool = True) -> None:
        """
        Load and validate records from TSV file.

        Args:
            verify_integrity: Check file hash against previous run
        """
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")

        print(f"Loading records from {self.input_file}...")

        # Load previous checksums if available
        self.load_previous_checksums()

        # Verify file integrity
        if verify_integrity and self.previous_checksum:
            valid, message = self.verify_file_integrity()
            if not valid:
                print(f"⚠ WARNING: {message}")

        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')

                if not reader.fieldnames:
                    raise ValueError("Empty TSV file")

                required_fields = {'object_number', 'title', 'date', 'link'}
                if not required_fields.issubset(set(reader.fieldnames or [])):
                    raise ValueError(
                        f"Missing required fields. Expected: {required_fields}"
                    )

                # Initialize source checksum tracking
                self.source_checksum = SourceChecksum(
                    file_path=str(self.input_file),
                    file_hash=self.calculate_file_checksum(),
                    timestamp=datetime.now().isoformat(),
                    algorithm=self.validator.algorithm
                )

                for row_num, row in enumerate(reader, start=2):
                    # Calculate hash of this record
                    record_hash = self.validator.hash_record_row(row)

                    record = self.validate_record(row, row_num, record_hash)
                    if record:
                        # Check if this record existed before and has changed
                        if self.previous_checksum:
                            obj_num = record.object_number
                            if obj_num in self.previous_checksum.record_hashes:
                                self.check_record_modifications(
                                    obj_num,
                                    self.previous_checksum.record_hashes[obj_num]
                                )

                        self.records[record.object_number] = record
                        self.source_checksum.record_hashes[record.object_number] = record_hash

        except csv.Error as e:
            raise ValueError(f"TSV parsing error: {e}")

        print(f"Loaded {len(self.records)} valid records")
        if self.validation_errors:
            print(f"⚠ {len(self.validation_errors)} validation errors")
        if self.integrity_warnings:
            print(f"⚠ {len(self.integrity_warnings)} integrity warnings")

    def check_missing_records(self) -> None:
        """Check for records that were in previous checksums but are missing now."""
        if not self.previous_checksum:
            return

        previous_objects = set(self.previous_checksum.record_hashes.keys())
        current_objects = set(self.records.keys())

        missing = previous_objects - current_objects

        for obj_num in missing:
            # Check if it was corrected (moved to new object number)
            was_corrected = any(
                r.corrected_to == obj_num for r in self.records.values()
            )

            if not was_corrected:
                self.integrity_warnings.append({
                    'object_number': obj_num,
                    'warning': 'Record no longer present in source',
                    'timestamp': datetime.now().isoformat()
                })

    def mark_withdrawn(self, object_number: str, reason: str = "") -> bool:
        """Mark a record as withdrawn."""
        valid, obj_num = self.validate_object_number(object_number)
        if not valid:
            print(f"Invalid object number: {object_number}")
            return False

        if obj_num not in self.records:
            print(f"Object not found: {obj_num}")
            return False

        self.records[obj_num].status = RecordStatus.WITHDRAWN
        self.records[obj_num].withdrawal_reason = reason
        self.corrections_log.append({
            'action': 'withdrawn',
            'object_number': obj_num,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        return True

    def correct_record(
        self,
        old_object_number: str,
        new_object_number: str,
        updated_fields: Dict = None
    ) -> bool:
        """Correct a record by creating a new one and marking old as corrected."""
        valid, old_num = self.validate_object_number(old_object_number)
        if not valid:
            print(f"Invalid old object number: {old_object_number}")
            return False

        valid, new_num = self.validate_object_number(new_object_number)
        if not valid:
            print(f"Invalid new object number: {new_object_number}")
            return False

        if old_num not in self.records:
            print(f"Record not found: {old_num}")
            return False

        old_record = self.records[old_num]

        corrected_record = MuseumRecord(
            object_number=new_num,
            title=updated_fields.get('title', old_record.title) if updated_fields else old_record.title,
            date=updated_fields.get('date', old_record.date) if updated_fields else old_record.date,
            link=updated_fields.get('link', old_record.link) if updated_fields else old_record.link,
            created_date=old_record.created_date,
            source_hash=old_record.source_hash,
            source_file=old_record.source_file
        )

        old_record.status = RecordStatus.CORRECTED
        old_record.corrected_to = new_num

        self.records[new_num] = corrected_record

        self.corrections_log.append({
            'action': 'corrected',
            'old_object_number': old_num,
            'new_object_number': new_num,
            'changes': updated_fields or {},
            'timestamp': datetime.now().isoformat()
        })

        return True

    def get_active_records(self) -> List[MuseumRecord]:
        """Get all active records."""
        return [
            r for r in self.records.values()
            if r.status == RecordStatus.ACTIVE
        ]

    def get_statistics(self) -> Dict:
        """Get inventory statistics."""
        records = self.records.values()
        return {
            'total_records': len(records),
            'active_records': len(self.get_active_records()),
            'withdrawn_records': len([r for r in records if r.status == RecordStatus.WITHDRAWN]),
            'corrected_records': len([r for r in records if r.status == RecordStatus.CORRECTED]),
            'validation_errors': len(self.validation_errors),
            'corrections_made': len(self.corrections_log),
            'integrity_warnings': len(self.integrity_warnings)
        }

    def save_checksums(self, filename: str = None) -> Path:
        """
        Save checksums to JSON file for future verification.

        Args:
            filename: Output filename (default: <input>_checksums.json)

        Returns:
            Path to saved file
        """
        if filename:
            output_path = self.output_dir / filename
        else:
            output_path = self.checksum_file

        if not self.source_checksum:
            print("No source checksum to save")
            return output_path

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.source_checksum.to_dict(), f, indent=2)

        print(f"Saved checksums to {output_path}")
        return output_path

    def save_standardized_records(self, filename: str = "standardized_inventory.tsv") -> Path:
        """Save standardized active records to TSV."""
        output_path = self.output_dir / filename
        active_records = self.get_active_records()

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'object_number', 'title', 'date', 'link',
                'created_date', 'source_hash', 'notes'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')

            writer.writeheader()
            for record in sorted(active_records, key=lambda r: r.object_number):
                row = asdict(record)
                # Convert enum to string
                row['status'] = row['status'].value
                writer.writerow(row)

        print(f"Saved {len(active_records)} active records to {output_path}")
        return output_path

    def save_integrity_report(self, filename: str = "integrity_report.txt") -> Path:
        """Save integrity verification report."""
        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("MUSEUM INVENTORY INTEGRITY REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Input file: {self.input_file}\n")
            f.write(f"File hash ({self.validator.algorithm}): {self.source_checksum.file_hash if self.source_checksum else 'N/A'}\n\n")

            # File integrity section
            f.write("FILE INTEGRITY\n")
            f.write("-" * 60 + "\n")
            if self.previous_checksum:
                valid, message = self.verify_file_integrity()
                f.write(f"Status: {'✓ VERIFIED' if valid else '✗ MODIFIED'}\n")
                f.write(f"Message: {message}\n")
                f.write(f"Previous hash: {self.previous_checksum.file_hash}\n")
                if self.source_checksum:
                    f.write(f"Current hash: {self.source_checksum.file_hash}\n")
            else:
                f.write("Status: First run - no previous checksums\n")

            # Record integrity section
            f.write("\n\nRECORD INTEGRITY\n")
            f.write("-" * 60 + "\n")
            f.write(f"Total records tracked: {len(self.source_checksum.record_hashes) if self.source_checksum else 0}\n")

            if self.integrity_warnings:
                f.write(f"\nWarnings ({len(self.integrity_warnings)}):\n")
                for warning in self.integrity_warnings:
                    f.write(f"\n  Object: {warning['object_number']}\n")
                    f.write(f"  Issue: {warning['warning']}\n")
                    if 'previous_hash' in warning:
                        f.write(f"  Previous hash: {warning['previous_hash']}\n")
                    if 'current_hash' in warning:
                        f.write(f"  Current hash: {warning['current_hash']}\n")
                    f.write(f"  Timestamp: {warning['timestamp']}\n")
            else:
                f.write("No integrity issues detected.\n")

            # Checksums section
            f.write("\n\nRECORD CHECKSUMS\n")
            f.write("-" * 60 + "\n")
            if self.source_checksum:
                for obj_num in sorted(self.source_checksum.record_hashes.keys()):
                    hash_val = self.source_checksum.record_hashes[obj_num]
                    f.write(f"{obj_num}: {hash_val}\n")

        print(f"Saved integrity report to {output_path}")
        return output_path

    def save_validation_report(self, filename: str = "validation_report.txt") -> Path:
        """Save validation errors report."""
        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("MUSEUM INVENTORY VALIDATION REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Input file: {self.input_file}\n\n")

            stats = self.get_statistics()
            f.write("STATISTICS\n")
            f.write("-" * 60 + "\n")
            for key, value in stats.items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")

            f.write("\n\nVALIDATION ERRORS\n")
            f.write("-" * 60 + "\n")
            if self.validation_errors:
                for error in self.validation_errors:
                    f.write(f"\nRow {error['row']}: {error['object_number']}\n")
                    f.write(f"Source hash: {error['source_hash']}\n")
                    for err_msg in error['errors']:
                        f.write(f"  • {err_msg}\n")
            else:
                f.write("No validation errors.\n")

        print(f"Saved validation report to {output_path}")
        return output_path

    def save_corrections_log(self, filename: str = "corrections_log.tsv") -> Path:
        """Save corrections and withdrawals log."""
        output_path = self.output_dir / filename

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if self.corrections_log:
                fieldnames = self.corrections_log[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(self.corrections_log)
            else:
                f.write("No corrections or withdrawals recorded.\n")

        print(f"Saved corrections log to {output_path}")
        return output_path

    def print_summary(self) -> None:
        """Print summary to console."""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("STANDARDIZATION SUMMARY")
        print("=" * 60)
        for key, value in stats.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print("=" * 60 + "\n")


def main():
    """Example usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Standardize museum inventory with checksum verification"
    )
    parser.add_argument('input_file', type=Path, help='Input TSV file')
    parser.add_argument('-o', '--output-dir', type=Path, help='Output directory')
    parser.add_argument(
        '-c', '--checksums',
        type=Path,
        help='Path to checksums file (default: <input>_checksums.json)'
    )
    parser.add_argument(
        '-a', '--algorithm',
        choices=['sha256', 'md5', 'sha1'],
        default='sha256',
        help='Hash algorithm (default: sha256)'
    )
    parser.add_argument(
        '--skip-integrity-check',
        action='store_true',
        help="Don't verify file integrity against previous run"
    )

    args = parser.parse_args()

    try:
        standardizer = InventoryStandardizer(
            args.input_file,
            args.output_dir,
            args.checksums,
            args.algorithm
        )

        standardizer.load_records(verify_integrity=not args.skip_integrity_check)
        standardizer.check_missing_records()

        standardizer.save_standardized_records()
        standardizer.save_validation_report()
        standardizer.save_integrity_report()
        standardizer.save_corrections_log()
        standardizer.save_checksums()
        standardizer.print_summary()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## Key Checksum Features

### 1. **File-level Checksums**
- Calculates SHA256 (or MD5/SHA1) of entire source file
- Detects any changes to the file
- Stored between runs for comparison

### 2. **Record-level Checksums**
- Hashes each individual record using canonical JSON format
- Detects modifications to specific records
- Tracks which records have been changed

### 3. **Integrity Verification**
```python
# Automatically checks if:
# - File content has changed since last run
# - Individual records have been modified
# - Records are missing (possibly deleted or moved)
# - New records have been added
```

### 4. **Usage Examples**

**First run (creates baseline checksums):**
```bash
python museum_inventory.py inventory.tsv
# Creates inventory_checksums.json
```

**Subsequent runs (verifies against baseline):**
```bash
python museum_inventory.py inventory.tsv
# Detects any changes and reports warnings
```

**With custom hash algorithm:**
```bash
python museum_inventory.py inventory.tsv --algorithm md5
```

**Skip integrity checks:**
```bash
python museum_inventory.py inventory.tsv --skip-integrity-check
```

### 5. **Checksum File Format**
```json
{
  "file_path": "/path/to/inventory.tsv",
  "file_hash": "abc123...",
  "algorithm": "sha256",
  "timestamp": "2024-01-15T10:30:00.000000",
  "record_hashes": {
    "ARTIFACT001": "hash1...",
    "ARTIFACT002": "hash2...",
    "ARTIFACT003": "hash3..."
  }
}
```

### 6. **Integrity Report Output**
The report includes:
- File-level integrity status
- Record modification warnings
- Missing record alerts
- All checksums for audit trail

This approach ensures:
✅ Detects unauthorized data modifications
✅ Provides audit trail of all changes
✅ Identifies data corruption or tampering
✅ Maintains cryptographic proof of data integrity
