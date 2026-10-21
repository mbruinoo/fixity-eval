# Museum Inventory Standardizer with Checksum Verification

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records from a TSV file with checksum verification.

Checksums verify that source data hasn't changed between runs, allowing you to:
- Detect accidental modifications to the input file
- Track when records were last modified
- Maintain an audit trail of data integrity
- Identify which specific records changed
"""

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class ChecksumManager:
    """Manages checksums for source data integrity verification."""
    
    def __init__(self, checksum_file: Path):
        self.checksum_file = Path(checksum_file)
        self.file_checksums: Dict[str, str] = {}
        self.record_checksums: Dict[str, Dict[str, str]] = {}
        self.load()
    
    def load(self) -> None:
        """Load existing checksum file if it exists."""
        if self.checksum_file.exists():
            try:
                with open(self.checksum_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.file_checksums = data.get('file_checksums', {})
                    self.record_checksums = data.get('record_checksums', {})
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load checksums: {e}", file=sys.stderr)
    
    def save(self) -> None:
        """Save checksums to file."""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'file_checksums': self.file_checksums,
                'record_checksums': self.record_checksums,
            }
            with open(self.checksum_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save checksums: {e}", file=sys.stderr)
    
    @staticmethod
    def compute_file_checksum(file_path: Path) -> str:
        """Compute SHA-256 checksum of entire file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def compute_record_checksum(row: Dict[str, str]) -> str:
        """
        Compute checksum for a single record.
        Only hashes the actual data fields (excludes status/metadata).
        """
        # Normalize data for consistent hashing
        data_fields = ['date', 'title', 'object_number', 'link']
        normalized = json.dumps(
            {k: row.get(k, '').strip() for k in data_fields},
            sort_keys=True,
            separators=(',', ':')
        )
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def verify_file_unchanged(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Verify file hasn't changed since last processing.
        Returns (is_unchanged, previous_checksum).
        """
        current_checksum = self.compute_file_checksum(file_path)
        file_key = str(file_path.resolve())
        previous_checksum = self.file_checksums.get(file_key)
        
        if previous_checksum is None:
            return True, None  # No previous checksum to compare
        
        return current_checksum == previous_checksum, previous_checksum
    
    def update_file_checksum(self, file_path: Path) -> str:
        """Update and return file checksum."""
        checksum = self.compute_file_checksum(file_path)
        file_key = str(file_path.resolve())
        self.file_checksums[file_key] = checksum
        return checksum
    
    def get_changed_records(self, object_num: str, new_checksum: str) -> bool:
        """Check if a record's checksum changed. Returns True if changed."""
        old_checksum = self.record_checksums.get(object_num, {}).get('checksum')
        return new_checksum != old_checksum
    
    def update_record_checksum(self, object_num: str, checksum: str, 
                              timestamp: str = None) -> None:
        """Update record checksum and track when it changed."""
        if object_num not in self.record_checksums:
            self.record_checksums[object_num] = {}
        
        if self.get_changed_records(object_num, checksum):
            # Record changed
            self.record_checksums[object_num]['previous_checksum'] = \
                self.record_checksums[object_num].get('checksum')
            self.record_checksums[object_num]['last_changed'] = \
                timestamp or datetime.now().isoformat()
        
        self.record_checksums[object_num]['checksum'] = checksum


class InventoryRecord:
    """Represents a single museum inventory record with checksum tracking."""
    
    REQUIRED_FIELDS = {'date', 'title', 'object_number', 'link'}
    
    def __init__(self, row: Dict[str, str], row_num: int, 
                 checksum_manager: ChecksumManager = None):
        self.row_num = row_num
        self.raw_data = row.copy()
        self.errors = []
        self.warnings = []
        self.checksum_manager = checksum_manager
        
        # Store original values
        self.date_str = row.get('date', '').strip()
        self.title = row.get('title', '').strip()
        self.object_number = row.get('object_number', '').strip()
        self.link = row.get('link', '').strip()
        self.status = row.get('status', 'active').strip().lower()
        
        # Checksums
        self.data_checksum = None
        self.checksum_changed = False
        
        # Standardized values
        self.date_standardized = None
        self.object_number_standardized = None
        
        # Calculate checksum
        if checksum_manager:
            self.data_checksum = checksum_manager.compute_record_checksum(row)
    
    def check_data_integrity(self) -> None:
        """Check if record data has changed since last processing."""
        if not self.checksum_manager or not self.data_checksum:
            return
        
        # Normalize object number for comparison
        temp_obj_num = self._standardize_object_number(self.object_number)
        if temp_obj_num:
            self.checksum_changed = \
                self.checksum_manager.get_changed_records(
                    temp_obj_num, 
                    self.data_checksum
                )
            if self.checksum_changed:
                self.warnings.append("Record data has changed since last processing")
    
    def validate(self) -> bool:
        """Validate required fields. Returns True if valid."""
        for field in self.REQUIRED_FIELDS:
            value = getattr(self, field.replace('object_number', 'object_number'))
            if not value:
                self.errors.append(f"Missing required field: {field}")
        
        # Validate status
        if self.status not in ('active', 'corrected', 'withdrawn'):
            self.errors.append(
                f"Invalid status '{self.status}'. Must be: active, corrected, or withdrawn"
            )
        
        # Validate URL format if not withdrawn
        if self.status != 'withdrawn' and self.link:
            if not self._is_valid_url(self.link):
                self.warnings.append(f"Link may be invalid: {self.link}")
        
        return len(self.errors) == 0
    
    def standardize(self) -> bool:
        """Standardize fields. Returns True if successful."""
        self.date_standardized = self._standardize_date(self.date_str)
        if self.date_standardized is None and self.date_str:
            self.errors.append(f"Could not parse date: {self.date_str}")
        
        self.object_number_standardized = self._standardize_object_number(
            self.object_number
        )
        if self.object_number_standardized is None:
            self.errors.append(f"Could not standardize object number: {self.object_number}")
        
        if len(self.title) > 500:
            self.warnings.append(
                f"Title is very long ({len(self.title)} chars), may need review"
            )
        
        return len(self.errors) == 0
    
    @staticmethod
    def _standardize_date(date_str: str) -> Optional[str]:
        """Convert various date formats to ISO 8601 (YYYY-MM-DD)."""
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                return None
        
        formats = [
            '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
            '%B %d, %Y', '%b %d, %Y', '%d %B %Y', '%d %b %Y',
            '%m-%d-%Y', '%d-%m-%Y',
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def _standardize_object_number(obj_num: str) -> Optional[str]:
        """Standardize object number format."""
        if not obj_num:
            return None
        
        obj_num = obj_num.strip()
        obj_num = re.sub(r'\s+', ' ', obj_num)
        obj_num = re.sub(r'\s*-\s*', '-', obj_num)
        
        if not re.search(r'[a-zA-Z0-9]', obj_num):
            return None
        
        return obj_num.upper()
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Basic URL validation."""
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$',
            re.IGNORECASE
        )
        return bool(url_pattern.match(url))
    
    def to_dict(self) -> Dict:
        """Return standardized record as dictionary."""
        return {
            'date': self.date_standardized,
            'title': self.title,
            'object_number': self.object_number_standardized,
            'link': self.link,
            'status': self.status,
        }


class InventoryStandardizer:
    """Manages the standardization process with checksum verification."""
    
    def __init__(self, input_file: Path, output_dir: Path, 
                 checksum_file: Optional[Path] = None):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up checksum file
        if checksum_file is None:
            checksum_file = self.output_dir / '.checksums.json'
        self.checksum_manager = ChecksumManager(checksum_file)
        
        self.records: List[InventoryRecord] = []
        self.valid_records: List[InventoryRecord] = []
        self.invalid_records: List[InventoryRecord] = []
        self.file_changed = False
    
    def read_input(self) -> bool:
        """Read and parse TSV file with checksum verification."""
        # Verify file integrity
        unchanged, previous_checksum = self.checksum_manager.verify_file_unchanged(
            self.input_file
        )
        
        if not unchanged:
            self.file_changed = True
            print("⚠ Warning: Source file has changed since last processing")
            print(f"  Previous checksum: {previous_checksum}")
            current = self.checksum_manager.compute_file_checksum(self.input_file)
            print(f"  Current checksum:  {current}")
        else:
            if previous_checksum:
                print("✓ Source file unchanged since last processing")
            else:
                print("→ First time processing this file")
        
        try:
            with open(self.input_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if reader.fieldnames is None:
                    print("Error: Empty TSV file", file=sys.stderr)
                    return False
                
                for row_num, row in enumerate(reader, start=2):
                    record = InventoryRecord(row, row_num, self.checksum_manager)
                    self.records.append(record)
            
            print(f"✓ Loaded {len(self.records)} records")
            return True
        
        except FileNotFoundError:
            print(f"Error: File not found: {self.input_file}", file=sys.stderr)
            return False
        except csv.Error as e:
            print(f"Error reading TSV: {e}", file=sys.stderr)
            return False
    
    def process_records(self) -> None:
        """Validate and standardize all records."""
        print("\nProcessing records...")
        
        for record in self.records:
            record.check_data_integrity()
            
            if not record.validate():
                self.invalid_records.append(record)
                continue
            
            if not record.standardize():
                self.invalid_records.append(record)
                continue
            
            self.valid_records.append(record)
        
        print(f"✓ Valid records: {len(self.valid_records)}")
        print(f"✓ Invalid records: {len(self.invalid_records)}")
    
    def handle_corrections_and_withdrawals(self) -> Tuple[List[InventoryRecord], Dict]:
        """Process corrections and withdrawals, keeping latest version of each."""
        by_object: Dict[str, List[InventoryRecord]] = defaultdict(list)
        for record in self.valid_records:
            by_object[record.object_number_standardized].append(record)
        
        active_records = []
        audit_info = {
            'corrections': 0,
            'withdrawn': 0,
            'duplicates_kept': 0,
            'records_changed': 0,
        }
        
        for obj_num, versions in by_object.items():
            versions.sort(key=lambda r: r.row_num)
            latest = versions[-1]
            
            if latest.status == 'withdrawn':
                audit_info['withdrawn'] += 1
            else:
                active_records.append(latest)
                if latest.status == 'corrected':
                    audit_info['corrections'] += 1
            
            if latest.checksum_changed:
                audit_info['records_changed'] += 1
            
            if len(versions) > 1:
                audit_info['duplicates_kept'] += 1
        
        return active_records, audit_info
    
    def update_checksums(self, active_records: List[InventoryRecord]) -> None:
        """Update checksums for all processed records."""
        # Update file checksum
        self.checksum_manager.update_file_checksum(self.input_file)
        
        # Update record checksums
        for record in active_records:
            self.checksum_manager.update_record_checksum(
                record.object_number_standardized,
                record.data_checksum
            )
        
        self.checksum_manager.save()
        print("✓ Checksums updated and saved")
    
    def write_output(self, active_records: List[InventoryRecord]) -> None:
        """Write standardized records to TSV file."""
        output_file = self.output_dir / 'inventory_standardized.tsv'
        fieldnames = ['date', 'title', 'object_number', 'link', 'status']
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                
                for record in sorted(active_records, 
                                   key=lambda r: r.date_standardized or ''):
                    writer.writerow(record.to_dict())
            
            print(f"✓ Wrote {len(active_records)} records to {output_file.name}")
        
        except IOError as e:
            print(f"Error writing output: {e}", file=sys.stderr)
    
    def generate_audit_report(self, audit_info: Dict) -> None:
        """Generate detailed audit report with checksum information."""
        report_file = self.output_dir / 'audit_report.txt'
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("MUSEUM INVENTORY STANDARDIZATION AUDIT REPORT\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"Input file: {self.input_file}\n")
                f.write(f"Processed: {datetime.now().isoformat()}\n\n")
                
                # File integrity
                f.write("FILE INTEGRITY\n")
                f.write("-" * 60 + "\n")
                if self.file_changed:
                    f.write("Status: SOURCE FILE HAS CHANGED\n")
                else:
                    f.write("Status: Source file unchanged since last processing\n")
                
                file_key = str(self.input_file.resolve())
                if file_key in self.checksum_manager.file_checksums:
                    f.write(f"Current checksum:  {self.checksum_manager.file_checksums[file_key]}\n")
                f.write("\n")
                
                # Summary
                f.write("SUMMARY\n")
                f.write("-" * 60 + "\n")
                f.write(f"Total records read:        {len(self.records)}\n")
                f.write(f"Valid records:             {len(self.valid_records)}\n")
                f.write(f"Invalid records:           {len(self.invalid_records)}\n")
                f.write(f"Active records (output):   {len(self.valid_records) - audit_info['corrections'] - audit_info['withdrawn']}\n")
                f.write(f"\nCorrections applied:       {audit_info['corrections']}\n")
                f.write(f"Records withdrawn:         {audit_info['withdrawn']}\n")
                f.write(f"Duplicate handling:        {audit_info['duplicates_kept']} objects had multiple versions\n")
                f.write(f"Records changed:           {audit_info['records_changed']}\n\n")
                
                # Changed records
                if audit_info['records_changed'] > 0:
                    f.write("RECORDS WITH CHANGED DATA\n")
                    f.write("-" * 60 + "\n")
                    for record in self.valid_records:
                        if record.checksum_changed:
                            f.write(f"{record.object_number_standardized}: ")
                            f.write(f"Row {record.row_num}\n")
                            if record.object_number_standardized in self.checksum_manager.record_checksums:
                                info = self.checksum_manager.record_checksums[record.object_number_standardized]
                                if 'last_changed' in info:
                                    f.write(f"  Last changed: {info['last_changed']}\n")
                    f.write("\n")
                
                # Errors
                if self.invalid_records:
                    f.write("ERRORS\n")
                    f.write("-" * 60 + "\n")
                    for record in self.invalid_records:
                        f.write(f"Row {record.row_num}:\n")
                        for error in record.errors:
                            f.write(f"  • {error}\n")
                        f.write("\n")
                
                # Warnings
                warnings_found = [r for r in self.valid_records if r.warnings]
                if warnings_found:
                    f.write("WARNINGS\n")
                    f.write("-" * 60 + "\n")
                    for record in warnings_found:
                        f.write(f"Row {record.row_num} ({record.object_number_standardized}):\n")
                        for warning in record.warnings:
                            f.write(f"  ⚠ {warning}\n")
                        f.write("\n")
            
            print(f"✓ Audit report written to {report_file.name}")
        
        except IOError as e:
            print(f"Error writing audit report: {e}", file=sys.stderr)
    
    def run(self) -> bool:
        """Execute the full standardization process."""
        print(f"Standardizing museum inventory from: {self.input_file}\n")
        
        if not self.read_input():
            return False
        
        self.process_records()
        active_records, audit_info = self.handle_corrections_and_withdrawals()
        
        self.write_output(active_records)
        self.generate_audit_report(audit_info)
        self.update_checksums(active_records)
        
        print("\n✓ Standardization complete!")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records with checksum verification'
    )
    parser.add_argument(
        'input',
        type=str,
        help='Input TSV file with inventory records'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='./standardized_inventory',
        help='Output directory (default: ./standardized_inventory)'
    )
    parser.add_argument(
        '-c', '--checksums',
        type=str,
        help='Checksum file path (default: output_dir/.checksums.json)'
    )
    
    args = parser.parse_args()
    
    standardizer = InventoryStandardizer(
        args.input,
        args.output,
        Path(args.checksums) if args.checksums else None
    )
    success = standardizer.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Key Checksum Features

### 1. **File-Level Checksums**
- SHA-256 hash of the entire input file
- Detects if source data has been modified
- Warns on first run and subsequent changes

### 2. **Record-Level Checksums**
- Hash of each record's data fields (date, title, object_number, link)
- Identifies which specific records changed
- Ignores status changes (corrections/withdrawals)

### 3. **Change Tracking**
- Records timestamp when data changed
- Stores previous checksum for comparison
- Maintains audit trail of modifications

### 4. **Integration**
```bash
# First run - establishes baseline checksums
python standardize_inventory.py records.tsv

# Second run - detects if file changed
python standardize_inventory.py records.tsv
# Output: ⚠ Warning: Source file has changed since last processing

# Custom checksum storage location
python standardize_inventory.py records.tsv -c ./my_checksums.json
```

### 5. **Audit Report**
The report now includes:
- File integrity status
- Count of records with changed data
- Timestamp of last change for each modified record
- Clear distinction between data changes and status changes

This approach ensures data integrity while allowing legitimate corrections and withdrawals to be tracked separately.
