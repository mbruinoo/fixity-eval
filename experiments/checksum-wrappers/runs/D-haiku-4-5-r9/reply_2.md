# Museum Inventory Standardizer with Checksums

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory spreadsheets (.tsv format) with checksum verification.

Handles corrections and withdrawals of entries.
Supports integrity verification of source data.
"""

import csv
import argparse
import sys
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import re


class ChecksumManager:
    """Manages checksums for integrity verification."""
    
    CHECKSUM_ALGORITHMS = {
        'md5': hashlib.md5,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512,
    }
    
    def __init__(self, algorithm: str = 'sha256'):
        """
        Initialize checksum manager.
        
        Args:
            algorithm: Hash algorithm ('md5', 'sha256', 'sha512')
        """
        if algorithm not in self.CHECKSUM_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        self.algorithm = algorithm
        self.hash_func = self.CHECKSUM_ALGORITHMS[algorithm]
    
    def file_checksum(self, filepath: Path) -> str:
        """Calculate checksum of entire file."""
        hasher = self.hash_func()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def row_checksum(self, row_data: Dict) -> str:
        """Calculate checksum of a single row."""
        # Create consistent JSON representation
        row_json = json.dumps(row_data, sort_keys=True, separators=(',', ':'))
        hasher = self.hash_func()
        hasher.update(row_json.encode('utf-8'))
        return hasher.hexdigest()
    
    def line_checksum(self, line: str) -> str:
        """Calculate checksum of a raw line."""
        hasher = self.hash_func()
        hasher.update(line.encode('utf-8'))
        return hasher.hexdigest()


class InventoryEntry:
    """Represents a single inventory entry with checksum tracking."""
    
    def __init__(self, date: str, title: str, object_number: str, link: str,
                 source_checksum: Optional[str] = None):
        self.date = self._standardize_date(date)
        self.title = self._standardize_title(title)
        self.object_number = self._standardize_object_number(object_number)
        self.link = self._standardize_link(link)
        self.is_withdrawn = False
        
        # Checksum tracking
        self.source_checksum = source_checksum  # Checksum from source file
        self.current_checksum = self._calculate_checksum()
        self.checksum_verified = False
        self.modifications: List[Dict] = []  # Track all modifications
    
    @staticmethod
    def _standardize_date(date: str) -> str:
        """Convert date to ISO format (YYYY-MM-DD)."""
        date = date.strip()
        if not date:
            return ""
        
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d-%m-%Y",
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        print(f"Warning: Could not parse date '{date}'. Using original.", file=sys.stderr)
        return date
    
    @staticmethod
    def _standardize_title(title: str) -> str:
        """Clean and normalize title."""
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)
        return title
    
    @staticmethod
    def _standardize_object_number(obj_num: str) -> str:
        """Standardize object number format."""
        obj_num = obj_num.strip().upper()
        obj_num = re.sub(r'\s+', ' ', obj_num)
        return obj_num
    
    @staticmethod
    def _standardize_link(link: str) -> str:
        """Validate and clean URL."""
        link = link.strip()
        if not link:
            return ""
        
        if link and not link.startswith(('http://', 'https://', 'ftp://')):
            link = 'https://' + link
        
        return link
    
    def _calculate_checksum(self) -> str:
        """Calculate checksum of current entry state."""
        checksum_mgr = ChecksumManager()
        data = {
            'date': self.date,
            'title': self.title,
            'object_number': self.object_number,
            'link': self.link,
            'is_withdrawn': self.is_withdrawn,
        }
        return checksum_mgr.row_checksum(data)
    
    def update_field(self, field: str, value: str, reason: str = "") -> bool:
        """
        Update a field and track the change.
        
        Args:
            field: Field name (date, title, link)
            value: New value
            reason: Reason for modification
        
        Returns:
            True if update successful
        """
        old_value = getattr(self, field, None)
        
        if field == 'date':
            setattr(self, field, self._standardize_date(value))
        elif field == 'title':
            setattr(self, field, self._standardize_title(value))
        elif field == 'link':
            setattr(self, field, self._standardize_link(value))
        else:
            return False
        
        new_value = getattr(self, field)
        
        # Track modification
        self.modifications.append({
            'timestamp': datetime.now().isoformat(),
            'field': field,
            'old_value': old_value,
            'new_value': new_value,
            'reason': reason,
            'checksum_before': self.current_checksum,
        })
        
        self.current_checksum = self._calculate_checksum()
        self.modifications[-1]['checksum_after'] = self.current_checksum
        
        return True
    
    def verify_checksum(self) -> bool:
        """Verify current checksum matches source."""
        if not self.source_checksum:
            return False
        
        self.checksum_verified = (self.source_checksum == self.current_checksum)
        return self.checksum_verified
    
    def get_checksum_report(self) -> str:
        """Generate checksum verification report."""
        report = f"""
Entry: {self.object_number}
Source Checksum:  {self.source_checksum or 'N/A'}
Current Checksum: {self.current_checksum}
Verified: {self.checksum_verified}
Modifications: {len(self.modifications)}
"""
        if self.modifications:
            report += "\nModification History:\n"
            for mod in self.modifications:
                report += f"  {mod['timestamp']}: {mod['field']}\n"
                report += f"    {mod['old_value']} → {mod['new_value']}\n"
                if mod['reason']:
                    report += f"    Reason: {mod['reason']}\n"
        
        return report
    
    def to_dict(self) -> Dict:
        """Convert entry to dictionary."""
        return {
            'date': self.date,
            'title': self.title,
            'object_number': self.object_number,
            'link': self.link,
        }
    
    def __repr__(self) -> str:
        status = " [WITHDRAWN]" if self.is_withdrawn else ""
        verified = " ✓" if self.checksum_verified else " ✗" if self.source_checksum else ""
        return f"Entry({self.object_number}){status}{verified}"


class InventoryManager:
    """Manages museum inventory with checksums and integrity verification."""
    
    def __init__(self, checksum_algorithm: str = 'sha256'):
        self.entries: Dict[str, InventoryEntry] = {}
        self.checksum_mgr = ChecksumManager(checksum_algorithm)
        self.source_file_checksum: Optional[str] = None
        self.manifest: Dict = {}  # Track file-level metadata
        self.history: List[Tuple[str, str, str]] = []
    
    def add_entry(self, entry: InventoryEntry) -> None:
        """Add or update an entry."""
        self.entries[entry.object_number] = entry
        self.history.append(('ADD', entry.object_number, datetime.now().isoformat()))
    
    def load_from_tsv(self, filepath: Path, track_checksums: bool = True) -> int:
        """
        Load entries from TSV file with optional checksum tracking.
        
        Args:
            filepath: Path to TSV file
            track_checksums: Whether to calculate row checksums
        
        Returns:
            Number of entries loaded
        """
        # Calculate file checksum
        self.source_file_checksum = self.checksum_mgr.file_checksum(filepath)
        
        self.manifest = {
            'source_file': str(filepath),
            'file_checksum': self.source_file_checksum,
            'algorithm': self.checksum_mgr.algorithm,
            'loaded_at': datetime.now().isoformat(),
            'total_rows': 0,
        }
        
        count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            expected_headers = {'date', 'title', 'object_number', 'link'}
            if reader.fieldnames and not expected_headers.issubset(set(reader.fieldnames)):
                raise ValueError(f"Invalid headers. Expected: {expected_headers}")
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Calculate checksum of raw row if requested
                    row_checksum = None
                    if track_checksums:
                        row_checksum = self.checksum_mgr.row_checksum(row)
                    
                    entry = InventoryEntry(
                        date=row.get('date', ''),
                        title=row.get('title', ''),
                        object_number=row.get('object_number', ''),
                        link=row.get('link', ''),
                        source_checksum=row_checksum
                    )
                    
                    if row.get('status', '').lower() == 'withdrawn':
                        entry.is_withdrawn = True
                    
                    self.add_entry(entry)
                    count += 1
                
                except Exception as e:
                    print(f"Error on row {row_num}: {e}", file=sys.stderr)
        
        self.manifest['total_rows'] = count
        return count
    
    def save_to_tsv(self, filepath: Path, include_withdrawn: bool = False) -> int:
        """
        Save entries to standardized TSV file.
        
        Args:
            filepath: Output file path
            include_withdrawn: Whether to include withdrawn entries
        
        Returns:
            Number of entries saved
        """
        entries_to_save = [
            entry for entry in self.entries.values()
            if include_withdrawn or not entry.is_withdrawn
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['date', 'title', 'object_number', 'link', 'status']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            
            writer.writeheader()
            for entry in sorted(entries_to_save, key=lambda e: e.date or ''):
                row = entry.to_dict()
                row['status'] = 'withdrawn' if entry.is_withdrawn else 'active'
                writer.writerow(row)
        
        return len(entries_to_save)
    
    def save_manifest(self, filepath: Path) -> None:
        """Save integrity manifest as JSON."""
        manifest_data = {
            **self.manifest,
            'entries': {
                obj_num: {
                    'source_checksum': entry.source_checksum,
                    'current_checksum': entry.current_checksum,
                    'verified': entry.checksum_verified,
                    'modifications': entry.modifications,
                    'withdrawn': entry.is_withdrawn,
                }
                for obj_num, entry in self.entries.items()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        print(f"Manifest saved to {filepath}")
    
    def verify_integrity(self, manifest_filepath: Path) -> Dict:
        """
        Verify current inventory against saved manifest.
        
        Args:
            manifest_filepath: Path to saved manifest file
        
        Returns:
            Dictionary with verification results
        """
        with open(manifest_filepath, 'r') as f:
            saved_manifest = json.load(f)
        
        results = {
            'valid': True,
            'file_checksum_match': False,
            'entries_verified': 0,
            'entries_modified': 0,
            'entries_missing': [],
            'new_entries': [],
            'issues': [],
        }
        
        # Check file checksum
        if self.source_file_checksum == saved_manifest.get('file_checksum'):
            results['file_checksum_match'] = True
        else:
            results['valid'] = False
            results['issues'].append(
                f"File checksum mismatch. Original: {saved_manifest.get('file_checksum')}, "
                f"Current: {self.source_file_checksum}"
            )
        
        # Check entries
        saved_entries = saved_manifest.get('entries', {})
        
        for obj_num, saved_data in saved_entries.items():
            if obj_num not in self.entries:
                results['entries_missing'].append(obj_num)
                results['valid'] = False
            else:
                entry = self.entries[obj_num]
                if entry.source_checksum == saved_data['source_checksum']:
                    results['entries_verified'] += 1
                    entry.checksum_verified = True
                else:
                    results['entries_modified'] += 1
        
        # Check for new entries
        for obj_num in self.entries:
            if obj_num not in saved_entries:
                results['new_entries'].append(obj_num)
        
        return results
    
    def get_integrity_report(self) -> str:
        """Generate integrity report."""
        total = len(self.entries)
        verified = sum(1 for e in self.entries.values() if e.checksum_verified)
        modified = sum(1 for e in self.entries.values() if e.modifications)
        
        report = f"""
Integrity Report
================
File Checksum: {self.source_file_checksum or 'Not calculated'}
Algorithm: {self.checksum_mgr.algorithm}

Entry Status:
  Total entries: {total}
  Checksums verified: {verified}
  Modified entries: {modified}

Modified Entries:
"""
        for entry in self.entries.values():
            if entry.modifications:
                report += f"\n  {entry.object_number}:\n"
                for mod in entry.modifications:
                    report += f"    - {mod['timestamp']}: {mod['field']} changed\n"
        
        return report
    
    def export_audit_trail(self, filepath: Path) -> None:
        """Export full audit trail including checksums."""
        audit_data = {
            'export_timestamp': datetime.now().isoformat(),
            'source_file_checksum': self.source_file_checksum,
            'algorithm': self.checksum_mgr.algorithm,
            'entries': []
        }
        
        for entry in self.entries.values():
            audit_data['entries'].append({
                'object_number': entry.object_number,
                'source_checksum': entry.source_checksum,
                'current_checksum': entry.current_checksum,
                'checksum_verified': entry.checksum_verified,
                'data': entry.to_dict(),
                'modifications': entry.modifications,
            })
        
        with open(filepath, 'w') as f:
            json.dump(audit_data, f, indent=2)
        
        print(f"Audit trail exported to {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory with checksum verification'
    )
    parser.add_argument('input', type=Path, help='Input TSV file')
    parser.add_argument('-o', '--output', type=Path, help='Output TSV file')
    parser.add_argument('-m', '--manifest', type=Path, help='Save/load manifest file')
    parser.add_argument('-a', '--audit', type=Path, help='Export audit trail')
    parser.add_argument('-v', '--verify', type=Path, help='Verify against manifest file')
    parser.add_argument('--checksum-algo', choices=['md5', 'sha256', 'sha512'],
                       default='sha256', help='Checksum algorithm')
    parser.add_argument('-r', '--report', action='store_true', help='Show integrity report')
    parser.add_argument('--correct', metavar='OBJECT_NUM', help='Correct an entry')
    parser.add_argument('--title', metavar='TITLE', help='New title')
    parser.add_argument('--date', metavar='DATE', help='New date')
    parser.add_argument('--link', metavar='LINK', help='New link')
    parser.add_argument('--reason', metavar='REASON', help='Reason for correction')
    parser.add_argument('--include-withdrawn', action='store_true',
                       help='Include withdrawn entries in output')
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = InventoryManager(checksum_algorithm=args.checksum_algo)
    
    # Load inventory
    print(f"Loading inventory from {args.input}...")
    count = manager.load_from_tsv(args.input, track_checksums=True)
    print(f"Loaded {count} entries")
    print(f"File checksum ({args.checksum_algo}): {manager.source_file_checksum}")
    
    # Handle verification against manifest
    if args.verify:
        print(f"\nVerifying against manifest: {args.verify}")
        results = manager.verify_integrity(args.verify)
        
        print(f"  File checksum match: {results['file_checksum_match']}")
        print(f"  Entries verified: {results['entries_verified']}")
        print(f"  Entries modified: {results['entries_modified']}")
        print(f"  Entries missing: {len(results['entries_missing'])}")
        print(f"  New entries: {len(results['new_entries'])}")
        
        if results['issues']:
            print("\n  Issues found:")
            for issue in results['issues']:
                print(f"    - {issue}")
        
        if not results['valid']:
            print("\n⚠️  WARNING: Integrity verification FAILED")
            sys.exit(1)
        else:
            print("\n✓ Integrity verification PASSED")
    
    # Handle corrections
    if args.correct:
        corrections = {}
        if args.title:
            corrections['title'] = args.title
        if args.date:
            corrections['date'] = args.date
        if args.link:
            corrections['link'] = args.link
        
        if corrections:
            entry = manager.entries.get(args.correct)
            if entry:
                for field, value in corrections.items():
                    entry.update_field(field, value, reason=args.reason or "Manual correction")
                print(f"Corrected {args.correct}")
                print(f"  Source checksum: {entry.source_checksum}")
                print(f"  Current checksum: {entry.current_checksum}")
            else:
                print(f"Error: {args.correct} not found", file=sys.stderr)
    
    # Show report
    if args.report:
        print(manager.get_integrity_report())
    
    # Save output
    if args.output:
        count = manager.save_to_tsv(args.output, include_withdrawn=args.include_withdrawn)
        print(f"\nSaved {count} entries to {args.output}")
    
    # Save manifest
    if args.manifest:
        manager.save_manifest(args.manifest)
    
    # Export audit trail
    if args.audit:
        manager.export_audit_trail(args.audit)


if __name__ == '__main__':
    main()
```

## Usage Examples

```bash
# Initial load and save manifest
python museum_inventory.py inventory.tsv -o output.tsv -m manifest.json

# Verify integrity against manifest
python museum_inventory.py inventory.tsv --verify manifest.json -r

# Make correction and export audit trail
python museum_inventory.py inventory.tsv -o output.tsv \
    --correct "OBJ-2024-001" --title "Updated Title" \
    --reason "Spelling correction" \
    --audit audit.json

# Use different checksum algorithm
python museum_inventory.py inventory.tsv --checksum-algo sha512 -m manifest.json
```

## Output Files

### manifest.json
```json
{
  "source_file": "inventory.tsv",
  "file_checksum": "a3f8d9e2c1b4...",
  "algorithm": "sha256",
  "loaded_at": "2024-01-15T10:30:45.123456",
  "total_rows": 100,
  "entries": {
    "OBJ-2024-001": {
      "source_checksum": "f7e9c2d1a4...",
      "current_checksum": "f7e9c2d1a4...",
      "verified": true,
      "modifications": [],
      "withdrawn": false
    }
  }
}
```

### audit.json
```json
{
  "export_timestamp": "2024-01-15T11:00:00",
  "source_file_checksum": "a3f8d9e2c1b4...",
  "algorithm": "sha256",
  "entries": [
    {
      "object_number": "OBJ-2024-001",
      "source_checksum": "f7e9c2d1a4...",
      "current_checksum": "a1b2c3d4e5...",
      "checksum_verified": false,
      "data": {
        "date": "2024-01-15",
        "title": "Updated Title",
        "object_number": "OBJ-2024-001",
        "link": "https://museum.org/vase"
      },
      "modifications": [
        {
          "timestamp": "2024-01-15T10:45:30",
          "field": "title",
          "old_value": "Ancient Vase",
          "new_value": "Updated Title",
          "reason": "Spelling correction",
          "checksum_before": "f7e9c2d1a4...",
          "checksum_after": "a1b2c3d4e5..."
        }
      ]
    }
  ]
}
```

## Key Features

- ✅ **File-level checksums**: Detect if source file changed
- ✅ **Row-level checksums**: Track individual entry integrity
- ✅ **Modification tracking**: Complete audit trail with timestamps
- ✅ **Multiple algorithms**: MD5, SHA256, SHA512
- ✅ **Manifest generation**: Save integrity state
- ✅ **Verification**: Compare current state against saved manifest
- ✅ **Audit trails**: Export complete change history
- ✅ **Checksum comparison**: Instantly detect modifications
- ✅ **Before/after checksums**: Track what changed at each step
