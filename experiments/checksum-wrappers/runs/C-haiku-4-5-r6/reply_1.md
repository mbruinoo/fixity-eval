# Museum Inventory Standardization Script

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records from a TSV file.

Handles:
- Date normalization
- Title standardization
- Object number validation
- URL verification
- Duplicate detection
- Correction/withdrawal tracking
"""

import csv
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import Optional, List, Dict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class InventoryRecord:
    """Represents a standardized inventory record."""
    date: str
    title: str
    object_number: str
    link: str
    original_date: str = ""
    is_withdrawn: bool = False
    correction_of: Optional[str] = None
    notes: List[str] = None

    def __post_init__(self):
        if self.notes is None:
            self.notes = []

    def to_dict(self) -> Dict:
        """Convert record to dictionary."""
        return {
            'date': self.date,
            'title': self.title,
            'object_number': self.object_number,
            'link': self.link,
            'is_withdrawn': str(self.is_withdrawn),
            'correction_of': self.correction_of or '',
            'notes': '; '.join(self.notes)
        }


class InventoryStandardizer:
    """Standardizes museum inventory records."""

    def __init__(self, input_file: str, output_file: str, corrections_file: Optional[str] = None):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.corrections_file = Path(corrections_file) if corrections_file else None
        self.records: Dict[str, InventoryRecord] = {}
        self.withdrawn_ids: set = set()
        self.issues: List[str] = []

    def load_corrections(self) -> Dict[str, str]:
        """Load corrections/withdrawals from a secondary file.
        
        Expected format: object_number\taction\tdetails
        Actions: 'withdraw', 'correct_to_number'
        """
        corrections = {}
        if not self.corrections_file or not self.corrections_file.exists():
            return corrections

        try:
            with open(self.corrections_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    obj_num = row.get('object_number', '').strip()
                    action = row.get('action', '').strip().lower()

                    if action == 'withdraw':
                        self.withdrawn_ids.add(obj_num)
                    elif action == 'correct_to_number':
                        corrections[obj_num] = row.get('new_number', '').strip()

            logger.info(f"Loaded {len(self.withdrawn_ids)} withdrawals, "
                       f"{len(corrections)} corrections")
        except Exception as e:
            logger.warning(f"Could not load corrections file: {e}")

        return corrections

    def normalize_date(self, date_str: str) -> tuple[str, str]:
        """Normalize date to ISO 8601 format (YYYY-MM-DD).
        
        Returns:
            Tuple of (normalized_date, original_date)
        """
        if not date_str or not date_str.strip():
            return "", date_str

        original = date_str.strip()
        date_str = original.strip()

        # Try common formats
        formats = [
            '%Y-%m-%d',      # ISO 8601
            '%Y/%m/%d',
            '%m/%d/%Y',      # US format
            '%d/%m/%Y',      # EU format
            '%B %d, %Y',     # January 15, 2020
            '%b %d, %Y',     # Jan 15, 2020
            '%Y',            # Year only
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime('%Y-%m-%d'), original
            except ValueError:
                continue

        # If year-only, keep as YYYY
        if re.match(r'^\d{4}$', date_str):
            return date_str, original

        logger.warning(f"Could not parse date: {original}")
        return "", original

    def validate_object_number(self, obj_num: str) -> tuple[str, List[str]]:
        """Validate and standardize object number.
        
        Returns:
            Tuple of (standardized_number, issues)
        """
        issues = []
        obj_num = obj_num.strip() if obj_num else ""

        if not obj_num:
            issues.append("Missing object number")
            return "", issues

        # Remove leading/trailing whitespace
        obj_num = obj_num.strip()

        # Warn about unusual formats (customize as needed)
        if not re.match(r'^[A-Za-z0-9\-_.]+$', obj_num):
            issues.append(f"Unusual object number format: {obj_num}")

        return obj_num, issues

    def normalize_title(self, title: str) -> str:
        """Normalize title formatting.
        
        - Strip whitespace
        - Normalize quotes
        - Remove control characters
        """
        if not title:
            return ""

        title = title.strip()

        # Normalize quotes
        title = title.replace('"', '"').replace('"', '"')
        title = title.replace("'", "'").replace("'", "'")

        # Remove control characters except newlines
        title = ''.join(char for char in title if ord(char) >= 32 or char == '\n')

        # Normalize whitespace
        title = ' '.join(title.split())

        return title

    def validate_url(self, url: str) -> tuple[str, List[str]]:
        """Validate URL format.
        
        Returns:
            Tuple of (url, issues)
        """
        issues = []
        url = url.strip() if url else ""

        if not url:
            issues.append("Missing URL")
            return "", issues

        # Check for valid URL structure
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                issues.append(f"Invalid URL format: {url}")
                return url, issues

            # Warn about non-HTTPS
            if result.scheme != 'https':
                issues.append(f"Non-HTTPS URL: {url}")

        except Exception as e:
            issues.append(f"URL parsing error: {e}")

        return url, issues

    def standardize_record(self, row: Dict, corrections: Dict) -> Optional[InventoryRecord]:
        """Standardize a single record from input data."""
        all_issues = []

        # Extract fields
        date_str = row.get('date', '').strip()
        title = row.get('title', '').strip()
        object_number = row.get('object_number', '').strip()
        link = row.get('link', '').strip()

        # Validate object number
        object_number, obj_num_issues = self.validate_object_number(object_number)
        all_issues.extend(obj_num_issues)

        if not object_number:
            logger.warning(f"Skipping record with no object number")
            return None

        # Normalize date
        norm_date, orig_date = self.normalize_date(date_str)
        if not norm_date:
            all_issues.append(f"Could not parse date: {orig_date}")

        # Normalize title
        title = self.normalize_title(title)
        if not title:
            all_issues.append("Missing title")

        # Validate URL
        link, url_issues = self.validate_url(link)
        all_issues.extend(url_issues)

        # Check if withdrawn
        is_withdrawn = object_number in self.withdrawn_ids

        # Check if this corrects another record
        correction_of = None
        for old_num, new_num in corrections.items():
            if new_num == object_number:
                correction_of = old_num
                break

        record = InventoryRecord(
            date=norm_date,
            title=title,
            object_number=object_number,
            link=link,
            original_date=orig_date,
            is_withdrawn=is_withdrawn,
            correction_of=correction_of,
            notes=all_issues
        )

        if all_issues:
            self.issues.append(f"{object_number}: {'; '.join(all_issues)}")

        return record

    def detect_duplicates(self) -> List[tuple[str, List[str]]]:
        """Detect duplicate object numbers (excluding withdrawn records).
        
        Returns:
            List of (object_number, list_of_dates)
        """
        duplicates = []
        seen: Dict[str, List[str]] = {}

        for obj_num, record in self.records.items():
            if record.is_withdrawn:
                continue

            if obj_num not in seen:
                seen[obj_num] = []
            seen[obj_num].append(record.date)

        for obj_num, dates in seen.items():
            if len(dates) > 1:
                duplicates.append((obj_num, dates))

        return duplicates

    def process(self) -> bool:
        """Process the inventory file.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.input_file.exists():
            logger.error(f"Input file not found: {self.input_file}")
            return False

        corrections = self.load_corrections()

        try:
            # Read and standardize records
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')

                if not reader.fieldnames or not all(
                    field in reader.fieldnames 
                    for field in ['date', 'title', 'object_number', 'link']
                ):
                    logger.error("TSV missing required columns: date, title, object_number, link")
                    return False

                for row_num, row in enumerate(reader, start=2):  # start=2 for header
                    record = self.standardize_record(row, corrections)
                    if record:
                        self.records[record.object_number] = record

            logger.info(f"Processed {len(self.records)} records")

            # Check for duplicates
            duplicates = self.detect_duplicates()
            if duplicates:
                logger.warning(f"Found {len(duplicates)} duplicate object numbers")
                for obj_num, dates in duplicates[:10]:  # Show first 10
                    logger.warning(f"  {obj_num}: {dates}")

            # Write output
            self.write_output()

            # Report issues
            if self.issues:
                logger.warning(f"Found {len(self.issues)} issues in records")

            return True

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return False

    def write_output(self):
        """Write standardized records to output TSV."""
        try:
            # Sort records by object number
            sorted_records = sorted(
                self.records.values(),
                key=lambda r: r.object_number
            )

            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['date', 'title', 'object_number', 'link', 
                             'is_withdrawn', 'correction_of', 'notes']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')

                writer.writeheader()
                for record in sorted_records:
                    writer.writerow(record.to_dict())

            logger.info(f"Wrote {len(sorted_records)} records to {self.output_file}")

        except Exception as e:
            logger.error(f"Error writing output: {e}")
            raise

    def write_issues_report(self, report_file: str):
        """Write validation issues to a report file."""
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("STANDARDIZATION REPORT\n")
                f.write("=" * 80 + "\n\n")

                f.write(f"Total records processed: {len(self.records)}\n")
                f.write(f"Withdrawn records: {sum(1 for r in self.records.values() if r.is_withdrawn)}\n")
                f.write(f"Issues found: {len(self.issues)}\n\n")

                if self.issues:
                    f.write("ISSUES:\n")
                    f.write("-" * 80 + "\n")
                    for issue in sorted(self.issues)[:100]:  # First 100
                        f.write(f"{issue}\n")

                duplicates = self.detect_duplicates()
                if duplicates:
                    f.write("\n\nDUPLICATE OBJECT NUMBERS:\n")
                    f.write("-" * 80 + "\n")
                    for obj_num, dates in duplicates:
                        f.write(f"{obj_num}: {', '.join(dates)}\n")

            logger.info(f"Wrote report to {report_file}")

        except Exception as e:
            logger.error(f"Error writing report: {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records'
    )
    parser.add_argument('input', help='Input TSV file')
    parser.add_argument('output', help='Output TSV file')
    parser.add_argument(
        '--corrections',
        help='TSV file with corrections/withdrawals'
    )
    parser.add_argument(
        '--report',
        help='Write validation report to this file'
    )

    args = parser.parse_args()

    standardizer = InventoryStandardizer(
        args.input,
        args.output,
        args.corrections
    )

    if standardizer.process():
        if args.report:
            standardizer.write_issues_report(args.report)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## Usage

```bash
# Basic usage
python standardize_inventory.py input.tsv output.tsv

# With corrections file
python standardize_inventory.py input.tsv output.tsv --corrections corrections.tsv

# With validation report
python standardize_inventory.py input.tsv output.tsv --report report.txt
```

## Input Format

**input.tsv:**
```
date	title	object_number	link
2020-01-15	Ancient Vase	OBJ-001	https://museum.org/obj/001
1/15/2020	Medieval Sword	OBJ-002	https://museum.org/obj/002
```

## Corrections Format

**corrections.tsv:**
```
object_number	action	new_number
OBJ-003	withdraw	
OBJ-001	correct_to_number	OBJ-001-A
```

## Features

- **Date normalization** to ISO 8601
- **Title standardization** (whitespace, quotes)
- **URL validation** (HTTPS check)
- **Duplicate detection**
- **Withdrawal tracking**
- **Correction tracking** (when records are corrected to new IDs)
- **Validation report** generation
- **Comprehensive logging**
