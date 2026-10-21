# Museum Inventory Standardization with Checksum Verification

Here's an enhanced version that incorporates checksums to verify source data integrity:

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records from a TSV file with checksum verification.

This script verifies that the source data hasn't changed between runs by:
- Calculating checksums of individual records
- Storing checksums for comparison
- Detecting modifications to source data
- Allowing safe re-runs with data integrity checks
"""

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChecksumManager:
    """Manage checksums for data integrity verification."""

    def __init__(self, checksum_file: Optional[Path] = None):
        """
        Initialize checksum manager.

        Args:
            checksum_file: Path to store/load checksums (JSON format)
        """
        self.checksum_file = checksum_file
        self.checksums: Dict[str, Dict] = {}
        self.file_hash: Optional[str] = None
        
        if checksum_file and checksum_file.exists():
            self.load_checksums()

    def calculate_record_checksum(self, record: Dict) -> str:
        """
        Calculate SHA-256 checksum for a record.

        Uses canonical JSON representation for consistent hashing.

        Args:
            record: Record dictionary

        Returns:
            Hexadecimal checksum string
        """
        # Create canonical representation: consistent key order
        canonical = json.dumps(record, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def calculate_file_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA-256 checksum for entire file.

        Args:
            file_path: Path to file

        Returns:
            Hexadecimal checksum string
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()

    def add_record_checksum(self, object_number: str, record: Dict, 
                           original: Dict) -> None:
        """
        Store checksum for a record.

        Args:
            object_number: Object identifier
            record: Processed record
            original: Original unprocessed record
        """
        self.checksums[object_number] = {
            'timestamp': datetime.now().isoformat(),
            'original_checksum': self.calculate_record_checksum(original),
            'processed_checksum': self.calculate_record_checksum(record),
            'original_data': original,
            'processed_data': record
        }

    def verify_record_unchanged(self, object_number: str, current_record: Dict) -> Tuple[bool, Optional[str]]:
        """
        Verify that a record hasn't changed since last processing.

        Args:
            object_number: Object identifier
            current_record: Current record data

        Returns:
            Tuple of (is_unchanged, message)
        """
        if object_number not in self.checksums:
            return True, "No previous checksum found (first run)"

        stored = self.checksums[object_number]
        current_checksum = self.calculate_record_checksum(current_record)
        original_checksum = stored['original_checksum']

        if current_checksum == original_checksum:
            return True, "Record unchanged"
        else:
            return False, (f"Record changed since last processing. "
                          f"Was: {original_checksum[:8]}..., "
                          f"Now: {current_checksum[:8]}...")

    def save_checksums(self) -> bool:
        """
        Save checksums to file.

        Returns:
            True if successful, False otherwise
        """
        if not self.checksum_file:
            logger.warning("No checksum file specified")
            return False

        try:
            with open(self.checksum_file, 'w', encoding='utf-8') as f:
                json.dump(self.checksums, f, indent=2)
            logger.info(f"Saved {len(self.checksums)} checksums to {self.checksum_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving checksums: {e}")
            return False

    def load_checksums(self) -> bool:
        """
        Load checksums from file.

        Returns:
            True if successful, False otherwise
        """
        if not self.checksum_file or not self.checksum_file.exists():
            return False

        try:
            with open(self.checksum_file, 'r', encoding='utf-8') as f:
                self.checksums = json.load(f)
            logger.info(f"Loaded {len(self.checksums)} checksums from {self.checksum_file}")
            return True
        except Exception as e:
            logger.error(f"Error loading checksums: {e}")
            return False

    def get_checksum_summary(self) -> Dict:
        """
        Get summary of checksums.

        Returns:
            Dictionary with checksum statistics
        """
        return {
            'total_checksums': len(self.checksums),
            'file_checksum': self.file_hash,
            'file_checksum_timestamp': datetime.now().isoformat()
        }


class InventoryStandardizer:
    """Standardize museum inventory records with checksum verification."""

    def __init__(self, input_file: str, output_file: str, 
                 checksum_file: Optional[str] = None,
                 log_file: Optional[str] = None,
                 verify_only: bool = False):
        """
        Initialize the standardizer.

        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file
            checksum_file: Optional path to checksums JSON file
            log_file: Optional path to detailed log file
            verify_only: If True, only verify checksums without processing
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.verify_only = verify_only
        self.log_file = Path(log_file) if log_file else None
        
        self.checksum_manager = ChecksumManager(
            Path(checksum_file) if checksum_file else None
        )
        
        self.records: List[Dict] = []
        self.standardized_records: List[Dict] = []
        self.change_log: List[Dict] = []
        self.errors: List[Dict] = []
        self.checksum_warnings: List[Dict] = []

    def read_tsv(self) -> bool:
        """
        Read TSV file and calculate file checksum.

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                self.records = list(reader)
            
            # Calculate file checksum
            self.checksum_manager.file_hash = self.checksum_manager.calculate_file_checksum(
                self.input_file
            )
            
            logger.info(f"Read {len(self.records)} records from {self.input_file}")
            logger.info(f"File checksum: {self.checksum_manager.file_hash}")
            return True
        except FileNotFoundError:
            logger.error(f"File not found: {self.input_file}")
            return False
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return False

    @staticmethod
    def standardize_date(date_str: str) -> Tuple[str, str]:
        """Standardize date to YYYY-MM-DD format."""
        if not date_str or not date_str.strip():
            return None, date_str

        date_str = date_str.strip()
        original = date_str

        formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%Y/%m/%d',
            '%B %d, %Y', '%b %d, %Y', '%d %B %Y', '%d %b %Y', '%Y',
        ]

        from datetime import datetime as dt
        for fmt in formats:
            try:
                parsed = dt.strptime(date_str, fmt)
                standardized = parsed.strftime('%Y-%m-%d')
                return standardized, original
            except ValueError:
                continue

        return None, original

    @staticmethod
    def standardize_title(title: str) -> str:
        """Standardize title using title case."""
        if not title:
            return ""
        
        title = title.strip()
        lowercase_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 
                          'at', 'to', 'of', 'for', 'with'}
        
        words = title.split()
        result = []
        
        for i, word in enumerate(words):
            if i == 0:
                result.append(word.capitalize())
            elif word.lower() in lowercase_words:
                result.append(word.lower())
            else:
                result.append(word.capitalize())
        
        return ' '.join(result)

    @staticmethod
    def standardize_object_number(obj_num: str) -> Tuple[str, bool]:
        """Standardize object number format."""
        if not obj_num:
            return None, False

        obj_num = obj_num.strip().upper()
        normalized = ''.join(c for c in obj_num if c.isalnum() or c in '.-/')
        
        if not normalized or len(normalized) < 4:
            return normalized, False
        
        return normalized, True

    @staticmethod
    def validate_url(url: str) -> Tuple[str, bool]:
        """Validate and clean URL."""
        if not url or not url.strip():
            return "", True

        url = url.strip()

        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url

        try:
            result = urlparse(url)
            if all([result.scheme, result.netloc]):
                return url, True
            else:
                return url, False
        except Exception:
            return url, False

    def check_duplicate(self, record: Dict) -> bool:
        """Check if record is a duplicate based on object number."""
        obj_num = record.get('object_number', '')
        for existing in self.standardized_records:
            if existing.get('object_number', '') == obj_num and obj_num:
                return True
        return False

    def standardize_record(self, record: Dict, index: int) -> Optional[Dict]:
        """Standardize a single record."""
        changes = {}
        standardized = {}

        for field in ['date', 'title', 'object_number', 'link']:
            if field not in record:
                self.errors.append({
                    'record_index': index,
                    'error': f'Missing required field: {field}'
                })
                return None

            original_value = record[field]

            if field == 'date':
                std_value, original = self.standardize_date(original_value)
                standardized[field] = std_value
                if std_value != original_value and original_value:
                    changes[field] = f"{original_value} → {std_value}"

            elif field == 'title':
                std_value = self.standardize_title(original_value)
                standardized[field] = std_value
                if std_value != original_value and original_value:
                    changes[field] = f"{original_value} → {std_value}"

            elif field == 'object_number':
                std_value, is_valid = self.standardize_object_number(original_value)
                standardized[field] = std_value
                if not is_valid and original_value:
                    self.errors.append({
                        'record_index': index,
                        'field': field,
                        'error': f'Invalid object number: {original_value}'
                    })
                if std_value != original_value and original_value:
                    changes[field] = f"{original_value} → {std_value}"

            elif field == 'link':
                std_value, is_valid = self.validate_url(original_value)
                standardized[field] = std_value
                if not is_valid and original_value:
                    self.errors.append({
                        'record_index': index,
                        'field': field,
                        'error': f'Invalid URL: {original_value}'
                    })
                if std_value != original_value and original_value:
                    changes[field] = f"{original_value} → {std_value}"

        if changes:
            self.change_log.append({
                'record_index': index,
                'object_number': standardized.get('object_number'),
                'changes': changes
            })

        return standardized

    def verify_data_integrity(self) -> bool:
        """
        Verify source data hasn't changed since last run.

        Returns:
            True if all records are unchanged or first run, False if changes detected
        """
        logger.info("Verifying data integrity...")
        all_unchanged = True

        for index, record in enumerate(self.records, start=1):
            obj_num = record.get('object_number', '')
            unchanged, message = self.checksum_manager.verify_record_unchanged(
                obj_num, record
            )

            if not unchanged:
                all_unchanged = False
                self.checksum_warnings.append({
                    'record_index': index,
                    'object_number': obj_num,
                    'status': 'CHANGED',
                    'message': message
                })
                logger.warning(f"Record {obj_num}: {message}")
            else:
                logger.debug(f"Record {obj_num}: {message}")

        if all_unchanged:
            logger.info("✓ All records verified - no changes detected")
        else:
            logger.warning(f"✗ {len(self.checksum_warnings)} records have changed")

        return all_unchanged

    def process(self) -> bool:
        """Process all records."""
        if not self.records:
            logger.error("No records to process")
            return False

        logger.info("Starting standardization...")

        for index, record in enumerate(self.records, start=1):
            # Verify record integrity before processing
            obj_num = record.get('object_number', '')
            unchanged, message = self.checksum_manager.verify_record_unchanged(
                obj_num, record
            )

            if not unchanged:
                logger.warning(f"Record {index} ({obj_num}): Source data changed - {message}")

            standardized = self.standardize_record(record, index)
            
            if standardized is None:
                continue

            if self.check_duplicate(standardized):
                self.errors.append({
                    'record_index': index,
                    'error': f'Duplicate object number: {standardized.get("object_number")}'
                })
                continue

            # Store checksums
            self.checksum_manager.add_record_checksum(
                obj_num, standardized, record
            )
            self.standardized_records.append(standardized)

        logger.info(f"Standardized {len(self.standardized_records)} records")
        logger.info(f"Found {len(self.errors)} errors")
        logger.info(f"Made {len(self.change_log)} changes")

        return True

    def write_tsv(self) -> bool:
        """Write standardized records to TSV file."""
        try:
            if not self.standardized_records:
                logger.error("No records to write")
                return False

            fieldnames = ['date', 'title', 'object_number', 'link']
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(self.standardized_records)

            logger.info(f"Wrote {len(self.standardized_records)} records to {self.output_file}")
            return True
        except Exception as e:
            logger.error(f"Error writing file: {e}")
            return False

    def write_report(self, report_file: str) -> bool:
        """Write detailed report of changes and errors."""
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("MUSEUM INVENTORY STANDARDIZATION REPORT\n")
                f.write("=" * 70 + "\n\n")

                # File integrity section
                f.write("DATA INTEGRITY\n")
                f.write("-" * 70 + "\n")
                f.write(f"Input file: {self.input_file}\n")
                f.write(f"File checksum (SHA-256): {self.checksum_manager.file_hash}\n")
                f.write(f"Checksum file: {self.checksum_manager.checksum_file}\n")
                f.write(f"Source records checked: {len(self.records)}\n")
                
                if self.checksum_warnings:
                    f.write(f"Records with changed source data: {len(self.checksum_warnings)}\n")
                    for warning in self.checksum_warnings:
                        f.write(f"  - Record {warning['record_index']}: "
                               f"{warning['object_number']} - {warning['message']}\n")
                else:
                    f.write("Records with changed source data: 0 (all verified)\n")
                f.write("\n")

                # Summary
                f.write("SUMMARY\n")
                f.write("-" * 70 + "\n")
                f.write(f"Total records processed: {len(self.records)}\n")
                f.write(f"Successfully standardized: {len(self.standardized_records)}\n")
                f.write(f"Records with errors: {len(self.errors)}\n")
                f.write(f"Total changes made: {len(self.change_log)}\n\n")

                # Changes
                if self.change_log:
                    f.write("CHANGES MADE\n")
                    f.write("-" * 70 + "\n")
                    for change in self.change_log:
                        f.write(f"\nRecord {change['record_index']} "
                               f"(Object: {change['object_number']})\n")
                        for field, modification in change['changes'].items():
                            f.write(f"  {field}: {modification}\n")
                    f.write("\n")

                # Errors
                if self.errors:
                    f.write("ERRORS\n")
                    f.write("-" * 70 + "\n")
                    for error in self.errors:
                        f.write(f"Record {error['record_index']}: {error.get('error', 'Unknown error')}\n")
                    f.write("\n")

            logger.info(f"Report written to {report_file}")
            return True
        except Exception as e:
            logger.error(f"Error writing report: {e}")
            return False

    def run(self, report_file: Optional[str] = None) -> bool:
        """Run the complete standardization process."""
        if not self.read_tsv():
            return False

        # Verify data integrity if checksums exist
        if self.checksum_manager.checksums:
            self.verify_data_integrity()

        if self.verify_only:
            logger.info("Verify-only mode: skipping standardization")
            return True

        if not self.process():
            return False

        if not self.write_tsv():
            return False

        # Save checksums for next run
        if self.checksum_manager.checksum_file:
            self.checksum_manager.save_checksums()

        if report_file:
            self.write_report(report_file)

        return True


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records with checksum verification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Initial run - standardize and save checksums
  %(prog)s input.tsv output.tsv --checksums checksums.json

  # Subsequent run - verify source data hasn't changed
  %(prog)s input.tsv output.tsv --checksums checksums.json --report report.txt

  # Verify-only mode - check integrity without re-processing
  %(prog)s input.tsv output.tsv --checksums checksums.json --verify-only

  # Verbose with all details
  %(prog)s input.tsv output.tsv --checksums checksums.json -r report.txt -v
        '''
    )

    parser.add_argument('input', help='Input TSV file')
    parser.add_argument('output', help='Output TSV file')
    parser.add_argument('-c', '--checksums', help='Checksums JSON file (for integrity verification)')
    parser.add_argument('-r', '--report', help='Generate detailed report file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--verify-only', action='store_true', 
                       help='Only verify checksums without re-processing')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    standardizer = InventoryStandardizer(
        args.input,
        args.output,
        checksum_file=args.checksums,
        verify_only=args.verify_only
    )
    success = standardizer.run(args.report)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Usage Examples

### First run - calculate and store checksums:
```bash
python standardize_inventory.py input.tsv output.tsv \
  --checksums checksums.json \
  --report report.txt
```

### Subsequent run - verify data integrity:
```bash
python standardize_inventory.py input.tsv output.tsv \
  --checksums checksums.json \
  --report report.txt
```

### Verify-only mode (no reprocessing):
```bash
python standardize_inventory.py input.tsv output.tsv \
  --checksums checksums.json \
  --verify-only
```

### Verbose mode:
```bash
python standardize_inventory.py input.tsv output.tsv \
  --checksums checksums.json -v
```

## Checksum File Format

The `checksums.json` file stores checksums in this format:

```json
{
  "2023.001.A": {
    "timestamp": "2024-01-15T10:30:45.123456",
    "original_checksum": "a1b2c3d4...",
    "processed_checksum": "e5f6g7h8...",
    "original_data": {
      "date": "1/15/2023",
      "title": "the ancient vase",
      "object_number": "2023.001.A",
      "link": "http://museum.org/vase"
    },
    "processed_data": {
      "date": "2023-01-15",
      "title": "The Ancient Vase",
      "object_number": "2023001A",
      "link": "https://museum.org/vase"
    }
  }
}
```

## Key Features

- **File-Level Checksums**: SHA-256 hash of entire input file
- **Record-Level Checksums**: Individual SHA-256 hashes for each record
- **Change Detection**: Compares current data against stored checksums
- **Integrity Verification**: Warns when source records have changed
- **Verify-Only Mode**: Check integrity without reprocessing
- **Comprehensive Logging**: Tracks all checksum activities
- **Detailed Reports**: Includes data integrity section in output
