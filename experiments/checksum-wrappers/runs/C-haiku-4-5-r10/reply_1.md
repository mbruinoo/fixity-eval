# Museum Inventory Record Standardizer

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records from a TSV file.

Handles deduplication, corrections, withdrawals, and format normalization.
"""

import csv
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse


@dataclass
class InventoryRecord:
    """Represents a single museum object record."""
    date: str
    title: str
    object_number: str
    link: str
    
    def __post_init__(self):
        """Validate and normalize fields after initialization."""
        self.date = self._normalize_date(self.date)
        self.title = self._normalize_title(self.title)
        self.object_number = self._normalize_object_number(self.object_number)
        self.link = self._normalize_link(self.link)
    
    @staticmethod
    def _normalize_date(date_str: str) -> str:
        """Convert date to ISO 8601 format (YYYY-MM-DD)."""
        date_str = date_str.strip()
        if not date_str:
            return ""
        
        # Try common formats
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%B %d, %Y",
            "%b %d, %Y",
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # If no format matches, return original with warning
        print(f"Warning: Could not parse date '{date_str}'", file=sys.stderr)
        return date_str
    
    @staticmethod
    def _normalize_title(title: str) -> str:
        """Normalize title formatting."""
        title = title.strip()
        # Remove extra whitespace
        title = " ".join(title.split())
        # Remove trailing punctuation if present
        title = title.rstrip(".,;:")
        return title
    
    @staticmethod
    def _normalize_object_number(obj_num: str) -> str:
        """Normalize object number (usually uppercase, no extra spaces)."""
        obj_num = obj_num.strip().upper()
        # Remove extra internal whitespace
        obj_num = "-".join(part.strip() for part in obj_num.split("-"))
        return obj_num
    
    @staticmethod
    def _normalize_link(link: str) -> str:
        """Validate and normalize URL."""
        link = link.strip()
        if not link:
            return ""
        
        # Add scheme if missing
        if link and not link.startswith(("http://", "https://")):
            link = "https://" + link
        
        # Validate URL structure
        try:
            result = urlparse(link)
            if not result.netloc:
                print(f"Warning: Invalid URL '{link}'", file=sys.stderr)
                return ""
        except Exception as e:
            print(f"Warning: Error parsing URL '{link}': {e}", file=sys.stderr)
            return ""
        
        return link
    
    def to_dict(self) -> Dict[str, str]:
        """Convert record to dictionary."""
        return {
            "date": self.date,
            "title": self.title,
            "object_number": self.object_number,
            "link": self.link,
        }


class InventoryStandardizer:
    """Standardizes and deduplicates museum inventory records."""
    
    def __init__(self, input_file: str, output_file: str, 
                 corrections_file: Optional[str] = None,
                 withdrawals_file: Optional[str] = None):
        """
        Initialize standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output standardized TSV file
            corrections_file: Optional path to TSV with corrected records
            withdrawals_file: Optional path to TSV with withdrawn object numbers
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.corrections_file = Path(corrections_file) if corrections_file else None
        self.withdrawals_file = Path(withdrawals_file) if withdrawals_file else None
        
        self.records: Dict[str, InventoryRecord] = {}
        self.withdrawn: set = set()
    
    def load_records(self) -> None:
        """Load records from input TSV file."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            # Validate headers
            required_fields = {'date', 'title', 'object_number', 'link'}
            if not reader.fieldnames or not required_fields.issubset(set(reader.fieldnames)):
                raise ValueError(f"Input file must have headers: {required_fields}")
            
            for row in reader:
                try:
                    record = InventoryRecord(
                        date=row.get('date', ''),
                        title=row.get('title', ''),
                        object_number=row.get('object_number', ''),
                        link=row.get('link', '')
                    )
                    
                    if not record.object_number:
                        print("Warning: Skipping record with empty object_number", 
                              file=sys.stderr)
                        continue
                    
                    # Keep latest by date, or overwrite if no date
                    if record.object_number in self.records:
                        existing = self.records[record.object_number]
                        if record.date and (not existing.date or record.date > existing.date):
                            self.records[record.object_number] = record
                    else:
                        self.records[record.object_number] = record
                
                except Exception as e:
                    print(f"Warning: Error processing record: {e}", file=sys.stderr)
                    continue
        
        print(f"Loaded {len(self.records)} unique records", file=sys.stderr)
    
    def apply_corrections(self) -> None:
        """Apply corrections from corrections file."""
        if not self.corrections_file or not self.corrections_file.exists():
            return
        
        corrected_count = 0
        with open(self.corrections_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            for row in reader:
                try:
                    record = InventoryRecord(
                        date=row.get('date', ''),
                        title=row.get('title', ''),
                        object_number=row.get('object_number', ''),
                        link=row.get('link', '')
                    )
                    
                    if record.object_number in self.records:
                        self.records[record.object_number] = record
                        corrected_count += 1
                    else:
                        print(f"Warning: Correction references unknown object: "
                              f"{record.object_number}", file=sys.stderr)
                
                except Exception as e:
                    print(f"Warning: Error processing correction: {e}", file=sys.stderr)
        
        print(f"Applied {corrected_count} corrections", file=sys.stderr)
    
    def apply_withdrawals(self) -> None:
        """Remove records marked as withdrawn."""
        if not self.withdrawals_file or not self.withdrawals_file.exists():
            return
        
        withdrawn_count = 0
        with open(self.withdrawals_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            for row in reader:
                obj_num = row.get('object_number', '').strip().upper()
                if obj_num in self.records:
                    del self.records[obj_num]
                    self.withdrawn.add(obj_num)
                    withdrawn_count += 1
                else:
                    print(f"Warning: Withdrawal references unknown object: {obj_num}", 
                          file=sys.stderr)
        
        print(f"Withdrawn {withdrawn_count} records", file=sys.stderr)
    
    def save_records(self) -> None:
        """Save standardized records to output TSV file."""
        fieldnames = ['date', 'title', 'object_number', 'link']
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            
            # Sort by object number for consistent output
            for obj_num in sorted(self.records.keys()):
                record = self.records[obj_num]
                writer.writerow(record.to_dict())
        
        print(f"Saved {len(self.records)} standardized records to {self.output_file}", 
              file=sys.stderr)
    
    def generate_report(self) -> None:
        """Generate a summary report."""
        report_file = self.output_file.with_suffix('.report.txt')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("Museum Inventory Standardization Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total records processed: {len(self.records)}\n")
            f.write(f"Total withdrawals: {len(self.withdrawn)}\n")
            f.write(f"Output file: {self.output_file}\n\n")
            
            # Check for records with missing fields
            missing_date = sum(1 for r in self.records.values() if not r.date)
            missing_link = sum(1 for r in self.records.values() if not r.link)
            
            f.write("Data Quality Issues:\n")
            f.write(f"  Records missing date: {missing_date}\n")
            f.write(f"  Records missing link: {missing_link}\n")
        
        print(f"Report saved to {report_file}", file=sys.stderr)
    
    def run(self) -> None:
        """Execute the standardization pipeline."""
        self.load_records()
        self.apply_corrections()
        self.apply_withdrawals()
        self.save_records()
        self.generate_report()


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python script.py <input.tsv> <output.tsv> "
              "[corrections.tsv] [withdrawals.tsv]", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    corrections_file = sys.argv[3] if len(sys.argv) > 3 else None
    withdrawals_file = sys.argv[4] if len(sys.argv) > 4 else None
    
    standardizer = InventoryStandardizer(
        input_file=input_file,
        output_file=output_file,
        corrections_file=corrections_file,
        withdrawals_file=withdrawals_file
    )
    
    standardizer.run()


if __name__ == "__main__":
    main()
```

## Usage

**Basic usage:**
```bash
python script.py inventory.tsv standardized_inventory.tsv
```

**With corrections and withdrawals:**
```bash
python script.py inventory.tsv standardized_inventory.tsv corrections.tsv withdrawals.tsv
```

## Input File Format

**inventory.tsv:**
```
date	title	object_number	link
2024-01-15	Portrait of Unknown Man	OBJ-2024-001	https://museum.org/obj001
01/20/2024	Ancient Vase	OBJ-2024-002	museum.org/obj002
```

**corrections.tsv:** (same format, overwrites matching object_number)
```
date	title	object_number	link
2024-01-15	Portrait of Unknown Man (Restored)	OBJ-2024-001	https://museum.org/obj001-v2
```

**withdrawals.tsv:**
```
object_number
OBJ-2024-003
OBJ-2024-005
```

## Features

- ✅ Date normalization (multiple input formats)
- ✅ Title & object number standardization
- ✅ URL validation and normalization
- ✅ Deduplication (keeps latest by date)
- ✅ Correction application
- ✅ Withdrawal processing
- ✅ Error reporting
- ✅ Quality report generation
