# Museum Inventory Standardizer with Checksums

Here's an enhanced version incorporating checksums for data integrity verification:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksums
Standardizes museum inventory TSV files and generates checksums for verification.
"""

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse


class ChecksumManager:
    """Manages checksums for data integrity verification."""
    
    HASH_ALGORITHM = 'sha256'
    
    @staticmethod
    def hash_value(value: str) -> str:
        """
        Generate hash for a single value.
        
        Args:
            value: String to hash
            
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(value.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_row(row: Dict[str, str], fields: List[str] = None) -> str:
        """
        Generate hash for entire row.
        
        Args:
            row: Dictionary with row data
            fields: List of fields to include (None = all)
            
        Returns:
            Hexadecimal hash string
        """
        if fields is None:
            fields = sorted(row.keys())
        
        # Create deterministic string representation
        row_str = '|'.join(str(row.get(field, '')) for field in sorted(fields))
        return hashlib.sha256(row_str.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_file(filepath: Path) -> str:
        """
        Generate hash for entire file.
        
        Args:
            filepath: Path to file
            
        Returns:
            Hexadecimal hash string
        """
        hash_obj = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()


class InventoryStandardizer:
    """Standardizes museum inventory data with checksum tracking."""
    
    def __init__(self, input_file: str, output_file: str, 
                 manifest_file: str = None, strict: bool = False):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file
            manifest_file: Path to checksum manifest (auto-generated if None)
            strict: If True, reject rows with errors; if False, fix them
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.manifest_file = Path(manifest_file) if manifest_file else \
            self.output_file.parent / f"{self.output_file.stem}_manifest.json"
        self.strict = strict
        
        self.errors = []
        self.warnings = []
        self.rows_processed = 0
        self.rows_cleaned = 0
        
        # Checksum tracking
        self.checksums = {
            'source_file': None,
            'output_file': None,
            'rows': {},  # Maps original row hash -> transformed row hash
            'metadata': {
                'algorithm': ChecksumManager.HASH_ALGORITHM,
                'timestamp': datetime.now().isoformat(),
                'total_rows': 0,
                'rows_with_changes': 0,
            }
        }
    
    def standardize_date(self, date_str: str) -> Tuple[str, bool]:
        """
        Standardize date to ISO 8601 format (YYYY-MM-DD).
        
        Args:
            date_str: Raw date string
            
        Returns:
            Tuple of (standardized_date, is_valid)
        """
        if not date_str or not date_str.strip():
            return "", False
        
        date_str = date_str.strip()
        
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d"), True
            except ValueError:
                continue
        
        year_match = re.search(r'\d{4}', date_str)
        if year_match:
            year = year_match.group()
            self.warnings.append(f"Could not parse date '{date_str}', extracted year: {year}")
            return year, False
        
        return "", False
    
    def standardize_title(self, title: str) -> str:
        """
        Standardize title formatting.
        
        Args:
            title: Raw title string
            
        Returns:
            Standardized title
        """
        if not title:
            return ""
        
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)
        title = title.rstrip('.,;:!?')
        
        return title
    
    def standardize_object_number(self, obj_num: str) -> Tuple[str, bool]:
        """
        Standardize object number format.
        
        Args:
            obj_num: Raw object number
            
        Returns:
            Tuple of (standardized_number, is_valid)
        """
        if not obj_num or not obj_num.strip():
            return "", False
        
        obj_num = obj_num.strip().upper()
        obj_num = re.sub(r'\s+', ' ', obj_num)
        
        if re.search(r'[a-zA-Z0-9]', obj_num):
            return obj_num, True
        
        return obj_num, False
    
    def standardize_link(self, link: str) -> Tuple[str, bool]:
        """
        Standardize and validate URL format.
        
        Args:
            link: Raw URL string
            
        Returns:
            Tuple of (standardized_link, is_valid)
        """
        if not link or not link.strip():
            return "", False
        
        link = link.strip()
        
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', link):
            if link.startswith('www.'):
                link = 'https://' + link
            elif not link.startswith('/'):
                link = 'https://' + link
        
        try:
            result = urlparse(link)
            is_valid = all([result.scheme, result.netloc])
        except Exception:
            is_valid = False
        
        return link, is_valid
    
    def process_row(self, row: Dict[str, str]) -> Tuple[Dict[str, str], List[str]]:
        """
        Process and standardize a single row.
        
        Args:
            row: Dictionary with raw data
            
        Returns:
            Tuple of (cleaned_row, error_list)
        """
        errors = []
        cleaned_row = {}
        
        date_val, date_valid = self.standardize_date(row.get('date', ''))
        if not date_valid and row.get('date', '').strip():
            errors.append(f"Invalid date format: '{row.get('date', '')}'")
        cleaned_row['date'] = date_val
        
        title_val = self.standardize_title(row.get('title', ''))
        if not title_val:
            errors.append("Missing or empty title")
        cleaned_row['title'] = title_val
        
        obj_num, obj_valid = self.standardize_object_number(row.get('object_number', ''))
        if not obj_valid:
            errors.append(f"Invalid object number: '{row.get('object_number', '')}'")
        cleaned_row['object_number'] = obj_num
        
        link_val, link_valid = self.standardize_link(row.get('link', ''))
        if not link_valid and row.get('link', '').strip():
            errors.append(f"Invalid URL format: '{row.get('link', '')}'")
        cleaned_row['link'] = link_val
        
        return cleaned_row, errors
    
    def read_input(self) -> List[Dict[str, str]]:
        """
        Read and parse the input TSV file.
        
        Returns:
            List of row dictionaries
        """
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        rows = []
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    raise ValueError("Empty file or missing headers")
                
                expected_fields = {'date', 'title', 'object_number', 'link'}
                actual_fields = set(reader.fieldnames)
                
                if actual_fields != expected_fields:
                    missing = expected_fields - actual_fields
                    extra = actual_fields - expected_fields
                    if missing:
                        raise ValueError(f"Missing required fields: {missing}")
                    if extra:
                        self.warnings.append(f"Extra fields will be ignored: {extra}")
                
                rows = list(reader)
        except Exception as e:
            raise ValueError(f"Error reading input file: {e}")
        
        return rows
    
    def write_output(self, cleaned_rows: List[Dict[str, str]]) -> None:
        """
        Write standardized data to output TSV file.
        
        Args:
            cleaned_rows: List of cleaned row dictionaries
        """
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        fieldnames = ['date', 'title', 'object_number', 'link']
        
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(cleaned_rows)
        except Exception as e:
            raise IOError(f"Error writing output file: {e}")
    
    def write_manifest(self) -> None:
        """Write checksum manifest to JSON file."""
        self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.manifest_file, 'w', encoding='utf-8') as f:
                json.dump(self.checksums, f, indent=2)
            print(f"Manifest written to {self.manifest_file}", file=sys.stderr)
        except Exception as e:
            raise IOError(f"Error writing manifest file: {e}")
    
    def run(self) -> bool:
        """
        Execute the standardization process with checksums.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read input
            print(f"Reading inventory from {self.input_file}...", file=sys.stderr)
            rows = self.read_input()
            print(f"Found {len(rows)} records.", file=sys.stderr)
            
            # Calculate source file checksum
            self.checksums['source_file'] = ChecksumManager.hash_file(self.input_file)
            print(f"Source file SHA256: {self.checksums['source_file']}", file=sys.stderr)
            
            # Process each row
            cleaned_rows = []
            for i, row in enumerate(rows, 1):
                # Calculate hash of original row
                original_hash = ChecksumManager.hash_row(row)
                
                cleaned_row, row_errors = self.process_row(row)
                self.rows_processed += 1
                
                # Calculate hash of cleaned row
                cleaned_hash = ChecksumManager.hash_row(cleaned_row)
                
                # Track mapping
                self.checksums['rows'][original_hash] = {
                    'cleaned_hash': cleaned_hash,
                    'row_number': i,
                    'changed': original_hash != cleaned_hash,
                    'errors': row_errors if row_errors else None,
                }
                
                if original_hash != cleaned_hash:
                    self.checksums['metadata']['rows_with_changes'] += 1
                
                if row_errors:
                    error_msg = f"Row {i}: {'; '.join(row_errors)}"
                    if self.strict:
                        self.errors.append(error_msg)
                        continue
                    else:
                        self.warnings.append(error_msg)
                        self.rows_cleaned += 1
                else:
                    self.rows_cleaned += 1
                
                cleaned_rows.append(cleaned_row)
            
            # Write output
            if cleaned_rows:
                print(f"Writing {len(cleaned_rows)} cleaned records to {self.output_file}...", 
                      file=sys.stderr)
                self.write_output(cleaned_rows)
                
                # Calculate output file checksum
                self.checksums['output_file'] = ChecksumManager.hash_file(self.output_file)
                print(f"Output file SHA256: {self.checksums['output_file']}", file=sys.stderr)
            
            # Update metadata
            self.checksums['metadata']['total_rows'] = len(cleaned_rows)
            
            # Write manifest
            self.write_manifest()
            
            # Report results
            self.print_report()
            
            return len(self.errors) == 0
            
        except Exception as e:
            print(f"Fatal error: {e}", file=sys.stderr)
            return False
    
    def print_report(self) -> None:
        """Print processing report."""
        print("\n" + "="*60, file=sys.stderr)
        print("STANDARDIZATION REPORT", file=sys.stderr)
        print("="*60, file=sys.stderr)
        print(f"Total rows processed: {self.rows_processed}", file=sys.stderr)
        print(f"Rows with issues: {self.rows_processed - self.rows_cleaned}", 
              file=sys.stderr)
        print(f"Rows modified: {self.checksums['metadata']['rows_with_changes']}", 
              file=sys.stderr)
        
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):", file=sys.stderr)
            for warning in self.warnings[:10]:
                print(f"  - {warning}", file=sys.stderr)
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more", file=sys.stderr)
        
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):", file=sys.stderr)
            for error in self.errors[:10]:
                print(f"  - {error}", file=sys.stderr)
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more", file=sys.stderr)
        
        print("="*60 + "\n", file=sys.stderr)


class ChecksumVerifier:
    """Verifies checksums and data integrity."""
    
    def __init__(self, manifest_file: str, input_file: str = None, 
                 output_file: str = None):
        """
        Initialize verifier.
        
        Args:
            manifest_file: Path to manifest JSON file
            input_file: Path to source file (optional)
            output_file: Path to output file (optional)
        """
        self.manifest_file = Path(manifest_file)
        self.input_file = Path(input_file) if input_file else None
        self.output_file = Path(output_file) if output_file else None
        
        self.manifest = None
        self.verification_results = {}
    
    def load_manifest(self) -> bool:
        """
        Load manifest from JSON file.
        
        Returns:
            True if successful
        """
        if not self.manifest_file.exists():
            print(f"Manifest file not found: {self.manifest_file}", file=sys.stderr)
            return False
        
        try:
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                self.manifest = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading manifest: {e}", file=sys.stderr)
            return False
    
    def verify_file(self, filepath: Path, expected_hash: str, 
                    file_type: str) -> bool:
        """
        Verify file integrity.
        
        Args:
            filepath: Path to file
            expected_hash: Expected checksum
            file_type: Description of file (e.g., "source", "output")
            
        Returns:
            True if checksum matches
        """
        if not filepath.exists():
            print(f"{file_type.capitalize()} file not found: {filepath}", 
                  file=sys.stderr)
            return False
        
        actual_hash = ChecksumManager.hash_file(filepath)
        matches = actual_hash == expected_hash
        
        status = "✓ VERIFIED" if matches else "✗ FAILED"
        print(f"{file_type.capitalize()} ({status}):", file=sys.stderr)
        print(f"  Expected: {expected_hash}", file=sys.stderr)
        print(f"  Actual:   {actual_hash}", file=sys.stderr)
        
        self.verification_results[file_type] = matches
        return matches
    
    def verify(self) -> bool:
        """
        Perform full verification.
        
        Returns:
            True if all checks pass
        """
        if not self.load_manifest():
            return False
        
        print("\n" + "="*60, file=sys.stderr)
        print("CHECKSUM VERIFICATION REPORT", file=sys.stderr)
        print("="*60, file=sys.stderr)
        print(f"Algorithm: {self.manifest.get('metadata', {}).get('algorithm')}", 
              file=sys.stderr)
        print(f"Timestamp: {self.manifest.get('metadata', {}).get('timestamp')}", 
              file=sys.stderr)
        print()
        
        all_pass = True
        
        # Verify source file
        if self.input_file and self.manifest.get('source_file'):
            if not self.verify_file(self.input_file, 
                                   self.manifest['source_file'], 
                                   'source'):
                all_pass = False
            print()
        
        # Verify output file
        if self.output_file and self.manifest.get('output_file'):
            if not self.verify_file(self.output_file, 
                                   self.manifest['output_file'], 
                                   'output'):
                all_pass = False
            print()
        
        # Report statistics
        metadata = self.manifest.get('metadata', {})
        print(f"Total rows: {metadata.get('total_rows', 'N/A')}", file=sys.stderr)
        print(f"Rows with changes: {metadata.get('rows_with_changes', 'N/A')}", 
              file=sys.stderr)
        
        # Sample some row checksums
        rows_with_errors = sum(1 for r in self.manifest.get('rows', {}).values() 
                               if r.get('errors'))
        print(f"Rows with validation errors: {rows_with_errors}", file=sys.stderr)
        
        print("="*60 + "\n", file=sys.stderr)
        
        return all_pass


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory TSV files with checksums",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standardize and generate checksums
  %(prog)s standardize input.tsv output.tsv
  
  # Standardize with custom manifest path
  %(prog)s standardize input.tsv output.tsv --manifest checksums.json
  
  # Verify checksums
  %(prog)s verify checksums.json --input input.tsv --output output.tsv
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Standardize command
    standardize_parser = subparsers.add_parser('standardize', 
                                               help='Standardize inventory file')
    standardize_parser.add_argument('input', help='Input TSV file path')
    standardize_parser.add_argument('output', help='Output TSV file path')
    standardize_parser.add_argument('--manifest', 
                                   help='Output manifest file path (auto-generated if omitted)')
    standardize_parser.add_argument('--strict', action='store_true',
                                   help='Reject rows with errors')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify checksums')
    verify_parser.add_argument('manifest', help='Manifest JSON file path')
    verify_parser.add_argument('--input', help='Source TSV file path')
    verify_parser.add_argument('--output', help='Output TSV file path')
    
    args = parser.parse_args()
    
    if args.command == 'standardize':
        standardizer = InventoryStandardizer(args.input, args.output, 
                                            args.manifest, args.strict)
        success = standardizer.run()
        sys.exit(0 if success else 1)
    
    elif args.command == 'verify':
        verifier = ChecksumVerifier(args.manifest, args.input, args.output)
        success = verifier.verify()
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## Usage

### Standardize with checksums:
```bash
python museum_standardizer.py standardize input.tsv output.tsv
```

### Standardize with custom manifest path:
```bash
python museum_standardizer.py standardize input.tsv output.tsv \
  --manifest my_checksums.json
```

### Verify checksums:
```bash
python museum_standardizer.py verify output_manifest.json \
  --input input.tsv --output output.tsv
```

## Example Manifest Output

```json
{
  "source_file": "a1b2c3d4e5f6...",
  "output_file": "f6e5d4c3b2a1...",
  "rows": {
    "original_hash_1": {
      "cleaned_hash": "cleaned_hash_1",
      "row_number": 1,
      "changed": true,
      "errors": null
    },
    "original_hash_2": {
      "cleaned_hash": "cleaned_hash_2",
      "row_number": 2,
      "changed": false,
      "errors": ["Missing object number"]
    }
  },
  "metadata": {
    "algorithm": "sha256",
    "timestamp": "2024-01-15T10:30:45.123456",
    "total_rows": 150,
    "rows_with_changes": 45
  }
}
```

## Key Features

1. **File-level checksums**: SHA256 hashes for entire files
2. **Row-level checksums**: Track which rows were modified
3. **Reversibility**: Original row hashes allow mapping back to source
4. **Verification**: Separate command to verify data integrity
5. **Detailed manifest**: JSON format for easy integration with other tools
6. **Change tracking**: Identify exactly which rows were modified
7. **Error logging**: Associate errors with specific rows in manifest

This approach enables complete data provenance and auditability!
