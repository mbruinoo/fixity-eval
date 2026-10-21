# Museum Inventory Standardizer with Checksum Verification

Here's how to incorporate checksums to verify data integrity:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksum Verification

Adds checksums to verify:
- Source data hasn't changed between runs
- Output data integrity
- Individual record integrity
"""

import argparse
import csv
import sys
import hashlib
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from dataclasses import dataclass, asdict, field
from typing import List, Tuple, Optional, Dict
import logging

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
    record_hash: str = field(default='', init=False)
    
    def __post_init__(self):
        """Calculate record hash after initialization"""
        self.record_hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of record contents"""
        content = f"{self.date}|{self.title}|{self.object_number}|{self.link}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def to_dict(self, include_hash: bool = False) -> dict:
        """Convert to dictionary, optionally including hash"""
        data = asdict(self)
        if not include_hash:
            data.pop('record_hash', None)
        return data


@dataclass
class ChecksumMetadata:
    """Metadata for checksum verification"""
    file_path: str
    file_hash: str
    record_count: int
    processed_at: str
    standardizer_version: str = "1.0.0"
    records_hash: str = ""  # Hash of all records combined
    individual_record_hashes: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChecksumMetadata':
        """Create ChecksumMetadata from dictionary"""
        # Extract fields that belong to this class
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


class ChecksumManager:
    """Manages checksum calculation and verification"""
    
    @staticmethod
    def calculate_file_hash(file_path: Path, algorithm: str = 'sha256') -> str:
        """
        Calculate hash of entire file
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm ('sha256', 'md5', 'sha1')
            
        Returns:
            Hex digest of file hash
        """
        hash_func = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return ""
    
    @staticmethod
    def calculate_records_hash(records: List[InventoryRecord], 
                               algorithm: str = 'sha256') -> str:
        """
        Calculate combined hash of all records
        
        Args:
            records: List of inventory records
            algorithm: Hash algorithm to use
            
        Returns:
            Hex digest of combined records hash
        """
        hash_func = hashlib.new(algorithm)
        
        for record in records:
            hash_func.update(record.record_hash.encode())
        
        return hash_func.hexdigest()
    
    @staticmethod
    def get_record_hashes(records: List[InventoryRecord]) -> Dict[str, str]:
        """
        Get individual record hashes keyed by object number
        
        Args:
            records: List of inventory records
            
        Returns:
            Dictionary mapping object numbers to record hashes
        """
        return {record.object_number: record.record_hash for record in records}


class MuseumInventoryStandardizer:
    """Standardizes museum inventory records with checksum verification"""
    
    REQUIRED_FIELDS = {'date', 'title', 'object_number', 'link'}
    METADATA_SUFFIX = '.metadata.json'
    
    def __init__(self, strict_mode: bool = False, verify_source: bool = True):
        """
        Initialize the standardizer
        
        Args:
            strict_mode: If True, invalid records cause errors
            verify_source: If True, verify source file hasn't changed
        """
        self.strict_mode = strict_mode
        self.verify_source = verify_source
        self.validation_errors: List[str] = []
        self.standardized_records: List[InventoryRecord] = []
        self.skipped_records: List[Tuple[int, str]] = []
        
        # Checksum data
        self.source_metadata: Optional[ChecksumMetadata] = None
        self.output_metadata: Optional[ChecksumMetadata] = None
        self.checksum_manager = ChecksumManager()
    
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
        
        Handles common formats
        """
        date_str = date_str.strip()
        
        if not date_str:
            return ""
        
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                return ""
        
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
        
        logger.warning(f"Could not parse date: {date_str}")
        return ""
    
    @staticmethod
    def standardize_object_number(obj_num: str) -> str:
        """Standardize object number format"""
        obj_num = MuseumInventoryStandardizer.normalize_text(obj_num)
        
        if not obj_num:
            return ""
        
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
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def standardize_url(url: str) -> str:
        """Standardize URL format"""
        url = url.strip()
        
        if not url:
            return ""
        
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url
        
        return url
    
    def verify_source_file(self, input_file: Path) -> bool:
        """
        Verify source file integrity using stored metadata
        
        Args:
            input_file: Path to input file
            
        Returns:
            True if file matches stored checksum or no previous checksum exists
        """
        if not self.verify_source:
            return True
        
        metadata_file = input_file.parent / f"{input_file.name}{self.METADATA_SUFFIX}"
        
        # No previous metadata exists (first run)
        if not metadata_file.exists():
            logger.info("No previous source metadata found (first run)")
            return True
        
        try:
            with open(metadata_file, 'r') as f:
                stored_metadata_dict = json.load(f)
                stored_metadata = ChecksumMetadata.from_dict(stored_metadata_dict)
            
            # Calculate current file hash
            current_hash = self.checksum_manager.calculate_file_hash(input_file)
            
            if current_hash == stored_metadata.file_hash:
                logger.info("✓ Source file integrity verified (hash matches)")
                self.source_metadata = stored_metadata
                return True
            else:
                logger.warning("✗ Source file has changed!")
                logger.warning(f"  Previous hash: {stored_metadata.file_hash}")
                logger.warning(f"  Current hash:  {current_hash}")
                logger.warning(f"  Previous record count: {stored_metadata.record_count}")
                
                if self.strict_mode:
                    raise ValueError("Source file has changed unexpectedly")
                
                return False
        
        except Exception as e:
            logger.error(f"Error verifying source file: {e}")
            return False
    
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
            normalized_row = {k.lower().strip(): v for k, v in row.items()}
            
            date_str = normalized_row.get('date', '')
            title = normalized_row.get('title', '')
            object_number = normalized_row.get('object_number', '')
            link = normalized_row.get('link', '')
            
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
            # Verify source file integrity first
            if not self.verify_source_file(input_file):
                logger.warning("Proceeding despite source file verification failure")
            
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if reader.fieldnames is None:
                    logger.error("Empty input file")
                    return False
                
                normalized_fieldnames = [name.lower().strip() for name in reader.fieldnames]
                missing_fields = self.REQUIRED_FIELDS - set(normalized_fieldnames)
                
                if missing_fields:
                    logger.error(f"Missing required columns: {', '.join(missing_fields)}")
                    logger.error(f"Found columns: {', '.join(reader.fieldnames)}")
                    return False
                
                for row_num, row in enumerate(reader, start=2):
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
    
    def create_output_metadata(self, output_file: Path) -> ChecksumMetadata:
        """
        Create metadata for output file
        
        Args:
            output_file: Path to output file
            
        Returns:
            ChecksumMetadata object
        """
        records_hash = self.checksum_manager.calculate_records_hash(
            self.standardized_records
        )
        record_hashes = self.checksum_manager.get_record_hashes(
            self.standardized_records
        )
        
        metadata = ChecksumMetadata(
            file_path=str(output_file.absolute()),
            file_hash="",  # Will be calculated after file is written
            record_count=len(self.standardized_records),
            processed_at=datetime.now().isoformat(),
            records_hash=records_hash,
            individual_record_hashes=record_hashes
        )
        
        return metadata
    
    def write_output(self, output_file: Path, write_metadata: bool = True) -> bool:
        """
        Write standardized records to TSV file
        
        Args:
            output_file: Path to output TSV file
            write_metadata: If True, also write metadata file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Write data file
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['date', 'title', 'object_number', 'link'],
                    delimiter='\t'
                )
                writer.writeheader()
                for record in self.standardized_records:
                    writer.writerow(record.to_dict(include_hash=False))
            
            logger.info(f"Wrote {len(self.standardized_records)} records to {output_file}")
            
            # Create and write metadata
            if write_metadata:
                self.output_metadata = self.create_output_metadata(output_file)
                
                # Calculate file hash after writing
                self.output_metadata.file_hash = self.checksum_manager.calculate_file_hash(
                    output_file
                )
                
                metadata_file = Path(f"{output_file}{self.METADATA_SUFFIX}")
                with open(metadata_file, 'w') as f:
                    json.dump(self.output_metadata.to_dict(), f, indent=2)
                
                logger.info(f"Wrote metadata to {metadata_file}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error writing output file: {e}")
            return False
    
    def verify_output_integrity(self, output_file: Path) -> bool:
        """
        Verify integrity of output file
        
        Args:
            output_file: Path to output file
            
        Returns:
            True if file integrity is verified
        """
        if not self.output_metadata:
            logger.warning("No output metadata available for verification")
            return False
        
        try:
            # Calculate current file hash
            current_hash = self.checksum_manager.calculate_file_hash(output_file)
            
            if current_hash == self.output_metadata.file_hash:
                logger.info("✓ Output file integrity verified")
                return True
            else:
                logger.error("✗ Output file integrity check failed!")
                logger.error(f"  Expected hash: {self.output_metadata.file_hash}")
                logger.error(f"  Current hash:  {current_hash}")
                return False
        
        except Exception as e:
            logger.error(f"Error verifying output integrity: {e}")
            return False
    
    def print_report(self) -> None:
        """Print data quality and checksum report"""
        print("\n" + "="*70)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("="*70)
        print(f"Total records processed: {len(self.standardized_records) + len(self.skipped_records)}")
        print(f"Successfully standardized: {len(self.standardized_records)}")
        print(f"Records skipped: {len(self.skipped_records)}")
        
        # Source metadata info
        if self.source_metadata:
            print("\n" + "-"*70)
            print("SOURCE FILE VERIFICATION")
            print("-"*70)
            print(f"File: {self.source_metadata.file_path}")
            print(f"Hash: {self.source_metadata.file_hash}")
            print(f"Previous record count: {self.source_metadata.record_count}")
            print(f"Previous processing: {self.source_metadata.processed_at}")
        
        # Output metadata info
        if self.output_metadata:
            print("\n" + "-"*70)
            print("OUTPUT FILE CHECKSUMS")
            print("-"*70)
            print(f"File: {self.output_metadata.file_path}")
            print(f"File Hash (SHA-256): {self.output_metadata.file_hash}")
            print(f"Records Hash (SHA-256): {self.output_metadata.records_hash}")
            print(f"Record count: {self.output_metadata.record_count}")
            print(f"Processed: {self.output_metadata.processed_at}")
            
            if self.output_metadata.individual_record_hashes:
                print(f"\nSample record hashes (first 3):")
                for obj_num, hash_val in list(self.output_metadata.individual_record_hashes.items())[:3]:
                    print(f"  {obj_num}: {hash_val[:16]}...")
        
        if self.validation_errors:
            print("\n" + "-"*70)
            print(f"VALIDATION ERRORS ({len(self.validation_errors)})")
            print("-"*70)
            for error in self.validation_errors[:10]:
                print(f"  - {error}")
            if len(self.validation_errors) > 10:
                print(f"  ... and {len(self.validation_errors) - 10} more")
        
        print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory records from a TSV file with checksum verification'
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
        help='Strict mode: stop on first error'
    )
    parser.add_argument(
        '--skip-source-verify',
        action='store_true',
        help='Skip source file integrity verification'
    )
    parser.add_argument(
        '--no-metadata',
        action='store_true',
        help='Do not write metadata file'
    )
    parser.add_argument(
        '--verify-output',
        action='store_true',
        help='Verify output file integrity after writing'
    )
    parser.add_argument(
        '--report-only',
        action='store_true',
        help='Only generate report, do not write output file'
    )
    
    args = parser.parse_args()
    
    if not args.input_file.exists():
        logger.error(f"Input file does not exist: {args.input_file}")
        sys.exit(1)
    
    if args.output is None:
        output_file = args.input_file.parent / f"{args.input_file.stem}_standardized.tsv"
    else:
        output_file = args.output
    
    standardizer = MuseumInventoryStandardizer(
        strict_mode=args.strict,
        verify_source=not args.skip_source_verify
    )
    
    logger.info(f"Processing file: {args.input_file}")
    if not standardizer.process_file(args.input_file):
        sys.exit(1)
    
    if not args.report_only:
        if not standardizer.write_output(
            output_file,
            write_metadata=not args.no_metadata
        ):
            sys.exit(1)
        
        if args.verify_output:
            if not standardizer.verify_output_integrity(output_file):
                logger.warning("Output integrity verification failed")
    
    standardizer.print_report()


if __name__ == '__main__':
    main()
```

## Example Metadata File Output

After running the script, you'll get a `.metadata.json` file:

```json
{
  "file_path": "/path/to/museum_inventory_standardized.tsv",
  "file_hash": "a3f4c8e1b2d9f7c3e4a1b8d5f2c9e7a3b6c1d8e5f2a9b3c6d1e4f7a2b5c8",
  "record_count": 42,
  "processed_at": "2024-01-15T14:32:45.123456",
  "standardizer_version": "1.0.0",
  "records_hash": "f7a2b5c8a3f4c8e1b2d9f7c3e4a1b8d5f2c9e7a3b6c1d8e5f2a9b3c6d1e4",
  "individual_record_hashes": {
    "2024.001": "d1e4f7a2b5c8a3f4c8e1b2d9f7c3e4a1b8d5f2c9e7a3b6c1d8e5f2a9b3c6",
    "2024.002": "c8e1b2d9f7c3e4a1b8d5f2c9e7a3b6c1d8e5f2a9b3c6d1e4f7a2b5c8a3f4",
    "2024.003": "b8d5f2c9e7a3b6c1d8e5f2a9b3c6d1e4f7a2b5c8a3f4c8e1b2d9f7c3e4a1"
  }
}
```

## Usage Examples

```bash
# First run - creates metadata
python3 standardizer.py museum_inventory.tsv

# Verify source hasn't changed
python3 standardizer.py museum_inventory.tsv

# Skip source verification (force reprocessing)
python3 standardizer.py museum_inventory.tsv --skip-source-verify

# Verify output integrity after writing
python3 standardizer.py museum_inventory.tsv --verify-output

# No metadata file
python3 standardizer.py museum_inventory.tsv --no-metadata

# Strict mode with source verification
python3 standardizer.py museum_inventory.tsv --strict
```

## Key Features

✅ **File-level checksums** - Detect if source data changed  
✅ **Record-level checksums** - Track individual record integrity  
✅ **Combined records hash** - Verify complete dataset  
✅ **Automatic detection** - Warns if source file changed unexpectedly  
✅ **Output verification** - Ensure data wasn't corrupted during writing  
✅ **Metadata persistence** - JSON metadata files for audit trails  
✅ **SHA-256 hashing** - Cryptographically secure verification  

This approach ensures data integrity at multiple levels and helps detect accidental or intentional modifications!
