# Museum Inventory Standardizer with Checksum Verification

Here's an enhanced version incorporating checksums for data integrity verification:

```python
#!/usr/bin/env python3
"""
Museum Inventory Standardizer with Checksum Verification

Standardizes museum inventory TSV files with integrity verification
using checksums to detect source data changes.
"""

import csv
import sys
import re
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse


class ChecksumManager:
    """Manages checksums for data integrity verification."""
    
    HASH_ALGORITHM = 'sha256'
    
    def __init__(self, checksum_file: Optional[Path] = None):
        """
        Initialize checksum manager.
        
        Args:
            checksum_file: Path to store/load checksums (JSON format)
        """
        self.checksum_file = checksum_file
        self.checksums: Dict[str, Dict] = {}
        self.current_checksums: Dict[str, str] = {}
        
        if checksum_file and checksum_file.exists():
            self.load_checksums()
    
    def compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA256 hash of entire file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex digest of file hash
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def compute_row_hash(self, row: Dict, field_order: List[str]) -> str:
        """
        Compute hash of a single row for change detection.
        
        Args:
            row: Row dictionary
            field_order: Ordered list of field names to include
            
        Returns:
            Hex digest of row hash
        """
        # Create canonical representation of row
        canonical = '|'.join(
            str(row.get(field, '')) for field in field_order
        )
        
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    def compute_dataset_hash(self, entries: Dict) -> str:
        """
        Compute hash of entire dataset for global integrity check.
        
        Args:
            entries: Dictionary of all entries
            
        Returns:
            Hex digest of dataset hash
        """
        # Sort by object number for consistency
        canonical = ''.join(
            entries[key].object_number + entries[key].title + entries[key].date
            for key in sorted(entries.keys())
        )
        
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    def save_checksums(self, file_path: Path, metadata: Dict = None):
        """
        Save checksums to file in JSON format.
        
        Args:
            file_path: Path to save checksums
            metadata: Optional metadata to include
        """
        data = {
            'algorithm': self.HASH_ALGORITHM,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {},
            'checksums': self.current_checksums
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load_checksums(self):
        """Load checksums from file."""
        if not self.checksum_file or not self.checksum_file.exists():
            return
        
        try:
            with open(self.checksum_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.checksums = data.get('checksums', {})
        except Exception as e:
            print(f"Warning: Could not load checksums: {e}")
    
    def verify_file_integrity(self, file_path: Path, stored_hash: str) -> Tuple[bool, str]:
        """
        Verify file hasn't changed since last processing.
        
        Args:
            file_path: Path to file to verify
            stored_hash: Previously computed hash
            
        Returns:
            Tuple of (is_valid, message)
        """
        current_hash = self.compute_file_hash(file_path)
        
        if current_hash == stored_hash:
            return True, "File integrity verified - no changes detected"
        else:
            return False, f"File changed since last processing"
    
    def store_checksum(self, key: str, hash_value: str, metadata: Dict = None):
        """
        Store a checksum with optional metadata.
        
        Args:
            key: Unique identifier for the checksum
            hash_value: Hash value to store
            metadata: Optional metadata
        """
        self.current_checksums[key] = {
            'hash': hash_value,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
    
    def compare_checksums(self, key: str, current_hash: str) -> Tuple[bool, Optional[str]]:
        """
        Compare current checksum with stored one.
        
        Args:
            key: Unique identifier
            current_hash: Current hash value
            
        Returns:
            Tuple of (is_changed, old_hash_or_none)
        """
        if key not in self.checksums:
            return None, None  # No previous checksum
        
        old_entry = self.checksums[key]
        if isinstance(old_entry, dict):
            old_hash = old_entry.get('hash')
        else:
            old_hash = old_entry
        
        is_changed = current_hash != old_hash
        return is_changed, old_hash if is_changed else None


class InventoryEntry:
    """Represents a single inventory entry with checksum tracking."""
    
    def __init__(self, date: str, title: str, object_number: str, link: str):
        self.date = date
        self.title = title
        self.object_number = object_number
        self.link = link
        self.is_withdrawn = False
        self.correction_history = []
        self.row_hash: Optional[str] = None  # Hash of original row
        self.field_hashes: Dict[str, str] = {}  # Individual field hashes
    
    def compute_field_hashes(self):
        """Compute hashes for individual fields."""
        self.field_hashes = {
            'date': hashlib.sha256(self.date.encode()).hexdigest(),
            'title': hashlib.sha256(self.title.encode()).hexdigest(),
            'object_number': hashlib.sha256(self.object_number.encode()).hexdigest(),
            'link': hashlib.sha256(self.link.encode()).hexdigest(),
        }
    
    def mark_withdrawn(self):
        """Mark entry as withdrawn from collection."""
        self.is_withdrawn = True
    
    def add_correction(self, field: str, old_value: str, new_value: str):
        """Record a correction made to this entry."""
        self.correction_history.append({
            'field': field,
            'old_value': old_value,
            'old_hash': hashlib.sha256(old_value.encode()).hexdigest(),
            'new_value': new_value,
            'new_hash': hashlib.sha256(new_value.encode()).hexdigest(),
            'timestamp': datetime.now().isoformat()
        })
    
    def to_dict(self) -> Dict:
        """Convert entry to dictionary."""
        return {
            'date': self.date,
            'title': self.title,
            'object_number': self.object_number,
            'link': self.link,
            'is_withdrawn': self.is_withdrawn
        }


class ChecksumVerificationReport:
    """Generates verification reports."""
    
    def __init__(self):
        self.file_integrity_checks: List[Dict] = []
        self.field_changes: List[Dict] = []
        self.entry_changes: List[Dict] = []
        self.dataset_changes: List[Dict] = []
    
    def add_file_check(self, file_name: str, is_valid: bool, message: str):
        """Record file integrity check result."""
        self.file_integrity_checks.append({
            'file': file_name,
            'is_valid': is_valid,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def add_field_change(self, object_number: str, field: str, 
                        old_hash: str, new_hash: str, change_detected: bool):
        """Record field-level change detection."""
        self.field_changes.append({
            'object_number': object_number,
            'field': field,
            'old_hash': old_hash,
            'new_hash': new_hash,
            'changed': change_detected,
            'timestamp': datetime.now().isoformat()
        })
    
    def add_entry_change(self, object_number: str, old_hash: str, new_hash: str):
        """Record entry-level change."""
        self.entry_changes.append({
            'object_number': object_number,
            'old_hash': old_hash,
            'new_hash': new_hash,
            'timestamp': datetime.now().isoformat()
        })
    
    def add_dataset_change(self, old_hash: str, new_hash: str, change_count: int):
        """Record dataset-level change."""
        self.dataset_changes.append({
            'old_hash': old_hash,
            'new_hash': new_hash,
            'changes_detected': change_count,
            'timestamp': datetime.now().isoformat()
        })
    
    def to_dict(self) -> Dict:
        """Convert report to dictionary."""
        return {
            'file_integrity': self.file_integrity_checks,
            'field_changes': self.field_changes,
            'entry_changes': self.entry_changes,
            'dataset_changes': self.dataset_changes,
            'summary': {
                'total_file_checks': len(self.file_integrity_checks),
                'valid_files': sum(1 for c in self.file_integrity_checks if c['is_valid']),
                'field_changes_detected': len([f for f in self.field_changes if f['changed']]),
                'entry_changes_detected': len(self.entry_changes),
                'dataset_changes_detected': len(self.dataset_changes)
            }
        }


class InventoryStandardizer:
    """Main standardizer class with checksum verification."""
    
    # Validation patterns
    OBJECT_NUMBER_PATTERN = re.compile(r'^[A-Z0-9\.\-/]+$')
    URL_PATTERN = re.compile(
        r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
    )
    DATE_PATTERNS = [
        r'^\d{4}-\d{2}-\d{2}$',
        r'^\d{2}/\d{2}/\d{4}$',
        r'^\d{4}/\d{2}/\d{2}$',
    ]
    
    def __init__(self, input_file: str, output_file: str = None, 
                 log_file: str = None, checksum_file: str = None,
                 verify_against_previous: bool = False):
        """
        Initialize standardizer with checksum support.
        
        Args:
            input_file: Path to input TSV file
            output_file: Path to output TSV file
            log_file: Path to log file
            checksum_file: Path to checksum file
            verify_against_previous: Whether to verify against previous run
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file or f"{input_file.rsplit('.', 1)[0]}_standardized.tsv")
        self.log_file = Path(log_file or f"{input_file.rsplit('.', 1)[0]}_log.txt")
        self.checksum_file = Path(checksum_file or f"{input_file.rsplit('.', 1)[0]}_checksums.json")
        self.verify_against_previous = verify_against_previous
        
        self.entries: Dict[str, InventoryEntry] = {}
        self.issues: List[Dict] = []
        self.corrections_log: List[Dict] = []
        
        self.checksum_manager = ChecksumManager(self.checksum_file if verify_against_previous else None)
        self.verification_report = ChecksumVerificationReport()
        
        self.source_file_hash: Optional[str] = None
        self.previous_source_hash: Optional[str] = None
    
    def validate_date(self, date_str: str) -> Tuple[bool, str]:
        """Validate and standardize date to ISO format."""
        date_str = date_str.strip()
        
        if not date_str:
            return False, "Empty date"
        
        if re.match(self.DATE_PATTERNS[0], date_str):
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return True, date_str
            except ValueError:
                return False, f"Invalid ISO date: {date_str}"
        
        if re.match(self.DATE_PATTERNS[1], date_str):
            try:
                dt = datetime.strptime(date_str, '%m/%d/%Y')
                return True, dt.strftime('%Y-%m-%d')
            except ValueError:
                return False, f"Invalid MM/DD/YYYY date: {date_str}"
        
        if re.match(self.DATE_PATTERNS[2], date_str):
            try:
                dt = datetime.strptime(date_str, '%Y/%m/%d')
                return True, dt.strftime('%Y-%m-%d')
            except ValueError:
                return False, f"Invalid YYYY/MM/DD date: {date_str}"
        
        return False, f"Unrecognized date format: {date_str}"
    
    def validate_object_number(self, obj_num: str) -> Tuple[bool, str]:
        """Validate object number format."""
        obj_num = obj_num.strip()
        
        if not obj_num:
            return False, "Empty object number"
        
        if not self.OBJECT_NUMBER_PATTERN.match(obj_num):
            return False, f"Invalid characters in object number: {obj_num}"
        
        return True, ""
    
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """Validate URL format."""
        url = url.strip()
        
        if not url:
            return True, ""
        
        if not self.URL_PATTERN.match(url):
            return False, f"Invalid URL format: {url}"
        
        return True, ""
    
    def normalize_title(self, title: str) -> str:
        """Normalize title formatting."""
        title = title.strip()
        title = ' '.join(title.split())
        return title
    
    def parse_input_file(self) -> bool:
        """Parse input TSV file with checksum computation."""
        if not self.input_file.exists():
            self.issues.append({
                'type': 'error',
                'message': f"Input file not found: {self.input_file}"
            })
            return False
        
        # Compute source file hash
        self.source_file_hash = self.checksum_manager.compute_file_hash(self.input_file)
        
        # Check if file has changed since last run
        if self.verify_against_previous:
            previous_hash = self.checksum_manager.checksums.get('source_file_hash', {}).get('hash')
            if previous_hash:
                is_changed, old_hash = self.checksum_manager.compare_checksums(
                    'source_file_hash', 
                    self.source_file_hash
                )
                self.previous_source_hash = old_hash
                
                message = f"Source file has {'CHANGED' if is_changed else 'NOT changed'} since last processing"
                if is_changed:
                    self.verification_report.add_file_check(
                        str(self.input_file), False, message
                    )
                else:
                    self.verification_report.add_file_check(
                        str(self.input_file), True, message
                    )
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    self.issues.append({
                        'type': 'error',
                        'message': 'Empty file or missing headers'
                    })
                    return False
                
                required_cols = {'date', 'title', 'object_number', 'link'}
                if not required_cols.issubset(set(reader.fieldnames)):
                    missing = required_cols - set(reader.fieldnames)
                    self.issues.append({
                        'type': 'error',
                        'message': f"Missing required columns: {', '.join(missing)}"
                    })
                    return False
                
                row_num = 1
                for row in reader:
                    row_num += 1
                    self._process_row(row, row_num, required_cols)
            
            return True
        
        except UnicodeDecodeError as e:
            self.issues.append({
                'type': 'error',
                'message': f"File encoding error: {e}"
            })
            return False
        except Exception as e:
            self.issues.append({
                'type': 'error',
                'message': f"Error reading file: {e}"
            })
            return False
    
    def _process_row(self, row: Dict, row_num: int, field_order: List[str]):
        """Process a single row with checksum tracking."""
        date = row.get('date', '').strip()
        title = row.get('title', '').strip()
        object_number = row.get('object_number', '').strip()
        link = row.get('link', '').strip()
        
        # Compute hash of original row
        original_row_hash = self.checksum_manager.compute_row_hash(
            row, 
            list(field_order)
        )
        
        # Check for withdrawal markers
        if title.lower() in ['withdrawn', 'deaccessioned', '[withdrawn]', '[deaccessioned]']:
            if object_number in self.entries:
                self.entries[object_number].mark_withdrawn()
                self.corrections_log.append({
                    'row': row_num,
                    'object_number': object_number,
                    'action': 'marked_withdrawn',
                    'original_row_hash': original_row_hash
                })
            return
        
        # Validate and normalize data
        date_valid, date_result = self.validate_date(date)
        if not date_valid:
            self.issues.append({
                'type': 'warning',
                'row': row_num,
                'object_number': object_number,
                'message': date_result
            })
            date = ""
        else:
            date = date_result
        
        obj_valid, obj_error = self.validate_object_number(object_number)
        if not obj_valid:
            self.issues.append({
                'type': 'error',
                'row': row_num,
                'message': f"{obj_error} - Row skipped"
            })
            return
        
        url_valid, url_error = self.validate_url(link)
        if not url_valid:
            self.issues.append({
                'type': 'warning',
                'row': row_num,
                'object_number': object_number,
                'message': url_error
            })
            link = ""
        
        title = self.normalize_title(title)
        
        # Handle duplicates (corrections)
        if object_number in self.entries:
            existing = self.entries[object_number]
            changes = []
            
            if date and date != existing.date:
                changes.append(('date', existing.date, date))
                existing.date = date
            
            if title != existing.title:
                changes.append(('title', existing.title, title))
                existing.title = title
            
            if link and link != existing.link:
                changes.append(('link', existing.link, link))
                existing.link = link
            
            for field, old_val, new_val in changes:
                existing.add_correction(field, old_val, new_val)
                self.corrections_log.append({
                    'row': row_num,
                    'object_number': object_number,
                    'field': field,
                    'old_value': old_val,
                    'new_value': new_val,
                    'action': 'corrected',
                    'original_row_hash': original_row_hash
                })
        else:
            # Create new entry
            entry = InventoryEntry(date, title, object_number, link)
            entry.row_hash = original_row_hash
            entry.compute_field_hashes()
            self.entries[object_number] = entry
    
    def write_output_file(self) -> bool:
        """Write standardized entries to output file."""
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['date', 'title', 'object_number', 'link', 'is_withdrawn']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                
                writer.writeheader()
                
                for obj_num in sorted(self.entries.keys()):
                    entry = self.entries[obj_num]
                    writer.writerow(entry.to_dict())
            
            return True
        except Exception as e:
            self.issues.append({
                'type': 'error',
                'message': f"Error writing output file: {e}"
            })
            return False
    
    def write_log_file(self) -> bool:
        """Write detailed log with checksum verification results."""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("MUSEUM INVENTORY STANDARDIZATION LOG\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Input file: {self.input_file}\n")
                f.write(f"Output file: {self.output_file}\n\n")
                
                # Checksum verification section
                f.write("=" * 70 + "\n")
                f.write("CHECKSUM VERIFICATION REPORT\n")
                f.write("=" * 70 + "\n")
                f.write(f"Source file hash (SHA-256): {self.source_file_hash}\n")
                
                if self.previous_source_hash:
                    f.write(f"Previous hash: {self.previous_source_hash}\n")
                    f.write(f"Status: SOURCE DATA HAS CHANGED\n")
                else:
                    f.write("Status: No previous hash on record\n")
                
                f.write("\n")
                
                # Summary
                f.write("=" * 70 + "\n")
                f.write("SUMMARY\n")
                f.write("=" * 70 + "\n")
                f.write(f"Total entries processed: {len(self.entries)}\n")
                f.write(f"Withdrawn entries: {sum(1 for e in self.entries.values() if e.is_withdrawn)}\n")
                f.write(f"Corrections made: {sum(1 for c in self.corrections_log if c.get('action') == 'corrected')}\n")
                f.write(f"Withdrawals recorded: {sum(1 for c in self.corrections_log if c.get('action') == 'marked_withdrawn')}\n")
                f.write(f"Issues found: {len(self.issues)}\n\n")
                
                # Detailed verification results
                f.write("=" * 70 + "\n")
                f.write("VERIFICATION DETAILS\n")
                f.write("=" * 70 + "\n")
                
                for check in self.verification_report.file_integrity_checks:
                    status = "✓ VALID" if check['is_valid'] else "✗ INVALID"
                    f.write(f"\n{status}: {check['file']}\n")
                    f.write(f"   {check['message']}\n")
                
                # Issues
                if self.issues:
                    f.write("\n" + "=" * 70 + "\n")
                    f.write("ISSUES\n")
                    f.write("=" * 70 + "\n")
                    for i, issue in enumerate(self.issues, 1):
                        f.write(f"\n{i}. [{issue.get('type', 'unknown').upper()}]")
                        if 'row' in issue:
                            f.write(f" Row {issue['row']}")
                        if 'object_number' in issue:
                            f.write(f" ({issue['object_number']})")
                        f.write(f"\n   {issue['message']}\n")
                
                # Corrections with checksums
                if self.corrections_log:
                    f.write("\n" + "=" * 70 + "\n")
                    f.write("CORRECTIONS LOG\n")
                    f.write("=" * 70 + "\n")
                    for i, correction in enumerate(self.corrections_log, 1):
                        f.write(f"\n{i}. Object #{correction['object_number']}")
                        if 'field' in correction:
                            f.write(f" - {correction['field'].upper()}")
                        f.write(f"\n   Row: {correction['row']}")
                        if 'old_value' in correction:
                            f.write(f"\n   Old: {correction['old_value']}")
                            f.write(f"\n   New: {correction['new_value']}\n")
                        if 'original_row_hash' in correction:
                            f.write(f"   Original row hash: {correction['original_row_hash']}\n")
            
            return True
        except Exception as e:
            print(f"Error writing log file: {e}")
            return False
    
    def write_verification_report(self, report_file: Optional[Path] = None) -> bool:
        """Write detailed verification report in JSON format."""
        if not report_file:
            report_file = Path(str(self.log_file).replace('.txt', '_verification.json'))
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.verification_report.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error writing verification report: {e}")
            return False
    
    def save_checksums_for_next_run(self) -> bool:
        """Save checksums for verification on next run."""
        try:
            metadata = {
                'entries_count': len(self.entries),
                'corrections_count': sum(1 for c in self.corrections_log if c.get('action') == 'corrected'),
                'source_file': str(self.input_file),
                'output_file': str(self.output_file)
            }
            
            # Store source file hash
            self.checksum_manager.current_checksums['source_file_hash'] = {
                'hash': self.source_file_hash,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata
            }
            
            # Store dataset hash
            dataset_hash = self.checksum_manager.compute_dataset_hash(self.entries)
            self.checksum_manager.current_checksums['dataset_hash'] = {
                'hash': dataset_hash,
                'timestamp': datetime.now().isoformat(),
                'metadata': {'entries': len(self.entries)}
            }
            
            # Store individual entry hashes
            for obj_num, entry in self.entries.items():
                self.checksum_manager.current_checksums[f'entry_{obj_num}'] = {
                    'hash': entry.row_hash,
                    'timestamp': datetime.now().isoformat(),
                    'field_hashes': entry.field_hashes,
                    'is_withdrawn': entry.is_withdrawn
                }
            
            self.checksum_manager.save_checksums(self.checksum_file, metadata)
            return True
        except Exception as e:
            print(f"Error saving checksums: {e}")
            return False
    
    def standardize(self, verbose: bool = False, save_checksums: bool = True) -> bool:
        """
        Run the full standardization process with checksum verification.
        
        Args:
            verbose: Print detailed output
            save_checksums: Save checksums for future verification
            
        Returns:
            True if successful, False otherwise
        """
        if verbose:
            print(f"Reading input file: {self.input_file}")
        
        if not self.parse_input_file():
            return False
        
        if verbose:
            print(f"Parsed {len(self.entries)} entries")
            print(f"Source file hash: {self.source_file_hash}")
            if self.previous_source_hash:
                print(f"⚠️  Source data has changed since last run")
        
        if verbose:
            print(f"Writing output file: {self.output_file}")
        
        if not self.write_output_file():
            return False
        
        if verbose:
            print(f"Writing log file: {self.log_file}")
        
        if not self.write_log_file():
            return False
        
        if not self.write_verification_report():
            return False
        
        if save_checksums:
            if verbose:
                print(f"Saving checksums: {self.checksum_file}")
            if not self.save_checksums_for_next_run():
                return False
        
        if verbose:
            print("\n✓ Standardization complete!")
            if self.issues:
                print(f"⚠️  {len(self.issues)} issue(s) found - see log file for details")
            if self.corrections_log:
                corrections = sum(1 for c in self.corrections_log if c.get('action') == 'corrected')
                withdrawals = sum(1 for c in self.corrections_log if c.get('action') == 'marked_withdrawn')
                if corrections:
                    print(f"✓ {corrections} correction(s) applied")
                if withdrawals:
                    print(f"✓ {withdrawals} item(s) marked as withdrawn")
        
        return True


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Standardize museum inventory spreadsheets with checksum verification'
    )
    parser.add_argument('input_file', help='Input TSV file')
    parser.add_argument('-o', '--output', help='Output TSV file', default=None)
    parser.add_argument('-l', '--log', help='Log file', default=None)
    parser.add_argument('-c', '--checksums', help='Checksums file', default=None)
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser.add_argument('--verify', help='Verify against previous run', action='store_true')
    parser.add_argument('--no-save-checksums', help='Do not save checksums', action='store_true')
    
    args = parser.parse_args()
    
    standardizer = InventoryStandardizer(
        args.input_file,
        args.output,
        args.log,
        args.checksums,
        verify_against_previous=args.verify
    )
    
    success = standardizer.standardize(
        verbose=args.verbose,
        save_checksums=not args.no_save_checksums
    )
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Usage Examples

### First run - establish checksums:
```bash
python standardizer.py inventory.tsv -v
```

### Verify against previous run:
```bash
python standardizer.py inventory.tsv -v --verify
```

### View checksums from previous run:
```bash
cat inventory_checksums.json
```

### Run without saving checksums:
```bash
python standardizer.py inventory.tsv -v --no-save-checksums
```

## Sample Checksum File Output

```json
{
  "algorithm": "sha256",
  "timestamp": "2024-01-20T10:30:45.123456",
  "metadata": {
    "entries_count": 150,
    "corrections_count": 3,
    "source_file": "inventory.tsv",
    "output_file": "inventory_standardized.tsv"
  },
  "checksums": {
    "source_file_hash": {
      "hash": "a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2",
      "timestamp": "2024-01-20T10:30:45.123456",
      "metadata": {...}
    },
    "dataset_hash": {
      "hash": "q2r3s4t5u6v7w8x9y0z1a2b3c4d5e6f",
      "timestamp": "2024-01-20T10:30:45.123456",
      "metadata": {"entries": 150}
    },
    "entry_VAS.001": {
      "hash": "...",
      "field_hashes": {...}
    }
  }
}
```

## Key Features

1. **File-level checksums**: Detect if source file has changed
2. **Row-level checksums**: Track individual row integrity
3. **Field-level checksums**: Monitor specific field changes
4. **Dataset checksums**: Verify overall collection integrity
5. **Change detection**: Compare current vs. previous runs
6. **Detailed reporting**: JSON verification report with all hash comparisons
7. **Audit trail**: Complete history of all changes with checksums
8. **Data integrity**: SHA-256 hashing for cryptographic verification
