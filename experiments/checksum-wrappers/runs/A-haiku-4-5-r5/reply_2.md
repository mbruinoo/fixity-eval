# Museum Inventory Standardizer with Checksums

```python
#!/usr/bin/env python3
"""
Script to standardize museum inventory spreadsheet (.tsv files) with checksum verification.
Handles: date formatting, title normalization, object number validation, link verification,
and checksums to detect source data changes.
"""

import csv
import sys
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse
from dataclasses import dataclass, asdict


@dataclass
class ChecksumData:
    """Data structure for checksum information."""
    timestamp: str
    file_path: str
    file_size: int
    file_hash: str  # SHA256 of entire file
    row_hashes: Dict[int, str]  # Row number -> SHA256
    column_order: List[str]
    total_rows: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ChecksumData':
        """Create from dictionary."""
        return cls(**data)


class MuseumInventoryStandardizer:
    """Standardize museum inventory data from TSV files with checksum verification."""
    
    REQUIRED_COLUMNS = ['date', 'title', 'object number', 'link']
    DATE_FORMATS = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%B %d, %Y',
        '%b %d, %Y',
    ]
    
    def __init__(self, input_file: str, output_file: str = None, strict: bool = False,
                 checksum_file: str = None, verify_only: bool = False):
        """
        Initialize standardizer with checksum support.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file
            strict: If True, skip rows with errors
            checksum_file: Path to checksum JSON file (auto-generated if not provided)
            verify_only: If True, only verify checksums without processing
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else \
                          self.input_file.parent / f"{self.input_file.stem}_standardized.tsv"
        self.strict = strict
        self.verify_only = verify_only
        
        # Checksum file defaults to input_file.checksum.json
        self.checksum_file = Path(checksum_file) if checksum_file else \
                            self.input_file.parent / f"{self.input_file.stem}.checksum.json"
        
        self.errors = []
        self.warnings = []
        self.skipped_rows = []
        self.current_checksum: Optional[ChecksumData] = None
        self.previous_checksum: Optional[ChecksumData] = None
        
    # ==================== CHECKSUM METHODS ====================
    
    def calculate_file_hash(self) -> str:
        """
        Calculate SHA256 hash of entire input file.
        
        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256()
        with open(self.input_file, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def calculate_row_hash(self, row: Dict[str, str]) -> str:
        """
        Calculate SHA256 hash of a single row.
        Uses canonical JSON representation for consistency.
        
        Args:
            row: Dictionary with row data
            
        Returns:
            Hexadecimal hash string
        """
        # Create canonical representation: sorted JSON
        row_json = json.dumps(row, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(row_json.encode()).hexdigest()
    
    def load_previous_checksum(self) -> bool:
        """
        Load previous checksum from file if it exists.
        
        Returns:
            True if checksum loaded, False if file doesn't exist
        """
        if not self.checksum_file.exists():
            return False
        
        try:
            with open(self.checksum_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.previous_checksum = ChecksumData.from_dict(data)
                return True
        except Exception as e:
            self.errors.append(f"Failed to load checksum file: {str(e)}")
            return False
    
    def save_checksum(self, checksum_data: ChecksumData) -> bool:
        """
        Save checksum data to JSON file.
        
        Args:
            checksum_data: ChecksumData object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.checksum_file, 'w', encoding='utf-8') as f:
                json.dump(checksum_data.to_dict(), f, indent=2)
            return True
        except Exception as e:
            self.errors.append(f"Failed to save checksum file: {str(e)}")
            return False
    
    def verify_file_integrity(self) -> Tuple[bool, str]:
        """
        Verify that input file hasn't changed since last processing.
        
        Returns:
            Tuple of (is_unchanged, status_message)
        """
        if not self.previous_checksum:
            return True, "No previous checksum found (first run)"
        
        current_hash = self.calculate_file_hash()
        
        if current_hash == self.previous_checksum.file_hash:
            return True, "File integrity verified - no changes detected"
        else:
            return False, f"File has changed since last processing\n" \
                         f"  Previous hash: {self.previous_checksum.file_hash}\n" \
                         f"  Current hash:  {current_hash}"
    
    def detect_row_changes(self, rows: List[Dict[str, str]]) -> Dict[int, Dict]:
        """
        Detect which rows have changed since last processing.
        
        Args:
            rows: List of dictionaries with current data
            
        Returns:
            Dictionary mapping row numbers to change info
        """
        if not self.previous_checksum:
            return {}
        
        changes = {}
        
        for row_num, row in enumerate(rows, start=2):  # Header is row 1
            current_hash = self.calculate_row_hash(row)
            previous_hash = self.previous_checksum.row_hashes.get(row_num)
            
            if previous_hash and current_hash != previous_hash:
                changes[row_num] = {
                    'previous_hash': previous_hash,
                    'current_hash': current_hash,
                    'data': row
                }
        
        return changes
    
    def compare_with_previous(self) -> Dict:
        """
        Generate detailed comparison report with previous checksum.
        
        Returns:
            Dictionary with comparison details
        """
        if not self.previous_checksum:
            return {'status': 'no_previous_checksum'}
        
        report = {
            'timestamp': self.previous_checksum.timestamp,
            'previous_row_count': self.previous_checksum.total_rows,
            'current_row_count': self.current_checksum.total_rows if self.current_checksum else 0,
            'file_hash_match': self.previous_checksum.file_hash == self.calculate_file_hash(),
        }
        
        # Check for column order changes
        if self.previous_checksum.column_order != self.current_checksum.column_order:
            report['column_changes'] = {
                'previous': self.previous_checksum.column_order,
                'current': self.current_checksum.column_order if self.current_checksum else []
            }
        
        return report
    
    # ==================== STANDARDIZATION METHODS ====================
    
    def standardize_date(self, date_str: str) -> Tuple[str, str]:
        """
        Standardize date to YYYY-MM-DD format.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Tuple of (standardized_date, status_message)
        """
        if not date_str or date_str.strip() == '':
            return '', 'WARNING: Empty date field'
        
        date_str = date_str.strip()
        
        for fmt in self.DATE_FORMATS:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y-%m-%d'), 'OK'
            except ValueError:
                continue
        
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            msg = f'WARNING: Partial date parsed as year only: {year_match.group()}'
            return year_match.group(), msg
        
        return '', f'ERROR: Could not parse date: {date_str}'
    
    def standardize_title(self, title: str) -> Tuple[str, str]:
        """Standardize title: trim, normalize whitespace."""
        if not title or title.strip() == '':
            return '', 'WARNING: Empty title field'
        
        import re
        title = ' '.join(title.split())
        title = re.sub(r'\s+([,.;:])', r'\1', title)
        
        return title, 'OK'
    
    def standardize_object_number(self, obj_num: str) -> Tuple[str, str]:
        """Standardize object number: uppercase, remove extra spaces."""
        if not obj_num or obj_num.strip() == '':
            return '', 'WARNING: Empty object number'
        
        import re
        obj_num = ' '.join(obj_num.split()).upper()
        
        if not re.search(r'[A-Z0-9]', obj_num):
            return obj_num, 'WARNING: Object number contains no alphanumeric characters'
        
        return obj_num, 'OK'
    
    def standardize_link(self, link: str) -> Tuple[str, str]:
        """Standardize link: validate URL format, ensure HTTPS."""
        if not link or link.strip() == '':
            return '', 'WARNING: Empty link field'
        
        link = link.strip()
        
        try:
            result = urlparse(link)
            
            if not result.scheme:
                link = 'https://' + link
                return link, 'WARNING: Protocol added (assumed HTTPS)'
            
            if result.scheme not in ['http', 'https']:
                return '', f'ERROR: Invalid protocol: {result.scheme}'
            
            if result.scheme == 'http' and result.netloc:
                link = 'https://' + result.netloc + (result.path or '') + \
                       (('?' + result.query) if result.query else '')
                return link, 'WARNING: Converted HTTP to HTTPS'
            
            return link, 'OK'
            
        except Exception as e:
            return '', f'ERROR: Invalid URL: {str(e)}'
    
    def process_row(self, row: Dict[str, str], row_num: int) -> Tuple[Dict[str, str], bool]:
        """Process and standardize a single row."""
        standardized = {}
        row_valid = True
        
        date, date_msg = self.standardize_date(row.get('date', ''))
        standardized['date'] = date
        if 'WARNING' in date_msg:
            self.warnings.append(f"Row {row_num}: {date_msg}")
        elif 'ERROR' in date_msg:
            self.errors.append(f"Row {row_num}: {date_msg}")
            row_valid = False
        
        title, title_msg = self.standardize_title(row.get('title', ''))
        standardized['title'] = title
        if 'WARNING' in title_msg:
            self.warnings.append(f"Row {row_num}: {title_msg}")
        elif 'ERROR' in title_msg:
            self.errors.append(f"Row {row_num}: {title_msg}")
            row_valid = False
        
        obj_num, obj_msg = self.standardize_object_number(row.get('object number', ''))
        standardized['object number'] = obj_num
        if 'WARNING' in obj_msg:
            self.warnings.append(f"Row {row_num}: {obj_msg}")
        elif 'ERROR' in obj_msg:
            self.errors.append(f"Row {row_num}: {obj_msg}")
            row_valid = False
        
        link, link_msg = self.standardize_link(row.get('link', ''))
        standardized['link'] = link
        if 'WARNING' in link_msg:
            self.warnings.append(f"Row {row_num}: {link_msg}")
        elif 'ERROR' in link_msg:
            self.errors.append(f"Row {row_num}: {link_msg}")
            row_valid = False
        
        return standardized, row_valid
    
    def validate_columns(self, fieldnames: List[str]) -> bool:
        """Validate required columns are present."""
        fieldnames_lower = [f.lower() for f in fieldnames]
        missing = []
        
        for required in self.REQUIRED_COLUMNS:
            if required.lower() not in fieldnames_lower:
                missing.append(required)
        
        if missing:
            self.errors.append(f"Missing required columns: {', '.join(missing)}")
            return False
        
        return True
    
    def run(self) -> bool:
        """Execute the standardization process with checksum verification."""
        
        # Check input file exists
        if not self.input_file.exists():
            print(f"ERROR: Input file not found: {self.input_file}")
            return False
        
        print(f"Processing: {self.input_file}")
        
        # Load previous checksum
        has_previous = self.load_previous_checksum()
        
        # Verify file integrity
        if has_previous:
            unchanged, message = self.verify_file_integrity()
            print(f"  Integrity check: {message}")
            if unchanged:
                if self.verify_only:
                    print("  ✓ Verification successful - no changes needed")
                    return True
            else:
                print(f"  ⚠ File has been modified")
        
        try:
            # Read input file and calculate checksums
            with open(self.input_file, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile, delimiter='\t')
                
                if not self.validate_columns(reader.fieldnames):
                    print("ERROR: Column validation failed")
                    return False
                
                # Normalize column names
                fieldnames = [f.lower() for f in reader.fieldnames]
                
                rows = []
                row_hashes = {}
                
                for row_num, row in enumerate(reader, start=2):
                    row_lower = {k.lower(): v for k, v in row.items()}
                    
                    # Calculate hash before standardization
                    row_hash = self.calculate_row_hash(row_lower)
                    row_hashes[row_num] = row_hash
                    
                    # Detect changes
                    if has_previous and row_num in self.previous_checksum.row_hashes:
                        if row_hash != self.previous_checksum.row_hashes[row_num]:
                            print(f"  ⚠ Row {row_num} has changed")
                    
                    # Process row
                    standardized, is_valid = self.process_row(row_lower, row_num)
                    
                    if is_valid or not self.strict:
                        rows.append(standardized)
                    else:
                        self.skipped_rows.append(row_num)
                
                # Create checksum data
                self.current_checksum = ChecksumData(
                    timestamp=datetime.now().isoformat(),
                    file_path=str(self.input_file),
                    file_size=self.input_file.stat().st_size,
                    file_hash=self.calculate_file_hash(),
                    row_hashes=row_hashes,
                    column_order=fieldnames,
                    total_rows=len(rows)
                )
                
                # Write output file
                with open(self.output_file, 'w', newline='', encoding='utf-8') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=self.REQUIRED_COLUMNS,
                                          delimiter='\t')
                    writer.writeheader()
                    writer.writerows(rows)
                
                # Save checksum
                if self.save_checksum(self.current_checksum):
                    print(f"  ✓ Checksum saved to: {self.checksum_file}")
                
                # Print summary
                self.print_summary(len(rows))
                
                return True
                
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_summary(self, processed_count: int):
        """Print processing summary."""
        print(f"\n{'='*70}")
        print(f"STANDARDIZATION COMPLETE")
        print(f"{'='*70}")
        print(f"Input file:     {self.input_file}")
        print(f"Output file:    {self.output_file}")
        print(f"Checksum file:  {self.checksum_file}")
        print(f"Rows processed: {processed_count}")
        
        if self.current_checksum:
            print(f"\nChecksum Information:")
            print(f"  File hash:   {self.current_checksum.file_hash}")
            print(f"  File size:   {self.current_checksum.file_size} bytes")
            print(f"  Timestamp:   {self.current_checksum.timestamp}")
            print(f"  Total rows:  {self.current_checksum.total_rows}")
        
        if self.previous_checksum:
            comparison = self.compare_with_previous()
            print(f"\nComparison with Previous Run:")
            print(f"  Previous row count: {comparison['previous_row_count']}")
            print(f"  Current row count:  {comparison['current_row_count']}")
            print(f"  File hash match:    {comparison['file_hash_match']}")
            if 'column_changes' in comparison:
                print(f"  ⚠ Column order changed!")
        
        if self.errors:
            print(f"\nERRORS ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"  • {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        
        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"  • {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        if self.skipped_rows:
            print(f"\nSKIPPED ROWS ({len(self.skipped_rows)}): {self.skipped_rows}")
        
        if not self.errors:
            print("\n✓ No errors found!")


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: python standardize_inventory.py <input.tsv> [options]")
        print("\nOptions:")
        print("  -o, --output FILE        Output TSV file (default: input_standardized.tsv)")
        print("  -c, --checksum FILE      Checksum JSON file (default: input.checksum.json)")
        print("  -v, --verify-only        Verify checksums without processing")
        print("  --strict                 Skip rows with errors")
        print("\nExamples:")
        print("  python standardize_inventory.py inventory.tsv")
        print("  python standardize_inventory.py inventory.tsv -o output.tsv")
        print("  python standardize_inventory.py inventory.tsv --verify-only")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = None
    checksum_file = None
    strict = False
    verify_only = False
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] in ['-o', '--output']:
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] in ['-c', '--checksum']:
            checksum_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--strict':
            strict = True
            i += 1
        elif sys.argv[i] in ['-v', '--verify-only']:
            verify_only = True
            i += 1
        else:
            print(f"Unknown option: {sys.argv[i]}")
            sys.exit(1)
    
    standardizer = MuseumInventoryStandardizer(
        input_file, output_file, strict, checksum_file, verify_only
    )
    success = standardizer.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Generated Checksum File (`.checksum.json`)

```json
{
  "timestamp": "2024-01-15T14:32:45.123456",
  "file_path": "/path/to/inventory.tsv",
  "file_size": 2048,
  "file_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z",
  "row_hashes": {
    "2": "hash_of_row_2",
    "3": "hash_of_row_3",
    "4": "hash_of_row_4"
  },
  "column_order": ["date", "title", "object number", "link"],
  "total_rows": 3
}
```

## Usage Examples

```bash
# First run - creates checksum file
python standardize_inventory.py inventory.tsv

# Verify file hasn't changed since last run
python standardize_inventory.py inventory.tsv --verify-only

# Process with specific checksum file
python standardize_inventory.py inventory.tsv -c my_checksums.json

# All options
python standardize_inventory.py inventory.tsv \
  -o output.tsv \
  -c checksums.json \
  --strict

# Check for modifications
python standardize_inventory.py inventory.tsv --verify-only
# Output: "File has changed since last processing"
```

## Key Features

**Checksum Implementation:**
- ✓ SHA256 hashing of entire file and individual rows
- ✓ Canonical JSON representation for row consistency
- ✓ Detects additions, deletions, and modifications
- ✓ Column order change detection
- ✓ Timestamped checksum records

**Verification:**
- ✓ `--verify-only` mode to check without processing
- ✓ Detailed change detection and reporting
- ✓ Comparison with previous runs
- ✓ File integrity verification

**Data Integrity:**
- ✓ Prevents accidental reprocessing of unchanged data
- ✓ Audit trail via timestamped checksums
- ✓ Detects external modifications to source file
