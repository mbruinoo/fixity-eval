# Museum Inventory Standardizer with Checksums

Here's an enhanced version with checksum functionality:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksum Verification

Standardizes museum inventory TSV files with checksums for data integrity.
"""

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


class ChecksumManager:
    """Manages checksums for data integrity verification."""

    ALGORITHMS = {'md5', 'sha256', 'sha512'}
    DEFAULT_ALGORITHM = 'sha256'

    def __init__(self, algorithm='sha256'):
        if algorithm not in self.ALGORITHMS:
            raise ValueError(f"Algorithm must be one of {self.ALGORITHMS}")
        self.algorithm = algorithm

    def compute_row_checksum(self, row_dict, include_fields=None):
        """
        Compute checksum for a row.
        
        Args:
            row_dict: Dictionary of row data
            include_fields: List of fields to include (None = all)
        
        Returns:
            Hex digest string
        """
        if include_fields:
            data = {k: row_dict.get(k, '') for k in include_fields}
        else:
            data = row_dict

        # Create deterministic string representation
        row_str = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
        
        hasher = hashlib.new(self.algorithm)
        hasher.update(row_str.encode('utf-8'))
        return hasher.hexdigest()

    def compute_file_checksum(self, file_path):
        """
        Compute checksum for entire file (streaming for large files).
        
        Args:
            file_path: Path to file
        
        Returns:
            Hex digest string
        """
        hasher = hashlib.new(self.algorithm)
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def compute_field_checksum(self, value):
        """Compute checksum for a single field value."""
        if value is None:
            value = ''
        value_str = str(value).strip()
        hasher = hashlib.new(self.algorithm)
        hasher.update(value_str.encode('utf-8'))
        return hasher.hexdigest()


class InventoryStandardizer:
    """Standardizes museum inventory data with checksums."""

    def __init__(self, input_file, output_file=None, verbose=False, 
                 include_checksums=True, checksum_algorithm='sha256'):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self._generate_output_path()
        self.verbose = verbose
        self.include_checksums = include_checksums
        self.checksum_manager = ChecksumManager(checksum_algorithm)
        
        # Checksum tracking
        self.source_checksums = {}  # row_num -> original checksums
        self.standardized_checksums = {}  # row_num -> standardized checksums
        self.metadata = {
            'standardization_date': datetime.now().isoformat(),
            'algorithm': checksum_algorithm,
            'source_file': str(self.input_file),
            'source_file_checksum': None,
            'output_file_checksum': None,
            'total_rows_processed': 0,
            'rows_with_changes': 0
        }
        
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_rows': 0,
            'successful': 0,
            'failed': 0,
            'cleaned_titles': 0,
            'standardized_dates': 0,
            'validated_links': 0
        }

    def _generate_output_path(self):
        """Generate output filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.input_file.parent / f"{self.input_file.stem}_standardized_{timestamp}.tsv"

    @staticmethod
    def standardize_date(date_str):
        """Standardize date to ISO 8601 format (YYYY-MM-DD)."""
        if not date_str or not str(date_str).strip():
            return ""

        date_str = str(date_str).strip()

        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

        for fmt in ["%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y", "%d-%m-%Y",
                    "%Y/%m/%d", "%B %d, %Y", "%b %d, %Y",
                    "%Y", "%m/%d/%y", "%m-%d-%y"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return date_str

    @staticmethod
    def standardize_title(title):
        """Standardize title formatting."""
        if not title:
            return ""

        title = str(title).strip()
        title = " ".join(title.split())
        title = title.replace(""", '"').replace(""", '"')
        title = title.replace("'", "'").replace("'", "'")

        if title and title[-1] in ",:;!?":
            title = title[:-1]

        if title.isupper() and len(title) > 1:
            title = title.title()

        return title

    @staticmethod
    def standardize_object_number(obj_num):
        """Standardize object number formatting."""
        if not obj_num:
            return ""

        obj_num = str(obj_num).strip()
        obj_num = re.sub(r'[\s_]+', ' ', obj_num)

        return obj_num

    @staticmethod
    def validate_link(link):
        """Validate and standardize URLs."""
        if not link:
            return ""

        link = str(link).strip()

        if not link:
            return ""

        if not re.match(r'^https?://', link):
            link = f"https://{link}"

        try:
            result = urlparse(link)
            if all([result.scheme, result.netloc]):
                return link
            else:
                return ""
        except Exception:
            return ""

    def standardize_row(self, row_num, row):
        """Standardize a single row and track checksums."""
        standardized = {}

        try:
            # Compute source checksums for individual fields
            source_checksums = {
                'date': self.checksum_manager.compute_field_checksum(row.get('date', '')),
                'title': self.checksum_manager.compute_field_checksum(row.get('title', '')),
                'object_number': self.checksum_manager.compute_field_checksum(row.get('object_number', '')),
                'link': self.checksum_manager.compute_field_checksum(row.get('link', ''))
            }
            
            # Compute checksum of original row
            source_checksums['row'] = self.checksum_manager.compute_row_checksum(row)
            self.source_checksums[row_num] = source_checksums

            # Extract and validate fields
            date = row.get('date', '').strip()
            title = row.get('title', '').strip()
            object_number = row.get('object_number', '').strip()
            link = row.get('link', '').strip()

            if not title:
                self.errors.append(f"Row {row_num}: Missing title")
                return None

            if not object_number:
                self.errors.append(f"Row {row_num}: Missing object number")
                return None

            # Standardize fields
            standardized['date'] = self.standardize_date(date)
            if date and not standardized['date']:
                self.warnings.append(f"Row {row_num}: Could not parse date '{date}'")
            elif date:
                self.stats['standardized_dates'] += 1

            standardized['title'] = self.standardize_title(title)
            self.stats['cleaned_titles'] += 1

            standardized['object_number'] = self.standardize_object_number(object_number)

            standardized['link'] = self.validate_link(link)
            if link and not standardized['link']:
                self.warnings.append(f"Row {row_num}: Invalid link '{link}'")
            elif link:
                self.stats['validated_links'] += 1

            # Compute standardized checksums
            standardized_checksums = {
                'date': self.checksum_manager.compute_field_checksum(standardized['date']),
                'title': self.checksum_manager.compute_field_checksum(standardized['title']),
                'object_number': self.checksum_manager.compute_field_checksum(standardized['object_number']),
                'link': self.checksum_manager.compute_field_checksum(standardized['link'])
            }
            standardized_checksums['row'] = self.checksum_manager.compute_row_checksum(standardized)
            self.standardized_checksums[row_num] = standardized_checksums

            # Track if row changed
            if source_checksums['row'] != standardized_checksums['row']:
                self.metadata['rows_with_changes'] += 1

            self.stats['successful'] += 1
            return standardized

        except Exception as e:
            self.errors.append(f"Row {row_num}: {str(e)}")
            return None

    def run(self):
        """Process the input file and write standardized output."""
        if not self.input_file.exists():
            print(f"Error: Input file '{self.input_file}' not found", file=sys.stderr)
            return False

        try:
            # Compute source file checksum
            self.metadata['source_file_checksum'] = self.checksum_manager.compute_file_checksum(
                self.input_file
            )

            # Read input
            rows = []
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                expected_headers = {'date', 'title', 'object_number', 'link'}
                if not reader.fieldnames:
                    print("Error: No headers found in TSV file", file=sys.stderr)
                    return False

                actual_headers = set(reader.fieldnames)
                if not expected_headers.issubset(actual_headers):
                    missing = expected_headers - actual_headers
                    print(f"Error: Missing required columns: {missing}", file=sys.stderr)
                    return False

                # Process rows
                for row_num, row in enumerate(reader, start=2):
                    self.stats['total_rows'] += 1
                    standardized = self.standardize_row(row_num, row)
                    if standardized:
                        rows.append(standardized)
                    else:
                        self.stats['failed'] += 1

            self.metadata['total_rows_processed'] = self.stats['total_rows']

            # Write output
            fieldnames = ['date', 'title', 'object_number', 'link']
            with open(self.output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(rows)

            # Compute output file checksum
            self.metadata['output_file_checksum'] = self.checksum_manager.compute_file_checksum(
                self.output_file
            )

            # Write metadata and checksums
            self._write_metadata()
            self._write_checksum_report()

            return True

        except Exception as e:
            print(f"Error processing file: {str(e)}", file=sys.stderr)
            return False

    def _write_metadata(self):
        """Write standardization metadata to JSON file."""
        metadata_file = self.output_file.with_suffix('.metadata.json')
        
        metadata = {
            'standardization': self.metadata,
            'statistics': self.stats,
            'checksum_algorithm': self.checksum_manager.algorithm
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

    def _write_checksum_report(self):
        """Write detailed checksum report to file."""
        report_file = self.output_file.with_suffix('.checksums.json')
        
        checksums_data = {
            'metadata': self.metadata,
            'rows': {}
        }

        for row_num in sorted(self.source_checksums.keys()):
            checksums_data['rows'][str(row_num)] = {
                'source': self.source_checksums.get(row_num, {}),
                'standardized': self.standardized_checksums.get(row_num, {})
            }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(checksums_data, f, indent=2)

    def verify_against_source(self, source_file=None):
        """
        Verify standardized file against source.
        
        Args:
            source_file: Path to source file (uses self.input_file if None)
        
        Returns:
            Dictionary with verification results
        """
        source_file = Path(source_file) if source_file else self.input_file
        
        if not source_file.exists():
            return {'valid': False, 'error': f"Source file not found: {source_file}"}

        try:
            source_checksum = self.checksum_manager.compute_file_checksum(source_file)
            
            verification = {
                'source_file': str(source_file),
                'computed_checksum': source_checksum,
                'stored_checksum': self.metadata.get('source_file_checksum'),
                'valid': source_checksum == self.metadata.get('source_file_checksum'),
                'timestamp': datetime.now().isoformat()
            }
            
            if not verification['valid']:
                verification['warning'] = "Source file may have been modified"
            
            return verification
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    def print_report(self):
        """Print standardization report."""
        print("\n" + "=" * 70)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("=" * 70)
        print(f"Input file:       {self.input_file}")
        print(f"Output file:      {self.output_file}")
        print(f"Checksum Algorithm: {self.checksum_manager.algorithm.upper()}")
        print("-" * 70)
        print(f"Source file checksum:  {self.metadata['source_file_checksum']}")
        print(f"Output file checksum:  {self.metadata['output_file_checksum']}")
        print("-" * 70)
        print(f"Total rows:           {self.stats['total_rows']}")
        print(f"Successful:           {self.stats['successful']}")
        print(f"Failed:               {self.stats['failed']}")
        print(f"Rows modified:        {self.metadata['rows_with_changes']}")
        print("-" * 70)
        print(f"Dates standardized:   {self.stats['standardized_dates']}")
        print(f"Titles cleaned:       {self.stats['cleaned_titles']}")
        print(f"Links validated:      {self.stats['validated_links']}")
        print("=" * 70)

        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"  ⚠ {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")

        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"  ✗ {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")

        print(f"\nChecksum reports written to:")
        print(f"  - {self.output_file.with_suffix('.checksums.json')}")
        print(f"  - {self.output_file.with_suffix('.metadata.json')}")
        print()


class ChecksumVerifier:
    """Verifies standardized data against checksums."""

    def __init__(self, checksum_report_file):
        self.report_file = Path(checksum_report_file)
        self.checksums_data = self._load_checksums()

    def _load_checksums(self):
        """Load checksum data from JSON file."""
        if not self.report_file.exists():
            raise FileNotFoundError(f"Checksum report not found: {self.report_file}")

        with open(self.report_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def verify_row(self, row_num, row_data):
        """
        Verify a row against stored checksums.
        
        Args:
            row_num: Row number
            row_data: Dictionary with row data
        
        Returns:
            Dictionary with verification results
        """
        row_num_str = str(row_num)
        
        if row_num_str not in self.checksums_data['rows']:
            return {'valid': False, 'error': f"Row {row_num} not found in checksums"}

        stored = self.checksums_data['rows'][row_num_str]['standardized']
        algorithm = self.checksums_data['metadata']['algorithm']
        checksum_manager = ChecksumManager(algorithm)

        results = {'row_num': row_num, 'matches': {}}

        for field in ['date', 'title', 'object_number', 'link']:
            computed = checksum_manager.compute_field_checksum(row_data.get(field, ''))
            stored_checksum = stored.get(field)
            matches = computed == stored_checksum
            results['matches'][field] = {
                'computed': computed,
                'stored': stored_checksum,
                'match': matches
            }

        results['valid'] = all(m['match'] for m in results['matches'].values())
        return results

    def verify_all_rows(self, data_file):
        """
        Verify all rows in a standardized data file.
        
        Args:
            data_file: Path to standardized TSV file
        
        Returns:
            Dictionary with overall verification results
        """
        data_file = Path(data_file)
        
        if not data_file.exists():
            return {'valid': False, 'error': f"Data file not found: {data_file}"}

        results = {
            'data_file': str(data_file),
            'timestamp': datetime.now().isoformat(),
            'total_rows': 0,
            'valid_rows': 0,
            'invalid_rows': 0,
            'row_results': [],
            'all_valid': True
        }

        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row_num, row in enumerate(reader, start=2):
                    results['total_rows'] += 1
                    row_result = self.verify_row(row_num, row)
                    results['row_results'].append(row_result)
                    
                    if row_result['valid']:
                        results['valid_rows'] += 1
                    else:
                        results['invalid_rows'] += 1
                        results['all_valid'] = False

            return results

        except Exception as e:
            return {'valid': False, 'error': str(e)}

    def print_verification_report(self, results):
        """Print verification results."""
        print("\n" + "=" * 70)
        print("CHECKSUM VERIFICATION REPORT")
        print("=" * 70)
        print(f"Data file:      {results.get('data_file')}")
        print(f"Timestamp:      {results.get('timestamp')}")
        print("-" * 70)
        print(f"Total rows:     {results.get('total_rows')}")
        print(f"Valid rows:     {results.get('valid_rows')}")
        print(f"Invalid rows:   {results.get('invalid_rows')}")
        print("-" * 70)
        
        if results.get('all_valid'):
            print("✓ ALL ROWS VERIFIED SUCCESSFULLY")
        else:
            print("✗ SOME ROWS FAILED VERIFICATION")
            print("\nFailed rows:")
            for row_result in results.get('row_results', []):
                if not row_result['valid']:
                    print(f"\n  Row {row_result['row_num']}:")
                    for field, match_info in row_result['matches'].items():
                        if not match_info['match']:
                            print(f"    {field}: MISMATCH")
                            print(f"      Stored:   {match_info['stored']}")
                            print(f"      Computed: {match_info['computed']}")

        print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory TSV files with checksums"
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Standardize command
    standardize_parser = subparsers.add_parser('standardize', help='Standardize inventory file')
    standardize_parser.add_argument('input', help='Path to input TSV file')
    standardize_parser.add_argument('-o', '--output', help='Path to output TSV file')
    standardize_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    standardize_parser.add_argument(
        '-a', '--algorithm',
        choices=['md5', 'sha256', 'sha512'],
        default='sha256',
        help='Checksum algorithm (default: sha256)'
    )

    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify standardized data')
    verify_parser.add_argument('data', help='Path to standardized TSV file')
    verify_parser.add_argument('checksums', help='Path to checksums JSON file')

    args = parser.parse_args()

    if args.command == 'standardize':
        standardizer = InventoryStandardizer(
            args.input,
            args.output,
            args.verbose,
            checksum_algorithm=args.algorithm
        )

        print(f"Processing {standardizer.input_file}...")
        if standardizer.run():
            print(f"✓ Successfully standardized to {standardizer.output_file}")
            standardizer.print_report()
        else:
            print("✗ Standardization failed")
            sys.exit(1)

    elif args.command == 'verify':
        print(f"Verifying {args.data} against {args.checksums}...")
        verifier = ChecksumVerifier(args.checksums)
        results = verifier.verify_all_rows(args.data)
        verifier.print_verification_report(results)
        
        if not results.get('all_valid', False):
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

## Usage Examples

### Standardize with checksums:
```bash
# Default (SHA256)
python museum_standardizer.py standardize inventory.tsv

# Specify output and algorithm
python museum_standardizer.py standardize inventory.tsv -o cleaned.tsv -a sha512

# Verbose mode
python museum_standardizer.py standardize inventory.tsv -v
```

### Verify standardized data:
```bash
python museum_standardizer.py verify cleaned.tsv cleaned.checksums.json
```

## Output Files

The standardizer creates:

1. **cleaned.tsv** - Standardized data
2. **cleaned.checksums.json** - Field-level and row-level checksums
3. **cleaned.metadata.json** - Standardization metadata

### Sample checksums.json:
```json
{
  "metadata": {
    "standardization_date": "2024-01-15T10:30:00",
    "algorithm": "sha256",
    "source_file": "inventory.tsv",
    "source_file_checksum": "abc123...",
    "output_file_checksum": "def456...",
    "total_rows_processed": 100,
    "rows_with_changes": 45
  },
  "rows": {
    "2": {
      "source": {
        "date": "e3b0c44...",
        "title": "f1d2d2f...",
        "object_number": "098f6bc...",
        "link": "a665a45...",
        "row": "7c4a8d0..."
      },
      "standardized": {
        "date": "d41d8cd...",
        "title": "356a192...",
        "object_number": "6d7fce9...",
        "link": "1b4f0e9...",
        "row": "e2e107a..."
      }
    }
  }
}
```

## Key Features

✓ **Field-level checksums** - Track changes to individual fields
✓ **Row-level checksums** - Detect any row changes
✓ **File checksums** - Verify source file integrity
✓ **Multiple algorithms** - SHA256 (default), MD5, SHA512
✓ **Verification tool** - Compare standardized data against checksums
✓ **Metadata tracking** - Store standardization details
✓ **Audit trail** - Complete record of transformations

This ensures data integrity and provides verification capability!
