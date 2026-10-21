# Museum Inventory Standardizer with Checksum Verification

```python
#!/usr/bin/env python3
"""
Standardizes a museum inventory spreadsheet (.tsv) with checksum verification
to ensure source data integrity.

Usage:
    python standardize_inventory.py input.tsv output.tsv [--save-checksum] [--verify-checksum]
"""

import sys
import csv
import re
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class ChecksumData:
    """Data structure for storing checksum information."""
    timestamp: str
    input_file: str
    file_hash: str  # SHA256 of entire file
    row_hashes: Dict[int, str]  # SHA256 of each row
    record_count: int
    columns: List[str]
    notes: str = ""


class ChecksumManager:
    """Manages checksums for inventory files."""
    
    HASH_ALGORITHM = 'sha256'
    CHECKSUM_SUFFIX = '.checksum.json'
    
    @staticmethod
    def calculate_file_hash(filepath: str, block_size: int = 65536) -> str:
        """Calculate SHA256 hash of entire file."""
        hasher = hashlib.sha256()
        
        try:
            with open(filepath, 'rb') as f:
                while True:
                    block = f.read(block_size)
                    if not block:
                        break
                    hasher.update(block)
            return hasher.hexdigest()
        except IOError as e:
            raise IOError(f"Cannot read file {filepath}: {e}")
    
    @staticmethod
    def calculate_row_hash(row: Dict[str, str]) -> str:
        """Calculate hash of a single row (order-independent)."""
        hasher = hashlib.sha256()
        
        # Sort keys for consistent hashing
        for key in sorted(row.keys()):
            value = row[key] if row[key] is not None else ""
            hasher.update(f"{key}={value}".encode('utf-8'))
        
        return hasher.hexdigest()
    
    @staticmethod
    def get_checksum_filename(filepath: str) -> str:
        """Generate checksum filename from input filename."""
        path = Path(filepath)
        return str(path.parent / f"{path.stem}{ChecksumManager.CHECKSUM_SUFFIX}")
    
    @staticmethod
    def save_checksum(
        checksum_data: ChecksumData,
        output_path: Optional[str] = None
    ) -> str:
        """
        Save checksum data to JSON file.
        Returns the path where checksum was saved.
        """
        if output_path is None:
            output_path = ChecksumManager.get_checksum_filename(
                checksum_data.input_file
            )
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(checksum_data), f, indent=2)
            return output_path
        except IOError as e:
            raise IOError(f"Cannot write checksum file {output_path}: {e}")
    
    @staticmethod
    def load_checksum(filepath: str) -> Optional[ChecksumData]:
        """Load checksum data from JSON file."""
        checksum_file = ChecksumManager.get_checksum_filename(filepath)
        
        if not Path(checksum_file).exists():
            return None
        
        try:
            with open(checksum_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ChecksumData(**data)
        except (IOError, json.JSONDecodeError, TypeError) as e:
            raise IOError(f"Cannot read checksum file {checksum_file}: {e}")
    
    @staticmethod
    def verify_file_integrity(filepath: str, expected_hash: str) -> Tuple[bool, str]:
        """
        Verify file hasn't changed by comparing file hash.
        Returns (is_valid, actual_hash)
        """
        actual_hash = ChecksumManager.calculate_file_hash(filepath)
        is_valid = actual_hash.lower() == expected_hash.lower()
        return is_valid, actual_hash
    
    @staticmethod
    def verify_row_integrity(
        row: Dict[str, str],
        expected_hash: str
    ) -> Tuple[bool, str]:
        """
        Verify row hasn't changed by comparing row hash.
        Returns (is_valid, actual_hash)
        """
        actual_hash = ChecksumManager.calculate_row_hash(row)
        is_valid = actual_hash.lower() == expected_hash.lower()
        return is_valid, actual_hash
    
    @staticmethod
    def detect_changes(
        filepath: str,
        old_checksum: ChecksumData
    ) -> Dict[str, any]:
        """
        Detect what has changed in the file since last checksum.
        Returns detailed change report.
        """
        changes = {
            'file_changed': False,
            'file_hash_changed': False,
            'row_count_changed': False,
            'columns_changed': False,
            'modified_rows': [],
            'deleted_rows': [],
            'new_rows': [],
            'details': []
        }
        
        # Check file hash
        is_valid, new_hash = ChecksumManager.verify_file_integrity(
            filepath,
            old_checksum.file_hash
        )
        
        if not is_valid:
            changes['file_changed'] = True
            changes['file_hash_changed'] = True
            changes['details'].append(
                f"File hash changed:\n  Old: {old_checksum.file_hash}\n  New: {new_hash}"
            )
        
        # Read current file and check rows
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                current_rows = list(reader)
            
            # Check record count
            if len(current_rows) != old_checksum.record_count:
                changes['row_count_changed'] = True
                changes['details'].append(
                    f"Row count changed: {old_checksum.record_count} → {len(current_rows)}"
                )
            
            # Check columns
            if reader.fieldnames != old_checksum.columns:
                changes['columns_changed'] = True
                changes['details'].append(
                    f"Columns changed:\n  Old: {old_checksum.columns}\n  "
                    f"New: {reader.fieldnames}"
                )
            
            # Check individual rows
            for row_num, row in enumerate(current_rows, start=2):
                row_key = str(row_num)
                row_hash = ChecksumManager.calculate_row_hash(row)
                
                if row_key not in old_checksum.row_hashes:
                    changes['new_rows'].append(row_num)
                    changes['details'].append(f"New row {row_num} added")
                elif row_hash != old_checksum.row_hashes[row_key]:
                    changes['modified_rows'].append(row_num)
                    changes['details'].append(
                        f"Row {row_num} modified: {row_hash}"
                    )
            
            # Check for deleted rows
            for row_num in old_checksum.row_hashes:
                if int(row_num) > len(current_rows) + 1:  # +1 for header
                    changes['deleted_rows'].append(int(row_num))
                    changes['details'].append(f"Row {row_num} deleted")
        
        except Exception as e:
            changes['details'].append(f"Error reading file: {str(e)}")
        
        return changes


class InventoryStandardizer:
    """Standardizes museum inventory data with checksum verification."""
    
    REQUIRED_COLUMNS = {'date', 'title', 'object number', 'link'}
    
    def __init__(
        self,
        input_file: str,
        output_file: str,
        verify_checksum: bool = False,
        save_checksum: bool = False,
        verbose: bool = True
    ):
        self.input_file = input_file
        self.output_file = output_file
        self.verify_checksum = verify_checksum
        self.save_checksum = save_checksum
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.checksum_data = None
        self.old_checksum = None
        self.change_report = None
    
    def log(self, message: str, level: str = "INFO"):
        """Print log messages if verbose mode is enabled."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def verify_source_integrity(self) -> bool:
        """
        Verify source file hasn't changed since last standardization.
        Returns True if verification passes or no previous checksum exists.
        """
        self.log("Checking for previous checksum...")
        
        try:
            self.old_checksum = ChecksumManager.load_checksum(self.input_file)
        except IOError as e:
            self.log(f"Cannot load checksum: {e}", "WARNING")
            return True
        
        if not self.old_checksum:
            self.log("No previous checksum found (first run)")
            return True
        
        self.log("Previous checksum found, verifying file integrity...")
        
        # Check file hash
        is_valid, _ = ChecksumManager.verify_file_integrity(
            self.input_file,
            self.old_checksum.file_hash
        )
        
        if is_valid:
            self.log("✓ File hash matches previous checksum")
            return True
        
        # File has changed, detect what changed
        self.change_report = ChecksumManager.detect_changes(
            self.input_file,
            self.old_checksum
        )
        
        self.log("⚠ Source file has changed since last standardization", "WARNING")
        self.log(f"  Changes detected:", "WARNING")
        for detail in self.change_report['details'][:5]:
            self.log(f"    - {detail}", "WARNING")
        
        if len(self.change_report['details']) > 5:
            self.log(
                f"    ... and {len(self.change_report['details']) - 5} more changes",
                "WARNING"
            )
        
        return True  # Continue processing, but user is warned
    
    def standardize_date(self, date_str: str) -> str:
        """Standardize date to ISO format (YYYY-MM-DD)."""
        if not date_str or not date_str.strip():
            self.warnings.append("Empty date field found")
            return ""
        
        date_str = date_str.strip()
        
        formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y",
            "%Y/%m/%d", "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y",
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            self.warnings.append(f"Could not parse date '{date_str}', keeping original")
            return date_str
        
        self.errors.append(f"Invalid date format: '{date_str}'")
        return ""
    
    def standardize_title(self, title: str) -> str:
        """Standardize title."""
        if not title or not title.strip():
            self.errors.append("Empty title field found")
            return ""
        
        title = " ".join(title.split())
        return title
    
    def standardize_object_number(self, obj_num: str) -> str:
        """Standardize object number."""
        if not obj_num or not obj_num.strip():
            self.errors.append("Empty object number found")
            return ""
        
        obj_num = obj_num.strip().upper()
        obj_num = re.sub(r'^[^\w\-\.]+|[^\w\-\.]+$', '', obj_num)
        
        if not re.match(r'^[\w\-\.]+$', obj_num):
            self.warnings.append(f"Object number contains unusual characters: '{obj_num}'")
        
        return obj_num
    
    def standardize_link(self, link: str) -> str:
        """Standardize URL."""
        if not link or not link.strip():
            return ""
        
        link = link.strip()
        
        if not link.startswith(('http://', 'https://', 'ftp://')):
            link = 'https://' + link
        
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, link):
            self.warnings.append(f"URL may be invalid: '{link}'")
        
        return link
    
    def normalize_column_names(self, fieldnames: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """Normalize column names."""
        mapping = {}
        normalized = []
        
        for field in fieldnames:
            field_lower = field.lower().strip()
            
            if field_lower in self.REQUIRED_COLUMNS:
                normalized.append(field_lower)
                mapping[field] = field_lower
            elif 'date' in field_lower:
                normalized.append('date')
                mapping[field] = 'date'
            elif any(t in field_lower for t in ['title', 'name', 'object name']):
                normalized.append('title')
                mapping[field] = 'title'
            elif any(o in field_lower for o in ['object', 'number', 'id', 'accession']):
                normalized.append('object number')
                mapping[field] = 'object number'
            elif 'link' in field_lower or 'url' in field_lower or 'uri' in field_lower:
                normalized.append('link')
                mapping[field] = 'link'
            else:
                normalized.append(field_lower)
                mapping[field] = field_lower
        
        return normalized, mapping
    
    def validate_row(self, row: Dict[str, str], row_num: int) -> bool:
        """Validate that a row has required columns with data."""
        has_critical_data = any([
            row.get('date', '').strip(),
            row.get('title', '').strip(),
            row.get('object number', '').strip()
        ])
        
        if not has_critical_data:
            self.warnings.append(f"Row {row_num}: Skipping empty row")
            return False
        
        return True
    
    def standardize(self) -> bool:
        """Main standardization routine."""
        self.log(f"Reading from: {self.input_file}")
        
        # Verify source integrity if requested
        if self.verify_checksum:
            self.verify_source_integrity()
        
        try:
            # Calculate checksums for source file
            self.log("Calculating source file checksums...")
            file_hash = ChecksumManager.calculate_file_hash(self.input_file)
            row_hashes = {}
            
            with open(self.input_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile, delimiter='\t')
                
                if not reader.fieldnames:
                    self.log("No fieldnames found", "ERROR")
                    return False
                
                normalized_fields, field_mapping = self.normalize_column_names(
                    reader.fieldnames
                )
                self.log(f"Detected columns: {reader.fieldnames}")
                self.log(f"Normalized to: {normalized_fields}")
                
                standardized_rows = []
                
                for row_num, row in enumerate(reader, start=2):
                    # Calculate row hash before processing
                    row_hashes[str(row_num)] = ChecksumManager.calculate_row_hash(row)
                    
                    # Remap old column names
                    remapped_row = {
                        field_mapping[k]: v for k, v in row.items()
                    }
                    
                    if not self.validate_row(remapped_row, row_num):
                        continue
                    
                    # Standardize each field
                    standardized_row = {
                        'date': self.standardize_date(remapped_row.get('date', '')),
                        'title': self.standardize_title(remapped_row.get('title', '')),
                        'object number': self.standardize_object_number(
                            remapped_row.get('object number', '')
                        ),
                        'link': self.standardize_link(remapped_row.get('link', '')),
                    }
                    
                    standardized_rows.append(standardized_row)
                
                # Write standardized data
                self.log(f"Writing to: {self.output_file}")
                with open(self.output_file, 'w', newline='', encoding='utf-8') as outfile:
                    writer = csv.DictWriter(
                        outfile,
                        fieldnames=['date', 'title', 'object number', 'link'],
                        delimiter='\t'
                    )
                    writer.writeheader()
                    writer.writerows(standardized_rows)
                
                # Save checksum if requested
                if self.save_checksum:
                    self.checksum_data = ChecksumData(
                        timestamp=datetime.now().isoformat(),
                        input_file=self.input_file,
                        file_hash=file_hash,
                        row_hashes=row_hashes,
                        record_count=len(standardized_rows),
                        columns=normalized_fields,
                        notes="Auto-generated checksum for source file verification"
                    )
                    
                    checksum_file = ChecksumManager.save_checksum(self.checksum_data)
                    self.log(f"Checksum saved to: {checksum_file}")
                
                self.log(f"Successfully standardized {len(standardized_rows)} records")
                return True
        
        except FileNotFoundError:
            self.log(f"Input file not found: {self.input_file}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Unexpected error: {str(e)}", "ERROR")
            return False
    
    def print_report(self):
        """Print summary report."""
        print("\n" + "="*70)
        print("STANDARDIZATION REPORT")
        print("="*70)
        
        # Checksum verification report
        if self.change_report:
            print("\n📋 SOURCE FILE CHANGES DETECTED:")
            print(f"  File Changed: {self.change_report['file_changed']}")
            print(f"  Row Count Changed: {self.change_report['row_count_changed']}")
            print(f"  Columns Changed: {self.change_report['columns_changed']}")
            if self.change_report['modified_rows']:
                print(f"  Modified Rows: {self.change_report['modified_rows']}")
            if self.change_report['new_rows']:
                print(f"  New Rows: {self.change_report['new_rows']}")
            if self.change_report['deleted_rows']:
                print(f"  Deleted Rows: {self.change_report['deleted_rows']}")
        
        # Checksum info
        if self.checksum_data:
            print("\n🔐 CHECKSUM INFORMATION:")
            print(f"  File Hash: {self.checksum_data.file_hash}")
            print(f"  Records: {self.checksum_data.record_count}")
            print(f"  Timestamp: {self.checksum_data.timestamp}")
        
        # Warnings and errors
        if self.warnings:
            print(f"\n⚠  Warnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"    {warning}")
            if len(self.warnings) > 10:
                print(f"    ... and {len(self.warnings) - 10} more")
        
        if self.errors:
            print(f"\n✗ Errors ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"    {error}")
            if len(self.errors) > 10:
                print(f"    ... and {len(self.errors) - 10} more")
        
        if not self.errors and not self.warnings:
            print("\n✓ No errors or warnings!")
        
        print("="*70 + "\n")


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory with checksum verification"
    )
    parser.add_argument("input", help="Input TSV file")
    parser.add_argument("output", help="Output TSV file")
    parser.add_argument(
        "--save-checksum",
        action="store_true",
        help="Save checksum of source file for future verification"
    )
    parser.add_argument(
        "--verify-checksum",
        action="store_true",
        help="Verify source file hasn't changed since last run"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output"
    )
    
    args = parser.parse_args()
    
    standardizer = InventoryStandardizer(
        input_file=args.input,
        output_file=args.output,
        verify_checksum=args.verify_checksum,
        save_checksum=args.save_checksum,
        verbose=not args.quiet
    )
    
    if standardizer.standardize():
        standardizer.print_report()
        print(f"✓ Output saved to: {args.output}")
        
        if args.save_checksum and standardizer.checksum_data:
            checksum_file = ChecksumManager.get_checksum_filename(args.input)
            print(f"✓ Checksum saved to: {checksum_file}")
        
        sys.exit(0)
    else:
        standardizer.print_report()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Usage Examples

### First run - save checksums for future verification:
```bash
python standardize_inventory.py input.tsv output.tsv --save-checksum
```

This creates `input.checksum.json` containing:
- File hash (SHA256 of entire file)
- Individual row hashes
- Record count
- Column names
- Timestamp

### Subsequent runs - verify source hasn't changed:
```bash
python standardize_inventory.py input.tsv output.tsv --verify-checksum
```

### Save and verify in one command:
```bash
python standardize_inventory.py input.tsv output.tsv --save-checksum --verify-checksum
```

## Example Checksum File (`input.checksum.json`)

```json
{
  "timestamp": "2024-01-15T14:32:05.123456",
  "input_file": "input.tsv",
  "file_hash": "a1b2c3d4e5f6...",
  "row_hashes": {
    "2": "hash_of_row_2",
    "3": "hash_of_row_3",
    "4": "hash_of_row_4"
  },
  "record_count": 150,
  "columns": ["date", "title", "object number", "link"],
  "notes": "Auto-generated checksum for source file verification"
}
```

## Key Features

1. **File-level integrity**: SHA256 hash of entire source file
2. **Row-level integrity**: Individual hashes for each row
3. **Change detection**: Identifies modified, added, or deleted rows
4. **Automatic verification**: Warns if source file has changed since last run
5. **Timestamp tracking**: Records when checksums were created
6. **Separate checksum files**: Stores checksums in `.checksum.json` alongside input
7. **Detailed change reports**: Shows exactly what changed between runs
