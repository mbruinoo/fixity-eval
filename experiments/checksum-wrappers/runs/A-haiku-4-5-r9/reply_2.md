# Museum Inventory Standardizer with Checksum Verification

Here's an enhanced version with checksum functionality:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksum Verification
Standardizes museum inventory TSV files with integrity checking
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
    """Manages checksums for data integrity verification."""
    
    CHECKSUM_ALGORITHMS = {
        'md5': hashlib.md5,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512,
    }
    
    def __init__(self, algorithm: str = 'sha256'):
        """
        Initialize checksum manager.
        
        Args:
            algorithm: Hash algorithm ('md5', 'sha256', 'sha512')
        """
        if algorithm not in self.CHECKSUM_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        self.algorithm = algorithm
        self.hash_func = self.CHECKSUM_ALGORITHMS[algorithm]
    
    def calculate_file_checksum(self, filepath: str) -> str:
        """Calculate checksum of entire file."""
        hasher = self.hash_func()
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def calculate_row_checksum(self, row: Dict[str, str]) -> str:
        """
        Calculate checksum of a single row.
        Uses serialized row content to ensure consistency.
        """
        # Create a canonical representation of the row
        canonical = json.dumps(row, sort_keys=True, separators=(',', ':'))
        hasher = self.hash_func()
        hasher.update(canonical.encode('utf-8'))
        return hasher.hexdigest()
    
    def calculate_dataset_checksum(self, rows: List[Dict[str, str]]) -> str:
        """
        Calculate checksum of entire dataset.
        Combines checksums of all rows for overall integrity.
        """
        hasher = self.hash_func()
        
        for row in rows:
            row_hash = self.calculate_row_checksum(row)
            hasher.update(row_hash.encode('utf-8'))
        
        return hasher.hexdigest()


class ChecksumManifest:
    """Manages manifest file for tracking checksums."""
    
    def __init__(self, manifest_file: str):
        self.manifest_file = manifest_file
        self.data = {
            'created': datetime.now().isoformat(),
            'algorithm': 'sha256',
            'files': {},
            'datasets': {}
        }
    
    def add_file_checksum(self, filepath: str, checksum: str, 
                         description: str = '') -> None:
        """Add file checksum to manifest."""
        self.data['files'][filepath] = {
            'checksum': checksum,
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'algorithm': self.data['algorithm']
        }
    
    def add_dataset_checksum(self, name: str, checksum: str, 
                            row_count: int, description: str = '') -> None:
        """Add dataset checksum to manifest."""
        self.data['datasets'][name] = {
            'checksum': checksum,
            'row_count': row_count,
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'algorithm': self.data['algorithm']
        }
    
    def add_row_checksums(self, row_checksums: Dict[int, str]) -> None:
        """Add checksums for individual rows."""
        if 'rows' not in self.data:
            self.data['rows'] = {}
        self.data['rows'].update(row_checksums)
    
    def save(self) -> None:
        """Save manifest to file."""
        with open(self.manifest_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)
    
    @staticmethod
    def load(manifest_file: str) -> 'ChecksumManifest':
        """Load manifest from file."""
        manifest = ChecksumManifest(manifest_file)
        
        if Path(manifest_file).exists():
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest.data = json.load(f)
        
        return manifest


class InventoryStandardizer:
    """Standardizes museum inventory data with checksum verification."""
    
    def __init__(self, input_file: str, output_file: str = None, 
                 manifest_file: str = None, verify_checksums: bool = False,
                 track_checksums: bool = True, verbose: bool = False):
        self.input_file = input_file
        self.output_file = output_file or self._generate_output_filename(input_file)
        self.manifest_file = manifest_file or self._generate_manifest_filename(self.output_file)
        self.verify_checksums = verify_checksums
        self.track_checksums = track_checksums
        self.verbose = verbose
        
        self.errors = []
        self.warnings = []
        self.checksums = {}
        
        # Initialize checksum manager
        self.checksum_manager = ChecksumManager('sha256')
        self.manifest = ChecksumManifest(self.manifest_file)
    
    def _generate_output_filename(self, input_file: str) -> str:
        """Generate output filename with _standardized suffix."""
        path = Path(input_file)
        return path.parent / f"{path.stem}_standardized{path.suffix}"
    
    def _generate_manifest_filename(self, output_file: str) -> str:
        """Generate manifest filename."""
        path = Path(output_file)
        return path.parent / f"{path.stem}_manifest.json"
    
    def log(self, message: str, level: str = "INFO"):
        """Print log message if verbose."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def verify_file_integrity(self) -> Tuple[bool, Optional[str]]:
        """
        Verify input file hasn't changed from previous run.
        
        Returns:
            (is_valid, stored_checksum)
        """
        if not self.verify_checksums:
            return True, None
        
        self.log("Verifying input file integrity...")
        
        if not Path(self.manifest_file).exists():
            self.log("No previous manifest found - creating new baseline")
            return True, None
        
        try:
            previous_manifest = ChecksumManifest.load(self.manifest_file)
            
            if self.input_file not in previous_manifest.data['files']:
                self.log("Input file not found in previous manifest")
                return True, None
            
            stored_checksum = previous_manifest.data['files'][self.input_file]['checksum']
            current_checksum = self.checksum_manager.calculate_file_checksum(self.input_file)
            
            if stored_checksum == current_checksum:
                self.log(f"✓ Input file integrity verified: {current_checksum[:16]}...")
                return True, stored_checksum
            else:
                self.warnings.append(
                    f"Input file has changed! "
                    f"Previous: {stored_checksum[:16]}... "
                    f"Current: {current_checksum[:16]}..."
                )
                return False, stored_checksum
                
        except Exception as e:
            self.errors.append(f"Error verifying checksum: {str(e)}")
            return False, None
    
    # [Include all previous methods from the original script]
    def standardize_date(self, date_str: str) -> str:
        """Standardize date to ISO format (YYYY-MM-DD)."""
        if not date_str or date_str.strip() == "":
            self.warnings.append("Empty date field found")
            return ""
        
        date_str = date_str.strip()
        
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
        
        formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%d-%m-%Y',
            '%Y/%m/%d', '%B %d, %Y', '%b %d, %Y', '%d %B %Y',
            '%d %b %Y', '%Y', '%m/%Y',
        ]
        
        for date_format in formats:
            try:
                parsed_date = datetime.strptime(date_str, date_format)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        self.warnings.append(f"Could not parse date: '{date_str}'")
        return date_str
    
    def standardize_title(self, title: str) -> str:
        """Standardize title formatting."""
        if not title:
            return ""
        title = " ".join(title.split())
        title = title.strip('.,;:"\'-')
        return title
    
    def standardize_object_number(self, obj_num: str) -> str:
        """Standardize object number formatting."""
        if not obj_num:
            return ""
        obj_num = obj_num.strip()
        if not obj_num:
            self.warnings.append("Empty object number found")
            return ""
        return obj_num
    
    def standardize_link(self, link: str) -> str:
        """Standardize URL formatting."""
        if not link or link.strip() == "":
            return ""
        
        link = link.strip()
        
        if link and not link.startswith(('http://', 'https://', 'ftp://')):
            link = 'https://' + link
        
        if not re.match(r'^https?://', link):
            self.warnings.append(f"Invalid URL format: '{link}'")
        
        return link
    
    def validate_row(self, row: Dict[str, str], row_num: int) -> bool:
        """Validate a row has required fields."""
        required_fields = ['date', 'title', 'object number', 'link']
        
        for field in required_fields:
            if field not in row:
                self.errors.append(f"Row {row_num}: Missing required column '{field}'")
                return False
        
        if not any([row.get('date'), row.get('title'), row.get('object number')]):
            self.errors.append(f"Row {row_num}: Must have at least date, title, or object number")
            return False
        
        return True
    
    def standardize_row(self, row: Dict[str, str], row_num: int) -> Dict[str, str]:
        """Apply standardization to a single row."""
        standardized = {}
        
        try:
            standardized['date'] = self.standardize_date(row.get('date', ''))
            standardized['title'] = self.standardize_title(row.get('title', ''))
            standardized['object number'] = self.standardize_object_number(row.get('object number', ''))
            standardized['link'] = self.standardize_link(row.get('link', ''))
        except Exception as e:
            self.errors.append(f"Row {row_num}: Error during standardization: {str(e)}")
            return row
        
        return standardized
    
    def process(self) -> Tuple[bool, List[str], List[str]]:
        """
        Process the inventory file and write standardized output.
        Returns (success, errors, warnings)
        """
        try:
            # Step 1: Verify file integrity
            integrity_ok, previous_checksum = self.verify_file_integrity()
            if not integrity_ok and self.verify_checksums:
                self.errors.append("Input file integrity check failed")
                return False, self.errors, self.warnings
            
            # Step 2: Calculate input file checksum
            self.log(f"Reading input file: {self.input_file}")
            
            if not Path(self.input_file).exists():
                self.errors.append(f"Input file not found: {self.input_file}")
                return False, self.errors, self.warnings
            
            input_checksum = self.checksum_manager.calculate_file_checksum(self.input_file)
            self.log(f"Input file checksum ({self.checksum_manager.algorithm}): {input_checksum}")
            
            rows = []
            row_checksums = {}
            fieldnames = None
            
            # Step 3: Read and process rows
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                fieldnames = reader.fieldnames
                
                required_fields = {'date', 'title', 'object number', 'link'}
                if not required_fields.issubset(set(fieldnames or [])):
                    self.errors.append(
                        f"Invalid header. Required columns: {required_fields}. "
                        f"Found: {set(fieldnames or [])}"
                    )
                    return False, self.errors, self.warnings
                
                for row_num, row in enumerate(reader, start=2):
                    if self.validate_row(row, row_num):
                        original_checksum = self.checksum_manager.calculate_row_checksum(row)
                        standardized_row = self.standardize_row(row, row_num)
                        rows.append(standardized_row)
                        
                        if self.track_checksums:
                            row_checksums[row_num] = {
                                'original': original_checksum,
                                'standardized': self.checksum_manager.calculate_row_checksum(standardized_row)
                            }
                    else:
                        self.log(f"Skipping invalid row {row_num}", "WARNING")
            
            self.log(f"Successfully read {len(rows)} rows")
            
            # Step 4: Calculate dataset checksum
            dataset_checksum = self.checksum_manager.calculate_dataset_checksum(rows)
            self.log(f"Dataset checksum: {dataset_checksum}")
            
            # Step 5: Write output file
            self.log(f"Writing output file: {self.output_file}")
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['date', 'title', 'object number', 'link'],
                    delimiter='\t'
                )
                writer.writeheader()
                writer.writerows(rows)
            
            output_checksum = self.checksum_manager.calculate_file_checksum(self.output_file)
            self.log(f"Output file checksum: {output_checksum}")
            
            # Step 6: Create manifest
            if self.track_checksums:
                self.manifest.data['algorithm'] = self.checksum_manager.algorithm
                
                self.manifest.add_file_checksum(
                    self.input_file,
                    input_checksum,
                    description="Original input file"
                )
                
                self.manifest.add_file_checksum(
                    self.output_file,
                    output_checksum,
                    description="Standardized output file"
                )
                
                self.manifest.add_dataset_checksum(
                    'output',
                    dataset_checksum,
                    len(rows),
                    description="Standardized dataset"
                )
                
                if row_checksums:
                    self.manifest.add_row_checksums(row_checksums)
                
                # Add metadata
                self.manifest.data['metadata'] = {
                    'input_file': self.input_file,
                    'output_file': self.output_file,
                    'rows_processed': len(rows),
                    'warnings_count': len(self.warnings),
                    'errors_count': len(self.errors),
                }
                
                self.manifest.save()
                self.log(f"Manifest saved to: {self.manifest_file}")
            
            self.log(f"Successfully wrote {len(rows)} rows")
            
            return True, self.errors, self.warnings
            
        except Exception as e:
            self.errors.append(f"Fatal error: {str(e)}")
            return False, self.errors, self.warnings


class ChecksumVerifier:
    """Verifies checksums against a manifest."""
    
    def __init__(self, manifest_file: str, verbose: bool = False):
        self.manifest_file = manifest_file
        self.verbose = verbose
        self.manifest = ChecksumManifest.load(manifest_file)
        self.checksum_manager = ChecksumManager(self.manifest.data.get('algorithm', 'sha256'))
    
    def log(self, message: str, level: str = "INFO"):
        """Print log message if verbose."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def verify_file(self, filepath: str) -> Tuple[bool, str]:
        """
        Verify a file against its stored checksum.
        
        Returns:
            (is_valid, message)
        """
        if filepath not in self.manifest.data.get('files', {}):
            return False, f"File '{filepath}' not found in manifest"
        
        stored_info = self.manifest.data['files'][filepath]
        stored_checksum = stored_info['checksum']
        
        if not Path(filepath).exists():
            return False, f"File not found: {filepath}"
        
        current_checksum = self.checksum_manager.calculate_file_checksum(filepath)
        
        is_valid = stored_checksum == current_checksum
        match_str = "✓ MATCH" if is_valid else "✗ MISMATCH"
        
        message = (
            f"{match_str} - {filepath}\n"
            f"  Stored:  {stored_checksum}\n"
            f"  Current: {current_checksum}"
        )
        
        return is_valid, message
    
    def verify_dataset(self, dataset_name: str) -> Tuple[bool, str]:
        """
        Verify a dataset against its stored checksum.
        
        Returns:
            (is_valid, message)
        """
        datasets = self.manifest.data.get('datasets', {})
        
        if dataset_name not in datasets:
            return False, f"Dataset '{dataset_name}' not found in manifest"
        
        stored_info = datasets[dataset_name]
        stored_checksum = stored_info['checksum']
        
        # Re-verify by checking the output file
        output_file = self.manifest.data['metadata']['output_file']
        
        if not Path(output_file).exists():
            return False, f"Output file not found: {output_file}"
        
        # Read and verify rows
        rows = []
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            rows = list(reader)
        
        current_checksum = self.checksum_manager.calculate_dataset_checksum(rows)
        
        is_valid = stored_checksum == current_checksum
        match_str = "✓ MATCH" if is_valid else "✗ MISMATCH"
        
        message = (
            f"{match_str} - Dataset '{dataset_name}' ({stored_info['row_count']} rows)\n"
            f"  Stored:  {stored_checksum}\n"
            f"  Current: {current_checksum}"
        )
        
        return is_valid, message
    
    def verify_all(self) -> Tuple[bool, List[str]]:
        """Verify all files and datasets in manifest."""
        results = []
        all_valid = True
        
        self.log("Verifying all files...")
        for filepath in self.manifest.data.get('files', {}):
            is_valid, message = self.verify_file(filepath)
            results.append(message)
            all_valid = all_valid and is_valid
        
        self.log("Verifying all datasets...")
        for dataset_name in self.manifest.data.get('datasets', {}):
            is_valid, message = self.verify_dataset(dataset_name)
            results.append(message)
            all_valid = all_valid and is_valid
        
        return all_valid, results


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory TSV files with checksum verification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard standardization with checksum tracking
  python standardize_inventory.py inventory.tsv
  
  # Verify file hasn't changed from previous run
  python standardize_inventory.py inventory.tsv --verify-checksums
  
  # Verify existing manifest
  python verify_inventory.py -m inventory_standardized_manifest.json
        """
    )
    
    parser.add_argument('input_file', nargs='?', help='Input TSV file')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-m', '--manifest', help='Manifest file')
    parser.add_argument('--verify-checksums', action='store_true',
                       help='Verify input file against previous checksum')
    parser.add_argument('--no-track', action='store_true',
                       help='Do not create checksum manifest')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify manifest without processing')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Verify-only mode
    if args.verify_only:
        if not args.manifest:
            print("Error: --manifest required for --verify-only mode")
            return 1
        
        verifier = ChecksumVerifier(args.manifest, args.verbose)
        all_valid, results = verifier.verify_all()
        
        print("\n" + "="*70)
        print("CHECKSUM VERIFICATION REPORT")
        print("="*70)
        for result in results:
            print(result)
        print("="*70)
        print(f"Overall: {'✓ ALL VALID' if all_valid else '✗ VERIFICATION FAILED'}\n")
        
        return 0 if all_valid else 1
    
    # Standard processing mode
    if not args.input_file:
        parser.print_help()
        return 1
    
    standardizer = InventoryStandardizer(
        args.input_file,
        args.output,
        args.manifest,
        verify_checksums=args.verify_checksums,
        track_checksums=not args.no_track,
        verbose=args.verbose
    )
    
    success, errors, warnings = standardizer.process()
    
    # Print results
    print("\n" + "="*70)
    print("STANDARDIZATION REPORT")
    print("="*70)
    
    if success:
        print(f"✓ Successfully standardized: {standardizer.output_file}")
        if not args.no_track:
            print(f"✓ Manifest saved: {standardizer.manifest_file}")
    else:
        print("✗ Standardization failed")
    
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for warning in warnings[:10]:
            print(f"  ⚠ {warning}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more")
    
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for error in errors[:10]:
            print(f"  ✗ {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    
    print("="*70 + "\n")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
```

## Usage Examples

### Create standardized file with checksum tracking:
```bash
python standardize_inventory.py inventory.tsv -v
```

### Verify file hasn't changed from previous run:
```bash
python standardize_inventory.py inventory.tsv --verify-checksums -v
```

### Only verify existing manifest:
```bash
python standardize_inventory.py --verify-only -m inventory_standardized_manifest.json -v
```

### Skip checksum tracking:
```bash
python standardize_inventory.py inventory.tsv --no-track
```

## Sample Manifest Output

```json
{
  "created": "2024-01-15T10:30:45.123456",
  "algorithm": "sha256",
  "files": {
    "inventory.tsv": {
      "checksum": "a1b2c3d4e5f6...",
      "timestamp": "2024-01-15T10:30:45.123456",
      "description": "Original input file",
      "algorithm": "sha256"
    },
    "inventory_standardized.tsv": {
      "checksum": "f6e5d4c3b2a1...",
      "timestamp": "2024-01-15T10:30:46.234567",
      "description": "Standardized output file",
      "algorithm": "sha256"
    }
  },
  "datasets": {
    "output": {
      "checksum": "xyz789abc123...",
      "row_count": 150,
      "timestamp": "2024-01-15T10:30:46.234567",
      "description": "Standardized dataset",
      "algorithm": "sha256"
    }
  },
  "rows": {
    "2": {
      "original": "hash1...",
      "standardized": "hash2..."
    }
  },
  "metadata": {
    "input_file": "inventory.tsv",
    "output_file": "inventory_standardized.tsv",
    "rows_processed": 150,
    "warnings_count": 3,
    "errors_count": 0
  }
}
```

## Key Features

✅ **File-level Checksums**: Verify entire input/output files
✅ **Dataset Checksums**: Verify all rows combined
✅ **Row Checksums**: Track changes at individual row level
✅ **Manifest Tracking**: JSON manifest of all checksums
✅ **Checksum Verification**: Detect if source data changed
✅ **Multiple Algorithms**: SHA256 (default), MD5, SHA512
✅ **Integrity Auditing**: Full audit trail of changes
✅ **Verification Mode**: Re-verify data without reprocessing
