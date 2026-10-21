# Museum Inventory Standardizer with Checksum Verification

```python
#!/usr/bin/env python3
"""
Standardize museum inventory spreadsheet (.tsv) with checksum verification.
Detects if source data has been modified since last processing.
"""

import argparse
import csv
import sys
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class ChecksumRecord:
    """Records checksums and metadata for source file verification."""
    timestamp: str
    file_hash: str  # SHA256 of entire file
    row_count: int
    row_hashes: Dict[str, str]  # object_number -> row_hash
    metadata: Dict = None

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'ChecksumRecord':
        return cls(**data)


@dataclass
class InventoryEntry:
    """Represents a standardized inventory entry."""
    date: str
    title: str
    object_number: str
    link: str
    status: str = "active"  # active, corrected, withdrawn
    notes: str = ""

    def to_dict(self) -> Dict:
        return {
            'date': self.date,
            'title': self.title,
            'object_number': self.object_number,
            'link': self.link,
            'status': self.status,
            'notes': self.notes
        }


class ChecksumVerifier:
    """Manages checksum calculation and verification."""

    @staticmethod
    def calculate_file_hash(filepath: Path, algorithm: str = 'sha256') -> str:
        """Calculate hash of entire file."""
        hasher = hashlib.new(algorithm)
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        
        return hasher.hexdigest()

    @staticmethod
    def calculate_row_hash(row: Dict[str, str], algorithm: str = 'sha256') -> str:
        """Calculate hash of a single row (normalized)."""
        hasher = hashlib.new(algorithm)
        
        # Normalize: sort keys and convert to consistent format
        normalized = json.dumps(row, sort_keys=True, separators=(',', ':'))
        hasher.update(normalized.encode('utf-8'))
        
        return hasher.hexdigest()

    @staticmethod
    def generate_checksum_record(filepath: Path) -> ChecksumRecord:
        """Generate complete checksum record for a file."""
        file_hash = ChecksumVerifier.calculate_file_hash(filepath)
        row_hashes = {}
        row_count = 0

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                row_count += 1
                object_number = row.get('object_number', '').strip()
                if object_number:
                    row_hashes[object_number] = ChecksumVerifier.calculate_row_hash(row)

        return ChecksumRecord(
            timestamp=datetime.now().isoformat(),
            file_hash=file_hash,
            row_count=row_count,
            row_hashes=row_hashes,
            metadata={
                'filepath': str(filepath),
                'filesize': filepath.stat().st_size,
                'modified': datetime.fromtimestamp(
                    filepath.stat().st_mtime
                ).isoformat()
            }
        )


class InventoryStandardizer:
    """Standardizes and deduplicates museum inventory records with checksum verification."""

    def __init__(self, verbose: bool = False, checksum_dir: Optional[Path] = None):
        self.verbose = verbose
        self.entries: Dict[str, InventoryEntry] = {}
        self.history: List[Tuple[str, str]] = []
        self.checksum_dir = checksum_dir or Path.cwd()
        self.source_checksum: Optional[ChecksumRecord] = None
        self.verification_report = {
            'verified': False,
            'changes_detected': False,
            'new_entries': [],
            'modified_entries': [],
            'removed_entries': [],
            'unchanged_entries': []
        }

    def log(self, message: str):
        """Print verbose output."""
        if self.verbose:
            print(f"[INFO] {message}", file=sys.stderr)

    def _get_checksum_path(self, source_path: Path) -> Path:
        """Get path for storing checksums."""
        return self.checksum_dir / f".{source_path.stem}.checksums.json"

    def _load_previous_checksum(self, source_path: Path) -> Optional[ChecksumRecord]:
        """Load checksum record from previous run."""
        checksum_path = self._get_checksum_path(source_path)
        
        if not checksum_path.exists():
            self.log(f"No previous checksum found at {checksum_path}")
            return None

        try:
            with open(checksum_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.log(f"Loaded previous checksum from {checksum_path}")
            return ChecksumRecord.from_dict(data)
        except Exception as e:
            self.log(f"Warning: Could not load previous checksum: {e}")
            return None

    def _save_checksum(self, checksum: ChecksumRecord, source_path: Path):
        """Save checksum record for future verification."""
        checksum_path = self._get_checksum_path(source_path)
        
        try:
            with open(checksum_path, 'w', encoding='utf-8') as f:
                json.dump(checksum.to_dict(), f, indent=2)
            self.log(f"Saved checksum to {checksum_path}")
        except Exception as e:
            self.log(f"Warning: Could not save checksum: {e}")

    def verify_source_integrity(self, source_path: Path, force: bool = False) -> Tuple[bool, str]:
        """
        Verify source file hasn't changed since last processing.
        
        Returns:
            Tuple of (verified: bool, message: str)
        """
        current_checksum = ChecksumVerifier.generate_checksum_record(source_path)
        self.source_checksum = current_checksum
        
        previous_checksum = self._load_previous_checksum(source_path)

        # First run - always proceed
        if previous_checksum is None:
            message = (
                f"First run - no previous checksum found.\n"
                f"File: {source_path}\n"
                f"Hash: {current_checksum.file_hash}\n"
                f"Rows: {current_checksum.row_count}"
            )
            self.log(message)
            return True, message

        # Compare file hashes
        if current_checksum.file_hash == previous_checksum.file_hash:
            message = (
                f"✓ Source file unchanged (hash matches).\n"
                f"Previous processing: {previous_checksum.timestamp}\n"
                f"Current file: {current_checksum.metadata['modified']}"
            )
            self.log(message)
            self.verification_report['verified'] = True
            return True, message

        # File has changed - analyze differences
        self.log("⚠ Source file has changed!")
        self.verification_report['changes_detected'] = True
        changes = self._analyze_changes(previous_checksum, current_checksum)

        if force:
            message = f"Changes detected but processing forced:\n{changes}"
            self.log(message)
            return True, message
        else:
            message = f"Changes detected - review required:\n{changes}"
            return False, message

    def _analyze_changes(self, previous: ChecksumRecord, current: ChecksumRecord) -> str:
        """Analyze differences between previous and current checksums."""
        prev_rows = set(previous.row_hashes.keys())
        curr_rows = set(current.row_hashes.keys())

        new = curr_rows - prev_rows
        removed = prev_rows - curr_rows
        modified = []

        for obj_num in prev_rows & curr_rows:
            if previous.row_hashes[obj_num] != current.row_hashes[obj_num]:
                modified.append(obj_num)

        self.verification_report['new_entries'] = list(new)
        self.verification_report['modified_entries'] = modified
        self.verification_report['removed_entries'] = list(removed)
        self.verification_report['unchanged_entries'] = list(
            prev_rows & curr_rows - set(modified)
        )

        analysis = f"""
Changes detected:
  Previous row count: {previous.row_count}
  Current row count:  {current.row_count}
  New entries:        {len(new)}
  Modified entries:   {len(modified)}
  Removed entries:    {len(removed)}
  Unchanged entries:  {len(self.verification_report['unchanged_entries'])}

New object numbers:
"""
        for obj_num in sorted(new)[:10]:
            analysis += f"  + {obj_num}\n"
        if len(new) > 10:
            analysis += f"  ... and {len(new) - 10} more\n"

        if modified:
            analysis += f"\nModified object numbers:\n"
            for obj_num in sorted(modified)[:10]:
                analysis += f"  ~ {obj_num}\n"
            if len(modified) > 10:
                analysis += f"  ... and {len(modified) - 10} more\n"

        if removed:
            analysis += f"\nRemoved object numbers:\n"
            for obj_num in sorted(removed)[:10]:
                analysis += f"  - {obj_num}\n"
            if len(removed) > 10:
                analysis += f"  ... and {len(removed) - 10} more\n"

        return analysis

    def validate_date(self, date_str: str) -> str:
        """Validate and standardize date to ISO 8601 format."""
        if not date_str or not date_str.strip():
            raise ValueError("Date cannot be empty")

        date_str = date_str.strip()
        formats = [
            "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%m-%d-%Y",
            "%d/%m/%Y", "%d-%m-%Y", "%Y%m%d",
            "%b %d, %Y", "%B %d, %Y",
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue

        raise ValueError(f"Could not parse date: {date_str}")

    def validate_object_number(self, obj_num: str) -> str:
        """Validate and standardize object number."""
        if not obj_num or not obj_num.strip():
            raise ValueError("Object number cannot be empty")

        normalized = " ".join(obj_num.strip().split())

        if not any(c.isalnum() for c in normalized):
            raise ValueError(f"Invalid object number: {obj_num}")

        return normalized

    def validate_title(self, title: str) -> str:
        """Validate and standardize title."""
        if not title or not title.strip():
            return "[Untitled]"

        normalized = " ".join(title.strip().split())

        if normalized:
            normalized = normalized[0].upper() + normalized[1:]

        return normalized

    def validate_link(self, link: str) -> str:
        """Validate and standardize link."""
        if not link or not link.strip():
            return ""

        link = link.strip()

        if link and not link.startswith(('http://', 'https://', 'ftp://')):
            link = 'https://' + link

        return link

    def process_row(self, row: Dict[str, str], row_num: int) -> Tuple[InventoryEntry, List[str]]:
        """Process a single row and return standardized entry and warnings."""
        warnings = []

        try:
            date = self.validate_date(row.get('date', '').strip())
        except ValueError as e:
            warnings.append(f"Row {row_num}: {e}")
            date = None

        try:
            object_number = self.validate_object_number(row.get('object_number', ''))
        except ValueError as e:
            warnings.append(f"Row {row_num}: {e}")
            return None, warnings

        try:
            title = self.validate_title(row.get('title', ''))
        except ValueError as e:
            warnings.append(f"Row {row_num}: {e}")
            title = "[Invalid Title]"

        link = self.validate_link(row.get('link', ''))

        entry = InventoryEntry(
            date=date or datetime.now().strftime("%Y-%m-%d"),
            title=title,
            object_number=object_number,
            link=link
        )

        return entry, warnings

    def load_tsv(self, filepath: Path) -> List[str]:
        """Load and process TSV file. Returns list of warnings."""
        warnings = []
        required_columns = {'date', 'title', 'object_number', 'link'}

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')

            if not reader.fieldnames:
                raise ValueError("Empty file")

            missing = required_columns - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f"Missing required columns: {missing}")

            for row_num, row in enumerate(reader, start=2):
                entry, row_warnings = self.process_row(row, row_num)
                warnings.extend(row_warnings)

                if entry is None:
                    continue

                if entry.object_number in self.entries:
                    existing = self.entries[entry.object_number]

                    if entry.date > existing.date:
                        self.log(f"Correction detected for {entry.object_number}")
                        existing.status = "corrected"
                        existing.notes = f"Superseded by entry from {entry.date}"
                        self.entries[entry.object_number] = entry
                        entry.notes = f"Corrected from {existing.date}"
                        self.history.append(("corrected", entry.object_number))
                    else:
                        self.log(f"Duplicate (older) entry for {entry.object_number}")
                        warnings.append(
                            f"Row {row_num}: Duplicate object number {entry.object_number}"
                        )
                else:
                    self.entries[entry.object_number] = entry
                    self.history.append(("added", entry.object_number))

        return warnings

    def mark_withdrawn(self, object_numbers: List[str]):
        """Mark entries as withdrawn."""
        for obj_num in object_numbers:
            if obj_num in self.entries:
                self.entries[obj_num].status = "withdrawn"
                self.entries[obj_num].notes = "Withdrawn from collection"
                self.log(f"Marked {obj_num} as withdrawn")
                self.history.append(("withdrawn", obj_num))

    def get_active_entries(self) -> List[InventoryEntry]:
        """Get only active entries."""
        return [e for e in self.entries.values() if e.status == "active"]

    def get_all_entries(self) -> List[InventoryEntry]:
        """Get all entries."""
        return list(self.entries.values())

    def save_tsv(self, filepath: Path, include_all: bool = False):
        """Save standardized inventory to TSV file."""
        entries = self.get_all_entries() if include_all else self.get_active_entries()
        entries.sort(key=lambda e: (e.date, e.object_number))

        fieldnames = ['date', 'title', 'object_number', 'link', 'status', 'notes']

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            for entry in entries:
                writer.writerow(entry.to_dict())

        self.log(f"Saved {len(entries)} entries to {filepath}")

    def generate_report(self) -> str:
        """Generate a standardization report with verification info."""
        total_entries = len(self.entries)
        active_entries = len(self.get_active_entries())
        corrected = sum(1 for e in self.entries.values() if e.status == "corrected")
        withdrawn = sum(1 for e in self.entries.values() if e.status == "withdrawn")

        report = f"""
INVENTORY STANDARDIZATION REPORT
================================
Total unique entries:  {total_entries}
Active entries:        {active_entries}
Corrected entries:     {corrected}
Withdrawn entries:     {withdrawn}

Processing history:
"""
        action_counts = defaultdict(int)
        for action, _ in self.history:
            action_counts[action] += 1

        for action, count in sorted(action_counts.items()):
            report += f"  {action}: {count}\n"

        if self.source_checksum:
            report += f"""
SOURCE FILE VERIFICATION
========================
Timestamp:             {self.source_checksum.timestamp}
File hash (SHA256):    {self.source_checksum.file_hash}
Row count:             {self.source_checksum.row_count}
File size:             {self.source_checksum.metadata['filesize']} bytes
Last modified:         {self.source_checksum.metadata['modified']}

Previous verification: {'✓ PASSED' if self.verification_report['verified'] else '✗ CHANGES DETECTED' if self.verification_report['changes_detected'] else 'N/A (first run)'}
"""
            if self.verification_report['changes_detected']:
                report += f"""
Change Summary:
  New entries:         {len(self.verification_report['new_entries'])}
  Modified entries:    {len(self.verification_report['modified_entries'])}
  Removed entries:     {len(self.verification_report['removed_entries'])}
  Unchanged entries:   {len(self.verification_report['unchanged_entries'])}
"""

        return report


def main():
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory with checksum verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First run - creates baseline checksums
  %(prog)s input.tsv -o output.tsv

  # Subsequent runs - verifies integrity
  %(prog)s input.tsv -o output.tsv

  # Force processing even if changes detected
  %(prog)s input.tsv -o output.tsv --force

  # Store checksums in custom directory
  %(prog)s input.tsv -o output.tsv --checksum-dir /path/to/checksums

  # With all options
  %(prog)s input.tsv -o output.tsv -w withdrawals.txt -r report.txt -v
        """
    )

    parser.add_argument('input', type=Path, help='Input TSV file')
    parser.add_argument('-o', '--output', type=Path, default=None,
                        help='Output TSV file (default: input_standardized.tsv)')
    parser.add_argument('-w', '--withdrawals', type=Path, default=None,
                        help='File listing object numbers to mark as withdrawn')
    parser.add_argument('--include-all', action='store_true',
                        help='Include corrected and withdrawn entries in output')
    parser.add_argument('-r', '--report', type=Path, default=None,
                        help='Save standardization report to file')
    parser.add_argument('--checksum-dir', type=Path, default=None,
                        help='Directory for storing checksum files (default: current dir)')
    parser.add_argument('--force', action='store_true',
                        help='Process even if source file has changed')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    output_path = args.output or args.input.parent / f"{args.input.stem}_standardized.tsv"

    standardizer = InventoryStandardizer(
        verbose=args.verbose,
        checksum_dir=args.checksum_dir
    )

    try:
        # Verify source integrity
        print(f"Verifying source integrity...", file=sys.stderr)
        verified, verification_msg = standardizer.verify_source_integrity(
            args.input,
            force=args.force
        )

        print(verification_msg, file=sys.stderr)

        if not verified and not args.force:
            print("\nUse --force to process anyway.", file=sys.stderr)
            sys.exit(1)

        # Load and process
        print(f"\nLoading {args.input}...", file=sys.stderr)
        warnings = standardizer.load_tsv(args.input)

        if args.withdrawals and args.withdrawals.exists():
            print(f"Loading withdrawals from {args.withdrawals}...", file=sys.stderr)
            with open(args.withdrawals, 'r', encoding='utf-8') as f:
                withdrawn = [line.strip() for line in f if line.strip()]
            standardizer.mark_withdrawn(withdrawn)

        if warnings:
            print(f"\nWarnings ({len(warnings)}):", file=sys.stderr)
            for warning in warnings[:10]:
                print(f"  {warning}", file=sys.stderr)
            if len(warnings) > 10:
                print(f"  ... and {len(warnings) - 10} more", file=sys.stderr)

        # Save output and checksums
        print(f"\nSaving to {output_path}...", file=sys.stderr)
        standardizer.save_tsv(output_path, include_all=args.include_all)
        standardizer._save_checksum(standardizer.source_checksum, args.input)

        # Save report
        if args.report:
            report = standardizer.generate_report()
            with open(args.report, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to {args.report}", file=sys.stderr)
        else:
            print(standardizer.generate_report(), file=sys.stderr)

        print("\nDone!", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## How Checksums Work

### File-Level Hash
- **SHA256 hash** of the entire input file
- Detects any changes whatsoever (even whitespace)
- Quick initial check

### Row-Level Hashes
- **SHA256 hash** for each row (by object number)
- Normalized JSON format for consistency
- Detects which specific entries changed

### Checksum Storage
- Stored in `.{filename}.checksums.json`
- Hidden file in same directory as source (or custom `--checksum-dir`)
- Includes timestamp, file stats, and all row hashes

## Usage Examples

```bash
# First run - creates baseline
python standardize_inventory.py museum_data.tsv -o cleaned.tsv -v

# Second run - verifies nothing changed
python standardize_inventory.py museum_data.tsv -o cleaned.tsv -v
# Output: "✓ Source file unchanged (hash matches)"

# If source changed - refuses to process
python standardize_inventory.py museum_data.tsv -o cleaned.tsv
# Output: "✗ Changes detected - review required"
# Exit code: 1

# Force processing after review
python standardize_inventory.py museum_data.tsv -o cleaned.tsv --force

# Store checksums separately (e.g., for version control)
python standardize_inventory.py museum_data.tsv \
  -o cleaned.tsv \
  --checksum-dir ./checksums

# Generate detailed report
python standardize_inventory.py museum_data.tsv \
  -o cleaned.tsv \
  -r report.txt \
  --force -v
```

## Key Features

✅ **Detects modifications** - Any changes to source file  
✅ **Identifies specifics** - Shows exactly which rows changed  
✅ **Baseline creation** - First run establishes baseline  
✅ **Safe by default** - Refuses processing on detected changes  
✅ **Force option** - Process anyway with `--force`  
✅ **Separate storage** - Checksums can be stored centrally  
✅ **Audit trail** - Verification results in reports  
✅ **Hidden by default** - Checksum files start with `.`
