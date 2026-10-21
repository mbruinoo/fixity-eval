# Museum Inventory Standardization with Checksums

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records with checksum verification.

Detects if source data has been modified since last standardization.
"""

import argparse
import csv
import sys
import hashlib
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Set, Tuple, Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ChecksumData:
    """Stores checksum information for verification."""
    file_hash: str  # Hash of entire file
    record_hashes: Dict[str, str] = field(default_factory=dict)  # object_number -> hash
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    algorithm: str = "sha256"
    file_size: int = 0
    record_count: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict) -> 'ChecksumData':
        """Create from dictionary."""
        return ChecksumData(**data)


@dataclass
class InventoryRecord:
    """Represents a standardized inventory record."""
    object_number: str
    title: str
    date: str
    link: str
    record_date: str
    status: str = "active"
    notes: str = ""
    source_hash: str = ""  # Hash of the original source row
    
    def is_valid(self) -> Tuple[bool, str]:
        """Validate record fields."""
        if not self.object_number or not self.object_number.strip():
            return False, "Missing object number"
        if not self.title or not self.title.strip():
            return False, "Missing title"
        if not self.date or not self.date.strip():
            return False, "Missing date"
        if not self.link or not self.link.strip():
            return False, "Missing link"
        return True, ""
    
    def normalize(self) -> None:
        """Standardize field formats."""
        self.object_number = self.object_number.strip().upper()
        self.title = self.title.strip()
        self.date = self.date.strip()
        self.link = self.link.strip()
        self.status = self.status.strip().lower()
        self.notes = self.notes.strip()


class ChecksumManager:
    """Manages checksum calculation and verification."""
    
    ALGORITHM = "sha256"
    
    @staticmethod
    def calculate_file_hash(file_path: Path, algorithm: str = ALGORITHM) -> str:
        """
        Calculate hash of entire file.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm to use
            
        Returns:
            Hex digest of file hash
        """
        hash_obj = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return ""
    
    @staticmethod
    def calculate_record_hash(row_data: Dict[str, str], 
                             algorithm: str = ALGORITHM) -> str:
        """
        Calculate hash of a single record (normalized).
        
        Normalizes order and whitespace for consistent hashing.
        
        Args:
            row_data: Dictionary of record fields
            algorithm: Hash algorithm to use
            
        Returns:
            Hex digest of record hash
        """
        # Normalize and sort fields for consistent hashing
        normalized = {}
        for key in sorted(row_data.keys()):
            normalized[key] = row_data[key].strip() if isinstance(row_data[key], str) else str(row_data[key])
        
        # Create string representation
        record_str = json.dumps(normalized, sort_keys=True, separators=(',', ':'))
        
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(record_str.encode('utf-8'))
        return hash_obj.hexdigest()
    
    @staticmethod
    def verify_file_integrity(file_path: Path, 
                             expected_hash: str,
                             algorithm: str = ALGORITHM) -> Tuple[bool, str]:
        """
        Verify that a file hasn't been modified.
        
        Args:
            file_path: Path to file to verify
            expected_hash: Previously calculated hash
            algorithm: Hash algorithm used
            
        Returns:
            Tuple of (is_valid, message)
        """
        calculated_hash = ChecksumManager.calculate_file_hash(file_path, algorithm)
        
        if calculated_hash == expected_hash:
            return True, f"File integrity verified ({algorithm})"
        else:
            return False, (f"File has been modified!\n"
                         f"Expected: {expected_hash}\n"
                         f"Calculated: {calculated_hash}")


class InventoryStandardizer:
    """Handles standardization with checksum verification."""
    
    def __init__(self, input_file: Path, checksum_dir: Path = None):
        self.input_file = input_file
        self.checksum_dir = checksum_dir or input_file.parent
        self.checksum_file = self.checksum_dir / f"{input_file.stem}.checksums.json"
        
        self.records: List[InventoryRecord] = []
        self.errors: List[Dict] = []
        self.withdrawals: Set[str] = set()
        self.record_history: Dict[str, List[InventoryRecord]] = {}
        
        self.current_checksums: ChecksumData = None
        self.previous_checksums: Optional[ChecksumData] = None
        self.checksum_changes: Dict[str, Dict] = {}  # Track what changed
        
    def load_previous_checksums(self) -> bool:
        """
        Load previously stored checksums.
        
        Returns:
            True if checksums exist and are loaded
        """
        if not self.checksum_file.exists():
            logger.info(f"No previous checksums found at {self.checksum_file}")
            return False
        
        try:
            with open(self.checksum_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.previous_checksums = ChecksumData.from_dict(data)
                logger.info(f"Loaded previous checksums from {self.checksum_file}")
                return True
        except Exception as e:
            logger.error(f"Error loading checksums: {e}")
            return False
    
    def verify_source_integrity(self) -> Tuple[bool, str]:
        """
        Verify source file hasn't been modified since last standardization.
        
        Returns:
            Tuple of (is_valid, message)
        """
        if self.previous_checksums is None:
            return True, "No previous checksums to compare against (first run)"
        
        is_valid, message = ChecksumManager.verify_file_integrity(
            self.input_file,
            self.previous_checksums.file_hash,
            self.previous_checksums.algorithm
        )
        
        return is_valid, message
    
    def load_tsv(self) -> bool:
        """Load records from TSV file and calculate checksums."""
        if not self.input_file.exists():
            logger.error(f"File not found: {self.input_file}")
            return False
        
        try:
            file_hash = ChecksumManager.calculate_file_hash(self.input_file)
            file_size = self.input_file.stat().st_size
            
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if reader.fieldnames is None:
                    logger.error("Empty TSV file")
                    return False
                
                required_fields = {'object_number', 'title', 'date', 'link'}
                if not required_fields.issubset(set(reader.fieldnames or [])):
                    logger.error(f"Missing required fields. Expected: {required_fields}")
                    return False
                
                record_hashes = {}
                
                for row_num, row in enumerate(reader, start=2):
                    # Calculate hash of source row
                    source_hash = ChecksumManager.calculate_record_hash(row)
                    
                    record = InventoryRecord(
                        object_number=row.get('object_number', ''),
                        title=row.get('title', ''),
                        date=row.get('date', ''),
                        link=row.get('link', ''),
                        record_date=row.get('record_date', datetime.now().isoformat()),
                        status=row.get('status', 'active'),
                        notes=row.get('notes', ''),
                        source_hash=source_hash
                    )
                    
                    is_valid, error_msg = record.is_valid()
                    if not is_valid:
                        self.errors.append({
                            'row': row_num,
                            'object_number': record.object_number,
                            'error': error_msg
                        })
                        logger.warning(f"Row {row_num}: {error_msg}")
                        continue
                    
                    record.normalize()
                    self.records.append(record)
                    record_hashes[record.object_number] = source_hash
                    
                    if record.object_number not in self.record_history:
                        self.record_history[record.object_number] = []
                    self.record_history[record.object_number].append(record)
                
                # Store checksums
                self.current_checksums = ChecksumData(
                    file_hash=file_hash,
                    record_hashes=record_hashes,
                    file_size=file_size,
                    record_count=len(self.records)
                )
            
            logger.info(f"Loaded {len(self.records)} valid records")
            logger.info(f"File hash: {file_hash[:16]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error reading TSV file: {e}")
            return False
    
    def detect_record_changes(self) -> Dict[str, Dict]:
        """
        Compare current records with previous checksums.
        
        Returns:
            Dictionary of changes by object_number
        """
        changes = {}
        
        if self.previous_checksums is None:
            return changes
        
        # Records that have changed
        for obj_num, current_hash in self.current_checksums.record_hashes.items():
            previous_hash = self.previous_checksums.record_hashes.get(obj_num)
            
            if previous_hash is None:
                changes[obj_num] = {
                    'type': 'added',
                    'previous_hash': None,
                    'current_hash': current_hash
                }
            elif previous_hash != current_hash:
                changes[obj_num] = {
                    'type': 'modified',
                    'previous_hash': previous_hash,
                    'current_hash': current_hash
                }
        
        # Records that were removed
        for obj_num, previous_hash in self.previous_checksums.record_hashes.items():
            if obj_num not in self.current_checksums.record_hashes:
                changes[obj_num] = {
                    'type': 'removed',
                    'previous_hash': previous_hash,
                    'current_hash': None
                }
        
        self.checksum_changes = changes
        return changes
    
    def handle_duplicates(self, keep_latest: bool = True) -> int:
        """Handle duplicate object numbers."""
        duplicates_removed = 0
        seen: Dict[str, int] = {}
        records_to_keep = []
        
        sorted_records = sorted(self.records, key=lambda r: r.record_date)
        
        for record in sorted_records:
            if record.object_number in seen:
                if keep_latest:
                    old_idx = seen[record.object_number]
                    if records_to_keep[old_idx].status != 'withdrawn':
                        records_to_keep[old_idx].status = 'superseded'
                        logger.info(f"Marked {record.object_number} as superseded")
                    duplicates_removed += 1
                else:
                    logger.error(f"Duplicate object number: {record.object_number}")
                    self.errors.append({
                        'object_number': record.object_number,
                        'error': 'Duplicate entry'
                    })
            
            seen[record.object_number] = len(records_to_keep)
            records_to_keep.append(record)
        
        self.records = records_to_keep
        return duplicates_removed
    
    def process_withdrawals(self, withdrawals_file: Path = None) -> int:
        """Process withdrawn records."""
        count = 0
        
        if withdrawals_file and withdrawals_file.exists():
            try:
                with open(withdrawals_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        obj_num = line.strip().upper()
                        if obj_num and not obj_num.startswith('#'):
                            self.withdrawals.add(obj_num)
                logger.info(f"Loaded {len(self.withdrawals)} withdrawal entries")
            except Exception as e:
                logger.error(f"Error reading withdrawals file: {e}")
        
        for record in self.records:
            if record.object_number in self.withdrawals:
                record.status = 'withdrawn'
                count += 1
        
        return count
    
    def save_checksums(self) -> bool:
        """Save checksums to file."""
        try:
            with open(self.checksum_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_checksums.to_dict(), f, indent=2)
            logger.info(f"Saved checksums to {self.checksum_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving checksums: {e}")
            return False
    
    def generate_report(self, output_dir: Path = None) -> Dict:
        """Generate detailed standardization report."""
        if output_dir is None:
            output_dir = Path('.')
        
        active_records = [r for r in self.records if r.status == 'active']
        withdrawn_records = [r for r in self.records if r.status == 'withdrawn']
        superseded_records = [r for r in self.records if r.status == 'superseded']
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'input_file': str(self.input_file),
            'checksums': {
                'algorithm': self.current_checksums.algorithm,
                'file_hash': self.current_checksums.file_hash,
                'file_size': self.current_checksums.file_size,
                'record_count': self.current_checksums.record_count,
            },
            'summary': {
                'total_records': len(self.records),
                'active_records': len(active_records),
                'withdrawn_records': len(withdrawn_records),
                'superseded_records': len(superseded_records),
                'invalid_records': len(self.errors),
            },
            'changes': {
                'total_changes': len(self.checksum_changes),
                'added': len([c for c in self.checksum_changes.values() 
                            if c['type'] == 'added']),
                'modified': len([c for c in self.checksum_changes.values() 
                               if c['type'] == 'modified']),
                'removed': len([c for c in self.checksum_changes.values() 
                              if c['type'] == 'removed']),
                'details': self.checksum_changes,
            },
            'errors': self.errors,
        }
        
        report_file = output_dir / 'inventory_report.json'
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {report_file}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
        
        return report
    
    def save_standardized(self, output_file: Path = None) -> bool:
        """Save standardized records to TSV file."""
        if output_file is None:
            output_file = self.input_file.parent / f"{self.input_file.stem}.standardized.tsv"
        
        try:
            valid_records = [r for r in self.records]
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['object_number', 'title', 'date', 'link', 
                            'record_date', 'status', 'notes', 'source_hash']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                
                writer.writeheader()
                for record in valid_records:
                    writer.writerow(asdict(record))
            
            logger.info(f"Saved {len(valid_records)} standardized records to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving standardized records: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records with integrity verification'
    )
    parser.add_argument('input_file', type=Path, help='Input TSV file')
    parser.add_argument('-o', '--output', type=Path, help='Output TSV file')
    parser.add_argument('-w', '--withdrawals', type=Path, 
                       help='File listing withdrawn object numbers')
    parser.add_argument('-d', '--output-dir', type=Path, default=Path('.'),
                       help='Directory for reports')
    parser.add_argument('-c', '--checksum-dir', type=Path,
                       help='Directory for checksum files (default: input directory)')
    parser.add_argument('--skip-integrity-check', action='store_true',
                       help='Skip file integrity verification')
    parser.add_argument('--force', action='store_true',
                       help='Proceed even if integrity check fails')
    
    args = parser.parse_args()
    
    # Initialize standardizer
    standardizer = InventoryStandardizer(args.input_file, args.checksum_dir)
    
    # Load previous checksums
    standardizer.load_previous_checksums()
    
    # Verify source integrity (unless skipped)
    if not args.skip_integrity_check:
        is_valid, message = standardizer.verify_source_integrity()
        print(f"\n{'='*60}")
        print("SOURCE INTEGRITY CHECK")
        print(f"{'='*60}")
        print(message)
        print(f"{'='*60}\n")
        
        if not is_valid and not args.force:
            logger.error("Source file integrity check failed. Use --force to override.")
            sys.exit(1)
    
    # Load and process records
    if not standardizer.load_tsv():
        sys.exit(1)
    
    # Detect changes from previous run
    changes = standardizer.detect_record_changes()
    if changes:
        print(f"\n{'='*60}")
        print("DETECTED CHANGES")
        print(f"{'='*60}")
        for obj_num, change_info in list(changes.items())[:10]:  # Show first 10
            print(f"{obj_num}: {change_info['type'].upper()}")
        if len(changes) > 10:
            print(f"... and {len(changes) - 10} more changes")
        print(f"{'='*60}\n")
    
    # Handle duplicates
    standardizer.handle_duplicates(keep_latest=True)
    
    # Process withdrawals
    if args.withdrawals:
        standardizer.process_withdrawals(args.withdrawals)
    
    # Generate report
    report = standardizer.generate_report(args.output_dir)
    print(f"\n{'='*60}")
    print("STANDARDIZATION SUMMARY")
    print(f"{'='*60}")
    print(f"File Hash: {report['checksums']['file_hash'][:16]}...")
    for key, value in report['summary'].items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    if report['changes']['total_changes'] > 0:
        print(f"\nChanges Detected:")
        for key, value in report['changes'].items():
            if key != 'details':
                print(f"  {key.replace('_', ' ').title()}: {value}")
    print(f"{'='*60}\n")
    
    # Save standardized records
    if not standardizer.save_standardized(args.output):
        sys.exit(1)
    
    # Save checksums for future verification
    if not standardizer.save_checksums():
        sys.exit(1)
    
    logger.info("Standardization complete")


if __name__ == '__main__':
    main()
```

## Checksum Files

### Generated `inventory.checksums.json`:
```json
{
  "file_hash": "a7f3c8e9d2b1f4a6c9e2d3b5f7a8c1e4d6f9a2b3c5d8e1f4a7b9c2d5e8f1",
  "record_hashes": {
    "ART-001": "e4d5f8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c",
    "ART-002": "f5e6a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d",
    "ART-003": "g6f7a0c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e"
  },
  "timestamp": "2024-01-16T10:30:45.123456",
  "algorithm": "sha256",
  "file_size": 1024,
  "record_count": 3
}
```

## Usage Examples

```bash
# First run - creates checksums
python3 standardize_inventory.py inventory.tsv

# Second run - verifies integrity, detects changes
python3 standardize_inventory.py inventory.tsv

# If source file was modified unexpectedly
python3 standardize_inventory.py inventory.tsv --force

# Skip integrity check
python3 standardize_inventory.py inventory.tsv --skip-integrity-check

# Custom checksum directory
python3 standardize_inventory.py inventory.tsv -c /data/checksums
```

## Key Features

✅ **File-level checksums** — Detects any modification to source file  
✅ **Record-level checksums** — Tracks individual record changes  
✅ **Change detection** — Reports added, modified, removed records  
✅ **Integrity verification** — Warns if source has been modified  
✅ **Persistent storage** — Checksums saved for future verification  
✅ **Detailed reporting** — JSON report with checksum information  
✅ **Force mode** — Override integrity checks when needed  
✅ **SHA256 algorithm** — Cryptographically secure hashing
