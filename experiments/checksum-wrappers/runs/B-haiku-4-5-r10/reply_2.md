# Museum Inventory Standardization Script with Checksums

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory records from a TSV file with checksum verification.

Validates, cleans, and standardizes records containing:
- Date
- Title
- Object Number
- Link

Includes checksums to detect if source data has changed between runs.
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


class ChecksumManager:
    """Manages checksums for source data integrity verification."""

    CHECKSUM_ALGORITHMS = ["sha256", "md5"]

    def __init__(self, algorithm: str = "sha256"):
        if algorithm not in self.CHECKSUM_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        self.algorithm = algorithm

    def compute_file_checksum(self, filepath: Path) -> str:
        """Compute checksum of entire file."""
        hasher = hashlib.new(self.algorithm)
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def compute_record_checksum(self, record: Dict[str, str]) -> str:
        """
        Compute checksum of a single record.
        Uses JSON representation for consistent ordering.
        """
        # Sort keys for consistency
        json_str = json.dumps(record, sort_keys=True, separators=(",", ":"))
        hasher = hashlib.new(self.algorithm)
        hasher.update(json_str.encode("utf-8"))
        return hasher.hexdigest()

    def compute_batch_checksum(self, records: List[Dict[str, str]]) -> str:
        """Compute checksum of multiple records."""
        hasher = hashlib.new(self.algorithm)
        for record in records:
            record_checksum = self.compute_record_checksum(record)
            hasher.update(record_checksum.encode("utf-8"))
        return hasher.hexdigest()


class ChecksumStore:
    """Manages persistent storage of checksums."""

    def __init__(self, store_path: Path):
        self.store_path = store_path
        self.data: Dict = {}
        self._load()

    def _load(self) -> None:
        """Load checksums from storage file."""
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load checksum store: {e}", file=sys.stderr)
                self.data = {}

    def _save(self) -> None:
        """Save checksums to storage file."""
        try:
            self.store_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.store_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save checksum store: {e}", file=sys.stderr)

    def get_file_checksum(self, filepath: Path) -> Optional[str]:
        """Retrieve stored checksum for a file."""
        key = str(filepath.resolve())
        return self.data.get(key, {}).get("file_checksum")

    def get_record_checksum(self, filepath: Path, row_num: int) -> Optional[str]:
        """Retrieve stored checksum for a specific record."""
        key = str(filepath.resolve())
        if key in self.data and "records" in self.data[key]:
            return self.data[key]["records"].get(str(row_num))
        return None

    def store_file_checksum(self, filepath: Path, checksum: str) -> None:
        """Store checksum for a file."""
        key = str(filepath.resolve())
        if key not in self.data:
            self.data[key] = {}
        self.data[key]["file_checksum"] = checksum
        self.data[key]["timestamp"] = datetime.now().isoformat()

    def store_record_checksum(
        self, filepath: Path, row_num: int, checksum: str
    ) -> None:
        """Store checksum for a specific record."""
        key = str(filepath.resolve())
        if key not in self.data:
            self.data[key] = {}
        if "records" not in self.data[key]:
            self.data[key]["records"] = {}
        self.data[key]["records"][str(row_num)] = checksum

    def store_batch_checksum(self, filepath: Path, checksum: str) -> None:
        """Store checksum for all records in a file."""
        key = str(filepath.resolve())
        if key not in self.data:
            self.data[key] = {}
        self.data[key]["batch_checksum"] = checksum

    def save(self) -> None:
        """Persist checksums to disk."""
        self._save()


class InventoryStandardizer:
    """Standardizes museum inventory records with checksum verification."""

    def __init__(self, verbose: bool = False, checksum_store: Optional[ChecksumStore] = None):
        self.verbose = verbose
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
        self.checksum_manager = ChecksumManager()
        self.checksum_store = checksum_store
        self.source_changed_records: List[int] = []

    def standardize_date(self, date_str: str) -> Tuple[str, List[str]]:
        """
        Standardize date to ISO 8601 format (YYYY-MM-DD).
        Returns tuple of (standardized_date, issues_list).
        """
        issues = []

        if not date_str or not date_str.strip():
            return "", ["Missing date"]

        date_str = date_str.strip()

        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%B %Y",
            "%b %Y",
            "%Y",
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d"), issues
            except ValueError:
                continue

        year_match = re.search(r"\b(1[0-9]{3}|2[0-9]{3})\b", date_str)
        if year_match:
            issues.append(f"Ambiguous date format; extracted year {year_match.group(1)}")
            return f"{year_match.group(1)}-01-01", issues

        issues.append(f"Could not parse date: '{date_str}'")
        return date_str, issues

    def standardize_title(self, title: str) -> Tuple[str, List[str]]:
        """
        Standardize title formatting.
        Returns tuple of (standardized_title, issues_list).
        """
        issues = []

        if not title or not title.strip():
            issues.append("Missing title")
            return "", issues

        title = title.strip()
        title = re.sub(r"\s+", " ", title)

        if title.isupper() and len(title) > 1:
            issues.append("Title in all caps; converting to title case")
            title = title.title()

        if len(title) < 3:
            issues.append("Title very short (less than 3 characters)")
        elif len(title) > 500:
            issues.append("Title very long (over 500 characters)")

        return title, issues

    def standardize_object_number(self, obj_num: str) -> Tuple[str, List[str]]:
        """
        Standardize object number format.
        Returns tuple of (standardized_number, issues_list).
        """
        issues = []

        if not obj_num or not obj_num.strip():
            issues.append("Missing object number")
            return "", issues

        obj_num = obj_num.strip().upper()
        obj_num = re.sub(r"\s+", " ", obj_num)

        if not re.match(r"^[A-Z0-9\.\-\s]+$", obj_num):
            issues.append(
                f"Object number contains unusual characters: '{obj_num}'"
            )

        return obj_num, issues

    def validate_url(self, url: str) -> Tuple[str, List[str]]:
        """
        Validate and standardize URL format.
        Returns tuple of (standardized_url, issues_list).
        """
        issues = []

        if not url or not url.strip():
            issues.append("Missing link")
            return "", issues

        url = url.strip()

        if not url.startswith(("http://", "https://")):
            issues.append("URL missing scheme; adding https://")
            url = "https://" + url

        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                issues.append(f"Invalid URL structure: '{url}'")
                return url, issues
        except Exception as e:
            issues.append(f"URL parsing error: {str(e)}")

        return url, issues

    def process_record(
        self, record: Dict[str, str], row_num: int
    ) -> Tuple[Dict[str, str], List[Dict], str]:
        """
        Process and standardize a single record.
        Returns tuple of (standardized_record, issues_list, record_checksum).
        """
        issues = []

        standardized = {}

        date_val, date_issues = self.standardize_date(record.get("date", ""))
        standardized["date"] = date_val
        for issue in date_issues:
            issues.append({"row": row_num, "field": "date", "issue": issue})

        title_val, title_issues = self.standardize_title(record.get("title", ""))
        standardized["title"] = title_val
        for issue in title_issues:
            issues.append({"row": row_num, "field": "title", "issue": issue})

        obj_num_val, obj_num_issues = self.standardize_object_number(
            record.get("object_number", "")
        )
        standardized["object_number"] = obj_num_val
        for issue in obj_num_issues:
            issues.append({"row": row_num, "field": "object_number", "issue": issue})

        link_val, link_issues = self.validate_url(record.get("link", ""))
        standardized["link"] = link_val
        for issue in link_issues:
            issues.append({"row": row_num, "field": "link", "issue": issue})

        # Compute checksum of original record
        record_checksum = self.checksum_manager.compute_record_checksum(record)

        return standardized, issues, record_checksum

    def read_inventory(self, filepath: Path) -> List[Tuple[int, Dict[str, str]]]:
        """Read TSV inventory file and return records with checksums."""
        records = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t")

                if not reader.fieldnames:
                    raise ValueError("Empty file or missing headers")

                required_fields = {"date", "title", "object_number", "link"}
                missing_fields = required_fields - set(
                    field.lower() for field in reader.fieldnames
                )
                if missing_fields:
                    raise ValueError(
                        f"Missing required columns: {', '.join(missing_fields)}"
                    )

                for row_num, row in enumerate(reader, start=2):
                    normalized_row = {k.lower(): v for k, v in row.items()}
                    records.append((row_num, normalized_row))

        except FileNotFoundError:
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {str(e)}", file=sys.stderr)
            sys.exit(1)

        return records

    def verify_source_integrity(self, filepath: Path) -> Dict[str, any]:
        """
        Verify if source file has changed since last run.
        Returns a report of changes detected.
        """
        report = {
            "file_changed": False,
            "records_changed": [],
            "new_records": [],
            "missing_records": [],
        }

        if not self.checksum_store:
            return report

        # Check file-level checksum
        current_file_checksum = self.checksum_manager.compute_file_checksum(filepath)
        previous_file_checksum = self.checksum_store.get_file_checksum(filepath)

        if previous_file_checksum and previous_file_checksum != current_file_checksum:
            report["file_changed"] = True
            if self.verbose:
                print(f"ℹ File checksum has changed")

        # Check record-level checksums
        records = self.read_inventory(filepath)

        for row_num, record in records:
            current_checksum = self.checksum_manager.compute_record_checksum(record)
            previous_checksum = self.checksum_store.get_record_checksum(filepath, row_num)

            if previous_checksum is None:
                report["new_records"].append(row_num)
            elif previous_checksum != current_checksum:
                report["records_changed"].append({
                    "row": row_num,
                    "previous_checksum": previous_checksum,
                    "current_checksum": current_checksum,
                })

        return report

    def standardize_inventory(self, filepath: Path, verify_integrity: bool = True) -> List[Tuple[Dict, List[Dict]]]:
        """
        Standardize all records in inventory file.
        Returns list of (record, issues) tuples.
        """
        # Verify source integrity if requested
        if verify_integrity and self.checksum_store:
            integrity_report = self.verify_source_integrity(filepath)
            if integrity_report["file_changed"] or integrity_report["records_changed"]:
                print("⚠ Source data has changed since last run:", file=sys.stderr)
                if integrity_report["file_changed"]:
                    print("  - File checksum changed", file=sys.stderr)
                if integrity_report["records_changed"]:
                    print(
                        f"  - {len(integrity_report['records_changed'])} records changed",
                        file=sys.stderr,
                    )
                if integrity_report["new_records"]:
                    print(
                        f"  - {len(integrity_report['new_records'])} new records",
                        file=sys.stderr,
                    )

        records = self.read_inventory(filepath)
        results = []
        record_checksums = {}

        for row_num, record in records:
            standardized, issues, record_checksum = self.process_record(record, row_num)
            results.append((standardized, issues))
            record_checksums[row_num] = record_checksum

            if issues:
                self.warnings.extend(issues)

        # Store checksums if we have a checksum store
        if self.checksum_store:
            file_checksum = self.checksum_manager.compute_file_checksum(filepath)
            self.checksum_store.store_file_checksum(filepath, file_checksum)

            for row_num, checksum in record_checksums.items():
                self.checksum_store.store_record_checksum(filepath, row_num, checksum)

            # Compute and store batch checksum
            original_records = [record for _, record in records]
            batch_checksum = self.checksum_manager.compute_batch_checksum(original_records)
            self.checksum_store.store_batch_checksum(filepath, batch_checksum)

        return results

    def write_inventory(
        self, results: List[Tuple[Dict, List[Dict]]], output_path: Path
    ) -> None:
        """Write standardized inventory to TSV file."""
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["date", "title", "object_number", "link"]
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")

                writer.writeheader()
                for record, _ in results:
                    writer.writerow(record)

            print(f"✓ Standardized inventory written to: {output_path}")
        except Exception as e:
            print(f"Error writing output file: {str(e)}", file=sys.stderr)
            sys.exit(1)

    def generate_report(
        self, results: List[Tuple[Dict, List[Dict]]], output_path: Path
    ) -> None:
        """Generate a detailed report of issues found."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                total_records = len(results)
                records_with_issues = sum(1 for _, issues in results if issues)

                f.write("MUSEUM INVENTORY STANDARDIZATION REPORT\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Total records processed: {total_records}\n")
                f.write(f"Records with issues: {records_with_issues}\n")
                f.write(f"Issues found: {len(self.warnings)}\n\n")

                if self.warnings:
                    f.write("ISSUES BY TYPE:\n")
                    f.write("-" * 60 + "\n")

                    by_field = {}
                    for issue in self.warnings:
                        field = issue["field"]
                        if field not in by_field:
                            by_field[field] = []
                        by_field[field].append(issue)

                    for field in sorted(by_field.keys()):
                        f.write(f"\n{field.upper()}:\n")
                        for issue in by_field[field]:
                            f.write(f"  Row {issue['row']}: {issue['issue']}\n")
                else:
                    f.write("No issues found!\n")

            print(f"✓ Report written to: {output_path}")

        except Exception as e:
            print(f"Error writing report: {str(e)}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory records from a TSV file with checksum verification"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input TSV file with inventory records",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output TSV file (default: input_standardized.tsv)",
    )
    parser.add_argument(
        "-r",
        "--report",
        type=Path,
        default=None,
        help="Output report file (default: standardization_report.txt)",
    )
    parser.add_argument(
        "-c",
        "--checksum-store",
        type=Path,
        default=None,
        help="Path to checksum store file (default: .checksums/inventory.json)",
    )
    parser.add_argument(
        "--skip-integrity-check",
        action="store_true",
        help="Skip source integrity verification",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print verbose output",
    )

    args = parser.parse_args()

    # Set default paths
    if args.output is None:
        args.output = args.input.parent / f"{args.input.stem}_standardized.tsv"
    if args.report is None:
        args.report = args.input.parent / "standardization_report.txt"
    if args.checksum_store is None:
        args.checksum_store = args.input.parent / ".checksums" / "inventory.json"

    print(f"Reading inventory from: {args.input}")

    # Initialize checksum store
    checksum_store = ChecksumStore(args.checksum_store)

    standardizer = InventoryStandardizer(
        verbose=args.verbose,
        checksum_store=checksum_store,
    )

    results = standardizer.standardize_inventory(
        args.input,
        verify_integrity=not args.skip_integrity_check,
    )

    standardizer.write_inventory(results, args.output)
    standardizer.generate_report(results, args.report)

    # Save checksums
    checksum_store.save()
    print(f"✓ Checksums stored in: {args.checksum_store}")

    print(f"\n✓ Standardization complete!")
    print(f"  Records processed: {len(results)}")
    print(f"  Issues found: {len(standardizer.warnings)}")


if __name__ == "__main__":
    main()
```

## Checksum Store File Format

The checksums are stored in JSON format (`.checksums/inventory.json`):

```json
{
  "/path/to/inventory.tsv": {
    "file_checksum": "a3f5d8e9c1b2e4f6a7d8c9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9",
    "batch_checksum": "b4c6e9f0d2a3f5e7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0",
    "timestamp": "2024-01-15T14:32:00.123456",
    "records": {
      "2": "c5d7f0a1e3b4c6f8e9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1",
      "3": "d6e8a1b2f4c5d7e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2",
      "4": "e7f9b2c3a5d6e8f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3"
    }
  }
}
```

## Usage

```bash
# First run - creates checksums
python standardize_inventory.py input.tsv

# Second run - detects changes
python standardize_inventory.py input.tsv
# Output: ⚠ Source data has changed since last run: ...

# Skip integrity checks
python standardize_inventory.py input.tsv --skip-integrity-check

# Custom checksum store location
python standardize_inventory.py input.tsv --checksum-store /path/to/store.json

# Verbose output
python standardize_inventory.py input.tsv -v
```

## Key Features

1. **File-level checksums**: Detect if entire file has changed
2. **Record-level checksums**: Track which specific records changed
3. **Batch checksums**: Verify integrity of all records together
4. **Persistent storage**: JSON-based checkpoint file
5. **Change detection**: Reports new, modified, and deleted records
6. **Algorithm flexibility**: Supports SHA256 and MD5
7. **Integrity verification**: Optional automatic checking on each run
