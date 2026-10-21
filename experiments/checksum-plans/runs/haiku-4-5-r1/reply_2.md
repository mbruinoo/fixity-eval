# Museum Inventory Standardizer with Checksum Verification

Here's an enhanced version with comprehensive checksum functionality:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksum Verification
Standardizes museum inventory .tsv files with checksum validation.
"""

import csv
import sys
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import argparse


class ChecksumManager:
    """Manages checksums for inventory items."""
    
    @staticmethod
    def hash_value(value: str) -> str:
        """
        Create SHA256 hash of a value.
        
        Args:
            value: String to hash
        
        Returns:
            Hex digest of SHA256 hash
        """
        if not value:
            return hashlib.sha256(b'').hexdigest()
        return hashlib.sha256(value.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_row(row: Dict, fields: List[str] = None) -> str:
        """
        Create hash of entire row.
        
        Args:
            row: Dictionary of row data
            fields: Specific fields to hash (default: all)
        
        Returns:
            Hex digest of SHA256 hash
        """
        if fields is None:
            fields = sorted(row.keys())
        
        # Create canonical representation
        row_data = '|'.join(
            f"{field}:{row.get(field, '')}"
            for field in sorted(fields)
        )
        
        return hashlib.sha256(row_data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_file(filepath: Path) -> str:
        """
        Create hash of entire file.
        
        Args:
            filepath: Path to file
        
        Returns:
            Hex digest of SHA256 hash
        """
        sha256 = hashlib.sha256()
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        
        return sha256.hexdigest()


class InventoryStandardizer:
    """Standardizes museum inventory data with checksum tracking."""
    
    REQUIRED_COLUMNS = {'date', 'title', 'object_number', 'link'}
    
    def __init__(self, input_file: str, output_file: str = None, 
                 checksum_file: str = None, verbose: bool = False):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input .tsv file
            output_file: Path to output .tsv file
            checksum_file: Path to checksum metadata file (default: input_checksums.json)
            verbose: Print detailed processing information
        """
        self.input_file = Path(input_file)
        self.verbose = verbose
        
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        if output_file is None:
            self.output_file = self.input_file.parent / f"{self.input_file.stem}_standardized.tsv"
        else:
            self.output_file = Path(output_file)
        
        if checksum_file is None:
            self.checksum_file = self.input_file.parent / f"{self.input_file.stem}_checksums.json"
        else:
            self.checksum_file = Path(checksum_file)
        
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_rows': 0,
            'valid_rows': 0,
            'invalid_rows': 0,
            'standardized_dates': 0,
            'fixed_links': 0,
            'trimmed_titles': 0,
        }
        
        # Checksum tracking
        self.source_checksums = {}  # Original row checksums
        self.standard_checksums = {}  # Standardized row checksums
        self.change_log = []  # Track what changed in each row
    
    def log(self, message: str, level: str = "INFO"):
        """Print log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def read_inventory(self) -> Tuple[List[str], List[Dict]]:
        """
        Read the TSV inventory file.
        
        Returns:
            Tuple of (fieldnames, rows)
        """
        self.log(f"Reading inventory from {self.input_file}")
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                fieldnames = reader.fieldnames or []
                rows = list(reader)
            
            self.stats['total_rows'] = len(rows)
            self.log(f"Found {len(rows)} rows with columns: {', '.join(fieldnames)}")
            return fieldnames, rows
        
        except Exception as e:
            raise Exception(f"Error reading file: {e}")
    
    def validate_columns(self, fieldnames: List[str]) -> bool:
        """
        Validate that all required columns are present.
        
        Args:
            fieldnames: List of column names from the file
        
        Returns:
            True if valid, False otherwise
        """
        fieldnames_lower = {f.lower().strip() for f in fieldnames}
        missing = self.REQUIRED_COLUMNS - fieldnames_lower
        
        if missing:
            self.errors.append(f"Missing required columns: {', '.join(missing)}")
            return False
        
        self.log("All required columns found")
        return True
    
    def standardize_date(self, date_str: str) -> Tuple[str, bool]:
        """Standardize date format to YYYY-MM-DD."""
        if not date_str or not date_str.strip():
            return "", False
        
        date_str = date_str.strip()
        
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%m-%d-%Y',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%B %d, %Y',
            '%b %d, %Y',
            '%Y',
            '%m/%Y',
            '%m-%Y',
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                if len(date_str) == 4:
                    return parsed.strftime('%Y'), date_str != parsed.strftime('%Y')
                return parsed.strftime('%Y-%m-%d'), date_str != parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        self.warnings.append(f"Could not parse date: '{date_str}'")
        return date_str, False
    
    def standardize_object_number(self, obj_num: str) -> str:
        """Standardize object number format."""
        if not obj_num:
            return ""
        
        obj_num = obj_num.strip()
        obj_num = re.sub(r'\s+', ' ', obj_num)
        obj_num = re.sub(r'–|—', '-', obj_num)
        
        return obj_num
    
    def standardize_title(self, title: str) -> Tuple[str, bool]:
        """Standardize title format."""
        if not title:
            return "", False
        
        original = title
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)
        title = title.replace('"', '"').replace('"', '"')
        title = title.replace(''', "'").replace(''', "'")
        
        was_modified = original != title
        return title, was_modified
    
    def standardize_link(self, link: str) -> Tuple[str, bool]:
        """Standardize URL format."""
        if not link:
            return "", False
        
        original = link
        link = link.strip()
        
        if link and not link.startswith(('http://', 'https://', 'ftp://')):
            if link.startswith('www.'):
                link = 'https://' + link
            elif '.' in link:
                link = 'https://' + link
        
        was_modified = original != link
        return link, was_modified
    
    def standardize_row(self, row: Dict, fieldnames: List[str], 
                       row_index: int) -> Tuple[Dict, Dict]:
        """
        Standardize a single row and track changes.
        
        Args:
            row: Dictionary of row data
            fieldnames: List of column names
            row_index: Index of row for tracking
        
        Returns:
            Tuple of (standardized_row, changes_dict)
        """
        # Find actual column names (case-insensitive)
        col_map = {}
        fieldnames_lower = {f.lower(): f for f in fieldnames}
        
        for req_col in self.REQUIRED_COLUMNS:
            col_map[req_col] = fieldnames_lower.get(req_col.lower(), req_col)
        
        # Store original values for checksum
        original_values = {
            'date': row.get(col_map['date'], ''),
            'title': row.get(col_map['title'], ''),
            'object_number': row.get(col_map['object_number'], ''),
            'link': row.get(col_map['link'], ''),
        }
        
        # Calculate source checksum
        source_hash = ChecksumManager.hash_row(original_values)
        self.source_checksums[row_index] = source_hash
        
        standardized = {}
        changes = {
            'row_index': row_index,
            'source_checksum': source_hash,
            'fields_changed': {},
            'original_values': original_values.copy(),
        }
        
        # Standardize each column
        date_col = col_map['date']
        date_val, date_modified = self.standardize_date(original_values['date'])
        standardized['date'] = date_val
        if date_modified:
            self.stats['standardized_dates'] += 1
            changes['fields_changed']['date'] = {
                'original': original_values['date'],
                'standardized': date_val
            }
        
        title_col = col_map['title']
        title_val, title_modified = self.standardize_title(original_values['title'])
        standardized['title'] = title_val
        if title_modified:
            self.stats['trimmed_titles'] += 1
            changes['fields_changed']['title'] = {
                'original': original_values['title'],
                'standardized': title_val
            }
        
        obj_col = col_map['object_number']
        obj_val = self.standardize_object_number(original_values['object_number'])
        standardized['object_number'] = obj_val
        if original_values['object_number'] != obj_val:
            changes['fields_changed']['object_number'] = {
                'original': original_values['object_number'],
                'standardized': obj_val
            }
        
        link_col = col_map['link']
        link_val, link_modified = self.standardize_link(original_values['link'])
        standardized['link'] = link_val
        if link_modified:
            self.stats['fixed_links'] += 1
            changes['fields_changed']['link'] = {
                'original': original_values['link'],
                'standardized': link_val
            }
        
        # Calculate standardized checksum
        standard_hash = ChecksumManager.hash_row(standardized)
        changes['standard_checksum'] = standard_hash
        
        self.standard_checksums[row_index] = standard_hash
        self.change_log.append(changes)
        
        return standardized, changes
    
    def validate_row(self, row: Dict) -> bool:
        """Validate that a row has minimum required data."""
        if not row.get('title', '').strip():
            return False
        if not row.get('object_number', '').strip():
            return False
        
        return True
    
    def process(self) -> bool:
        """
        Process the inventory file and create standardized output.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read file
            fieldnames, rows = self.read_inventory()
            
            # Validate columns
            if not self.validate_columns(fieldnames):
                return False
            
            # Calculate source file hash
            source_file_hash = ChecksumManager.hash_file(self.input_file)
            self.log(f"Source file checksum: {source_file_hash}")
            
            # Standardize rows
            standardized_rows = []
            for i, row in enumerate(rows):
                try:
                    standardized, changes = self.standardize_row(row, fieldnames, i)
                    
                    if self.validate_row(standardized):
                        standardized_rows.append(standardized)
                        self.stats['valid_rows'] += 1
                    else:
                        self.stats['invalid_rows'] += 1
                        self.log(f"Row {i}: Skipped invalid row", "WARNING")
                
                except Exception as e:
                    self.stats['invalid_rows'] += 1
                    self.log(f"Row {i}: {e}", "ERROR")
            
            # Write output file
            self.write_inventory(standardized_rows)
            
            # Write checksums
            self.write_checksums(source_file_hash)
            
            return True
        
        except Exception as e:
            self.errors.append(str(e))
            return False
    
    def write_inventory(self, rows: List[Dict]) -> None:
        """Write standardized inventory to output file."""
        self.log(f"Writing standardized inventory to {self.output_file}")
        
        fieldnames = ['date', 'title', 'object_number', 'link']
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            writer.writerows(rows)
        
        self.log(f"Successfully wrote {len(rows)} rows")
    
    def write_checksums(self, source_file_hash: str) -> None:
        """
        Write checksum metadata to JSON file.
        
        Args:
            source_file_hash: Hash of source file
        """
        self.log(f"Writing checksums to {self.checksum_file}")
        
        # Calculate output file hash
        output_file_hash = ChecksumManager.hash_file(self.output_file)
        
        checksum_data = {
            'metadata': {
                'created': datetime.now().isoformat(),
                'source_file': str(self.input_file),
                'output_file': str(self.output_file),
                'source_file_checksum': source_file_hash,
                'output_file_checksum': output_file_hash,
                'total_rows_processed': self.stats['total_rows'],
                'valid_rows': self.stats['valid_rows'],
                'invalid_rows': self.stats['invalid_rows'],
            },
            'row_checksums': {
                'source': self.source_checksums,
                'standardized': self.standard_checksums,
            },
            'changes': self.change_log,
            'statistics': self.stats,
        }
        
        with open(self.checksum_file, 'w', encoding='utf-8') as f:
            json.dump(checksum_data, f, indent=2)
        
        self.log(f"Output file checksum: {output_file_hash}")
    
    def print_report(self) -> None:
        """Print standardization report."""
        print("\n" + "="*60)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("="*60)
        print(f"\nInput file:    {self.input_file}")
        print(f"Output file:   {self.output_file}")
        print(f"Checksum file: {self.checksum_file}")
        print(f"\nStatistics:")
        print(f"  Total rows processed:     {self.stats['total_rows']}")
        print(f"  Valid rows:               {self.stats['valid_rows']}")
        print(f"  Invalid rows (skipped):   {self.stats['invalid_rows']}")
        print(f"  Standardized dates:       {self.stats['standardized_dates']}")
        print(f"  Fixed URLs:               {self.stats['fixed_links']}")
        print(f"  Trimmed titles:           {self.stats['trimmed_titles']}")
        
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        print("\n" + "="*60 + "\n")


class ChecksumVerifier:
    """Verifies standardized data against source checksums."""
    
    def __init__(self, checksum_file: str, verbose: bool = False):
        """
        Initialize the verifier.
        
        Args:
            checksum_file: Path to checksum JSON file
            verbose: Print detailed information
        """
        self.checksum_file = Path(checksum_file)
        self.verbose = verbose
        self.checksum_data = None
        
        if not self.checksum_file.exists():
            raise FileNotFoundError(f"Checksum file not found: {checksum_file}")
        
        self._load_checksums()
    
    def _load_checksums(self) -> None:
        """Load checksum data from file."""
        with open(self.checksum_file, 'r', encoding='utf-8') as f:
            self.checksum_data = json.load(f)
    
    def log(self, message: str):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(message)
    
    def verify_source_file(self) -> bool:
        """
        Verify that source file hasn't been modified.
        
        Returns:
            True if source file is valid, False otherwise
        """
        source_file = Path(self.checksum_data['metadata']['source_file'])
        
        if not source_file.exists():
            print(f"Error: Source file not found: {source_file}")
            return False
        
        current_hash = ChecksumManager.hash_file(source_file)
        original_hash = self.checksum_data['metadata']['source_file_checksum']
        
        if current_hash == original_hash:
            print(f"✓ Source file verified: {source_file}")
            return True
        else:
            print(f"✗ Source file has been modified: {source_file}")
            print(f"  Original checksum: {original_hash}")
            print(f"  Current checksum:  {current_hash}")
            return False
    
    def verify_output_file(self) -> bool:
        """
        Verify that output file hasn't been modified.
        
        Returns:
            True if output file is valid, False otherwise
        """
        output_file = Path(self.checksum_data['metadata']['output_file'])
        
        if not output_file.exists():
            print(f"Error: Output file not found: {output_file}")
            return False
        
        current_hash = ChecksumManager.hash_file(output_file)
        original_hash = self.checksum_data['metadata']['output_file_checksum']
        
        if current_hash == original_hash:
            print(f"✓ Output file verified: {output_file}")
            return True
        else:
            print(f"✗ Output file has been modified: {output_file}")
            print(f"  Original checksum: {original_hash}")
            print(f"  Current checksum:  {current_hash}")
            return False
    
    def verify_row(self, row_index: int, row_data: Dict) -> bool:
        """
        Verify a specific row against stored checksum.
        
        Args:
            row_index: Index of row
            row_data: Row data dictionary
        
        Returns:
            True if row matches checksum, False otherwise
        """
        current_hash = ChecksumManager.hash_row(row_data)
        stored_hash = self.checksum_data['row_checksums']['standardized'].get(str(row_index))
        
        return current_hash == stored_hash
    
    def get_changes_for_row(self, row_index: int) -> Dict:
        """
        Get the changes made to a specific row.
        
        Args:
            row_index: Index of row
        
        Returns:
            Dictionary of changes
        """
        for change in self.checksum_data['changes']:
            if change['row_index'] == row_index:
                return change
        return None
    
    def print_verification_report(self) -> None:
        """Print comprehensive verification report."""
        print("\n" + "="*60)
        print("CHECKSUM VERIFICATION REPORT")
        print("="*60)
        
        metadata = self.checksum_data['metadata']
        print(f"\nProcessing Information:")
        print(f"  Created: {metadata['created']}")
        print(f"  Source:  {metadata['source_file']}")
        print(f"  Output:  {metadata['output_file']}")
        
        print(f"\nFile Verification:")
        source_valid = self.verify_source_file()
        output_valid = self.verify_output_file()
        
        print(f"\nStatistics:")
        print(f"  Total rows: {metadata['total_rows_processed']}")
        print(f"  Valid rows: {metadata['valid_rows']}")
        print(f"  Invalid rows: {metadata['invalid_rows']}")
        
        print(f"\nChanges Summary:")
        changes = self.checksum_data['changes']
        rows_with_changes = sum(1 for c in changes if c['fields_changed'])
        print(f"  Rows with changes: {rows_with_changes}/{len(changes)}")
        
        field_change_counts = {}
        for change in changes:
            for field in change['fields_changed'].keys():
                field_change_counts[field] = field_change_counts.get(field, 0) + 1
        
        if field_change_counts:
            print(f"\n  Field-level changes:")
            for field, count in sorted(field_change_counts.items()):
                print(f"    {field}: {count} rows")
        
        print(f"\nSample Changes (first 3):")
        for change in changes[:3]:
            if change['fields_changed']:
                print(f"\n  Row {change['row_index']}:")
                for field, mods in change['fields_changed'].items():
                    print(f"    {field}:")
                    print(f"      Original:     {mods['original'][:50]}")
                    print(f"      Standardized: {mods['standardized'][:50]}")
        
        print(f"\nOverall Status: {'✓ Valid' if source_valid and output_valid else '✗ Invalid'}")
        print("\n" + "="*60 + "\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory spreadsheets with checksum verification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standardize and create checksums
  python standardizer.py inventory.tsv

  # Standardize with custom output
  python standardizer.py inventory.tsv -o output.tsv

  # Verify checksums
  python standardizer.py --verify inventory_checksums.json

  # Verbose processing
  python standardizer.py inventory.tsv -v
        """
    )
    
    parser.add_argument('input_file', nargs='?', help='Input .tsv file path')
    parser.add_argument('-o', '--output', dest='output_file',
                       help='Output .tsv file path')
    parser.add_argument('-c', '--checksums', dest='checksum_file',
                       help='Checksum metadata file path')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Print detailed processing information')
    parser.add_argument('--verify', dest='verify_checksums',
                       help='Verify against checksum file')
    
    args = parser.parse_args()
    
    try:
        if args.verify_checksums:
            # Verification mode
            verifier = ChecksumVerifier(args.verify_checksums, verbose=args.verbose)
            verifier.print_verification_report()
        else:
            # Standardization mode
            if not args.input_file:
                parser.error("input_file is required for standardization mode")
            
            standardizer = InventoryStandardizer(
                input_file=args.input_file,
                output_file=args.output_file,
                checksum_file=args.checksum_file,
                verbose=args.verbose
            )
            
            success = standardizer.process()
            standardizer.print_report()
            
            sys.exit(0 if success else 1)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## Usage Examples

```bash
# Standardize and create checksums
python standardizer.py inventory.tsv

# Standardize with custom output and checksum files
python standardizer.py inventory.tsv -o standardized.tsv -c my_checksums.json

# Verbose mode
python standardizer.py inventory.tsv -v

# Verify checksums later
python standardizer.py --verify inventory_checksums.json

# Verify with verbose output
python standardizer.py --verify inventory_checksums.json -v
```

## Sample Checksum File Output

```json
{
  "metadata": {
    "created": "2024-01-15T10:30:45.123456",
    "source_file": "inventory.tsv",
    "output_file": "inventory_standardized.tsv",
    "source_file_checksum": "abc123def456...",
    "output_file_checksum": "xyz789uvw012...",
    "total_rows_processed": 100,
    "valid_rows": 98,
    "invalid_rows": 2
  },
  "row_checksums": {
    "source": {
      "0": "hash_of_original_row_0",
      "1": "hash_of_original_row_1"
    },
    "standardized": {
      "0": "hash_of_standard_row_0",
      "1": "hash_of_standard_row_1"
    }
  },
  "changes": [
    {
      "row_index": 0,
      "source_checksum": "hash_of_original_row_0",
      "standard_checksum": "hash_of_standard_row_0",
      "fields_changed": {
        "date": {
          "original": "1/15/2023",
          "standardized": "2023-01-15"
        }
      },
      "original_values": {
        "date": "1/15/2023",
        "title": "Ancient Vase",
        "object_number": "2023.001.A",
        "link": "www.museum.org/item1"
      }
    }
  ],
  "statistics": {
    "total_rows": 100,
    "valid_rows": 98,
    "invalid_rows": 2,
    "standardized_dates": 45,
    "fixed_links": 32,
    "trimmed_titles": 12
  }
}
```

## Key Features

1. **File-Level Checksums**: SHA256 hash of entire source and output files
2. **Row-Level Checksums**: Individual checksums for each row before and after standardization
3. **Change Tracking**: Detailed log of what changed in each field
4. **Verification Mode**: Verify that files haven't been modified since processing
5. **Audit Trail**: Complete record of all transformations
6. **Integrity Checking**: Detect any modifications to source or output files
7. **JSON Report**: Machine-readable checksum metadata for integration with other tools
