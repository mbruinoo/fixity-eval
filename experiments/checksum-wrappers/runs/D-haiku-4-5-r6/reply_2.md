# Museum Inventory Standardizer with Checksums

Here's the enhanced version with checksum verification:

```python
#!/usr/bin/env python3
"""
Standardize museum inventory spreadsheet with checksum verification.
Detects if source data has been modified since last standardization.
"""

import csv
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
import re
from urllib.parse import urlparse


class ChecksumManager:
    """Manages checksums for data integrity verification."""
    
    # Checksum strategies
    STRATEGY_FILE = 'file'      # Hash entire file
    STRATEGY_ROWS = 'rows'      # Hash individual rows
    STRATEGY_FIELDS = 'fields'  # Hash individual fields
    
    def __init__(self, strategy: str = 'rows'):
        """
        Initialize checksum manager.
        
        Args:
            strategy: 'file', 'rows', or 'fields'
        """
        self.strategy = strategy
        self.file_hash: Optional[str] = None
        self.row_hashes: Dict[int, str] = {}  # row_num -> hash
        self.field_hashes: Dict[Tuple[int, str], str] = {}  # (row_num, field) -> hash
        self.timestamp: Optional[str] = None
    
    @staticmethod
    def sha256(data: str) -> str:
        """Generate SHA-256 hash of string."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def md5(data: str) -> str:
        """Generate MD5 hash of string (faster, for non-critical use)."""
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    
    def hash_file(self, filepath: Path) -> str:
        """Hash entire file content."""
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def hash_row(self, row_dict: Dict[str, str], field_order: List[str]) -> str:
        """Hash a single row (ordered by field_order for consistency)."""
        ordered_data = '|'.join(
            str(row_dict.get(field, '')) for field in field_order
        )
        return self.sha256(ordered_data)
    
    def hash_field(self, value: str) -> str:
        """Hash a single field value."""
        return self.md5(value.strip())
    
    def compute_checksums_from_file(self, filepath: Path) -> bool:
        """Compute checksums for file."""
        try:
            self.timestamp = datetime.utcnow().isoformat()
            
            # File-level checksum
            self.file_hash = self.hash_file(filepath)
            
            # Row and field checksums
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                field_order = reader.fieldnames or []
                
                for row_num, row in enumerate(reader, start=2):
                    # Row checksum
                    if self.strategy in ('rows', 'fields'):
                        self.row_hashes[row_num] = self.hash_row(row, field_order)
                    
                    # Field checksums
                    if self.strategy == 'fields':
                        for field, value in row.items():
                            self.field_hashes[(row_num, field)] = self.hash_field(value)
            
            return True
        
        except Exception as e:
            print(f"Error computing checksums: {e}", file=sys.stderr)
            return False
    
    def save_manifest(self, manifest_path: Path) -> bool:
        """Save checksum manifest to JSON file."""
        try:
            manifest = {
                'timestamp': self.timestamp,
                'strategy': self.strategy,
                'file_hash': self.file_hash,
                'row_hashes': {str(k): v for k, v in self.row_hashes.items()},
                'field_hashes': {f"{k[0]}:{k[1]}": v for k, v in self.field_hashes.items()},
                'record_count': len(self.row_hashes) if self.row_hashes else 0,
            }
            
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving manifest: {e}", file=sys.stderr)
            return False
    
    def load_manifest(self, manifest_path: Path) -> bool:
        """Load checksum manifest from JSON file."""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            self.timestamp = manifest.get('timestamp')
            self.strategy = manifest.get('strategy', 'rows')
            self.file_hash = manifest.get('file_hash')
            self.row_hashes = {int(k): v for k, v in manifest.get('row_hashes', {}).items()}
            
            # Parse field hashes back to tuple keys
            field_hashes_raw = manifest.get('field_hashes', {})
            self.field_hashes = {}
            for key_str, hash_val in field_hashes_raw.items():
                row_num, field = key_str.split(':', 1)
                self.field_hashes[(int(row_num), field)] = hash_val
            
            return True
        
        except Exception as e:
            print(f"Error loading manifest: {e}", file=sys.stderr)
            return False
    
    def verify_file(self, filepath: Path) -> Tuple[bool, Dict]:
        """
        Verify file against stored checksums.
        
        Returns:
            (is_valid, details_dict)
        """
        details = {
            'file_changed': False,
            'rows_changed': [],
            'fields_changed': [],
            'rows_added': [],
            'rows_removed': [],
            'new_file_hash': None,
            'matches_stored': None,
        }
        
        try:
            # Check file hash
            new_file_hash = self.hash_file(filepath)
            details['new_file_hash'] = new_file_hash
            
            if self.file_hash and new_file_hash != self.file_hash:
                details['file_changed'] = True
            
            # Check row hashes
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                field_order = reader.fieldnames or []
                current_rows = set()
                
                for row_num, row in enumerate(reader, start=2):
                    current_rows.add(row_num)
                    
                    if self.strategy in ('rows', 'fields'):
                        new_row_hash = self.hash_row(row, field_order)
                        
                        if row_num in self.row_hashes:
                            if new_row_hash != self.row_hashes[row_num]:
                                details['rows_changed'].append({
                                    'row': row_num,
                                    'object_number': row.get('object_number', 'unknown')
                                })
                        else:
                            details['rows_added'].append(row_num)
                    
                    # Check field hashes
                    if self.strategy == 'fields':
                        for field, value in row.items():
                            new_field_hash = self.hash_field(value)
                            key = (row_num, field)
                            
                            if key in self.field_hashes:
                                if new_field_hash != self.field_hashes[key]:
                                    details['fields_changed'].append({
                                        'row': row_num,
                                        'field': field,
                                        'object_number': row.get('object_number', 'unknown')
                                    })
            
            # Check for removed rows
            details['rows_removed'] = [r for r in self.row_hashes.keys() if r not in current_rows]
            
            # Summary
            details['matches_stored'] = (
                not details['file_changed'] and
                not details['rows_changed'] and
                not details['rows_added'] and
                not details['rows_removed']
            )
            
            return details['matches_stored'], details
        
        except Exception as e:
            print(f"Error verifying file: {e}", file=sys.stderr)
            return False, details


class InventoryEntry:
    """Represents a single inventory entry with validation."""
    
    def __init__(self, date: str, title: str, object_number: str, link: str,
                 row_num: int = 0, status: str = "active", checksum: Optional[str] = None):
        self.date = date
        self.title = title
        self.object_number = object_number
        self.link = link
        self.row_num = row_num
        self.status = status
        self.checksum = checksum  # Original row checksum
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def standardize(self) -> None:
        """Apply standardization rules to entry."""
        self._standardize_date()
        self._standardize_title()
        self._standardize_object_number()
        self._standardize_link()
    
    def _standardize_date(self) -> None:
        """Standardize date to YYYY-MM-DD format."""
        if not self.date or self.date.lower() == 'unknown':
            self.warnings.append("Missing date")
            return
        
        date_formats = [
            '%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y',
            '%B %d, %Y', '%b %d, %Y', '%Y', '%m/%d/%y'
        ]
        
        for fmt in date_formats:
            try:
                parsed = datetime.strptime(self.date.strip(), fmt)
                self.date = parsed.strftime('%Y-%m-%d')
                return
            except ValueError:
                continue
        
        self.errors.append(f"Invalid date format: {self.date}")
    
    def _standardize_title(self) -> None:
        """Standardize title: strip whitespace, title case validation."""
        self.title = self.title.strip()
        
        if not self.title:
            self.errors.append("Empty title")
            return
        
        if len(self.title) > 500:
            self.warnings.append(f"Title very long ({len(self.title)} chars)")
        
        self.title = ' '.join(self.title.split())
        
        if self.title.isupper() and len(self.title.split()) > 1:
            self.warnings.append("Title is all uppercase")
        if self.title.islower():
            self.warnings.append("Title is all lowercase")
    
    def _standardize_object_number(self) -> None:
        """Standardize object number format."""
        self.object_number = self.object_number.strip().upper()
        
        if not self.object_number or self.object_number == 'UNKNOWN':
            self.errors.append("Missing or unknown object number")
            return
        
        self.object_number = re.sub(r'\s+', ' ', self.object_number)
        
        if not re.match(r'^[\w\-./]+$', self.object_number):
            self.warnings.append(f"Unusual characters in object number: {self.object_number}")
    
    def _standardize_link(self) -> None:
        """Standardize and validate URL."""
        self.link = self.link.strip()
        
        if not self.link or self.link.lower() in ('unknown', 'n/a', ''):
            self.warnings.append("Missing link")
            return
        
        if not self.link.startswith(('http://', 'https://')):
            self.link = 'https://' + self.link
            self.warnings.append("Added https:// protocol to link")
        
        try:
            result = urlparse(self.link)
            if not all([result.scheme, result.netloc]):
                self.errors.append(f"Invalid URL: {self.link}")
        except Exception as e:
            self.errors.append(f"URL parsing error: {e}")
    
    def is_valid(self) -> bool:
        """Return True if entry has no errors."""
        return len(self.errors) == 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'date': self.date,
            'title': self.title,
            'object_number': self.object_number,
            'link': self.link,
            'status': self.status
        }


class InventoryStandardizer:
    """Main standardization and validation engine with checksum support."""
    
    def __init__(self, input_file: str, output_file: str = None,
                 checksum_strategy: str = 'rows', verify_checksums: bool = True):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self._get_output_path()
        self.manifest_file = self.input_file.parent / f"{self.input_file.stem}_manifest.json"
        
        self.checksum_mgr = ChecksumManager(strategy=checksum_strategy)
        self.verify_checksums = verify_checksums
        self.checksum_verification: Optional[Dict] = None
        
        self.entries: List[InventoryEntry] = []
        self.corrections: Dict[str, str] = {}
        self.withdrawn: Set[str] = set()
        self.duplicates: Dict[str, List[int]] = {}
        
        self.report = {
            'total_entries': 0,
            'valid_entries': 0,
            'entries_with_errors': 0,
            'entries_with_warnings': 0,
            'duplicates_found': 0,
            'withdrawn_entries': 0,
            'checksum_status': 'not_checked',
            'data_integrity': 'unknown',
        }
    
    def _get_output_path(self) -> Path:
        """Generate output filename."""
        stem = self.input_file.stem
        return self.input_file.parent / f"{stem}_standardized.tsv"
    
    def verify_source_data(self) -> bool:
        """
        Verify that source data hasn't changed since last standardization.
        
        Returns:
            True if data matches stored checksums or no manifest exists yet
        """
        if not self.manifest_file.exists():
            print(f"ℹ No checksum manifest found (first run): {self.manifest_file}")
            self.report['checksum_status'] = 'first_run'
            return True
        
        print(f"Verifying source data integrity...")
        is_valid, details = self.checksum_mgr.verify_file(self.input_file)
        self.checksum_verification = details
        
        if is_valid:
            print("✓ Source data matches stored checksums - data integrity verified")
            self.report['checksum_status'] = 'verified'
            self.report['data_integrity'] = 'valid'
            return True
        else:
            self.report['checksum_status'] = 'modified'
            self.report['data_integrity'] = 'invalid'
            self._print_verification_details(details)
            return False
    
    def _print_verification_details(self, details: Dict) -> None:
        """Print detailed verification results."""
        print("\n" + "!"*60)
        print("⚠ SOURCE DATA HAS BEEN MODIFIED")
        print("!"*60)
        
        if details['file_changed']:
            print(f"File hash changed:")
            print(f"  Previous: {self.checksum_mgr.file_hash}")
            print(f"  Current:  {details['new_file_hash']}")
        
        if details['rows_changed']:
            print(f"\n{len(details['rows_changed'])} rows modified:")
            for change in details['rows_changed'][:10]:  # Show first 10
                print(f"  Row {change['row']}: {change['object_number']}")
            if len(details['rows_changed']) > 10:
                print(f"  ... and {len(details['rows_changed']) - 10} more")
        
        if details['rows_added']:
            print(f"\n{len(details['rows_added'])} rows added: {details['rows_added']}")
        
        if details['rows_removed']:
            print(f"\n{len(details['rows_removed'])} rows removed: {details['rows_removed']}")
        
        if details['fields_changed']:
            print(f"\n{len(details['fields_changed'])} field changes:")
            for change in details['fields_changed'][:5]:  # Show first 5
                print(f"  Row {change['row']}, Field '{change['field']}': {change['object_number']}")
            if len(details['fields_changed']) > 5:
                print(f"  ... and {len(details['fields_changed']) - 5} more")
        
        print("!"*60 + "\n")
    
    def load(self) -> bool:
        """Load and parse TSV file."""
        if not self.input_file.exists():
            print(f"Error: File not found: {self.input_file}", file=sys.stderr)
            return False
        
        # Verify checksums first if requested
        if self.verify_checksums:
            self.checksum_mgr.load_manifest(self.manifest_file)
            if not self.verify_source_data():
                print("Warning: Proceeding despite data changes (use --force to continue)\n")
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    print("Error: Empty file", file=sys.stderr)
                    return False
                
                required_cols = {'date', 'title', 'object_number', 'link'}
                if not required_cols.issubset(set(reader.fieldnames)):
                    print(f"Error: Missing required columns. Found: {reader.fieldnames}",
                          file=sys.stderr)
                    return False
                
                field_order = list(reader.fieldnames)
                
                for row_num, row in enumerate(reader, start=2):
                    # Compute checksum for this row if we're storing them
                    row_checksum = None
                    if self.checksum_mgr.strategy in ('rows', 'fields'):
                        row_checksum = self.checksum_mgr.hash_row(row, field_order)
                    
                    entry = InventoryEntry(
                        date=row.get('date', ''),
                        title=row.get('title', ''),
                        object_number=row.get('object_number', ''),
                        link=row.get('link', ''),
                        row_num=row_num,
                        checksum=row_checksum
                    )
                    self.entries.append(entry)
            
            self.report['total_entries'] = len(self.entries)
            return True
        
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return False
    
    def standardize(self) -> None:
        """Standardize all entries."""
        for entry in self.entries:
            entry.standardize()
    
    def detect_duplicates(self) -> None:
        """Identify duplicate object numbers."""
        by_number = {}
        
        for entry in self.entries:
            key = entry.object_number
            if key not in by_number:
                by_number[key] = []
            by_number[key].append(entry)
        
        for key, dupes in by_number.items():
            if len(dupes) > 1:
                self.duplicates[key] = [e.row_num for e in dupes]
                self.report['duplicates_found'] += 1
                
                dupes.sort(key=lambda x: x.date, reverse=True)
                for old_entry in dupes[1:]:
                    old_entry.status = 'corrected'
    
    def mark_withdrawn(self, object_numbers: List[str]) -> None:
        """Mark entries as withdrawn."""
        normalized = [num.upper().strip() for num in object_numbers]
        
        for entry in self.entries:
            if entry.object_number in normalized:
                entry.status = 'withdrawn'
                self.withdrawn.add(entry.object_number)
                self.report['withdrawn_entries'] += 1
    
    def validate(self) -> None:
        """Validate all entries and update report."""
        for entry in self.entries:
            if entry.is_valid():
                if entry.status == 'active':
                    self.report['valid_entries'] += 1
            else:
                self.report['entries_with_errors'] += 1
            
            if entry.warnings:
                self.report['entries_with_warnings'] += 1
    
    def save(self, include_status: bool = True, include_errors: bool = True,
             include_checksums: bool = False) -> bool:
        """Save standardized inventory to file."""
        try:
            fieldnames = ['date', 'title', 'object_number', 'link']
            if include_status:
                fieldnames.append('status')
            if include_errors:
                fieldnames.extend(['errors', 'warnings'])
            if include_checksums:
                fieldnames.append('source_checksum')
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                
                for entry in self.entries:
                    row = {
                        'date': entry.date,
                        'title': entry.title,
                        'object_number': entry.object_number,
                        'link': entry.link,
                    }
                    if include_status:
                        row['status'] = entry.status
                    if include_errors:
                        row['errors'] = '; '.join(entry.errors) if entry.errors else ''
                        row['warnings'] = '; '.join(entry.warnings) if entry.warnings else ''
                    if include_checksums:
                        row['source_checksum'] = entry.checksum or ''
                    
                    writer.writerow(row)
            
            print(f"✓ Standardized file saved: {self.output_file}")
            return True
        
        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            return False
    
    def save_manifest(self) -> bool:
        """Save checksum manifest for future verification."""
        # Recompute checksums from loaded file
        if not self.checksum_mgr.file_hash:
            self.checksum_mgr.compute_checksums_from_file(self.input_file)
        
        if self.checksum_mgr.save_manifest(self.manifest_file):
            print(f"✓ Checksum manifest saved: {self.manifest_file}")
            return True
        return False
    
    def save_error_report(self) -> bool:
        """Save detailed error report."""
        report_file = self.input_file.parent / f"{self.input_file.stem}_errors.tsv"
        
        try:
            error_entries = [e for e in self.entries if e.errors or e.warnings]
            
            if not error_entries:
                print("✓ No errors found - no report generated")
                return True
            
            with open(report_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['row', 'object_number', 'title', 'errors', 'warnings'],
                    delimiter='\t'
                )
                writer.writeheader()
                
                for entry in error_entries:
                    writer.writerow({
                        'row': entry.row_num,
                        'object_number': entry.object_number,
                        'title': entry.title[:50],
                        'errors': '; '.join(entry.errors),
                        'warnings': '; '.join(entry.warnings),
                    })
            
            print(f"✓ Error report saved: {report_file}")
            return True
        
        except Exception as e:
            print(f"Error writing report: {e}", file=sys.stderr)
            return False
    
    def save_verification_report(self) -> bool:
        """Save detailed verification report."""
        if not self.checksum_verification:
            return False
        
        report_file = self.input_file.parent / f"{self.input_file.stem}_verification.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.utcnow().isoformat(),
                    'verification': self.checksum_verification,
                    'status': self.report['checksum_status'],
                }, f, indent=2)
            
            print(f"✓ Verification report saved: {report_file}")
            return True
        
        except Exception as e:
            print(f"Error writing verification report: {e}", file=sys.stderr)
            return False
    
    def print_summary(self) -> None:
        """Print validation summary."""
        print("\n" + "="*60)
        print("INVENTORY STANDARDIZATION SUMMARY")
        print("="*60)
        print(f"Total entries:           {self.report['total_entries']}")
        print(f"Valid entries:           {self.report['valid_entries']}")
        print(f"Entries with errors:     {self.report['entries_with_errors']}")
        print(f"Entries with warnings:   {self.report['entries_with_warnings']}")
        print(f"Duplicate object numbers:{self.report['duplicates_found']}")
        print(f"Withdrawn entries:       {self.report['withdrawn_entries']}")
        print(f"\nChecksum Status:         {self.report['checksum_status']}")
        print(f"Data Integrity:          {self.report['data_integrity']}")
        print("="*60 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory with checksum verification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First run (creates manifest)
  python standardize_inventory.py inventory.tsv --save-manifest

  # Subsequent runs (verifies data)
  python standardize_inventory.py inventory.tsv

  # Force processing despite changes
  python standardize_inventory.py inventory.tsv --no-verify

  # Save detailed verification report
  python standardize_inventory.py inventory.tsv --verification-report
        """
    )
    
    parser.add_argument('input', help='Input TSV file')
    parser.add_argument('-o', '--output', help='Output TSV file')
    parser.add_argument('-w', '--withdrawn', help='File with withdrawn object numbers')
    
    parser.add_argument('--checksum-strategy', 
                       choices=['file', 'rows', 'fields'],
                       default='rows',
                       help='Checksum strategy (default: rows)')
    parser.add_argument('--save-manifest', action='store_true',
                       help='Save checksum manifest for future verification')
    parser.add_argument('--no-verify', action='store_true',
                       help='Skip checksum verification')
    parser.add_argument('--force', action='store_true',
                       help='Process even if verification fails')
    
    parser.add_argument('--include-errors', action='store_true',
                       help='Include error/warning columns in output')
    parser.add_argument('--include-checksums', action='store_true',
                       help='Include source row checksums in output')
    parser.add_argument('--error-report', action='store_true',
                       help='Generate separate error report')
    parser.add_argument('--verification-report', action='store_true',
                       help='Generate verification report')
    
    args = parser.parse_args()
    
    # Initialize standardizer
    standardizer = InventoryStandardizer(
        args.input,
        args.output,
        checksum_strategy=args.checksum_strategy,
        verify_checksums=not args.no_verify
    )
    
    # Load and verify
    if not standardizer.load():
        sys.exit(1)
    
    print(f"Loaded {standardizer.report['total_entries']} entries from {args.input}")
    
    # Handle verification failures
    if (standardizer.checksum_verification and 
        not standardizer.checksum_verification['matches_stored'] and
        not args.force):
        print("Error: Source data has been modified. Use --force to continue.",
              file=sys.stderr)
        if args.verification_report:
            standardizer.save_verification_report()
        sys.exit(1)
    
    # Standardize
    standardizer.standardize()
    print("✓ Standardization complete")
    
    # Detect duplicates
    standardizer.detect_duplicates()
    if standardizer.duplicates:
        print(f"⚠ Found {len(standardizer.duplicates)} object numbers with duplicates")
    
    # Mark withdrawn
    if args.withdrawn:
        try:
            with open(args.withdrawn, 'r', encoding='utf-8') as f:
                withdrawn_list = [line.strip() for line in f if line.strip()]
            standardizer.mark_withdrawn(withdrawn_list)
            print(f"✓ Marked {len(withdrawn_list)} entries as withdrawn")
        except FileNotFoundError:
            print(f"Warning: Withdrawn file not found: {args.withdrawn}", file=sys.stderr)
    
    # Validate
    standardizer.validate()
    
    # Save outputs
    standardizer.save(
        include_status=True,
        include_errors=args.include_errors,
        include_checksums=args.include_checksums
    )
    
    # Save manifest
    if args.save_manifest:
        standardizer.save_manifest()
    
    # Generate reports
    if args.error_report:
        standardizer.save_error_report()
    
    if args.verification_report and standardizer.checksum_verification:
        standardizer.save_verification_report()
    
    # Print summary
    standardizer.print_summary()


if __name__ == '__main__':
    main()
```

## Usage Examples

### First run (create manifest):
```bash
python standardize_inventory.py inventory.tsv --save-manifest
```

Output files:
- `inventory_standardized.tsv` - Standardized data
- `inventory_manifest.json` - Checksum manifest

### Subsequent runs (verify data):
```bash
python standardize_inventory.py inventory.tsv
```

The script will:
✓ Load and verify checksums from manifest
✓ Alert if data has changed
✓ Prevent processing if changes detected

### Force processing despite changes:
```bash
python standardize_inventory.py inventory.tsv --force --verification-report
```

### Advanced: Field-level checksum tracking:
```bash
python standardize_inventory.py inventory.tsv --checksum-strategy fields --save-manifest
```

## Manifest File Example (`inventory_manifest.json`)

```json
{
  "timestamp": "2024-01-15T14:32:45.123456",
  "strategy": "rows",
  "file_hash": "a1b2c3d4e5f6...",
  "record_count": 1250,
  "row_hashes": {
    "2": "hash_of_row_2",
    "3": "hash_of_row_3",
    ...
  },
  "field_hashes": {}
}
```

## Features

✅ **Three checksum strategies:**
- `file` - Single hash of entire file
- `rows` - Hash per row (detects modified records)
- `fields` - Hash per field (detects specific changes)

✅ **Verification reports:**
- Identifies modified rows
- Detects added/removed rows
- Shows field-level changes
- Exports detailed JSON report

✅ **Data integrity:**
- Prevents accidental processing of modified data
- Tracks exact changes
- Maintains audit trail with timestamps
