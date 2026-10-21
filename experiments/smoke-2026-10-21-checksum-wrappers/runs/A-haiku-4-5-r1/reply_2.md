# Museum Inventory Standardizer with Checksum Verification

Here's an enhanced version with checksum support:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksum Verification

Standardizes museum inventory TSV files with optional checksum verification
to detect changes in source data.
"""

import csv
import sys
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse


class ChecksumManager:
    """Manage checksums for inventory verification."""
    
    CHECKSUM_ALGORITHMS = ['sha256', 'sha1', 'md5']
    DEFAULT_ALGORITHM = 'sha256'
    
    def __init__(self, checksum_file: Optional[Path] = None, algorithm: str = 'sha256'):
        """
        Initialize checksum manager.
        
        Args:
            checksum_file: Path to store/load checksums (JSON format)
            algorithm: Hash algorithm to use (sha256, sha1, md5)
        """
        if algorithm not in self.CHECKSUM_ALGORITHMS:
            raise ValueError(f"Algorithm must be one of {self.CHECKSUM_ALGORITHMS}")
        
        self.checksum_file = checksum_file
        self.algorithm = algorithm
        self.checksums = {}
        self.load_checksums()
    
    def load_checksums(self):
        """Load existing checksums from file."""
        if self.checksum_file and self.checksum_file.exists():
            try:
                with open(self.checksum_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.checksums = data.get('checksums', {})
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load checksums: {e}")
                self.checksums = {}
    
    def save_checksums(self):
        """Save checksums to file."""
        if not self.checksum_file:
            return
        
        try:
            self.checksum_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.checksum_file, 'w', encoding='utf-8') as f:
                data = {
                    'algorithm': self.algorithm,
                    'timestamp': datetime.now().isoformat(),
                    'checksums': self.checksums
                }
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save checksums: {e}")
    
    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate checksum of entire file."""
        hash_obj = hashlib.new(self.algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except IOError as e:
            raise IOError(f"Could not calculate file checksum: {e}")
    
    def calculate_row_checksum(self, row: Dict[str, str]) -> str:
        """Calculate checksum of a single row."""
        # Create consistent string representation
        row_str = json.dumps(row, sort_keys=True, separators=(',', ':'))
        hash_obj = hashlib.new(self.algorithm)
        hash_obj.update(row_str.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def verify_file_integrity(self, file_path: Path) -> Tuple[bool, str]:
        """
        Verify file hasn't changed since last processing.
        
        Returns:
            Tuple of (is_valid, status_message)
        """
        file_key = str(file_path.resolve())
        current_checksum = self.calculate_file_checksum(file_path)
        
        if file_key not in self.checksums:
            return True, f"No previous checksum found (new file)"
        
        previous_checksum = self.checksums[file_key]['file_checksum']
        
        if current_checksum == previous_checksum:
            return True, "File integrity verified (unchanged)"
        else:
            return False, "File has changed since last processing"
    
    def update_file_checksum(self, file_path: Path, row_checksums: Dict[str, str]):
        """Update stored checksum for file."""
        file_key = str(file_path.resolve())
        file_checksum = self.calculate_file_checksum(file_path)
        
        self.checksums[file_key] = {
            'file_checksum': file_checksum,
            'algorithm': self.algorithm,
            'timestamp': datetime.now().isoformat(),
            'row_count': len(row_checksums),
            'row_checksums': row_checksums
        }
    
    def verify_row_changes(self, file_path: Path, current_rows: List[Dict[str, str]]) -> Dict:
        """
        Detect which rows have changed.
        
        Returns:
            Dict with changed rows and their status
        """
        file_key = str(file_path.resolve())
        changes = {
            'unchanged': [],
            'modified': [],
            'new': [],
            'deleted': []
        }
        
        if file_key not in self.checksums:
            # All rows are new
            for i, row in enumerate(current_rows):
                changes['new'].append({
                    'index': i,
                    'checksum': self.calculate_row_checksum(row)
                })
            return changes
        
        previous_data = self.checksums[file_key]
        previous_checksums = previous_data.get('row_checksums', {})
        
        current_checksums = {}
        for i, row in enumerate(current_rows):
            checksum = self.calculate_row_checksum(row)
            current_checksums[str(i)] = checksum
            
            prev_checksum = previous_checksums.get(str(i))
            
            if prev_checksum is None:
                changes['new'].append({'index': i, 'checksum': checksum})
            elif prev_checksum != checksum:
                changes['modified'].append({
                    'index': i,
                    'checksum': checksum,
                    'previous_checksum': prev_checksum
                })
            else:
                changes['unchanged'].append({'index': i, 'checksum': checksum})
        
        # Detect deleted rows
        for prev_index in previous_checksums:
            if prev_index not in current_checksums:
                changes['deleted'].append({
                    'index': int(prev_index),
                    'checksum': previous_checksums[prev_index]
                })
        
        return changes


class MuseumInventoryStandardizer:
    """Standardize museum inventory spreadsheet data with checksum verification."""
    
    REQUIRED_COLUMNS = {'date', 'title', 'object_number', 'link'}
    
    def __init__(
        self,
        input_file: str,
        output_file: str = None,
        checksum_file: str = None,
        verify_checksums: bool = False,
        verbose: bool = False
    ):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file
            checksum_file: Path to checksum JSON file
            verify_checksums: Verify source data integrity
            verbose: Print detailed processing information
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else \
            self.input_file.parent / f"{self.input_file.stem}_standardized.tsv"
        
        # Set default checksum file location if not specified
        if checksum_file:
            checksum_path = Path(checksum_file)
        else:
            checksum_path = self.input_file.parent / f".{self.input_file.stem}_checksums.json"
        
        self.checksum_manager = ChecksumManager(checksum_path)
        self.verify_checksums = verify_checksums
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_rows': 0,
            'processed_rows': 0,
            'skipped_rows': 0,
            'unchanged_rows': 0,
            'modified_rows': 0,
            'new_rows': 0,
            'deleted_rows': 0,
        }
        self.raw_rows = []  # Store raw rows for checksum calculation
    
    def log(self, message: str, level: str = "INFO"):
        """Print log message if verbose is enabled."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def standardize_date(self, date_str: str) -> str:
        """Standardize date to YYYY-MM-DD format."""
        if not date_str or not date_str.strip():
            return ""
        
        date_str = date_str.strip()
        formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y",
            "%b %d, %Y", "%d %B %Y", "%d %b %Y", "%Y/%m/%d", "%d-%m-%Y",
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        self.warnings.append(f"Could not parse date: '{date_str}'")
        return date_str
    
    def standardize_title(self, title: str) -> str:
        """Standardize title formatting."""
        if not title:
            return ""
        
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)
        return title
    
    def standardize_object_number(self, obj_num: str) -> str:
        """Standardize object number."""
        if not obj_num:
            return ""
        
        obj_num = obj_num.strip().upper()
        obj_num = re.sub(r'\s+', ' ', obj_num)
        return obj_num
    
    def standardize_link(self, link: str) -> str:
        """Standardize URL."""
        if not link or not link.strip():
            return ""
        
        link = link.strip()
        
        if link and not link.startswith(('http://', 'https://', 'ftp://')):
            link = 'https://' + link
        
        if not re.match(r'https?://\S+', link):
            self.warnings.append(f"Invalid URL format: '{link}'")
        
        return link
    
    def validate_row(self, row: Dict[str, str], row_num: int) -> Tuple[bool, str]:
        """Validate a data row."""
        if not row.get('title', '').strip():
            return False, f"Row {row_num}: Missing or empty title"
        
        if not row.get('object_number', '').strip():
            return False, f"Row {row_num}: Missing or empty object number"
        
        return True, ""
    
    def process_row(self, row: Dict[str, str], row_num: int) -> Dict[str, str]:
        """Process and standardize a single row."""
        processed_row = {
            'date': self.standardize_date(row.get('date', '')),
            'title': self.standardize_title(row.get('title', '')),
            'object_number': self.standardize_object_number(row.get('object_number', '')),
            'link': self.standardize_link(row.get('link', '')),
        }
        return processed_row
    
    def read_input(self) -> List[Tuple[int, Dict[str, str]]]:
        """Read and parse input TSV file."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        self.log(f"Reading input file: {self.input_file}")
        
        # Verify file integrity if requested
        if self.verify_checksums:
            is_valid, status = self.checksum_manager.verify_file_integrity(self.input_file)
            self.log(f"File integrity check: {status}")
            if not is_valid:
                self.warnings.append(f"Source file changed: {status}")
        
        rows = []
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    raise ValueError("Empty input file")
                
                missing_cols = self.REQUIRED_COLUMNS - set(reader.fieldnames)
                if missing_cols:
                    raise ValueError(f"Missing required columns: {missing_cols}")
                
                self.log(f"Found columns: {list(reader.fieldnames)}")
                
                for row_num, row in enumerate(reader, start=2):
                    self.stats['total_rows'] += 1
                    self.raw_rows.append(row)  # Store for checksums
                    
                    is_valid, error_msg = self.validate_row(row, row_num)
                    if not is_valid:
                        self.errors.append(error_msg)
                        self.stats['skipped_rows'] += 1
                        self.log(f"Skipping: {error_msg}", "WARNING")
                        continue
                    
                    rows.append((row_num, row))
                    self.stats['processed_rows'] += 1
        
        except Exception as e:
            self.log(f"Error reading input file: {e}", "ERROR")
            raise
        
        return rows
    
    def detect_changes(self, raw_rows: List[Dict[str, str]]):
        """Detect changes in raw data since last processing."""
        changes = self.checksum_manager.verify_row_changes(self.input_file, raw_rows)
        
        self.stats['unchanged_rows'] = len(changes['unchanged'])
        self.stats['modified_rows'] = len(changes['modified'])
        self.stats['new_rows'] = len(changes['new'])
        self.stats['deleted_rows'] = len(changes['deleted'])
        
        return changes
    
    def standardize(self):
        """Main standardization process."""
        try:
            # Read input
            rows = self.read_input()
            
            # Detect changes in raw data
            self.log("Analyzing source data changes...")
            changes = self.detect_changes(self.raw_rows)
            
            # Process rows
            self.log(f"Processing {len(rows)} rows...")
            processed_rows = []
            
            for row_num, row in rows:
                processed_row = self.process_row(row, row_num)
                processed_rows.append(processed_row)
            
            # Write output
            self.log(f"Writing standardized data to: {self.output_file}")
            self.write_output(processed_rows)
            
            # Update checksums
            self.log("Updating checksums...")
            row_checksums = {
                str(i): self.checksum_manager.calculate_row_checksum(row)
                for i, row in enumerate(self.raw_rows)
            }
            self.checksum_manager.update_file_checksum(self.input_file, row_checksums)
            self.checksum_manager.save_checksums()
            
            # Print summary
            self.print_summary(changes)
            
            return True
        
        except Exception as e:
            self.log(f"Fatal error during standardization: {e}", "ERROR")
            return False
    
    def write_output(self, rows: List[Dict[str, str]]):
        """Write standardized data to output TSV file."""
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['date', 'title', 'object_number', 'link'],
                    delimiter='\t'
                )
                writer.writeheader()
                writer.writerows(rows)
            
            self.log(f"Successfully wrote {len(rows)} rows to output file")
        
        except Exception as e:
            self.log(f"Error writing output file: {e}", "ERROR")
            raise
    
    def print_summary(self, changes: Dict = None):
        """Print processing summary with checksum information."""
        print("\n" + "="*70)
        print("STANDARDIZATION SUMMARY")
        print("="*70)
        print(f"Input file:       {self.input_file}")
        print(f"Output file:      {self.output_file}")
        print(f"Checksum file:    {self.checksum_manager.checksum_file}")
        print(f"Hash algorithm:   {self.checksum_manager.algorithm.upper()}")
        
        print("\nProcessing Statistics:")
        print(f"  Total rows:       {self.stats['total_rows']}")
        print(f"  Processed rows:   {self.stats['processed_rows']}")
        print(f"  Skipped rows:     {self.stats['skipped_rows']}")
        
        if changes:
            print("\nData Change Detection:")
            print(f"  Unchanged rows:   {self.stats['unchanged_rows']}")
            print(f"  Modified rows:    {self.stats['modified_rows']}")
            print(f"  New rows:         {self.stats['new_rows']}")
            print(f"  Deleted rows:     {self.stats['deleted_rows']}")
            
            if changes['modified']:
                print(f"\n  Modified row indices: {[c['index'] for c in changes['modified']]}")
            if changes['new']:
                print(f"  New row indices: {[c['index'] for c in changes['new']]}")
            if changes['deleted']:
                print(f"  Deleted row indices: {[c['index'] for c in changes['deleted']]}")
        
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        
        if self.warnings and self.verbose:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        print("="*70 + "\n")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory TSV spreadsheets with checksum verification'
    )
    parser.add_argument(
        'input_file',
        help='Path to input TSV file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Path to output TSV file (default: input_standardized.tsv)'
    )
    parser.add_argument(
        '-c', '--checksums',
        help='Path to checksums JSON file (default: .input_checksums.json)'
    )
    parser.add_argument(
        '-v', '--verify',
        action='store_true',
        help='Verify source file integrity and detect changes'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed processing information'
    )
    parser.add_argument(
        '--algorithm',
        choices=['sha256', 'sha1', 'md5'],
        default='sha256',
        help='Hash algorithm for checksums (default: sha256)'
    )
    
    args = parser.parse_args()
    
    # Create and configure checksum manager with chosen algorithm
    standardizer = MuseumInventoryStandardizer(
        args.input_file,
        args.output,
        args.checksums,
        args.verify,
        args.verbose
    )
    
    # Update algorithm if specified
    standardizer.checksum_manager.algorithm = args.algorithm
    
    success = standardizer.standardize()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Usage Examples

### First run (create checksums):
```bash
python standardize_inventory.py input.tsv
```

### Verify and detect changes on subsequent runs:
```bash
python standardize_inventory.py input.tsv --verify
```

### With custom checksum file location:
```bash
python standardize_inventory.py input.tsv --verify -c ./checksums/inventory.json
```

### Using different hash algorithm:
```bash
python standardize_inventory.py input.tsv --verify --algorithm sha1
```

### Verbose output with change detection:
```bash
python standardize_inventory.py input.tsv --verify --verbose
```

## Checksum File Format

The `.input_checksums.json` file looks like:

```json
{
  "algorithm": "sha256",
  "timestamp": "2024-01-15T10:30:45.123456",
  "checksums": {
    "/full/path/to/input.tsv": {
      "file_checksum": "a1b2c3d4e5f6...",
      "algorithm": "sha256",
      "timestamp": "2024-01-15T10:30:45.123456",
      "row_count": 150,
      "row_checksums": {
        "0": "abc123...",
        "1": "def456...",
        "2": "ghi789..."
      }
    }
  }
}
```

## Key Features

1. **File-level checksums**: Detect if entire file has changed
2. **Row-level checksums**: Identify which specific rows changed
3. **Change tracking**: Reports new, modified, unchanged, and deleted rows
4. **Multiple algorithms**: SHA256 (default), SHA1, or MD5
5. **Persistent storage**: JSON format for easy inspection
6. **Integrity verification**: Optional on each run
7. **Detailed reporting**: Summary of all changes detected

## Benefits

- **Data quality**: Ensure source data hasn't been corrupted
- **Audit trail**: Track what changed between runs
- **Reproducibility**: Verify consistency of standardization
- **Change management**: Know exactly which rows were affected
