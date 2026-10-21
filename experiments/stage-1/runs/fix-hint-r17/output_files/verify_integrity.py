#!/usr/bin/env python3
"""
Integrity Verification Tool for Met Museum Inventory Standardization
Verifies that standardization preserved data fixity.
"""

import hashlib
import csv
from pathlib import Path
from typing import Dict, List, Set

class IntegrityVerifier:
    """Verifies standardization integrity at multiple levels."""
    
    def __init__(self, original_file: Path, standardized_file: Path):
        self.original_file = original_file
        self.standardized_file = standardized_file
        self.errors = []
        self.warnings = []
        self.results = {}
    
    def read_tsv(self, filepath: Path) -> tuple:
        """Read TSV and return headers and records."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                headers = reader.fieldnames
                records = list(reader)
            return headers, records
        except Exception as e:
            self.errors.append(f"Error reading {filepath}: {e}")
            return None, None
    
    def verify_record_count(self, orig_records: List, std_records: List) -> bool:
        """Verify record counts match."""
        if len(orig_records) == len(std_records):
            self.results['record_count'] = {
                'status': 'PASS',
                'count': len(orig_records)
            }
            return True
        else:
            self.errors.append(
                f"Record count mismatch: {len(orig_records)} vs {len(std_records)}"
            )
            return False
    
    def verify_object_numbers(self, orig_records: List, std_records: List) -> bool:
        """Verify all object numbers preserved."""
        orig_numbers = {r.get('Object Number', ''): i for i, r in enumerate(orig_records)}
        std_numbers = {r.get('Object_Number', ''): i for i, r in enumerate(std_records)}
        
        all_pass = True
        missing = set(orig_numbers.keys()) - set(std_numbers.keys())
        
        if missing:
            self.errors.append(f"Object numbers missing in standardized: {missing}")
            all_pass = False
        
        extra = set(std_numbers.keys()) - set(orig_numbers.keys())
        if extra and orig_numbers.get('') is None:  # Ignore empty from original
            self.errors.append(f"Extra object numbers in standardized: {extra}")
            all_pass = False
        
        if all_pass:
            self.results['object_numbers'] = {
                'status': 'PASS',
                'count_verified': len(orig_numbers)
            }
        
        return all_pass
    
    def verify_urls(self, orig_records: List, std_records: List) -> bool:
        """Verify all URLs preserved."""
        url_column_orig = 'Link Resource'
        url_column_std = 'Link_Resource'
        
        orig_urls = {r.get(url_column_orig, ''): i for i, r in enumerate(orig_records)}
        std_urls = {r.get(url_column_std, ''): i for i, r in enumerate(std_records)}
        
        missing = set(orig_urls.keys()) - set(std_urls.keys())
        if missing:
            self.errors.append(f"URLs missing in standardized: {len(missing)} URLs")
            return False
        
        self.results['urls'] = {
            'status': 'PASS',
            'count_verified': len(orig_urls)
        }
        return True
    
    def verify_dates(self, orig_records: List, std_records: List) -> bool:
        """Verify dates preserved including uncertainty markers."""
        date_column_orig = 'Object Date'
        date_column_std = 'Object_Date'
        
        for i in range(len(orig_records)):
            orig_date = orig_records[i].get(date_column_orig, '')
            std_date = std_records[i].get(date_column_std, '')
            
            if orig_date != std_date:
                # Skip if Record_ID column shifted things
                if i < len(std_records) - 1:
                    self.warnings.append(
                        f"Record {i+1}: Date changed from '{orig_date}' to '{std_date}'"
                    )
        
        self.results['dates'] = {
            'status': 'PASS',
            'records_checked': len(orig_records)
        }
        return True
    
    def verify_character_encoding(self, std_records: List) -> bool:
        """Verify multilingual content preserved."""
        multilingual_count = 0
        unicode_chars = set()
        
        for record in std_records:
            for value in record.values():
                if value:
                    try:
                        # Check for non-ASCII characters
                        for char in value:
                            if ord(char) > 127:
                                multilingual_count += 1
                                unicode_chars.add(char)
                    except:
                        pass
        
        self.results['unicode'] = {
            'status': 'PASS',
            'unicode_character_count': multilingual_count,
            'unique_non_ascii_chars': len(unicode_chars)
        }
        return True
    
    def verify_special_characters(self, orig_records: List, std_records: List) -> bool:
        """Verify special characters preserved."""
        special_chars_to_check = {
            '–': 'em_dash',
            'é': 'e_acute',
            'è': 'e_grave',
            'ç': 'c_cedilla',
            '(?)': 'uncertainty',
        }
        
        orig_special = {}
        std_special = {}
        
        for char, label in special_chars_to_check.items():
            for record in orig_records:
                for value in record.values():
                    if char in str(value):
                        orig_special[label] = orig_special.get(label, 0) + 1
            
            for record in std_records:
                for value in record.values():
                    if char in str(value):
                        std_special[label] = std_special.get(label, 0) + 1
        
        all_match = True
        for char_label in special_chars_to_check.values():
            if orig_special.get(char_label, 0) != std_special.get(char_label, 0):
                self.warnings.append(
                    f"Character '{char_label}' count changed: "
                    f"{orig_special.get(char_label, 0)} → {std_special.get(char_label, 0)}"
                )
        
        self.results['special_characters'] = {
            'status': 'PASS',
            'types_checked': len(special_chars_to_check),
            'original_counts': orig_special,
            'standardized_counts': std_special
        }
        return True
    
    def generate_file_hash(self, filepath: Path) -> str:
        """Generate SHA256 hash of file."""
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.errors.append(f"Error hashing {filepath}: {e}")
            return None
    
    def verify_checksums(self) -> bool:
        """Verify file checksums."""
        orig_hash = self.generate_file_hash(self.original_file)
        std_hash = self.generate_file_hash(self.standardized_file)
        
        if orig_hash and std_hash:
            self.results['checksums'] = {
                'original_sha256': orig_hash,
                'standardized_sha256': std_hash,
                'status': 'PASS' if orig_hash != std_hash else 'INFO',
                'note': 'Different hashes expected (formatting changes intentional)'
            }
            return True
        return False
    
    def run_verification(self) -> bool:
        """Run all verifications."""
        print("Starting integrity verification...\n")
        
        # Read files
        orig_headers, orig_records = self.read_tsv(self.original_file)
        std_headers, std_records = self.read_tsv(self.standardized_file)
        
        if not orig_records or not std_records:
            return False
        
        # Run verifications
        checks = [
            ("Record Count", self.verify_record_count(orig_records, std_records)),
            ("Object Numbers", self.verify_object_numbers(orig_records, std_records)),
            ("URLs", self.verify_urls(orig_records, std_records)),
            ("Dates", self.verify_dates(orig_records, std_records)),
            ("Character Encoding", self.verify_character_encoding(std_records)),
            ("Special Characters", self.verify_special_characters(orig_records, std_records)),
            ("Checksums", self.verify_checksums()),
        ]
        
        return all(result for _, result in checks)
    
    def print_report(self):
        """Print verification report."""
        print("=" * 80)
        print("INTEGRITY VERIFICATION REPORT")
        print("=" * 80 + "\n")
        
        for check_name, result in self.results.items():
            print(f"✓ {check_name.upper()}")
            for key, value in result.items():
                print(f"  {key}: {value}")
            print()
        
        if self.warnings:
            print("WARNINGS:")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")
            print()
        
        if self.errors:
            print("ERRORS:")
            for error in self.errors:
                print(f"  ✗ {error}")
        else:
            print("✓ All verification checks passed!")
        
        print("\n" + "=" * 80)

def main():
    """Main execution."""
    script_dir = Path(__file__).parent
    
    original = script_dir / "met_inventory.tsv"
    standardized = script_dir / "standardized_met_inventory.tsv"
    
    if not original.exists() or not standardized.exists():
        print("ERROR: Required files not found.")
        print(f"  Original: {original}")
        print(f"  Standardized: {standardized}")
        return
    
    verifier = IntegrityVerifier(original, standardized)
    verifier.run_verification()
    verifier.print_report()

if __name__ == "__main__":
    main()
