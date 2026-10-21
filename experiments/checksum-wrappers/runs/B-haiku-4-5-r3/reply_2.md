# Museum Inventory Standardization with Checksums

```python
#!/usr/bin/env python3
"""
Script to standardize museum inventory records with checksum verification.

Incorporates MD5 and SHA256 checksums to detect changes to source data.
"""

import argparse
import csv
import sys
import hashlib
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import re


class ChecksumManager:
    """Manages checksums for inventory files and records."""
    
    @staticmethod
    def calculate_file_checksum(filepath, algorithm='sha256'):
        """
        Calculate checksum of entire file.
        
        Args:
            filepath: Path to file
            algorithm: 'md5' or 'sha256'
            
        Returns:
            Hex digest of checksum
        """
        if algorithm == 'md5':
            hasher = hashlib.md5()
        else:
            hasher = hashlib.sha256()
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    @staticmethod
    def calculate_record_checksum(record, algorithm='sha256'):
        """
        Calculate checksum of a single record.
        
        Creates deterministic JSON representation for consistent hashing.
        
        Args:
            record: Dictionary of record data
            algorithm: 'md5' or 'sha256'
            
        Returns:
            Hex digest of checksum
        """
        # Sort keys for deterministic JSON
        record_json = json.dumps(record, sort_keys=True, separators=(',', ':'))
        record_bytes = record_json.encode('utf-8')
        
        if algorithm == 'md5':
            hasher = hashlib.md5()
        else:
            hasher = hashlib.sha256()
        
        hasher.update(record_bytes)
        return hasher.hexdigest()
    
    @staticmethod
    def calculate_field_checksum(field_value, algorithm='sha256'):
        """
        Calculate checksum of a single field value.
        
        Args:
            field_value: Field value as string
            algorithm: 'md5' or 'sha256'
            
        Returns:
            Hex digest of checksum
        """
        field_bytes = str(field_value).encode('utf-8')
        
        if algorithm == 'md5':
            hasher = hashlib.md5()
        else:
            hasher = hashlib.sha256()
        
        hasher.update(field_bytes)
        return hasher.hexdigest()


class InventoryStandardizer:
    """Standardizes museum inventory records with checksum verification."""
    
    def __init__(self, object_prefix="OBJ", track_checksums=True):
        self.object_prefix = object_prefix
        self.track_checksums = track_checksums
        self.errors = []
        self.warnings = []
        self.checksum_log = {
            'file': {},
            'records': {}
        }
    
    def standardize_date(self, date_str):
        """Standardize date to ISO 8601 format (YYYY-MM-DD)."""
        if not date_str or date_str.strip() == "":
            self.warnings.append("Empty date field")
            return ""
        
        date_str = date_str.strip()
        
        formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d",
            "%B %d, %Y", "%b %d, %Y", "%Y", "%m-%d-%Y",
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        self.errors.append(f"Could not parse date: {date_str}")
        return date_str
    
    def standardize_title(self, title):
        """Standardize title to Title Case."""
        if not title or title.strip() == "":
            self.warnings.append("Empty title field")
            return ""
        
        title = title.strip()
        lowercase_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for',
                          'if', 'in', 'of', 'on', 'or', 'the', 'to', 'with'}
        
        words = title.split()
        standardized = []
        
        for i, word in enumerate(words):
            if i == 0 or i == len(words) - 1:
                standardized.append(word.capitalize())
            elif word.lower() in lowercase_words:
                standardized.append(word.lower())
            else:
                standardized.append(word.capitalize())
        
        return " ".join(standardized)
    
    def standardize_object_number(self, obj_num):
        """Standardize object number format."""
        if not obj_num or obj_num.strip() == "":
            self.errors.append("Empty object number")
            return ""
        
        obj_num = obj_num.strip().upper().replace(" ", "")
        
        if not obj_num.startswith(self.object_prefix):
            obj_num = f"{self.object_prefix}.{obj_num}"
        
        match = re.match(r"([A-Z]+)\.?(\d+)", obj_num)
        if match:
            prefix, number = match.groups()
            obj_num = f"{prefix}.{number.zfill(6)}"
        else:
            self.errors.append(f"Invalid object number format: {obj_num}")
        
        return obj_num
    
    def standardize_link(self, link):
        """Standardize and validate URL."""
        if not link or link.strip() == "":
            return ""
        
        link = link.strip()
        
        if not link.startswith(("http://", "https://")):
            link = f"https://{link}"
        
        try:
            result = urlparse(link)
            if not all([result.scheme, result.netloc]):
                self.errors.append(f"Invalid URL: {link}")
                return link
        except Exception as e:
            self.errors.append(f"Error parsing URL {link}: {str(e)}")
            return link
        
        return link
    
    def standardize_record(self, record, row_num=None):
        """
        Standardize a single record with checksum tracking.
        
        Args:
            record: Dictionary with keys: date, title, object_number, link
            row_num: Row number for tracking
            
        Returns:
            Tuple of (standardized_record, checksums)
        """
        self.errors = []
        self.warnings = []
        
        checksums = {}
        
        # Calculate source checksums if tracking
        if self.track_checksums:
            checksums['source'] = {}
            for field, value in record.items():
                checksums['source'][field] = ChecksumManager.calculate_field_checksum(value)
        
        standardized = {
            'date': self.standardize_date(record.get('date', '')),
            'title': self.standardize_title(record.get('title', '')),
            'object_number': self.standardize_object_number(record.get('object_number', '')),
            'link': self.standardize_link(record.get('link', '')),
        }
        
        # Calculate standardized checksums if tracking
        if self.track_checksums:
            checksums['standardized'] = {}
            for field, value in standardized.items():
                checksums['standardized'][field] = ChecksumManager.calculate_field_checksum(value)
            
            checksums['record_source'] = ChecksumManager.calculate_record_checksum(record)
            checksums['record_standardized'] = ChecksumManager.calculate_record_checksum(standardized)
        
        return standardized, checksums
    
    def process_file(self, input_file, output_file, checksum_file=None):
        """
        Process entire inventory file with checksum verification.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file
            checksum_file: Path to store checksums (optional)
            
        Returns:
            Tuple of (success_count, error_count, warning_count)
        """
        success_count = 0
        error_count = 0
        warning_count = 0
        all_warnings = []
        all_errors = []
        
        try:
            # Calculate source file checksum
            if self.track_checksums:
                source_checksum = ChecksumManager.calculate_file_checksum(input_file)
                self.checksum_log['file']['source'] = {
                    'path': str(input_file),
                    'checksum': source_checksum,
                    'algorithm': 'sha256',
                    'timestamp': datetime.now().isoformat()
                }
            
            with open(input_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile, delimiter='\t')
                
                if not reader.fieldnames:
                    print("Error: Empty file or invalid TSV format", file=sys.stderr)
                    return 0, 1, 0
                
                required_fields = {'date', 'title', 'object_number', 'link'}
                if not required_fields.issubset(set(reader.fieldnames)):
                    print(f"Error: Missing required fields. Need: {required_fields}",
                          file=sys.stderr)
                    return 0, 1, 0
                
                records = list(reader)
            
            standardized_records = []
            for row_num, record in enumerate(records, start=2):
                self.errors = []
                self.warnings = []
                
                standardized, checksums = self.standardize_record(record, row_num)
                
                # Store checksums
                if self.track_checksums:
                    record_key = f"row_{row_num}"
                    self.checksum_log['records'][record_key] = checksums
                
                if self.errors:
                    error_count += len(self.errors)
                    for error in self.errors:
                        all_errors.append(f"Row {row_num}: {error}")
                
                if self.warnings:
                    warning_count += len(self.warnings)
                    for warning in self.warnings:
                        all_warnings.append(f"Row {row_num}: {warning}")
                
                if not self.errors:
                    success_count += 1
                
                standardized_records.append(standardized)
            
            # Write standardized records
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                fieldnames = ['date', 'title', 'object_number', 'link']
                writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(standardized_records)
            
            # Calculate output file checksum
            if self.track_checksums:
                output_checksum = ChecksumManager.calculate_file_checksum(output_file)
                self.checksum_log['file']['output'] = {
                    'path': str(output_file),
                    'checksum': output_checksum,
                    'algorithm': 'sha256',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Save checksum log if requested
            if checksum_file and self.track_checksums:
                self._save_checksum_log(checksum_file)
            
            # Print summary
            self._print_summary(output_file, success_count, error_count, 
                              warning_count, all_errors, all_warnings)
            
            return success_count, error_count, warning_count
        
        except FileNotFoundError:
            print(f"Error: Input file not found: {input_file}", file=sys.stderr)
            return 0, 1, 0
        except Exception as e:
            print(f"Error processing file: {str(e)}", file=sys.stderr)
            return 0, 1, 0
    
    def _save_checksum_log(self, checksum_file):
        """Save checksum log to JSON file."""
        try:
            with open(checksum_file, 'w', encoding='utf-8') as f:
                json.dump(self.checksum_log, f, indent=2)
            print(f"Checksum log saved to: {checksum_file}")
        except Exception as e:
            print(f"Warning: Could not save checksum log: {str(e)}", file=sys.stderr)
    
    def verify_checksums(self, checksum_file, input_file):
        """
        Verify that source data matches recorded checksums.
        
        Args:
            checksum_file: Path to checksum log JSON
            input_file: Path to input file to verify
            
        Returns:
            Tuple of (is_valid, messages)
        """
        try:
            with open(checksum_file, 'r', encoding='utf-8') as f:
                stored_log = json.load(f)
            
            messages = []
            is_valid = True
            
            # Verify file checksum
            if 'source' in stored_log.get('file', {}):
                stored_checksum = stored_log['file']['source']['checksum']
                current_checksum = ChecksumManager.calculate_file_checksum(input_file)
                
                if stored_checksum == current_checksum:
                    messages.append(f"✓ File checksum verified: {current_checksum}")
                else:
                    messages.append(f"✗ File checksum mismatch!")
                    messages.append(f"  Stored:  {stored_checksum}")
                    messages.append(f"  Current: {current_checksum}")
                    is_valid = False
            
            return is_valid, messages
        
        except FileNotFoundError:
            return False, [f"Checksum file not found: {checksum_file}"]
        except Exception as e:
            return False, [f"Error verifying checksums: {str(e)}"]
    
    def _print_summary(self, output_file, success_count, error_count, 
                      warning_count, all_errors, all_warnings):
        """Print processing summary."""
        print(f"\n{'='*60}")
        print(f"Standardization Complete")
        print(f"{'='*60}")
        print(f"Records standardized successfully: {success_count}")
        print(f"Errors: {error_count}")
        print(f"Warnings: {warning_count}")
        print(f"Output file: {output_file}")
        
        if self.track_checksums and 'source' in self.checksum_log['file']:
            print(f"\nFile Checksums:")
            print(f"  Source:  {self.checksum_log['file']['source']['checksum']}")
            if 'output' in self.checksum_log['file']:
                print(f"  Output:  {self.checksum_log['file']['output']['checksum']}")
        
        if all_errors:
            print(f"\n{'='*60}")
            print("ERRORS:")
            for error in all_errors[:10]:
                print(f"  {error}")
            if len(all_errors) > 10:
                print(f"  ... and {len(all_errors) - 10} more")
        
        if all_warnings:
            print(f"\n{'='*60}")
            print("WARNINGS:")
            for warning in all_warnings[:10]:
                print(f"  {warning}")
            if len(all_warnings) > 10:
                print(f"  ... and {len(all_warnings) - 10} more")


def create_sample_file():
    """Create a sample TSV file for testing."""
    sample_data = [
        ["date", "title", "object_number", "link"],
        ["01/15/2020", "portrait of lady", "OBJ 001", "www.example.com/obj001"],
        ["2021-03-22", "ANCIENT VASE", "002", "https://museum.org/vase"],
        ["March 10, 2019", "the great painting", "OBJ003", "museum.org/painting"],
    ]
    
    with open("sample_inventory.tsv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(sample_data)
    
    print("Sample file created: sample_inventory.tsv")


def main():
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory records with checksum verification"
    )
    parser.add_argument(
        "input_file",
        help="Input TSV file with inventory records"
    )
    parser.add_argument(
        "-o", "--output",
        default="standardized_inventory.tsv",
        help="Output file for standardized records"
    )
    parser.add_argument(
        "-c", "--checksums",
        help="JSON file to store/verify checksums"
    )
    parser.add_argument(
        "-p", "--prefix",
        default="OBJ",
        help="Object number prefix (default: OBJ)"
    )
    parser.add_argument(
        "--verify",
        nargs=2,
        metavar=("CHECKSUM_FILE", "INPUT_FILE"),
        help="Verify that input file matches stored checksums"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Create a sample inventory file and exit"
    )
    
    args = parser.parse_args()
    
    if args.sample:
        create_sample_file()
        return
    
    # Verify mode
    if args.verify:
        checksum_file, input_file = args.verify
        standardizer = InventoryStandardizer(object_prefix=args.prefix)
        is_valid, messages = standardizer.verify_checksums(checksum_file, input_file)
        
        for msg in messages:
            print(msg)
        
        sys.exit(0 if is_valid else 1)
    
    # Normal processing mode
    if not Path(args.input_file).exists():
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    
    standardizer = InventoryStandardizer(object_prefix=args.prefix, track_checksums=True)
    success, errors, warnings = standardizer.process_file(
        args.input_file,
        args.output,
        checksum_file=args.checksums
    )
    
    sys.exit(0 if errors == 0 else 1)


if __name__ == "__main__":
    main()
```

## Usage Examples

### Process file and save checksums:
```bash
python standardize_inventory.py inventory.tsv -c checksums.json
```

### Verify source file hasn't changed:
```bash
python standardize_inventory.py --verify checksums.json inventory.tsv
```

### Process without checksums:
```bash
python standardize_inventory.py inventory.tsv --no-checksums
```

## Sample Checksum Log Output

```json
{
  "file": {
    "source": {
      "path": "inventory.tsv",
      "checksum": "a1b2c3d4...",
      "algorithm": "sha256",
      "timestamp": "2024-01-15T10:30:45.123456"
    },
    "output": {
      "path": "standardized_inventory.tsv",
      "checksum": "e5f6g7h8...",
      "algorithm": "sha256",
      "timestamp": "2024-01-15T10:30:46.234567"
    }
  },
  "records": {
    "row_2": {
      "source": {
        "date": "abc123...",
        "title": "def456...",
        "object_number": "ghi789...",
        "link": "jkl012..."
      },
      "standardized": {
        "date": "xyz987...",
        "title": "uvw654...",
        "object_number": "rst321...",
        "link": "qpo789..."
      },
      "record_source": "source_hash_here",
      "record_standardized": "standardized_hash_here"
    }
  }
}
```

## Key Features

- **File-level checksums**: SHA256 of entire source and output files
- **Field-level checksums**: Individual checksums for each field (source and standardized)
- **Record-level checksums**: Complete record hashes for integrity verification
- **Verification mode**: Check if source file matches stored checksums
- **Audit trail**: Timestamps and algorithm information stored
- **Detect changes**: Quickly identify if data was modified or corrupted
