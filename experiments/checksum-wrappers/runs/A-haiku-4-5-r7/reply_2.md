# Museum Inventory Standardizer with Checksum Verification

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory spreadsheets (.tsv format) with checksum verification.
Validates that source data hasn't changed between runs.
"""

import sys
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import re


class ChecksumManager:
    """Manages checksums for data integrity verification."""
    
    def __init__(self, checksum_dir=None):
        """
        Initialize checksum manager.
        
        Args:
            checksum_dir: Directory to store checksum files (default: .checksums/)
        """
        self.checksum_dir = Path(checksum_dir or '.checksums')
        self.checksum_dir.mkdir(exist_ok=True)
    
    def get_checksum_file(self, input_file):
        """Get path to checksum file for input file."""
        input_path = Path(input_file)
        checksum_name = f"{input_path.stem}.checksum.json"
        return self.checksum_dir / checksum_name
    
    def calculate_file_hash(self, filepath, algorithm='sha256'):
        """
        Calculate hash of entire file.
        
        Args:
            filepath: Path to file
            algorithm: Hash algorithm ('sha256', 'md5', 'sha1')
            
        Returns:
            Hash digest string
        """
        hash_obj = hashlib.new(algorithm)
        
        with open(filepath, 'rb') as f:
            # Read in chunks for memory efficiency
            while chunk := f.read(8192):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    def calculate_row_hash(self, row_dict, algorithm='sha256'):
        """
        Calculate hash of a single row (for row-level integrity).
        
        Args:
            row_dict: Dictionary representing row
            algorithm: Hash algorithm
            
        Returns:
            Hash digest string
        """
        # Create canonical JSON representation
        row_json = json.dumps(row_dict, sort_keys=True, separators=(',', ':'))
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(row_json.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def calculate_content_hash(self, rows, algorithm='sha256'):
        """
        Calculate hash of all row content (column order independent).
        
        Args:
            rows: List of row dictionaries
            algorithm: Hash algorithm
            
        Returns:
            Hash digest string
        """
        hash_obj = hashlib.new(algorithm)
        
        for row in rows:
            # Sort keys for consistent ordering
            row_json = json.dumps(row, sort_keys=True, separators=(',', ':'))
            hash_obj.update(row_json.encode('utf-8'))
        
        return hash_obj.hexdigest()
    
    def save_checksums(self, filepath, file_hash, rows, row_hashes=None):
        """
        Save checksums to file.
        
        Args:
            filepath: Path to original file
            file_hash: Hash of entire file
            rows: List of row dictionaries
            row_hashes: Optional list of row hashes
        """
        checksum_file = self.get_checksum_file(filepath)
        
        content_hash = self.calculate_content_hash(rows)
        
        checksums = {
            'source_file': str(Path(filepath).resolve()),
            'timestamp': datetime.now().isoformat(),
            'file_hash': {
                'algorithm': 'sha256',
                'value': file_hash
            },
            'content_hash': {
                'algorithm': 'sha256',
                'value': content_hash
            },
            'row_count': len(rows),
            'row_hashes': row_hashes if row_hashes else []
        }
        
        with open(checksum_file, 'w', encoding='utf-8') as f:
            json.dump(checksums, f, indent=2)
        
        return checksum_file
    
    def load_checksums(self, filepath):
        """
        Load previously saved checksums.
        
        Args:
            filepath: Path to original file
            
        Returns:
            Dictionary of checksums or None if not found
        """
        checksum_file = self.get_checksum_file(filepath)
        
        if not checksum_file.exists():
            return None
        
        try:
            with open(checksum_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load checksum file: {e}", file=sys.stderr)
            return None
    
    def verify_file(self, filepath, saved_checksums):
        """
        Verify file hasn't changed using file hash.
        
        Args:
            filepath: Path to file to verify
            saved_checksums: Previously saved checksum data
            
        Returns:
            Tuple (is_valid, message)
        """
        if not saved_checksums:
            return False, "No previous checksums found"
        
        current_hash = self.calculate_file_hash(filepath)
        saved_hash = saved_checksums.get('file_hash', {}).get('value')
        
        if current_hash == saved_hash:
            return True, f"File unchanged (hash: {current_hash[:16]}...)"
        else:
            return False, (f"File has changed!\n"
                          f"  Previous: {saved_hash[:16]}...\n"
                          f"  Current:  {current_hash[:16]}...")
    
    def verify_content(self, rows, saved_checksums):
        """
        Verify content hasn't changed using content hash.
        
        Args:
            rows: Current rows
            saved_checksums: Previously saved checksum data
            
        Returns:
            Tuple (is_valid, message)
        """
        if not saved_checksums:
            return False, "No previous checksums found"
        
        current_hash = self.calculate_content_hash(rows)
        saved_hash = saved_checksums.get('content_hash', {}).get('value')
        
        if current_hash == saved_hash:
            return True, f"Content unchanged (hash: {current_hash[:16]}...)"
        else:
            return False, (f"Content has changed!\n"
                          f"  Previous: {saved_hash[:16]}...\n"
                          f"  Current:  {current_hash[:16]}...")
    
    def verify_row_count(self, rows, saved_checksums):
        """
        Verify row count matches previous verification.
        
        Args:
            rows: Current rows
            saved_checksums: Previously saved checksum data
            
        Returns:
            Tuple (is_valid, message)
        """
        if not saved_checksums:
            return False, "No previous checksums found"
        
        current_count = len(rows)
        saved_count = saved_checksums.get('row_count')
        
        if current_count == saved_count:
            return True, f"Row count unchanged ({current_count} rows)"
        else:
            return False, (f"Row count changed!\n"
                          f"  Previous: {saved_count} rows\n"
                          f"  Current:  {current_count} rows")


class InventoryStandardizer:
    """Standardizes museum inventory data with checksum verification."""
    
    REQUIRED_COLUMNS = ['date', 'title', 'object_number', 'link']
    
    def __init__(self, input_file, output_file=None, strict=False, 
                 verify_checksums=False, checksum_dir=None):
        """
        Initialize standardizer.
        
        Args:
            input_file: Path to input .tsv file
            output_file: Path to output .tsv file
            strict: If True, skip invalid rows instead of attempting fixes
            verify_checksums: If True, verify against previous checksums
            checksum_dir: Directory for checksum files
        """
        self.input_file = Path(input_file)
        self.strict = strict
        self.verify_checksums = verify_checksums
        
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        if output_file is None:
            output_file = self.input_file.stem + "_standardized.tsv"
        
        self.output_file = Path(output_file)
        self.checksum_manager = ChecksumManager(checksum_dir)
        
        self.errors = []
        self.warnings = []
        self.checksum_report = []
        self.stats = {
            'total_rows': 0,
            'valid_rows': 0,
            'skipped_rows': 0,
            'fixed_rows': 0
        }
    
    def standardize_date(self, date_str, row_num):
        """Standardize date to ISO format (YYYY-MM-DD)."""
        if not date_str or date_str.strip() == '':
            self.warnings.append(f"Row {row_num}: Empty date field")
            return None
        
        date_str = date_str.strip()
        formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
            '%B %d, %Y', '%b %d, %Y', '%Y-%m', '%Y',
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        self.errors.append(f"Row {row_num}: Invalid date format: '{date_str}'")
        return None
    
    def standardize_title(self, title, row_num):
        """Standardize title (trim whitespace, normalize spacing)."""
        if not title or title.strip() == '':
            self.errors.append(f"Row {row_num}: Empty title field")
            return None
        
        title = ' '.join(title.split())
        
        if len(title) < 3:
            self.errors.append(f"Row {row_num}: Title too short: '{title}'")
            return None
        
        if len(title) > 500:
            self.warnings.append(f"Row {row_num}: Title exceeds 500 chars, truncating")
            title = title[:500]
        
        return title
    
    def standardize_object_number(self, obj_num, row_num):
        """Standardize object number (remove extra whitespace, validate format)."""
        if not obj_num or obj_num.strip() == '':
            self.errors.append(f"Row {row_num}: Empty object number field")
            return None
        
        obj_num = obj_num.strip().upper()
        obj_num = re.sub(r'\s+', ' ', obj_num)
        
        if not re.match(r'^[A-Z0-9\s\.\-]+$', obj_num):
            self.errors.append(
                f"Row {row_num}: Invalid object number format: '{obj_num}'"
            )
            return None
        
        return obj_num
    
    def standardize_link(self, link, row_num):
        """Standardize link (validate URL format)."""
        if not link or link.strip() == '':
            self.warnings.append(f"Row {row_num}: Empty link field")
            return ''
        
        link = link.strip()
        
        if not link.startswith(('http://', 'https://')):
            link = 'https://' + link
        
        try:
            result = urlparse(link)
            if not all([result.scheme, result.netloc]):
                self.errors.append(f"Row {row_num}: Invalid URL: '{link}'")
                return None
        except Exception as e:
            self.errors.append(f"Row {row_num}: URL parsing error: {e}")
            return None
        
        return link
    
    def process_row(self, row, row_num):
        """Process and standardize a single row."""
        self.stats['total_rows'] += 1
        
        try:
            standardized = {}
            
            standardized['date'] = self.standardize_date(row.get('date', ''), row_num)
            standardized['title'] = self.standardize_title(row.get('title', ''), row_num)
            standardized['object_number'] = self.standardize_object_number(
                row.get('object_number', ''), row_num
            )
            standardized['link'] = self.standardize_link(row.get('link', ''), row_num)
            
            if None in standardized.values():
                if self.strict:
                    self.stats['skipped_rows'] += 1
                    return None
                else:
                    standardized = {k: v if v is not None else '' for k, v in standardized.items()}
                    self.stats['fixed_rows'] += 1
            else:
                self.stats['valid_rows'] += 1
            
            return standardized
        
        except Exception as e:
            self.errors.append(f"Row {row_num}: Unexpected error: {e}")
            self.stats['skipped_rows'] += 1
            return None
    
    def verify_source_data(self, raw_rows):
        """
        Verify source data hasn't changed using checksums.
        
        Args:
            raw_rows: List of raw row dictionaries before standardization
        """
        saved_checksums = self.checksum_manager.load_checksums(self.input_file)
        
        if not self.verify_checksums:
            self.checksum_report.append("Checksum verification disabled")
            return
        
        if not saved_checksums:
            self.checksum_report.append("No previous checksums found (first run)")
            return
        
        print("\n" + "="*60)
        print("VERIFYING SOURCE DATA INTEGRITY")
        print("="*60)
        
        # Verify file hash
        file_valid, file_msg = self.checksum_manager.verify_file(
            self.input_file, saved_checksums
        )
        print(f"File hash:    {file_msg}")
        self.checksum_report.append(f"File hash: {file_msg}")
        
        # Verify content hash
        content_valid, content_msg = self.checksum_manager.verify_content(
            raw_rows, saved_checksums
        )
        print(f"Content hash: {content_msg}")
        self.checksum_report.append(f"Content hash: {content_msg}")
        
        # Verify row count
        count_valid, count_msg = self.checksum_manager.verify_row_count(
            raw_rows, saved_checksums
        )
        print(f"Row count:    {count_msg}")
        self.checksum_report.append(f"Row count: {count_msg}")
        
        # Overall verification result
        all_valid = file_valid and content_valid and count_valid
        status = "✓ PASSED" if all_valid else "✗ FAILED"
        print(f"\nVerification: {status}")
        self.checksum_report.append(f"Overall: {status}")
        
        if not all_valid:
            print("\nWARNING: Source data has changed since last verification!")
            if not file_valid:
                print("  - File contents have been modified")
            if not content_valid:
                print("  - Row data has been modified")
            if not count_valid:
                print("  - Number of rows has changed")
        
        print("="*60 + "\n")
    
    def run(self):
        """Process the inventory file and write standardized output."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile, delimiter='\t')
                
                if not reader.fieldnames:
                    raise ValueError("Empty file or invalid format")
                
                missing_cols = set(self.REQUIRED_COLUMNS) - set(reader.fieldnames or [])
                if missing_cols:
                    raise ValueError(f"Missing required columns: {missing_cols}")
                
                # Read all rows first (needed for checksum verification)
                raw_rows = list(reader)
            
            # Verify source data before processing
            self.verify_source_data(raw_rows)
            
            # Process rows
            standardized_rows = []
            row_hashes = []
            
            for row_num, raw_row in enumerate(raw_rows, start=2):
                standardized_row = self.process_row(raw_row, row_num)
                if standardized_row:
                    standardized_rows.append(standardized_row)
                    row_hashes.append(
                        self.checksum_manager.calculate_row_hash(standardized_row)
                    )
            
            # Write output
            with open(self.output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(
                    outfile,
                    fieldnames=self.REQUIRED_COLUMNS,
                    delimiter='\t'
                )
                writer.writeheader()
                writer.writerows(standardized_rows)
            
            # Calculate and save checksums for next run
            file_hash = self.checksum_manager.calculate_file_hash(self.input_file)
            checksum_file = self.checksum_manager.save_checksums(
                self.input_file,
                file_hash,
                raw_rows,
                row_hashes=row_hashes
            )
            
            self.print_report(checksum_file)
            return True
        
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return False
    
    def print_report(self, checksum_file):
        """Print standardization and checksum report."""
        print("\n" + "="*60)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("="*60)
        print(f"Input file:    {self.input_file}")
        print(f"Output file:   {self.output_file}")
        print(f"Checksum file: {checksum_file}")
        print("-"*60)
        print(f"Total rows processed:    {self.stats['total_rows']}")
        print(f"Valid rows:              {self.stats['valid_rows']}")
        print(f"Fixed rows:              {self.stats['fixed_rows']}")
        print(f"Skipped rows:            {self.stats['skipped_rows']}")
        print("-"*60)
        
        if self.checksum_report:
            print("\nCHECKSUM VERIFICATION:")
            for report_line in self.checksum_report:
                print(f"  {report_line}")
        
        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"  • {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        if self.errors:
            print(f"\nERRORS ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"  • {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        
        print("="*60 + "\n")


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file.tsv> [options]")
        print("\nOptions:")
        print("  -o, --output FILE       Output file path")
        print("  --strict                Skip invalid rows instead of fixing")
        print("  --verify                Verify against previous checksums")
        print("  --checksum-dir DIR      Directory for checksum files")
        print("\nExamples:")
        print("  python script.py inventory.tsv --verify")
        print("  python script.py inventory.tsv -o clean.tsv --verify --strict")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = None
    strict = '--strict' in sys.argv
    verify = '--verify' in sys.argv
    checksum_dir = None
    
    # Parse additional arguments
    for i, arg in enumerate(sys.argv[2:], start=2):
        if arg in ['-o', '--output'] and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
        elif arg == '--checksum-dir' and i + 1 < len(sys.argv):
            checksum_dir = sys.argv[i + 1]
    
    standardizer = InventoryStandardizer(
        input_file,
        output_file,
        strict=strict,
        verify_checksums=verify,
        checksum_dir=checksum_dir
    )
    success = standardizer.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Usage Examples

### First run (creates checksums):
```bash
python standardizer.py inventory.tsv
```

### Verify data hasn't changed:
```bash
python standardizer.py inventory.tsv --verify
```

### Verify with strict mode:
```bash
python standardizer.py inventory.tsv --verify --strict -o clean.tsv
```

### Custom checksum directory:
```bash
python standardizer.py inventory.tsv --verify --checksum-dir ./data_checksums/
```

## Checksum File Format

Checksums are stored in `.checksums/<filename>.checksum.json`:

```json
{
  "source_file": "/path/to/inventory.tsv",
  "timestamp": "2024-01-15T10:30:45.123456",
  "file_hash": {
    "algorithm": "sha256",
    "value": "a1b2c3d4e5f6..."
  },
  "content_hash": {
    "algorithm": "sha256",
    "value": "f6e5d4c3b2a1..."
  },
  "row_count": 147,
  "row_hashes": [
    "hash_of_row_1",
    "hash_of_row_2",
    ...
  ]
}
```

## Verification Levels

1. **File Hash**: Detects any byte-level changes
2. **Content Hash**: Detects logical data changes (order-independent)
3. **Row Count**: Detects added/removed rows
4. **Row Hashes**: Detects individual row modifications

## Benefits

- **Data Integrity**: Ensures source data consistency
- **Audit Trail**: Tracks when data changed
- **Error Detection**: Catches accidental modifications
- **Reproducibility**: Verify standardization against same source data
