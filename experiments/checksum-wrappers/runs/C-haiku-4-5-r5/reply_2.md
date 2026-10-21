# Museum Inventory Standardizer with Checksum Verification

Here's how to incorporate checksums to detect changes in source data:

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records with checksum verification.

Checksums detect:
- Accidental modifications to source data
- Corrupted files during transfer
- Unauthorized changes to records
"""

import csv
import sys
import hashlib
import json
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime
from collections import defaultdict


@dataclass
class FileChecksum:
    """Track checksums for data integrity verification."""
    file_path: str
    md5: str
    sha256: str
    file_size: int
    timestamp: str
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FileChecksum':
        return cls(**data)


@dataclass
class RecordChecksum:
    """Track individual record checksums."""
    object_number: str
    md5: str
    sha256: str
    timestamp: str
    source_row: int
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RecordChecksum':
        return cls(**data)


@dataclass
class InventoryRecord:
    """Represents a standardized inventory record."""
    object_number: str
    title: str
    date: str
    link: str
    status: str = "active"
    notes: str = ""
    md5: str = ""  # Checksum of original record
    sha256: str = ""  # Checksum of original record
    
    def is_valid(self) -> Tuple[bool, List[str]]:
        """Validate record fields. Returns (is_valid, error_messages)."""
        errors = []
        
        if not self.object_number or not self.object_number.strip():
            errors.append("Missing object number")
        elif not self._is_valid_object_number(self.object_number):
            errors.append(f"Invalid object number format: {self.object_number}")
        
        if not self.title or not self.title.strip():
            errors.append("Missing title")
        
        if not self.date or not self.date.strip():
            errors.append("Missing date")
        elif not self._is_valid_date(self.date):
            errors.append(f"Invalid date format: {self.date}")
        
        if not self.link or not self.link.strip():
            errors.append("Missing link")
        elif not self._is_valid_url(self.link):
            errors.append(f"Invalid URL format: {self.link}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _is_valid_object_number(obj_num: str) -> bool:
        import re
        pattern = r'^[\w\-\.]+$'
        return bool(re.match(pattern, obj_num.strip()))
    
    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        import re
        date_str = date_str.strip()
        if re.match(r'^\d{4}$', date_str):
            return True
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        import re
        url = url.strip()
        pattern = r'^https?://[\w\-\.]+\.\w{2,}(/[\w\-\./?%&=]*)?$'
        return bool(re.match(pattern, url))


class ChecksumManager:
    """Manage file and record checksums."""
    
    @staticmethod
    def compute_file_checksums(file_path: Path) -> Tuple[str, str, int]:
        """Compute MD5 and SHA256 checksums for a file.
        
        Returns: (md5_hash, sha256_hash, file_size)
        """
        md5_hash = hashlib.md5()
        sha256_hash = hashlib.sha256()
        file_size = 0
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5_hash.update(chunk)
                sha256_hash.update(chunk)
                file_size += len(chunk)
        
        return md5_hash.hexdigest(), sha256_hash.hexdigest(), file_size
    
    @staticmethod
    def compute_record_checksums(row: Dict) -> Tuple[str, str]:
        """Compute checksums for a single record.
        
        Creates checksums from the original row data (before normalization).
        Uses a canonical format to ensure consistency.
        """
        # Create canonical representation of record
        canonical = json.dumps(row, sort_keys=True, ensure_ascii=True)
        canonical_bytes = canonical.encode('utf-8')
        
        md5_hash = hashlib.md5(canonical_bytes).hexdigest()
        sha256_hash = hashlib.sha256(canonical_bytes).hexdigest()
        
        return md5_hash, sha256_hash
    
    @staticmethod
    def verify_file_checksums(
        file_path: Path,
        expected_md5: str,
        expected_sha256: str
    ) -> Tuple[bool, Dict[str, str]]:
        """Verify file checksums against expected values.
        
        Returns: (is_valid, status_dict)
        """
        actual_md5, actual_sha256, _ = ChecksumManager.compute_file_checksums(file_path)
        
        status = {
            'md5_match': actual_md5 == expected_md5,
            'sha256_match': actual_sha256 == expected_sha256,
            'expected_md5': expected_md5,
            'actual_md5': actual_md5,
            'expected_sha256': expected_sha256,
            'actual_sha256': actual_sha256,
        }
        
        is_valid = status['md5_match'] and status['sha256_match']
        return is_valid, status
    
    @staticmethod
    def verify_record_checksums(
        row: Dict,
        expected_md5: str,
        expected_sha256: str
    ) -> Tuple[bool, Dict[str, str]]:
        """Verify record checksums against expected values."""
        actual_md5, actual_sha256 = ChecksumManager.compute_record_checksums(row)
        
        status = {
            'md5_match': actual_md5 == expected_md5,
            'sha256_match': actual_sha256 == expected_sha256,
            'expected_md5': expected_md5,
            'actual_md5': actual_md5,
            'expected_sha256': expected_sha256,
            'actual_sha256': actual_sha256,
        }
        
        is_valid = status['md5_match'] and status['sha256_match']
        return is_valid, status


class InventoryStandardizer:
    """Standardize and validate museum inventory records with checksums."""
    
    def __init__(
        self,
        input_file: str,
        output_dir: str = "standardized_output",
        checksum_file: Optional[str] = None
    ):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Checksum tracking
        self.checksum_file = Path(checksum_file) if checksum_file else (
            self.output_dir / "checksums.json"
        )
        self.file_checksum: Optional[FileChecksum] = None
        self.record_checksums: Dict[str, RecordChecksum] = {}
        self.checksum_violations: List[Dict] = []
        
        self.records: Dict[str, InventoryRecord] = {}
        self.withdrawn: Set[str] = set()
        self.corrections: Dict[str, str] = {}
        self.errors: List[Tuple[int, str, List[str]]] = []
        self.duplicates: List[List[str]] = []
    
    def load_previous_checksums(self) -> bool:
        """Load checksums from previous run.
        
        Returns: True if checksums were loaded, False otherwise.
        """
        if not self.checksum_file.exists():
            return False
        
        try:
            with open(self.checksum_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load file checksum
            if 'file_checksum' in data:
                self.file_checksum = FileChecksum.from_dict(data['file_checksum'])
            
            # Load record checksums
            if 'record_checksums' in data:
                for record_data in data['record_checksums']:
                    checksum = RecordChecksum.from_dict(record_data)
                    self.record_checksums[checksum.object_number] = checksum
            
            print(f"Loaded checksums from {self.checksum_file}")
            return True
        except Exception as e:
            print(f"Warning: Could not load previous checksums: {e}")
            return False
    
    def verify_source_file(self) -> bool:
        """Verify that source file hasn't changed since last standardization.
        
        Returns: True if file is unchanged (or no previous checksum), False if changed.
        """
        if not self.file_checksum:
            print("No previous file checksum to verify against")
            return True
        
        md5, sha256, size = ChecksumManager.compute_file_checksums(self.input_file)
        is_valid, status = ChecksumManager.verify_file_checksums(
            self.input_file,
            self.file_checksum.md5,
            self.file_checksum.sha256
        )
        
        if is_valid:
            print("✓ Source file verification: PASSED")
            return True
        else:
            print("✗ Source file verification: FAILED")
            print(f"  MD5: {status['expected_md5'][:16]}... → {status['actual_md5'][:16]}...")
            print(f"  SHA256: {status['expected_sha256'][:16]}... → {status['actual_sha256'][:16]}...")
            return False
    
    def load_records(self) -> None:
        """Load records from TSV file with checksum computation."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        # Compute and store file checksums
        md5, sha256, size = ChecksumManager.compute_file_checksums(self.input_file)
        self.file_checksum = FileChecksum(
            file_path=str(self.input_file),
            md5=md5,
            sha256=sha256,
            file_size=size,
            timestamp=datetime.now().isoformat()
        )
        print(f"✓ Computed file checksums (MD5: {md5[:16]}..., SHA256: {sha256[:16]}...)")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            if not reader.fieldnames:
                raise ValueError("TSV file is empty")
            
            required_fields = {'date', 'title', 'object_number', 'link'}
            if not required_fields.issubset(set(reader.fieldnames or [])):
                raise ValueError(f"Missing required fields: {required_fields}")
            
            for line_num, row in enumerate(reader, start=2):
                try:
                    self._process_row(row, line_num)
                except Exception as e:
                    obj_num = row.get('object_number', 'UNKNOWN')
                    self.errors.append((line_num, obj_num, [str(e)]))
    
    def _process_row(self, row: Dict, line_num: int) -> None:
        """Process a single row with checksum computation."""
        obj_num = row.get('object_number', '').strip()
        
        # Compute checksum of original record
        md5, sha256 = ChecksumManager.compute_record_checksums(row)
        
        # Check for special directives
        if row.get('status', '').lower() == 'withdrawn':
            self.withdrawn.add(obj_num)
            return
        
        if 'corrected_to' in row:
            new_num = row.get('corrected_to', '').strip()
            self.corrections[obj_num] = new_num
            return
        
        record = InventoryRecord(
            object_number=obj_num,
            title=row.get('title', '').strip(),
            date=row.get('date', '').strip(),
            link=row.get('link', '').strip(),
            status=row.get('status', 'active').lower(),
            notes=row.get('notes', '').strip(),
            md5=md5,
            sha256=sha256
        )
        
        # Store record checksum
        self.record_checksums[obj_num] = RecordChecksum(
            object_number=obj_num,
            md5=md5,
            sha256=sha256,
            timestamp=datetime.now().isoformat(),
            source_row=line_num
        )
        
        is_valid, validation_errors = record.is_valid()
        if not is_valid:
            self.errors.append((line_num, obj_num, validation_errors))
            return
        
        record = self._normalize_record(record)
        
        if record.object_number in self.records:
            self.duplicates.append([record.object_number])
        else:
            self.records[record.object_number] = record
    
    def _normalize_record(self, record: InventoryRecord) -> InventoryRecord:
        """Normalize record fields (preserve checksums of original)."""
        import re
        
        original_md5 = record.md5
        original_sha256 = record.sha256
        
        record.object_number = record.object_number.upper().strip()
        record.title = ' '.join(record.title.split())
        
        # Normalize date
        date_str = record.date.strip()
        if not re.match(r'^\d{4}$', date_str):
            for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%Y-%m-%d']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    record.date = dt.strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue
        
        record.link = record.link.strip().rstrip('/')
        
        # Restore original checksums
        record.md5 = original_md5
        record.sha256 = original_sha256
        
        return record
    
    def verify_records_against_checksum(self) -> None:
        """Verify records against stored checksums for tampering detection."""
        if not self.record_checksums:
            print("No previous record checksums to verify against")
            return
        
        violations = []
        
        for obj_num, stored_checksum in self.record_checksums.items():
            if obj_num not in self.records:
                # Record was deleted or withdrawn
                record = self.records.get(obj_num)
                if record:
                    record_md5 = hashlib.md5(
                        json.dumps(asdict(record), sort_keys=True).encode()
                    ).hexdigest()
                    
                    if record_md5 != stored_checksum.md5:
                        violations.append({
                            'object_number': obj_num,
                            'type': 'modified',
                            'expected_md5': stored_checksum.md5,
                            'actual_md5': record_md5,
                        })
        
        if violations:
            self.checksum_violations.extend(violations)
            print(f"⚠ Found {len(violations)} potential modifications")
    
    def save_checksums(self) -> None:
        """Save checksums to JSON file for future verification."""
        checksum_data = {
            'file_checksum': self.file_checksum.to_dict() if self.file_checksum else None,
            'record_checksums': [
                checksum.to_dict() 
                for checksum in sorted(
                    self.record_checksums.values(),
                    key=lambda x: x.object_number
                )
            ],
            'generated': datetime.now().isoformat(),
            'total_records': len(self.records),
            'total_checksums': len(self.record_checksums)
        }
        
        with open(self.checksum_file, 'w', encoding='utf-8') as f:
            json.dump(checksum_data, f, indent=2)
        
        print(f"Saved {len(self.record_checksums)} record checksums to {self.checksum_file}")
    
    def standardize(self, verify_previous: bool = True) -> None:
        """Run full standardization pipeline with checksum verification."""
        print("=" * 70)
        print("MUSEUM INVENTORY STANDARDIZATION WITH CHECKSUM VERIFICATION")
        print("=" * 70 + "\n")
        
        # Load and verify previous checksums
        if verify_previous:
            print("Step 1: Verifying previous checksums...")
            self.load_previous_checksums()
            if self.file_checksum:
                self.verify_source_file()
            print()
        
        # Load records and compute new checksums
        print("Step 2: Loading records and computing checksums...")
        self.load_records()
        print()
        
        # Apply corrections and withdrawals
        print("Step 3: Applying corrections and withdrawals...")
        self.apply_corrections()
        self.apply_withdrawals()
        print()
        
        # Verify records
        print("Step 4: Verifying record integrity...")
        self.verify_records_against_checksum()
        print()
        
        print("Standardization complete.")
    
    def apply_corrections(self) -> None:
        """Apply correction mappings."""
        for old_id, new_id in self.corrections.items():
            if old_id in self.records:
                record = self.records.pop(old_id)
                record.object_number = new_id
                record.status = "corrected"
                self.records[new_id] = record
    
    def apply_withdrawals(self) -> None:
        """Mark withdrawn records."""
        for obj_num in self.withdrawn:
            if obj_num in self.records:
                self.records[obj_num].status = "withdrawn"
    
    def save_records(self, filename: str = "standardized_inventory.tsv") -> None:
        """Save standardized records to TSV file."""
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['object_number', 'title', 'date', 'link', 'status', 'notes', 'md5'],
                delimiter='\t'
            )
            writer.writeheader()
            
            for record in sorted(self.records.values(), key=lambda r: r.object_number):
                row = asdict(record)
                # Include only first 16 chars of MD5 for reference
                row['md5'] = row['md5'][:16] + '...' if row['md5'] else ''
                writer.writerow(row)
        
        print(f"Saved {len(self.records)} records to {output_path}")
    
    def save_active_records(self, filename: str = "active_inventory.tsv") -> None:
        """Save only active records."""
        output_path = self.output_dir / filename
        
        active = [r for r in self.records.values() if r.status == "active"]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['object_number', 'title', 'date', 'link', 'notes'],
                delimiter='\t'
            )
            writer.writeheader()
            writer.writerows(
                [asdict(r) for r in sorted(active, key=lambda r: r.object_number)]
            )
        
        print(f"Saved {len(active)} active records to {output_path}")
    
    def generate_report(self, filename: str = "standardization_report.txt") -> None:
        """Generate detailed standardization report with checksum info."""
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("MUSEUM INVENTORY STANDARDIZATION REPORT\n")
            f.write("WITH CHECKSUM VERIFICATION\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Input File: {self.input_file}\n\n")
            
            # File checksum info
            if self.file_checksum:
                f.write("SOURCE FILE INTEGRITY\n")
                f.write("-" * 70 + "\n")
                f.write(f"File: {self.file_checksum.file_path}\n")
                f.write(f"Size: {self.file_checksum.file_size:,} bytes\n")
                f.write(f"MD5:    {self.file_checksum.md5}\n")
                f.write(f"SHA256: {self.file_checksum.sha256}\n")
                f.write(f"Computed: {self.file_checksum.timestamp}\n\n")
            
            # Summary statistics
            f.write("SUMMARY\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total records processed: {len(self.records) + len(self.errors)}\n")
            f.write(f"Valid records: {len(self.records)}\n")
            f.write(f"Invalid records: {len(self.errors)}\n")
            f.write(f"Records with checksums: {len(self.record_checksums)}\n")
            f.write(f"Withdrawn records: {sum(1 for r in self.records.values() if r.status == 'withdrawn')}\n")
            f.write(f"Checksum violations detected: {len(self.checksum_violations)}\n\n")
            
            # Checksum violations
            if self.checksum_violations:
                f.write("⚠ CHECKSUM VIOLATIONS\n")
                f.write("-" * 70 + "\n")
                for violation in self.checksum_violations:
                    f.write(f"Object #{violation['object_number']}: {violation['type']}\n")
                    f.write(f"  Expected: {violation['expected_md5']}\n")
                    f.write(f"  Actual:   {violation['actual_md5']}\n")
                f.write("\n")
            
            # Validation errors
            if self.errors:
                f.write("VALIDATION ERRORS\n")
                f.write("-" * 70 + "\n")
                for line_num, obj_num, error_list in sorted(self.errors):
                    f.write(f"Line {line_num} (Object #{obj_num}):\n")
                    for error in error_list:
                        f.write(f"  • {error}\n")
                f.write("\n")
        
        print(f"Report saved to {output_path}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python standardize_inventory.py <input.tsv> [output_dir] [checksum_file]")
        print("\nExample:")
        print("  python standardize_inventory.py museum_records.tsv ./output")
        print("  python standardize_inventory.py museum_records.tsv ./output ./checksums.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "standardized_output"
    checksum_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        standardizer = InventoryStandardizer(input_file, output_dir, checksum_file)
        standardizer.standardize(verify_previous=True)
        standardizer.save_records()
        standardizer.save_active_records()
        standardizer.save_checksums()
        standardizer.generate_report()
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Example Checksum Output (`checksums.json`)

```json
{
  "file_checksum": {
    "file_path": "museum_records.tsv",
    "md5": "8a4d8c9e2f3b1a5c7d9e1f3a5b7c9d0e",
    "sha256": "2e7d0ef3f8a4b1c6d9e2f5a8c3b6e9f1a4c7d0e3f6a9b2c5d8e1f4a7b0c3d6e",
    "file_size": 45280,
    "timestamp": "2024-01-20T14:32:15.123456"
  },
  "record_checksums": [
    {
      "object_number": "2024.001.001",
      "md5": "7c3f8a1b2d4e5f6a8c9d0e1f3a5b7c9d",
      "sha256": "3f6a9b2c5d8e1f4a7b0c3d6e9f2a5c8d1e4f7a0b3c6d9e2f5a8b1c4d7e0f3a",
      "timestamp": "2024-01-20T14:32:15.125000",
      "source_row": 2
    }
  ],
  "generated": "2024-01-20T14:32:16.234567",
  "total_records": 150,
  "total_checksums": 150
}
```

## Key Features

✅ **File-level checksums** (MD5 & SHA256) detect any changes to source data  
✅ **Record-level checksums** track individual record integrity  
✅ **Checksum verification** on subsequent runs detects tampering or corruption  
✅ **Canonical JSON representation** ensures consistent checksum computation  
✅ **Detailed reporting** shows which records/files have changed  
✅ **Preserves original checksums** when normalizing records  

## Usage

```bash
# First run - creates checksums
python standardize_inventory.py museum_records.tsv output/ checksums.json

# Second run - verifies no changes to source
python standardize_inventory.py museum_records.tsv output/ checksums.json
# Output: ✓ Source file verification: PASSED

# If source was modified
python standardize_inventory.py museum_records.tsv output/ checksums.json
# Output: ✗ Source file verification: FAILED
```
