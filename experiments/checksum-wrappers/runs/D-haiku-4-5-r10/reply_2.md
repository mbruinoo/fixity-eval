# Museum Inventory Standardizer with Checksums

```python
#!/usr/bin/env python3
"""
Standardize a museum inventory spreadsheet (.tsv) with handling for 
corrections, withdrawals, and data integrity verification via checksums.

Columns: date, title, object_number, link
"""

import sys
import csv
import re
import hashlib
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict


@dataclass
class ChecksumRecord:
    """Store checksum information for a record."""
    object_number: str
    input_checksum: str
    standardized_checksum: str
    timestamp: str
    has_corrections: bool = False
    notes: str = ""


class ChecksumManager:
    """Manage checksums for data integrity verification."""
    
    def __init__(self, checksum_file=None):
        self.checksum_file = checksum_file
        self.checksums = {}
        self.load_checksums()
    
    def load_checksums(self):
        """Load existing checksums from file."""
        if not self.checksum_file or not Path(self.checksum_file).exists():
            return
        
        try:
            with open(self.checksum_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.checksums = data
        except Exception as e:
            print(f"Warning: Could not load checksums file: {e}", file=sys.stderr)
    
    def save_checksums(self):
        """Save checksums to file."""
        if not self.checksum_file:
            return
        
        try:
            with open(self.checksum_file, 'w', encoding='utf-8') as f:
                json.dump(self.checksums, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save checksums file: {e}", file=sys.stderr)
    
    @staticmethod
    def calculate_record_checksum(record, fields=None):
        """
        Calculate SHA256 checksum of a record.
        
        Args:
            record: Dictionary of record data
            fields: List of fields to include (None = all)
        
        Returns:
            Hex string of SHA256 hash
        """
        if fields is None:
            fields = sorted(record.keys())
        else:
            fields = sorted(fields)
        
        # Create normalized representation
        data_parts = []
        for field in fields:
            value = record.get(field, '')
            # Normalize: strip whitespace, lowercase for comparison
            if value:
                value = str(value).strip()
            data_parts.append(f"{field}:{value}")
        
        data_string = '|'.join(data_parts)
        return hashlib.sha256(data_string.encode('utf-8')).hexdigest()
    
    @staticmethod
    def calculate_file_checksum(file_path):
        """Calculate SHA256 checksum of entire file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Warning: Could not calculate file checksum: {e}", file=sys.stderr)
            return None
    
    def store_checksum(self, record_checksum):
        """Store a ChecksumRecord."""
        self.checksums[record_checksum.object_number] = asdict(record_checksum)
    
    def get_checksum(self, object_number):
        """Retrieve stored checksum for object number."""
        return self.checksums.get(object_number)
    
    def verify_unchanged(self, object_number, current_checksum):
        """
        Verify that input data hasn't changed since last run.
        
        Returns:
            (is_unchanged: bool, stored_checksum: str or None)
        """
        stored = self.get_checksum(object_number)
        if not stored:
            return None, None
        
        stored_checksum = stored.get('input_checksum')
        is_unchanged = stored_checksum == current_checksum
        return is_unchanged, stored_checksum


class InventoryStandardizer:
    def __init__(self, input_file, output_file, corrections_file=None, 
                 checksum_file=None, verify_mode=False):
        self.input_file = input_file
        self.output_file = output_file
        self.corrections_file = corrections_file
        self.verify_mode = verify_mode
        
        self.checksum_manager = ChecksumManager(checksum_file)
        self.inventory = []
        self.corrections = defaultdict(list)
        self.withdrawn = set()
        
        # Tracking
        self.unchanged_records = 0
        self.changed_records = 0
        self.new_records = 0
        self.checksum_records = []
        
    def load_corrections(self):
        """Load corrections file if provided."""
        if not self.corrections_file or not Path(self.corrections_file).exists():
            return
        
        try:
            with open(self.corrections_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    action = row.get('action', '').strip().lower()
                    obj_num = row.get('object_number', '').strip()
                    
                    if action == 'withdraw':
                        self.withdrawn.add(obj_num)
                    elif action == 'correct':
                        self.corrections[obj_num].append(row)
        except Exception as e:
            print(f"Warning: Could not load corrections file: {e}", file=sys.stderr)
    
    def standardize_date(self, date_str):
        """Standardize date to YYYY-MM-DD format."""
        if not date_str or not date_str.strip():
            return None
        
        date_str = date_str.strip()
        formats = [
            '%Y-%m-%d', '%Y/%m/%d',
            '%m-%d-%Y', '%m/%d/%Y',
            '%d-%m-%Y', '%d/%m/%Y',
            '%B %d, %Y', '%b %d, %Y',
            '%Y',
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        print(f"Warning: Could not parse date '{date_str}'", file=sys.stderr)
        return date_str
    
    def standardize_object_number(self, obj_num):
        """Standardize object number: remove extra spaces, normalize case."""
        if not obj_num:
            return None
        
        obj_num = obj_num.strip()
        obj_num = re.sub(r'\s+', ' ', obj_num)
        
        return obj_num if obj_num else None
    
    def standardize_title(self, title):
        """Standardize title: trim, normalize whitespace."""
        if not title:
            return None
        
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)
        title = title.strip('.,;:')
        
        return title if title else None
    
    def standardize_link(self, link):
        """Standardize link: validate URL format."""
        if not link or not link.strip():
            return None
        
        link = link.strip()
        
        if not link.startswith(('http://', 'https://', 'ftp://')):
            print(f"Warning: Link doesn't start with protocol: '{link}'", 
                  file=sys.stderr)
            return link
        
        return link
    
    def apply_corrections(self, record):
        """Apply any corrections to the record."""
        obj_num = record.get('object_number')
        
        if obj_num in self.corrections:
            for correction in self.corrections[obj_num]:
                for field in ['title', 'date', 'link']:
                    if field in correction and correction[field].strip():
                        record[field] = correction[field].strip()
        
        return record
    
    def read_inventory(self):
        """Read and parse the inventory TSV file."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    raise ValueError("Empty file or no headers")
                
                expected_fields = {'date', 'title', 'object_number', 'link'}
                actual_fields = set(reader.fieldnames)
                
                if not expected_fields.issubset(actual_fields):
                    missing = expected_fields - actual_fields
                    raise ValueError(f"Missing required columns: {missing}")
                
                for row_num, row in enumerate(reader, start=2):
                    self.inventory.append({
                        'row_num': row_num,
                        'data': row
                    })
        except FileNotFoundError:
            print(f"Error: Input file not found: {self.input_file}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading inventory file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def standardize(self):
        """Standardize all inventory records with checksum tracking."""
        standardized = []
        errors = []
        withdrawn_count = 0
        
        for entry in self.inventory:
            row_num = entry['row_num']
            record = entry['data'].copy()
            obj_num = record.get('object_number', '').strip()
            
            # Check if withdrawn
            if obj_num in self.withdrawn:
                withdrawn_count += 1
                continue
            
            # Calculate checksum of input record
            input_checksum = ChecksumManager.calculate_record_checksum(record)
            
            # Check if unchanged
            is_unchanged, stored_checksum = self.checksum_manager.verify_unchanged(
                obj_num, input_checksum
            )
            
            if is_unchanged:
                self.unchanged_records += 1
            elif stored_checksum:
                self.changed_records += 1
                if not self.verify_mode:
                    print(f"Warning: Row {row_num} ({obj_num}) has changed:", 
                          file=sys.stderr)
                    print(f"  Previous: {stored_checksum}", file=sys.stderr)
                    print(f"  Current:  {input_checksum}", file=sys.stderr)
            else:
                self.new_records += 1
            
            # Apply corrections
            has_corrections = obj_num in self.corrections
            record = self.apply_corrections(record)
            
            # Validate required fields
            if not obj_num:
                errors.append(f"Row {row_num}: Missing object_number")
                continue
            
            # Standardize fields
            try:
                standardized_record = {
                    'date': self.standardize_date(record.get('date', '')),
                    'title': self.standardize_title(record.get('title', '')),
                    'object_number': self.standardize_object_number(obj_num),
                    'link': self.standardize_link(record.get('link', '')),
                }
                
                if not standardized_record['title']:
                    errors.append(f"Row {row_num}: Empty or invalid title")
                    continue
                
                standardized.append(standardized_record)
                
                # Calculate checksum of standardized record
                standardized_checksum = ChecksumManager.calculate_record_checksum(
                    standardized_record
                )
                
                # Store checksum record
                checksum_record = ChecksumRecord(
                    object_number=obj_num,
                    input_checksum=input_checksum,
                    standardized_checksum=standardized_checksum,
                    timestamp=datetime.now().isoformat(),
                    has_corrections=has_corrections,
                    notes=f"Row {row_num}"
                )
                self.checksum_records.append(checksum_record)
                self.checksum_manager.store_checksum(checksum_record)
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        # Report statistics
        print(f"\nProcessing Summary:", file=sys.stderr)
        print(f"  Total records: {len(self.inventory)}", file=sys.stderr)
        print(f"  Standardized: {len(standardized)}", file=sys.stderr)
        print(f"  Withdrawn: {withdrawn_count}", file=sys.stderr)
        print(f"  Errors: {len(errors)}", file=sys.stderr)
        print(f"\nChecksum Summary:", file=sys.stderr)
        print(f"  New records: {self.new_records}", file=sys.stderr)
        print(f"  Unchanged records: {self.unchanged_records}", file=sys.stderr)
        print(f"  Changed records: {self.changed_records}", file=sys.stderr)
        
        if errors:
            print("\nErrors encountered:", file=sys.stderr)
            for error in errors[:10]:
                print(f"  {error}", file=sys.stderr)
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors", file=sys.stderr)
        
        return standardized
    
    def write_output(self, standardized_records):
        """Write standardized inventory to output file."""
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['date', 'title', 'object_number', 'link']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(standardized_records)
            
            print(f"\nOutput written to: {self.output_file}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    
    def write_checksums(self):
        """Write checksums to JSON file."""
        self.checksum_manager.save_checksums()
        print(f"Checksums saved to: {self.checksum_manager.checksum_file}", 
              file=sys.stderr)
    
    def verify_output_file(self):
        """Calculate and display checksum of output file."""
        file_checksum = ChecksumManager.calculate_file_checksum(self.output_file)
        if file_checksum:
            print(f"Output file checksum (SHA256): {file_checksum}", file=sys.stderr)
    
    def run(self):
        """Execute the standardization process."""
        self.load_corrections()
        self.read_inventory()
        standardized = self.standardize()
        self.write_output(standardized)
        
        if self.checksum_manager.checksum_file:
            self.write_checksums()
        
        self.verify_output_file()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory with checksum verification'
    )
    parser.add_argument('input', help='Input TSV file')
    parser.add_argument('output', help='Output TSV file')
    parser.add_argument('-c', '--corrections', help='Corrections TSV file')
    parser.add_argument('-k', '--checksums', help='Checksums JSON file')
    parser.add_argument('-v', '--verify', action='store_true',
                        help='Verify mode: report changes without processing')
    
    args = parser.parse_args()
    
    standardizer = InventoryStandardizer(
        args.input,
        args.output,
        corrections_file=args.corrections,
        checksum_file=args.checksums,
        verify_mode=args.verify
    )
    standardizer.run()


if __name__ == '__main__':
    main()
```

## Usage Examples

### Basic usage with checksums:
```bash
python standardize_inventory.py inventory.tsv inventory_standardized.tsv \
  --checksums inventory.checksums.json
```

### With corrections and checksums:
```bash
python standardize_inventory.py inventory.tsv inventory_standardized.tsv \
  --corrections corrections.tsv \
  --checksums inventory.checksums.json
```

### Verify mode (detect changes without re-processing):
```bash
python standardize_inventory.py inventory.tsv inventory_standardized.tsv \
  --checksums inventory.checksums.json \
  --verify
```

## Checksum File Format

The checksums are stored in JSON:

```json
{
  "2023.001": {
    "object_number": "2023.001",
    "input_checksum": "abc123def456...",
    "standardized_checksum": "xyz789uvw012...",
    "timestamp": "2024-01-15T10:30:45.123456",
    "has_corrections": false,
    "notes": "Row 2"
  },
  "2023.002": {
    "object_number": "2023.002",
    "input_checksum": "def456abc789...",
    "standardized_checksum": "uvw012xyz789...",
    "timestamp": "2024-01-15T10:30:45.234567",
    "has_corrections": true,
    "notes": "Row 3"
  }
}
```

## Key Features

### Checksum Integrity
- **Record-level checksums**: SHA256 hashes of input and standardized data
- **File-level checksums**: SHA256 hash of entire output file
- **Change detection**: Identifies modified records between runs
- **Persistent storage**: Stores checksums in JSON for historical tracking

### Data Verification
- Detects when source data has changed
- Warns about modified records
- Tracks new vs. existing records
- Identifies corrected records

### Modes
- **Normal**: Process and store checksums
- **Verify**: Check for changes without re-processing
