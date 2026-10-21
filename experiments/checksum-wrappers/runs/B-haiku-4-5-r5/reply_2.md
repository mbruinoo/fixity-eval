# Museum Inventory Standardization Script with Checksums

```python
#!/usr/bin/env python3
"""
Script to standardize museum inventory records from a TSV file.

Includes checksum verification to detect changes in source data.
"""

import csv
import re
import sys
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ChecksumManager:
    """Manages checksums for source data integrity verification."""
    
    def __init__(self, checksum_file: Path):
        """
        Initialize checksum manager.
        
        Args:
            checksum_file: Path to store/load checksums
        """
        self.checksum_file = checksum_file
        self.checksums = {}
        self.load_checksums()
    
    def load_checksums(self):
        """Load previously stored checksums from file."""
        if self.checksum_file.exists():
            try:
                with open(self.checksum_file, 'r', encoding='utf-8') as f:
                    self.checksums = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load checksums: {e}", file=sys.stderr)
                self.checksums = {}
    
    def save_checksums(self):
        """Save checksums to file."""
        try:
            with open(self.checksum_file, 'w', encoding='utf-8') as f:
                json.dump(self.checksums, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save checksums: {e}", file=sys.stderr)
    
    def calculate_file_checksum(self, file_path: Path, algorithm: str = 'sha256') -> str:
        """
        Calculate checksum of entire file.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm ('md5', 'sha1', 'sha256', 'sha512')
            
        Returns:
            Hex digest of file hash
        """
        hash_obj = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            raise Exception(f"Error calculating file checksum: {e}")
    
    def calculate_record_checksum(self, record: Dict, algorithm: str = 'sha256') -> str:
        """
        Calculate checksum of a single record.
        
        Args:
            record: Record dictionary
            algorithm: Hash algorithm
            
        Returns:
            Hex digest of record hash
        """
        # Sort keys for consistent hashing
        record_str = json.dumps(record, sort_keys=True, separators=(',', ':'))
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(record_str.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def verify_file_integrity(self, file_path: Path, source_name: str) -> Tuple[bool, Optional[str]]:
        """
        Verify if file has changed since last run.
        
        Args:
            file_path: Path to file
            source_name: Identifier for this source
            
        Returns:
            (is_unchanged, message)
        """
        current_checksum = self.calculate_file_checksum(file_path)
        previous_checksum = self.checksums.get(source_name, {}).get('file_checksum')
        
        if previous_checksum is None:
            return True, f"First run - storing baseline checksum"
        
        if current_checksum == previous_checksum:
            return True, f"File unchanged (checksum verified)"
        else:
            return False, f"File has changed since last run"
    
    def store_file_checksum(self, file_path: Path, source_name: str, metadata: Dict = None):
        """
        Store checksum for future verification.
        
        Args:
            file_path: Path to file
            source_name: Identifier for this source
            metadata: Optional metadata to store with checksum
        """
        checksum = self.calculate_file_checksum(file_path)
        
        self.checksums[source_name] = {
            'file_checksum': checksum,
            'timestamp': datetime.now().isoformat(),
            'file_name': file_path.name,
            'file_size': file_path.stat().st_size,
        }
        
        if metadata:
            self.checksums[source_name]['metadata'] = metadata
    
    def verify_record_integrity(self, records: List[Dict], source_name: str) -> Tuple[bool, List[Dict]]:
        """
        Verify if records have changed since last run.
        
        Args:
            records: List of records
            source_name: Identifier for this source
            
        Returns:
            (records_unchanged, list of changed records)
        """
        previous_records = self.checksums.get(source_name, {}).get('record_checksums', {})
        
        if not previous_records:
            return True, []  # First run
        
        changed_records = []
        
        for i, record in enumerate(records):
            current_checksum = self.calculate_record_checksum(record)
            previous_checksum = previous_records.get(str(i))
            
            if previous_checksum and current_checksum != previous_checksum:
                changed_records.append({
                    'index': i,
                    'record': record,
                    'previous_checksum': previous_checksum,
                    'current_checksum': current_checksum
                })
        
        return len(changed_records) == 0, changed_records
    
    def store_record_checksums(self, records: List[Dict], source_name: str):
        """
        Store checksums for all records.
        
        Args:
            records: List of records
            source_name: Identifier for this source
        """
        if source_name not in self.checksums:
            self.checksums[source_name] = {}
        
        record_checksums = {}
        for i, record in enumerate(records):
            record_checksums[str(i)] = self.calculate_record_checksum(record)
        
        self.checksums[source_name]['record_checksums'] = record_checksums
        self.checksums[source_name]['record_count'] = len(records)


class InventoryStandardizer:
    """Standardizes museum inventory records with checksum verification."""

    # Configuration
    REQUIRED_FIELDS = ["date", "title", "object_number", "link"]
    DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y"]
    
    def __init__(self, input_file: str, output_file: str, log_file: str = None, 
                 checksum_file: str = None, verify_only: bool = False):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output standardized TSV file
            log_file: Optional path to error/warning log file
            checksum_file: Optional path to checksum storage file
            verify_only: If True, only verify checksums without standardizing
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.log_file = Path(log_file) if log_file else None
        self.verify_only = verify_only
        
        # Initialize checksum manager
        if checksum_file:
            self.checksum_file = Path(checksum_file)
        else:
            self.checksum_file = self.input_file.parent / f".{self.input_file.stem}.checksums.json"
        
        self.checksum_manager = ChecksumManager(self.checksum_file)
        
        self.records = []
        self.errors = []
        self.warnings = []
        self.integrity_info = {}
        
    def verify_source_integrity(self) -> bool:
        """
        Verify source file hasn't changed.
        
        Returns:
            True if file is unchanged or first run, False if changed
        """
        print("Verifying source file integrity...")
        
        source_name = self.input_file.stem
        is_unchanged, message = self.checksum_manager.verify_file_integrity(
            self.input_file, 
            source_name
        )
        
        self.integrity_info['file_unchanged'] = is_unchanged
        self.integrity_info['file_message'] = message
        
        if is_unchanged:
            print(f"✓ {message}")
            return True
        else:
            print(f"⚠ {message}")
            self.warnings.append(f"Source file has changed: {message}")
            return False
    
    def load_records(self) -> bool:
        """
        Load records from TSV file.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.input_file.exists():
            self.errors.append(f"Input file not found: {self.input_file}")
            return False
            
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    self.errors.append("TSV file is empty")
                    return False
                
                # Check for required fields
                missing_fields = set(self.REQUIRED_FIELDS) - set(reader.fieldnames or [])
                if missing_fields:
                    self.errors.append(f"Missing required fields: {missing_fields}")
                    return False
                
                for row_num, row in enumerate(reader, start=2):
                    self.records.append((row_num, row))
                    
            print(f"✓ Loaded {len(self.records)} records from {self.input_file}")
            return True
            
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False
    
    def standardize_date(self, date_str: str, row_num: int) -> str:
        """Standardize date to YYYY-MM-DD format."""
        if not date_str or not date_str.strip():
            return ""
        
        date_str = date_str.strip()
        
        for fmt in self.DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        self.warnings.append(f"Row {row_num}: Could not parse date '{date_str}'")
        return date_str
    
    def standardize_title(self, title: str, row_num: int) -> str:
        """Standardize title formatting."""
        if not title or not title.strip():
            self.warnings.append(f"Row {row_num}: Empty title")
            return ""
        
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)
        title = title.title()
        
        return title
    
    def standardize_object_number(self, obj_num: str, row_num: int) -> str:
        """Standardize object number format."""
        if not obj_num or not obj_num.strip():
            self.errors.append(f"Row {row_num}: Missing object number")
            return ""
        
        obj_num = obj_num.strip()
        obj_num = re.sub(r'\s+', ' ', obj_num)
        obj_num = obj_num.upper()
        
        return obj_num
    
    def standardize_link(self, link: str, row_num: int) -> str:
        """Validate and standardize URL."""
        if not link or not link.strip():
            self.warnings.append(f"Row {row_num}: Empty link")
            return ""
        
        link = link.strip()
        
        url_pattern = r'^https?://'
        if not re.match(url_pattern, link):
            self.warnings.append(f"Row {row_num}: URL missing protocol: {link}")
            link = "https://" + link
        
        return link
    
    def check_duplicates(self) -> List[Tuple[str, List[int]]]:
        """Check for duplicate object numbers."""
        obj_num_map = {}
        
        for row_num, record in self.records:
            obj_num = record.get("object_number", "").upper().strip()
            if obj_num:
                if obj_num not in obj_num_map:
                    obj_num_map[obj_num] = []
                obj_num_map[obj_num].append(row_num)
        
        duplicates = [(k, v) for k, v in obj_num_map.items() if len(v) > 1]
        
        for obj_num, rows in duplicates:
            self.warnings.append(f"Duplicate object number '{obj_num}' in rows: {rows}")
        
        return duplicates
    
    def standardize_records(self) -> List[Dict]:
        """Standardize all loaded records."""
        standardized = []
        
        for row_num, record in self.records:
            try:
                standardized_record = {
                    "date": self.standardize_date(record.get("date", ""), row_num),
                    "title": self.standardize_title(record.get("title", ""), row_num),
                    "object_number": self.standardize_object_number(record.get("object_number", ""), row_num),
                    "link": self.standardize_link(record.get("link", ""), row_num),
                }
                
                if not standardized_record["object_number"]:
                    self.errors.append(f"Row {row_num}: Failed to standardize required field 'object_number'")
                    continue
                
                if not standardized_record["title"]:
                    self.errors.append(f"Row {row_num}: Failed to standardize required field 'title'")
                    continue
                
                standardized.append(standardized_record)
                
            except Exception as e:
                self.errors.append(f"Row {row_num}: Unexpected error: {e}")
                continue
        
        self.check_duplicates()
        
        print(f"✓ Standardized {len(standardized)} records")
        return standardized
    
    def save_records(self, standardized_records: List[Dict]) -> bool:
        """Save standardized records to output TSV file."""
        if not standardized_records:
            self.errors.append("No records to save")
            return False
        
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=self.REQUIRED_FIELDS,
                    delimiter='\t'
                )
                writer.writeheader()
                writer.writerows(standardized_records)
            
            print(f"✓ Saved {len(standardized_records)} records to {self.output_file}")
            return True
            
        except Exception as e:
            self.errors.append(f"Error writing output file: {e}")
            return False
    
    def update_checksums(self):
        """Update checksums for source and processed data."""
        source_name = self.input_file.stem
        
        print("Updating checksums...")
        
        # Store file checksum
        self.checksum_manager.store_file_checksum(
            self.input_file,
            source_name,
            metadata={'field_count': len(self.REQUIRED_FIELDS)}
        )
        
        # Store record checksums
        if self.records:
            raw_records = [dict(record) for _, record in self.records]
            self.checksum_manager.store_record_checksums(raw_records, source_name)
        
        self.checksum_manager.save_checksums()
        print(f"✓ Checksums updated and saved to {self.checksum_file}")
    
    def write_log(self) -> bool:
        """Write errors and warnings to log file."""
        if not self.log_file:
            return False
        
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("MUSEUM INVENTORY STANDARDIZATION LOG\n")
                f.write("=" * 60 + "\n\n")
                
                # File integrity section
                f.write("FILE INTEGRITY VERIFICATION\n")
                f.write("-" * 60 + "\n")
                f.write(f"Source File: {self.input_file}\n")
                f.write(f"Checksum File: {self.checksum_file}\n")
                if self.integrity_info:
                    f.write(f"Status: {self.integrity_info.get('file_message', 'Unknown')}\n")
                f.write("\n")
                
                if self.errors:
                    f.write(f"ERRORS ({len(self.errors)}):\n")
                    f.write("-" * 60 + "\n")
                    for error in self.errors:
                        f.write(f"  • {error}\n")
                    f.write("\n")
                
                if self.warnings:
                    f.write(f"WARNINGS ({len(self.warnings)}):\n")
                    f.write("-" * 60 + "\n")
                    for warning in self.warnings:
                        f.write(f"  • {warning}\n")
                    f.write("\n")
                
                if not self.errors and not self.warnings:
                    f.write("✓ No errors or warnings\n")
            
            print(f"✓ Log saved to {self.log_file}")
            return True
            
        except Exception as e:
            print(f"✗ Error writing log file: {e}", file=sys.stderr)
            return False
    
    def print_summary(self):
        """Print summary of standardization process."""
        print("\n" + "=" * 60)
        print("STANDARDIZATION SUMMARY")
        print("=" * 60)
        print(f"Records processed: {len(self.records)}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Checksum file: {self.checksum_file}")
        
        if self.errors:
            print("\nFirst 5 errors:")
            for error in self.errors[:5]:
                print(f"  • {error}")
        
        if self.warnings:
            print("\nFirst 5 warnings:")
            for warning in self.warnings[:5]:
                print(f"  • {warning}")
    
    def run(self) -> bool:
        """Execute the full standardization process."""
        print("Starting museum inventory standardization...\n")
        
        # Verify source integrity
        self.verify_source_integrity()
        
        if self.verify_only:
            print("\n✓ Verification complete (no standardization performed)")
            return True
        
        if not self.load_records():
            self.print_summary()
            return False
        
        standardized = self.standardize_records()
        
        if not self.save_records(standardized):
            self.print_summary()
            return False
        
        # Update checksums for next run
        self.update_checksums()
        
        self.write_log()
        self.print_summary()
        
        return len(self.errors) == 0


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records with checksum verification'
    )
    parser.add_argument('input_file', help='Input TSV file')
    parser.add_argument('output_file', help='Output standardized TSV file')
    parser.add_argument('-l', '--log', help='Log file path', default='standardization.log')
    parser.add_argument('-c', '--checksums', help='Checksum file path')
    parser.add_argument('-v', '--verify-only', action='store_true',
                        help='Only verify checksums, do not standardize')
    
    args = parser.parse_args()
    
    standardizer = InventoryStandardizer(
        args.input_file,
        args.output_file,
        args.log,
        args.checksums,
        args.verify_only
    )
    
    success = standardizer.run()
    sys.exit(0 if success else 1)
```

## Usage Examples

```bash
# First run - creates baseline checksums
python standardize_inventory.py inventory.tsv inventory_standardized.tsv

# Subsequent runs - verifies data hasn't changed
python standardize_inventory.py inventory.tsv inventory_standardized.tsv

# Only verify checksums without processing
python standardize_inventory.py inventory.tsv inventory_standardized.tsv -v

# Custom checksum file location
python standardize_inventory.py inventory.tsv inventory_standardized.tsv -c .checksums.json
```

## Checksum File Format

```json
{
  "inventory": {
    "file_checksum": "a3f5e8d9c1b2f4a6e7c8d9b1a2f3e4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0",
    "timestamp": "2024-01-15T10:30:45.123456",
    "file_name": "inventory.tsv",
    "file_size": 45627,
    "metadata": {
      "field_count": 4
    },
    "record_checksums": {
      "0": "5f3d2e1c9a8b7f6e5d4c3b2a1f0e9d8c",
      "1": "7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b",
      "2": "9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c"
    },
    "record_count": 3
  }
}
```

## Key Features

- **File-level checksums**: Detects any changes to source file
- **Record-level checksums**: Identifies which specific records changed
- **Multiple algorithms**: Supports MD5, SHA1, SHA256, SHA512
- **Persistent storage**: Stores checksums in JSON for historical tracking
- **Verification mode**: Can verify integrity without processing
- **Detailed reporting**: Log file documents all integrity checks
- **First-run handling**: Gracefully handles first execution with no baseline
