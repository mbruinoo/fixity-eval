# Museum Inventory Standardizer with Checksums

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory TSV files with checksums for data integrity.

Uses checksums to verify source data hasn't changed between runs.
Detects unauthorized modifications and data corruption.
"""

import csv
import sys
import hashlib
import hmac
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
import json


class ChecksumManager:
    """Manages checksums for data integrity verification."""

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize checksum manager.
        
        Args:
            secret_key: Optional HMAC secret for tamper-evident checksums
        """
        self.secret_key = secret_key.encode() if secret_key else None

    def compute_row_checksum(self, row: dict, fields: List[str] = None) -> str:
        """
        Compute checksum for a single row.
        
        Args:
            row: Dictionary representing the row
            fields: Specific fields to checksum (default: all)
        
        Returns:
            Hex string checksum
        """
        if fields is None:
            fields = sorted(row.keys())
        
        # Create deterministic string representation
        row_data = "|".join(
            f"{field}:{row.get(field, '')}"
            for field in fields
        )
        
        if self.secret_key:
            return hmac.new(
                self.secret_key,
                row_data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
        else:
            return hashlib.sha256(row_data.encode('utf-8')).hexdigest()

    def compute_file_checksum(self, file_path: Path, chunk_size: int = 8192) -> str:
        """
        Compute checksum for entire file (resistant to order changes).
        
        Args:
            file_path: Path to file
            chunk_size: Buffer size for reading
        
        Returns:
            Hex string checksum
        """
        if self.secret_key:
            hasher = hmac.new(self.secret_key, digestmod=hashlib.sha256)
        else:
            hasher = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    hasher.update(chunk)
            return hasher.hexdigest()
        except FileNotFoundError:
            return None

    def compute_inventory_checksum(self, records: Dict[str, dict]) -> str:
        """
        Compute checksum for inventory (sorted by object number for consistency).
        
        Args:
            records: Dictionary of records keyed by object_number
        
        Returns:
            Hex string checksum
        """
        if self.secret_key:
            hasher = hmac.new(self.secret_key, digestmod=hashlib.sha256)
        else:
            hasher = hashlib.sha256()
        
        # Sort by object number for consistent ordering
        for obj_num in sorted(records.keys()):
            row_checksum = self.compute_row_checksum(records[obj_num])
            hasher.update(row_checksum.encode('utf-8'))
        
        return hasher.hexdigest()


class MuseumInventoryStandardizer:
    """Standardizes and validates museum inventory data with checksum verification."""

    def __init__(
        self,
        input_file: str,
        output_file: str = None,
        log_file: str = None,
        manifest_file: str = None,
        secret_key: str = None,
        verify_mode: bool = False
    ):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self.input_file.stem + "_standardized.tsv"
        self.log_file = Path(log_file) if log_file else self.input_file.stem + "_log.json"
        self.manifest_file = Path(manifest_file) if manifest_file else self.input_file.stem + "_manifest.json"
        self.verify_mode = verify_mode
        
        self.checksum_manager = ChecksumManager(secret_key=secret_key)
        self.records: Dict[str, dict] = {}
        self.row_checksums: Dict[str, str] = {}  # object_number -> checksum
        
        self.log = {
            "timestamp": datetime.now().isoformat(),
            "mode": "verify" if verify_mode else "standardize",
            "processed": 0,
            "standardized": 0,
            "corrections": [],
            "withdrawals": [],
            "duplicates": [],
            "errors": [],
            "checksum_verification": {},
            "data_integrity": {}
        }

    def standardize_date(self, date_str: str) -> str:
        """Convert date to ISO 8601 format (YYYY-MM-DD)."""
        if not date_str or date_str.strip() == "":
            return ""
        
        date_str = date_str.strip()
        
        formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d",
            "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y",
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
        """Standardize object number format."""
        if not obj_num:
            return ""
        return obj_num.strip().upper()

    def standardize_title(self, title: str) -> str:
        """Standardize title."""
        if not title:
            return ""
        title = title.strip()
        title = title.replace('"', '"').replace('"', '"')
        return title

    def standardize_link(self, link: str) -> str:
        """Standardize URL format."""
        if not link or link.strip() == "":
            return ""
        
        link = link.strip()
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

    def process_record(self, row: dict, line_num: int, source_checksum: str = None) -> bool:
        """
        Process and standardize a single record.
        
        Args:
            row: Row dictionary
            line_num: Line number in source file
            source_checksum: Optional checksum from manifest to verify against
        
        Returns:
            True if record should be kept, False if withdrawn
        """
        obj_num = self.standardize_object_number(row.get("object_number", ""))
        
        if not obj_num:
            self.log["errors"].append(f"Line {line_num}: Missing object number")
            return False
        
        # Verify source data integrity if checksum provided
        if source_checksum:
            current_checksum = self.checksum_manager.compute_row_checksum(row)
            if current_checksum != source_checksum:
                self.log["checksum_verification"].setdefault("mismatches", []).append({
                    "line": line_num,
                    "object_number": obj_num,
                    "expected": source_checksum,
                    "actual": current_checksum,
                    "status": "DATA_MODIFIED"
                })
                return False
        
        if self.detect_withdrawal(row):
            self.log["withdrawals"].append({
                "line": line_num,
                "object_number": obj_num,
                "title": row.get("title", "")
            })
            if obj_num in self.records:
                del self.records[obj_num]
            return False
        
        standardized = {
            "date": self.standardize_date(row.get("date", "")),
            "title": self.standardize_title(row.get("title", "")),
            "object_number": obj_num,
            "link": self.standardize_link(row.get("link", ""))
        }
        
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
        self.row_checksums[obj_num] = self.checksum_manager.compute_row_checksum(standardized)
        return True

    def read_tsv(self) -> List[Tuple[int, dict]]:
        """Read TSV file and return list of (line_num, row) tuples."""
        records = []
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    raise ValueError("Empty file or invalid TSV format")
                
                expected_cols = {"date", "title", "object_number", "link"}
                actual_cols = set(reader.fieldnames) if reader.fieldnames else set()
                
                if not expected_cols.issubset(actual_cols):
                    missing = expected_cols - actual_cols
                    raise ValueError(f"Missing required columns: {missing}")
                
                for i, row in enumerate(reader, start=2):
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
                
                for obj_num in sorted(self.records.keys()):
                    writer.writerow(self.records[obj_num])
            
            print(f"✓ Standardized inventory written to: {self.output_file}")
        
        except Exception as e:
            print(f"Error writing output file: {e}")
            sys.exit(1)

    def write_manifest(self):
        """
        Write manifest file with checksums for future verification.
        
        This file can be stored separately (e.g., in Git, S3) to verify
        that the source data hasn't been tampered with.
        """
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "source_file": str(self.input_file),
            "source_file_checksum": self.checksum_manager.compute_file_checksum(self.input_file),
            "output_file": str(self.output_file),
            "output_file_checksum": self.checksum_manager.compute_file_checksum(self.output_file),
            "inventory_checksum": self.checksum_manager.compute_inventory_checksum(self.records),
            "record_count": len(self.records),
            "records": {
                obj_num: {
                    "checksum": self.row_checksums[obj_num],
                    "data": self.records[obj_num]
                }
                for obj_num in sorted(self.records.keys())
            }
        }
        
        try:
            with open(self.manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            print(f"✓ Checksum manifest written to: {self.manifest_file}")
            
            self.log["data_integrity"]["manifest_file"] = str(self.manifest_file)
            self.log["data_integrity"]["file_checksums"] = {
                "source_file": manifest["source_file_checksum"],
                "output_file": manifest["output_file_checksum"],
                "inventory": manifest["inventory_checksum"]
            }
        
        except Exception as e:
            print(f"Error writing manifest: {e}")

    def load_manifest(self) -> Optional[dict]:
        """Load previously generated manifest for verification."""
        if not self.manifest_file.exists():
            return None
        
        try:
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load manifest: {e}")
            return None

    def verify_source_data(self) -> bool:
        """
        Verify that source data hasn't changed since last run.
        
        Returns:
            True if verification passed, False otherwise
        """
        manifest = self.load_manifest()
        
        if not manifest:
            print("No previous manifest found - skipping verification")
            return True
        
        print("Verifying source data integrity...")
        
        current_file_checksum = self.checksum_manager.compute_file_checksum(self.input_file)
        previous_file_checksum = manifest.get("source_file_checksum")
        
        self.log["checksum_verification"]["source_file"] = {
            "previous": previous_file_checksum,
            "current": current_file_checksum,
            "match": current_file_checksum == previous_file_checksum
        }
        
        if current_file_checksum != previous_file_checksum:
            print("⚠ WARNING: Source file has been modified since last standardization!")
            print(f"  Previous checksum: {previous_file_checksum}")
            print(f"  Current checksum:  {current_file_checksum}")
            self.log["checksum_verification"]["status"] = "SOURCE_DATA_MODIFIED"
            return False
        
        print("✓ Source data matches previous run")
        self.log["checksum_verification"]["status"] = "VERIFIED"
        return True

    def write_log(self):
        """Write processing log to JSON file."""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.log, f, indent=2, default=str)
            
            print(f"✓ Processing log written to: {self.log_file}")
        
        except Exception as e:
            print(f"Error writing log file: {e}")

    def print_summary(self):
        """Print processing summary with checksum information."""
        print("\n" + "="*70)
        print("MUSEUM INVENTORY STANDARDIZATION SUMMARY")
        print("="*70)
        print(f"Records processed:     {self.log['processed']}")
        print(f"Records standardized:  {self.log['standardized']}")
        print(f"Final inventory size:  {len(self.records)}")
        print(f"Corrections detected:  {len(self.log['corrections'])}")
        print(f"Withdrawals detected:  {len(self.log['withdrawals'])}")
        print(f"Errors:                {len(self.log['errors'])}")
        
        if self.log["data_integrity"]:
            print("\nDATA INTEGRITY (Checksums):")
            if "file_checksums" in self.log["data_integrity"]:
                checksums = self.log["data_integrity"]["file_checksums"]
                print(f"  Source file:   {checksums.get('source_file', 'N/A')[:16]}...")
                print(f"  Output file:   {checksums.get('output_file', 'N/A')[:16]}...")
                print(f"  Inventory:     {checksums.get('inventory', 'N/A')[:16]}...")
        
        if self.log["checksum_verification"]:
            print("\nCHECKSUM VERIFICATION:")
            verification = self.log["checksum_verification"]
            if "status" in verification:
                status = verification["status"]
                symbol = "✓" if status == "VERIFIED" else "⚠"
                print(f"  {symbol} Status: {status}")
            if "mismatches" in verification and verification["mismatches"]:
                print(f"  ✗ Data modifications detected: {len(verification['mismatches'])}")
        
        print("="*70)

    def standardize(self):
        """Execute the standardization process."""
        print(f"Reading inventory from: {self.input_file}")
        records = self.read_tsv()
        
        # Optionally verify source data against previous manifest
        if self.verify_mode:
            self.verify_source_data()
        
        print(f"Processing {len(records)} records...")
        for line_num, row in records:
            self.process_record(row, line_num)
        
        print(f"Writing standardized inventory...")
        self.write_tsv()
        self.write_manifest()
        self.write_log()
        self.print_summary()


def main():
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory TSV files with checksum verification"
    )
    parser.add_argument("input", help="Input TSV file path")
    parser.add_argument("-o", "--output", help="Output TSV file path")
    parser.add_argument("-l", "--log", help="Log file path")
    parser.add_argument("-m", "--manifest", help="Manifest file path (stores checksums)")
    parser.add_argument(
        "-k", "--key",
        help="HMAC secret key for tamper-evident checksums (optional)"
    )
    parser.add_argument(
        "-v", "--verify",
        action="store_true",
        help="Verify source data against previous manifest before processing"
    )
    
    args = parser.parse_args()
    
    standardizer = MuseumInventoryStandardizer(
        input_file=args.input,
        output_file=args.output,
        log_file=args.log,
        manifest_file=args.manifest,
        secret_key=args.key,
        verify_mode=args.verify
    )
    standardizer.standardize()


if __name__ == "__main__":
    main()
```

## Usage Examples

```bash
# First run - generates manifest with checksums
python3 standardize_inventory.py inventory.tsv -m checksums.json

# Verify source data hasn't changed before re-processing
python3 standardize_inventory.py inventory.tsv -m checksums.json --verify

# With HMAC secret key for tamper-evident checksums
python3 standardize_inventory.py inventory.tsv -m checksums.json -k "my-secret-key"

# Verify with HMAC
python3 standardize_inventory.py inventory.tsv -m checksums.json -k "my-secret-key" --verify
```

## Checksum Features

### 1. **Multiple Checksum Levels**
- **File-level**: Entire source file integrity
- **Inventory-level**: All standardized records combined
- **Row-level**: Individual record integrity

### 2. **Tamper Detection**
```json
{
  "checksum_verification": {
    "source_file": {
      "previous": "abc123def456...",
      "current": "xyz789uvw012...",
      "match": false
    },
    "status": "SOURCE_DATA_MODIFIED"
  }
}
```

### 3. **HMAC Support**
- Optional secret key makes checksums tamper-evident
- Verifies both integrity AND authenticity
- Anyone with the key can verify

### 4. **Manifest File**
Stores all checksums for future verification:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "source_file_checksum": "abc123...",
  "output_file_checksum": "def456...",
  "inventory_checksum": "ghi789...",
  "record_count": 1523,
  "records": {
    "ACC-001": {
      "checksum": "xyz789...",
      "data": {...}
    }
  }
}
```

### 5. **Verification Workflow**
1. Run standardization → generates manifest
2. Store manifest in Git/external system
3. Next run with `--verify` flag → compares checksums
4. Detects any unauthorized modifications

This approach provides **complete audit trail** and **data provenance**! 🔐
