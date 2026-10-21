# Museum Inventory Standardizer with Checksum Verification

```python
#!/usr/bin/env python3
"""
Standardize and validate museum inventory spreadsheet (.tsv) with checksums.
Verifies source data integrity and tracks changes.
"""

import csv
import sys
import re
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse


class ChecksumManager:
    """Manage checksums for data integrity verification."""
    
    CHECKSUM_VERSION = 1
    
    def __init__(self, checksum_file: Optional[Path] = None):
        """
        Initialize checksum manager.
        
        Args:
            checksum_file: Path to store checksums (default: .checksums.json)
        """
        self.checksum_file = checksum_file or Path(".checksums.json")
        self.checksums: Dict = self._load_checksums()
    
    def _load_checksums(self) -> Dict:
        """Load existing checksums from file."""
        if self.checksum_file.exists():
            try:
                with open(self.checksum_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {'version': self.CHECKSUM_VERSION, 'files': {}}
        
        return {'version': self.CHECKSUM_VERSION, 'files': {}}
    
    def save_checksums(self) -> None:
        """Save checksums to file."""
        try:
            with open(self.checksum_file, 'w') as f:
                json.dump(self.checksums, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save checksums: {e}", file=sys.stderr)
    
    def compute_file_checksum(self, file_path: Path, 
                             algorithm: str = 'sha256') -> str:
        """
        Compute checksum for entire file.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm (sha256, md5, sha1)
            
        Returns:
            Hex digest of file hash
        """
        hash_obj = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except IOError as e:
            raise IOError(f"Could not read file {file_path}: {e}")
    
    def compute_row_checksum(self, row: Dict, 
                            fields: List[str] = None,
                            algorithm: str = 'sha256') -> str:
        """
        Compute checksum for a single row.
        
        Args:
            row: Dictionary row
            fields: Specific fields to include (default: all)
            algorithm: Hash algorithm
            
        Returns:
            Hex digest of row hash
        """
        if fields is None:
            fields = sorted(row.keys())
        
        # Create canonical string representation
        row_data = '|'.join(
            str(row.get(field, '')) for field in sorted(fields)
        )
        
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(row_data.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def compute_dataset_checksum(self, rows: List[Dict],
                                fields: List[str] = None,
                                algorithm: str = 'sha256') -> str:
        """
        Compute checksum for entire dataset.
        Useful for detecting if source data has changed.
        
        Args:
            rows: List of row dictionaries
            fields: Specific fields to include
            algorithm: Hash algorithm
            
        Returns:
            Hex digest of dataset hash
        """
        hash_obj = hashlib.new(algorithm)
        
        for row in rows:
            row_hash = self.compute_row_checksum(row, fields, algorithm)
            hash_obj.update(row_hash.encode('utf-8'))
        
        return hash_obj.hexdigest()
    
    def store_file_checksum(self, file_path: Path, 
                           algorithm: str = 'sha256') -> str:
        """
        Compute and store file checksum.
        
        Returns:
            The computed checksum
        """
        checksum = self.compute_file_checksum(file_path, algorithm)
        
        if 'files' not in self.checksums:
            self.checksums['files'] = {}
        
        file_key = str(file_path)
        self.checksums['files'][file_key] = {
            'checksum': checksum,
            'algorithm': algorithm,
            'timestamp': datetime.now().isoformat(),
            'size': file_path.stat().st_size,
        }
        
        return checksum
    
    def verify_file_checksum(self, file_path: Path, 
                            algorithm: str = 'sha256') -> Tuple[bool, str]:
        """
        Verify file hasn't changed since last checksum.
        
        Returns:
            (is_unchanged, message)
        """
        file_key = str(file_path)
        
        if file_key not in self.checksums.get('files', {}):
            return False, "No previous checksum found"
        
        stored = self.checksums['files'][file_key]
        current = self.compute_file_checksum(file_path, algorithm)
        
        if stored['checksum'] == current:
            return True, "Checksum matches - file unchanged"
        else:
            return False, (
                f"Checksum mismatch!\n"
                f"  Previous: {stored['checksum']} "
                f"({stored['algorithm']})\n"
                f"  Current:  {current}\n"
                f"  Last verified: {stored['timestamp']}"
            )


class MuseumInventoryStandardizer:
    """Standardize and validate museum inventory data with checksums."""
    
    REQUIRED_COLUMNS = {'date', 'title', 'object_number', 'link'}
    WITHDRAWAL_MARKERS = {'withdrawn', 'deleted', 'removed', 'void'}
    
    def __init__(self, input_file: str, output_file: str = None,
                 log_file: str = None, checksum_file: str = None,
                 keep_history: bool = False, verify_checksums: bool = False):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input .tsv file
            output_file: Path to output .tsv file
            log_file: Path to log file
            checksum_file: Path to checksums file
            keep_history: Keep all versions
            verify_checksums: Verify source data hasn't changed
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file or 
                               self.input_file.stem + "_standardized.tsv")
        self.log_file = Path(log_file or "standardization.log")
        self.keep_history = keep_history
        self.verify_checksums = verify_checksums
        
        self.checksum_mgr = ChecksumManager(
            Path(checksum_file) if checksum_file else None
        )
        
        self.entries: Dict[str, Dict] = {}
        self.history: Dict[str, List[Dict]] = {}
        self.warnings: List[str] = []
        self.errors: List[str] = []
        
        # Store checksums for this run
        self.run_checksums: Dict = {
            'input_file': None,
            'output_file': None,
            'source_data': None,
            'raw_rows': [],  # Checksums of each raw row
            'processed_entries': {},  # object_number -> checksum
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log message to file and optionally console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {level}: {message}"
        print(log_message, file=sys.stderr)
        
        with open(self.log_file, 'a') as f:
            f.write(log_message + "\n")
    
    def verify_input_file(self) -> bool:
        """
        Verify input file hasn't changed since last run.
        
        Returns:
            True if checksum matches or no previous checksum exists
        """
        if not self.verify_checksums:
            return True
        
        unchanged, message = self.checksum_mgr.verify_file_checksum(
            self.input_file
        )
        
        self.log(f"Input file verification: {message}")
        
        if not unchanged and self.checksum_mgr.checksums['files'].get(str(self.input_file)):
            self.warnings.append(f"SOURCE DATA CHANGED: {message}")
            return False
        
        return True
    
    def read_input_with_checksums(self) -> List[Dict]:
        """
        Read TSV file and compute checksums for each row.
        
        Returns:
            List of row dictionaries
        """
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        entries = []
        
        try:
            with open(self.input_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    raise ValueError("Empty file or unable to read headers")
                
                reader.fieldnames = [col.lower().strip() for col in reader.fieldnames]
                
                for row_num, row in enumerate(reader, start=2):
                    entry = {k.lower(): v for k, v in row.items()}
                    
                    # Compute checksum for raw row
                    row_checksum = self.checksum_mgr.compute_row_checksum(entry)
                    self.run_checksums['raw_rows'].append({
                        'row_num': row_num,
                        'checksum': row_checksum,
                        'object_number': entry.get('object_number', 'UNKNOWN')
                    })
                    
                    entries.append(entry)
        
        except Exception as e:
            self.log(f"Error reading input file: {e}", "ERROR")
            raise
        
        # Compute checksum for entire source dataset
        self.run_checksums['source_data'] = (
            self.checksum_mgr.compute_dataset_checksum(entries)
        )
        
        return entries
    
    def standardize_date(self, date_str: str) -> str:
        """Standardize date to YYYY-MM-DD format."""
        if not date_str or date_str.strip() == '':
            return ''
        
        date_str = date_str.strip()
        formats = [
            '%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y',
            '%m-%d-%Y', '%d-%m-%Y', '%B %d, %Y', '%b %d, %Y',
            '%d %B %Y', '%d %b %Y',
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        self.warnings.append(f"Could not parse date: {date_str}")
        return date_str
    
    def standardize_object_number(self, obj_num: str) -> str:
        """Standardize object number."""
        if not obj_num:
            return ''
        obj_num = obj_num.strip()
        obj_num = re.sub(r'[\s]+', '', obj_num)
        return obj_num.upper()
    
    def standardize_title(self, title: str) -> str:
        """Standardize title."""
        if not title:
            return ''
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)
        return title
    
    def standardize_link(self, link: str) -> str:
        """Standardize URL."""
        if not link:
            return ''
        link = link.strip()
        if link and not link.startswith(('http://', 'https://')):
            self.warnings.append(f"Link missing protocol: {link}")
        return link
    
    def is_withdrawal(self, entry: Dict) -> bool:
        """Check if entry is marked as withdrawn."""
        for field in entry.values():
            if isinstance(field, str):
                if any(marker in field.lower() for marker in self.WITHDRAWAL_MARKERS):
                    return True
        return False
    
    def process_entries(self, entries: List[Dict]) -> None:
        """Process entries: standardize, handle corrections/withdrawals."""
        for row_num, entry in enumerate(entries, start=2):
            try:
                standardized = {
                    'date': self.standardize_date(entry.get('date', '')),
                    'title': self.standardize_title(entry.get('title', '')),
                    'object_number': self.standardize_object_number(
                        entry.get('object_number', '')
                    ),
                    'link': self.standardize_link(entry.get('link', '')),
                }
                
                if not standardized['object_number']:
                    self.errors.append(f"Row {row_num}: Missing object_number")
                    continue
                
                obj_num = standardized['object_number']
                
                # Compute checksum for standardized entry
                entry_checksum = self.checksum_mgr.compute_row_checksum(standardized)
                
                if self.keep_history:
                    if obj_num not in self.history:
                        self.history[obj_num] = []
                    self.history[obj_num].append(standardized)
                
                if self.is_withdrawal(standardized):
                    if obj_num in self.entries:
                        self.log(
                            f"Withdrawal: {obj_num} - {self.entries[obj_num]['title']}",
                            "INFO"
                        )
                    if obj_num in self.run_checksums['processed_entries']:
                        del self.run_checksums['processed_entries'][obj_num]
                    if obj_num in self.entries:
                        del self.entries[obj_num]
                else:
                    if obj_num in self.entries:
                        old_checksum = self.run_checksums['processed_entries'].get(obj_num)
                        if old_checksum != entry_checksum:
                            self.log(
                                f"Updated: {obj_num} - "
                                f"checksum {old_checksum[:8]}... -> {entry_checksum[:8]}...",
                                "INFO"
                            )
                    
                    self.entries[obj_num] = standardized
                    self.run_checksums['processed_entries'][obj_num] = entry_checksum
            
            except Exception as e:
                self.log(f"Error processing row {row_num}: {e}", "ERROR")
                self.errors.append(f"Row {row_num}: {e}")
    
    def validate_entries(self) -> None:
        """Validate processed entries."""
        for obj_num, entry in self.entries.items():
            for field in ['date', 'title', 'object_number']:
                if not entry.get(field, '').strip():
                    self.warnings.append(f"Object {obj_num}: Missing {field}")
            
            if entry.get('date') and not self._is_valid_date_format(entry['date']):
                self.warnings.append(
                    f"Object {obj_num}: Invalid date format: {entry['date']}"
                )
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """Check if date matches YYYY-MM-DD format."""
        return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', date_str))
    
    def write_output(self) -> None:
        """Write standardized entries to output TSV file."""
        if not self.entries:
            self.log("No entries to write", "WARNING")
            return
        
        try:
            sorted_entries = sorted(
                self.entries.values(),
                key=lambda x: x['object_number']
            )
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['date', 'title', 'object_number', 'link'],
                    delimiter='\t'
                )
                writer.writeheader()
                writer.writerows(sorted_entries)
            
            # Compute checksum for output file
            self.run_checksums['output_file'] = (
                self.checksum_mgr.compute_file_checksum(self.output_file)
            )
            
            self.log(
                f"Output written: {self.output_file} "
                f"({len(sorted_entries)} entries)",
                "INFO"
            )
        except Exception as e:
            self.log(f"Error writing output: {e}", "ERROR")
            raise
    
    def write_checksums(self) -> None:
        """Write checksums from this run to file."""
        try:
            # Store input file checksum
            self.run_checksums['input_file'] = (
                self.checksum_mgr.store_file_checksum(self.input_file)
            )
            
            # Store output file checksum if it exists
            if self.output_file.exists():
                self.run_checksums['output_file'] = (
                    self.checksum_mgr.store_file_checksum(self.output_file)
                )
            
            self.checksum_mgr.checksums.setdefault('runs', [])
            
            run_record = {
                'timestamp': datetime.now().isoformat(),
                'input_file': str(self.input_file),
                'output_file': str(self.output_file),
                'source_data_checksum': self.run_checksums['source_data'],
                'output_data_checksum': self.run_checksums['output_file'],
                'entries_processed': len(self.entries),
                'warnings': len(self.warnings),
                'errors': len(self.errors),
                'processed_entries': self.run_checksums['processed_entries'],
            }
            
            self.checksum_mgr.checksums['runs'].append(run_record)
            self.checksum_mgr.save_checksums()
            
            self.log(f"Checksums saved to {self.checksum_mgr.checksum_file}")
        
        except Exception as e:
            self.log(f"Error writing checksums: {e}", "ERROR")
    
    def print_checksum_report(self) -> None:
        """Print checksum verification report."""
        print("\n" + "="*70)
        print("CHECKSUM VERIFICATION REPORT")
        print("="*70)
        
        print(f"\nInput file checksum (SHA256):")
        print(f"  {self.run_checksums['input_file']}")
        
        print(f"\nSource data checksum (SHA256):")
        print(f"  {self.run_checksums['source_data']}")
        
        print(f"\nOutput file checksum (SHA256):")
        print(f"  {self.run_checksums['output_file']}")
        
        print(f"\nProcessed entries: {len(self.run_checksums['processed_entries'])}")
        
        print("\nEntry checksums (first 5):")
        for i, (obj_num, checksum) in enumerate(
            sorted(self.run_checksums['processed_entries'].items())[:5]
        ):
            print(f"  {obj_num}: {checksum[:16]}...")
        
        if len(self.run_checksums['processed_entries']) > 5:
            remaining = len(self.run_checksums['processed_entries']) - 5
            print(f"  ... and {remaining} more")
        
        print("\n" + "="*70 + "\n")
    
    def print_report(self) -> None:
        """Print standardization report."""
        print("\n" + "="*70)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("="*70)
        print(f"\nInput file: {self.input_file}")
        print(f"Output file: {self.output_file}")
        print(f"Log file: {self.log_file}")
        print(f"Checksum file: {self.checksum_mgr.checksum_file}")
        print(f"\nEntries processed: {len(self.entries)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Errors: {len(self.errors)}")
        
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings[:10]:
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        if self.errors:
            print("\nErrors:")
            for error in self.errors[:10]:
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        
        print("\n" + "="*70)
    
    def standardize(self) -> bool:
        """
        Main standardization process with checksum verification.
        
        Returns:
            True if successful, False if errors occurred
        """
        try:
            self.log(f"Starting standardization of {self.input_file}", "INFO")
            self.log_file.write_text("")
            
            # Verify input file hasn't changed
            if not self.verify_input_file():
                self.log("WARNING: Source data may have changed", "WARNING")
            
            # Read and process
            entries = self.read_input_with_checksums()
            self.log(
                f"Read {len(entries)} entries - "
                f"source checksum: {self.run_checksums['source_data'][:16]}...",
                "INFO"
            )
            
            self.process_entries(entries)
            self.validate_entries()
            self.write_output()
            self.write_checksums()
            
            self.print_report()
            self.print_checksum_report()
            
            return len(self.errors) == 0
        
        except Exception as e:
            self.log(f"Standardization failed: {e}", "ERROR")
            return False


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory with checksum verification"
    )
    parser.add_argument('input_file', help="Input TSV file")
    parser.add_argument('-o', '--output', help="Output TSV file")
    parser.add_argument('-l', '--log', help="Log file path")
    parser.add_argument('-c', '--checksums', help="Checksums file path")
    parser.add_argument(
        '--keep-history',
        action='store_true',
        help="Keep revision history"
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help="Verify source data hasn't changed"
    )
    
    args = parser.parse_args()
    
    standardizer = MuseumInventoryStandardizer(
        input_file=args.input_file,
        output_file=args.output,
        log_file=args.log,
        checksum_file=args.checksums,
        keep_history=args.keep_history,
        verify_checksums=args.verify,
    )
    
    success = standardizer.standardize()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Usage Examples

```bash
# First run - creates checksums
python standardize_inventory.py inventory.tsv

# Verify source data hasn't changed
python standardize_inventory.py inventory.tsv --verify

# Custom checksum file location
python standardize_inventory.py inventory.tsv -c .museum_checksums.json

# All options
python standardize_inventory.py inventory.tsv \
    -o output.tsv \
    -c checksums.json \
    --keep-history \
    --verify
```

## Checksum File Format

```json
{
  "version": 1,
  "files": {
    "inventory.tsv": {
      "checksum": "a1b2c3d4e5f6...",
      "algorithm": "sha256",
      "timestamp": "2024-01-15T10:30:45.123456",
      "size": 15234
    }
  },
  "runs": [
    {
      "timestamp": "2024-01-15T10:30:50.234567",
      "input_file": "inventory.tsv",
      "output_file": "inventory_standardized.tsv",
      "source_data_checksum": "abc123def456...",
      "output_data_checksum": "xyz789uvw012...",
      "entries_processed": 45,
      "warnings": 2,
      "errors": 0,
      "processed_entries": {
        "POT-001": "hash1...",
        "SCULPT-002": "hash2..."
      }
    }
  ]
}
```

## Key Features

- **File-level checksums**: Detect if source file has changed
- **Row-level checksums**: Track individual entry changes
- **Dataset checksums**: Verify entire source data integrity
- **Entry checksums**: Monitor standardized data changes
- **Run history**: Records all standardization runs
- **Change detection**: Alert when source data modified
- **Integrity verification**: Compare current vs. stored checksums
- **Multiple algorithms**: SHA256 (default), MD5, SHA1
- **Audit trail**: Complete history for compliance
