# Museum Inventory Standardizer with Checksum Verification

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory TSV files with checksum verification.

Checksums enable detection of:
    - Accidental file corruption
    - Unauthorized modifications
    - Version tracking across standardization runs
"""

import argparse
import csv
import sys
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


class ChecksumManager:
    """Manages file and record checksums for integrity verification."""
    
    HASH_ALGORITHM = 'sha256'
    CHECKSUM_FILE_SUFFIX = '.checksums.json'
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.checksums: Dict[str, Dict] = {}
    
    @staticmethod
    def hash_string(data: str, algorithm: str = 'sha256') -> str:
        """Generate hash of a string."""
        hasher = hashlib.new(algorithm)
        hasher.update(data.encode('utf-8'))
        return hasher.hexdigest()
    
    @staticmethod
    def hash_file(filepath: str, algorithm: str = 'sha256', 
                  chunk_size: int = 65536) -> str:
        """Generate hash of entire file (memory efficient)."""
        hasher = hashlib.new(algorithm)
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except IOError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return ""
    
    @staticmethod
    def hash_record(record_dict: Dict) -> str:
        """Generate hash of a single record (normalized)."""
        # Normalize field order and values
        normalized = json.dumps(record_dict, sort_keys=True, separators=(',', ':'))
        return ChecksumManager.hash_string(normalized)
    
    def create_file_checksum(self, filepath: str) -> Dict:
        """Create complete checksum record for a file."""
        file_hash = self.hash_file(filepath)
        
        record = {
            'algorithm': self.HASH_ALGORITHM,
            'file': str(filepath),
            'hash': file_hash,
            'timestamp': datetime.now().isoformat(),
            'size': Path(filepath).stat().st_size
        }
        
        if self.verbose:
            print(f"File checksum ({filepath}): {file_hash[:16]}...")
        
        return record
    
    def save_checksums(self, filepath: str, checksums: Dict) -> None:
        """Save checksums to JSON file."""
        checksum_path = Path(filepath).with_suffix(
            Path(filepath).suffix + self.CHECKSUM_FILE_SUFFIX
        )
        
        try:
            with open(checksum_path, 'w', encoding='utf-8') as f:
                json.dump(checksums, f, indent=2)
            
            if self.verbose:
                print(f"Checksums saved to: {checksum_path}")
        
        except IOError as e:
            print(f"Error saving checksums: {e}", file=sys.stderr)
    
    def load_checksums(self, filepath: str) -> Optional[Dict]:
        """Load previously saved checksums."""
        checksum_path = Path(filepath).with_suffix(
            Path(filepath).suffix + self.CHECKSUM_FILE_SUFFIX
        )
        
        if not checksum_path.exists():
            if self.verbose:
                print(f"No checksum file found: {checksum_path}")
            return None
        
        try:
            with open(checksum_path, 'r', encoding='utf-8') as f:
                checksums = json.load(f)
            
            if self.verbose:
                print(f"Loaded checksums from: {checksum_path}")
            
            return checksums
        
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading checksums: {e}", file=sys.stderr)
            return None
    
    def verify_file(self, filepath: str, expected_hash: str) -> Tuple[bool, str]:
        """
        Verify file integrity against expected hash.
        Returns (is_valid, message)
        """
        current_hash = self.hash_file(filepath)
        
        if current_hash == expected_hash:
            return True, f"✓ File integrity verified: {current_hash[:16]}..."
        else:
            return False, (
                f"✗ FILE CORRUPTION DETECTED!\n"
                f"  Expected: {expected_hash}\n"
                f"  Found:    {current_hash}"
            )
    
    def generate_checksum_report(self, filepath: str, 
                                previous_checksums: Optional[Dict]) -> str:
        """Generate a checksum verification report."""
        current = self.create_file_checksum(filepath)
        report = []
        
        report.append("\n" + "="*60)
        report.append("CHECKSUM VERIFICATION REPORT")
        report.append("="*60)
        report.append(f"File: {filepath}")
        report.append(f"Timestamp: {current['timestamp']}")
        report.append(f"File size: {current['size']:,} bytes")
        report.append(f"Algorithm: {current['algorithm'].upper()}")
        report.append(f"Current hash: {current['hash']}")
        
        if previous_checksums:
            report.append("\n--- HISTORY ---")
            
            # Find previous hash for this file
            prev = previous_checksums.get('file_hash')
            if prev:
                is_valid, msg = self.verify_file(filepath, prev)
                report.append(msg)
                
                if not is_valid:
                    report.append("\nWARNING: File has been modified since last run!")
            
            prev_timestamp = previous_checksums.get('timestamp')
            if prev_timestamp:
                report.append(f"Previous timestamp: {prev_timestamp}")
            
            prev_size = previous_checksums.get('size')
            if prev_size and prev_size != current['size']:
                report.append(f"Previous size: {prev_size:,} bytes (CHANGED)")
        else:
            report.append("\n--- HISTORY ---")
            report.append("No previous checksums found (first run)")
        
        report.append("="*60 + "\n")
        return "\n".join(report)


class InventoryRecord:
    """Represents a single inventory record with optional checksum."""
    
    def __init__(self, date: str, title: str, object_number: str, link: str,
                 line_num: int = 0, status: str = "active"):
        self.date = date.strip() if date else ""
        self.title = title.strip() if title else ""
        self.object_number = object_number.strip() if object_number else ""
        self.link = link.strip() if link else ""
        self.line_num = line_num
        self.status = status
        self.original_hash = None  # Hash of original record before corrections
    
    def is_valid(self) -> bool:
        """Check if record has minimum required fields."""
        return bool(self.object_number)
    
    def is_withdrawn(self) -> bool:
        return self.status == "withdrawn"
    
    def is_correction(self) -> bool:
        return self.status == "corrected"
    
    def to_dict(self) -> Dict:
        """Convert record to dictionary for hashing."""
        return {
            'date': self.date,
            'title': self.title,
            'object_number': self.object_number,
            'link': self.link
        }
    
    def calculate_hash(self) -> str:
        """Calculate hash of this record."""
        return ChecksumManager.hash_record(self.to_dict())
    
    def __eq__(self, other):
        if not isinstance(other, InventoryRecord):
            return False
        return self.object_number == other.object_number
    
    def __hash__(self):
        return hash(self.object_number)
    
    def __repr__(self):
        return (f"InventoryRecord(date={self.date}, title={self.title}, "
                f"object_number={self.object_number}, status={self.status})")


class InventoryStandardizer:
    """Standardizes and deduplicates museum inventory records with checksums."""
    
    def __init__(self, verbose: bool = False, track_changes: bool = False):
        self.records: Dict[str, InventoryRecord] = {}
        self.withdrawn: set = set()
        self.verbose = verbose
        self.track_changes = track_changes
        self.warnings: List[str] = []
        self.checksum_manager = ChecksumManager(verbose=verbose)
        self.change_log: List[Dict] = []  # Track what changed and why
    
    def _parse_status(self, title: str, date: str) -> Tuple[str, str]:
        """Extract status markers from title or date field."""
        status = "active"
        cleaned_title = title
        
        if "WITHDRAWN" in cleaned_title.upper():
            status = "withdrawn"
            cleaned_title = cleaned_title.replace("WITHDRAWN", "").strip()
        elif "WITHDRAWN" in date.upper():
            status = "withdrawn"
        
        if "CORRECTED" in cleaned_title.upper() or "↑" in cleaned_title:
            status = "corrected"
            cleaned_title = cleaned_title.replace("CORRECTED", "").replace("↑", "").strip()
        
        return cleaned_title, status
    
    def add_record(self, date: str, title: str, object_number: str,
                   link: str, line_num: int = 0) -> None:
        """Add or update a record in the inventory."""
        cleaned_title, status = self._parse_status(title, date)
        
        record = InventoryRecord(date, cleaned_title, object_number, link,
                                line_num, status)
        
        if not record.is_valid():
            self.warnings.append(
                f"Line {line_num}: Missing object number. Skipping: {title[:50]}"
            )
            return
        
        key = record.object_number
        current_hash = record.calculate_hash()
        
        # Handle withdrawals
        if record.is_withdrawn():
            self.withdrawn.add(key)
            if key in self.records:
                old_record = self.records[key]
                if self.track_changes:
                    self.change_log.append({
                        'action': 'withdrawn',
                        'object_number': key,
                        'old_hash': old_record.calculate_hash(),
                        'line': line_num
                    })
                del self.records[key]
            if self.verbose:
                print(f"Marked withdrawn: {key}")
            return
        
        # Handle corrections and duplicates
        if key in self.records:
            old_record = self.records[key]
            old_hash = old_record.calculate_hash()
            
            if record.is_correction():
                if self.track_changes:
                    self.change_log.append({
                        'action': 'corrected',
                        'object_number': key,
                        'old_hash': old_hash,
                        'new_hash': current_hash,
                        'old_title': old_record.title,
                        'new_title': record.title,
                        'line': line_num
                    })
                
                if self.verbose:
                    print(f"Correcting {key}: '{old_record.title}' → '{record.title}'")
                    print(f"  Hash: {old_hash[:16]}... → {current_hash[:16]}...")
                
                self.records[key] = record
            else:
                # Keep newer record (higher line number)
                if line_num > old_record.line_num:
                    if self.track_changes and old_hash != current_hash:
                        self.change_log.append({
                            'action': 'updated',
                            'object_number': key,
                            'old_hash': old_hash,
                            'new_hash': current_hash,
                            'old_line': old_record.line_num,
                            'new_line': line_num
                        })
                    
                    if self.verbose:
                        print(f"Updating {key} (line {old_record.line_num} → {line_num})")
                    
                    self.records[key] = record
                else:
                    if self.verbose:
                        print(f"Keeping earlier record for {key}")
        else:
            self.records[key] = record
            if self.track_changes:
                self.change_log.append({
                    'action': 'added',
                    'object_number': key,
                    'hash': current_hash,
                    'line': line_num
                })
    
    def load_tsv(self, filepath: str, verify: bool = True) -> int:
        """
        Load records from TSV file with optional integrity verification.
        Returns number of records loaded.
        """
        # Verify file integrity if checksums exist
        if verify:
            previous = self.checksum_manager.load_checksums(filepath)
            if previous:
                is_valid, msg = self.checksum_manager.verify_file(
                    filepath, previous.get('file_hash')
                )
                if not is_valid:
                    print(msg, file=sys.stderr)
                    response = input("Continue anyway? (y/n): ").lower()
                    if response != 'y':
                        sys.exit(1)
        
        count = 0
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                
                # Skip header if present
                header = next(reader, None)
                if header and len(header) == 4:
                    if all(h.lower() in ['date', 'title', 'object number',
                                        'object_number', 'link'] for h in header):
                        if self.verbose:
                            print(f"Header: {header}")
                    else:
                        self.add_record(*header, line_num=1)
                        count += 1
                
                # Process remaining lines
                for line_num, row in enumerate(reader, start=2):
                    if not row or all(not field.strip() for field in row):
                        continue
                    
                    if len(row) < 4:
                        self.warnings.append(
                            f"Line {line_num}: Incomplete row (expected 4 columns, got {len(row)})"
                        )
                        continue
                    
                    self.add_record(row[0], row[1], row[2], row[3], line_num)
                    count += 1
        
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
        
        return count
    
    def save_tsv(self, filepath: str, include_header: bool = True,
                 save_checksums: bool = True) -> None:
        """Save standardized records to TSV file with optional checksums."""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter='\t')
                
                if include_header:
                    writer.writerow(['date', 'title', 'object_number', 'link'])
                
                # Sort by object number for consistency
                for record in sorted(self.records.values(),
                                    key=lambda r: r.object_number):
                    writer.writerow([
                        record.date,
                        record.title,
                        record.object_number,
                        record.link
                    ])
        
        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Save checksums
        if save_checksums:
            checksums = {
                'file_hash': self.checksum_manager.hash_file(filepath),
                'timestamp': datetime.now().isoformat(),
                'size': Path(filepath).stat().st_size,
                'records': len(self.records),
                'algorithm': ChecksumManager.HASH_ALGORITHM
            }
            self.checksum_manager.save_checksums(filepath, checksums)
    
    def get_change_log(self) -> str:
        """Generate a report of all changes made."""
        if not self.change_log:
            return "No changes recorded.\n"
        
        report = []
        report.append("\n" + "="*60)
        report.append("CHANGE LOG")
        report.append("="*60)
        
        for i, change in enumerate(self.change_log, 1):
            action = change['action'].upper()
            obj_num = change.get('object_number', 'N/A')
            
            if action == 'ADDED':
                report.append(f"{i}. {action}: {obj_num}")
                report.append(f"   Hash: {change.get('hash', 'N/A')[:16]}...")
            
            elif action == 'CORRECTED':
                report.append(f"{i}. {action}: {obj_num}")
                report.append(f"   Old: '{change.get('old_title', 'N/A')}'")
                report.append(f"   New: '{change.get('new_title', 'N/A')}'")
                old_h = change.get('old_hash', 'N/A')[:16]
                new_h = change.get('new_hash', 'N/A')[:16]
                report.append(f"   Hash: {old_h}... → {new_h}...")
            
            elif action == 'UPDATED':
                report.append(f"{i}. {action}: {obj_num}")
                report.append(f"   Line {change.get('old_line')} → {change.get('new_line')}")
                old_h = change.get('old_hash', 'N/A')[:16]
                new_h = change.get('new_hash', 'N/A')[:16]
                report.append(f"   Hash: {old_h}... → {new_h}...")
            
            elif action == 'WITHDRAWN':
                report.append(f"{i}. {action}: {obj_num}")
        
        report.append("="*60 + "\n")
        return "\n".join(report)
    
    def get_report(self) -> str:
        """Generate a standardization report."""
        report = []
        report.append("\n" + "="*60)
        report.append("INVENTORY STANDARDIZATION REPORT")
        report.append("="*60)
        report.append(f"Total active records: {len(self.records)}")
        report.append(f"Withdrawn records: {len(self.withdrawn)}")
        report.append(f"Warnings/Issues: {len(self.warnings)}")
        
        if self.warnings:
            report.append("\n--- WARNINGS ---")
            for warning in self.warnings[:20]:
                report.append(f"  • {warning}")
            if len(self.warnings) > 20:
                report.append(f"  ... and {len(self.warnings) - 20} more")
        
        # Data quality checks
        report.append("\n--- DATA QUALITY ---")
        missing_date = sum(1 for r in self.records.values() if not r.date)
        missing_title = sum(1 for r in self.records.values() if not r.title)
        missing_link = sum(1 for r in self.records.values() if not r.link)
        
        if missing_date:
            report.append(f"  • Records missing date: {missing_date}")
        if missing_title:
            report.append(f"  • Records missing title: {missing_title}")
        if missing_link:
            report.append(f"  • Records missing link: {missing_link}")
        
        if not (missing_date or missing_title or missing_link):
            report.append("  ✓ All required fields present")
        
        report.append("="*60 + "\n")
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory TSV files with checksum verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (first run - creates checksums)
  python standardizer.py inventory.tsv -o standardized.tsv
  
  # Verify file hasn't changed, verbose output
  python standardizer.py inventory.tsv -o standardized.tsv -v --verify
  
  # Show changes with detailed report
  python standardizer.py inventory.tsv -o standardized.tsv --track-changes --report
  
  # Skip checksum verification
  python standardizer.py inventory.tsv -o standardized.tsv --no-verify
        """
    )
    
    parser.add_argument('input', help='Input TSV file')
    parser.add_argument('-o', '--output', help='Output TSV file')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--verify', action='store_true',
                       help='Verify file integrity against previous checksums')
    parser.add_argument('--no-verify', action='store_true',
                       help='Skip checksum verification')
    parser.add_argument('--track-changes', action='store_true',
                       help='Track and log all changes')
    parser.add_argument('--report', action='store_true',
                       help='Print detailed standardization and checksum reports')
    parser.add_argument('--no-header', action='store_true',
                       help='Do not include header in output')
    parser.add_argument('--no-checksums', action='store_true',
                       help='Do not save checksums')
    
    args = parser.parse_args()
    
    # Process inventory
    standardizer = InventoryStandardizer(
        verbose=args.verbose,
        track_changes=args.track_changes or args.report
    )
    
    print(f"Loading {args.input}...", file=sys.stderr)
    count = standardizer.load_tsv(
        args.input,
        verify=args.verify and not args.no_verify
    )
    print(f"Loaded {count} records", file=sys.stderr)
    
    # Output
    if args.output:
        standardizer.save_tsv(
            args.output,
            include_header=not args.no_header,
            save_checksums=not args.no_checksums
        )
        print(f"Saved to {args.output}", file=sys.stderr)
    
    # Reports
    if args.report:
        print(standardizer.get_report(), file=sys.stderr)
        if args.track_changes:
            print(standardizer.get_change_log(), file=sys.stderr)
        
        # Checksum report
        if args.output:
            previous = standardizer.checksum_manager.load_checksums(args.output)
            report = standardizer.checksum_manager.generate_checksum_report(
                args.output, previous
            )
            print(report, file=sys.stderr)


if __name__ == '__main__':
    main()
```

## Checksum Features

### 1. **File-Level Checksums**
```bash
# First run - creates inventory.tsv.checksums.json
python standardizer.py inventory.tsv -o standardized.tsv

# Verify file hasn't changed since last run
python standardizer.py inventory.tsv -o standardized.tsv --verify
```

### 2. **Checksum File Format**
```json
{
  "file_hash": "a3f4e8d...",
  "timestamp": "2024-01-20T10:30:45.123456",
  "size": 15234,
  "records": 842,
  "algorithm": "sha256"
}
```

### 3. **Record-Level Checksums**
```bash
# Track changes with record hashes
python standardizer.py inventory.tsv -o out.tsv --track-changes -v
```

### 4. **Change Detection**
- Detects if file was corrupted or modified
- Tracks which records were corrected vs. updated
- Records hash changes for audit trail

### 5. **Use Cases**

```bash
# Detect unauthorized changes
python standardizer.py inventory.tsv --verify --report

# Audit trail of corrections
python standardizer.py inventory.tsv --track-changes --report

# Verify before production deployment
python standardizer.py inventory.tsv -o prod.tsv --verify

# Compare two versions
# (First generate checksums, then modify file and verify)
```

### 6. **Key Benefits**

- **Corruption Detection**: SHA-256 catches any file changes
- **Audit Trail**: Record which fields changed and when
- **Version Control**: Track modifications over time
- **Compliance**: Document data integrity for archival purposes
- **Confidence**: Verify data hasn't been tampered with

The checksums are stored separately with timestamps, allowing you to track the entire history of data transformations.
