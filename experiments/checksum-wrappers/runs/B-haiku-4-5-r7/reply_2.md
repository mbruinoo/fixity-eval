# Museum Inventory Standardizer with Checksums

Here's an enhanced version incorporating checksums for data integrity verification:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksum Verification

Standardizes museum inventory records and uses checksums to:
- Verify source data hasn't been corrupted
- Detect unauthorized modifications
- Track changes over time
- Validate standardized output
"""

import sys
import csv
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse


class ChecksumManager:
    """Manages file and record checksums."""
    
    CHECKSUM_FILE_SUFFIX = '.checksums.json'
    HASH_ALGORITHM = 'sha256'
    
    @staticmethod
    def calculate_file_checksum(filepath: Path, algorithm: str = 'sha256') -> str:
        """Calculate checksum of entire file."""
        hash_obj = hashlib.new(algorithm)
        
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except IOError as e:
            raise IOError(f"Error calculating file checksum: {str(e)}")
    
    @staticmethod
    def calculate_record_checksum(record: Dict, algorithm: str = 'sha256') -> str:
        """
        Calculate checksum of a record.
        
        Uses canonical JSON to ensure consistent hashing regardless of field order.
        """
        hash_obj = hashlib.new(algorithm)
        
        # Sort keys for consistent ordering
        canonical_json = json.dumps(record, sort_keys=True, separators=(',', ':'))
        hash_obj.update(canonical_json.encode('utf-8'))
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def calculate_field_checksum(value: str, algorithm: str = 'sha256') -> str:
        """Calculate checksum of a single field value."""
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(str(value).encode('utf-8'))
        return hash_obj.hexdigest()


class ChecksumStorage:
    """Stores and manages checksums."""
    
    def __init__(self, checksum_file: Path):
        """Initialize checksum storage."""
        self.checksum_file = checksum_file
        self.data = self._load()
    
    def _load(self) -> Dict:
        """Load checksums from file if it exists."""
        if self.checksum_file.exists():
            try:
                with open(self.checksum_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._initialize_structure()
        return self._initialize_structure()
    
    @staticmethod
    def _initialize_structure() -> Dict:
        """Initialize checksum storage structure."""
        return {
            'file_checksums': {},
            'record_checksums': {},
            'field_checksums': {},
            'metadata': {
                'created': datetime.now().isoformat(),
                'last_updated': None,
                'version': '1.0'
            }
        }
    
    def save(self) -> None:
        """Save checksums to file."""
        self.data['metadata']['last_updated'] = datetime.now().isoformat()
        
        try:
            with open(self.checksum_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            raise IOError(f"Error saving checksums: {str(e)}")
    
    def set_file_checksum(self, filename: str, checksum: str, 
                         timestamp: str = None) -> None:
        """Store file checksum."""
        if filename not in self.data['file_checksums']:
            self.data['file_checksums'][filename] = []
        
        self.data['file_checksums'][filename].append({
            'checksum': checksum,
            'timestamp': timestamp or datetime.now().isoformat()
        })
    
    def get_file_checksum(self, filename: str) -> str:
        """Get most recent file checksum."""
        if filename in self.data['file_checksums']:
            checksums = self.data['file_checksums'][filename]
            if checksums:
                return checksums[-1]['checksum']
        return None
    
    def get_file_checksum_history(self, filename: str) -> List[Dict]:
        """Get all file checksums for a file."""
        return self.data['file_checksums'].get(filename, [])
    
    def set_record_checksum(self, record_id: str, checksum: str, 
                           original: bool = True) -> None:
        """Store record checksum."""
        key = 'original' if original else 'standardized'
        
        if record_id not in self.data['record_checksums']:
            self.data['record_checksums'][record_id] = {}
        
        self.data['record_checksums'][record_id][key] = {
            'checksum': checksum,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_record_checksum(self, record_id: str, original: bool = True) -> str:
        """Get record checksum."""
        key = 'original' if original else 'standardized'
        
        if record_id in self.data['record_checksums']:
            if key in self.data['record_checksums'][record_id]:
                return self.data['record_checksums'][record_id][key]['checksum']
        return None
    
    def verify_record_integrity(self, record_id: str, original: bool = True) -> bool:
        """Check if record checksum exists."""
        return self.get_record_checksum(record_id, original) is not None


class MuseumInventoryStandardizer:
    """Standardizes museum inventory records with checksum verification."""
    
    REQUIRED_FIELDS = ['date', 'title', 'object_number', 'link']
    DATE_FORMATS = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%B %d, %Y',
        '%b %d, %Y',
        '%Y',
    ]
    
    def __init__(self, input_file: str, output_file: str = None, 
                 checksum_file: str = None, verbose: bool = False,
                 verify_checksums: bool = True):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file
            checksum_file: Path to checksum storage file
            verbose: Print detailed processing information
            verify_checksums: Verify source data hasn't changed
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else \
                          self.input_file.parent / f"{self.input_file.stem}_standardized.tsv"
        
        # Initialize checksum management
        if checksum_file is None:
            checksum_file = self.input_file.parent / \
                           f"{self.input_file.stem}{ChecksumManager.CHECKSUM_FILE_SUFFIX}"
        self.checksum_file = Path(checksum_file)
        self.checksum_storage = ChecksumStorage(self.checksum_file)
        
        self.verify_checksums = verify_checksums
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.records_processed = 0
        self.records_successful = 0
        self.integrity_warnings = []
    
    def log(self, message: str, level: str = "INFO"):
        """Print log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def verify_source_integrity(self) -> Tuple[bool, str]:
        """
        Verify that source file hasn't been modified.
        
        Returns:
            Tuple of (is_valid, message)
        """
        current_checksum = ChecksumManager.calculate_file_checksum(self.input_file)
        previous_checksum = self.checksum_storage.get_file_checksum(self.input_file.name)
        
        if previous_checksum is None:
            msg = "First time processing this file - no previous checksum to compare"
            self.log(msg, "INFO")
            return True, msg
        
        if current_checksum == previous_checksum:
            msg = "✓ Source file integrity verified - no changes detected"
            self.log(msg, "INFO")
            return True, msg
        else:
            msg = f"✗ WARNING: Source file has been modified since last processing\n" \
                  f"  Previous checksum: {previous_checksum}\n" \
                  f"  Current checksum:  {current_checksum}"
            self.integrity_warnings.append(msg)
            self.log(msg, "WARNING")
            return False, msg
    
    def standardize_date(self, date_str: str) -> Tuple[str, bool]:
        """Standardize date to YYYY-MM-DD format."""
        if not date_str or not date_str.strip():
            return "", False
        
        date_str = date_str.strip()
        
        for fmt in self.DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d'), True
            except ValueError:
                continue
        
        self.warnings.append(f"Could not parse date: '{date_str}'")
        return date_str, False
    
    def standardize_title(self, title: str) -> str:
        """Standardize title formatting."""
        if not title:
            return ""
        
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)
        return title
    
    def standardize_object_number(self, obj_num: str) -> str:
        """Standardize object number formatting."""
        if not obj_num:
            return ""
        
        obj_num = obj_num.strip().upper()
        obj_num = re.sub(r'\s*([.\-])\s*', r'\1', obj_num)
        return obj_num
    
    def validate_url(self, url: str) -> Tuple[str, bool]:
        """Validate and standardize URL."""
        if not url or not url.strip():
            return "", False
        
        url = url.strip()
        
        try:
            result = urlparse(url)
            if not result.scheme:
                url = 'https://' + url
                result = urlparse(url)
            
            if result.scheme and result.netloc:
                return url, True
            else:
                return url, False
        except Exception as e:
            self.warnings.append(f"Error validating URL '{url}': {str(e)}")
            return url, False
    
    def validate_record(self, record: Dict) -> Tuple[bool, List[str]]:
        """Validate a record has all required fields."""
        errors = []
        
        for field in self.REQUIRED_FIELDS:
            if field not in record:
                errors.append(f"Missing required field: {field}")
            elif not record[field] or not str(record[field]).strip():
                errors.append(f"Empty required field: {field}")
        
        return len(errors) == 0, errors
    
    def standardize_record(self, record: Dict) -> Tuple[Dict, List[str]]:
        """Standardize a single record."""
        errors = []
        standardized = record.copy()
        
        if 'date' in record:
            standardized_date, success = self.standardize_date(record['date'])
            standardized['date'] = standardized_date
            if not success and standardized_date:
                self.log(f"Date parsed with uncertainty: {record['date']} -> {standardized_date}", 
                        "WARNING")
        
        if 'title' in record:
            standardized['title'] = self.standardize_title(record['title'])
        
        if 'object_number' in record:
            standardized['object_number'] = self.standardize_object_number(
                record['object_number']
            )
        
        if 'link' in record:
            url, valid = self.validate_url(record['link'])
            standardized['link'] = url
            if not valid:
                errors.append(f"Invalid URL: {record['link']}")
        
        return standardized, errors
    
    def read_input_file(self) -> List[Tuple[int, Dict]]:
        """Read and parse the input TSV file."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        records = []
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    raise ValueError("TSV file is empty or has no headers")
                
                missing_fields = set(self.REQUIRED_FIELDS) - set(reader.fieldnames)
                if missing_fields:
                    raise ValueError(f"Missing required columns: {missing_fields}")
                
                for i, row in enumerate(reader, start=2):
                    records.append((i, row))
            
            self.log(f"Read {len(records)} records from input file")
            return records
        
        except csv.Error as e:
            raise ValueError(f"Error parsing TSV file: {str(e)}")
    
    def process_records(self, records: List[Tuple[int, Dict]]) -> List[Dict]:
        """Process and standardize all records with checksum tracking."""
        standardized_records = []
        
        for line_num, record in records:
            self.records_processed += 1
            
            # Generate record ID
            record_id = f"{self.input_file.stem}:line_{line_num}"
            
            # Calculate original record checksum
            original_checksum = ChecksumManager.calculate_record_checksum(record)
            self.checksum_storage.set_record_checksum(record_id, original_checksum, original=True)
            
            # Verify integrity if checksums exist from previous run
            if self.verify_checksums:
                previous_checksum = self.checksum_storage.get_record_checksum(record_id, original=True)
                if previous_checksum and previous_checksum != original_checksum:
                    self.integrity_warnings.append(
                        f"Record {record_id} has changed since last standardization"
                    )
                    self.log(f"Record {record_id}: Data has been modified", "WARNING")
            
            # Validate record
            is_valid, validation_errors = self.validate_record(record)
            if not is_valid:
                for error in validation_errors:
                    self.errors.append(f"Line {line_num}: {error}")
                self.log(f"Line {line_num}: Validation failed - {validation_errors}", "ERROR")
                continue
            
            # Standardize record
            standardized, standardize_errors = self.standardize_record(record)
            
            if standardize_errors:
                for error in standardize_errors:
                    self.errors.append(f"Line {line_num}: {error}")
                self.log(f"Line {line_num}: {standardize_errors}", "ERROR")
            
            # Calculate standardized record checksum
            standardized_checksum = ChecksumManager.calculate_record_checksum(standardized)
            self.checksum_storage.set_record_checksum(record_id, standardized_checksum, original=False)
            
            standardized_records.append(standardized)
            self.records_successful += 1
            
            self.log(f"Record {record_id}: {original_checksum[:8]}... → {standardized_checksum[:8]}...")
        
        self.log(f"Successfully standardized {self.records_successful}/{self.records_processed} records")
        return standardized_records
    
    def write_output_file(self, records: List[Dict]) -> None:
        """Write standardized records to output TSV file."""
        if not records:
            self.log("No records to write", "WARNING")
            return
        
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f, 
                    fieldnames=self.REQUIRED_FIELDS,
                    delimiter='\t',
                    extrasaction='ignore'
                )
                writer.writeheader()
                writer.writerows(records)
            
            # Calculate and store output file checksum
            output_checksum = ChecksumManager.calculate_file_checksum(self.output_file)
            self.checksum_storage.set_file_checksum(self.output_file.name, output_checksum)
            
            self.log(f"Wrote {len(records)} standardized records to {self.output_file}")
            self.log(f"Output file checksum: {output_checksum}")
        
        except IOError as e:
            raise IOError(f"Error writing output file: {str(e)}")
    
    def print_report(self) -> None:
        """Print processing report with checksum information."""
        print("\n" + "="*70)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("="*70)
        
        print(f"\nFILE INFORMATION:")
        print(f"  Input file: {self.input_file}")
        print(f"  Output file: {self.output_file}")
        print(f"  Checksum file: {self.checksum_file}")
        
        # Checksum information
        input_checksum = ChecksumManager.calculate_file_checksum(self.input_file)
        print(f"\nCHECKSUM VERIFICATION:")
        print(f"  Current input checksum: {input_checksum}")
        
        history = self.checksum_storage.get_file_checksum_history(self.input_file.name)
        if len(history) > 1:
            print(f"  Previous checksums ({len(history)-1} prior run{'s' if len(history) > 2 else ''}):")
            for i, entry in enumerate(history[:-1]):
                print(f"    - {entry['checksum'][:16]}... ({entry['timestamp']})")
        
        print(f"\nPROCESSING RESULTS:")
        print(f"  Records processed: {self.records_processed}")
        print(f"  Records successful: {self.records_successful}")
        print(f"  Success rate: {self.records_successful/self.records_processed*100:.1f}%" 
              if self.records_processed > 0 else "N/A")
        
        if self.integrity_warnings:
            print(f"\nINTEGRITY WARNINGS ({len(self.integrity_warnings)}):")
            for warning in self.integrity_warnings[:5]:
                print(f"  ⚠ {warning}")
            if len(self.integrity_warnings) > 5:
                print(f"  ... and {len(self.integrity_warnings) - 5} more")
        
        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        if self.errors:
            print(f"\nERRORS ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        else:
            print("\nNo errors encountered!")
        
        print("="*70 + "\n")
    
    def standardize(self) -> bool:
        """Run the standardization process."""
        try:
            self.log("Starting standardization process...")
            
            # Verify source file integrity
            if self.verify_checksums:
                file_valid, msg = self.verify_source_integrity()
            
            # Read input
            records = self.read_input_file()
            
            # Process records
            standardized = self.process_records(records)
            
            # Write output
            self.write_output_file(standardized)
            
            # Save checksums
            self.log("Saving checksums...")
            input_checksum = ChecksumManager.calculate_file_checksum(self.input_file)
            self.checksum_storage.set_file_checksum(self.input_file.name, input_checksum)
            self.checksum_storage.save()
            self.log(f"Checksums saved to {self.checksum_file}")
            
            # Print report
            self.print_report()
            
            return self.records_successful == self.records_processed
        
        except Exception as e:
            print(f"FATAL ERROR: {str(e)}", file=sys.stderr)
            return False


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records with checksum verification'
    )
    parser.add_argument('input_file', help='Path to input TSV file')
    parser.add_argument('-o', '--output', help='Path to output TSV file')
    parser.add_argument('-c', '--checksums', help='Path to checksum storage file')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Print detailed processing information')
    parser.add_argument('--skip-verify', action='store_true',
                       help='Skip integrity verification of source data')
    
    args = parser.parse_args()
    
    standardizer = MuseumInventoryStandardizer(
        args.input_file,
        args.output,
        args.checksums,
        args.verbose,
        verify_checksums=not args.skip_verify
    )
    
    success = standardizer.standardize()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Usage Examples

### First run (establishes baseline checksums):
```bash
python standardizer.py inventory.tsv -v
```

### Subsequent runs (verifies data hasn't changed):
```bash
python standardizer.py inventory.tsv -v
```

### Skip verification if you know data changed legitimately:
```bash
python standardizer.py inventory.tsv --skip-verify
```

### Custom checksum location:
```bash
python standardizer.py inventory.tsv -c checksums/inventory.json
```

## Key Checksum Features

1. **File-level checksums**: Detects modifications to entire source file
2. **Record-level checksums**: Tracks changes to individual records
3. **Historical tracking**: Maintains history of all checksums
4. **Before/after comparison**: Stores both original and standardized checksums
5. **Integrity warnings**: Alerts when source data has been modified
6. **JSON storage**: Human-readable checksum database with timestamps

## Example Checksum File

```json
{
  "file_checksums": {
    "inventory.tsv": [
      {
        "checksum": "abc123def456...",
        "timestamp": "2024-01-15T10:30:00"
      },
      {
        "checksum": "xyz789uvw012...",
        "timestamp": "2024-01-16T09:15:00"
      }
    ]
  },
  "record_checksums": {
    "inventory:line_2": {
      "original": {
        "checksum": "hash1...",
        "timestamp": "2024-01-15T10:30:00"
      },
      "standardized": {
        "checksum": "hash2...",
        "timestamp": "2024-01-15T10:30:00"
      }
    }
  },
  "metadata": {
    "created": "2024-01-15T10:30:00",
    "last_updated": "2024-01-16T09:15:00",
    "version": "1.0"
  }
}
```

This approach ensures data integrity while tracking standardization changes!
