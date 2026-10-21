# Museum Inventory Standardizer with Checksum Verification

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory spreadsheets with checksum verification.
Detects if source data has been modified between runs.
"""

import csv
import sys
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Tuple, Optional


@dataclass
class InventoryEntry:
    """Represents a standardized museum inventory entry."""
    date: str
    title: str
    object_number: str
    link: str
    status: str = "active"
    notes: str = ""


@dataclass
class ChecksumRecord:
    """Stores checksum information for verification."""
    file_path: str
    file_checksum: str  # SHA256 of entire file
    entry_checksums: Dict[str, str] = field(default_factory=dict)  # object_number -> SHA256
    timestamp: str = ""
    row_count: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_path': self.file_path,
            'file_checksum': self.file_checksum,
            'entry_checksums': self.entry_checksums,
            'timestamp': self.timestamp,
            'row_count': self.row_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ChecksumRecord':
        """Create from dictionary."""
        return cls(
            file_path=data.get('file_path', ''),
            file_checksum=data.get('file_checksum', ''),
            entry_checksums=data.get('entry_checksums', {}),
            timestamp=data.get('timestamp', ''),
            row_count=data.get('row_count', 0)
        )


class ChecksumManager:
    """Manages checksums for data integrity verification."""
    
    @staticmethod
    def compute_file_checksum(file_path: Path) -> str:
        """Compute SHA256 checksum of entire file."""
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            raise ValueError(f"Cannot compute file checksum: {str(e)}")
    
    @staticmethod
    def compute_entry_checksum(entry_dict: Dict) -> str:
        """Compute SHA256 checksum of an entry's data."""
        # Create canonical representation (sorted keys, consistent format)
        canonical = json.dumps(entry_dict, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    @staticmethod
    def compute_row_checksum(row: Dict) -> str:
        """Compute checksum of raw TSV row."""
        canonical = json.dumps(row, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()


class MuseumInventoryStandardizer:
    """Standardizes and validates museum inventory data with checksum verification."""
    
    def __init__(self, input_file: str, output_file: str = None, checksum_file: str = None):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self.input_file.with_stem(
            f"{self.input_file.stem}_standardized"
        )
        self.checksum_file = Path(checksum_file) if checksum_file else self.input_file.with_stem(
            f"{self.input_file.stem}_checksums"
        ).with_suffix('.json')
        
        self.entries: Dict[str, InventoryEntry] = {}
        self.history: List[Dict] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        self.current_checksums = ChecksumRecord(
            file_path=str(self.input_file),
            file_checksum="",
            timestamp=datetime.now().isoformat(),
            row_count=0
        )
        
        self.previous_checksums: Optional[ChecksumRecord] = None
        self.checksum_manager = ChecksumManager()
    
    def load_previous_checksums(self) -> bool:
        """Load previous checksums for comparison."""
        if not self.checksum_file.exists():
            return False
        
        try:
            with open(self.checksum_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.previous_checksums = ChecksumRecord.from_dict(data)
            print(f"✓ Loaded previous checksums from: {self.checksum_file}")
            return True
        except Exception as e:
            self.warnings.append(f"Could not load previous checksums: {str(e)}")
            return False
    
    def verify_file_integrity(self) -> bool:
        """Verify that source file hasn't changed."""
        if not self.previous_checksums:
            return True  # Nothing to verify against
        
        current_checksum = self.checksum_manager.compute_file_checksum(self.input_file)
        self.current_checksums.file_checksum = current_checksum
        
        if current_checksum != self.previous_checksums.file_checksum:
            self.warnings.append(
                f"FILE MODIFIED: Source file has changed since last standardization.\n"
                f"  Previous: {self.previous_checksums.file_checksum}\n"
                f"  Current:  {current_checksum}"
            )
            return False
        
        print(f"✓ File integrity verified: {current_checksum[:16]}...")
        return True
    
    def load_inventory(self) -> None:
        """Load and parse the TSV file."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    raise ValueError("Empty file or missing header")
                
                required_fields = {'date', 'title', 'object_number', 'link'}
                if not required_fields.issubset(set(reader.fieldnames or [])):
                    raise ValueError(f"Missing required columns. Expected: {required_fields}")
                
                for row_num, row in enumerate(reader, start=2):
                    self._process_row(row, row_num)
                
                self.current_checksums.row_count = row_num - 1
                
        except FileNotFoundError:
            self.errors.append(f"File not found: {self.input_file}")
            raise
        except Exception as e:
            self.errors.append(f"Error loading file: {str(e)}")
            raise
    
    def _process_row(self, row: Dict, row_num: int) -> None:
        """Process and validate a single row."""
        try:
            # Compute checksum of raw row for audit trail
            row_checksum = self.checksum_manager.compute_row_checksum(row)
            
            # Parse action markers
            action, cleaned_row = self._extract_action(row)
            
            # Standardize fields
            date = self._standardize_date(cleaned_row.get('date', '').strip())
            title = cleaned_row.get('title', '').strip()
            object_number = self._standardize_object_number(cleaned_row.get('object_number', '').strip())
            link = self._standardize_link(cleaned_row.get('link', '').strip())
            
            if not object_number:
                self.errors.append(f"Row {row_num}: Missing object number")
                return
            
            entry = InventoryEntry(
                date=date,
                title=title,
                object_number=object_number,
                link=link
            )
            
            # Compute entry checksum
            entry_checksum = self.checksum_manager.compute_entry_checksum(asdict(entry))
            self.current_checksums.entry_checksums[object_number] = entry_checksum
            
            # Check if entry has changed from previous run
            if self.previous_checksums and object_number in self.previous_checksums.entry_checksums:
                previous_checksum = self.previous_checksums.entry_checksums[object_number]
                if entry_checksum != previous_checksum:
                    self.warnings.append(
                        f"Row {row_num}: Entry {object_number} has changed\n"
                        f"  Previous: {previous_checksum}\n"
                        f"  Current:  {entry_checksum}"
                    )
            
            # Handle actions
            if action == "WITHDRAWN":
                self._handle_withdrawal(entry, row_num)
            elif action == "CORRECTED":
                self._handle_correction(entry, row_num)
            else:
                self._handle_new_entry(entry, row_num)
                
        except Exception as e:
            self.errors.append(f"Row {row_num}: {str(e)}")
    
    def _extract_action(self, row: Dict) -> Tuple[str, Dict]:
        """Extract action markers from row."""
        actions = {"WITHDRAWN", "CORRECTED", "DUPLICATE"}
        action = None
        cleaned_row = row.copy()
        
        title = row.get('title', '')
        for act in actions:
            pattern = f"^{act}\\s*:\\s*"
            if re.match(pattern, title, re.IGNORECASE):
                action = act.upper()
                cleaned_row['title'] = re.sub(pattern, '', title, flags=re.IGNORECASE).strip()
                break
        
        return action, cleaned_row
    
    def _standardize_date(self, date_str: str) -> str:
        """Standardize date format to YYYY-MM-DD."""
        if not date_str:
            return ""
        
        from datetime import datetime as dt
        
        date_str = date_str.strip()
        date_formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y",
            "%Y/%m/%d", "%B %d, %Y", "%b %d, %Y",
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = dt.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        self.errors.append(f"Could not parse date: {date_str}")
        return date_str
    
    def _standardize_object_number(self, obj_num: str) -> str:
        """Standardize object number format."""
        if not obj_num:
            return ""
        
        obj_num = re.sub(r'\s+', ' ', obj_num).strip()
        obj_num = re.sub(r'[\-_/]', '.', obj_num)
        return obj_num.upper()
    
    def _standardize_link(self, link: str) -> str:
        """Standardize URL format."""
        if not link:
            return ""
        
        link = link.strip()
        if link and not link.startswith(('http://', 'https://')):
            link = 'https://' + link
        
        return link
    
    def _handle_new_entry(self, entry: InventoryEntry, row_num: int) -> None:
        """Handle a new or updated entry."""
        if entry.object_number in self.entries:
            old_entry = self.entries[entry.object_number]
            self.history.append({
                'object_number': entry.object_number,
                'action': 'updated',
                'row': row_num,
                'old_data': asdict(old_entry),
                'new_data': asdict(entry)
            })
        else:
            self.history.append({
                'object_number': entry.object_number,
                'action': 'added',
                'row': row_num
            })
        
        entry.status = "active"
        self.entries[entry.object_number] = entry
    
    def _handle_withdrawal(self, entry: InventoryEntry, row_num: int) -> None:
        """Handle withdrawn entry."""
        if entry.object_number in self.entries:
            old_entry = self.entries[entry.object_number]
            self.history.append({
                'object_number': entry.object_number,
                'action': 'withdrawn',
                'row': row_num,
                'reason': entry.title or "No reason provided"
            })
            old_entry.status = "withdrawn"
            old_entry.notes = f"Withdrawn: {entry.title}"
        else:
            self.errors.append(f"Row {row_num}: Cannot withdraw non-existent object {entry.object_number}")
    
    def _handle_correction(self, entry: InventoryEntry, row_num: int) -> None:
        """Handle corrected entry."""
        if entry.object_number in self.entries:
            old_entry = self.entries[entry.object_number]
            self.history.append({
                'object_number': entry.object_number,
                'action': 'corrected',
                'row': row_num,
                'old_data': asdict(old_entry),
                'new_data': asdict(entry)
            })
            for field in ['date', 'title', 'link']:
                if getattr(entry, field):
                    setattr(old_entry, field, getattr(entry, field))
            old_entry.notes = f"Corrected on {datetime.now().strftime('%Y-%m-%d')}"
        else:
            self.errors.append(f"Row {row_num}: Cannot correct non-existent object {entry.object_number}")
    
    def get_statistics(self) -> Dict:
        """Generate statistics about the inventory."""
        active = sum(1 for e in self.entries.values() if e.status == "active")
        withdrawn = sum(1 for e in self.entries.values() if e.status == "withdrawn")
        missing_dates = sum(1 for e in self.entries.values() if not e.date)
        missing_links = sum(1 for e in self.entries.values() if not e.link)
        
        return {
            'total_entries': len(self.entries),
            'active_entries': active,
            'withdrawn_entries': withdrawn,
            'missing_dates': missing_dates,
            'missing_links': missing_links,
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings)
        }
    
    def save_standardized(self, include_withdrawn: bool = False) -> None:
        """Save standardized inventory to TSV file."""
        entries_to_save = [
            e for e in self.entries.values()
            if include_withdrawn or e.status == "active"
        ]
        
        entries_to_save.sort(key=lambda e: e.object_number)
        
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['date', 'title', 'object_number', 'link', 'status', 'notes']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                
                writer.writeheader()
                for entry in entries_to_save:
                    writer.writerow(asdict(entry))
            
            print(f"✓ Standardized inventory saved to: {self.output_file}")
            
        except Exception as e:
            self.errors.append(f"Error saving file: {str(e)}")
            raise
    
    def save_checksums(self) -> None:
        """Save checksums for future verification."""
        self.current_checksums.timestamp = datetime.now().isoformat()
        
        try:
            with open(self.checksum_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_checksums.to_dict(), f, indent=2)
            
            print(f"✓ Checksums saved to: {self.checksum_file}")
            
        except Exception as e:
            self.errors.append(f"Error saving checksums: {str(e)}")
    
    def save_audit_log(self) -> None:
        """Save audit log of all changes."""
        log_file = self.output_file.with_stem(f"{self.output_file.stem}_audit")
        
        try:
            with open(log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['timestamp', 'object_number', 'action', 'details'],
                    delimiter='\t'
                )
                writer.writeheader()
                
                for record in self.history:
                    writer.writerow({
                        'timestamp': datetime.now().isoformat(),
                        'object_number': record.get('object_number', ''),
                        'action': record.get('action', ''),
                        'details': str(record)
                    })
            
            print(f"✓ Audit log saved to: {log_file}")
            
        except Exception as e:
            self.errors.append(f"Error saving audit log: {str(e)}")
    
    def save_checksum_verification_report(self) -> None:
        """Save detailed checksum verification report."""
        report_file = self.output_file.with_stem(f"{self.output_file.stem}_checksum_report")
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("CHECKSUM VERIFICATION REPORT\n")
                f.write("="*70 + "\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Input file: {self.input_file}\n\n")
                
                # File-level verification
                f.write("FILE-LEVEL INTEGRITY\n")
                f.write("-"*70 + "\n")
                f.write(f"Current file SHA256:  {self.current_checksums.file_checksum}\n")
                
                if self.previous_checksums:
                    f.write(f"Previous file SHA256: {self.previous_checksums.file_checksum}\n")
                    if self.current_checksums.file_checksum == self.previous_checksums.file_checksum:
                        f.write("✓ File has NOT changed (checksums match)\n")
                    else:
                        f.write("✗ File HAS changed (checksums differ)\n")
                else:
                    f.write("(No previous checksum to compare)\n")
                
                # Entry-level analysis
                f.write(f"\nRow count: {self.current_checksums.row_count}\n")
                if self.previous_checksums:
                    f.write(f"Previous row count: {self.previous_checksums.row_count}\n")
                    if self.current_checksums.row_count != self.previous_checksums.row_count:
                        f.write(f"⚠ Row count changed: {self.previous_checksums.row_count} → {self.current_checksums.row_count}\n")
                
                # Entry-level verification
                f.write("\nENTRY-LEVEL ANALYSIS\n")
                f.write("-"*70 + "\n")
                
                if self.previous_checksums:
                    unchanged = 0
                    changed = 0
                    new_entries = 0
                    removed_entries = 0
                    
                    for obj_num, current_checksum in self.current_checksums.entry_checksums.items():
                        if obj_num not in self.previous_checksums.entry_checksums:
                            new_entries += 1
                        elif current_checksum == self.previous_checksums.entry_checksums[obj_num]:
                            unchanged += 1
                        else:
                            changed += 1
                            f.write(f"Changed: {obj_num}\n")
                            f.write(f"  Previous: {self.previous_checksums.entry_checksums[obj_num]}\n")
                            f.write(f"  Current:  {current_checksum}\n")
                    
                    for obj_num in self.previous_checksums.entry_checksums:
                        if obj_num not in self.current_checksums.entry_checksums:
                            removed_entries += 1
                    
                    f.write("\nSUMMARY:\n")
                    f.write(f"  Unchanged entries: {unchanged}\n")
                    f.write(f"  Changed entries:   {changed}\n")
                    f.write(f"  New entries:       {new_entries}\n")
                    f.write(f"  Removed entries:   {removed_entries}\n")
                else:
                    f.write(f"Total entries: {len(self.current_checksums.entry_checksums)}\n")
                    f.write("(No previous checksums to compare)\n")
            
            print(f"✓ Checksum report saved to: {report_file}")
            
        except Exception as e:
            self.errors.append(f"Error saving checksum report: {str(e)}")
    
    def save_error_report(self) -> None:
        """Save error and warning report."""
        error_file = self.output_file.with_stem(f"{self.output_file.stem}_errors")
        
        if not self.errors and not self.warnings:
            return
        
        try:
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write("VALIDATION REPORT\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Input file: {self.input_file}\n\n")
                
                if self.warnings:
                    f.write(f"WARNINGS ({len(self.warnings)}):\n")
                    f.write("-"*70 + "\n")
                    for warning in self.warnings:
                        f.write(f"⚠ {warning}\n\n")
                
                if self.errors:
                    f.write(f"\nERRORS ({len(self.errors)}):\n")
                    f.write("-"*70 + "\n")
                    for error in self.errors:
                        f.write(f"✗ {error}\n")
            
            print(f"✓ Error/warning report saved to: {error_file}")
            
        except Exception as e:
            print(f"Error saving error report: {str(e)}")
    
    def print_summary(self) -> None:
        """Print summary of standardization."""
        stats = self.get_statistics()
        
        print("\n" + "="*70)
        print("MUSEUM INVENTORY STANDARDIZATION SUMMARY")
        print("="*70)
        print(f"Input file:         {self.input_file}")
        print(f"Output file:        {self.output_file}")
        print(f"Checksum file:      {self.checksum_file}")
        print(f"\nStatistics:")
        print(f"  Total entries:      {stats['total_entries']}")
        print(f"  Active entries:     {stats['active_entries']}")
        print(f"  Withdrawn entries:  {stats['withdrawn_entries']}")
        print(f"  Missing dates:      {stats['missing_dates']}")
        print(f"  Missing links:      {stats['missing_links']}")
        print(f"  Errors:             {stats['total_errors']}")
        print(f"  Warnings:           {stats['total_warnings']}")
        
        print(f"\nChecksum Information:")
        print(f"  File SHA256:        {self.current_checksums.file_checksum[:16]}...")
        print(f"  Entries tracked:    {len(self.current_checksums.entry_checksums)}")
        
        if self.previous_checksums:
            if self.current_checksums.file_checksum == self.previous_checksums.file_checksum:
                print(f"  File status:        ✓ Unchanged")
            else:
                print(f"  File status:        ⚠ Modified")
        
        if self.warnings:
            print(f"\nFirst 3 warnings:")
            for warning in self.warnings[:3]:
                print(f"  ⚠ {warning[:60]}...")
        
        print("="*70 + "\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python script.py <input.tsv> [output.tsv] [checksum_file.json]")
        print("\nExample: python script.py museum_inventory.tsv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    checksum_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        standardizer = MuseumInventoryStandardizer(input_file, output_file, checksum_file)
        
        # Load and verify previous checksums
        standardizer.load_previous_checksums()
        
        # Load inventory
        standardizer.load_inventory()
        
        # Verify file integrity
        standardizer.verify_file_integrity()
        
        # Save results
        standardizer.save_standardized(include_withdrawn=False)
        standardizer.save_checksums()
        standardizer.save_audit_log()
        standardizer.save_checksum_verification_report()
        standardizer.save_error_report()
        standardizer.print_summary()
        
    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Key Checksum Features

### 1. **File-Level Checksums**
```python
# SHA256 of entire file
file_checksum = ChecksumManager.compute_file_checksum(Path("inventory.tsv"))
```

### 2. **Entry-Level Checksums**
```python
# SHA256 of standardized entry
entry_dict = {"date": "2024-01-15", "title": "Vase", ...}
entry_checksum = ChecksumManager.compute_entry_checksum(entry_dict)
```

### 3. **Persistent Storage**
```json
{
  "file_path": "museum_inventory.tsv",
  "file_checksum": "a1b2c3d4...",
  "entry_checksums": {
    "VAS.001": "e5f6g7h8...",
    "COIN.042": "i9j0k1l2..."
  },
  "timestamp": "2024-01-20T10:30:00.123456",
  "row_count": 150
}
```

### 4. **Verification Reports**
- Detects file modifications
- Identifies changed entries
- Tracks row count changes
- Flags new/removed entries

### Usage

```bash
# First run (creates checksums)
python script.py museum_inventory.tsv

# Second run (verifies checksums)
python script.py museum_inventory.tsv
```

## Output Files

1. `*_standardized.tsv` - Clean data
2. `*_checksums.json` - Checksum records
3. `*_checksum_report.txt` - Verification report
4. `*_audit.tsv` - Change history
5. `*_errors.txt` - Validation issues

This approach ensures data integrity and helps detect accidental or malicious modifications to source data.
