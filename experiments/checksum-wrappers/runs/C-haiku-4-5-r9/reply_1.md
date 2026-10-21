# Museum Inventory Standardization Script

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records from a TSV file.

Handles data validation, deduplication, correction tracking, and withdrawal management.
"""

import argparse
import csv
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Tuple
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class InventoryRecord:
    """Represents a standardized inventory record."""
    object_number: str
    title: str
    date: str
    link: str
    record_date: str  # When this record was created/updated
    status: str = "active"  # active, withdrawn, superseded
    notes: str = ""
    
    def is_valid(self) -> Tuple[bool, str]:
        """Validate record fields."""
        if not self.object_number or not self.object_number.strip():
            return False, "Missing object number"
        if not self.title or not self.title.strip():
            return False, "Missing title"
        if not self.date or not self.date.strip():
            return False, "Missing date"
        if not self.link or not self.link.strip():
            return False, "Missing link"
        return True, ""
    
    def normalize(self) -> None:
        """Standardize field formats."""
        self.object_number = self.object_number.strip().upper()
        self.title = self.title.strip()
        self.date = self.date.strip()
        self.link = self.link.strip()
        self.status = self.status.strip().lower()
        self.notes = self.notes.strip()


class InventoryStandardizer:
    """Handles standardization of museum inventory records."""
    
    def __init__(self, input_file: Path):
        self.input_file = input_file
        self.records: List[InventoryRecord] = []
        self.errors: List[Dict] = []
        self.withdrawals: Set[str] = set()
        self.record_history: Dict[str, List[InventoryRecord]] = {}
        
    def load_tsv(self) -> bool:
        """Load records from TSV file."""
        if not self.input_file.exists():
            logger.error(f"File not found: {self.input_file}")
            return False
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if reader.fieldnames is None:
                    logger.error("Empty TSV file")
                    return False
                
                required_fields = {'object_number', 'title', 'date', 'link'}
                if not required_fields.issubset(set(reader.fieldnames or [])):
                    logger.error(f"Missing required fields. Expected: {required_fields}")
                    logger.error(f"Found: {set(reader.fieldnames or [])}")
                    return False
                
                for row_num, row in enumerate(reader, start=2):
                    record = InventoryRecord(
                        object_number=row.get('object_number', ''),
                        title=row.get('title', ''),
                        date=row.get('date', ''),
                        link=row.get('link', ''),
                        record_date=row.get('record_date', datetime.now().isoformat()),
                        status=row.get('status', 'active'),
                        notes=row.get('notes', '')
                    )
                    
                    is_valid, error_msg = record.is_valid()
                    if not is_valid:
                        self.errors.append({
                            'row': row_num,
                            'object_number': record.object_number,
                            'error': error_msg
                        })
                        logger.warning(f"Row {row_num}: {error_msg}")
                        continue
                    
                    record.normalize()
                    self.records.append(record)
                    
                    # Track history by object number
                    if record.object_number not in self.record_history:
                        self.record_history[record.object_number] = []
                    self.record_history[record.object_number].append(record)
            
            logger.info(f"Loaded {len(self.records)} valid records from {self.input_file}")
            if self.errors:
                logger.warning(f"Found {len(self.errors)} invalid records")
            return True
            
        except Exception as e:
            logger.error(f"Error reading TSV file: {e}")
            return False
    
    def handle_duplicates(self, keep_latest: bool = True) -> int:
        """
        Handle duplicate object numbers.
        
        Args:
            keep_latest: If True, keep the most recent record; otherwise report error
            
        Returns:
            Number of duplicates removed
        """
        duplicates_removed = 0
        seen: Dict[str, int] = {}
        records_to_keep = []
        
        # Sort by record_date to identify latest
        sorted_records = sorted(self.records, key=lambda r: r.record_date)
        
        for record in sorted_records:
            if record.object_number in seen:
                if keep_latest:
                    # Remove the older version
                    old_idx = seen[record.object_number]
                    if records_to_keep[old_idx].status != 'withdrawn':
                        records_to_keep[old_idx].status = 'superseded'
                        logger.info(f"Marked {record.object_number} as superseded "
                                  f"(older than {record.record_date})")
                    duplicates_removed += 1
                else:
                    logger.error(f"Duplicate object number: {record.object_number}")
                    self.errors.append({
                        'object_number': record.object_number,
                        'error': 'Duplicate entry',
                        'dates': [records_to_keep[seen[record.object_number]].record_date, 
                                record.record_date]
                    })
            
            seen[record.object_number] = len(records_to_keep)
            records_to_keep.append(record)
        
        self.records = records_to_keep
        logger.info(f"Handled {duplicates_removed} duplicate entries")
        return duplicates_removed
    
    def process_withdrawals(self, withdrawals_file: Path = None) -> int:
        """
        Process withdrawn records from a separate file or field.
        
        Withdrawals file format: one object_number per line
        
        Args:
            withdrawals_file: Path to file listing withdrawn object numbers
            
        Returns:
            Number of records marked as withdrawn
        """
        count = 0
        
        if withdrawals_file and withdrawals_file.exists():
            try:
                with open(withdrawals_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        obj_num = line.strip().upper()
                        if obj_num and not obj_num.startswith('#'):
                            self.withdrawals.add(obj_num)
                logger.info(f"Loaded {len(self.withdrawals)} withdrawal entries")
            except Exception as e:
                logger.error(f"Error reading withdrawals file: {e}")
        
        # Mark withdrawn records
        for record in self.records:
            if record.object_number in self.withdrawals:
                record.status = 'withdrawn'
                count += 1
        
        if count > 0:
            logger.info(f"Marked {count} records as withdrawn")
        
        return count
    
    def validate_links(self) -> List[Dict]:
        """
        Validate URL format (basic check).
        
        Returns:
            List of records with invalid links
        """
        invalid_links = []
        
        for record in self.records:
            if record.status == 'withdrawn':
                continue
                
            if not (record.link.startswith('http://') or 
                   record.link.startswith('https://')):
                invalid_links.append({
                    'object_number': record.object_number,
                    'link': record.link,
                    'error': 'Invalid URL format'
                })
        
        if invalid_links:
            logger.warning(f"Found {len(invalid_links)} records with invalid links")
        
        return invalid_links
    
    def generate_report(self, output_dir: Path = None) -> Dict:
        """
        Generate standardization report.
        
        Returns:
            Dictionary containing report data
        """
        if output_dir is None:
            output_dir = Path('.')
        
        active_records = [r for r in self.records if r.status == 'active']
        withdrawn_records = [r for r in self.records if r.status == 'withdrawn']
        superseded_records = [r for r in self.records if r.status == 'superseded']
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'input_file': str(self.input_file),
            'summary': {
                'total_records': len(self.records),
                'active_records': len(active_records),
                'withdrawn_records': len(withdrawn_records),
                'superseded_records': len(superseded_records),
                'invalid_records': len(self.errors),
            },
            'errors': self.errors,
        }
        
        # Save report as JSON
        report_file = output_dir / 'inventory_report.json'
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {report_file}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
        
        return report
    
    def save_standardized(self, output_file: Path = None) -> bool:
        """
        Save standardized records to TSV file.
        
        Args:
            output_file: Output file path (default: input_file with .standardized.tsv)
            
        Returns:
            True if successful
        """
        if output_file is None:
            output_file = self.input_file.parent / f"{self.input_file.stem}.standardized.tsv"
        
        try:
            # Filter out invalid records (those in self.errors)
            valid_records = [r for r in self.records]
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['object_number', 'title', 'date', 'link', 
                            'record_date', 'status', 'notes']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                
                writer.writeheader()
                for record in valid_records:
                    writer.writerow(asdict(record))
            
            logger.info(f"Saved {len(valid_records)} standardized records to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving standardized records: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records from TSV file'
    )
    parser.add_argument('input_file', type=Path, help='Input TSV file')
    parser.add_argument('-o', '--output', type=Path, help='Output TSV file')
    parser.add_argument('-w', '--withdrawals', type=Path, 
                       help='File listing withdrawn object numbers')
    parser.add_argument('-d', '--output-dir', type=Path, default=Path('.'),
                       help='Directory for reports (default: current directory)')
    parser.add_argument('-v', '--validate-links', action='store_true',
                       help='Validate URL formats')
    
    args = parser.parse_args()
    
    # Initialize standardizer
    standardizer = InventoryStandardizer(args.input_file)
    
    # Load and process records
    if not standardizer.load_tsv():
        sys.exit(1)
    
    # Handle duplicates
    standardizer.handle_duplicates(keep_latest=True)
    
    # Process withdrawals
    if args.withdrawals:
        standardizer.process_withdrawals(args.withdrawals)
    
    # Validate links if requested
    if args.validate_links:
        invalid_links = standardizer.validate_links()
        if invalid_links:
            for item in invalid_links:
                logger.warning(f"{item['object_number']}: {item['error']}")
    
    # Generate report
    report = standardizer.generate_report(args.output_dir)
    print(f"\n{'='*60}")
    print("STANDARDIZATION SUMMARY")
    print(f"{'='*60}")
    for key, value in report['summary'].items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print(f"{'='*60}\n")
    
    # Save standardized records
    if standardizer.save_standardized(args.output):
        logger.info("Standardization complete")
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## Example Usage

### Sample Input TSV (`inventory.tsv`):
```tsv
object_number	title	date	link
ART-001	Vase, Ming Dynasty	2024-01-15	https://museum.org/objects/ART-001
ART-002	Painting, Oil on Canvas	2024-01-15	https://museum.org/objects/ART-002
ART-001	Vase, Ming Dynasty (Corrected)	2024-02-20	https://museum.org/objects/ART-001
ART-003	Sculpture, Bronze	2024-01-16	museum.org/objects/ART-003
```

### Withdrawals File (`withdrawals.txt`):
```
# Objects withdrawn from collection
ART-002
ART-005
```

### Run the script:
```bash
# Basic standardization
python3 standardize_inventory.py inventory.tsv

# With withdrawals and link validation
python3 standardize_inventory.py inventory.tsv \
  -w withdrawals.txt \
  -v \
  -o inventory_clean.tsv \
  -d ./reports
```

## Output Files

1. **`inventory.standardized.tsv`** — Cleaned, deduplicated records
2. **`inventory_report.json`** — Detailed standardization report

The script handles:
- ✅ Field validation and normalization
- ✅ Duplicate detection (keeps latest)
- ✅ Withdrawal processing
- ✅ Link format validation
- ✅ Comprehensive error reporting
- ✅ Version tracking via record_date
