# Museum Inventory Standardizer with Checksum Verification

Here's how to incorporate checksums to verify source data integrity:

```python
#!/usr/bin/env python3
"""
Museum Inventory Spreadsheet Standardizer with Checksum Verification
Standardizes TSV files and verifies data integrity using checksums.
"""

import argparse
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import csv


class ChecksumManager:
    """Manages checksums for data integrity verification."""
    
    def __init__(self, checksum_dir: Path = None):
        """
        Initialize checksum manager.
        
        Args:
            checksum_dir: Directory to store checksum files (default: .checksums/)
        """
        self.checksum_dir = checksum_dir or Path('.checksums')
        self.checksum_dir.mkdir(exist_ok=True)
    
    @staticmethod
    def hash_file(file_path: Path, algorithm: str = 'sha256') -> str:
        """
        Calculate hash of entire file.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm (md5, sha1, sha256, sha512)
        
        Returns:
            Hex digest of file hash
        """
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def hash_rows(rows: List[Dict], algorithm: str = 'sha256') -> str:
        """
        Calculate hash of row data (content-based).
        Ignores row order but detects content changes.
        
        Args:
            rows: List of row dictionaries
            algorithm: Hash algorithm
        
        Returns:
            Hex digest of content hash
        """
        hash_obj = hashlib.new(algorithm)
        
        # Sort rows by object_number for consistent ordering
        sorted_rows = sorted(rows, key=lambda r: r.get('object_number', ''))
        
        for row in sorted_rows:
            # Create deterministic string representation
            row_str = json.dumps(row, sort_keys=True, separators=(',', ':'))
            hash_obj.update(row_str.encode('utf-8'))
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def hash_string(data: str, algorithm: str = 'sha256') -> str:
        """
        Calculate hash of a string.
        
        Args:
            data: String to hash
            algorithm: Hash algorithm
        
        Returns:
            Hex digest
        """
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(data.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def get_checksum_file(self, input_file: Path) -> Path:
        """Get path to checksum file for a given input file."""
        filename = f"{input_file.stem}.checksum.json"
        return self.checksum_dir / filename
    
    def create_checksum_record(self, 
                              input_file: Path, 
                              rows: List[Dict],
                              headers: List[str]) -> Dict:
        """
        Create a comprehensive checksum record.
        
        Args:
            input_file: Path to source file
            rows: Original rows from file
            headers: Column headers
        
        Returns:
            Dictionary containing multiple checksums and metadata
        """
        file_hash = self.hash_file(input_file)
        content_hash = self.hash_rows(rows)
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'source_file': str(input_file),
            'file_hash': {
                'algorithm': 'sha256',
                'value': file_hash
            },
            'content_hash': {
                'algorithm': 'sha256',
                'value': content_hash
            },
            'metadata': {
                'row_count': len(rows),
                'column_count': len(headers),
                'columns': headers,
                'file_size': input_file.stat().st_size,
                'file_modified': datetime.fromtimestamp(
                    input_file.stat().st_mtime
                ).isoformat()
            }
        }
        
        return record
    
    def save_checksum(self, input_file: Path, record: Dict) -> bool:
        """
        Save checksum record to file.
        
        Args:
            input_file: Path to source file
            record: Checksum record dictionary
        
        Returns:
            True if successful
        """
        try:
            checksum_file = self.get_checksum_file(input_file)
            with open(checksum_file, 'w', encoding='utf-8') as f:
                json.dump(record, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving checksum: {e}")
            return False
    
    def load_checksum(self, input_file: Path) -> Optional[Dict]:
        """
        Load previously saved checksum record.
        
        Args:
            input_file: Path to source file
        
        Returns:
            Checksum record dictionary or None if not found
        """
        checksum_file = self.get_checksum_file(input_file)
        
        if not checksum_file.exists():
            return None
        
        try:
            with open(checksum_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading checksum: {e}")
            return None
    
    def verify_file_integrity(self, input_file: Path, 
                             previous_record: Dict) -> Tuple[bool, str]:
        """
        Verify that source file hasn't changed using file hash.
        
        Args:
            input_file: Path to current file
            previous_record: Previously saved checksum record
        
        Returns:
            Tuple of (is_valid, message)
        """
        if 'file_hash' not in previous_record:
            return False, "No file hash in previous record"
        
        current_hash = self.hash_file(input_file)
        previous_hash = previous_record['file_hash']['value']
        
        if current_hash == previous_hash:
            return True, f"File unchanged (hash: {current_hash[:16]}...)"
        else:
            return False, (f"File has changed!\n"
                          f"  Previous: {previous_hash}\n"
                          f"  Current:  {current_hash}")
    
    def verify_content_integrity(self, rows: List[Dict], 
                                previous_record: Dict) -> Tuple[bool, str]:
        """
        Verify that content hasn't changed using content hash.
        
        Args:
            rows: Current rows
            previous_record: Previously saved checksum record
        
        Returns:
            Tuple of (is_valid, message)
        """
        if 'content_hash' not in previous_record:
            return False, "No content hash in previous record"
        
        current_hash = self.hash_rows(rows)
        previous_hash = previous_record['content_hash']['value']
        
        if current_hash == previous_hash:
            return True, f"Content unchanged (hash: {current_hash[:16]}...)"
        else:
            return False, (f"Content has changed!\n"
                          f"  Previous: {previous_hash}\n"
                          f"  Current:  {current_hash}")
    
    def verify_metadata(self, rows: List[Dict], headers: List[str],
                       previous_record: Dict) -> List[str]:
        """
        Check if metadata has changed (row count, columns, etc).
        
        Args:
            rows: Current rows
            headers: Current headers
            previous_record: Previously saved checksum record
        
        Returns:
            List of metadata change messages
        """
        metadata = previous_record.get('metadata', {})
        changes = []
        
        prev_row_count = metadata.get('row_count', -1)
        if len(rows) != prev_row_count:
            changes.append(
                f"Row count changed: {prev_row_count} → {len(rows)}"
            )
        
        prev_col_count = metadata.get('column_count', -1)
        if len(headers) != prev_col_count:
            changes.append(
                f"Column count changed: {prev_col_count} → {len(headers)}"
            )
        
        prev_columns = metadata.get('columns', [])
        if set(headers) != set(prev_columns):
            changes.append(
                f"Columns changed: {prev_columns} → {headers}"
            )
        
        return changes


class InventoryStandardizer:
    """Standardizes museum inventory spreadsheets with checksum verification."""
    
    EXPECTED_COLUMNS = ['date', 'title', 'object_number', 'link']
    
    def __init__(self, input_file: str, output_file: str = None, 
                 strict: bool = False, checksum_dir: str = None,
                 require_checksum: bool = False):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file
            strict: If True, fail on any issues
            checksum_dir: Directory for checksum files
            require_checksum: If True, fail if previous checksum not found
        """
        self.input_file = Path(input_file)
        self.strict = strict
        self.require_checksum = require_checksum
        self.errors = []
        self.warnings = []
        self.checksum_manager = ChecksumManager(
            Path(checksum_dir) if checksum_dir else None
        )
        
        if output_file is None:
            self.output_file = self.input_file.parent / f"{self.input_file.stem}_standardized.tsv"
        else:
            self.output_file = Path(output_file)
        
        self.original_checksum = None
        self.new_checksum = None
    
    def validate_file_exists(self) -> bool:
        """Check if input file exists."""
        if not self.input_file.exists():
            self.errors.append(f"Input file not found: {self.input_file}")
            return False
        return True
    
    def verify_source_data(self, rows: List[Dict], headers: List[str]) -> bool:
        """
        Verify that source data hasn't changed since last run.
        
        Args:
            rows: Rows read from file
            headers: Column headers
        
        Returns:
            True if verification passed or no previous checksum
        """
        previous_record = self.checksum_manager.load_checksum(self.input_file)
        
        if previous_record is None:
            self.warnings.append(
                "No previous checksum found - creating baseline"
            )
            return True
        
        print("\n🔍 Verifying source data integrity...")
        
        # Verify file hash
        file_valid, file_msg = self.checksum_manager.verify_file_integrity(
            self.input_file, previous_record
        )
        
        if file_valid:
            print(f"  ✅ File: {file_msg}")
        else:
            msg = f"File integrity check failed: {file_msg}"
            if self.strict or self.require_checksum:
                self.errors.append(msg)
                return False
            else:
                self.warnings.append(msg)
        
        # Verify content hash
        content_valid, content_msg = self.checksum_manager.verify_content_integrity(
            rows, previous_record
        )
        
        if content_valid:
            print(f"  ✅ Content: {content_msg}")
        else:
            msg = f"Content integrity check failed: {content_msg}"
            if self.strict or self.require_checksum:
                self.errors.append(msg)
                return False
            else:
                self.warnings.append(msg)
        
        # Verify metadata
        metadata_changes = self.checksum_manager.verify_metadata(
            rows, headers, previous_record
        )
        
        if metadata_changes:
            for change in metadata_changes:
                print(f"  ⚠️  {change}")
                self.warnings.append(f"Metadata: {change}")
        else:
            print("  ✅ Metadata: Unchanged")
        
        return True
    
    def read_file(self) -> Tuple[List[str], List[Dict]]:
        """Read TSV file and return headers and rows."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                headers = reader.fieldnames
                rows = list(reader)
            return headers, rows
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return None, None
    
    def standardize_column_names(self, headers: List[str]) -> List[str]:
        """Standardize column names to lowercase with underscores."""
        mapping = {
            'date': ['date', 'acquisition date', 'date acquired', 'accession date'],
            'title': ['title', 'name', 'object name', 'description'],
            'object_number': ['object number', 'object_number', 'accession number', 'catalog number', 'id', 'object id'],
            'link': ['link', 'url', 'reference', 'webpage', 'web link']
        }
        
        standardized = []
        found_columns = {col: False for col in self.EXPECTED_COLUMNS}
        
        for header in headers:
            header_lower = header.lower().strip()
            matched = False
            
            for standard_name, variations in mapping.items():
                if header_lower in variations:
                    standardized.append(standard_name)
                    found_columns[standard_name] = True
                    matched = True
                    if header != standard_name:
                        self.warnings.append(f"Renamed column '{header}' -> '{standard_name}'")
                    break
            
            if not matched:
                self.warnings.append(f"Unknown column '{header}' - preserved")
                standardized.append(header_lower.replace(' ', '_'))
        
        missing = [col for col in self.EXPECTED_COLUMNS if not found_columns[col]]
        if missing:
            msg = f"Missing required columns: {', '.join(missing)}"
            if self.strict:
                self.errors.append(msg)
            else:
                self.warnings.append(msg)
        
        return standardized
    
    def standardize_date(self, date_str: str) -> str:
        """Standardize date to YYYY-MM-DD format."""
        if not date_str or not date_str.strip():
            return ""
        
        date_str = date_str.strip()
        formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
            '%m-%d-%Y', '%d-%m-%Y', '%B %d, %Y', '%b %d, %Y', '%Y',
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        self.warnings.append(f"Could not parse date '{date_str}'")
        return date_str
    
    def standardize_title(self, title: str) -> str:
        """Standardize title: trim whitespace, proper capitalization."""
        if not title:
            return ""
        title = title.strip()
        title = ' '.join(word.capitalize() for word in title.split())
        return title
    
    def standardize_object_number(self, obj_num: str) -> str:
        """Standardize object number: remove extra spaces."""
        if not obj_num:
            return ""
        obj_num = ' '.join(obj_num.split()).strip()
        return obj_num
    
    def standardize_link(self, link: str) -> str:
        """Standardize link: trim whitespace, validate."""
        if not link:
            return ""
        link = link.strip()
        if link and not link.startswith(('http://', 'https://', 'ftp://')):
            self.warnings.append(f"Link missing protocol: '{link}'")
        return link
    
    def standardize_row(self, row: Dict, headers: List[str]) -> Dict:
        """Standardize a single row of data."""
        standardized = {}
        
        for header in headers:
            value = row.get(header, "")
            
            if header == 'date':
                standardized[header] = self.standardize_date(value)
            elif header == 'title':
                standardized[header] = self.standardize_title(value)
            elif header == 'object_number':
                standardized[header] = self.standardize_object_number(value)
            elif header == 'link':
                standardized[header] = self.standardize_link(value)
            else:
                standardized[header] = value.strip() if isinstance(value, str) else value
        
        return standardized
    
    def remove_duplicates(self, rows: List[Dict]) -> Tuple[List[Dict], int]:
        """Remove duplicate rows based on object_number."""
        seen = set()
        cleaned = []
        duplicates = 0
        
        for row in rows:
            obj_num = row.get('object_number', '')
            if obj_num and obj_num in seen:
                duplicates += 1
                self.warnings.append(f"Duplicate removed: '{obj_num}'")
            else:
                if obj_num:
                    seen.add(obj_num)
                cleaned.append(row)
        
        return cleaned, duplicates
    
    def validate_rows(self, rows: List[Dict]) -> int:
        """Validate rows for missing required fields."""
        errors_found = 0
        
        for i, row in enumerate(rows, 1):
            if not row.get('object_number', '').strip():
                msg = f"Row {i}: Missing object_number"
                errors_found += 1
                if self.strict:
                    self.errors.append(msg)
                else:
                    self.warnings.append(msg)
        
        return errors_found
    
    def write_file(self, rows: List[Dict], headers: List[str]) -> bool:
        """Write standardized data to output file."""
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers, delimiter='\t')
                writer.writeheader()
                writer.writerows(rows)
            return True
        except Exception as e:
            self.errors.append(f"Error writing output file: {e}")
            return False
    
    def save_checksums(self, rows: List[Dict], headers: List[str]) -> bool:
        """Save checksums for future verification."""
        record = self.checksum_manager.create_checksum_record(
            self.input_file, rows, headers
        )
        self.new_checksum = record
        return self.checksum_manager.save_checksum(self.input_file, record)
    
    def run(self) -> bool:
        """Execute the standardization process."""
        if not self.validate_file_exists():
            return False
        
        # Read original file
        headers, rows = self.read_file()
        if headers is None:
            return False
        
        print(f"Read {len(rows)} rows from {self.input_file}")
        
        # Verify source data integrity
        if not self.verify_source_data(rows, headers):
            return False
        
        # Standardize column names
        headers = self.standardize_column_names(headers)
        
        # Standardize each row
        standardized_rows = [self.standardize_row(row, headers) for row in rows]
        
        # Remove duplicates
        standardized_rows, duplicates_removed = self.remove_duplicates(standardized_rows)
        
        # Validate rows
        validation_errors = self.validate_rows(standardized_rows)
        
        # Write output
        if not self.write_file(standardized_rows, headers):
            return False
        
        # Save checksums for next run
        if not self.save_checksums(rows, headers):
            self.warnings.append("Failed to save checksum record")
        
        print(f"Successfully standardized {len(standardized_rows)} rows")
        if duplicates_removed:
            print(f"Removed {duplicates_removed} duplicate entries")
        
        return True
    
    def print_report(self):
        """Print standardization report."""
        print("\n" + "="*60)
        print("STANDARDIZATION REPORT")
        print("="*60)
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"  • {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if not self.warnings and not self.errors:
            print("\n✅ No issues found!")
        
        if self.new_checksum:
            print("\n📋 Checksum Information:")
            checksum_file = self.checksum_manager.get_checksum_file(self.input_file)
            print(f"  File hash:    {self.new_checksum['file_hash']['value'][:16]}...")
            print(f"  Content hash: {self.new_checksum['content_hash']['value'][:16]}...")
            print(f"  Stored in:    {checksum_file}")
        
        print(f"\nOutput file: {self.output_file}")
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory TSV files with checksum verification'
    )
    parser.add_argument('input', help='Input TSV file path')
    parser.add_argument('-o', '--output', help='Output TSV file path')
    parser.add_argument('-s', '--strict', action='store_true',
                       help='Fail on any issues')
    parser.add_argument('-c', '--checksum-dir', help='Directory for checksum files')
    parser.add_argument('-r', '--require-checksum', action='store_true',
                       help='Fail if previous checksum not found')
    parser.add_argument('-v', '--verify-only', action='store_true',
                       help='Only verify checksums, don\'t standardize')
    
    args = parser.parse_args()
    
    standardizer = InventoryStandardizer(
        args.input, args.output, args.strict, args.checksum_dir, args.require_checksum
    )
    
    if args.verify_only:
        headers, rows = standardizer.read_file()
        if headers is not None:
            standardizer.verify_source_data(rows, headers)
    else:
        success = standardizer.run()
        if args.strict and standardizer.errors:
            success = False
    
    standardizer.print_report()
    sys.exit(0 if not standardizer.errors else 1)


if __name__ == '__main__':
    main()
```

## Usage Examples

**First run (creates baseline checksums):**
```bash
python standardizer.py inventory.tsv
```

**Verify data hasn't changed:**
```bash
python standardizer.py inventory.tsv --verify-only
```

**Require previous checksum (fail if source changed):**
```bash
python standardizer.py inventory.tsv --require-checksum
```

**Custom checksum directory:**
```bash
python standardizer.py inventory.tsv --checksum-dir ./checksums
```

## Checksum File Structure

Stored as `.checksums/inventory.checksum.json`:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "source_file": "/path/to/inventory.tsv",
  "file_hash": {
    "algorithm": "sha256",
    "value": "abc123def456..."
  },
  "content_hash": {
    "algorithm": "sha256",
    "value": "xyz789uvw123..."
  },
  "metadata": {
    "row_count": 150,
    "column_count": 4,
    "columns": ["date", "title", "object_number", "link"],
    "file_size": 25600,
    "file_modified": "2024-01-15T09:45:30.123456"
  }
}
```

## Key Features

🔒 **Two-level verification:**
- **File hash** - Detects any byte-level changes
- **Content hash** - Detects logical changes (independent of order)

📊 **Metadata tracking:**
- Row count changes
- Column additions/removals
- File size and modification time

⚙️ **Flexible modes:**
- `--verify-only` - Check without processing
- `--require-checksum` - Enforce verification
- `--strict` - Fail on any warning

✅ **Production-ready:**
- JSON-based checksum storage
- Deterministic hashing (row order independent)
- Detailed change reporting
