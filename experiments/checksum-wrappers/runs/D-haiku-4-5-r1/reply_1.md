# Museum Inventory Standardizer

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory TSV files with versioning and deduplication.

Input TSV columns: date, title, object_number, link
Handles corrections and withdrawals of entries.
"""

import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
import json


class MuseumInventoryStandardizer:
    """Standardizes and validates museum inventory data."""

    def __init__(self, input_file: str, output_file: str = None, log_file: str = None):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self.input_file.stem + "_standardized.tsv"
        self.log_file = Path(log_file) if log_file else self.input_file.stem + "_log.json"
        
        self.records: Dict[str, dict] = {}  # object_number -> record
        self.log = {
            "processed": 0,
            "standardized": 0,
            "corrections": [],
            "withdrawals": [],
            "duplicates": [],
            "errors": []
        }

    def standardize_date(self, date_str: str) -> str:
        """Convert date to ISO 8601 format (YYYY-MM-DD)."""
        if not date_str or date_str.strip() == "":
            return ""
        
        date_str = date_str.strip()
        
        # Try common formats
        formats = [
            "%Y-%m-%d",  # 2023-01-15
            "%m/%d/%Y",  # 01/15/2023
            "%d/%m/%Y",  # 15/01/2023
            "%Y/%m/%d",  # 2023/01/15
            "%B %d, %Y", # January 15, 2023
            "%b %d, %Y", # Jan 15, 2023
            "%d %B %Y",  # 15 January 2023
            "%d %b %Y",  # 15 Jan 2023
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        self.log["errors"].append(f"Could not parse date: {date_str}")
        return date_str

    def standardize_object_number(self, obj_num: str) -> str:
        """Standardize object number format (remove extra spaces, uppercase)."""
        if not obj_num:
            return ""
        return obj_num.strip().upper()

    def standardize_title(self, title: str) -> str:
        """Standardize title (strip whitespace, normalize quotes)."""
        if not title:
            return ""
        title = title.strip()
        # Normalize quotes
        title = title.replace('"', '"').replace('"', '"')
        return title

    def standardize_link(self, link: str) -> str:
        """Standardize URL format."""
        if not link or link.strip() == "":
            return ""
        
        link = link.strip()
        
        # Add https:// if no protocol
        if link and not link.startswith(("http://", "https://", "ftp://")):
            link = "https://" + link
        
        return link

    def detect_withdrawal(self, row: dict) -> bool:
        """Detect if entry is marked as withdrawn."""
        withdrawal_indicators = ["withdrawn", "deleted", "removed", "cancelled", "canceled"]
        
        for field in ["title", "object_number"]:
            if field in row:
                value = str(row[field]).lower()
                if any(indicator in value for indicator in withdrawal_indicators):
                    return True
        return False

    def process_record(self, row: dict, line_num: int) -> bool:
        """
        Process and standardize a single record.
        Returns True if record should be kept, False if withdrawn.
        """
        # Standardize fields
        obj_num = self.standardize_object_number(row.get("object_number", ""))
        
        if not obj_num:
            self.log["errors"].append(f"Line {line_num}: Missing object number")
            return False
        
        # Check for withdrawal
        if self.detect_withdrawal(row):
            self.log["withdrawals"].append({
                "line": line_num,
                "object_number": obj_num,
                "title": row.get("title", "")
            })
            # Remove from records if it exists
            if obj_num in self.records:
                del self.records[obj_num]
            return False
        
        # Standardize all fields
        standardized = {
            "date": self.standardize_date(row.get("date", "")),
            "title": self.standardize_title(row.get("title", "")),
            "object_number": obj_num,
            "link": self.standardize_link(row.get("link", ""))
        }
        
        # Check for corrections/duplicates
        if obj_num in self.records:
            old_record = self.records[obj_num]
            if old_record != standardized:
                self.log["corrections"].append({
                    "object_number": obj_num,
                    "line": line_num,
                    "old": old_record,
                    "new": standardized
                })
        else:
            self.log["standardized"] += 1
        
        self.records[obj_num] = standardized
        return True

    def read_tsv(self) -> List[dict]:
        """Read TSV file and return list of dictionaries."""
        records = []
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    raise ValueError("Empty file or invalid TSV format")
                
                # Normalize column names
                expected_cols = {"date", "title", "object_number", "link"}
                actual_cols = set(reader.fieldnames) if reader.fieldnames else set()
                
                if not expected_cols.issubset(actual_cols):
                    missing = expected_cols - actual_cols
                    raise ValueError(f"Missing required columns: {missing}")
                
                for i, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                    records.append((i, row))
                    self.log["processed"] += 1
        
        except FileNotFoundError:
            print(f"Error: File not found: {self.input_file}")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
        
        return records

    def write_tsv(self):
        """Write standardized records to output TSV file."""
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ["date", "title", "object_number", "link"]
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                
                writer.writeheader()
                
                # Sort by object number for consistency
                for obj_num in sorted(self.records.keys()):
                    writer.writerow(self.records[obj_num])
            
            print(f"✓ Standardized inventory written to: {self.output_file}")
        
        except Exception as e:
            print(f"Error writing output file: {e}")
            sys.exit(1)

    def write_log(self):
        """Write processing log to JSON file."""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.log, f, indent=2, default=str)
            
            print(f"✓ Processing log written to: {self.log_file}")
        
        except Exception as e:
            print(f"Error writing log file: {e}")

    def print_summary(self):
        """Print processing summary."""
        print("\n" + "="*60)
        print("MUSEUM INVENTORY STANDARDIZATION SUMMARY")
        print("="*60)
        print(f"Records processed:     {self.log['processed']}")
        print(f"Records standardized:  {self.log['standardized']}")
        print(f"Final inventory size:  {len(self.records)}")
        print(f"Corrections detected:  {len(self.log['corrections'])}")
        print(f"Withdrawals detected:  {len(self.log['withdrawals'])}")
        print(f"Errors:                {len(self.log['errors'])}")
        print("="*60)
        
        if self.log["corrections"]:
            print("\nRecent Corrections:")
            for corr in self.log["corrections"][-3:]:
                print(f"  - {corr['object_number']} (line {corr['line']})")
        
        if self.log["withdrawals"]:
            print("\nRecent Withdrawals:")
            for wd in self.log["withdrawals"][-3:]:
                print(f"  - {wd['object_number']}: {wd['title']} (line {wd['line']})")
        
        if self.log["errors"]:
            print("\nErrors:")
            for err in self.log["errors"][-3:]:
                print(f"  - {err}")

    def standardize(self):
        """Execute the standardization process."""
        print(f"Reading inventory from: {self.input_file}")
        records = self.read_tsv()
        
        print(f"Processing {len(records)} records...")
        for line_num, row in records:
            self.process_record(row, line_num)
        
        print(f"Writing standardized inventory...")
        self.write_tsv()
        self.write_log()
        self.print_summary()


def main():
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory TSV files"
    )
    parser.add_argument(
        "input",
        help="Input TSV file path"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output TSV file path (default: input_standardized.tsv)"
    )
    parser.add_argument(
        "-l", "--log",
        help="Log file path (default: input_log.json)"
    )
    
    args = parser.parse_args()
    
    standardizer = MuseumInventoryStandardizer(
        input_file=args.input,
        output_file=args.output,
        log_file=args.log
    )
    standardizer.standardize()


if __name__ == "__main__":
    main()
```

## Usage

```bash
# Basic usage
python3 standardize_inventory.py inventory.tsv

# Custom output paths
python3 standardize_inventory.py inventory.tsv -o clean_inventory.tsv -l processing.log

# Check the results
cat inventory_standardized.tsv
cat inventory_log.json
```

## Features

✅ **Date Standardization**: Converts multiple date formats to ISO 8601  
✅ **Object Number Normalization**: Removes spaces, standardizes case  
✅ **URL Formatting**: Adds protocols, cleans whitespace  
✅ **Title Normalization**: Normalizes quotes and spacing  
✅ **Duplicate/Correction Detection**: Tracks when entries are updated  
✅ **Withdrawal Handling**: Removes entries marked as withdrawn  
✅ **Comprehensive Logging**: JSON log of all changes  
✅ **Error Reporting**: Identifies and reports data quality issues  

The script maintains a complete audit trail in the JSON log for data governance!
