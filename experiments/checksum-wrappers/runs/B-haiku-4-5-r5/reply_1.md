# Museum Inventory Standardization Script

```python
#!/usr/bin/env python3
"""
Script to standardize museum inventory records from a TSV file.

Handles validation, cleaning, and formatting of museum object records.
"""

import csv
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class InventoryStandardizer:
    """Standardizes museum inventory records."""

    # Configuration
    REQUIRED_FIELDS = ["date", "title", "object_number", "link"]
    DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y"]
    
    def __init__(self, input_file: str, output_file: str, log_file: str = None):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output standardized TSV file
            log_file: Optional path to error/warning log file
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.log_file = Path(log_file) if log_file else None
        
        self.records = []
        self.errors = []
        self.warnings = []
        
    def load_records(self) -> bool:
        """
        Load records from TSV file.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.input_file.exists():
            self.errors.append(f"Input file not found: {self.input_file}")
            return False
            
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    self.errors.append("TSV file is empty")
                    return False
                
                # Check for required fields
                missing_fields = set(self.REQUIRED_FIELDS) - set(reader.fieldnames or [])
                if missing_fields:
                    self.errors.append(f"Missing required fields: {missing_fields}")
                    return False
                
                for row_num, row in enumerate(reader, start=2):  # start=2 accounts for header
                    self.records.append((row_num, row))
                    
            print(f"✓ Loaded {len(self.records)} records from {self.input_file}")
            return True
            
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False
    
    def standardize_date(self, date_str: str, row_num: int) -> str:
        """
        Standardize date to YYYY-MM-DD format.
        
        Args:
            date_str: Date string to standardize
            row_num: Row number for error reporting
            
        Returns:
            Standardized date string or empty string if parsing fails
        """
        if not date_str or not date_str.strip():
            return ""
        
        date_str = date_str.strip()
        
        # Try each format
        for fmt in self.DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # If no format matched
        self.warnings.append(f"Row {row_num}: Could not parse date '{date_str}'")
        return date_str  # Return original
    
    def standardize_title(self, title: str, row_num: int) -> str:
        """
        Standardize title formatting.
        
        Args:
            title: Title string to standardize
            row_num: Row number for error reporting
            
        Returns:
            Standardized title
        """
        if not title or not title.strip():
            self.warnings.append(f"Row {row_num}: Empty title")
            return ""
        
        title = title.strip()
        
        # Remove extra whitespace
        title = re.sub(r'\s+', ' ', title)
        
        # Title case (capitalize first letter of major words)
        title = title.title()
        
        return title
    
    def standardize_object_number(self, obj_num: str, row_num: int) -> str:
        """
        Standardize object number format.
        
        Args:
            obj_num: Object number to standardize
            row_num: Row number for error reporting
            
        Returns:
            Standardized object number
        """
        if not obj_num or not obj_num.strip():
            self.errors.append(f"Row {row_num}: Missing object number")
            return ""
        
        obj_num = obj_num.strip()
        
        # Remove extra whitespace
        obj_num = re.sub(r'\s+', ' ', obj_num)
        
        # Make uppercase for consistency
        obj_num = obj_num.upper()
        
        return obj_num
    
    def standardize_link(self, link: str, row_num: int) -> str:
        """
        Validate and standardize URL.
        
        Args:
            link: URL to standardize
            row_num: Row number for error reporting
            
        Returns:
            Standardized link or empty string if invalid
        """
        if not link or not link.strip():
            self.warnings.append(f"Row {row_num}: Empty link")
            return ""
        
        link = link.strip()
        
        # Check for valid URL pattern
        url_pattern = r'^https?://'
        if not re.match(url_pattern, link):
            self.warnings.append(f"Row {row_num}: URL missing protocol: {link}")
            link = "https://" + link
        
        return link
    
    def check_duplicates(self) -> List[Tuple[str, List[int]]]:
        """
        Check for duplicate object numbers.
        
        Returns:
            List of (object_number, [row_numbers]) tuples for duplicates
        """
        obj_num_map = {}
        
        for row_num, record in self.records:
            obj_num = record.get("object_number", "").upper().strip()
            if obj_num:
                if obj_num not in obj_num_map:
                    obj_num_map[obj_num] = []
                obj_num_map[obj_num].append(row_num)
        
        # Find duplicates
        duplicates = [(k, v) for k, v in obj_num_map.items() if len(v) > 1]
        
        for obj_num, rows in duplicates:
            self.warnings.append(f"Duplicate object number '{obj_num}' in rows: {rows}")
        
        return duplicates
    
    def standardize_records(self) -> List[Dict]:
        """
        Standardize all loaded records.
        
        Returns:
            List of standardized record dictionaries
        """
        standardized = []
        
        for row_num, record in self.records:
            try:
                standardized_record = {
                    "date": self.standardize_date(record.get("date", ""), row_num),
                    "title": self.standardize_title(record.get("title", ""), row_num),
                    "object_number": self.standardize_object_number(record.get("object_number", ""), row_num),
                    "link": self.standardize_link(record.get("link", ""), row_num),
                }
                
                # Validate that required fields are present after standardization
                if not standardized_record["object_number"]:
                    self.errors.append(f"Row {row_num}: Failed to standardize required field 'object_number'")
                    continue
                
                if not standardized_record["title"]:
                    self.errors.append(f"Row {row_num}: Failed to standardize required field 'title'")
                    continue
                
                standardized.append(standardized_record)
                
            except Exception as e:
                self.errors.append(f"Row {row_num}: Unexpected error during standardization: {e}")
                continue
        
        # Check for duplicates
        self.check_duplicates()
        
        print(f"✓ Standardized {len(standardized)} records")
        return standardized
    
    def save_records(self, standardized_records: List[Dict]) -> bool:
        """
        Save standardized records to output TSV file.
        
        Args:
            standardized_records: List of standardized records
            
        Returns:
            True if successful, False otherwise
        """
        if not standardized_records:
            self.errors.append("No records to save")
            return False
        
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=self.REQUIRED_FIELDS,
                    delimiter='\t'
                )
                writer.writeheader()
                writer.writerows(standardized_records)
            
            print(f"✓ Saved {len(standardized_records)} records to {self.output_file}")
            return True
            
        except Exception as e:
            self.errors.append(f"Error writing output file: {e}")
            return False
    
    def write_log(self) -> bool:
        """
        Write errors and warnings to log file.
        
        Returns:
            True if log file was written, False if no log file specified
        """
        if not self.log_file:
            return False
        
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("MUSEUM INVENTORY STANDARDIZATION LOG\n")
                f.write("=" * 50 + "\n\n")
                
                if self.errors:
                    f.write(f"ERRORS ({len(self.errors)}):\n")
                    f.write("-" * 50 + "\n")
                    for error in self.errors:
                        f.write(f"  • {error}\n")
                    f.write("\n")
                
                if self.warnings:
                    f.write(f"WARNINGS ({len(self.warnings)}):\n")
                    f.write("-" * 50 + "\n")
                    for warning in self.warnings:
                        f.write(f"  • {warning}\n")
                    f.write("\n")
                
                if not self.errors and not self.warnings:
                    f.write("✓ No errors or warnings\n")
            
            print(f"✓ Log saved to {self.log_file}")
            return True
            
        except Exception as e:
            print(f"✗ Error writing log file: {e}", file=sys.stderr)
            return False
    
    def print_summary(self):
        """Print summary of standardization process."""
        print("\n" + "=" * 50)
        print("STANDARDIZATION SUMMARY")
        print("=" * 50)
        print(f"Records processed: {len(self.records)}")
        print(f"Records saved: {len(self.records) - len([e for e in self.errors if 'Row' in e])}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        
        if self.errors:
            print("\nFirst 5 errors:")
            for error in self.errors[:5]:
                print(f"  • {error}")
        
        if self.warnings:
            print("\nFirst 5 warnings:")
            for warning in self.warnings[:5]:
                print(f"  • {warning}")
    
    def run(self) -> bool:
        """
        Execute the full standardization process.
        
        Returns:
            True if successful, False otherwise
        """
        print("Starting museum inventory standardization...\n")
        
        if not self.load_records():
            self.print_summary()
            return False
        
        standardized = self.standardize_records()
        
        if not self.save_records(standardized):
            self.print_summary()
            return False
        
        self.write_log()
        self.print_summary()
        
        return len(self.errors) == 0


# Example usage
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python standardize_inventory.py <input.tsv> <output.tsv> [log.txt]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    log_file = sys.argv[3] if len(sys.argv) > 3 else "standardization.log"
    
    standardizer = InventoryStandardizer(input_file, output_file, log_file)
    success = standardizer.run()
    
    sys.exit(0 if success else 1)
```

## Usage

```bash
python standardize_inventory.py inventory.tsv inventory_standardized.tsv standardization.log
```

## Features

- **Date standardization**: Converts multiple date formats to YYYY-MM-DD
- **Title formatting**: Removes extra whitespace, applies title case
- **Object number validation**: Uppercases, removes duplicates detection
- **URL validation**: Ensures proper protocol and formatting
- **Error tracking**: Logs all errors and warnings
- **Duplicate detection**: Identifies duplicate object numbers
- **Comprehensive logging**: Detailed report of all issues

## Input TSV Format

```
date	title	object_number	link
2023-01-15	Ancient Vase	VAS-001	https://museum.example.com/vase1
01/15/2023	marble statue	STAT-002	museum.example.com/statue1
```
