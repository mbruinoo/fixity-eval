# Museum Inventory Record Standardizer with Checksums

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records from a TSV file with checksum verification.

Handles deduplication, corrections, withdrawals, and format normalization.
Includes checksums to detect changes in source data.
"""

import csv
import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse


@dataclass
class ChecksumRecord:
    """Tracks checksums for integrity verification."""
    file_path: str
    file_hash: str  # Hash of entire file
    record_count: int
    timestamp: str
    records: Dict[str, str] = field(default_factory=dict)  # object_number -> record_hash
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'record_count': self.record_count,
            'timestamp': self.timestamp,
            'records': self.records
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ChecksumRecord':
        """Create from dictionary."""
        return cls(
            file_path=data['file_path'],
            file_hash=data['file_hash'],
            record_count=data['record_count'],
            timestamp=data['timestamp'],
            records=data.get('records', {})
        )


@dataclass
class InventoryRecord:
    """Represents a single museum object record."""
    date: str
    title: str
    object_number: str
    link: str
    
    def __post_init__(self):
        """Validate and normalize fields after initialization."""
        self.date = self._normalize_date(self.date)
        self.title = self._normalize_title(self.title)
        self.object_number = self._normalize_object_number(self.object_number)
        self.link = self._normalize_link(self.link)
    
    @staticmethod
    def _normalize_date(date_str: str) -> str:
        """Convert date to ISO 8601 format (YYYY-MM-DD)."""
        date_str = date_str.strip()
        if not date_str:
            return ""
        
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%B %d, %Y",
            "%b %d, %Y",
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        print(f"Warning: Could not parse date '{date_str}'", file=sys.stderr)
        return date_str
    
    @staticmethod
    def _normalize_title(title: str) -> str:
        """Normalize title formatting."""
        title = title.strip()
        title = " ".join(title.split())
        title = title.rstrip(".,;:")
        return title
    
    @staticmethod
    def _normalize_object_number(obj_num: str) -> str:
        """Normalize object number (usually uppercase, no extra spaces)."""
        obj_num = obj_num.strip().upper()
        obj_num = "-".join(part.strip() for part in obj_num.split("-"))
        return obj_num
    
    @staticmethod
    def _normalize_link(link: str) -> str:
        """Validate and normalize URL."""
        link = link.strip()
        if not link:
            return ""
        
        if link and not link.startswith(("http://", "https://")):
            link = "https://" + link
        
        try:
            result = urlparse(link)
            if not result.netloc:
                print(f"Warning: Invalid URL '{link}'", file=sys.stderr)
                return ""
        except Exception as e:
            print(f"Warning: Error parsing URL '{link}': {e}", file=sys.stderr)
            return ""
        
        return link
    
    def to_dict(self) -> Dict[str, str]:
        """Convert record to dictionary."""
        return {
            "date": self.date,
            "title": self.title,
            "object_number": self.object_number,
            "link": self.link,
        }
    
    def compute_hash(self) -> str:
        """Compute SHA256 hash of this record's canonical form."""
        # Use normalized, sorted representation for consistent hashing
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


class ChecksumManager:
    """Manages checksums for source and output files."""
    
    def __init__(self, checksum_dir: Optional[Path] = None):
        """
        Initialize checksum manager.
        
        Args:
            checksum_dir: Directory to store checksum records (defaults to .checksums)
        """
        self.checksum_dir = checksum_dir or Path('.checksums')
        self.checksum_dir.mkdir(exist_ok=True)
    
    @staticmethod
    def compute_file_hash(file_path: Path, algorithm: str = 'sha256') -> str:
        """
        Compute hash of entire file.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm ('sha256', 'md5', etc.)
        
        Returns:
            Hex digest of file hash
        """
        hasher = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files efficiently
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def create_checksum_record(self, file_path: Path, 
                               records: Dict[str, InventoryRecord]) -> ChecksumRecord:
        """
        Create a checksum record for a file.
        
        Args:
            file_path: Path to the file
            records: Dictionary of InventoryRecord objects
        
        Returns:
            ChecksumRecord with file and individual record hashes
        """
        file_hash = self.compute_file_hash(file_path)
        record_hashes = {
            obj_num: record.compute_hash()
            for obj_num, record in records.items()
        }
        
        checksum = ChecksumRecord(
            file_path=str(file_path),
            file_hash=file_hash,
            record_count=len(records),
            timestamp=datetime.now().isoformat(),
            records=record_hashes
        )
        
        return checksum
    
    def save_checksum(self, checksum: ChecksumRecord) -> Path:
        """
        Save checksum record to file.
        
        Args:
            checksum: ChecksumRecord to save
        
        Returns:
            Path where checksum was saved
        """
        file_name = Path(checksum.file_path).stem
        checksum_file = self.checksum_dir / f"{file_name}.checksum.json"
        
        with open(checksum_file, 'w', encoding='utf-8') as f:
            json.dump(checksum.to_dict(), f, indent=2)
        
        return checksum_file
    
    def load_checksum(self, file_path: Path) -> Optional[ChecksumRecord]:
        """
        Load previous checksum record for a file.
        
        Args:
            file_path: Original file path
        
        Returns:
            Previous ChecksumRecord if exists, None otherwise
        """
        checksum_file = self.checksum_dir / f"{file_path.stem}.checksum.json"
        
        if not checksum_file.exists():
            return None
        
        with open(checksum_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return ChecksumRecord.from_dict(data)
    
    def verify_file_integrity(self, file_path: Path, 
                              previous_checksum: Optional[ChecksumRecord]) -> Tuple[bool, str]:
        """
        Verify file hasn't changed since last run.
        
        Args:
            file_path: Path to file to verify
            previous_checksum: Previous ChecksumRecord
        
        Returns:
            Tuple of (is_valid, message)
        """
        if not previous_checksum:
            return True, "No previous checksum found (first run)"
        
        current_hash = self.compute_file_hash(file_path)
        
        if current_hash == previous_checksum.file_hash:
            return True, "File unchanged"
        else:
            return False, "File has changed since last run"
    
    def verify_record_integrity(self, record: InventoryRecord, 
                                previous_hash: str) -> Tuple[bool, str]:
        """
        Verify individual record hasn't changed.
        
        Args:
            record: InventoryRecord to verify
            previous_hash: Previous hash value
        
        Returns:
            Tuple of (is_valid, message)
        """
        current_hash = record.compute_hash()
        
        if current_hash == previous_hash:
            return True, "Record unchanged"
        else:
            return False, f"Record modified (was {previous_hash[:8]}..., now {current_hash[:8]}...)"


class InventoryStandardizer:
    """Standardizes and deduplicates museum inventory records with checksum verification."""
    
    def __init__(self, input_file: str, output_file: str, 
                 corrections_file: Optional[str] = None,
                 withdrawals_file: Optional[str] = None,
                 checksum_dir: Optional[str] = None,
                 verify_integrity: bool = True):
        """
        Initialize standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output standardized TSV file
            corrections_file: Optional path to TSV with corrected records
            withdrawals_file: Optional path to TSV with withdrawn object numbers
            checksum_dir: Optional directory for checksum files
            verify_integrity: Whether to verify source file hasn't changed
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.corrections_file = Path(corrections_file) if corrections_file else None
        self.withdrawals_file = Path(withdrawals_file) if withdrawals_file else None
        
        self.checksum_manager = ChecksumManager(
            Path(checksum_dir) if checksum_dir else None
        )
        self.verify_integrity = verify_integrity
        
        self.records: Dict[str, InventoryRecord] = {}
        self.withdrawn: set = set()
        self.integrity_issues: List[str] = []
    
    def verify_source_files(self) -> None:
        """Verify source files haven't changed since last run."""
        if not self.verify_integrity:
            return
        
        for file_path in [self.input_file, self.corrections_file, self.withdrawals_file]:
            if not file_path or not file_path.exists():
                continue
            
            previous = self.checksum_manager.load_checksum(file_path)
            is_valid, message = self.checksum_manager.verify_file_integrity(
                file_path, previous
            )
            
            if not is_valid:
                self.integrity_issues.append(f"{file_path}: {message}")
                print(f"Warning: {file_path}: {message}", file=sys.stderr)
    
    def load_records(self) -> None:
        """Load records from input TSV file."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            required_fields = {'date', 'title', 'object_number', 'link'}
            if not reader.fieldnames or not required_fields.issubset(set(reader.fieldnames)):
                raise ValueError(f"Input file must have headers: {required_fields}")
            
            previous_checksum = self.checksum_manager.load_checksum(self.input_file)
            
            for row in reader:
                try:
                    record = InventoryRecord(
                        date=row.get('date', ''),
                        title=row.get('title', ''),
                        object_number=row.get('object_number', ''),
                        link=row.get('link', '')
                    )
                    
                    if not record.object_number:
                        print("Warning: Skipping record with empty object_number", 
                              file=sys.stderr)
                        continue
                    
                    # Check if record was modified
                    if previous_checksum and record.object_number in previous_checksum.records:
                        is_valid, message = self.checksum_manager.verify_record_integrity(
                            record, previous_checksum.records[record.object_number]
                        )
                        if not is_valid:
                            print(f"Info: {record.object_number}: {message}", file=sys.stderr)
                    
                    if record.object_number in self.records:
                        existing = self.records[record.object_number]
                        if record.date and (not existing.date or record.date > existing.date):
                            self.records[record.object_number] = record
                    else:
                        self.records[record.object_number] = record
                
                except Exception as e:
                    print(f"Warning: Error processing record: {e}", file=sys.stderr)
        
        # Save checksum of input file
        input_checksum = self.checksum_manager.create_checksum_record(
            self.input_file, self.records
        )
        self.checksum_manager.save_checksum(input_checksum)
        
        print(f"Loaded {len(self.records)} unique records", file=sys.stderr)
    
    def apply_corrections(self) -> None:
        """Apply corrections from corrections file."""
        if not self.corrections_file or not self.corrections_file.exists():
            return
        
        corrected_count = 0
        with open(self.corrections_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            for row in reader:
                try:
                    record = InventoryRecord(
                        date=row.get('date', ''),
                        title=row.get('title', ''),
                        object_number=row.get('object_number', ''),
                        link=row.get('link', '')
                    )
                    
                    if record.object_number in self.records:
                        self.records[record.object_number] = record
                        corrected_count += 1
                    else:
                        print(f"Warning: Correction references unknown object: "
                              f"{record.object_number}", file=sys.stderr)
                
                except Exception as e:
                    print(f"Warning: Error processing correction: {e}", file=sys.stderr)
        
        # Save checksum of corrections file
        if self.records:
            corrections_checksum = self.checksum_manager.create_checksum_record(
                self.corrections_file, self.records
            )
            self.checksum_manager.save_checksum(corrections_checksum)
        
        print(f"Applied {corrected_count} corrections", file=sys.stderr)
    
    def apply_withdrawals(self) -> None:
        """Remove records marked as withdrawn."""
        if not self.withdrawals_file or not self.withdrawals_file.exists():
            return
        
        withdrawn_count = 0
        withdrawn_records = {}
        
        with open(self.withdrawals_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            for row in reader:
                obj_num = row.get('object_number', '').strip().upper()
                if obj_num in self.records:
                    withdrawn_records[obj_num] = self.records[obj_num]
                    del self.records[obj_num]
                    self.withdrawn.add(obj_num)
                    withdrawn_count += 1
                else:
                    print(f"Warning: Withdrawal references unknown object: {obj_num}", 
                          file=sys.stderr)
        
        # Save checksum of withdrawals file
        if withdrawn_records:
            withdrawals_checksum = self.checksum_manager.create_checksum_record(
                self.withdrawals_file, withdrawn_records
            )
            self.checksum_manager.save_checksum(withdrawals_checksum)
        
        print(f"Withdrawn {withdrawn_count} records", file=sys.stderr)
    
    def save_records(self) -> None:
        """Save standardized records to output TSV file."""
        fieldnames = ['date', 'title', 'object_number', 'link']
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            
            for obj_num in sorted(self.records.keys()):
                record = self.records[obj_num]
                writer.writerow(record.to_dict())
        
        # Save checksum of output file
        output_checksum = self.checksum_manager.create_checksum_record(
            self.output_file, self.records
        )
        self.checksum_manager.save_checksum(output_checksum)
        
        print(f"Saved {len(self.records)} standardized records to {self.output_file}", 
              file=sys.stderr)
    
    def generate_report(self) -> None:
        """Generate a summary report with checksum information."""
        report_file = self.output_file.with_suffix('.report.txt')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("Museum Inventory Standardization Report\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")
            
            f.write("File Statistics:\n")
            f.write(f"  Total records processed: {len(self.records)}\n")
            f.write(f"  Total withdrawals: {len(self.withdrawn)}\n")
            f.write(f"  Output file: {self.output_file}\n\n")
            
            # Checksum information
            f.write("Checksum Information:\n")
            f.write(f"  Checksum directory: {self.checksum_manager.checksum_dir}\n")
            f.write(f"  Input file hash: {self.checksum_manager.compute_file_hash(self.input_file)}\n")
            f.write(f"  Output file hash: {self.checksum_manager.compute_file_hash(self.output_file)}\n\n")
            
            # Data quality issues
            missing_date = sum(1 for r in self.records.values() if not r.date)
            missing_link = sum(1 for r in self.records.values() if not r.link)
            
            f.write("Data Quality Issues:\n")
            f.write(f"  Records missing date: {missing_date}\n")
            f.write(f"  Records missing link: {missing_link}\n\n")
            
            # Integrity issues
            if self.integrity_issues:
                f.write("Integrity Issues Detected:\n")
                for issue in self.integrity_issues:
                    f.write(f"  - {issue}\n")
            else:
                f.write("Integrity Issues: None\n")
        
        print(f"Report saved to {report_file}", file=sys.stderr)
    
    def run(self) -> None:
        """Execute the standardization pipeline."""
        self.verify_source_files()
        self.load_records()
        self.apply_corrections()
        self.apply_withdrawals()
        self.save_records()
        self.generate_report()


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python script.py <input.tsv> <output.tsv> "
              "[--corrections corrections.tsv] [--withdrawals withdrawals.tsv] "
              "[--checksum-dir .checksums] [--skip-verify]", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    corrections_file = None
    withdrawals_file = None
    checksum_dir = None
    verify_integrity = True
    
    # Parse optional arguments
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--corrections' and i + 1 < len(sys.argv):
            corrections_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--withdrawals' and i + 1 < len(sys.argv):
            withdrawals_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--checksum-dir' and i + 1 < len(sys.argv):
            checksum_dir = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--skip-verify':
            verify_integrity = False
            i += 1
        else:
            i += 1
    
    standardizer = InventoryStandardizer(
        input_file=input_file,
        output_file=output_file,
        corrections_file=corrections_file,
        withdrawals_file=withdrawals_file,
        checksum_dir=checksum_dir,
        verify_integrity=verify_integrity
    )
    
    standardizer.run()


if __name__ == "__main__":
    main()
```

## Usage Examples

**Basic usage with integrity checking:**
```bash
python script.py inventory.tsv standardized_inventory.tsv
```

**With all options:**
```bash
python script.py inventory.tsv standardized_inventory.tsv \
  --corrections corrections.tsv \
  --withdrawals withdrawals.tsv \
  --checksum-dir .checksums
```

**Skip integrity verification:**
```bash
python script.py inventory.tsv standardized_inventory.tsv --skip-verify
```

## Checksum Features

### What Gets Checksummed:
1. **File-level checksums** (SHA256 hash of entire file)
2. **Record-level checksums** (individual record hashes)
3. **Timestamps** for when checksums were created

### How It Works:

1. **First Run**: Creates `.checksums/inventory.checksum.json` with baseline hashes
2. **Subsequent Runs**: 
   - Compares current file hash against previous
   - Alerts if source files changed
   - Shows individual record modifications
3. **Output Verification**: Checksums output file to detect corruption

### Checksum File Format:

```json
{
  "file_path": "inventory.tsv",
  "file_hash": "a1b2c3d4e5f6...",
  "record_count": 2543,
  "timestamp": "2024-01-15T10:30:45.123456",
  "records": {
    "OBJ-2024-001": "f1a2b3c4d5e6...",
    "OBJ-2024-002": "g6h7i8j9k0l1..."
  }
}
```

### Benefits:

✅ **Audit trail** of source file changes  
✅ **Data integrity** verification  
✅ **Change detection** at record level  
✅ **Reproducibility** tracking  
✅ **Accidental modification** alerts
