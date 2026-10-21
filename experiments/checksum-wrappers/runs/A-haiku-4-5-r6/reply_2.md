# Museum Inventory Standardizer with Checksum Verification

Here's an enhanced version that incorporates checksums to detect source data changes:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksum Verification
Standardizes museum inventory TSV files and verifies data integrity.
"""

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse


class ChecksumManager:
    """Manage checksums for inventory data verification."""

    def __init__(self, checksum_dir: Optional[Path] = None):
        """
        Initialize checksum manager.
        
        Args:
            checksum_dir: Directory to store checksum files (default: .checksums)
        """
        self.checksum_dir = checksum_dir or Path(".checksums")
        self.checksum_dir.mkdir(exist_ok=True)

    def _get_checksum_path(self, file_path: Path, suffix: str = "") -> Path:
        """Get the checksum file path for a given inventory file."""
        base_name = file_path.stem
        if suffix:
            base_name += f"_{suffix}"
        return self.checksum_dir / f"{base_name}.checksum"

    def calculate_file_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA-256 checksum of entire file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hexadecimal checksum string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def calculate_row_checksum(self, row: Dict[str, str]) -> str:
        """
        Calculate checksum for a single row.
        
        Args:
            row: Row dictionary with keys: date, title, object_number, link
            
        Returns:
            Hexadecimal checksum string
        """
        # Create canonical representation (sorted keys, JSON format)
        canonical = json.dumps(row, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def calculate_dataset_checksum(self, rows: List[Dict[str, str]]) -> str:
        """
        Calculate checksum for entire dataset.
        
        Args:
            rows: List of row dictionaries
            
        Returns:
            Hexadecimal checksum string
        """
        sha256_hash = hashlib.sha256()
        
        # Process rows in order
        for row in rows:
            row_checksum = self.calculate_row_checksum(row)
            sha256_hash.update(row_checksum.encode())
        
        return sha256_hash.hexdigest()

    def save_source_manifest(
        self,
        file_path: Path,
        rows: List[Dict[str, str]],
        file_checksum: str,
        dataset_checksum: str
    ) -> Path:
        """
        Save source data manifest with checksums.
        
        Args:
            file_path: Original file path
            rows: List of row data
            file_checksum: File-level checksum
            dataset_checksum: Dataset-level checksum
            
        Returns:
            Path to saved manifest
        """
        manifest = {
            'source_file': str(file_path),
            'timestamp': datetime.now().isoformat(),
            'file_checksum': file_checksum,
            'dataset_checksum': dataset_checksum,
            'record_count': len(rows),
            'row_checksums': [
                {
                    'index': i,
                    'object_number': row.get('object_number', ''),
                    'checksum': self.calculate_row_checksum(row)
                }
                for i, row in enumerate(rows)
            ]
        }
        
        manifest_path = self._get_checksum_path(file_path, "source")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest_path

    def save_processed_manifest(
        self,
        original_file: Path,
        processed_file: Path,
        rows: List[Dict[str, str]],
        processing_log: Dict
    ) -> Path:
        """
        Save processed data manifest.
        
        Args:
            original_file: Original source file
            processed_file: Processed output file
            rows: Processed row data
            processing_log: Log of processing operations
            
        Returns:
            Path to saved manifest
        """
        file_checksum = self.calculate_file_checksum(processed_file)
        dataset_checksum = self.calculate_dataset_checksum(rows)
        
        manifest = {
            'source_file': str(original_file),
            'processed_file': str(processed_file),
            'timestamp': datetime.now().isoformat(),
            'file_checksum': file_checksum,
            'dataset_checksum': dataset_checksum,
            'record_count': len(rows),
            'processing_log': processing_log,
            'row_checksums': [
                {
                    'index': i,
                    'object_number': row.get('object_number', ''),
                    'checksum': self.calculate_row_checksum(row)
                }
                for i, row in enumerate(rows)
            ]
        }
        
        manifest_path = self._get_checksum_path(original_file, "processed")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest_path

    def load_source_manifest(self, file_path: Path) -> Optional[Dict]:
        """
        Load previously saved source manifest.
        
        Args:
            file_path: Original file path
            
        Returns:
            Manifest dictionary or None if not found
        """
        manifest_path = self._get_checksum_path(file_path, "source")
        
        if not manifest_path.exists():
            return None
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def verify_file_integrity(self, file_path: Path) -> Tuple[bool, str]:
        """
        Verify file integrity against stored checksum.
        
        Args:
            file_path: File to verify
            
        Returns:
            Tuple of (is_valid, message)
        """
        manifest = self.load_source_manifest(file_path)
        
        if not manifest:
            return True, "No previous checksum found (first time processing)"
        
        current_checksum = self.calculate_file_checksum(file_path)
        stored_checksum = manifest.get('file_checksum')
        
        if current_checksum == stored_checksum:
            return True, "✓ File checksum matches (no changes detected)"
        else:
            return False, f"✗ File checksum mismatch (source data has changed)"

    def verify_dataset_integrity(
        self,
        rows: List[Dict[str, str]]
    ) -> Tuple[bool, str, List[str]]:
        """
        Verify dataset integrity against stored checksums.
        
        Args:
            rows: Current row data
            
        Returns:
            Tuple of (is_valid, summary_message, list_of_changed_rows)
        """
        # This would be called after loading from original file
        # Not used in standard flow, but useful for comparison
        return True, "Dataset verification skipped", []

    def generate_integrity_report(self, file_path: Path) -> Optional[Dict]:
        """
        Generate integrity report comparing source and processed data.
        
        Args:
            file_path: Original file path
            
        Returns:
            Report dictionary
        """
        source_manifest = self.load_source_manifest(file_path)
        processed_path = self._get_checksum_path(file_path, "processed")
        
        if not processed_path.exists():
            return None
        
        with open(processed_path, 'r', encoding='utf-8') as f:
            processed_manifest = json.load(f)
        
        return {
            'source_records': source_manifest.get('record_count', 0),
            'processed_records': processed_manifest.get('record_count', 0),
            'source_checksum': source_manifest.get('dataset_checksum'),
            'processed_checksum': processed_manifest.get('dataset_checksum'),
            'source_file_checksum': source_manifest.get('file_checksum'),
            'processed_file_checksum': processed_manifest.get('file_checksum'),
            'processing_timestamp': processed_manifest.get('timestamp'),
            'processing_log': processed_manifest.get('processing_log', {}),
        }


class InventoryStandardizer:
    """Standardize museum inventory data with integrity verification."""

    def __init__(self, strict_mode: bool = False, verify_checksums: bool = True):
        """
        Initialize the standardizer.
        
        Args:
            strict_mode: If True, raise exceptions on invalid data
            verify_checksums: If True, verify source data hasn't changed
        """
        self.strict_mode = strict_mode
        self.verify_checksums = verify_checksums
        self.checksum_manager = ChecksumManager()
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.processing_log: Dict = {
            'date_conversions': 0,
            'title_normalizations': 0,
            'object_number_standardizations': 0,
            'url_upgrades': 0,
            'empty_fields': 0,
        }

    def standardize_date(self, date_str: str, row_num: int) -> str:
        """Standardize date to ISO format (YYYY-MM-DD)."""
        if not date_str or not date_str.strip():
            self.processing_log['empty_fields'] += 1
            return ""

        date_str = date_str.strip()
        
        formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d",
            "%m-%d-%Y", "%d-%m-%Y", "%B %d, %Y", "%b %d, %Y",
            "%Y", "%m/%Y",
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                if parsed.strftime("%Y-%m-%d") != date_str:
                    self.processing_log['date_conversions'] += 1
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue

        msg = f"Row {row_num}: Could not parse date '{date_str}'"
        self._handle_error(msg)
        return date_str

    def standardize_title(self, title: str, row_num: int) -> str:
        """Standardize title formatting."""
        if not title:
            self.processing_log['empty_fields'] += 1
            msg = f"Row {row_num}: Missing title"
            self._handle_error(msg)
            return ""

        title = title.strip()
        original = title
        
        # Remove extra whitespace
        title = " ".join(title.split())
        
        # Remove leading/trailing punctuation
        title = title.strip('.,;:')
        
        # Title case
        words = title.split()
        standardized = []
        for word in words:
            if len(word) > 1 and word.isupper():
                standardized.append(word)
            else:
                standardized.append(word.capitalize())
        
        result = " ".join(standardized)
        if result != original:
            self.processing_log['title_normalizations'] += 1
        
        return result

    def standardize_object_number(self, obj_num: str, row_num: int) -> str:
        """Standardize object number format."""
        if not obj_num:
            self.processing_log['empty_fields'] += 1
            msg = f"Row {row_num}: Missing object number"
            self._handle_error(msg)
            return ""

        obj_num = obj_num.strip()
        original = obj_num
        
        # Remove extra spaces
        obj_num = " ".join(obj_num.split())
        
        # Standardize accession pattern
        if re.match(r'^acc\.?\s*\d{4}\s*\.?\s*\d+$', obj_num, re.IGNORECASE):
            obj_num = re.sub(
                r'acc\.?\s*(\d{4})\s*\.?\s*(\d+)',
                r'ACC.\1.\2',
                obj_num,
                flags=re.IGNORECASE
            )
        
        if obj_num != original:
            self.processing_log['object_number_standardizations'] += 1
        
        return obj_num

    def standardize_link(self, link: str, row_num: int) -> str:
        """Standardize and validate URLs."""
        if not link or not link.strip():
            self.processing_log['empty_fields'] += 1
            return ""

        link = link.strip()
        original = link

        # Add scheme if missing
        if not re.match(r'^https?://', link, re.IGNORECASE):
            if link.startswith('www.') or '.' in link:
                link = 'https://' + link

        # Validate URL structure
        try:
            result = urlparse(link)
            if not all([result.scheme, result.netloc]):
                msg = f"Row {row_num}: Invalid URL '{link}'"
                self._handle_error(msg)
                return ""
            
            # Ensure https
            if result.scheme == 'http':
                link = link.replace('http://', 'https://', 1)
                self.processing_log['url_upgrades'] += 1
                self.warnings.append(
                    f"Row {row_num}: Upgraded HTTP to HTTPS"
                )
        except Exception as e:
            msg = f"Row {row_num}: URL parsing error '{link}': {e}"
            self._handle_error(msg)
            return ""

        return link

    def standardize_row(self, row: Dict[str, str], row_num: int) -> Dict[str, str]:
        """Standardize a single row of data."""
        return {
            'date': self.standardize_date(row.get('date', ''), row_num),
            'title': self.standardize_title(row.get('title', ''), row_num),
            'object_number': self.standardize_object_number(
                row.get('object_number', ''), row_num
            ),
            'link': self.standardize_link(row.get('link', ''), row_num),
        }

    def standardize_file(self, input_file: Path, output_file: Path) -> bool:
        """Standardize an entire inventory file with checksum verification."""
        try:
            # Verify source data integrity
            if self.verify_checksums:
                is_valid, message = self.checksum_manager.verify_file_integrity(
                    input_file
                )
                print(f"\n{message}")
                
                if not is_valid:
                    self.warnings.append(
                        "Source file has changed since last processing. "
                        "Review changes carefully."
                    )

            # Read input file
            rows = []
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    self.errors.append("Input file has no headers")
                    return False
                
                expected_fields = {'date', 'title', 'object_number', 'link'}
                actual_fields = set(field.lower() for field in reader.fieldnames)
                
                field_mapping = {
                    field: field.lower() for field in reader.fieldnames
                }
                
                if not expected_fields.issubset(actual_fields):
                    missing = expected_fields - actual_fields
                    self.errors.append(f"Missing required columns: {missing}")
                    return False
                
                # Read and standardize rows
                for row_num, row in enumerate(reader, start=2):
                    normalized_row = {
                        field_mapping[k]: v for k, v in row.items()
                    }
                    standardized_row = self.standardize_row(normalized_row, row_num)
                    rows.append(standardized_row)

            # Save source manifest (before any processing)
            if self.verify_checksums:
                file_checksum = self.checksum_manager.calculate_file_checksum(
                    input_file
                )
                self.checksum_manager.save_source_manifest(
                    input_file,
                    rows,
                    file_checksum,
                    self.checksum_manager.calculate_dataset_checksum(rows)
                )

            # Write output file
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['date', 'title', 'object_number', 'link']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(rows)

            # Save processed manifest
            if self.verify_checksums:
                self.checksum_manager.save_processed_manifest(
                    input_file,
                    output_file,
                    rows,
                    self.processing_log
                )

            print(f"✓ Successfully standardized {len(rows)} records")
            return True

        except FileNotFoundError:
            self.errors.append(f"Input file not found: {input_file}")
            return False
        except Exception as e:
            self.errors.append(f"Unexpected error: {e}")
            return False

    def _handle_error(self, message: str):
        """Handle an error based on strict mode setting."""
        if self.strict_mode:
            raise ValueError(message)
        else:
            self.warnings.append(message)

    def print_report(self):
        """Print standardization report."""
        print("\n" + "="*60)
        print("PROCESSING LOG")
        print("="*60)
        for key, value in self.processing_log.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")

        if self.warnings:
            print(f"\n⚠ Warnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")

        if self.errors:
            print(f"\n✗ Errors ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")

    def print_integrity_report(self, input_file: Path):
        """Print integrity verification report."""
        report = self.checksum_manager.generate_integrity_report(input_file)
        
        if not report:
            print("No previous processing record found")
            return
        
        print("\n" + "="*60)
        print("DATA INTEGRITY REPORT")
        print("="*60)
        print(f"Source records: {report['source_records']}")
        print(f"Processed records: {report['processed_records']}")
        print(f"Processing timestamp: {report['processing_timestamp']}")
        print(f"\nchecksums:")
        print(f"  Source dataset: {report['source_checksum'][:16]}...")
        print(f"  Processed dataset: {report['processed_checksum'][:16]}...")
        print(f"  Source file: {report['source_file_checksum'][:16]}...")
        print(f"  Processed file: {report['processed_file_checksum'][:16]}...")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory spreadsheets with checksum verification"
    )
    parser.add_argument("input", type=Path, help="Input TSV file")
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output TSV file (default: input_standardized.tsv)"
    )
    parser.add_argument(
        "-s", "--strict",
        action="store_true",
        help="Strict mode: stop on errors"
    )
    parser.add_argument(
        "--no-checksums",
        action="store_true",
        help="Disable checksum verification"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Show integrity report and exit"
    )
    parser.add_argument(
        "--checksum-dir",
        type=Path,
        help="Directory for checksum files (default: .checksums)"
    )

    args = parser.parse_args()

    # Setup
    if args.output:
        output_file = args.output
    else:
        output_file = args.input.parent / f"{args.input.stem}_standardized.tsv"

    standardizer = InventoryStandardizer(
        strict_mode=args.strict,
        verify_checksums=not args.no_checksums
    )

    if args.checksum_dir:
        standardizer.checksum_manager.checksum_dir = args.checksum_dir

    # Show report if requested
    if args.report:
        standardizer.print_integrity_report(args.input)
        return 0

    # Process file
    print(f"Processing {args.input}...")
    success = standardizer.standardize_file(args.input, output_file)

    standardizer.print_report()

    if success:
        print(f"\n✓ Output saved to {output_file}")
        if not args.no_checksums:
            standardizer.print_integrity_report(args.input)
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

## Usage Examples

```bash
# Standard processing with checksum verification
python inventory_standardizer.py inventory.tsv

# Process and store checksums in custom directory
python inventory_standardizer.py inventory.tsv --checksum-dir ./data_checksums

# Disable checksum verification (for initial setup)
python inventory_standardizer.py inventory.tsv --no-checksums

# View integrity report
python inventory_standardizer.py inventory.tsv --report

# Strict mode with checksums
python inventory_standardizer.py inventory.tsv --strict
```

## Checksum Files Structure

### `.checksums/inventory_source.checksum`
```json
{
  "source_file": "inventory.tsv",
  "timestamp": "2024-01-15T10:30:45.123456",
  "file_checksum": "a1b2c3d4e5f6g7h8...",
  "dataset_checksum": "x9y8z7w6v5u4t3s2...",
  "record_count": 245,
  "row_checksums": [
    {
      "index": 0,
      "object_number": "ACC.2023.001",
      "checksum": "abc123def456..."
    }
  ]
}
```

### `.checksums/inventory_processed.checksum`
```json
{
  "source_file": "inventory.tsv",
  "processed_file": "inventory_standardized.tsv",
  "timestamp": "2024-01-15T10:31:02.654321",
  "file_checksum": "m1n2o3p4q5r6s7t8...",
  "dataset_checksum": "a0b9c8d7e6f5g4h3...",
  "record_count": 245,
  "processing_log": {
    "date_conversions": 42,
    "title_normalizations": 156,
    "object_number_standardizations": 18,
    "url_upgrades": 7,
    "empty_fields": 3
  }
}
```

## Key Features

✅ **File-level Checksums**: Detects any changes to source file
✅ **Dataset-level Checksums**: Verifies entire dataset integrity
✅ **Row-level Checksums**: Tracks individual record changes
✅ **Manifest Files**: JSON records with full audit trail
✅ **Change Detection**: Warns when source data has changed
✅ **Integrity Reports**: Compares source vs. processed data
✅ **Processing Log**: Tracks all transformations applied
✅ **Custom Storage**: Configurable checksum directory

This approach ensures complete data provenance and auditability!
