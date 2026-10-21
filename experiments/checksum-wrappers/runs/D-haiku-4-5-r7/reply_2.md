# Museum Inventory Standardizer with Checksum Verification

Here's the enhanced script with checksums for data integrity verification:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksum Verification

Standardizes and validates museum inventory TSV files with checksums
to detect source data changes.
"""

import argparse
import csv
import sys
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, asdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ChecksumRecord:
    """Stores checksum information for verification."""
    file_path: str
    file_size: int
    file_mtime: float
    file_hash: str  # SHA-256 of entire file
    row_count: int
    header_hash: str  # SHA-256 of header
    row_hashes: Dict[int, str] = field(default_factory=dict)  # row_num -> hash
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ChecksumRecord':
        """Create from dictionary."""
        return cls(**data)


class ChecksumManager:
    """Manages checksums for source data integrity verification."""
    
    HASH_ALGORITHM = hashlib.sha256
    
    @staticmethod
    def compute_file_hash(filepath: Path) -> str:
        """Compute SHA-256 hash of entire file."""
        hash_obj = ChecksumManager.HASH_ALGORITHM()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Error computing file hash: {e}")
            raise
    
    @staticmethod
    def compute_row_hash(row: Dict[str, str]) -> str:
        """Compute SHA-256 hash of a row's data."""
        # Sort keys for consistent hashing
        row_str = json.dumps(row, sort_keys=True, separators=(',', ':'))
        return ChecksumManager.HASH_ALGORITHM(
            row_str.encode('utf-8')
        ).hexdigest()
    
    @staticmethod
    def compute_header_hash(fieldnames: List[str]) -> str:
        """Compute hash of header fields."""
        header_str = json.dumps(sorted(fieldnames), separators=(',', ':'))
        return ChecksumManager.HASH_ALGORITHM(
            header_str.encode('utf-8')
        ).hexdigest()
    
    @staticmethod
    def generate_checksums(filepath: Path) -> ChecksumRecord:
        """Generate complete checksums for a TSV file."""
        logger.info(f"Generating checksums for: {filepath}")
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # File-level checksums
        file_stat = filepath.stat()
        file_hash = ChecksumManager.compute_file_hash(filepath)
        
        record = ChecksumRecord(
            file_path=str(filepath.absolute()),
            file_size=file_stat.st_size,
            file_mtime=file_stat.st_mtime,
            file_hash=file_hash,
            row_count=0,
            header_hash=""
        )
        
        # Row-level checksums
        row_hashes = {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if reader.fieldnames:
                    record.header_hash = ChecksumManager.compute_header_hash(
                        list(reader.fieldnames)
                    )
                
                for row_num, row in enumerate(reader, start=2):
                    row_hash = ChecksumManager.compute_row_hash(row)
                    row_hashes[row_num] = row_hash
                    record.row_count += 1
        
        except Exception as e:
            logger.error(f"Error reading file for checksums: {e}")
            raise
        
        record.row_hashes = row_hashes
        logger.info(
            f"Generated checksums: {record.row_count} rows, "
            f"file hash: {file_hash[:16]}..."
        )
        return record
    
    @staticmethod
    def verify_file_integrity(filepath: Path, 
                             checksum_record: ChecksumRecord) -> Tuple[bool, List[str]]:
        """
        Verify that file hasn't changed using stored checksums.
        Returns (is_valid, list_of_discrepancies).
        """
        issues = []
        
        if not filepath.exists():
            issues.append(f"File no longer exists: {filepath}")
            return False, issues
        
        # Check file size
        file_stat = filepath.stat()
        if file_stat.st_size != checksum_record.file_size:
            issues.append(
                f"File size changed: {checksum_record.file_size} → {file_stat.st_size}"
            )
        
        # Check file hash
        current_hash = ChecksumManager.compute_file_hash(filepath)
        if current_hash != checksum_record.file_hash:
            issues.append(
                f"File content changed: {checksum_record.file_hash[:16]}... "
                f"→ {current_hash[:16]}..."
            )
            
            # Detailed row-by-row comparison
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter='\t')
                    
                    for row_num, row in enumerate(reader, start=2):
                        if row_num in checksum_record.row_hashes:
                            current_row_hash = ChecksumManager.compute_row_hash(row)
                            stored_row_hash = checksum_record.row_hashes[row_num]
                            
                            if current_row_hash != stored_row_hash:
                                issues.append(
                                    f"Row {row_num} changed: "
                                    f"'{row.get('object number', 'N/A')}'"
                                )
                        else:
                            issues.append(f"New row {row_num}: '{row.get('object number', 'N/A')}'")
                
                # Check for deleted rows
                for stored_row_num in checksum_record.row_hashes:
                    if stored_row_num > row_num:
                        issues.append(
                            f"Row {stored_row_num} deleted"
                        )
            
            except Exception as e:
                logger.error(f"Error during row-by-row verification: {e}")
        
        return len(issues) == 0, issues


@dataclass
class InventoryEntry:
    """Represents a single inventory entry."""
    date: str
    title: str
    object_number: str
    link: str
    row_number: int = 0
    status: str = "active"
    correction_row: int = 0
    source_hash: str = ""  # Hash of original row from source
    
    def is_valid(self) -> Tuple[bool, List[str]]:
        """Validate the entry."""
        errors = []
        
        if not self._validate_date():
            errors.append(f"Invalid date format: '{self.date}'")
        
        if not self.title.strip():
            errors.append("Title cannot be empty")
        if not self.object_number.strip():
            errors.append("Object number cannot be empty")
        
        if self.link.strip() and not self._validate_url():
            errors.append(f"Invalid URL format: '{self.link}'")
        
        return len(errors) == 0, errors
    
    def _validate_date(self) -> bool:
        """Validate date is in ISO format."""
        try:
            datetime.strptime(self.date.strip(), "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def _validate_url(self) -> bool:
        """Basic URL validation."""
        link = self.link.strip()
        return link.startswith(('http://', 'https://', 'ftp://')) or link == ""
    
    def standardize(self) -> None:
        """Standardize field values."""
        try:
            date_obj = datetime.strptime(self.date.strip(), "%Y-%m-%d")
            self.date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            for fmt in ["%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]:
                try:
                    date_obj = datetime.strptime(self.date.strip(), fmt)
                    self.date = date_obj.strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
        
        self.title = ' '.join(self.title.split())
        self.object_number = self.object_number.strip().upper()
        self.link = self.link.strip().lower()


@dataclass
class InventoryDatabase:
    """Manages the complete inventory with checksums."""
    entries: List[InventoryEntry] = field(default_factory=list)
    object_number_map: Dict[str, List[int]] = field(default_factory=dict)
    source_checksum: Optional[ChecksumRecord] = None
    processing_checksum: Optional[ChecksumRecord] = None
    
    def add_entry(self, entry: InventoryEntry) -> None:
        """Add entry and track by object number."""
        idx = len(self.entries)
        self.entries.append(entry)
        
        if entry.object_number not in self.object_number_map:
            self.object_number_map[entry.object_number] = []
        self.object_number_map[entry.object_number].append(idx)
    
    def process_corrections(self) -> Tuple[int, int]:
        """Process corrections and withdrawals."""
        corrections = 0
        withdrawals = 0
        
        for obj_num, indices in self.object_number_map.items():
            if len(indices) > 1:
                sorted_indices = sorted(indices, 
                    key=lambda i: self.entries[i].row_number)
                
                for i in sorted_indices[:-1]:
                    self.entries[i].status = "corrected"
                    self.entries[i].correction_row = sorted_indices[-1]
                    corrections += 1
                    logger.info(
                        f"Object '{obj_num}' corrected: "
                        f"row {self.entries[i].row_number} → "
                        f"row {self.entries[sorted_indices[-1]].row_number}"
                    )
        
        for entry in self.entries:
            if entry.title.lower() in ["withdrawn", "deleted", "cancelled"]:
                entry.status = "withdrawn"
                withdrawals += 1
                logger.info(
                    f"Object '{entry.object_number}' withdrawn at row {entry.row_number}"
                )
        
        return corrections, withdrawals
    
    def get_active_entries(self) -> List[InventoryEntry]:
        """Return only active entries."""
        return [e for e in self.entries if e.status == "active"]
    
    def get_report(self) -> str:
        """Generate processing report."""
        total = len(self.entries)
        active = len(self.get_active_entries())
        corrected = sum(1 for e in self.entries if e.status == "corrected")
        withdrawn = sum(1 for e in self.entries if e.status == "withdrawn")
        
        report = f"""
=== Inventory Processing Report ===
Total entries processed: {total}
Active entries: {active}
Corrected entries: {corrected}
Withdrawn entries: {withdrawn}
"""
        
        if self.source_checksum:
            report += f"\n=== Source Data Verification ===\n"
            report += f"Source file: {self.source_checksum.file_path}\n"
            report += f"File size: {self.source_checksum.file_size} bytes\n"
            report += f"File hash: {self.source_checksum.file_hash}\n"
            report += f"Header hash: {self.source_checksum.header_hash}\n"
            report += f"Total rows: {self.source_checksum.row_count}\n"
            report += f"Verified: {datetime.fromisoformat(self.source_checksum.timestamp)}\n"
        
        return report


def read_inventory(filepath: Path, 
                  verify_against: Optional[ChecksumRecord] = None) -> InventoryDatabase:
    """Read TSV file, optionally verifying against stored checksums."""
    db = InventoryDatabase()
    
    # Generate checksums for current file
    source_checksum = ChecksumManager.generate_checksums(filepath)
    db.source_checksum = source_checksum
    
    # Verify against stored checksums if provided
    if verify_against:
        logger.info("Verifying file integrity against stored checksums...")
        is_valid, issues = ChecksumManager.verify_file_integrity(
            filepath, 
            verify_against
        )
        
        if not is_valid:
            logger.warning("=" * 60)
            logger.warning("DATA INTEGRITY ISSUES DETECTED:")
            for issue in issues:
                logger.warning(f"  • {issue}")
            logger.warning("=" * 60)
        else:
            logger.info("✓ File integrity verified - no changes detected")
    
    # Read and parse file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            if not reader.fieldnames:
                raise ValueError("Empty file or invalid format")
            
            required_fields = {'date', 'title', 'object number', 'link'}
            if not required_fields.issubset(set(reader.fieldnames)):
                raise ValueError(
                    f"Missing required columns. Expected: {required_fields}\n"
                    f"Got: {set(reader.fieldnames)}"
                )
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Store hash of original row
                    row_hash = ChecksumManager.compute_row_hash(row)
                    
                    entry = InventoryEntry(
                        date=row['date'],
                        title=row['title'],
                        object_number=row['object number'],
                        link=row['link'],
                        row_number=row_num,
                        source_hash=row_hash
                    )
                    entry.standardize()
                    
                    is_valid, errors = entry.is_valid()
                    if not is_valid:
                        logger.warning(
                            f"Row {row_num}: Invalid entry for '{entry.object_number}'\n"
                            f"  {'; '.join(errors)}"
                        )
                    
                    db.add_entry(entry)
                
                except KeyError as e:
                    logger.error(f"Row {row_num}: Missing field {e}")
                except Exception as e:
                    logger.error(f"Row {row_num}: {e}")
    
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        sys.exit(1)
    
    return db


def write_inventory(db: InventoryDatabase, output_path: Path, 
                   include_all: bool = False) -> None:
    """Write standardized inventory to TSV file."""
    entries = db.entries if include_all else db.get_active_entries()
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['date', 'title', 'object number', 'link']
            if include_all:
                fieldnames.extend(['status', 'row_number'])
            
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            
            for entry in entries:
                row = {
                    'date': entry.date,
                    'title': entry.title,
                    'object number': entry.object_number,
                    'link': entry.link,
                }
                if include_all:
                    row['status'] = entry.status
                    row['row_number'] = entry.row_number
                
                writer.writerow(row)
        
        logger.info(f"Standardized inventory written to: {output_path}")
    
    except Exception as e:
        logger.error(f"Error writing output file: {e}")
        sys.exit(1)


def save_checksums(checksum_record: ChecksumRecord, output_path: Path) -> None:
    """Save checksums to JSON file for future verification."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(checksum_record.to_dict(), f, indent=2)
        logger.info(f"Checksums saved to: {output_path}")
    except Exception as e:
        logger.error(f"Error saving checksums: {e}")
        sys.exit(1)


def load_checksums(checksum_path: Path) -> ChecksumRecord:
    """Load checksums from JSON file."""
    try:
        with open(checksum_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Checksums loaded from: {checksum_path}")
        return ChecksumRecord.from_dict(data)
    except FileNotFoundError:
        logger.error(f"Checksum file not found: {checksum_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading checksums: {e}")
        sys.exit(1)


def write_audit_log(db: InventoryDatabase, output_path: Path) -> None:
    """Write detailed audit log including source hashes."""
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['row_number', 'object_number', 'title', 'status', 
                         'correction_row', 'date', 'link', 'source_hash']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            
            for entry in db.entries:
                writer.writerow({
                    'row_number': entry.row_number,
                    'object_number': entry.object_number,
                    'title': entry.title,
                    'status': entry.status,
                    'correction_row': entry.correction_row if entry.correction_row else '',
                    'date': entry.date,
                    'link': entry.link,
                    'source_hash': entry.source_hash,
                })
        
        logger.info(f"Audit log written to: {output_path}")
    
    except Exception as e:
        logger.error(f"Error writing audit log: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory TSV files with checksum verification'
    )
    parser.add_argument(
        'input_file',
        type=Path,
        help='Input TSV file'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=None,
        help='Output TSV file (default: input_standardized.tsv)'
    )
    parser.add_argument(
        '-a', '--audit-log',
        type=Path,
        default=None,
        help='Write detailed audit log'
    )
    parser.add_argument(
        '-c', '--checksums',
        type=Path,
        default=None,
        help='Save checksums to JSON file for future verification'
    )
    parser.add_argument(
        '-v', '--verify',
        type=Path,
        default=None,
        help='Verify against previously saved checksums'
    )
    parser.add_argument(
        '--include-all',
        action='store_true',
        help='Include corrected and withdrawn entries in output'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Set default output path
    if args.output is None:
        args.output = args.input_file.parent / (
            args.input_file.stem + '_standardized.tsv'
        )
    
    # Set default checksum path if saving
    if args.checksums is None and (args.checksums or not args.verify):
        args.checksums = args.input_file.parent / (
            args.input_file.stem + '_checksums.json'
        )
    
    logger.info(f"Reading inventory from: {args.input_file}")
    
    # Load previous checksums if verifying
    verify_against = None
    if args.verify:
        verify_against = load_checksums(args.verify)
    
    db = read_inventory(args.input_file, verify_against=verify_against)
    
    logger.info("Processing corrections and withdrawals...")
    corrections, withdrawals = db.process_corrections()
    
    logger.info(f"Found {corrections} corrections and {withdrawals} withdrawals")
    
    logger.info("Writing standardized inventory...")
    write_inventory(db, args.output, include_all=args.include_all)
    
    if args.checksums:
        save_checksums(db.source_checksum, args.checksums)
    
    if args.audit_log:
        write_audit_log(db, args.audit_log)
    
    print(db.get_report())


if __name__ == '__main__':
    main()
```

## Usage Examples

### 1. Initial Processing (Generate Checksums)

```bash
# Generate checksums and save them
python inventory_standardizer.py inventory.tsv \
    --checksums inventory_checksums.json \
    --audit-log audit.tsv
```

### 2. Verify File Hasn't Changed

```bash
# On subsequent runs, verify against stored checksums
python inventory_standardizer.py inventory.tsv \
    --verify inventory_checksums.json \
    --checksums inventory_checksums.json
```

### 3. Complete Workflow

```bash
# Initial run with all outputs
python inventory_standardizer.py source_data.tsv \
    -o clean_inventory.tsv \
    --checksums checksums.json \
    --audit-log audit.tsv \
    --verbose

# Later verification
python inventory_standardizer.py source_data.tsv \
    -o clean_inventory.tsv \
    --verify checksums.json \
    --checksums checksums.json
```

## Checksum JSON Output Example

```json
{
  "file_path": "/path/to/inventory.tsv",
  "file_size": 2048,
  "file_mtime": 1704067200.0,
  "file_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "row_count": 150,
  "header_hash": "f7e8d9c0b1a2345678901234567890ab",
  "row_hashes": {
    "2": "1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6",
    "3": "2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7",
    ...
  },
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

## Key Features Added

✅ **File-Level Checksums**
- SHA-256 hash of entire file
- File size tracking
- Modification time tracking

✅ **Row-Level Checksums**
- Individual hash for each row
- Detects specific row changes
- Identifies new/deleted rows

✅ **Header Validation**
- Separate header hash
- Column order verification

✅ **Integrity Verification**
- Compare current file against stored checksums
- Detailed change reporting
- Tracks source data provenance

✅ **Audit Trail**
- Row hashes stored in audit log
- Complete change history
- Source data preservation

This approach ensures you can:
1. **Detect changes** to the source data over time
2. **Identify exactly which rows changed**
3. **Maintain data provenance** for compliance
4. **Prevent accidental reprocessing** of modified data
