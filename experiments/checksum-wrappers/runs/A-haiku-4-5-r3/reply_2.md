# Museum Inventory Standardizer with Checksum Verification

Here's the enhanced script with checksum functionality:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksum Verification
Standardizes museum inventory TSV files with data integrity verification
"""

import csv
import sys
import re
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import argparse


class ChecksumManager:
    """Manages checksums for data integrity verification"""
    
    HASH_ALGORITHM = 'sha256'
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.checksums: Dict[str, str] = {}
    
    def log(self, message: str):
        """Log if verbose mode enabled"""
        if self.verbose:
            print(f"[CHECKSUM] {message}")
    
    @staticmethod
    def compute_file_hash(filepath: Path, algorithm: str = 'sha256') -> str:
        """
        Compute hash of entire file
        Useful for detecting any changes to source file
        """
        hash_obj = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    
    @staticmethod
    def compute_row_hash(row: Dict, fields: List[str], algorithm: str = 'sha256') -> str:
        """
        Compute hash of a single row
        Only includes specified fields for comparison
        """
        hash_obj = hashlib.new(algorithm)
        for field in sorted(fields):
            value = str(row.get(field, '')).encode('utf-8')
            hash_obj.update(value)
        return hash_obj.hexdigest()
    
    @staticmethod
    def compute_data_hash(data: List[Dict], fields: List[str], 
                         algorithm: str = 'sha256') -> str:
        """
        Compute cumulative hash of all data
        Useful for detecting if dataset has changed
        """
        hash_obj = hashlib.new(algorithm)
        for row in data:
            for field in sorted(fields):
                value = str(row.get(field, '')).encode('utf-8')
                hash_obj.update(value)
        return hash_obj.hexdigest()
    
    def save_checksums(self, filepath: Path, data: Dict):
        """Save checksums to JSON file for later verification"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            self.log(f"Checksums saved to {filepath}")
        except Exception as e:
            raise Exception(f"Error saving checksums: {str(e)}")
    
    def load_checksums(self, filepath: Path) -> Dict:
        """Load previously saved checksums"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.log(f"Checksum file not found: {filepath}")
            return {}
        except Exception as e:
            raise Exception(f"Error loading checksums: {str(e)}")


class InventoryStandardizer:
    """Standardizes museum inventory data with checksum verification"""
    
    REQUIRED_COLUMNS = ['date', 'title', 'object number', 'link']
    CHECKSUM_FIELDS = ['date', 'title', 'object number', 'link']
    
    def __init__(self, input_file: str, output_file: str = None, 
                 checksum_file: str = None, verify_mode: bool = False,
                 verbose: bool = False):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self.input_file.with_stem(
            self.input_file.stem + '_standardized'
        )
        self.checksum_file = Path(checksum_file) if checksum_file else self.output_file.with_suffix('.checksums.json')
        self.verify_mode = verify_mode
        self.verbose = verbose
        self.checksum_mgr = ChecksumManager(verbose)
        
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
        self.data: List[Dict] = []
        self.integrity_issues: List[Dict] = []
        
        # Checksum tracking
        self.source_file_hash = None
        self.source_data_hash = None
        self.raw_row_hashes = {}
        self.standardized_row_hashes = {}
    
    def log(self, message: str, level: str = "INFO"):
        """Log messages if verbose mode is enabled"""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def compute_source_checksums(self, raw_data: List[Dict]):
        """Compute checksums for source data"""
        self.log("Computing source data checksums...")
        
        # Compute file-level hash
        self.source_file_hash = self.checksum_mgr.compute_file_hash(self.input_file)
        self.log(f"Source file SHA256: {self.source_file_hash[:16]}...")
        
        # Compute row-level hashes
        for idx, row in enumerate(raw_data):
            row_hash = self.checksum_mgr.compute_row_hash(
                row, self.CHECKSUM_FIELDS
            )
            self.raw_row_hashes[idx] = row_hash
        
        # Compute data-level hash
        self.source_data_hash = self.checksum_mgr.compute_data_hash(
            raw_data, self.CHECKSUM_FIELDS
        )
        self.log(f"Source data SHA256: {self.source_data_hash[:16]}...")
        self.log(f"Computed checksums for {len(self.raw_row_hashes)} rows")
    
    def compute_standardized_checksums(self, standardized_data: List[Dict]):
        """Compute checksums for standardized data"""
        self.log("Computing standardized data checksums...")
        
        # Compute row-level hashes
        for idx, row in enumerate(standardized_data):
            row_hash = self.checksum_mgr.compute_row_hash(
                row, self.CHECKSUM_FIELDS
            )
            self.standardized_row_hashes[idx] = row_hash
    
    def verify_source_integrity(self, saved_checksums: Dict) -> bool:
        """
        Verify that source data hasn't changed since last run
        Useful when re-standardizing the same source file
        """
        self.log("Verifying source data integrity...")
        
        if not saved_checksums:
            self.log("No previous checksums found - skipping verification")
            return True
        
        all_valid = True
        
        # Check file hash
        if 'source_file_hash' in saved_checksums:
            saved_hash = saved_checksums['source_file_hash']
            if self.source_file_hash != saved_hash:
                self.integrity_issues.append({
                    'severity': 'CRITICAL',
                    'check': 'file_hash',
                    'message': 'Source file has been modified',
                    'saved_hash': saved_hash[:16] + '...',
                    'current_hash': self.source_file_hash[:16] + '...'
                })
                all_valid = False
                self.log("⚠ Source file hash mismatch!", level="WARNING")
        
        # Check data hash
        if 'source_data_hash' in saved_checksums:
            saved_hash = saved_checksums['source_data_hash']
            if self.source_data_hash != saved_hash:
                self.integrity_issues.append({
                    'severity': 'HIGH',
                    'check': 'data_hash',
                    'message': 'Source data content has changed',
                    'saved_hash': saved_hash[:16] + '...',
                    'current_hash': self.source_data_hash[:16] + '...'
                })
                all_valid = False
                self.log("⚠ Source data hash mismatch!", level="WARNING")
        
        # Check individual row hashes
        if 'raw_row_hashes' in saved_checksums:
            saved_row_hashes = saved_checksums['raw_row_hashes']
            for row_idx, saved_hash in saved_row_hashes.items():
                current_hash = self.raw_row_hashes.get(int(row_idx))
                if current_hash != saved_hash:
                    self.integrity_issues.append({
                        'severity': 'MEDIUM',
                        'check': 'row_hash',
                        'row': int(row_idx),
                        'message': f'Row {row_idx} has been modified',
                        'saved_hash': saved_hash[:16] + '...',
                        'current_hash': current_hash[:16] + '...' if current_hash else 'N/A'
                    })
                    all_valid = False
        
        if all_valid:
            self.log("✓ Source data integrity verified")
        else:
            self.log(f"⚠ Found {len(self.integrity_issues)} integrity issues", level="WARNING")
        
        return all_valid
    
    def standardize_date(self, date_str: str) -> Tuple[str, bool]:
        """Standardize date to ISO format (YYYY-MM-DD)"""
        if not date_str or not date_str.strip():
            return "", False
        
        date_str = date_str.strip()
        
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%m-%d-%Y",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%Y",
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d"), True
            except ValueError:
                continue
        
        return date_str, False
    
    def standardize_title(self, title: str) -> str:
        """Standardize title formatting"""
        if not title:
            return ""
        
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)
        return title
    
    def standardize_object_number(self, obj_num: str) -> Tuple[str, bool]:
        """Standardize object number"""
        if not obj_num or not obj_num.strip():
            return "", False
        
        obj_num = obj_num.strip()
        obj_num = re.sub(r'\s+', ' ', obj_num)
        
        if not obj_num:
            return "", False
        
        return obj_num, True
    
    def standardize_link(self, link: str) -> Tuple[str, bool]:
        """Standardize URL"""
        if not link or not link.strip():
            return "", False
        
        link = link.strip()
        
        url_pattern = r'^https?://.+'
        is_valid = bool(re.match(url_pattern, link))
        
        if not link.startswith(('http://', 'https://')):
            self.warnings.append({
                'row': None,
                'column': 'link',
                'value': link,
                'issue': 'URL does not start with http:// or https://'
            })
        
        return link, is_valid
    
    def read_input(self) -> List[Dict]:
        """Read and parse the input TSV file"""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        self.log(f"Reading input file: {self.input_file}")
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if reader.fieldnames is None:
                    raise ValueError("TSV file is empty")
                
                fieldnames = [col.strip().lower() for col in reader.fieldnames]
                
                missing_cols = set(self.REQUIRED_COLUMNS) - set(fieldnames)
                if missing_cols:
                    raise ValueError(f"Missing required columns: {missing_cols}")
                
                raw_data = []
                for row_num, row in enumerate(reader, start=2):
                    normalized_row = {k.strip().lower(): v for k, v in row.items()}
                    normalized_row['_row_number'] = row_num
                    raw_data.append(normalized_row)
                
                self.log(f"Successfully read {len(raw_data)} rows")
                return raw_data
                
        except Exception as e:
            raise Exception(f"Error reading input file: {str(e)}")
    
    def standardize_records(self, raw_data: List[Dict]) -> List[Dict]:
        """Standardize all records"""
        self.log("Standardizing records...")
        standardized = []
        
        for row in raw_data:
            row_num = row.get('_row_number')
            standardized_row = {'_row_number': row_num}
            
            # Standardize date
            date_val, date_valid = self.standardize_date(row.get('date', ''))
            standardized_row['date'] = date_val
            if not date_valid and date_val:
                self.warnings.append({
                    'row': row_num,
                    'column': 'date',
                    'value': row.get('date'),
                    'issue': 'Date format not recognized, kept as-is'
                })
            if not date_val:
                self.errors.append({
                    'row': row_num,
                    'column': 'date',
                    'value': row.get('date'),
                    'issue': 'Date is missing or empty'
                })
            
            # Standardize title
            title_val = self.standardize_title(row.get('title', ''))
            standardized_row['title'] = title_val
            if not title_val:
                self.errors.append({
                    'row': row_num,
                    'column': 'title',
                    'value': row.get('title'),
                    'issue': 'Title is missing or empty'
                })
            
            # Standardize object number
            obj_num_val, obj_num_valid = self.standardize_object_number(row.get('object number', ''))
            standardized_row['object number'] = obj_num_val
            if not obj_num_valid:
                self.errors.append({
                    'row': row_num,
                    'column': 'object number',
                    'value': row.get('object number'),
                    'issue': 'Object number is missing or invalid'
                })
            
            # Standardize link
            link_val, link_valid = self.standardize_link(row.get('link', ''))
            standardized_row['link'] = link_val
            if not link_valid and link_val:
                self.warnings.append({
                    'row': row_num,
                    'column': 'link',
                    'value': row.get('link'),
                    'issue': 'Link format may be invalid'
                })
            if not link_val:
                self.warnings.append({
                    'row': row_num,
                    'column': 'link',
                    'value': row.get('link'),
                    'issue': 'Link is missing or empty'
                })
            
            standardized.append(standardized_row)
        
        self.log(f"Standardized {len(standardized)} records")
        return standardized
    
    def write_output(self, standardized_data: List[Dict]):
        """Write standardized data to output file"""
        self.log(f"Writing output to: {self.output_file}")
        
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['date', 'title', 'object number', 'link']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                
                writer.writeheader()
                for row in standardized_data:
                    output_row = {field: row.get(field, '') for field in fieldnames}
                    writer.writerow(output_row)
            
            self.log(f"Successfully wrote output file")
        except Exception as e:
            raise Exception(f"Error writing output file: {str(e)}")
    
    def save_checksums_to_file(self):
        """Save all checksums to JSON file"""
        checksums_data = {
            'timestamp': datetime.now().isoformat(),
            'input_file': str(self.input_file),
            'source_file_hash': self.source_file_hash,
            'source_data_hash': self.source_data_hash,
            'raw_row_hashes': self.raw_row_hashes,
            'standardized_row_hashes': self.standardized_row_hashes,
            'total_rows': len(self.data),
        }
        
        self.checksum_mgr.save_checksums(self.checksum_file, checksums_data)
    
    def generate_report(self) -> str:
        """Generate a comprehensive validation report"""
        report = []
        report.append("=" * 70)
        report.append("MUSEUM INVENTORY STANDARDIZATION REPORT")
        report.append("=" * 70)
        report.append(f"Input file: {self.input_file}")
        report.append(f"Output file: {self.output_file}")
        report.append(f"Checksum file: {self.checksum_file}")
        report.append(f"Total records processed: {len(self.data)}")
        report.append("")
        
        # Checksums section
        report.append("-" * 70)
        report.append("DATA INTEGRITY - CHECKSUMS")
        report.append("-" * 70)
        report.append(f"Source File (SHA256):    {self.source_file_hash}")
        report.append(f"Source Data (SHA256):    {self.source_data_hash}")
        report.append(f"Rows with checksums:     {len(self.raw_row_hashes)}")
        report.append("")
        
        # Integrity issues section
        if self.integrity_issues:
            report.append("-" * 70)
            report.append(f"INTEGRITY ISSUES ({len(self.integrity_issues)}):")
            report.append("-" * 70)
            for issue in self.integrity_issues:
                severity = issue['severity']
                check = issue['check']
                message = issue['message']
                report.append(f"  [{severity}] {check.upper()}")
                report.append(f"    Message: {message}")
                if 'row' in issue:
                    report.append(f"    Row: {issue['row']}")
                report.append(f"    Previous: {issue.get('saved_hash', 'N/A')}")
                report.append(f"    Current:  {issue.get('current_hash', 'N/A')}")
                report.append("")
        else:
            report.append("✓ No integrity issues found")
            report.append("")
        
        # Errors section
        if self.errors:
            report.append("-" * 70)
            report.append(f"VALIDATION ERRORS ({len(self.errors)}):")
            report.append("-" * 70)
            for error in self.errors:
                report.append(f"  Row {error['row']}, Column '{error['column']}':")
                report.append(f"    Value: {error['value']}")
                report.append(f"    Issue: {error['issue']}")
                report.append("")
        else:
            report.append("✓ No validation errors found")
            report.append("")
        
        # Warnings section
        if self.warnings:
            report.append("-" * 70)
            report.append(f"WARNINGS ({len(self.warnings)}):")
            report.append("-" * 70)
            for warning in self.warnings:
                report.append(f"  Row {warning['row']}, Column '{warning['column']}':")
                report.append(f"    Value: {warning['value']}")
                report.append(f"    Issue: {warning['issue']}")
                report.append("")
        else:
            report.append("✓ No warnings found")
            report.append("")
        
        report.append("=" * 70)
        return "\n".join(report)
    
    def run(self):
        """Run the standardization process"""
        try:
            # Read input
            raw_data = self.read_input()
            
            # Compute source checksums
            self.compute_source_checksums(raw_data)
            
            # Verify against saved checksums if in verify mode
            if self.verify_mode:
                saved_checksums = self.checksum_mgr.load_checksums(self.checksum_file)
                if saved_checksums and not self.verify_source_integrity(saved_checksums):
                    self.log("⚠ Source data integrity check failed", level="WARNING")
            
            # Standardize records
            standardized_data = self.standardize_records(raw_data)
            self.data = standardized_data
            
            # Compute standardized checksums
            self.compute_standardized_checksums(standardized_data)
            
            # Write output
            self.write_output(standardized_data)
            
            # Save checksums
            self.save_checksums_to_file()
            
            # Generate and print report
            report = self.generate_report()
            print(report)
            
            # Save report to file
            report_file = self.output_file.with_suffix('.report.txt')
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            self.log(f"Report saved to: {report_file}")
            
            return True
            
        except Exception as e:
            print(f"ERROR: {str(e)}", file=sys.stderr)
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory TSV files with checksum verification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First run - creates checksums
  python standardize_inventory.py input.tsv
  
  # Verify source hasn't changed before re-standardizing
  python standardize_inventory.py input.tsv --verify
  
  # Custom output and checksum files
  python standardize_inventory.py input.tsv -o output.tsv -c checksums.json -v
        """
    )
    
    parser.add_argument('input_file', help='Input TSV file')
    parser.add_argument('-o', '--output', help='Output TSV file')
    parser.add_argument('-c', '--checksums', help='Checksum file (JSON)')
    parser.add_argument('--verify', action='store_true',
                       help='Verify source data against saved checksums')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    standardizer = InventoryStandardizer(
        args.input_file,
        args.output,
        args.checksums,
        args.verify,
        args.verbose
    )
    
    success = standardizer.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Usage Examples

### First run (creates checksums):
```bash
python standardize_inventory.py input.tsv -v
```

### Verify source hasn't changed:
```bash
python standardize_inventory.py input.tsv --verify -v
```

### Custom files with checksums:
```bash
python standardize_inventory.py input.tsv -o cleaned.tsv -c checksums.json --verify
```

## Output Files Generated

1. **`*_standardized.tsv`** - Cleaned inventory data
2. **`*.checksums.json`** - Integrity checksums (see below)
3. **`*.report.txt`** - Validation report

## Checksum File Example

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "input_file": "/path/to/input.tsv",
  "source_file_hash": "a1b2c3d4e5f6...",
  "source_data_hash": "f6e5d4c3b2a1...",
  "raw_row_hashes": {
    "0": "hash_of_row_1",
    "1": "hash_of_row_2",
    "2": "hash_of_row_3"
  },
  "standardized_row_hashes": {
    "0": "hash_of_standardized_row_1",
    "1": "hash_of_standardized_row_2"
  },
  "total_rows": 100
}
```

## Key Checksum Features

✓ **File-level checksums**: Detect any modification to source file
✓ **Data-level checksums**: Track overall dataset changes
✓ **Row-level checksums**: Identify which specific rows changed
✓ **Verification mode**: Compare against previous checksums
✓ **Integrity reporting**: Alert on critical/high/medium severity changes
✓ **JSON persistence**: Save checksums for future comparison
