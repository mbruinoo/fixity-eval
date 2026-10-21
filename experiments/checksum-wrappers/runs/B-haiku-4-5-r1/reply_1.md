# Museum Inventory Standardization Script

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records from a TSV file.

This script reads museum inventory records and standardizes them by:
- Normalizing date formats (YYYY-MM-DD)
- Standardizing title capitalization
- Validating and formatting object numbers
- Checking and cleaning URLs
- Removing duplicates
- Generating a report of changes
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InventoryStandardizer:
    """Standardize museum inventory records."""

    def __init__(self, input_file: str, output_file: str, log_file: str = None):
        """
        Initialize the standardizer.

        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file
            log_file: Optional path to detailed log file
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.log_file = Path(log_file) if log_file else None
        
        self.records: List[Dict] = []
        self.standardized_records: List[Dict] = []
        self.change_log: List[Dict] = []
        self.errors: List[Dict] = []

    def read_tsv(self) -> bool:
        """
        Read TSV file.

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                self.records = list(reader)
            logger.info(f"Read {len(self.records)} records from {self.input_file}")
            return True
        except FileNotFoundError:
            logger.error(f"File not found: {self.input_file}")
            return False
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return False

    @staticmethod
    def standardize_date(date_str: str) -> Tuple[str, str]:
        """
        Standardize date to YYYY-MM-DD format.

        Args:
            date_str: Date string in various formats

        Returns:
            Tuple of (standardized_date, original_date) or (None, original) if invalid
        """
        if not date_str or not date_str.strip():
            return None, date_str

        date_str = date_str.strip()
        original = date_str

        # Common date formats to try
        formats = [
            '%Y-%m-%d',      # 2023-01-15
            '%m/%d/%Y',      # 01/15/2023
            '%d/%m/%Y',      # 15/01/2023
            '%m-%d-%Y',      # 01-15-2023
            '%Y/%m/%d',      # 2023/01/15
            '%B %d, %Y',     # January 15, 2023
            '%b %d, %Y',     # Jan 15, 2023
            '%d %B %Y',      # 15 January 2023
            '%d %b %Y',      # 15 Jan 2023
            '%Y',            # 2023
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                standardized = parsed.strftime('%Y-%m-%d')
                return standardized, original
            except ValueError:
                continue

        return None, original

    @staticmethod
    def standardize_title(title: str) -> str:
        """
        Standardize title using title case.

        Args:
            title: Title string

        Returns:
            Standardized title
        """
        if not title:
            return ""
        
        title = title.strip()
        
        # Words that should be lowercase (unless first word)
        lowercase_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'of', 'for', 'with'}
        
        words = title.split()
        result = []
        
        for i, word in enumerate(words):
            if i == 0:  # First word always capitalized
                result.append(word.capitalize())
            elif word.lower() in lowercase_words:
                result.append(word.lower())
            else:
                result.append(word.capitalize())
        
        return ' '.join(result)

    @staticmethod
    def standardize_object_number(obj_num: str) -> Tuple[str, bool]:
        """
        Standardize object number format.

        Expects format: YYYY.###.## or similar
        Returns standardized format and validity flag.

        Args:
            obj_num: Object number string

        Returns:
            Tuple of (standardized_number, is_valid)
        """
        if not obj_num:
            return None, False

        obj_num = obj_num.strip().upper()
        
        # Remove common separators and normalize
        # Allow alphanumeric with dots, dashes, slashes
        normalized = ''.join(c for c in obj_num if c.isalnum() or c in '.-/')
        
        if not normalized:
            return None, False
        
        # Check minimum length (usually at least 4 characters)
        if len(normalized) < 4:
            return normalized, False
        
        return normalized, True

    @staticmethod
    def validate_url(url: str) -> Tuple[str, bool]:
        """
        Validate and clean URL.

        Args:
            url: URL string

        Returns:
            Tuple of (cleaned_url, is_valid)
        """
        if not url or not url.strip():
            return "", True  # Empty is valid (optional field)

        url = url.strip()

        # Add scheme if missing
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url

        try:
            result = urlparse(url)
            # Check for required components
            if all([result.scheme, result.netloc]):
                return url, True
            else:
                return url, False
        except Exception:
            return url, False

    def check_duplicate(self, record: Dict) -> bool:
        """
        Check if record is a duplicate based on object number.

        Args:
            record: Record dictionary

        Returns:
            True if duplicate, False otherwise
        """
        obj_num = record.get('object_number', '')
        for existing in self.standardized_records:
            if existing.get('object_number', '') == obj_num and obj_num:
                return True
        return False

    def standardize_record(self, record: Dict, index: int) -> Dict:
        """
        Standardize a single record.

        Args:
            record: Raw record dictionary
            index: Record index for logging

        Returns:
            Standardized record dictionary
        """
        changes = {}
        standardized = {}

        # Process each field
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

        # Log changes
        if changes:
            self.change_log.append({
                'record_index': index,
                'object_number': standardized.get('object_number'),
                'changes': changes
            })

        return standardized

    def process(self) -> bool:
        """
        Process all records.

        Returns:
            True if successful, False otherwise
        """
        if not self.records:
            logger.error("No records to process")
            return False

        logger.info("Starting standardization...")

        for index, record in enumerate(self.records, start=1):
            standardized = self.standardize_record(record, index)
            
            if standardized is None:
                continue

            # Check for duplicates
            if self.check_duplicate(standardized):
                self.errors.append({
                    'record_index': index,
                    'error': f'Duplicate object number: {standardized.get("object_number")}'
                })
                continue

            self.standardized_records.append(standardized)

        logger.info(f"Standardized {len(self.standardized_records)} records")
        logger.info(f"Found {len(self.errors)} errors")
        logger.info(f"Made {len(self.change_log)} changes")

        return True

    def write_tsv(self) -> bool:
        """
        Write standardized records to TSV file.

        Returns:
            True if successful, False otherwise
        """
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
        """
        Write detailed report of changes and errors.

        Args:
            report_file: Path to report file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("MUSEUM INVENTORY STANDARDIZATION REPORT\n")
                f.write("=" * 60 + "\n\n")

                # Summary
                f.write("SUMMARY\n")
                f.write("-" * 60 + "\n")
                f.write(f"Total records processed: {len(self.records)}\n")
                f.write(f"Successfully standardized: {len(self.standardized_records)}\n")
                f.write(f"Records with errors: {len(self.errors)}\n")
                f.write(f"Total changes made: {len(self.change_log)}\n\n")

                # Changes
                if self.change_log:
                    f.write("CHANGES MADE\n")
                    f.write("-" * 60 + "\n")
                    for change in self.change_log:
                        f.write(f"\nRecord {change['record_index']} "
                               f"(Object: {change['object_number']})\n")
                        for field, modification in change['changes'].items():
                            f.write(f"  {field}: {modification}\n")
                    f.write("\n")

                # Errors
                if self.errors:
                    f.write("ERRORS\n")
                    f.write("-" * 60 + "\n")
                    for error in self.errors:
                        f.write(f"Record {error['record_index']}: {error.get('error', 'Unknown error')}\n")
                    f.write("\n")

            logger.info(f"Report written to {report_file}")
            return True
        except Exception as e:
            logger.error(f"Error writing report: {e}")
            return False

    def run(self, report_file: str = None) -> bool:
        """
        Run the complete standardization process.

        Args:
            report_file: Optional path for detailed report

        Returns:
            True if successful, False otherwise
        """
        if not self.read_tsv():
            return False

        if not self.process():
            return False

        if not self.write_tsv():
            return False

        if report_file:
            self.write_report(report_file)

        return True


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s input.tsv output.tsv
  %(prog)s input.tsv output.tsv --report report.txt
  %(prog)s input.tsv output.tsv -r report.txt --log debug.log
        '''
    )

    parser.add_argument('input', help='Input TSV file')
    parser.add_argument('output', help='Output TSV file')
    parser.add_argument('-r', '--report', help='Generate detailed report file')
    parser.add_argument('-l', '--log', help='Log file path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    standardizer = InventoryStandardizer(args.input, args.output, args.log)
    success = standardizer.run(args.report)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Usage

### Basic usage:
```bash
python standardize_inventory.py input.tsv output.tsv
```

### With detailed report:
```bash
python standardize_inventory.py input.tsv output.tsv --report changes.txt
```

### Verbose mode:
```bash
python standardize_inventory.py input.tsv output.tsv -v --report changes.txt
```

## Input Format

The input TSV file should have these columns:

```
date	title	object_number	link
1/15/2023	the ancient vase	2023.001.A	http://museum.org/vase
2023-02-20	Sculpture by Smith	2023-002	museum.org/sculpture
```

## Features

- **Date Standardization**: Converts multiple date formats to YYYY-MM-DD
- **Title Standardization**: Applies title case with proper handling of articles
- **Object Number Validation**: Normalizes object numbers and validates format
- **URL Validation**: Cleans and validates URLs
- **Duplicate Detection**: Identifies duplicate object numbers
- **Change Logging**: Tracks all modifications made
- **Error Reporting**: Documents all validation errors
- **Detailed Report**: Generates comprehensive standardization report
