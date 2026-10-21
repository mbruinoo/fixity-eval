# Museum Inventory Standardization Script

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records from a TSV file.

Handles corrections, withdrawals, and validation of object records.
"""

import argparse
import csv
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class InventoryRecord:
    """Represents a single museum inventory record."""
    
    date: str
    title: str
    object_number: str
    link: str
    withdrawn: bool = False
    correction_note: Optional[str] = None
    
    def validate(self) -> list[str]:
        """
        Validate record fields.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate date format (ISO 8601)
        try:
            datetime.fromisoformat(self.date)
        except ValueError:
            errors.append(f"Invalid date format: {self.date}")
        
        # Validate required fields
        if not self.title or not self.title.strip():
            errors.append("Title cannot be empty")
        
        if not self.object_number or not self.object_number.strip():
            errors.append("Object number cannot be empty")
        
        # Validate object number format (basic check)
        if self.object_number and not self._is_valid_object_number():
            errors.append(f"Invalid object number format: {self.object_number}")
        
        # Validate link format
        if not self.link or not self.link.strip():
            errors.append("Link cannot be empty")
        elif not self._is_valid_url():
            errors.append(f"Invalid URL format: {self.link}")
        
        return errors
    
    def _is_valid_object_number(self) -> bool:
        """Check if object number matches expected format."""
        # Adjust pattern based on your museum's numbering scheme
        # Example: "2024.001.001"
        parts = self.object_number.strip().split('.')
        if len(parts) < 2:
            return False
        # Check that year part is numeric
        if not parts[0].isdigit() or len(parts[0]) != 4:
            return False
        return True
    
    def _is_valid_url(self) -> bool:
        """Basic URL validation."""
        url = self.link.strip()
        return url.startswith(('http://', 'https://', 'file://'))
    
    def normalize(self) -> 'InventoryRecord':
        """
        Normalize record fields.
        
        Returns:
            Normalized copy of the record
        """
        return InventoryRecord(
            date=self.date.strip(),
            title=self.title.strip(),
            object_number=self.object_number.strip(),
            link=self.link.strip(),
            withdrawn=self.withdrawn,
            correction_note=self.correction_note.strip() if self.correction_note else None
        )
    
    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            'date': self.date,
            'title': self.title,
            'object_number': self.object_number,
            'link': self.link,
            'withdrawn': self.withdrawn,
            'correction_note': self.correction_note or ''
        }


class InventoryProcessor:
    """Process and standardize museum inventory records."""
    
    def __init__(self, input_file: Path):
        self.input_file = input_file
        self.records: dict[str, InventoryRecord] = {}
        self.corrections_log: list[dict] = []
        self.validation_errors: list[tuple[int, str, list[str]]] = []
    
    def read_inventory(self) -> bool:
        """
        Read inventory from TSV file.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.input_file.exists():
            logger.error(f"File not found: {self.input_file}")
            return False
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    logger.error("TSV file is empty or malformed")
                    return False
                
                required_fields = {'date', 'title', 'object_number', 'link'}
                missing_fields = required_fields - set(reader.fieldnames or [])
                
                if missing_fields:
                    logger.error(f"Missing required columns: {missing_fields}")
                    return False
                
                for line_num, row in enumerate(reader, start=2):  # start=2 (header is 1)
                    try:
                        record = InventoryRecord(
                            date=row['date'],
                            title=row['title'],
                            object_number=row['object_number'],
                            link=row['link'],
                            withdrawn=row.get('withdrawn', 'False').lower() == 'true',
                            correction_note=row.get('correction_note')
                        )
                        
                        # Store by object number (latest entry wins)
                        self.records[record.object_number] = (line_num, record)
                    
                    except KeyError as e:
                        logger.warning(f"Line {line_num}: Missing field {e}")
            
            logger.info(f"Loaded {len(self.records)} records")
            return True
        
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return False
    
    def apply_corrections(self, corrections_file: Path) -> bool:
        """
        Apply corrections from a separate corrections file.
        
        Expected format: object_number, corrected_field, new_value, reason
        
        Returns:
            True if successful
        """
        if not corrections_file.exists():
            logger.warning(f"Corrections file not found: {corrections_file}")
            return True
        
        try:
            with open(corrections_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                for row in reader:
                    object_num = row.get('object_number')
                    field = row.get('field')
                    new_value = row.get('new_value')
                    reason = row.get('reason', '')
                    
                    if object_num not in self.records:
                        logger.warning(f"Correction for unknown object: {object_num}")
                        continue
                    
                    _, record = self.records[object_num]
                    old_value = getattr(record, field, None)
                    
                    if field == 'withdrawn':
                        record.withdrawn = new_value.lower() == 'true'
                    elif hasattr(record, field):
                        setattr(record, field, new_value)
                        record.correction_note = reason
                    else:
                        logger.warning(f"Unknown field for correction: {field}")
                        continue
                    
                    self.corrections_log.append({
                        'object_number': object_num,
                        'field': field,
                        'old_value': old_value,
                        'new_value': new_value,
                        'reason': reason,
                        'date_applied': datetime.now().isoformat()
                    })
                    logger.info(f"Applied correction to {object_num}: {field}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error reading corrections file: {e}")
            return False
    
    def validate_all(self) -> bool:
        """
        Validate all records.
        
        Returns:
            True if all records are valid
        """
        for object_num, (line_num, record) in self.records.items():
            errors = record.validate()
            if errors:
                self.validation_errors.append((line_num, object_num, errors))
        
        if self.validation_errors:
            logger.warning(f"Found {len(self.validation_errors)} records with validation errors")
            return False
        
        logger.info("All records passed validation")
        return True
    
    def normalize_all(self):
        """Normalize all records in place."""
        for object_num in self.records:
            line_num, record = self.records[object_num]
            normalized = record.normalize()
            self.records[object_num] = (line_num, normalized)
        logger.info("Normalized all records")
    
    def write_output(self, output_file: Path, include_withdrawn: bool = False):
        """
        Write standardized inventory to TSV file.
        
        Args:
            output_file: Path to output file
            include_withdrawn: Whether to include withdrawn records
        """
        try:
            # Filter records
            records_to_write = [
                record for _, record in self.records.values()
                if include_withdrawn or not record.withdrawn
            ]
            
            # Sort by date and object number
            records_to_write.sort(
                key=lambda r: (r.date, r.object_number)
            )
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['date', 'title', 'object_number', 'link', 
                            'withdrawn', 'correction_note']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                
                writer.writeheader()
                for record in records_to_write:
                    writer.writerow(record.to_dict())
            
            logger.info(f"Wrote {len(records_to_write)} records to {output_file}")
        
        except Exception as e:
            logger.error(f"Error writing output: {e}")
    
    def write_validation_report(self, report_file: Path):
        """Write validation errors to a report file."""
        if not self.validation_errors:
            logger.info("No validation errors to report")
            return
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("VALIDATION ERROR REPORT\n")
                f.write("=" * 80 + "\n\n")
                
                for line_num, object_num, errors in self.validation_errors:
                    f.write(f"Line {line_num}: {object_num}\n")
                    for error in errors:
                        f.write(f"  - {error}\n")
                    f.write("\n")
            
            logger.info(f"Validation report written to {report_file}")
        
        except Exception as e:
            logger.error(f"Error writing validation report: {e}")
    
    def write_corrections_log(self, log_file: Path):
        """Write corrections log."""
        if not self.corrections_log:
            return
        
        try:
            with open(log_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['object_number', 'field', 'old_value', 
                            'new_value', 'reason', 'date_applied']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                
                writer.writeheader()
                writer.writerows(self.corrections_log)
            
            logger.info(f"Corrections log written to {log_file}")
        
        except Exception as e:
            logger.error(f"Error writing corrections log: {e}")
    
    def generate_summary(self) -> dict:
        """Generate summary statistics."""
        total = len(self.records)
        withdrawn = sum(1 for _, r in self.records.values() if r.withdrawn)
        active = total - withdrawn
        corrected = len(self.corrections_log)
        
        return {
            'total_records': total,
            'active_records': active,
            'withdrawn_records': withdrawn,
            'corrections_applied': corrected,
            'validation_errors': len(self.validation_errors)
        }


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records'
    )
    parser.add_argument(
        'input_file',
        type=Path,
        help='Input TSV file with inventory records'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=None,
        help='Output file (default: standardized_inventory.tsv)'
    )
    parser.add_argument(
        '-c', '--corrections',
        type=Path,
        help='TSV file with corrections to apply'
    )
    parser.add_argument(
        '--include-withdrawn',
        action='store_true',
        help='Include withdrawn records in output'
    )
    parser.add_argument(
        '--validation-report',
        type=Path,
        help='Write validation errors to this file'
    )
    parser.add_argument(
        '--corrections-log',
        type=Path,
        help='Write corrections log to this file'
    )
    
    args = parser.parse_args()
    
    # Set default output file
    if args.output is None:
        args.output = args.input_file.parent / 'standardized_inventory.tsv'
    
    # Process inventory
    processor = InventoryProcessor(args.input_file)
    
    if not processor.read_inventory():
        sys.exit(1)
    
    if args.corrections:
        processor.apply_corrections(args.corrections)
    
    processor.normalize_all()
    
    is_valid = processor.validate_all()
    
    processor.write_output(args.output, include_withdrawn=args.include_withdrawn)
    
    if args.validation_report:
        processor.write_validation_report(args.validation_report)
    
    if args.corrections_log:
        processor.write_corrections_log(args.corrections_log)
    
    # Print summary
    summary = processor.generate_summary()
    print("\n" + "=" * 50)
    print("STANDARDIZATION SUMMARY")
    print("=" * 50)
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print("=" * 50)
    
    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()
```

## Usage Examples

**Basic usage:**
```bash
python standardize_inventory.py inventory.tsv
```

**With corrections and reports:**
```bash
python standardize_inventory.py inventory.tsv \
    -c corrections.tsv \
    -o standardized.tsv \
    --validation-report errors.txt \
    --corrections-log changes.tsv
```

**Include withdrawn records:**
```bash
python standardize_inventory.py inventory.tsv --include-withdrawn
```

## Input File Format

**inventory.tsv:**
```
date	title	object_number	link	withdrawn	correction_note
2024-01-15	Egyptian Vase	2024.001.001	https://museum.org/2024.001.001	False	
2024-01-16	Roman Coin	2024.001.002	https://museum.org/2024.001.002	False	
2024-01-17	Medieval Sword	2024.001.003	https://museum.org/2024.001.003	True	Deaccessioned
```

**corrections.tsv:**
```
object_number	field	new_value	reason
2024.001.001	title	Egyptian Alabaster Vase	Corrected classification
2024.001.002	withdrawn	True	Lost in inventory
```

## Features

- ✅ Validates dates, URLs, and object numbers
- ✅ Handles corrections from a separate file
- ✅ Tracks withdrawn records
- ✅ Normalizes whitespace
- ✅ Generates validation reports
- ✅ Maintains corrections audit log
- ✅ Sorts output by date and object number
- ✅ Summary statistics
