# Museum Inventory Standardizer

Here's a comprehensive Python script for standardizing museum inventory records:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer

Standardizes museum inventory records from a TSV file by:
- Validating required fields
- Formatting dates consistently
- Standardizing object numbers
- Cleaning titles
- Validating URLs
- Generating a standardized output file
"""

import sys
import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse


class MuseumInventoryStandardizer:
    """Standardizes museum inventory records."""
    
    REQUIRED_FIELDS = ['date', 'title', 'object_number', 'link']
    DATE_FORMATS = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%B %d, %Y',
        '%b %d, %Y',
        '%Y',
    ]
    
    def __init__(self, input_file: str, output_file: str = None, 
                 verbose: bool = False):
        """
        Initialize the standardizer.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file (defaults to input_standardized.tsv)
            verbose: Print detailed processing information
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else \
                          self.input_file.parent / f"{self.input_file.stem}_standardized.tsv"
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.records_processed = 0
        self.records_successful = 0
    
    def log(self, message: str, level: str = "INFO"):
        """Print log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def standardize_date(self, date_str: str) -> Tuple[str, bool]:
        """
        Standardize date to YYYY-MM-DD format.
        
        Returns:
            Tuple of (standardized_date, success_flag)
        """
        if not date_str or not date_str.strip():
            return "", False
        
        date_str = date_str.strip()
        
        # Try each format
        for fmt in self.DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d'), True
            except ValueError:
                continue
        
        # If no format matched, return original with warning
        self.warnings.append(f"Could not parse date: '{date_str}'")
        return date_str, False
    
    def standardize_title(self, title: str) -> str:
        """
        Standardize title formatting.
        
        - Strip whitespace
        - Remove extra spaces
        - Preserve capitalization
        """
        if not title:
            return ""
        
        title = title.strip()
        # Remove extra spaces
        title = re.sub(r'\s+', ' ', title)
        return title
    
    def standardize_object_number(self, obj_num: str) -> str:
        """
        Standardize object number formatting.
        
        - Strip whitespace
        - Uppercase
        - Remove extra punctuation
        """
        if not obj_num:
            return ""
        
        obj_num = obj_num.strip().upper()
        # Remove extra spaces around separators
        obj_num = re.sub(r'\s*([.\-])\s*', r'\1', obj_num)
        return obj_num
    
    def validate_url(self, url: str) -> Tuple[str, bool]:
        """
        Validate and standardize URL.
        
        Returns:
            Tuple of (url, is_valid)
        """
        if not url or not url.strip():
            return "", False
        
        url = url.strip()
        
        try:
            result = urlparse(url)
            # Check if URL has scheme and netloc
            if not result.scheme:
                url = 'https://' + url
                result = urlparse(url)
            
            if result.scheme and result.netloc:
                return url, True
            else:
                return url, False
        except Exception as e:
            self.warnings.append(f"Error validating URL '{url}': {str(e)}")
            return url, False
    
    def validate_record(self, record: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a record has all required fields.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        for field in self.REQUIRED_FIELDS:
            if field not in record:
                errors.append(f"Missing required field: {field}")
            elif not record[field] or not str(record[field]).strip():
                errors.append(f"Empty required field: {field}")
        
        return len(errors) == 0, errors
    
    def standardize_record(self, record: Dict) -> Tuple[Dict, List[str]]:
        """
        Standardize a single record.
        
        Returns:
            Tuple of (standardized_record, error_messages)
        """
        errors = []
        standardized = record.copy()
        
        # Standardize date
        if 'date' in record:
            standardized_date, success = self.standardize_date(record['date'])
            standardized['date'] = standardized_date
            if not success and standardized_date:
                self.log(f"Date parsed with uncertainty: {record['date']} -> {standardized_date}", 
                        "WARNING")
        
        # Standardize title
        if 'title' in record:
            standardized['title'] = self.standardize_title(record['title'])
        
        # Standardize object number
        if 'object_number' in record:
            standardized['object_number'] = self.standardize_object_number(
                record['object_number']
            )
        
        # Validate and standardize link
        if 'link' in record:
            url, valid = self.validate_url(record['link'])
            standardized['link'] = url
            if not valid:
                errors.append(f"Invalid URL: {record['link']}")
        
        return standardized, errors
    
    def read_input_file(self) -> List[Dict]:
        """Read and parse the input TSV file."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        records = []
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    raise ValueError("TSV file is empty or has no headers")
                
                # Check for required fields
                missing_fields = set(self.REQUIRED_FIELDS) - set(reader.fieldnames)
                if missing_fields:
                    raise ValueError(f"Missing required columns: {missing_fields}")
                
                for i, row in enumerate(reader, start=2):  # Start at 2 (after header)
                    records.append((i, row))
            
            self.log(f"Read {len(records)} records from input file")
            return records
        
        except csv.Error as e:
            raise ValueError(f"Error parsing TSV file: {str(e)}")
    
    def process_records(self, records: List[Tuple[int, Dict]]) -> List[Dict]:
        """Process and standardize all records."""
        standardized_records = []
        
        for line_num, record in records:
            self.records_processed += 1
            
            # Validate record
            is_valid, validation_errors = self.validate_record(record)
            if not is_valid:
                for error in validation_errors:
                    self.errors.append(f"Line {line_num}: {error}")
                self.log(f"Line {line_num}: Validation failed - {validation_errors}", "ERROR")
                continue
            
            # Standardize record
            standardized, standardize_errors = self.standardize_record(record)
            
            if standardize_errors:
                for error in standardize_errors:
                    self.errors.append(f"Line {line_num}: {error}")
                self.log(f"Line {line_num}: {standardize_errors}", "ERROR")
            
            standardized_records.append(standardized)
            self.records_successful += 1
        
        self.log(f"Successfully standardized {self.records_successful}/{self.records_processed} records")
        return standardized_records
    
    def write_output_file(self, records: List[Dict]) -> None:
        """Write standardized records to output TSV file."""
        if not records:
            self.log("No records to write", "WARNING")
            return
        
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f, 
                    fieldnames=self.REQUIRED_FIELDS,
                    delimiter='\t',
                    extrasaction='ignore'
                )
                writer.writeheader()
                writer.writerows(records)
            
            self.log(f"Wrote {len(records)} standardized records to {self.output_file}")
        except IOError as e:
            raise IOError(f"Error writing output file: {str(e)}")
    
    def print_report(self) -> None:
        """Print processing report."""
        print("\n" + "="*60)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("="*60)
        print(f"Input file: {self.input_file}")
        print(f"Output file: {self.output_file}")
        print(f"Records processed: {self.records_processed}")
        print(f"Records successful: {self.records_successful}")
        print(f"Success rate: {self.records_successful/self.records_processed*100:.1f}%" 
              if self.records_processed > 0 else "N/A")
        
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors[:10]:  # Show first 10
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        else:
            print("\nNo errors encountered!")
        
        print("="*60 + "\n")
    
    def standardize(self) -> bool:
        """
        Run the standardization process.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.log("Starting standardization process...")
            
            # Read input
            records = self.read_input_file()
            
            # Process records
            standardized = self.process_records(records)
            
            # Write output
            self.write_output_file(standardized)
            
            # Print report
            self.print_report()
            
            return self.records_successful == self.records_processed
        
        except Exception as e:
            print(f"FATAL ERROR: {str(e)}", file=sys.stderr)
            return False


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records from a TSV file'
    )
    parser.add_argument('input_file', help='Path to input TSV file')
    parser.add_argument('-o', '--output', help='Path to output TSV file')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Print detailed processing information')
    
    args = parser.parse_args()
    
    standardizer = MuseumInventoryStandardizer(
        args.input_file,
        args.output,
        args.verbose
    )
    
    success = standardizer.standardize()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Usage

### Basic usage:
```bash
python standardizer.py inventory.tsv
```

### With custom output file:
```bash
python standardizer.py inventory.tsv -o output.tsv
```

### With verbose logging:
```bash
python standardizer.py inventory.tsv -v
```

## Example Input File

```
date	title	object_number	link
1923-04-15	The Blue Vase	2021.45.12	https://museum.org/items/vase-001
04/20/1890	Portrait of Dr. Smith	1999-107-A	museum.org/portrait
May 3, 2000	Ancient Coin		https://museum.org/coins/123
2010	Sculpture	2015.22.5	not a url
```

## Features

- **Date standardization** – Handles multiple date formats
- **Title cleanup** – Removes extra whitespace
- **Object number standardization** – Consistent formatting
- **URL validation** – Ensures valid URLs
- **Error handling** – Reports issues with line numbers
- **Progress reporting** – Detailed summary of changes
- **Flexible input** – Handles various date formats

Customize the `REQUIRED_FIELDS`, `DATE_FORMATS`, and validation rules for your specific needs!
