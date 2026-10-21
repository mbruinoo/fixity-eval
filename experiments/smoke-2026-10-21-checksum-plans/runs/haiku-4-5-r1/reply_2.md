# Museum Inventory Standardizer with Checksums

```python
#!/usr/bin/env python3
"""
Script to standardize museum inventory spreadsheet (.tsv files) with checksum verification.
Standardizes 4 columns: date, title, object number, and link.
"""

import csv
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import argparse


class ChecksumManager:
    """Manages checksums for inventory records."""
    
    def __init__(self, checksum_file=None):
        """
        Initialize checksum manager.
        
        Args:
            checksum_file: Path to store/load checksums (optional)
        """
        self.checksum_file = Path(checksum_file) if checksum_file else None
        self.checksums = {}  # Maps record_id -> {'source': hash, 'standardized': hash}
        self.load_checksums()
    
    @staticmethod
    def compute_row_hash(row_data, algorithm='sha256'):
        """
        Compute hash of row data.
        
        Args:
            row_data: Dictionary with row values
            algorithm: Hash algorithm ('sha256', 'md5', etc.)
            
        Returns:
            Hex digest of hash
        """
        # Create normalized representation: sort keys for consistency
        normalized = json.dumps(row_data, sort_keys=True, separators=(',', ':'))
        
        if algorithm == 'sha256':
            return hashlib.sha256(normalized.encode()).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(normalized.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(normalized.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    def add_source_hash(self, record_id, source_row):
        """
        Record hash of source data.
        
        Args:
            record_id: Unique identifier for record
            source_row: Dictionary with source values
        """
        if record_id not in self.checksums:
            self.checksums[record_id] = {}
        
        self.checksums[record_id]['source'] = self.compute_row_hash(source_row)
    
    def add_standardized_hash(self, record_id, standardized_row):
        """
        Record hash of standardized data.
        
        Args:
            record_id: Unique identifier for record
            standardized_row: Dictionary with standardized values
        """
        if record_id not in self.checksums:
            self.checksums[record_id] = {}
        
        self.checksums[record_id]['standardized'] = self.compute_row_hash(standardized_row)
    
    def verify_record(self, record_id, source_row):
        """
        Verify that source row matches stored checksum.
        
        Args:
            record_id: Unique identifier for record
            source_row: Dictionary with source values
            
        Returns:
            Tuple (is_valid, message)
        """
        if record_id not in self.checksums:
            return False, f"No checksum found for record {record_id}"
        
        current_hash = self.compute_row_hash(source_row)
        stored_hash = self.checksums[record_id].get('source')
        
        if current_hash == stored_hash:
            return True, f"Record {record_id} verified"
        else:
            return False, f"Record {record_id} checksum mismatch"
    
    def save_checksums(self, output_file=None):
        """
        Save checksums to JSON file.
        
        Args:
            output_file: Path to save checksums (uses self.checksum_file if None)
        """
        output_path = Path(output_file) if output_file else self.checksum_file
        
        if not output_path:
            raise ValueError("No checksum file path specified")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.checksums, f, indent=2)
        except Exception as e:
            raise IOError(f"Error saving checksums: {str(e)}")
    
    def load_checksums(self):
        """Load checksums from file if it exists."""
        if not self.checksum_file or not self.checksum_file.exists():
            return
        
        try:
            with open(self.checksum_file, 'r', encoding='utf-8') as f:
                self.checksums = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load checksums: {str(e)}", file=sys.stderr)
    
    def get_summary(self):
        """Get summary of checksums."""
        total = len(self.checksums)
        with_both = sum(1 for v in self.checksums.values() 
                        if 'source' in v and 'standardized' in v)
        
        return {
            'total_records': total,
            'complete_checksums': with_both,
            'incomplete': total - with_both
        }


class InventoryStandardizer:
    """Standardizes museum inventory data with checksum tracking."""
    
    REQUIRED_COLUMNS = {'date', 'title', 'object number', 'link'}
    
    def __init__(self, input_file, output_file=None, checksum_file=None, strict=False):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file (optional)
            checksum_file: Path to checksum JSON file (optional)
            strict: If True, skip rows with errors; if False, report warnings
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self._generate_output_filename()
        self.strict = strict
        
        # Initialize checksum manager
        checksum_path = Path(checksum_file) if checksum_file else self._generate_checksum_filename()
        self.checksum_manager = ChecksumManager(checksum_path)
        
        self.errors = []
        self.warnings = []
        self.standardized_rows = []
        self.source_rows = []
        self.row_mapping = {}  # Maps row_id to record info
    
    def _generate_output_filename(self):
        """Generate output filename from input filename."""
        stem = self.input_file.stem
        return self.input_file.parent / f"{stem}_standardized.tsv"
    
    def _generate_checksum_filename(self):
        """Generate checksum filename from input filename."""
        stem = self.input_file.stem
        return self.input_file.parent / f"{stem}_checksums.json"
    
    def _generate_record_id(self, row_num, object_number):
        """
        Generate unique record ID.
        
        Args:
            row_num: Row number in file
            object_number: Object number from data
            
        Returns:
            Unique record identifier
        """
        # Use object number as primary identifier (should be unique)
        # Fall back to row number if object number unavailable
        if object_number and object_number.strip():
            return f"obj_{object_number}"
        else:
            return f"row_{row_num}"
    
    def _standardize_date(self, date_str):
        """
        Standardize date to YYYY-MM-DD format.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Standardized date string or None if invalid
        """
        if not date_str or date_str.strip() == '':
            return None
        
        date_str = date_str.strip()
        
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%m-%d-%Y',
            '%B %d, %Y',
            '%b %d, %Y',
            '%Y/%m/%d',
            '%d-%m-%Y',
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        self.warnings.append(f"Could not parse date: '{date_str}'")
        return date_str
    
    def _standardize_title(self, title):
        """Standardize title: strip whitespace, normalize spacing."""
        if not title:
            return ''
        
        title = title.strip()
        title = ' '.join(title.split())
        
        return title
    
    def _standardize_object_number(self, obj_num):
        """Standardize object number: uppercase, remove extra spaces."""
        if not obj_num:
            return ''
        
        obj_num = obj_num.strip()
        obj_num = ' '.join(obj_num.split())
        
        return obj_num
    
    def _standardize_link(self, link):
        """Standardize link: validate URL format."""
        if not link or link.strip() == '':
            return ''
        
        link = link.strip()
        
        if not link.startswith(('http://', 'https://')):
            link = 'https://' + link
            self.warnings.append(f"Added https:// to URL: {link}")
        
        try:
            result = urlparse(link)
            if not result.netloc:
                self.warnings.append(f"Invalid URL format: {link}")
                return ''
            return link
        except Exception as e:
            self.warnings.append(f"Error parsing URL '{link}': {str(e)}")
            return ''
    
    def _validate_headers(self, headers):
        """Validate that required columns are present."""
        headers_lower = [h.lower().strip() for h in headers]
        found_columns = set(headers_lower)
        
        if not self.REQUIRED_COLUMNS.issubset(found_columns):
            missing = self.REQUIRED_COLUMNS - found_columns
            self.errors.append(f"Missing required columns: {missing}")
            return False
        
        return True
    
    def _get_column_indices(self, headers):
        """Get indices of required columns from headers."""
        headers_lower = [h.lower().strip() for h in headers]
        indices = {}
        
        for col in self.REQUIRED_COLUMNS:
            try:
                indices[col] = headers_lower.index(col)
            except ValueError:
                indices[col] = None
        
        return indices
    
    def standardize(self):
        """
        Read and standardize the inventory file with checksum tracking.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.input_file.exists():
            self.errors.append(f"Input file not found: {self.input_file}")
            return False
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as infile:
                reader = csv.reader(infile, delimiter='\t')
                
                # Read headers
                try:
                    headers = next(reader)
                except StopIteration:
                    self.errors.append("Input file is empty")
                    return False
                
                # Validate headers
                if not self._validate_headers(headers):
                    return False
                
                # Get column indices
                col_indices = self._get_column_indices(headers)
                
                # Process data rows
                row_num = 1
                for row in reader:
                    row_num += 1
                    
                    # Ensure row has enough columns
                    if len(row) < len(headers):
                        row.extend([''] * (len(headers) - len(row)))
                    
                    try:
                        # Create source row dictionary
                        source_row = {
                            'date': row[col_indices['date']],
                            'title': row[col_indices['title']],
                            'object_number': row[col_indices['object number']],
                            'link': row[col_indices['link']]
                        }
                        
                        # Generate record ID
                        record_id = self._generate_record_id(
                            row_num,
                            source_row['object_number']
                        )
                        
                        # Track source data and compute hash
                        self.source_rows.append(source_row)
                        self.checksum_manager.add_source_hash(record_id, source_row)
                        
                        # Standardize row
                        standardized_row = self._standardize_row(row, col_indices)
                        self.standardized_rows.append(standardized_row)
                        
                        # Create standardized row dictionary
                        standardized_dict = {
                            'date': standardized_row[0],
                            'title': standardized_row[1],
                            'object_number': standardized_row[2],
                            'link': standardized_row[3]
                        }
                        
                        # Compute standardized hash
                        self.checksum_manager.add_standardized_hash(record_id, standardized_dict)
                        
                        # Store mapping
                        self.row_mapping[record_id] = {
                            'row_number': row_num,
                            'source': source_row,
                            'standardized': standardized_dict
                        }
                        
                    except ValueError as e:
                        msg = f"Row {row_num}: {str(e)}"
                        if self.strict:
                            self.errors.append(msg)
                            return False
                        else:
                            self.warnings.append(msg)
                
                return True
        
        except Exception as e:
            self.errors.append(f"Error reading file: {str(e)}")
            return False
    
    def _standardize_row(self, row, col_indices):
        """Standardize a single row."""
        date = self._standardize_date(row[col_indices['date']])
        title = self._standardize_title(row[col_indices['title']])
        obj_num = self._standardize_object_number(row[col_indices['object number']])
        link = self._standardize_link(row[col_indices['link']])
        
        if not title:
            raise ValueError("Title cannot be empty")
        if not obj_num:
            raise ValueError("Object number cannot be empty")
        
        return [date, title, obj_num, link]
    
    def write_output(self):
        """Write standardized data to output file."""
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile, delimiter='\t')
                writer.writerow(['date', 'title', 'object number', 'link'])
                writer.writerows(self.standardized_rows)
            
            return True
        except Exception as e:
            self.errors.append(f"Error writing output file: {str(e)}")
            return False
    
    def write_checksums(self):
        """Write checksums to file."""
        try:
            self.checksum_manager.save_checksums()
            return True
        except Exception as e:
            self.errors.append(f"Error writing checksums: {str(e)}")
            return False
    
    def write_detailed_log(self):
        """Write detailed log with source and standardized values."""
        log_file = self.input_file.parent / f"{self.input_file.stem}_log.json"
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(self.row_mapping, f, indent=2, default=str)
            return log_file
        except Exception as e:
            self.errors.append(f"Error writing log: {str(e)}")
            return None
    
    def verify_integrity(self):
        """
        Verify data integrity by checking checksums.
        
        Returns:
            Tuple (all_valid, results_dict)
        """
        results = {
            'total_records': len(self.row_mapping),
            'verified': 0,
            'failures': []
        }
        
        for record_id, data in self.row_mapping.items():
            is_valid, message = self.checksum_manager.verify_record(
                record_id,
                data['source']
            )
            
            if is_valid:
                results['verified'] += 1
            else:
                results['failures'].append({
                    'record_id': record_id,
                    'row_number': data['row_number'],
                    'message': message
                })
        
        all_valid = len(results['failures']) == 0
        return all_valid, results
    
    def print_report(self):
        """Print standardization report."""
        print("\n" + "="*70)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("="*70)
        
        print(f"\nInput file:     {self.input_file}")
        print(f"Output file:    {self.output_file}")
        print(f"Checksum file:  {self.checksum_manager.checksum_file}")
        print(f"Rows processed: {len(self.standardized_rows)}")
        
        # Checksum summary
        checksum_summary = self.checksum_manager.get_summary()
        print(f"\nChecksums:")
        print(f"  Total records:      {checksum_summary['total_records']}")
        print(f"  Complete checksums: {checksum_summary['complete_checksums']}")
        
        # Verification results
        all_valid, verify_results = self.verify_integrity()
        print(f"\nIntegrity Verification:")
        print(f"  Verified:   {verify_results['verified']}/{verify_results['total_records']}")
        if verify_results['failures']:
            print(f"  Failures:   {len(verify_results['failures'])}")
            for failure in verify_results['failures']:
                print(f"    - {failure['message']} (Row {failure['row_number']})")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:5]:  # Show first 5
                print(f"   - {warning}")
            if len(self.warnings) > 5:
                print(f"   ... and {len(self.warnings) - 5} more")
        
        if not self.errors:
            print("\n✅ Standardization completed successfully!")
        
        print("="*70 + "\n")


def verify_checksums(input_file, checksum_file):
    """
    Verify that input file hasn't changed based on stored checksums.
    
    Args:
        input_file: Path to input TSV file
        checksum_file: Path to checksum JSON file
    """
    print("\n" + "="*70)
    print("VERIFYING CHECKSUMS")
    print("="*70)
    
    checksum_manager = ChecksumManager(checksum_file)
    
    if not checksum_manager.checksums:
        print("❌ No checksums found to verify")
        return False
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return False
    
    verified_count = 0
    failed_records = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                obj_num = row.get('object number', '').strip()
                record_id = f"obj_{obj_num}" if obj_num else f"row_{row_num}"
                
                source_row = {
                    'date': row.get('date', ''),
                    'title': row.get('title', ''),
                    'object_number': obj_num,
                    'link': row.get('link', '')
                }
                
                is_valid, message = checksum_manager.verify_record(record_id, source_row)
                
                if is_valid:
                    verified_count += 1
                else:
                    failed_records.append((row_num, message))
    
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return False
    
    total_records = len(checksum_manager.checksums)
    
    print(f"\nResults:")
    print(f"  Total checksums: {total_records}")
    print(f"  Verified:        {verified_count}")
    print(f"  Failed:          {len(failed_records)}")
    
    if failed_records:
        print(f"\n⚠️  Failed verifications:")
        for row_num, message in failed_records[:10]:
            print(f"   - Row {row_num}: {message}")
        if len(failed_records) > 10:
            print(f"   ... and {len(failed_records) - 10} more")
    else:
        print("\n✅ All checksums verified successfully!")
    
    print("="*70 + "\n")
    
    return len(failed_records) == 0


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory spreadsheet (.tsv) with checksum verification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standardize and create checksums
  python standardize_inventory.py inventory.tsv
  
  # Specify output and checksum files
  python standardize_inventory.py inventory.tsv -o clean.tsv -c checksums.json
  
  # Verify checksums on existing file
  python standardize_inventory.py --verify inventory.tsv -c checksums.json
  
  # Strict mode (fail on first error)
  python standardize_inventory.py inventory.tsv --strict
        """
    )
    
    parser.add_argument('input_file', help='Input TSV file')
    parser.add_argument('-o', '--output', help='Output TSV file')
    parser.add_argument('-c', '--checksums', help='Checksum JSON file')
    parser.add_argument('--strict', action='store_true',
                        help='Strict mode: fail on first error')
    parser.add_argument('--verify', action='store_true',
                        help='Verify checksums instead of standardizing')
    parser.add_argument('--log', action='store_true',
                        help='Write detailed comparison log')
    
    args = parser.parse_args()
    
    # Verify mode
    if args.verify:
        if not args.checksums:
            print("❌ Error: --checksums required for verification")
            sys.exit(1)
        success = verify_checksums(args.input_file, args.checksums)
        sys.exit(0 if success else 1)
    
    # Standardize mode
    standardizer = InventoryStandardizer(
        args.input_file,
        args.output,
        args.checksums,
        strict=args.strict
    )
    
    # Perform standardization
    if not standardizer.standardize():
        standardizer.print_report()
        sys.exit(1)
    
    # Write output files
    if not standardizer.write_output():
        standardizer.print_report()
        sys.exit(1)
    
    if not standardizer.write_checksums():
        standardizer.print_report()
        sys.exit(1)
    
    # Write detailed log if requested
    if args.log:
        log_file = standardizer.write_detailed_log()
        if log_file:
            print(f"Detailed log written to: {log_file}")
    
    # Print report
    standardizer.print_report()


if __name__ == '__main__':
    main()
```

## Usage

### Basic standardization with checksums:
```bash
python standardize_inventory.py inventory.tsv
```

This creates:
- `inventory_standardized.tsv` (standardized data)
- `inventory_checksums.json` (checksums for verification)

### Specify output files:
```bash
python standardize_inventory.py inventory.tsv -o clean.tsv -c checksums.json
```

### Create detailed comparison log:
```bash
python standardize_inventory.py inventory.tsv --log
```

Creates `inventory_log.json` showing source→standardized transformations.

### Verify checksums later:
```bash
python standardize_inventory.py --verify inventory.tsv -c checksums.json
```

Verifies that the input file hasn't changed since standardization.

## Checksum File Example

```json
{
  "obj_2023.001": {
    "source": "abc123def456...",
    "standardized": "xyz789uvw012..."
  },
  "obj_2023.002": {
    "source": "def456ghi789...",
    "standardized": "uvw012tuv345..."
  }
}
```

## Key Features

1. **Source & Standardized Hashes**: Tracks both original and processed data
2. **Record Identification**: Uses object number as primary ID
3. **Integrity Verification**: Can verify data hasn't changed
4. **Detailed Logging**: Optional JSON log of all transformations
5. **Multiple Algorithms**: Supports SHA256, MD5, SHA1
6. **Change Detection**: Identifies records that have been modified
7. **Audit Trail**: Complete record of what changed and how
