# Museum Inventory Standardizer with Checksums

Here's how to incorporate checksums to verify data integrity:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksum Verification

Standardizes museum object records and uses checksums to verify
that source data hasn't changed between runs.
"""

import csv
import sys
import re
import hashlib
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict


@dataclass
class MuseumObject:
    """Represents a standardized museum object record."""
    date: str
    title: str
    object_number: str
    link: str
    
    def to_dict(self) -> dict:
        return {
            'Date': self.date,
            'Title': self.title,
            'Object Number': self.object_number,
            'Link': self.link
        }


@dataclass
class ChecksumRecord:
    """Represents checksum information for a source file."""
    file_path: str
    file_hash: str  # Hash of entire file
    record_count: int
    record_hashes: Dict[int, str]  # Row number -> row hash
    timestamp: str
    
    def to_dict(self) -> dict:
        return {
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'record_count': self.record_count,
            'record_hashes': self.record_hashes,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChecksumRecord':
        return cls(
            file_path=data['file_path'],
            file_hash=data['file_hash'],
            record_count=data['record_count'],
            record_hashes=data['record_hashes'],
            timestamp=data['timestamp']
        )


class ChecksumManager:
    """Manages checksum generation and verification."""
    
    def __init__(self, checksum_file: str = '.museum_checksums.json'):
        self.checksum_file = checksum_file
        self.checksums: Dict[str, ChecksumRecord] = {}
        self.load_checksums()
    
    def _hash_data(self, data: bytes, algorithm: str = 'sha256') -> str:
        """Generate hash of data using specified algorithm."""
        hasher = hashlib.new(algorithm)
        hasher.update(data)
        return hasher.hexdigest()
    
    def _hash_file(self, filepath: str, algorithm: str = 'sha256') -> str:
        """Generate hash of entire file."""
        hasher = hashlib.new(algorithm)
        
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def _hash_row(self, row_data: Dict[str, str]) -> str:
        """Generate hash of a single row (order-independent)."""
        # Sort keys to ensure consistent hashing regardless of column order
        sorted_items = sorted(row_data.items())
        row_json = json.dumps(sorted_items, sort_keys=True, ensure_ascii=True)
        return self._hash_data(row_json.encode('utf-8'))
    
    def generate_checksums(self, filepath: str) -> ChecksumRecord:
        """
        Generate checksums for a source file.
        
        Creates:
        - Full file hash
        - Individual row hashes
        - Metadata (timestamp, record count)
        """
        file_path = str(Path(filepath).resolve())
        
        # Generate file hash
        file_hash = self._hash_file(filepath)
        
        # Generate row hashes
        record_hashes = {}
        record_count = 0
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                for row_num, row in enumerate(reader, start=2):
                    record_count += 1
                    row_hash = self._hash_row(row)
                    record_hashes[row_num] = row_hash
            
            checksum = ChecksumRecord(
                file_path=file_path,
                file_hash=file_hash,
                record_count=record_count,
                record_hashes=record_hashes,
                timestamp=datetime.now().isoformat()
            )
            
            self.checksums[file_path] = checksum
            return checksum
            
        except Exception as e:
            raise RuntimeError(f"Error generating checksums: {str(e)}")
    
    def verify_file_unchanged(self, filepath: str) -> Tuple[bool, str]:
        """
        Verify that a file hasn't changed since last run.
        
        Returns:
            (is_unchanged, message)
        """
        file_path = str(Path(filepath).resolve())
        
        if file_path not in self.checksums:
            return True, "No previous checksum found (first run)"
        
        previous = self.checksums[file_path]
        current_hash = self._hash_file(filepath)
        
        if current_hash == previous.file_hash:
            return True, "File unchanged"
        
        return False, f"File has changed since {previous.timestamp}"
    
    def verify_rows_unchanged(self, filepath: str) -> Tuple[bool, List[str]]:
        """
        Verify that individual rows haven't changed.
        
        Returns:
            (all_unchanged, list_of_changed_rows)
        """
        file_path = str(Path(filepath).resolve())
        
        if file_path not in self.checksums:
            return True, []
        
        previous = self.checksums[file_path]
        changed_rows = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                for row_num, row in enumerate(reader, start=2):
                    if row_num in previous.record_hashes:
                        current_hash = self._hash_row(row)
                        if current_hash != previous.record_hashes[row_num]:
                            changed_rows.append(f"Row {row_num}")
                    else:
                        changed_rows.append(f"Row {row_num} (new)")
                
                # Check for deleted rows
                current_count = row_num - 1
                if current_count < previous.record_count:
                    for missing_row in range(current_count + 2, previous.record_count + 2):
                        if missing_row in previous.record_hashes:
                            changed_rows.append(f"Row {missing_row} (deleted)")
            
            return len(changed_rows) == 0, changed_rows
            
        except Exception as e:
            return False, [f"Error verifying rows: {str(e)}"]
    
    def save_checksums(self):
        """Save checksums to file."""
        try:
            checksum_data = {
                path: record.to_dict() 
                for path, record in self.checksums.items()
            }
            
            with open(self.checksum_file, 'w', encoding='utf-8') as f:
                json.dump(checksum_data, f, indent=2)
        except Exception as e:
            raise RuntimeError(f"Error saving checksums: {str(e)}")
    
    def load_checksums(self):
        """Load checksums from file."""
        if not Path(self.checksum_file).exists():
            return
        
        try:
            with open(self.checksum_file, 'r', encoding='utf-8') as f:
                checksum_data = json.load(f)
            
            self.checksums = {
                path: ChecksumRecord.from_dict(data)
                for path, data in checksum_data.items()
            }
        except Exception as e:
            raise RuntimeError(f"Error loading checksums: {str(e)}")


class InventoryStandardizer:
    """Standardizes museum inventory records with checksum verification."""
    
    EXPECTED_COLUMNS = {'date', 'title', 'object number', 'link'}
    OBJECT_NUMBER_PATTERN = re.compile(r'^[A-Z0-9\.\-_]+$', re.IGNORECASE)
    
    def __init__(self, verbose: bool = True, verify_checksums: bool = True):
        self.verbose = verbose
        self.verify_checksums = verify_checksums
        self.records: List[MuseumObject] = []
        self.errors: List[Tuple[int, str]] = []
        self.warnings: List[Tuple[int, str]] = []
        self.checksum_manager = ChecksumManager()
    
    def log(self, message: str):
        """Print log message if verbose mode is enabled."""
        if self.verbose:
            print(message)
    
    def standardize_date(self, date_str: str, row_num: int) -> Optional[str]:
        """Standardize date to YYYY-MM-DD format."""
        if not date_str or not date_str.strip():
            self.errors.append((row_num, "Date field is empty"))
            return None
        
        date_str = date_str.strip()
        
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%d %b %Y',
            '%Y',
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                if fmt == '%Y':
                    self.warnings.append(
                        (row_num, f"Only year provided: {date_str}. Using {parsed.strftime('%Y-01-01')}")
                    )
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        self.errors.append((row_num, f"Could not parse date: {date_str}"))
        return None
    
    def standardize_title(self, title: str, row_num: int) -> Optional[str]:
        """Standardize title by cleaning whitespace and validating."""
        if not title or not title.strip():
            self.errors.append((row_num, "Title field is empty"))
            return None
        
        title = ' '.join(title.split())
        
        if len(title) < 3:
            self.warnings.append((row_num, f"Title is very short: {title}"))
        
        if len(title) > 500:
            self.warnings.append((row_num, f"Title exceeds 500 characters: {len(title)} chars"))
        
        return title
    
    def standardize_object_number(self, obj_num: str, row_num: int) -> Optional[str]:
        """Standardize object number."""
        if not obj_num or not obj_num.strip():
            self.errors.append((row_num, "Object Number field is empty"))
            return None
        
        obj_num = obj_num.strip().upper()
        
        if not self.OBJECT_NUMBER_PATTERN.match(obj_num):
            self.errors.append(
                (row_num, f"Invalid object number format: {obj_num}")
            )
            return None
        
        return obj_num
    
    def standardize_link(self, link: str, row_num: int) -> Optional[str]:
        """Standardize and validate URL."""
        if not link or not link.strip():
            self.errors.append((row_num, "Link field is empty"))
            return None
        
        link = link.strip()
        
        if not link.startswith(('http://', 'https://')):
            if link.startswith('www.'):
                link = 'https://' + link
            else:
                self.warnings.append(
                    (row_num, f"URL missing scheme, assuming https: {link}")
                )
                link = 'https://' + link
        
        try:
            result = urlparse(link)
            if not result.netloc:
                self.errors.append((row_num, f"Invalid URL structure: {link}"))
                return None
        except Exception as e:
            self.errors.append((row_num, f"Error parsing URL {link}: {str(e)}"))
            return None
        
        return link
    
    def read_tsv(self, filepath: str) -> bool:
        """
        Read TSV file with optional checksum verification.
        
        Returns True if successful, False otherwise.
        """
        self.log(f"\nReading {filepath}...")
        
        # Verify checksums if enabled
        if self.verify_checksums:
            self._verify_and_report_checksums(filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    self.log("ERROR: Empty file or no headers found")
                    return False
                
                fieldnames_lower = {name.lower().strip() for name in reader.fieldnames}
                
                missing_cols = self.EXPECTED_COLUMNS - fieldnames_lower
                if missing_cols:
                    self.log(f"ERROR: Missing required columns: {missing_cols}")
                    return False
                
                col_map = {name.lower().strip(): name for name in reader.fieldnames}
                
                for row_num, row in enumerate(reader, start=2):
                    date_str = row.get(col_map['date'], '').strip()
                    title = row.get(col_map['title'], '').strip()
                    object_number = row.get(col_map['object number'], '').strip()
                    link = row.get(col_map['link'], '').strip()
                    
                    std_date = self.standardize_date(date_str, row_num)
                    std_title = self.standardize_title(title, row_num)
                    std_obj_num = self.standardize_object_number(object_number, row_num)
                    std_link = self.standardize_link(link, row_num)
                    
                    if all([std_date, std_title, std_obj_num, std_link]):
                        self.records.append(
                            MuseumObject(std_date, std_title, std_obj_num, std_link)
                        )
                    else:
                        self.log(f"Row {row_num}: Skipped due to validation errors")
                
                self.log(f"Successfully read {len(self.records)} valid records")
                
                # Generate and save checksums after successful read
                if self.verify_checksums:
                    self.checksum_manager.generate_checksums(filepath)
                    self.checksum_manager.save_checksums()
                
                return True
                
        except FileNotFoundError:
            self.log(f"ERROR: File not found: {filepath}")
            return False
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            return False
    
    def _verify_and_report_checksums(self, filepath: str):
        """Verify checksums and report findings."""
        # Check if file has changed
        unchanged, file_msg = self.checksum_manager.verify_file_unchanged(filepath)
        
        if unchanged:
            self.log(f"✓ File integrity: {file_msg}")
        else:
            self.log(f"⚠ File integrity: {file_msg}")
            
            # Provide detailed row-level information
            rows_unchanged, changed_rows = self.checksum_manager.verify_rows_unchanged(filepath)
            
            if not rows_unchanged:
                self.log(f"  Changed rows: {len(changed_rows)}")
                for row_info in changed_rows[:10]:
                    self.log(f"    - {row_info}")
                if len(changed_rows) > 10:
                    self.log(f"    ... and {len(changed_rows) - 10} more")
    
    def write_tsv(self, output_filepath: str) -> bool:
        """Write standardized records to TSV file."""
        try:
            with open(output_filepath, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['Date', 'Title', 'Object Number', 'Link']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                
                writer.writeheader()
                for record in self.records:
                    writer.writerow(record.to_dict())
            
            self.log(f"Wrote {len(self.records)} records to {output_filepath}")
            return True
            
        except Exception as e:
            self.log(f"ERROR writing output: {str(e)}")
            return False
    
    def print_report(self):
        """Print a report of errors and warnings."""
        print("\n" + "="*70)
        print("STANDARDIZATION REPORT")
        print("="*70)
        
        print(f"\nRecords processed: {len(self.records)}")
        
        if self.errors:
            print(f"\n⚠ ERRORS ({len(self.errors)}):")
            for row_num, error in self.errors[:10]:
                print(f"  Row {row_num}: {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")
        
        if self.warnings:
            print(f"\nⓘ WARNINGS ({len(self.warnings)}):")
            for row_num, warning in self.warnings[:10]:
                print(f"  Row {row_num}: {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more warnings")
        
        print("\n" + "="*70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records with checksum verification'
    )
    parser.add_argument('input_file', help='Input TSV file')
    parser.add_argument(
        '-o', '--output',
        default='standardized.tsv',
        help='Output TSV file (default: standardized.tsv)'
    )
    parser.add_argument(
        '-c', '--checksums',
        default='.museum_checksums.json',
        help='Checksum file location (default: .museum_checksums.json)'
    )
    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Skip checksum verification'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress verbose output'
    )
    
    args = parser.parse_args()
    
    standardizer = InventoryStandardizer(
        verbose=not args.quiet,
        verify_checksums=not args.no_verify
    )
    
    # Set custom checksum file if provided
    standardizer.checksum_manager.checksum_file = args.checksums
    standardizer.checksum_manager.load_checksums()
    
    if not standardizer.read_tsv(args.input_file):
        sys.exit(1)
    
    if not standardizer.write_tsv(args.output):
        sys.exit(1)
    
    standardizer.print_report()


if __name__ == '__main__':
    main()
```

## Usage Examples

**First run (generates and saves checksums):**
```bash
python museum_standardizer.py inventory.tsv
```

**Subsequent runs (verifies data hasn't changed):**
```bash
python museum_standardizer.py inventory.tsv
# Output will show checksum verification results
```

**Skip checksum verification:**
```bash
python museum_standardizer.py inventory.tsv --no-verify
```

**Custom checksum file location:**
```bash
python museum_standardizer.py inventory.tsv -c /path/to/checksums.json
```

**Quiet mode:**
```bash
python museum_standardizer.py inventory.tsv -q
```

## Key Features

**Checksum Types:**
- **File-level hash** (SHA-256): Detects any changes to entire file
- **Row-level hashes**: Identifies specific rows that changed
- **Order-independent**: Hashes account for different column ordering

**Verification Reports:**
```
✓ File integrity: File unchanged
✓ File integrity: No previous checksum found (first run)
⚠ File integrity: File has changed since 2024-01-15T10:30:45
  Changed rows: 3
    - Row 5
    - Row 12
    - Row 18 (new)
```

**Checksum Storage** (`.museum_checksums.json`):
```json
{
  "/path/to/inventory.tsv": {
    "file_path": "/path/to/inventory.tsv",
    "file_hash": "abc123...",
    "record_count": 150,
    "record_hashes": {
      "2": "hash_row_2",
      "3": "hash_row_3"
    },
    "timestamp": "2024-01-15T10:30:45.123456"
  }
}
```

This approach ensures data integrity and allows tracking source file changes over time!
