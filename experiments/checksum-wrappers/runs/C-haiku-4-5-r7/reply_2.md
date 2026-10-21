# Museum Inventory Standardization Script with Checksums

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records from a TSV file with checksum verification.

Records can be corrected or withdrawn later. Checksums verify source data integrity.
"""

import argparse
import csv
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from datetime import datetime


@dataclass
class ChecksumRecord:
    """Stores checksums for verification."""
    file_path: str
    file_hash: str  # SHA-256 of entire file
    record_count: int
    timestamp: str
    record_hashes: dict[str, str] = field(default_factory=dict)  # object_number -> row hash

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'record_count': self.record_count,
            'timestamp': self.timestamp,
            'record_hashes': self.record_hashes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ChecksumRecord':
        """Create from dictionary."""
        return cls(
            file_path=data['file_path'],
            file_hash=data['file_hash'],
            record_count=data['record_count'],
            timestamp=data['timestamp'],
            record_hashes=data.get('record_hashes', {}),
        )


@dataclass
class InventoryRecord:
    """Represents a standardized museum inventory record."""
    date: str
    title: str
    object_number: str
    link: str
    status: str = "active"  # active, corrected, withdrawn
    amendments: list = field(default_factory=list)
    original_hash: Optional[str] = None  # Hash of original row

    def __post_init__(self):
        """Validate and standardize fields."""
        self.date = self._standardize_date(self.date)
        self.title = self._standardize_title(self.title)
        self.object_number = self._standardize_object_number(self.object_number)
        self.link = self._standardize_link(self.link)

    @staticmethod
    def _standardize_date(date_str: str) -> str:
        """
        Standardize date to YYYY-MM-DD format.
        
        Accepts: YYYY-MM-DD, MM/DD/YYYY, DD.MM.YYYY, etc.
        """
        date_str = date_str.strip()
        
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d.%m.%Y",
            "%m-%d-%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        raise ValueError(f"Could not parse date: {date_str}")

    @staticmethod
    def _standardize_title(title: str) -> str:
        """
        Standardize title formatting.
        
        - Strip whitespace
        - Remove extra spaces
        - Proper capitalization
        """
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)  # Collapse multiple spaces
        title = title.title()
        return title

    @staticmethod
    def _standardize_object_number(obj_num: str) -> str:
        """
        Standardize object number.
        
        Format: YYYY.NNN or similar patterns depending on institution.
        Remove spaces and ensure consistent formatting.
        """
        obj_num = obj_num.strip().upper()
        obj_num = re.sub(r'[\s]+', '', obj_num)
        return obj_num

    @staticmethod
    def _standardize_link(link: str) -> str:
        """
        Standardize URL.
        
        - Strip whitespace
        - Ensure proper scheme
        - Remove trailing slashes
        """
        link = link.strip()
        
        if not link:
            return ""
        
        if not re.match(r'^https?://', link):
            link = 'https://' + link
        
        link = link.rstrip('/')
        
        return link

    def apply_amendment(self, amendment: 'Amendment') -> None:
        """Apply an amendment (correction or withdrawal) to this record."""
        self.amendments.append(amendment)
        
        if amendment.amendment_type == "withdrawal":
            self.status = "withdrawn"
        elif amendment.amendment_type == "correction":
            self.status = "corrected"
            if amendment.field == "title":
                self.title = InventoryRecord._standardize_title(amendment.new_value)
            elif amendment.field == "link":
                self.link = InventoryRecord._standardize_link(amendment.new_value)
            elif amendment.field == "object_number":
                self.object_number = InventoryRecord._standardize_object_number(amendment.new_value)
            elif amendment.field == "date":
                self.date = InventoryRecord._standardize_date(amendment.new_value)

    def to_dict(self) -> dict:
        """Convert to dictionary for output."""
        return {
            'date': self.date,
            'title': self.title,
            'object_number': self.object_number,
            'link': self.link,
            'status': self.status,
        }


@dataclass
class Amendment:
    """Represents a correction or withdrawal amendment."""
    date: str
    object_number: str
    amendment_type: str  # "correction" or "withdrawal"
    field: Optional[str] = None
    new_value: Optional[str] = None

    def __post_init__(self):
        """Validate amendment."""
        self.date = InventoryRecord._standardize_date(self.date)
        self.object_number = InventoryRecord._standardize_object_number(self.object_number)
        self.amendment_type = self.amendment_type.lower()
        
        if self.amendment_type not in ["correction", "withdrawal"]:
            raise ValueError(f"Invalid amendment type: {self.amendment_type}")
        
        if self.amendment_type == "correction" and (not self.field or not self.new_value):
            raise ValueError("Corrections must specify field and new_value")


class ChecksumManager:
    """Manage file and record checksums."""

    @staticmethod
    def compute_file_hash(file_path: Path, algorithm: str = 'sha256') -> str:
        """Compute hash of entire file."""
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()

    @staticmethod
    def compute_row_hash(row: dict, algorithm: str = 'sha256') -> str:
        """
        Compute hash of a record row.
        
        Uses JSON serialization for consistent ordering.
        """
        # Sort keys for consistent hashing
        row_json = json.dumps(row, sort_keys=True, separators=(',', ':'))
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(row_json.encode('utf-8'))
        return hash_obj.hexdigest()

    @staticmethod
    def save_checksums(checksum_record: ChecksumRecord, output_path: Path) -> None:
        """Save checksums to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(checksum_record.to_dict(), f, indent=2)
        print(f"Saved checksums to {output_path}")

    @staticmethod
    def load_checksums(input_path: Path) -> ChecksumRecord:
        """Load checksums from JSON file."""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return ChecksumRecord.from_dict(data)


class InventoryStandardizer:
    """Standardize museum inventory records with checksum verification."""

    def __init__(
        self,
        input_file: Path,
        amendments_file: Optional[Path] = None,
        verify_checksum: Optional[Path] = None,
        save_checksum: Optional[Path] = None,
    ):
        self.input_file = input_file
        self.amendments_file = amendments_file
        self.verify_checksum_file = verify_checksum
        self.save_checksum_file = save_checksum
        self.records: dict[str, InventoryRecord] = {}
        self.amendments: list[Amendment] = []
        self.checksum_manager = ChecksumManager()
        self.current_checksums: Optional[ChecksumRecord] = None
        self.previous_checksums: Optional[ChecksumRecord] = None

    def verify_file_integrity(self) -> bool:
        """
        Verify file hasn't changed using stored checksums.
        
        Returns True if verification passes or no checksum file exists.
        Returns False if verification fails.
        """
        if not self.verify_checksum_file:
            return True
        
        if not self.verify_checksum_file.exists():
            print(f"Note: Checksum file not found: {self.verify_checksum_file}")
            return True
        
        print(f"Verifying file integrity against {self.verify_checksum_file}...")
        
        try:
            self.previous_checksums = self.checksum_manager.load_checksums(
                self.verify_checksum_file
            )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error: Invalid checksum file: {e}", file=sys.stderr)
            return False
        
        # Verify file hash
        current_file_hash = self.checksum_manager.compute_file_hash(self.input_file)
        
        if current_file_hash != self.previous_checksums.file_hash:
            print(
                f"✗ File integrity check FAILED",
                file=sys.stderr
            )
            print(
                f"  Expected hash: {self.previous_checksums.file_hash}",
                file=sys.stderr
            )
            print(
                f"  Actual hash:   {current_file_hash}",
                file=sys.stderr
            )
            return False
        
        print(f"✓ File integrity verified (SHA-256: {current_file_hash[:16]}...)")
        return True

    def load_records(self) -> None:
        """Load inventory records from TSV file, computing checksums."""
        print(f"Loading records from {self.input_file}...")
        
        record_hashes = {}
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            if reader.fieldnames is None:
                raise ValueError("Empty file or missing header")
            
            required_fields = {'date', 'title', 'object_number', 'link'}
            if not required_fields.issubset(set(reader.fieldnames)):
                raise ValueError(
                    f"Missing required fields. Expected: {required_fields}"
                )
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Compute hash of original row
                    row_hash = self.checksum_manager.compute_row_hash(row)
                    
                    record = InventoryRecord(
                        date=row['date'],
                        title=row['title'],
                        object_number=row['object_number'],
                        link=row['link'],
                        original_hash=row_hash,
                    )
                    
                    self.records[record.object_number] = record
                    record_hashes[record.object_number] = row_hash
                    
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping row {row_num}: {e}", file=sys.stderr)
        
        # Compute and store file hash
        file_hash = self.checksum_manager.compute_file_hash(self.input_file)
        self.current_checksums = ChecksumRecord(
            file_path=str(self.input_file.resolve()),
            file_hash=file_hash,
            record_count=len(self.records),
            timestamp=datetime.now().isoformat(),
            record_hashes=record_hashes,
        )
        
        print(f"Loaded {len(self.records)} records")
        print(f"File hash (SHA-256): {file_hash[:16]}...")

    def verify_record_checksums(self) -> tuple[int, int]:
        """
        Verify record checksums against previously stored values.
        
        Returns: (matching_count, mismatched_count)
        """
        if not self.previous_checksums:
            return 0, 0
        
        print("\nVerifying record checksums...")
        
        matching = 0
        mismatched = 0
        
        for obj_num, record in self.records.items():
            if obj_num not in self.previous_checksums.record_hashes:
                print(
                    f"Warning: New record (not in previous checksums): {obj_num}",
                    file=sys.stderr
                )
                continue
            
            previous_hash = self.previous_checksums.record_hashes[obj_num]
            
            if record.original_hash == previous_hash:
                matching += 1
            else:
                print(
                    f"✗ Record checksum mismatch: {obj_num}",
                    file=sys.stderr
                )
                print(
                    f"  Expected: {previous_hash}",
                    file=sys.stderr
                )
                print(
                    f"  Actual:   {record.original_hash}",
                    file=sys.stderr
                )
                mismatched += 1
        
        # Check for deleted records
        for obj_num in self.previous_checksums.record_hashes:
            if obj_num not in self.records:
                print(
                    f"Warning: Record removed: {obj_num}",
                    file=sys.stderr
                )
        
        if matching > 0:
            print(f"✓ {matching} records verified")
        if mismatched > 0:
            print(f"✗ {mismatched} records have mismatched checksums")
        
        return matching, mismatched

    def load_amendments(self) -> None:
        """Load amendments from TSV file."""
        if not self.amendments_file or not self.amendments_file.exists():
            print("No amendments file provided or found")
            return
        
        print(f"Loading amendments from {self.amendments_file}...")
        
        with open(self.amendments_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            required_fields = {'date', 'object_number', 'amendment_type'}
            if reader.fieldnames and not required_fields.issubset(set(reader.fieldnames)):
                raise ValueError(
                    f"Missing required fields in amendments. Expected: {required_fields}"
                )
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    amendment = Amendment(
                        date=row['date'],
                        object_number=row['object_number'],
                        amendment_type=row['amendment_type'],
                        field=row.get('field'),
                        new_value=row.get('new_value'),
                    )
                    self.amendments.append(amendment)
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping amendment row {row_num}: {e}", file=sys.stderr)
        
        print(f"Loaded {len(self.amendments)} amendments")

    def apply_amendments(self) -> None:
        """Apply amendments to matching records."""
        print("Applying amendments...")
        
        unmatched = 0
        for amendment in self.amendments:
            if amendment.object_number in self.records:
                self.records[amendment.object_number].apply_amendment(amendment)
            else:
                print(
                    f"Warning: Amendment references unknown object number: "
                    f"{amendment.object_number}",
                    file=sys.stderr
                )
                unmatched += 1
        
        if unmatched:
            print(f"Warning: {unmatched} amendments did not match any records", 
                  file=sys.stderr)

    def save_standardized(self, output_file: Path) -> None:
        """Save standardized records to TSV file."""
        print(f"Saving standardized records to {output_file}...")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['date', 'title', 'object_number', 'link', 'status']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            
            for record in sorted(self.records.values(), key=lambda r: r.object_number):
                writer.writerow(record.to_dict())
        
        print(f"Saved {len(self.records)} records")

    def save_checksums(self) -> None:
        """Save checksums for future verification."""
        if not self.save_checksum_file or not self.current_checksums:
            return
        
        self.checksum_manager.save_checksums(self.current_checksums, self.save_checksum_file)

    def generate_report(self) -> dict:
        """Generate standardization report."""
        total = len(self.records)
        active = sum(1 for r in self.records.values() if r.status == "active")
        corrected = sum(1 for r in self.records.values() if r.status == "corrected")
        withdrawn = sum(1 for r in self.records.values() if r.status == "withdrawn")
        
        return {
            'total_records': total,
            'active': active,
            'corrected': corrected,
            'withdrawn': withdrawn,
            'total_amendments': len(self.amendments),
        }

    def print_report(self) -> None:
        """Print standardization report."""
        report = self.generate_report()
        
        print("\n" + "="*50)
        print("STANDARDIZATION REPORT")
        print("="*50)
        print(f"Total Records:     {report['total_records']}")
        print(f"  Active:          {report['active']}")
        print(f"  Corrected:       {report['corrected']}")
        print(f"  Withdrawn:       {report['withdrawn']}")
        print(f"Total Amendments:  {report['total_amendments']}")
        print("="*50 + "\n")


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
        '-a', '--amendments',
        type=Path,
        help='TSV file with amendments (corrections and withdrawals)'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=Path('standardized_inventory.tsv'),
        help='Output TSV file (default: standardized_inventory.tsv)'
    )
    parser.add_argument(
        '-s', '--save-checksum',
        type=Path,
        help='Save checksums to JSON file for future verification'
    )
    parser.add_argument(
        '-v', '--verify-checksum',
        type=Path,
        help='Verify against previously saved checksums'
    )
    parser.add_argument(
        '-r', '--report',
        action='store_true',
        help='Print standardization report'
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not args.input_file.exists():
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    
    # Run standardization
    try:
        standardizer = InventoryStandardizer(
            args.input_file,
            args.amendments,
            verify_checksum=args.verify_checksum,
            save_checksum=args.save_checksum,
        )
        
        # Verify file integrity
        if not standardizer.verify_file_integrity():
            sys.exit(1)
        
        standardizer.load_records()
        
        # Verify record checksums if available
        if standardizer.previous_checksums:
            matching, mismatched = standardizer.verify_record_checksums()
            if mismatched > 0:
                print(f"\nWarning: {mismatched} records have changed", file=sys.stderr)
        
        standardizer.load_amendments()
        standardizer.apply_amendments()
        standardizer.save_standardized(args.output)
        standardizer.save_checksums()
        
        if args.report:
            standardizer.print_report()
        
        print("✓ Standardization complete")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## Usage Examples

### First run - save checksums:
```bash
python standardize_inventory.py inventory.tsv \
  -o output.tsv \
  -s checksums.json \
  -r
```

### Subsequent runs - verify checksums:
```bash
python standardize_inventory.py inventory.tsv \
  -o output.tsv \
  -v checksums.json \
  -a amendments.tsv \
  -r
```

### Full workflow:
```bash
# Initial standardization and checksum creation
python standardize_inventory.py inventory.tsv \
  -a amendments.tsv \
  -o standardized.tsv \
  -s checksums.json \
  -r

# Later verification
python standardize_inventory.py inventory.tsv \
  -a amendments_v2.tsv \
  -o standardized_v2.tsv \
  -v checksums.json
```

## Output Files

**checksums.json:**
```json
{
  "file_path": "/path/to/inventory.tsv",
  "file_hash": "a1b2c3d4e5f6...",
  "record_count": 1000,
  "timestamp": "2024-01-15T10:30:45.123456",
  "record_hashes": {
    "2024.001": "hash123...",
    "2024.002": "hash456...",
    "2024.003": "hash789..."
  }
}
```

## Key Features

### Checksum Strategies:

1. **File-level checksum**: SHA-256 of entire file
   - Detects any changes to source data
   - Prevents accidental modifications

2. **Row-level checksums**: SHA-256 of each record
   - Identifies which specific records changed
   - Tracks additions/deletions
   - Uses JSON serialization for consistent ordering

3. **JSON storage**: 
   - Human-readable format
   - Timestamped for audit trail
   - Includes record count for quick validation

### Verification Modes:

- **File integrity**: Full file hash comparison
- **Record-level**: Individual row hash matching
- **Change detection**: Identifies new/modified/deleted records
- **Audit trail**: Timestamp shows when checksums were created

### Error Handling:

- Mismatched file hash alerts
- Individual record changes flagged
- New/missing records detected
- Invalid checksum files caught
- Warnings for unverified records

This approach ensures data integrity throughout the workflow and creates an audit trail for compliance.
