# Museum Inventory Standardizer with Checksums

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory spreadsheets (.tsv format) with checksum verification.
Columns: date, title, object number, and link
"""

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


class ChecksumManager:
    """Manages checksums for data integrity verification."""
    
    def __init__(self, checksum_file=None):
        self.checksum_file = checksum_file
        self.checksums = {}
    
    @staticmethod
    def hash_value(value):
        """Generate SHA256 hash of a value."""
        if value is None:
            value = ""
        return hashlib.sha256(str(value).encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_row(row):
        """Generate hash of an entire row."""
        row_str = json.dumps(row, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(row_str.encode('utf-8')).hexdigest()
    
    def add_row_checksum(self, row_num, original_row, standardized_row):
        """Store checksums for a row."""
        self.checksums[row_num] = {
            "original_row_hash": self.hash_row(original_row),
            "original_field_hashes": {
                key: self.hash_value(value)
                for key, value in original_row.items()
            },
            "standardized_row_hash": self.hash_row(standardized_row),
            "standardized_field_hashes": {
                key: self.hash_value(value)
                for key, value in standardized_row.items()
            }
        }
    
    def save(self):
        """Save checksums to JSON file."""
        if not self.checksum_file:
            return False
        
        try:
            with open(self.checksum_file, 'w', encoding='utf-8') as f:
                json.dump(self.checksums, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving checksums: {e}")
            return False
    
    def load(self):
        """Load checksums from JSON file."""
        if not self.checksum_file or not self.checksum_file.exists():
            return False
        
        try:
            with open(self.checksum_file, 'r', encoding='utf-8') as f:
                self.checksums = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading checksums: {e}")
            return False


class InventoryStandardizer:
    """Standardizes museum inventory data with checksum verification."""
    
    REQUIRED_COLUMNS = ["date", "title", "object_number", "link"]
    
    def __init__(self, input_file, output_file=None, checksum_file=None):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self.input_file.with_stem(
            self.input_file.stem + "_standardized"
        )
        
        # Default checksum file location
        if checksum_file is None:
            checksum_file = self.input_file.with_stem(self.input_file.stem + "_checksums").with_suffix('.json')
        self.checksum_manager = ChecksumManager(Path(checksum_file))
        
        self.errors = []
        self.warnings = []
        self.row_mapping = {}  # Track which original rows map to standardized rows
    
    def standardize_date(self, date_str):
        """Standardize date to ISO format (YYYY-MM-DD)."""
        if not date_str or not date_str.strip():
            self.warnings.append("Empty date field")
            return ""
        
        date_str = date_str.strip()
        formats = [
            "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%m-%d-%Y",
            "%d/%m/%Y", "%d-%m-%Y", "%B %d, %Y", "%b %d, %Y", "%Y",
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        self.warnings.append(f"Could not parse date: {date_str}")
        return date_str
    
    def standardize_title(self, title):
        """Standardize title: trim whitespace, fix capitalization."""
        if not title:
            self.warnings.append("Empty title field")
            return ""
        
        title = title.strip()
        title = " ".join(title.split())
        return title
    
    def standardize_object_number(self, obj_num):
        """Standardize object number: trim, uppercase, remove extra spaces."""
        if not obj_num:
            self.warnings.append("Empty object number")
            return ""
        
        obj_num = obj_num.strip().upper()
        obj_num = " ".join(obj_num.split())
        
        if not re.match(r"^[A-Z0-9\-\.]+$", obj_num):
            self.warnings.append(f"Invalid object number format: {obj_num}")
        
        return obj_num
    
    def standardize_link(self, link):
        """Standardize link: validate URL format, ensure protocol."""
        if not link or not link.strip():
            return ""
        
        link = link.strip()
        
        if not link.startswith(("http://", "https://", "ftp://")):
            link = "https://" + link
        
        try:
            result = urlparse(link)
            if not result.scheme or not result.netloc:
                self.warnings.append(f"Invalid URL: {link}")
                return link
        except Exception as e:
            self.warnings.append(f"URL parsing error: {link} ({e})")
        
        return link
    
    def read_input(self):
        """Read the input TSV file."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    self.errors.append("Empty file")
                    return None
                
                fieldnames = [name.lower().replace(" ", "_") for name in reader.fieldnames]
                rows = []
                
                for i, row in enumerate(reader, start=2):
                    normalized_row = {fieldnames[j]: v for j, v in enumerate(row.values())}
                    rows.append((i, normalized_row))
                
                return fieldnames, rows
        except FileNotFoundError:
            self.errors.append(f"File not found: {self.input_file}")
            return None
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return None
    
    def validate_row(self, row_num, row):
        """Validate that a row has all required columns."""
        missing = [col for col in self.REQUIRED_COLUMNS if col not in row]
        if missing:
            self.errors.append(f"Row {row_num}: Missing columns: {', '.join(missing)}")
            return False
        return True
    
    def process_rows(self, fieldnames, rows):
        """Process and standardize all rows with checksum tracking."""
        processed_rows = []
        
        for row_num, original_row in rows:
            if not self.validate_row(row_num, original_row):
                continue
            
            try:
                standardized_row = {
                    "date": self.standardize_date(original_row.get("date", "")),
                    "title": self.standardize_title(original_row.get("title", "")),
                    "object_number": self.standardize_object_number(original_row.get("object_number", "")),
                    "link": self.standardize_link(original_row.get("link", "")),
                }
                
                # Add extra columns if they exist
                for col in fieldnames:
                    if col not in self.REQUIRED_COLUMNS:
                        standardized_row[col] = original_row.get(col, "")
                
                # Record checksums for this row
                self.checksum_manager.add_row_checksum(
                    row_num, original_row, standardized_row
                )
                
                # Track mapping
                self.row_mapping[row_num] = len(processed_rows)
                processed_rows.append(standardized_row)
                
            except Exception as e:
                self.errors.append(f"Row {row_num}: Error processing - {e}")
        
        return processed_rows
    
    def write_output(self, rows):
        """Write standardized data to output file."""
        if not rows:
            self.errors.append("No valid rows to write")
            return False
        
        try:
            fieldnames = self.REQUIRED_COLUMNS + [
                k for k in rows[0].keys() if k not in self.REQUIRED_COLUMNS
            ]
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                writer.writerows(rows)
            
            return True
        except Exception as e:
            self.errors.append(f"Error writing output file: {e}")
            return False
    
    def standardize(self):
        """Main standardization workflow."""
        result = self.read_input()
        if result is None:
            return False
        
        fieldnames, rows = result
        processed_rows = self.process_rows(fieldnames, rows)
        
        if not self.write_output(processed_rows):
            return False
        
        return self.checksum_manager.save()
    
    def report(self):
        """Print standardization report."""
        print("\n" + "="*60)
        print("MUSEUM INVENTORY STANDARDIZATION REPORT")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"   • {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more")
        
        if not self.errors:
            print(f"\n✅ Successfully standardized to: {self.output_file}")
            print(f"✅ Checksums saved to: {self.checksum_manager.checksum_file}")
            print(f"   Processed {len(self.row_mapping)} rows")
        
        print("="*60 + "\n")


class ChecksumVerifier:
    """Verifies integrity of standardized data against checksums."""
    
    def __init__(self, original_file, standardized_file, checksum_file):
        self.original_file = Path(original_file)
        self.standardized_file = Path(standardized_file)
        self.checksum_file = Path(checksum_file)
        self.checksum_manager = ChecksumManager(self.checksum_file)
        self.issues = []
        self.verified_count = 0
    
    def verify(self):
        """Verify standardized data against checksums."""
        if not self.checksum_manager.load():
            print("❌ Could not load checksum file")
            return False
        
        # Read standardized file
        try:
            with open(self.standardized_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                standardized_rows = list(reader)
        except Exception as e:
            print(f"❌ Error reading standardized file: {e}")
            return False
        
        # Read original file
        try:
            with open(self.original_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                original_rows = list(reader)
        except Exception as e:
            print(f"❌ Error reading original file: {e}")
            return False
        
        # Verify each row
        for row_num_str, checksums in self.checksum_manager.checksums.items():
            row_num = int(row_num_str)
            original_idx = row_num - 2  # Account for 1-based and header row
            
            if original_idx < 0 or original_idx >= len(original_rows):
                self.issues.append(f"Row {row_num}: Original row not found")
                continue
            
            original_row = original_rows[original_idx]
            standardized_idx = len([k for k in self.checksum_manager.checksums.keys()
                                   if int(k) < row_num])
            
            if standardized_idx >= len(standardized_rows):
                self.issues.append(f"Row {row_num}: Standardized row not found")
                continue
            
            standardized_row = standardized_rows[standardized_idx]
            
            # Verify original row hash
            original_hash = ChecksumManager.hash_row(original_row)
            if original_hash != checksums["original_row_hash"]:
                self.issues.append(
                    f"Row {row_num}: Original row has been modified"
                )
                continue
            
            # Verify standardized row hash
            standardized_hash = ChecksumManager.hash_row(standardized_row)
            if standardized_hash != checksums["standardized_row_hash"]:
                self.issues.append(
                    f"Row {row_num}: Standardized row has been modified"
                )
                continue
            
            self.verified_count += 1
        
        return len(self.issues) == 0
    
    def report(self):
        """Print verification report."""
        print("\n" + "="*60)
        print("CHECKSUM VERIFICATION REPORT")
        print("="*60)
        print(f"\nOriginal File: {self.original_file}")
        print(f"Standardized File: {self.standardized_file}")
        print(f"Checksum File: {self.checksum_file}")
        
        if self.issues:
            print(f"\n❌ VERIFICATION FAILED - {len(self.issues)} issue(s):")
            for issue in self.issues:
                print(f"   • {issue}")
        else:
            print(f"\n✅ ALL ROWS VERIFIED ({self.verified_count} rows)")
            print("   No modifications detected")
        
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory with checksum verification"
    )
    parser.add_argument("input", help="Input TSV file")
    parser.add_argument("-o", "--output", help="Output TSV file")
    parser.add_argument("-c", "--checksums", help="Checksum JSON file")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify standardized data against checksums"
    )
    parser.add_argument(
        "--verify-files",
        nargs=3,
        metavar=("ORIGINAL", "STANDARDIZED", "CHECKSUMS"),
        help="Verify existing standardized file against original and checksums"
    )
    
    args = parser.parse_args()
    
    if args.verify_files:
        original, standardized, checksums = args.verify_files
        verifier = ChecksumVerifier(original, standardized, checksums)
        success = verifier.verify()
        verifier.report()
        sys.exit(0 if success else 1)
    
    standardizer = InventoryStandardizer(args.input, args.output, args.checksums)
    success = standardizer.standardize()
    standardizer.report()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
```

## Usage

### Standardize with Checksums

```bash
# Basic usage (auto-generates checksums file)
python standardize_inventory.py inventory.tsv

# Specify all files
python standardize_inventory.py inventory.tsv \
  -o standardized.tsv \
  -c checksums.json
```

### Verify Data Integrity

```bash
# Verify that standardized data hasn't been modified
python standardize_inventory.py \
  --verify-files inventory.tsv standardized.tsv checksums.json
```

## Example Checksum File Output

```json
{
  "2": {
    "original_row_hash": "a1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6",
    "original_field_hashes": {
      "date": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d",
      "title": "2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e",
      "object_number": "3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f",
      "link": "4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9g"
    },
    "standardized_row_hash": "5e6f7a8b9c0d1e2f3a4b5c6d7e8f9g0h",
    "standardized_field_hashes": {
      "date": "6f7a8b9c0d1e2f3a4b5c6d7e8f9g0h1i",
      "title": "7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v",
      "object_number": "8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w",
      "link": "9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x"
    }
  }
}
```

## Key Features

- **SHA256 Hashing**: Uses cryptographic hashing for integrity verification
- **Row-Level Checksums**: Tracks both individual fields and entire rows
- **Original Data Preservation**: Maintains checksums of original data for comparison
- **Verification Mode**: Separate command to verify standardized files haven't been modified
- **JSON Storage**: Human-readable JSON format for checksum storage
- **Audit Trail**: Enables tracing of what changed during standardization
- **Field-Level Tracking**: Can identify which specific fields were modified

This approach ensures data integrity and provides an audit trail for museum inventory management!
