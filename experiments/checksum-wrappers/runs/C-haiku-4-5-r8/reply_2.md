# Museum Inventory with Checksum Verification

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records with checksum verification.

Detects unauthorized changes to source data between runs.
"""

import argparse
import csv
import hashlib
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class InventoryRecord:
    """Represents a single museum inventory record."""
    
    date: str
    title: str
    object_number: str
    link: str
    withdrawn: bool = False
    correction_note: Optional[str] = None
    
    def validate(self) -> list[str]:
        """Validate record fields."""
        errors = []
        
        try:
            datetime.fromisoformat(self.date)
        except ValueError:
            errors.append(f"Invalid date format: {self.date}")
        
        if not self.title or not self.title.strip():
            errors.append("Title cannot be empty")
        
        if not self.object_number or not self.object_number.strip():
            errors.append("Object number cannot be empty")
        
        if self.object_number and not self._is_valid_object_number():
            errors.append(f"Invalid object number format: {self.object_number}")
        
        if not self.link or not self.link.strip():
            errors.append("Link cannot be empty")
        elif not self._is_valid_url():
            errors.append(f"Invalid URL format: {self.link}")
        
        return errors
    
    def _is_valid_object_number(self) -> bool:
        """Check if object number matches expected format."""
        parts = self.object_number.strip().split('.')
        if len(parts) < 2:
            return False
        if not parts[0].isdigit() or len(parts[0]) != 4:
            return False
        return True
    
    def _is_valid_url(self) -> bool:
        """Basic URL validation."""
        url = self.link.strip()
        return url.startswith(('http://', 'https://', 'file://'))
    
    def normalize(self) -> 'InventoryRecord':
        """Normalize record fields."""
        return InventoryRecord(
            date=self.date.strip(),
            title=self.title.strip(),
            object_number=self.object_number.strip(),
            link=self.link.strip(),
            withdrawn=self.withdrawn,
            correction_note=self.correction_note.strip() if self.correction_note else None
        )
    
    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            'date': self.date,
            'title': self.title,
            'object_number': self.object_number,
            'link': self.link,
            'withdrawn': self.withdrawn,
            'correction_note': self.correction_note or ''
        }


@dataclass
class ChecksumEntry:
    """Represents a checksum record for a single object."""
    
    object_number: str
    record_hash: str
    file_hash: str
    timestamp: str
    hash_algorithm: str = 'sha256'
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


class ChecksumManager:
    """Manage checksums for inventory records and files."""
    
    HASH_ALGORITHM = 'sha256'
    
    @staticmethod
    def compute_record_hash(record: InventoryRecord) -> str:
        """
        Compute hash of a single record's data.
        
        Uses normalized record data to ensure consistent hashing.
        """
        # Create canonical representation
        data = {
            'date': record.date.strip(),
            'title': record.title.strip(),
            'object_number': record.object_number.strip(),
            'link': record.link.strip(),
            'withdrawn': record.withdrawn
        }
        
        # Convert to JSON with sorted keys for consistency
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        
        # Compute hash
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    @staticmethod
    def compute_file_hash(file_path: Path) -> str:
        """
        Compute hash of entire file.
        
        Useful for detecting any changes to the source file.
        """
        hash_obj = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except IOError as e:
            logger.error(f"Error computing file hash: {e}")
            return None
    
    @staticmethod
    def compute_manifest_hash(records: dict[str, InventoryRecord]) -> str:
        """
        Compute hash of all record hashes (manifest checksum).
        
        Detects changes to the collection as a whole.
        """
        # Sort by object number and create manifest
        sorted_numbers = sorted(records.keys())
        manifest_data = []
        
        for obj_num in sorted_numbers:
            record = records[obj_num]
            record_hash = ChecksumManager.compute_record_hash(record)
            manifest_data.append(f"{obj_num}:{record_hash}")
        
        manifest_str = '\n'.join(manifest_data)
        return hashlib.sha256(manifest_str.encode('utf-8')).hexdigest()


class ChecksumStore:
    """Store and retrieve checksums for verification."""
    
    def __init__(self, checksum_file: Path):
        self.checksum_file = checksum_file
        self.checksums: dict[str, ChecksumEntry] = {}
        self.manifest_hash: Optional[str] = None
        self.file_hash: Optional[str] = None
    
    def load(self) -> bool:
        """
        Load checksums from file.
        
        Returns:
            True if successful
        """
        if not self.checksum_file.exists():
            logger.info(f"No existing checksum file: {self.checksum_file}")
            return True
        
        try:
            with open(self.checksum_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load metadata
            self.manifest_hash = data.get('manifest_hash')
            self.file_hash = data.get('file_hash')
            
            # Load individual record checksums
            for entry_data in data.get('records', []):
                entry = ChecksumEntry(**entry_data)
                self.checksums[entry.object_number] = entry
            
            logger.info(f"Loaded {len(self.checksums)} checksums")
            return True
        
        except Exception as e:
            logger.error(f"Error loading checksums: {e}")
            return False
    
    def save(self, records: dict[str, InventoryRecord], 
             file_hash: str, manifest_hash: str):
        """
        Save checksums to file.
        
        Args:
            records: Dictionary of inventory records
            file_hash: Hash of the source file
            manifest_hash: Hash of all record hashes
        """
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'hash_algorithm': ChecksumManager.HASH_ALGORITHM,
                'manifest_hash': manifest_hash,
                'file_hash': file_hash,
                'records': []
            }
            
            for object_num in sorted(records.keys()):
                record = records[object_num]
                entry = ChecksumEntry(
                    object_number=object_num,
                    record_hash=ChecksumManager.compute_record_hash(record),
                    file_hash=file_hash,
                    timestamp=datetime.now().isoformat()
                )
                data['records'].append(entry.to_dict())
            
            with open(self.checksum_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(records)} checksums")
        
        except Exception as e:
            logger.error(f"Error saving checksums: {e}")
    
    def verify_record(self, record: InventoryRecord) -> tuple[bool, str]:
        """
        Verify that a record matches its stored checksum.
        
        Returns:
            (is_valid, message)
        """
        if record.object_number not in self.checksums:
            return True, "No previous checksum (new record)"
        
        stored_entry = self.checksums[record.object_number]
        current_hash = ChecksumManager.compute_record_hash(record)
        
        if current_hash == stored_entry.record_hash:
            return True, "Checksum matches"
        else:
            return False, f"Checksum mismatch (expected {stored_entry.record_hash}, got {current_hash})"
    
    def verify_all(self, records: dict[str, InventoryRecord]) -> list[tuple[str, bool, str]]:
        """
        Verify all records.
        
        Returns:
            List of (object_number, is_valid, message) tuples
        """
        results = []
        for obj_num in sorted(records.keys()):
            record = records[obj_num]
            is_valid, message = self.verify_record(record)
            results.append((obj_num, is_valid, message))
        return results
    
    def verify_file_integrity(self, file_path: Path) -> tuple[bool, str]:
        """
        Verify that the source file hasn't been modified.
        
        Returns:
            (is_valid, message)
        """
        if not self.file_hash:
            return True, "No previous file hash"
        
        current_hash = ChecksumManager.compute_file_hash(file_path)
        
        if current_hash == self.file_hash:
            return True, "File integrity verified"
        else:
            return False, f"File has been modified (expected {self.file_hash}, got {current_hash})"
    
    def verify_manifest(self, records: dict[str, InventoryRecord]) -> tuple[bool, str]:
        """
        Verify that the collection as a whole hasn't changed.
        
        Returns:
            (is_valid, message)
        """
        if not self.manifest_hash:
            return True, "No previous manifest hash"
        
        current_manifest = ChecksumManager.compute_manifest_hash(records)
        
        if current_manifest == self.manifest_hash:
            return True, "Manifest verified (no collection changes)"
        else:
            return False, f"Collection changed (manifest mismatch)"


class InventoryProcessor:
    """Process and standardize museum inventory records."""
    
    def __init__(self, input_file: Path, checksum_file: Optional[Path] = None):
        self.input_file = input_file
        self.checksum_store = ChecksumStore(
            checksum_file or input_file.parent / f"{input_file.stem}.checksums.json"
        )
        self.records: dict[str, InventoryRecord] = {}
        self.corrections_log: list[dict] = []
        self.validation_errors: list[tuple[int, str, list[str]]] = []
        self.integrity_issues: list[tuple[str, bool, str]] = []
    
    def read_inventory(self) -> bool:
        """Read inventory from TSV file."""
        if not self.input_file.exists():
            logger.error(f"File not found: {self.input_file}")
            return False
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    logger.error("TSV file is empty or malformed")
                    return False
                
                required_fields = {'date', 'title', 'object_number', 'link'}
                missing_fields = required_fields - set(reader.fieldnames or [])
                
                if missing_fields:
                    logger.error(f"Missing required columns: {missing_fields}")
                    return False
                
                for line_num, row in enumerate(reader, start=2):
                    try:
                        record = InventoryRecord(
                            date=row['date'],
                            title=row['title'],
                            object_number=row['object_number'],
                            link=row['link'],
                            withdrawn=row.get('withdrawn', 'False').lower() == 'true',
                            correction_note=row.get('correction_note')
                        )
                        self.records[record.object_number] = record
                    
                    except KeyError as e:
                        logger.warning(f"Line {line_num}: Missing field {e}")
            
            logger.info(f"Loaded {len(self.records)} records")
            return True
        
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return False
    
    def verify_integrity(self) -> bool:
        """
        Verify checksums and file integrity.
        
        Returns:
            True if all checks pass
        """
        logger.info("Verifying data integrity...")
        
        # Load previous checksums
        if not self.checksum_store.load():
            return False
        
        # Verify file integrity
        file_valid, file_msg = self.checksum_store.verify_file_integrity(self.input_file)
        logger.info(f"File integrity: {file_msg}")
        if not file_valid:
            logger.warning("Source file has been modified")
        
        # Verify manifest
        manifest_valid, manifest_msg = self.checksum_store.verify_manifest(self.records)
        logger.info(f"Collection integrity: {manifest_msg}")
        if not manifest_valid:
            logger.warning("Collection has changed")
        
        # Verify individual records
        results = self.checksum_store.verify_all(self.records)
        
        issues = [(obj, valid, msg) for obj, valid, msg in results if not valid]
        if issues:
            logger.warning(f"Found {len(issues)} records with checksum mismatches")
            self.integrity_issues = issues
            return False
        
        logger.info("All integrity checks passed")
        return True
    
    def apply_corrections(self, corrections_file: Path) -> bool:
        """Apply corrections from a separate corrections file."""
        if not corrections_file.exists():
            logger.warning(f"Corrections file not found: {corrections_file}")
            return True
        
        try:
            with open(corrections_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                for row in reader:
                    object_num = row.get('object_number')
                    field = row.get('field')
                    new_value = row.get('new_value')
                    reason = row.get('reason', '')
                    
                    if object_num not in self.records:
                        logger.warning(f"Correction for unknown object: {object_num}")
                        continue
                    
                    record = self.records[object_num]
                    old_value = getattr(record, field, None)
                    
                    if field == 'withdrawn':
                        record.withdrawn = new_value.lower() == 'true'
                    elif hasattr(record, field):
                        setattr(record, field, new_value)
                        record.correction_note = reason
                    else:
                        logger.warning(f"Unknown field for correction: {field}")
                        continue
                    
                    self.corrections_log.append({
                        'object_number': object_num,
                        'field': field,
                        'old_value': old_value,
                        'new_value': new_value,
                        'reason': reason,
                        'date_applied': datetime.now().isoformat()
                    })
                    logger.info(f"Applied correction to {object_num}: {field}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error reading corrections file: {e}")
            return False
    
    def normalize_all(self):
        """Normalize all records in place."""
        for object_num in self.records:
            self.records[object_num] = self.records[object_num].normalize()
        logger.info("Normalized all records")
    
    def validate_all(self) -> bool:
        """Validate all records."""
        for object_num, record in self.records.items():
            errors = record.validate()
            if errors:
                self.validation_errors.append((0, object_num, errors))
        
        if self.validation_errors:
            logger.warning(f"Found {len(self.validation_errors)} records with validation errors")
            return False
        
        logger.info("All records passed validation")
        return True
    
    def write_output(self, output_file: Path, include_withdrawn: bool = False):
        """Write standardized inventory to TSV file."""
        try:
            records_to_write = [
                record for record in self.records.values()
                if include_withdrawn or not record.withdrawn
            ]
            
            records_to_write.sort(key=lambda r: (r.date, r.object_number))
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['date', 'title', 'object_number', 'link', 
                            'withdrawn', 'correction_note']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                
                writer.writeheader()
                for record in records_to_write:
                    writer.writerow(record.to_dict())
            
            logger.info(f"Wrote {len(records_to_write)} records to {output_file}")
        
        except Exception as e:
            logger.error(f"Error writing output: {e}")
    
    def save_checksums(self):
        """Save checksums for future verification."""
        file_hash = ChecksumManager.compute_file_hash(self.input_file)
        manifest_hash = ChecksumManager.compute_manifest_hash(self.records)
        
        self.checksum_store.save(self.records, file_hash, manifest_hash)
    
    def write_integrity_report(self, report_file: Path):
        """Write integrity check results."""
        if not self.integrity_issues:
            logger.info("No integrity issues to report")
            return
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("INTEGRITY VERIFICATION REPORT\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Algorithm: {ChecksumManager.HASH_ALGORITHM}\n\n")
                
                f.write(f"Issues found: {len(self.integrity_issues)}\n\n")
                
                for object_num, is_valid, message in self.integrity_issues:
                    f.write(f"Object {object_num}:\n")
                    f.write(f"  Status: {'VALID' if is_valid else 'INVALID'}\n")
                    f.write(f"  Details: {message}\n\n")
            
            logger.info(f"Integrity report written to {report_file}")
        
        except Exception as e:
            logger.error(f"Error writing integrity report: {e}")
    
    def generate_summary(self) -> dict:
        """Generate summary statistics."""
        total = len(self.records)
        withdrawn = sum(1 for r in self.records.values() if r.withdrawn)
        active = total - withdrawn
        corrected = len(self.corrections_log)
        
        return {
            'total_records': total,
            'active_records': active,
            'withdrawn_records': withdrawn,
            'corrections_applied': corrected,
            'validation_errors': len(self.validation_errors),
            'integrity_issues': len(self.integrity_issues)
        }


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records with checksum verification'
    )
    parser.add_argument(
        'input_file',
        type=Path,
        help='Input TSV file with inventory records'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=None,
        help='Output file (default: standardized_inventory.tsv)'
    )
    parser.add_argument(
        '--checksums',
        type=Path,
        help='Checksum storage file (default: <input>.checksums.json)'
    )
    parser.add_argument(
        '-c', '--corrections',
        type=Path,
        help='TSV file with corrections to apply'
    )
    parser.add_argument(
        '--include-withdrawn',
        action='store_true',
        help='Include withdrawn records in output'
    )
    parser.add_argument(
        '--skip-integrity-check',
        action='store_true',
        help='Skip integrity verification'
    )
    parser.add_argument(
        '--integrity-report',
        type=Path,
        help='Write integrity check results to this file'
    )
    parser.add_argument(
        '--validation-report',
        type=Path,
        help='Write validation errors to this file'
    )
    
    args = parser.parse_args()
    
    if args.output is None:
        args.output = args.input_file.parent / 'standardized_inventory.tsv'
    
    # Process inventory
    processor = InventoryProcessor(args.input_file, args.checksums)
    
    if not processor.read_inventory():
        sys.exit(1)
    
    # Verify integrity unless skipped
    if not args.skip_integrity_check:
        integrity_ok = processor.verify_integrity()
        if not integrity_ok:
            logger.warning("Integrity checks found issues (continuing with processing)")
    
    if args.corrections:
        processor.apply_corrections(args.corrections)
    
    processor.normalize_all()
    
    is_valid = processor.validate_all()
    
    processor.write_output(args.output, include_withdrawn=args.include_withdrawn)
    
    # Save checksums for future verification
    processor.save_checksums()
    
    if args.integrity_report:
        processor.write_integrity_report(args.integrity_report)
    
    # Print summary
    summary = processor.generate_summary()
    print("\n" + "=" * 50)
    print("STANDARDIZATION SUMMARY")
    print("=" * 50)
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print("=" * 50)
    
    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()
```

## Usage Examples

**First run (creates checksums):**
```bash
python standardize_inventory.py inventory.tsv -o standardized.tsv
```

**Subsequent runs (verifies integrity):**
```bash
python standardize_inventory.py inventory.tsv -o standardized.tsv
```

**With integrity report:**
```bash
python standardize_inventory.py inventory.tsv \
    -o standardized.tsv \
    --integrity-report integrity.txt
```

**Skip integrity check if needed:**
```bash
python standardize_inventory.py inventory.tsv --skip-integrity-check
```

## Checksum File Format

**inventory.checksums.json:**
```json
{
  "timestamp": "2024-01-20T15:30:45.123456",
  "hash_algorithm": "sha256",
  "manifest_hash": "a1b2c3d4e5f6...",
  "file_hash": "f6e5d4c3b2a1...",
  "records": [
    {
      "object_number": "2024.001.001",
      "record_hash": "abc123def456...",
      "file_hash": "f6e5d4c3b2a1...",
      "timestamp": "2024-01-20T15:30:45.123456",
      "hash_algorithm": "sha256"
    }
  ]
}
```

## Key Features

- ✅ **Record-level hashing**: Detects changes to individual objects
- ✅ **File integrity verification**: Detects unauthorized modifications to source file
- ✅ **Manifest hashing**: Detects additions/deletions from collection
- ✅ **Persistence**: Stores checksums for future verification
- ✅ **Detailed reporting**: Shows exactly which records changed
- ✅ **Flexible verification**: Can skip integrity checks when needed
- ✅ **Canonical hashing**: Normalizes data before hashing for consistency
- ✅ **Audit trail**: Records timestamp of each verification
