# Museum Inventory Standardizer

Here's a comprehensive Python script for standardizing museum inventory records:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer

Standardizes museum object records from a TSV file by:
- Validating required fields
- Formatting dates consistently
- Normalizing object numbers
- Cleaning whitespace and special characters
- Validating URLs
- Generating reports on data quality
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class InventoryRecord:
    """Represents a standardized museum inventory record"""
    date: str
    title: str
    object_number: str
    link: str
    
    def to_dict(self) -> dict:
        return asdict(self)


class MuseumInventoryStandardizer:
    """Standardizes museum inventory records"""
    
    # Expected column names (case-insensitive)
    REQUIRED_FIELDS = {'date', 'title', 'object_number', 'link'}
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize the standardizer
        
        Args:
            strict_mode: If True, invalid records cause errors; if False, they're skipped
        """
        self.strict_mode = strict_mode
        self.validation_errors: List[str] = []
        self.standardized_records: List[InventoryRecord] = []
        self.skipped_records: List[Tuple[int, str]] = []
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text: strip whitespace, handle encoding"""
        if not isinstance(text, str):
            return ""
        return text.strip()
    
    @staticmethod
    def standardize_date(date_str: str) -> str:
        """
        Standardize date to ISO format (YYYY-MM-DD)
        
        Handles common formats:
        - ISO format: 2024-01-15
        - US format: 01/15/2024, 01-15-2024
        - European format: 15/01/2024, 15-01-2024
        - Text format: January 15, 2024
        - Partial dates: 2024, January 2024
        """
        date_str = date_str.strip()
        
        if not date_str:
            return ""
        
        # Already ISO format
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                return ""
        
        # Common date formats to try
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y', '%m-%d-%Y',
            '%d/%m/%Y', '%d-%m-%Y',
            '%B %d, %Y', '%b %d, %Y',
            '%d %B %Y', '%d %b %Y',
            '%Y',
            '%B %Y', '%b %Y',
            '%m/%Y', '%m-%Y',
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matched, return empty (invalid date)
        logger.warning(f"Could not parse date: {date_str}")
        return ""
    
    @staticmethod
    def standardize_object_number(obj_num: str) -> str:
        """
        Standardize object number format
        
        Removes extra whitespace, converts to uppercase if applicable
        """
        obj_num = MuseumInventoryStandardizer.normalize_text(obj_num)
        
        if not obj_num:
            return ""
        
        # Remove extra spaces around separators
        obj_num = ' '.join(obj_num.split())
        
        return obj_num
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate that URL is properly formatted"""
        url = url.strip()
        
        if not url:
            return False
        
        try:
            result = urlparse(url)
            # Check for minimum URL requirements
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def standardize_url(url: str) -> str:
        """Standardize URL format"""
        url = url.strip()
        
        if not url:
            return ""
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url
        
        return url
    
    def standardize_record(self, row: dict, row_num: int) -> Optional[InventoryRecord]:
        """
        Standardize a single record
        
        Args:
            row: Dictionary of record fields
            row_num: Row number for error reporting
            
        Returns:
            InventoryRecord if successful, None if invalid
        """
        try:
            # Normalize field names to lowercase
            normalized_row = {k.lower().strip(): v for k, v in row.items()}
            
            # Extract and validate required fields
            date_str = normalized_row.get('date', '')
            title = normalized_row.get('title', '')
            object_number = normalized_row.get('object_number', '')
            link = normalized_row.get('link', '')
            
            # Check for required fields
            missing_fields = []
            if not date_str.strip():
                missing_fields.append('date')
            if not title.strip():
                missing_fields.append('title')
            if not object_number.strip():
                missing_fields.append('object_number')
            if not link.strip():
                missing_fields.append('link')
            
            if missing_fields:
                error_msg = f"Row {row_num}: Missing required fields: {', '.join(missing_fields)}"
                self.validation_errors.append(error_msg)
                if self.strict_mode:
                    raise ValueError(error_msg)
                return None
            
            # Standardize each field
            standardized_date = self.standardize_date(date_str)
            if not standardized_date:
                error_msg = f"Row {row_num}: Invalid date format: {date_str}"
                self.validation_errors.append(error_msg)
                if self.strict_mode:
                    raise ValueError(error_msg)
                return None
            
            standardized_title = self.normalize_text(title)
            if not standardized_title:
                error_msg = f"Row {row_num}: Title cannot be empty after normalization"
                self.validation_errors.append(error_msg)
                if self.strict_mode:
                    raise ValueError(error_msg)
                return None
            
            standardized_obj_num = self.standardize_object_number(object_number)
            if not standardized_obj_num:
                error_msg = f"Row {row_num}: Object number cannot be empty after standardization"
                self.validation_errors.append(error_msg)
                if self.strict_mode:
                    raise ValueError(error_msg)
                return None
            
            standardized_link = self.standardize_url(link)
            if not self.validate_url(standardized_link):
                error_msg = f"Row {row_num}: Invalid URL format: {link}"
                self.validation_errors.append(error_msg)
                if self.strict_mode:
                    raise ValueError(error_msg)
                return None
            
            return InventoryRecord(
                date=standardized_date,
                title=standardized_title,
                object_number=standardized_obj_num,
                link=standardized_link
            )
        
        except Exception as e:
            self.validation_errors.append(f"Row {row_num}: {str(e)}")
            if self.strict_mode:
                raise
            return None
    
    def process_file(self, input_file: Path) -> bool:
        """
        Process inventory TSV file
        
        Args:
            input_file: Path to input TSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if reader.fieldnames is None:
                    logger.error("Empty input file")
                    return False
                
                # Normalize and validate column names
                normalized_fieldnames = [name.lower().strip() for name in reader.fieldnames]
                missing_fields = self.REQUIRED_FIELDS - set(normalized_fieldnames)
                
                if missing_fields:
                    logger.error(f"Missing required columns: {', '.join(missing_fields)}")
                    logger.error(f"Found columns: {', '.join(reader.fieldnames)}")
                    return False
                
                # Process each row
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                    standardized = self.standardize_record(row, row_num)
                    if standardized:
                        self.standardized_records.append(standardized)
                    else:
                        self.skipped_records.append((row_num, str(row)))
            
            return True
        
        except FileNotFoundError:
            logger.error(f"File not found: {input_file}")
            return False
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return False
    
    def write_output(self, output_file: Path) -> bool:
        """
        Write standardized records to TSV file
        
        Args:
            output_file: Path to output TSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['date', 'title', 'object_number', 'link'],
                    delimiter='\t'
                )
                writer.writeheader()
                for record in self.standardized_records:
                    writer.writerow(record.to_dict())
            
            logger.info(f"Wrote {len(self.standardized_records)} records to {output_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error writing output file: {e}")
            return False
    
    def print_report(self) -> None:
        """Print data quality report"""
        print("\n" + "="*60)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("="*60)
        print(f"Total records processed: {len(self.standardized_records) + len(self.skipped_records)}")
        print(f"Successfully standardized: {len(self.standardized_records)}")
        print(f"Records skipped: {len(self.skipped_records)}")
        
        if self.validation_errors:
            print(f"\nValidation errors ({len(self.validation_errors)}):")
            for error in self.validation_errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(self.validation_errors) > 10:
                print(f"  ... and {len(self.validation_errors) - 10} more")
        
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records from a TSV file'
    )
    parser.add_argument(
        'input_file',
        type=Path,
        help='Path to input TSV file'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=None,
        help='Path to output TSV file (default: input_file_standardized.tsv)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Strict mode: stop on first error (default: skip invalid records)'
    )
    parser.add_argument(
        '--report-only',
        action='store_true',
        help='Only generate report, do not write output file'
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not args.input_file.exists():
        logger.error(f"Input file does not exist: {args.input_file}")
        sys.exit(1)
    
    # Set output file path
    if args.output is None:
        output_file = args.input_file.parent / f"{args.input_file.stem}_standardized.tsv"
    else:
        output_file = args.output
    
    # Process inventory
    standardizer = MuseumInventoryStandardizer(strict_mode=args.strict)
    
    logger.info(f"Processing file: {args.input_file}")
    if not standardizer.process_file(args.input_file):
        sys.exit(1)
    
    # Write output
    if not args.report_only:
        if not standardizer.write_output(output_file):
            sys.exit(1)
    
    # Print report
    standardizer.print_report()


if __name__ == '__main__':
    main()
```

## Example Usage

### Create a sample input file (`museum_inventory.tsv`):
```tsv
Date	Title	Object Number	Link
01/15/2024	Ancient Greek Vase	2024.001	www.example.com/vase
2024-02-20	Medieval Manuscript	 2024.002	https://example.com/manuscript
February 14, 2024	Victorian Clock	2024.003	example.com/clock
2024	Modern Sculpture	2024.004	https://example.com/sculpture
```

### Run the script:
```bash
# Basic usage
python3 standardizer.py museum_inventory.tsv

# With custom output file
python3 standardizer.py museum_inventory.tsv -o standardized_inventory.tsv

# Strict mode (stop on first error)
python3 standardizer.py museum_inventory.tsv --strict

# Report only (no output file)
python3 standardizer.py museum_inventory.tsv --report-only
```

## Features

✅ **Flexible date parsing** - Handles multiple date formats  
✅ **URL validation** - Ensures valid URLs with automatic protocol addition  
✅ **Whitespace normalization** - Cleans up extra spaces  
✅ **Error reporting** - Detailed validation error messages  
✅ **Skippable records** - Process files with some invalid records  
✅ **Strict mode** - Optional strict validation  
✅ **Quality report** - Summary of processing results  

Would you like me to add features like duplicate detection, data backup, or integration with database systems?
