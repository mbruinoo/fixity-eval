# Museum Inventory Standardizer

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records from a TSV file.

Handles data validation, deduplication, and tracks corrections/withdrawals.
"""

import csv
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class RecordStatus(Enum):
    """Status of an inventory record."""
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"
    CORRECTED = "corrected"


@dataclass
class MuseumRecord:
    """Standardized museum inventory record."""
    object_number: str
    title: str
    date: str
    link: str
    status: RecordStatus = RecordStatus.ACTIVE
    created_date: str = ""
    corrected_to: Optional[str] = None  # object_number if corrected
    withdrawal_reason: Optional[str] = None
    notes: str = ""

    def __hash__(self):
        return hash(self.object_number)

    def __eq__(self, other):
        if not isinstance(other, MuseumRecord):
            return False
        return self.object_number == other.object_number


class InventoryStandardizer:
    """Standardize and manage museum inventory records."""

    # Validation patterns
    OBJECT_NUMBER_PATTERN = re.compile(r'^[A-Z0-9]{3,20}$')
    URL_PATTERN = re.compile(r'^https?://.+')
    YEAR_PATTERN = re.compile(r'^\d{4}$')

    def __init__(self, input_file: Path, output_dir: Path = None):
        """
        Initialize the standardizer.

        Args:
            input_file: Path to input TSV file
            output_dir: Directory for output files (default: same as input)
        """
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir) if output_dir else self.input_file.parent
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.records: Dict[str, MuseumRecord] = {}
        self.validation_errors: List[Dict] = []
        self.corrections_log: List[Dict] = []

    def validate_object_number(self, obj_num: str) -> Tuple[bool, str]:
        """Validate object number format."""
        if not obj_num or not obj_num.strip():
            return False, "Object number is empty"

        obj_num = obj_num.strip().upper()

        if not self.OBJECT_NUMBER_PATTERN.match(obj_num):
            return (
                False,
                f"Invalid format: {obj_num}. Must be 3-20 alphanumeric characters."
            )
        return True, obj_num

    def validate_title(self, title: str) -> Tuple[bool, str]:
        """Validate and normalize title."""
        if not title or not title.strip():
            return False, "Title is empty"

        # Normalize whitespace
        title = ' '.join(title.strip().split())

        # Check minimum length
        if len(title) < 2:
            return False, "Title too short"

        return True, title

    def validate_date(self, date_str: str) -> Tuple[bool, str]:
        """Validate date field (flexible format)."""
        if not date_str or not date_str.strip():
            return False, "Date is empty"

        date_str = date_str.strip()

        # Accept YYYY, YYYY-MM-DD, or descriptive dates
        if self.YEAR_PATTERN.match(date_str):
            return True, date_str

        # Try ISO format
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True, date_str
        except ValueError:
            pass

        # Accept any non-empty date (e.g., "circa 1850", "19th century")
        if len(date_str) >= 3:
            return True, date_str

        return False, f"Invalid date format: {date_str}"

    def validate_link(self, link: str) -> Tuple[bool, str]:
        """Validate link format."""
        if not link or not link.strip():
            return True, ""  # Links are optional

        link = link.strip()

        if not self.URL_PATTERN.match(link):
            return False, f"Invalid URL format: {link}"

        return True, link

    def validate_record(self, row: Dict, row_num: int) -> Optional[MuseumRecord]:
        """
        Validate a single record row.

        Returns:
            MuseumRecord if valid, None otherwise
        """
        errors = []

        # Validate object number (required)
        valid, obj_num = self.validate_object_number(row.get('object_number', ''))
        if not valid:
            errors.append(f"Object number: {obj_num}")
        else:
            object_number = obj_num

        # Validate title (required)
        valid, title = self.validate_title(row.get('title', ''))
        if not valid:
            errors.append(f"Title: {title}")
        else:
            title = title

        # Validate date (required)
        valid, date = self.validate_date(row.get('date', ''))
        if not valid:
            errors.append(f"Date: {date}")
        else:
            date = date

        # Validate link (optional)
        valid, link = self.validate_link(row.get('link', ''))
        if not valid:
            errors.append(f"Link: {link}")
        else:
            link = link

        if errors:
            self.validation_errors.append({
                'row': row_num,
                'object_number': row.get('object_number', 'N/A'),
                'errors': errors
            })
            return None

        return MuseumRecord(
            object_number=object_number,
            title=title,
            date=date,
            link=link,
            created_date=datetime.now().isoformat()
        )

    def load_records(self) -> None:
        """Load and validate records from TSV file."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")

        print(f"Loading records from {self.input_file}...")

        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')

                if not reader.fieldnames:
                    raise ValueError("Empty TSV file")

                required_fields = {'object_number', 'title', 'date', 'link'}
                if not required_fields.issubset(set(reader.fieldnames or [])):
                    raise ValueError(
                        f"Missing required fields. Expected: {required_fields}"
                    )

                for row_num, row in enumerate(reader, start=2):  # +1 for header
                    record = self.validate_record(row, row_num)
                    if record:
                        self.records[record.object_number] = record

        except csv.Error as e:
            raise ValueError(f"TSV parsing error: {e}")

        print(f"Loaded {len(self.records)} valid records")
        if self.validation_errors:
            print(f"⚠ {len(self.validation_errors)} validation errors")

    def mark_withdrawn(self, object_number: str, reason: str = "") -> bool:
        """Mark a record as withdrawn."""
        valid, obj_num = self.validate_object_number(object_number)
        if not valid:
            print(f"Invalid object number: {object_number}")
            return False

        if obj_num not in self.records:
            print(f"Object not found: {obj_num}")
            return False

        self.records[obj_num].status = RecordStatus.WITHDRAWN
        self.records[obj_num].withdrawal_reason = reason
        self.corrections_log.append({
            'action': 'withdrawn',
            'object_number': obj_num,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        return True

    def correct_record(
        self,
        old_object_number: str,
        new_object_number: str,
        updated_fields: Dict = None
    ) -> bool:
        """
        Correct a record by creating a new one and marking old as corrected.

        Args:
            old_object_number: Current object number
            new_object_number: Corrected object number
            updated_fields: Dict of fields to update (title, date, link)
        """
        valid, old_num = self.validate_object_number(old_object_number)
        if not valid:
            print(f"Invalid old object number: {old_object_number}")
            return False

        valid, new_num = self.validate_object_number(new_object_number)
        if not valid:
            print(f"Invalid new object number: {new_object_number}")
            return False

        if old_num not in self.records:
            print(f"Record not found: {old_num}")
            return False

        old_record = self.records[old_num]

        # Create corrected record
        corrected_record = MuseumRecord(
            object_number=new_num,
            title=updated_fields.get('title', old_record.title) if updated_fields else old_record.title,
            date=updated_fields.get('date', old_record.date) if updated_fields else old_record.date,
            link=updated_fields.get('link', old_record.link) if updated_fields else old_record.link,
            created_date=old_record.created_date
        )

        # Mark old record as corrected
        old_record.status = RecordStatus.CORRECTED
        old_record.corrected_to = new_num

        # Add corrected record
        self.records[new_num] = corrected_record

        self.corrections_log.append({
            'action': 'corrected',
            'old_object_number': old_num,
            'new_object_number': new_num,
            'changes': updated_fields or {},
            'timestamp': datetime.now().isoformat()
        })

        return True

    def get_active_records(self) -> List[MuseumRecord]:
        """Get all active (non-withdrawn, non-corrected) records."""
        return [
            r for r in self.records.values()
            if r.status == RecordStatus.ACTIVE
        ]

    def get_statistics(self) -> Dict:
        """Get inventory statistics."""
        records = self.records.values()
        return {
            'total_records': len(records),
            'active_records': len(self.get_active_records()),
            'withdrawn_records': len([r for r in records if r.status == RecordStatus.WITHDRAWN]),
            'corrected_records': len([r for r in records if r.status == RecordStatus.CORRECTED]),
            'validation_errors': len(self.validation_errors),
            'corrections_made': len(self.corrections_log)
        }

    def save_standardized_records(self, filename: str = "standardized_inventory.tsv") -> Path:
        """Save standardized active records to TSV."""
        output_path = self.output_dir / filename
        active_records = self.get_active_records()

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['object_number', 'title', 'date', 'link', 'created_date', 'notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')

            writer.writeheader()
            for record in sorted(active_records, key=lambda r: r.object_number):
                writer.writerow(asdict(record))

        print(f"Saved {len(active_records)} active records to {output_path}")
        return output_path

    def save_validation_report(self, filename: str = "validation_report.txt") -> Path:
        """Save validation errors report."""
        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("MUSEUM INVENTORY VALIDATION REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Input file: {self.input_file}\n\n")

            stats = self.get_statistics()
            f.write("STATISTICS\n")
            f.write("-" * 50 + "\n")
            for key, value in stats.items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")

            f.write("\n\nVALIDATION ERRORS\n")
            f.write("-" * 50 + "\n")
            if self.validation_errors:
                for error in self.validation_errors:
                    f.write(f"\nRow {error['row']}: {error['object_number']}\n")
                    for err_msg in error['errors']:
                        f.write(f"  • {err_msg}\n")
            else:
                f.write("No validation errors.\n")

        print(f"Saved validation report to {output_path}")
        return output_path

    def save_corrections_log(self, filename: str = "corrections_log.tsv") -> Path:
        """Save corrections and withdrawals log."""
        output_path = self.output_dir / filename

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if self.corrections_log:
                fieldnames = self.corrections_log[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(self.corrections_log)
            else:
                f.write("No corrections or withdrawals recorded.\n")

        print(f"Saved corrections log to {output_path}")
        return output_path

    def print_summary(self) -> None:
        """Print summary to console."""
        stats = self.get_statistics()

        print("\n" + "=" * 50)
        print("STANDARDIZATION SUMMARY")
        print("=" * 50)
        for key, value in stats.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print("=" * 50 + "\n")


def main():
    """Example usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Standardize museum inventory records"
    )
    parser.add_argument('input_file', type=Path, help='Input TSV file')
    parser.add_argument(
        '-o', '--output-dir',
        type=Path,
        help='Output directory (default: same as input)'
    )
    parser.add_argument(
        '-w', '--withdraw',
        nargs=2,
        metavar=('OBJECT_NUMBER', 'REASON'),
        help='Mark a record as withdrawn'
    )
    parser.add_argument(
        '-c', '--correct',
        nargs=3,
        metavar=('OLD_NUMBER', 'NEW_NUMBER', 'UPDATES'),
        help='Correct a record (UPDATES as JSON dict or empty string)'
    )

    args = parser.parse_args()

    try:
        standardizer = InventoryStandardizer(args.input_file, args.output_dir)
        standardizer.load_records()

        if args.withdraw:
            standardizer.mark_withdrawn(args.withdraw[0], args.withdraw[1])

        if args.correct:
            updates = {}
            if args.correct[2] != '{}':
                import json
                try:
                    updates = json.loads(args.correct[2])
                except json.JSONDecodeError:
                    print("Warning: Could not parse updates JSON, using defaults")
            standardizer.correct_record(args.correct[0], args.correct[1], updates)

        standardizer.save_standardized_records()
        standardizer.save_validation_report()
        standardizer.save_corrections_log()
        standardizer.print_summary()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## Usage Examples

### Basic standardization:
```bash
python museum_inventory.py inventory.tsv
```

### With custom output directory:
```bash
python museum_inventory.py inventory.tsv -o ./output
```

### Withdraw a record:
```bash
python museum_inventory.py inventory.tsv -w "ARTIFACT001" "Duplicate entry"
```

### Correct a record:
```bash
python museum_inventory.py inventory.tsv -c "ARTIFACT001" "ARTIFACT002" '{"title": "New Title"}'
```

### Programmatic usage:
```python
from pathlib import Path

standardizer = InventoryStandardizer(Path('inventory.tsv'))
standardizer.load_records()

# Withdraw a record
standardizer.mark_withdrawn('ARTIFACT001', 'Found to be misidentified')

# Correct a record
standardizer.correct_record(
    'ARTIFACT001',
    'ARTIFACT002',
    {'title': 'Corrected Title', 'date': '1920'}
)

standardizer.save_standardized_records()
standardizer.save_validation_report()
standardizer.print_summary()
```

This script provides:
- ✅ TSV file parsing with validation
- ✅ Standardized data format
- ✅ Duplicate/correction tracking
- ✅ Withdrawal management
- ✅ Comprehensive reporting
- ✅ Command-line and programmatic interfaces
