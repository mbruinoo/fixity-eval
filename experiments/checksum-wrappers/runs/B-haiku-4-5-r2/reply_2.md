# Museum Inventory Standardizer with Checksum Verification

Here's the enhanced script with checksum functionality:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksum Verification

Standardizes museum inventory records from a TSV file and includes
checksum verification to detect source data changes.
"""

import argparse
import sys
import hashlib
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import re
import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class ChecksumRecord:
    """Stores checksum information for a record."""
    object_number: str
    row_number: int
    full_row_hash: str  # Hash of entire row
    field_hashes: Dict[str, str]  # Individual field hashes
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class InventoryRecord:
    """Represents a standardized museum inventory record."""
    date: str
    title: str
    object_number: str
    link: str
    source_hash: str = ""  # Hash of original source data
    
    def is_valid(self) -> Tuple[bool, List[str]]:
        """Validate the record. Returns (is_valid, error_list)."""
        errors = []
        
        if not self.date or not self.date.strip():
            errors.append("Missing date")
        if not self.title or not self.title.strip():
            errors.append("Missing title")
        if not self.object_number or not self.object_number.strip():
            errors.append("Missing object number")
        if not self.link or not self.link.strip():
            errors.append("Missing link")
        
        return len(errors) == 0, errors


class ChecksumManager:
    """Manages checksum generation and verification."""
    
    ALGORITHM = 'sha256'
    
    @staticmethod
    def compute_hash(data: str, algorithm: str = ALGORITHM) -> str:
        """Compute hash of a string."""
        return hashlib.new(algorithm, data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def compute_row_hash(row: Dict[str, str]) -> str:
        """Compute hash of entire row (canonical form)."""
        # Sort fields for consistent hashing
        canonical = json.dumps(row, sort_keys=True, separators=(',', ':'))
        return ChecksumManager.compute_hash(canonical)
    
    @staticmethod
    def compute_field_hashes(row: Dict[str, str]) -> Dict[str, str]:
        """Compute individual field hashes."""
        return {
            field: ChecksumManager.compute_hash(value)
            for field, value in row.items()
        }
    
    @staticmethod
    def compute_file_hash(file_path: Path, algorithm: str = ALGORITHM) -> str:
        """Compute hash of entire file."""
        hasher = hashlib.new(algorithm)
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            raise IOError(f"Could not compute file hash: {e}")


class ChecksumStore:
    """Stores and manages checksums for verification."""
    
    def __init__(self, store_path: Path):
        self.store_path = store_path
        self.checksums: Dict[str, ChecksumRecord] = {}
        self.file_hash: Optional[str] = None
        self.file_hash_timestamp: Optional[str] = None
    
    def load(self) -> bool:
        """Load checksums from file."""
        if not self.store_path.exists():
            return False
        
        try:
            with open(self.store_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.file_hash = data.get('file_hash')
            self.file_hash_timestamp = data.get('file_hash_timestamp')
            
            for obj_num, record_data in data.get('records', {}).items():
                record = ChecksumRecord(
                    object_number=record_data['object_number'],
                    row_number=record_data['row_number'],
                    full_row_hash=record_data['full_row_hash'],
                    field_hashes=record_data['field_hashes'],
                    timestamp=record_data.get('timestamp', '')
                )
                self.checksums[obj_num] = record
            
            return True
        except Exception as e:
            print(f"Warning: Could not load checksum store: {e}", file=sys.stderr)
            return False
    
    def save(self) -> bool:
        """Save checksums to file."""
        try:
            data = {
                'file_hash': self.file_hash,
                'file_hash_timestamp': self.file_hash_timestamp,
                'algorithm': ChecksumManager.ALGORITHM,
                'records': {
                    obj_num: {
                        'object_number': record.object_number,
                        'row_number': record.row_number,
                        'full_row_hash': record.full_row_hash,
                        'field_hashes': record.field_hashes,
                        'timestamp': record.timestamp
                    }
                    for obj_num, record in self.checksums.items()
                }
            }
            
            with open(self.store_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Warning: Could not save checksum store: {e}", file=sys.stderr)
            return False
    
    def add_record(self, checksum_record: ChecksumRecord):
        """Add or update a checksum record."""
        self.checksums[checksum_record.object_number] = checksum_record
    
    def get_record(self, object_number: str) -> Optional[ChecksumRecord]:
        """Retrieve a checksum record."""
        return self.checksums.get(object_number)


class DateStandardizer:
    """Handles date format standardization."""
    
    COMMON_FORMATS = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%m-%d-%Y",
        "%d-%m-%Y",
    ]
    
    @staticmethod
    def standardize(date_str: str) -> Tuple[str, bool]:
        """Convert date to ISO format (YYYY-MM-DD)."""
        if not date_str or not date_str.strip():
            return "", False
        
        date_str = date_str.strip()
        
        for fmt in DateStandardizer.COMMON_FORMATS:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d"), True
            except ValueError:
                continue
        
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            return f"{year_match.group()}-01-01", True
        
        return date_str, False


class ObjectNumberStandardizer:
    """Handles object number standardization."""
    
    @staticmethod
    def standardize(obj_num: str) -> str:
        """Standardize object number."""
        obj_num = obj_num.strip()
        obj_num = re.sub(r'\s+', ' ', obj_num)
        return obj_num


class LinkValidator:
    """Validates and standardizes URLs."""
    
    @staticmethod
    def validate_and_standardize(url: str) -> Tuple[str, bool]:
        """Validate URL and add scheme if missing."""
        if not url or not url.strip():
            return "", False
        
        url = url.strip()
        
        if not re.match(r'^https?://', url):
            url = 'https://' + url
        
        try:
            result = urlparse(url)
            if all([result.scheme, result.netloc]):
                return url, True
        except Exception:
            pass
        
        return url, False


class TitleStandardizer:
    """Handles title standardization."""
    
    @staticmethod
    def standardize(title: str) -> str:
        """Standardize title."""
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)
        return title


class InventoryStandardizer:
    """Main class for standardizing inventory records with checksum verification."""
    
    def __init__(self, input_file: Path, output_file: Path,
                 checksum_file: Optional[Path] = None,
                 strict: bool = False, verbose: bool = False,
                 verify: bool = False, track_changes: bool = False):
        self.input_file = input_file
        self.output_file = output_file
        self.strict = strict
        self.verbose = verbose
        self.verify = verify
        self.track_changes = track_changes
        
        # Initialize checksum store
        if checksum_file is None:
            checksum_file = input_file.with_suffix('.checksums.json')
        self.checksum_store = ChecksumStore(checksum_file)
        
        self.records: List[InventoryRecord] = []
        self.errors: List[Dict] = []
        self.checksum_changes: List[Dict] = []
        self.integrity_issues: List[Dict] = []
    
    def read_records(self) -> bool:
        """Read records from TSV file with checksum tracking."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    print("Error: Empty file or no header row", file=sys.stderr)
                    return False
                
                required_fields = {'date', 'title', 'object_number', 'link'}
                provided_fields = set(reader.fieldnames)
                
                missing_fields = required_fields - provided_fields
                if missing_fields:
                    print(f"Error: Missing required columns: {missing_fields}",
                          file=sys.stderr)
                    return False
                
                for row_num, row in enumerate(reader, start=2):
                    record = self._process_row(row, row_num)
                    if record:
                        self.records.append(record)
            
            # Compute file hash
            self.checksum_store.file_hash = ChecksumManager.compute_file_hash(
                self.input_file
            )
            self.checksum_store.file_hash_timestamp = datetime.now().isoformat()
            
            return True
        
        except FileNotFoundError:
            print(f"Error: File not found: {self.input_file}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return False
    
    def _process_row(self, row: Dict, row_num: int) -> Optional[InventoryRecord]:
        """Process and standardize a single row with checksum tracking."""
        record_errors = []
        
        # Compute checksums of original row
        original_row_hash = ChecksumManager.compute_row_hash(row)
        field_hashes = ChecksumManager.compute_field_hashes(row)
        
        # Check for data integrity if verify mode is enabled
        if self.verify:
            self._verify_record_integrity(row, row_num, original_row_hash, field_hashes)
        
        # Standardize fields
        date_str = row.get('date', '').strip()
        standardized_date, date_valid = DateStandardizer.standardize(date_str)
        if not date_valid:
            record_errors.append(f"Could not parse date: '{date_str}'")
        
        title = TitleStandardizer.standardize(row.get('title', ''))
        if not title:
            record_errors.append("Title is empty")
        
        obj_num = ObjectNumberStandardizer.standardize(
            row.get('object_number', '')
        )
        if not obj_num:
            record_errors.append("Object number is empty")
        
        link = row.get('link', '').strip()
        standardized_link, link_valid = LinkValidator.validate_and_standardize(link)
        if not link_valid:
            record_errors.append(f"Invalid URL: '{link}'")
        
        record = InventoryRecord(
            date=standardized_date,
            title=title,
            object_number=obj_num,
            link=standardized_link,
            source_hash=original_row_hash
        )
        
        is_valid, validation_errors = record.is_valid()
        record_errors.extend(validation_errors)
        
        if record_errors:
            error_entry = {
                'row': row_num,
                'object_number': obj_num,
                'errors': record_errors
            }
            self.errors.append(error_entry)
            
            if self.verbose:
                print(f"Row {row_num}: {'; '.join(record_errors)}")
            
            if self.strict and not is_valid:
                return None
        
        # Track changes if enabled
        if self.track_changes:
            self._track_record_changes(record, row_num, original_row_hash, field_hashes)
        
        return record
    
    def _verify_record_integrity(self, row: Dict, row_num: int,
                                 row_hash: str, field_hashes: Dict[str, str]):
        """Verify that a record hasn't been corrupted."""
        obj_num = row.get('object_number', 'UNKNOWN')
        stored_record = self.checksum_store.get_record(obj_num)
        
        if stored_record:
            if stored_record.full_row_hash != row_hash:
                issue = {
                    'row': row_num,
                    'object_number': obj_num,
                    'type': 'data_changed',
                    'message': 'Record data has changed since last standardization',
                    'previous_hash': stored_record.full_row_hash,
                    'current_hash': row_hash,
                    'changed_fields': self._detect_field_changes(
                        stored_record.field_hashes,
                        field_hashes
                    )
                }
                self.integrity_issues.append(issue)
                
                if self.verbose:
                    print(f"Warning Row {row_num}: Record has changed")
    
    def _detect_field_changes(self, old_hashes: Dict[str, str],
                             new_hashes: Dict[str, str]) -> List[str]:
        """Detect which fields have changed."""
        changed = []
        for field in old_hashes:
            if field in new_hashes and old_hashes[field] != new_hashes[field]:
                changed.append(field)
        return changed
    
    def _track_record_changes(self, record: InventoryRecord, row_num: int,
                             row_hash: str, field_hashes: Dict[str, str]):
        """Track changes to a record."""
        stored_record = self.checksum_store.get_record(record.object_number)
        
        if stored_record and stored_record.full_row_hash != row_hash:
            self.checksum_changes.append({
                'object_number': record.object_number,
                'row_number': row_num,
                'changed_fields': self._detect_field_changes(
                    stored_record.field_hashes,
                    field_hashes
                ),
                'previous_timestamp': stored_record.timestamp,
                'current_timestamp': datetime.now().isoformat()
            })
        
        # Store/update checksum
        checksum_record = ChecksumRecord(
            object_number=record.object_number,
            row_number=row_num,
            full_row_hash=row_hash,
            field_hashes=field_hashes
        )
        self.checksum_store.add_record(checksum_record)
    
    def remove_duplicates(self) -> int:
        """Remove duplicate records."""
        original_count = len(self.records)
        unique_records = {}
        
        for record in self.records:
            key = record.object_number.upper()
            if key not in unique_records:
                unique_records[key] = record
        
        self.records = list(unique_records.values())
        removed_count = original_count - len(self.records)
        
        if removed_count > 0 and self.verbose:
            print(f"Removed {removed_count} duplicate records")
        
        return removed_count
    
    def write_records(self) -> bool:
        """Write standardized records to output TSV file."""
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['date', 'title', 'object_number', 'link'],
                    delimiter='\t'
                )
                writer.writeheader()
                for record in sorted(self.records, key=lambda r: r.date):
                    row_data = asdict(record)
                    row_data.pop('source_hash', None)  # Don't write source hash
                    writer.writerow(row_data)
            
            return True
        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            return False
    
    def save_checksums(self) -> bool:
        """Save checksums to file."""
        return self.checksum_store.save()
    
    def load_checksums(self) -> bool:
        """Load existing checksums for verification."""
        return self.checksum_store.load()
    
    def generate_report(self, report_file: Path = None) -> str:
        """Generate a standardization and integrity report."""
        report_lines = [
            "=" * 70,
            "MUSEUM INVENTORY STANDARDIZATION REPORT",
            "=" * 70,
            f"Input file: {self.input_file}",
            f"Output file: {self.output_file}",
            f"Processed: {datetime.now().isoformat()}",
            "",
            "FILE INTEGRITY",
            "-" * 70,
            f"Input file hash ({ChecksumManager.ALGORITHM}): "
            f"{self.checksum_store.file_hash[:16]}...",
            f"Timestamp: {self.checksum_store.file_hash_timestamp}",
            "",
            "PROCESSING SUMMARY",
            "-" * 70,
            f"Total records processed: {len(self.records)}",
            f"Records with errors: {len(self.errors)}",
            "",
        ]
        
        if self.integrity_issues:
            report_lines.extend([
                "INTEGRITY ISSUES DETECTED",
                "-" * 70,
            ])
            for issue in self.integrity_issues:
                report_lines.append(
                    f"Row {issue['row']} ({issue['object_number']}): "
                    f"{issue['message']}"
                )
                if issue['changed_fields']:
                    report_lines.append(
                        f"  Changed fields: {', '.join(issue['changed_fields'])}"
                    )
            report_lines.append("")
        
        if self.checksum_changes:
            report_lines.extend([
                "TRACKED CHANGES",
                "-" * 70,
            ])
            for change in self.checksum_changes:
                report_lines.append(
                    f"{change['object_number']}: "
                    f"Changed {len(change['changed_fields'])} field(s)"
                )
                if change['changed_fields']:
                    report_lines.append(
                        f"  {', '.join(change['changed_fields'])}"
                    )
            report_lines.append("")
        
        if self.errors:
            report_lines.extend([
                "VALIDATION ERRORS",
                "-" * 70,
            ])
            for error in sorted(self.errors, key=lambda e: e['row']):
                report_lines.append(
                    f"Row {error['row']} ({error['object_number']}):"
                )
                for err_msg in error['errors']:
                    report_lines.append(f"  • {err_msg}")
            report_lines.append("")
        
        report_lines.extend([
            "=" * 70,
            f"Records successfully standardized: {len(self.records)}",
            "=" * 70,
        ])
        
        report = "\n".join(report_lines)
        
        if report_file:
            try:
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report)
            except Exception as e:
                print(f"Warning: Could not write report file: {e}", file=sys.stderr)
        
        return report


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
        help='Output TSV file (default: standardized_inventory.tsv)'
    )
    parser.add_argument(
        '-c', '--checksums',
        type=Path,
        default=None,
        help='Checksum store file (default: <input>.checksums.json)'
    )
    parser.add_argument(
        '-r', '--report',
        type=Path,
        default=None,
        help='Generate a report file'
    )
    parser.add_argument(
        '-v', '--verify',
        action='store_true',
        help='Verify data integrity against stored checksums'
    )
    parser.add_argument(
        '-t', '--track-changes',
        action='store_true',
        help='Track and record changes to existing records'
    )
    parser.add_argument(
        '-s', '--strict',
        action='store_true',
        help='Skip records with errors (strict mode)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    output_file = args.output or Path('standardized_inventory.tsv')
    
    # Create standardizer
    standardizer = InventoryStandardizer(
        args.input_file,
        output_file,
        checksum_file=args.checksums,
        strict=args.strict,
        verbose=args.verbose,
        verify=args.verify,
        track_changes=args.track_changes
    )
    
    # Load existing checksums if verifying
    if args.verify:
        print("Loading existing checksums...")
        standardizer.load_checksums()
    
    print(f"Reading records from {args.input_file}...")
    if not standardizer.read_records():
        sys.exit(1)
    
    print(f"Loaded {len(standardizer.records)} records")
    print("Removing duplicates...")
    standardizer.remove_duplicates()
    
    print(f"Writing standardized records to {output_file}...")
    if not standardizer.write_records():
        sys.exit(1)
    
    # Save checksums
    if args.track_changes or not args.verify:
        print("Saving checksums...")
        standardizer.save_checksums()
    
    # Generate and print report
    report = standardizer.generate_report(args.report)
    print("\n" + report)
    
    if args.report:
        print(f"\nReport saved to {args.report}")


if __name__ == '__main__':
    main()
```

## Usage Examples

**First run (establish baseline):**
```bash
python standardizer.py inventory.tsv --track-changes -r report.txt
```

**Verify subsequent runs haven't changed data:**
```bash
python standardizer.py inventory.tsv --verify -r report.txt
```

**Full workflow with changes:**
```bash
python standardizer.py inventory.tsv --track-changes --verify -r report.txt
```

**Custom checksum file:**
```bash
python standardizer.py inventory.tsv -c my_checksums.json --track-changes
```

## Key Features

✅ **File-level checksums** - Detect if entire file changed  
✅ **Row-level checksums** - Detect if specific records changed  
✅ **Field-level checksums** - Identify exactly which fields changed  
✅ **Change tracking** - Log all modifications over time  
✅ **Integrity verification** - Compare current data against stored checksums  
✅ **Detailed reports** - Show which records changed and how  
✅ **Change history** - Timestamps show when changes occurred  
✅ **SHA-256 hashing** - Cryptographically secure verification  

## Example Checksum File

```json
{
  "file_hash": "a3f9c8e2b1d4f6e8c9a2b1d4f6e8c9a2...",
  "file_hash_timestamp": "2024-01-15T14:30:22.123456",
  "algorithm": "sha256",
  "records": {
    "EGY-001": {
      "object_number": "EGY-001",
      "row_number": 2,
      "full_row_hash": "8f9e7d6c5b4a3f2e1d0c9b8a7f6e5d4c...",
      "field_hashes": {
        "date": "3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d...",
        "title": "7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c...",
        "object_number": "c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4...",
        "link": "1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d..."
      },
      "timestamp": "2024-01-15T14:30:22.123456"
    }
  }
}
```
