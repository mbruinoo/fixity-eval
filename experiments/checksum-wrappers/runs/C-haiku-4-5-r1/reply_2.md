# Museum Inventory Standardization Script with Checksums

```python
#!/usr/bin/env python3
"""
Standardize museum inventory records from a TSV file with checksum verification.

Handles corrections, withdrawals, and standardization of dates, titles,
object numbers, and links. Uses checksums to detect unauthorized changes
to source data.
"""

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse


class InventoryRecord:
    """Represents a single museum inventory record."""

    REQUIRED_FIELDS = {"date", "title", "object_number", "link"}

    def __init__(self, record_dict: Dict[str, str], row_number: int):
        """
        Initialize a record.

        Args:
            record_dict: Dictionary with keys matching REQUIRED_FIELDS
            row_number: Line number in source file (for error reporting)
        """
        self.row_number = row_number
        self.date = record_dict.get("date", "").strip()
        self.title = record_dict.get("title", "").strip()
        self.object_number = record_dict.get("object_number", "").strip()
        self.link = record_dict.get("link", "").strip()
        self.withdrawn = False
        self.errors = []

        # Store original values for checksum
        self.original_values = {
            "date": self.date,
            "title": self.title,
            "object_number": self.object_number,
            "link": self.link,
        }
        self.original_checksum = self._compute_checksum(self.original_values)

    def _compute_checksum(self, values: Dict[str, str]) -> str:
        """
        Compute SHA-256 checksum of record values.

        Uses a canonical JSON representation for consistency.
        """
        # Sort keys for consistency
        canonical = json.dumps(values, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def get_current_checksum(self) -> str:
        """Get checksum of current (potentially modified) values."""
        current_values = {
            "date": self.date,
            "title": self.title,
            "object_number": self.object_number,
            "link": self.link,
        }
        return self._compute_checksum(current_values)

    def has_changed(self) -> bool:
        """Check if record has been modified since loading."""
        return self.get_current_checksum() != self.original_checksum

    def standardize_date(self) -> None:
        """Standardize date to ISO 8601 format (YYYY-MM-DD)."""
        if not self.date:
            self.errors.append("Missing date")
            return

        original = self.date
        formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d",
            "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y", "%Y",
        ]

        for fmt in formats:
            try:
                parsed_date = datetime.strptime(original, fmt)
                self.date = parsed_date.strftime("%Y-%m-%d")
                return
            except ValueError:
                continue

        self.errors.append(f"Could not parse date: '{original}'")

    def standardize_title(self) -> None:
        """Standardize title formatting."""
        if not self.title:
            self.errors.append("Missing title")
            return

        self.title = " ".join(self.title.split())
        self.title = self.title.rstrip(".,;:")
        if self.title and not self.title.endswith("."):
            self.title += "."

    def standardize_object_number(self) -> None:
        """Standardize object number format."""
        if not self.object_number:
            self.errors.append("Missing object number")
            return

        original = self.object_number
        normalized = original.replace("_", ".").replace("-", ".")
        normalized = re.sub(r"\.+", ".", normalized)
        normalized = normalized.strip(".")

        parts = normalized.split(".")
        if len(parts) < 2 or len(parts) > 3:
            self.errors.append(
                f"Object number '{original}' doesn't match expected format"
            )
            return

        try:
            year = int(parts[0])
            if year < 1800 or year > datetime.now().year + 1:
                self.errors.append(f"Object number year '{year}' seems unrealistic")
        except ValueError:
            self.errors.append(f"Object number year '{parts[0]}' is not numeric")
            return

        for i, part in enumerate(parts[1:], start=1):
            if not part.isdigit():
                self.errors.append(f"Object number part {i+1} '{part}' is not numeric")
                return

        self.object_number = normalized

    def standardize_link(self) -> None:
        """Standardize URL format."""
        if not self.link:
            self.errors.append("Missing link")
            return

        original = self.link

        if not original.startswith(("http://", "https://")):
            self.link = "https://" + original

        self.link = self.link.rstrip("/")

        try:
            result = urlparse(self.link)
            if not result.netloc:
                self.errors.append(f"Invalid URL: '{original}'")
                self.link = original
        except Exception as e:
            self.errors.append(f"Could not parse URL '{original}': {e}")

    def standardize(self) -> None:
        """Run all standardization steps."""
        self.standardize_date()
        self.standardize_title()
        self.standardize_object_number()
        self.standardize_link()

    def to_dict(self) -> Dict[str, str]:
        """Return record as dictionary."""
        return {
            "date": self.date,
            "title": self.title,
            "object_number": self.object_number,
            "link": self.link,
        }

    def is_valid(self) -> bool:
        """Check if record has no errors."""
        return len(self.errors) == 0


class ChecksumManager:
    """Manages checksums for data integrity verification."""

    def __init__(self, checksum_file: Optional[str] = None):
        """
        Initialize checksum manager.

        Args:
            checksum_file: Path to file storing checksums (JSON format)
        """
        self.checksum_file = Path(checksum_file) if checksum_file else None
        self.stored_checksums: Dict[str, str] = {}
        self.current_checksums: Dict[str, str] = {}

    def load_checksums(self) -> None:
        """Load stored checksums from file."""
        if not self.checksum_file or not self.checksum_file.exists():
            return

        try:
            with open(self.checksum_file, "r", encoding="utf-8") as f:
                self.stored_checksums = json.load(f)
        except json.JSONDecodeError:
            print(
                f"Warning: Could not parse checksum file {self.checksum_file}",
                file=sys.stderr,
            )

    def compute_file_checksum(self, file_path: Path) -> str:
        """
        Compute SHA-256 checksum of entire file.

        Uses streaming to handle large files efficiently.
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def compute_record_checksums(self, records: List[InventoryRecord]) -> Dict[str, str]:
        """
        Compute checksums for all records by object number.

        Args:
            records: List of InventoryRecord objects

        Returns:
            Dictionary mapping object_number to checksum
        """
        checksums = {}
        for record in records:
            if record.object_number:
                checksums[record.object_number] = record.original_checksum
        return checksums

    def verify_file_integrity(
        self, file_path: Path, expected_checksum: str
    ) -> Tuple[bool, str]:
        """
        Verify that a file hasn't been modified.

        Args:
            file_path: Path to file to check
            expected_checksum: Expected SHA-256 checksum

        Returns:
            Tuple of (is_valid, actual_checksum)
        """
        actual = self.compute_file_checksum(file_path)
        is_valid = actual == expected_checksum
        return is_valid, actual

    def verify_record_integrity(
        self, records: List[InventoryRecord]
    ) -> Tuple[bool, List[str]]:
        """
        Verify that records haven't been modified.

        Compares current checksums against stored checksums.

        Returns:
            Tuple of (all_valid, error_messages)
        """
        errors = []

        for record in records:
            if not record.object_number:
                continue

            if record.object_number not in self.stored_checksums:
                continue

            stored = self.stored_checksums[record.object_number]
            current = record.original_checksum

            if stored != current:
                errors.append(
                    f"Record {record.object_number} (row {record.row_number}): "
                    f"Data integrity check failed. "
                    f"Expected checksum {stored}, got {current}"
                )

        return len(errors) == 0, errors

    def save_checksums(self, records: List[InventoryRecord]) -> None:
        """
        Save checksums for all records.

        Args:
            records: List of InventoryRecord objects
        """
        if not self.checksum_file:
            return

        checksums = self.compute_record_checksums(records)
        with open(self.checksum_file, "w", encoding="utf-8") as f:
            json.dump(checksums, f, indent=2)

    def save_file_checksum(self, file_path: Path, checksum_file: Path) -> None:
        """
        Save file-level checksum to a separate file.

        Useful for detecting any changes to source files.

        Args:
            file_path: Path to file being checksummed
            checksum_file: Path to store the checksum
        """
        checksum = self.compute_file_checksum(file_path)
        metadata = {
            "file": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "checksum": checksum,
            "algorithm": "sha256",
        }
        with open(checksum_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)


class InventoryStandardizer:
    """Manages standardization of inventory records."""

    def __init__(
        self,
        input_file: str,
        corrections_file: Optional[str] = None,
        checksum_file: Optional[str] = None,
        verify_checksums: bool = False,
    ):
        """
        Initialize standardizer.

        Args:
            input_file: Path to input TSV file
            corrections_file: Optional TSV file with corrections/withdrawals
            checksum_file: Optional file for storing record checksums
            verify_checksums: Whether to verify checksums on load
        """
        self.input_file = Path(input_file)
        self.corrections_file = Path(corrections_file) if corrections_file else None
        self.checksum_manager = ChecksumManager(checksum_file)
        self.verify_checksums = verify_checksums
        self.records: List[InventoryRecord] = []
        self.corrections: Dict[str, Dict] = {}
        self.withdrawals: set = set()
        self.integrity_errors: List[str] = []

    def load_checksums(self) -> None:
        """Load stored checksums."""
        self.checksum_manager.load_checksums()

    def load_corrections(self) -> None:
        """Load corrections and withdrawals from corrections file."""
        if not self.corrections_file or not self.corrections_file.exists():
            return

        with open(self.corrections_file, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                obj_num = row.get("object_number", "").strip()
                action = row.get("action", "").strip().lower()

                if action == "withdraw":
                    self.withdrawals.add(obj_num)
                elif action == "update":
                    self.corrections[obj_num] = {
                        k: v.strip()
                        for k, v in row.items()
                        if k != "object_number"
                        and k != "action"
                        and v.strip()
                    }

    def load_records(self) -> None:
        """Load inventory records from TSV file."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")

        with open(self.input_file, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")

            if not reader.fieldnames:
                raise ValueError("Input file is empty or not a valid TSV")

            missing_fields = (
                InventoryRecord.REQUIRED_FIELDS - set(reader.fieldnames)
            )
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")

            for row_num, row in enumerate(reader, start=2):
                record = InventoryRecord(row, row_num)
                self.records.append(record)

    def verify_integrity(self) -> bool:
        """
        Verify data integrity if checksums are available.

        Returns:
            True if all checks pass or no stored checksums exist
        """
        if not self.verify_checksums or not self.checksum_manager.stored_checksums:
            return True

        valid, errors = self.checksum_manager.verify_record_integrity(self.records)
        self.integrity_errors = errors
        return valid

    def apply_corrections(self) -> None:
        """Apply corrections and mark withdrawals."""
        for record in self.records:
            if record.object_number in self.withdrawals:
                record.withdrawn = True
                continue

            if record.object_number in self.corrections:
                corrections = self.corrections[record.object_number]
                for field, value in corrections.items():
                    if hasattr(record, field):
                        setattr(record, field, value)

    def standardize_all(self) -> None:
        """Standardize all active records."""
        for record in self.records:
            if not record.withdrawn:
                record.standardize()

    def get_report(
        self,
    ) -> Tuple[int, int, int, int, List[str], List[str]]:
        """
        Generate processing report.

        Returns:
            Tuple of (total, valid, invalid, withdrawn, errors, integrity_errors)
        """
        total = len(self.records)
        withdrawn = sum(1 for r in self.records if r.withdrawn)
        valid = sum(1 for r in self.records if not r.withdrawn and r.is_valid())
        invalid = total - withdrawn - valid

        error_messages = []
        for record in self.records:
            if not record.withdrawn and record.errors:
                error_msg = (
                    f"Row {record.row_number} "
                    f"({record.object_number}): "
                    f"{'; '.join(record.errors)}"
                )
                error_messages.append(error_msg)

        return total, valid, invalid, withdrawn, error_messages, self.integrity_errors

    def save(
        self, output_file: str, include_withdrawn: bool = False
    ) -> None:
        """Save standardized records to TSV file."""
        output_path = Path(output_file)
        fieldnames = ["date", "title", "object_number", "link"]
        if include_withdrawn:
            fieldnames.append("status")

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()

            for record in self.records:
                if record.withdrawn and not include_withdrawn:
                    continue

                row = record.to_dict()
                if include_withdrawn:
                    row["status"] = "withdrawn" if record.withdrawn else "active"

                writer.writerow(row)

    def save_checksums(self) -> None:
        """Save checksums for current records."""
        self.checksum_manager.save_checksums(self.records)

    def save_file_checksum(self, output_file: Optional[str] = None) -> None:
        """
        Save checksum of input file for future verification.

        Args:
            output_file: Optional custom path for checksum file
        """
        checksum_path = output_file or self.input_file.with_suffix(".sha256")
        self.checksum_manager.save_file_checksum(self.input_file, checksum_path)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory records with checksum verification."
    )
    parser.add_argument("input", help="Input TSV file with inventory records")
    parser.add_argument(
        "-o",
        "--output",
        default="inventory_standardized.tsv",
        help="Output TSV file (default: inventory_standardized.tsv)",
    )
    parser.add_argument(
        "-c", "--corrections", help="TSV file with corrections and withdrawals"
    )
    parser.add_argument(
        "--checksums",
        help="JSON file storing record checksums for integrity verification",
    )
    parser.add_argument(
        "--save-checksums",
        action="store_true",
        help="Save checksums after processing (for future verification)",
    )
    parser.add_argument(
        "--verify-checksums",
        action="store_true",
        help="Verify data integrity against stored checksums",
    )
    parser.add_argument(
        "--save-file-checksum",
        metavar="FILE",
        help="Save SHA-256 checksum of input file to specified file",
    )
    parser.add_argument(
        "--verify-file-checksum",
        metavar="FILE",
        help="Verify input file against checksum stored in specified file",
    )
    parser.add_argument(
        "--include-withdrawn",
        action="store_true",
        help="Include withdrawn records in output (marked with status)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print detailed report"
    )

    args = parser.parse_args()

    try:
        # Verify file integrity if requested
        if args.verify_file_checksum:
            checksum_mgr = ChecksumManager()
            checksum_path = Path(args.verify_file_checksum)
            if checksum_path.exists():
                with open(checksum_path, "r") as f:
                    metadata = json.load(f)
                expected = metadata["checksum"]
                valid, actual = checksum_mgr.verify_file_integrity(
                    Path(args.input), expected
                )
                if not valid:
                    print(
                        f"Error: File integrity check failed!\n"
                        f"  Expected: {expected}\n"
                        f"  Actual:   {actual}",
                        file=sys.stderr,
                    )
                    return 1
                print("✓ File integrity verified")
            else:
                print(f"Warning: Checksum file not found: {checksum_path}",
                      file=sys.stderr)

        # Process inventory
        standardizer = InventoryStandardizer(
            args.input,
            args.corrections,
            args.checksums,
            args.verify_checksums,
        )
        standardizer.load_checksums()
        standardizer.load_records()

        # Verify record integrity
        if not standardizer.verify_integrity():
            print(
                "Warning: Data integrity issues detected:",
                file=sys.stderr,
            )
            for error in standardizer.integrity_errors:
                print(f"  {error}", file=sys.stderr)

        standardizer.apply_corrections()
        standardizer.standardize_all()

        # Generate report
        total, valid, invalid, withdrawn, errors, integrity_errs = (
            standardizer.get_report()
        )

        print(f"\n{'='*60}")
        print("INVENTORY STANDARDIZATION REPORT")
        print(f"{'='*60}")
        print(f"Total records:      {total}")
        print(f"Valid records:      {valid}")
        print(f"Invalid records:    {invalid}")
        print(f"Withdrawn records:  {withdrawn}")

        if integrity_errs:
            print(f"\n{'INTEGRITY WARNINGS':-^60}")
            for error in integrity_errs:
                print(f"  {error}")

        if errors and args.verbose:
            print(f"\n{'ERRORS':-^60}")
            for error in errors:
                print(f"  {error}")

        # Save standardized records
        standardizer.save(args.output, args.include_withdrawn)
        print(f"\nStandardized records saved to: {args.output}")

        # Save checksums if requested
        if args.save_checksums:
            standardizer.save_checksums()
            print(f"Record checksums saved to: {standardizer.checksum_manager.checksum_file}")

        # Save file checksum if requested
        if args.save_file_checksum:
            standardizer.save_file_checksum(args.save_file_checksum)
            print(f"File checksum saved to: {args.save_file_checksum}")

        print(f"{'='*60}\n")

        return 0 if invalid == 0 else 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

## Usage Examples

### Initial processing with checksum generation:
```bash
# Process and save record checksums
python standardize_inventory.py inventory.tsv \
  --checksums inventory.checksums.json \
  --save-checksums \
  -o standardized.tsv

# Also save file-level checksum
python standardize_inventory.py inventory.tsv \
  --checksums inventory.checksums.json \
  --save-checksums \
  --save-file-checksum inventory.sha256 \
  -o standardized.tsv
```

### Later processing with verification:
```bash
# Verify data hasn't changed and re-process
python standardize_inventory.py inventory.tsv \
  --checksums inventory.checksums.json \
  --verify-checksums \
  --verify-file-checksum inventory.sha256 \
  -o standardized.tsv
```

### With corrections and verification:
```bash
python standardize_inventory.py inventory.tsv \
  -c corrections.tsv \
  --checksums inventory.checksums.json \
  --verify-checksums \
  -o standardized.tsv \
  -v
```

## Checksum Files Generated

### inventory.checksums.json
```json
{
  "2020.15": "a1b2c3d4e5f6...",
  "2020.16": "f6e5d4c3b2a1...",
  "2020.17": "1a2b3c4d5e6f..."
}
```

### inventory.sha256
```json
{
  "file": "inventory.tsv",
  "timestamp": "2024-01-15T10:30:45.123456",
  "checksum": "abc123def456...",
  "algorithm": "sha256"
}
```

## Key Features

✓ **Record-level checksums** (SHA-256 of individual records)  
✓ **File-level checksums** (SHA-256 of entire file)  
✓ **Integrity verification** against stored checksums  
✓ **Detects unauthorized modifications** to source data  
✓ **Separate storage** for checksums (audit trail)  
✓ **Timestamp metadata** for checksum files  
✓ **Efficient streaming** for large files  
✓ **Comprehensive error reporting**
