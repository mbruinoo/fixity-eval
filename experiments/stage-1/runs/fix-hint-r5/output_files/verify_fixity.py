#!/usr/bin/env python3
"""
TSV Fixity Verification Script
Verifies the integrity of the standardized Met Museum inventory file against checksums.
"""

import csv
import hashlib
import json
from pathlib import Path


class TSVVerifier:
    def __init__(self, tsv_path: str, checksums_path: str):
        self.tsv_path = Path(tsv_path)
        self.checksums_path = Path(checksums_path)
        self.checksums = None
        self.verification_results = {
            'overall_status': 'PASS',
            'file_checksum_match': False,
            'row_count_match': False,
            'row_checksums': []
        }
    
    def compute_hash(self, data: str) -> str:
        """Compute SHA-256 hash of data."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def load_checksums(self) -> bool:
        """Load checksum record from JSON file."""
        try:
            with open(self.checksums_path, 'r', encoding='utf-8') as f:
                self.checksums = json.load(f)
            print(f"✓ Checksums loaded from {self.checksums_path}")
            return True
        except Exception as e:
            print(f"✗ Failed to load checksums: {e}")
            return False
    
    def verify_file_checksum(self) -> bool:
        """Verify the entire output file checksum."""
        with open(self.tsv_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        computed_hash = self.compute_hash(content)
        recorded_hash = self.checksums['output_file']['sha256']
        
        if computed_hash == recorded_hash:
            print(f"✓ File checksum verified")
            print(f"  SHA-256: {computed_hash}")
            self.verification_results['file_checksum_match'] = True
            return True
        else:
            print(f"✗ File checksum MISMATCH")
            print(f"  Expected: {recorded_hash}")
            print(f"  Got:      {computed_hash}")
            self.verification_results['overall_status'] = 'FAIL'
            return False
    
    def verify_row_count(self) -> bool:
        """Verify the number of data rows matches."""
        with open(self.tsv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            row_count = sum(1 for _ in reader)
        
        recorded_count = self.checksums['output_file']['total_rows']
        
        if row_count == recorded_count:
            print(f"✓ Row count verified: {row_count} rows")
            self.verification_results['row_count_match'] = True
            return True
        else:
            print(f"✗ Row count MISMATCH")
            print(f"  Expected: {recorded_count}")
            print(f"  Got:      {row_count}")
            self.verification_results['overall_status'] = 'FAIL'
            return False
    
    def verify_row_checksums(self, sample_size: int = 10) -> bool:
        """Verify checksums of individual rows (sample)."""
        with open(self.tsv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            all_match = True
            verified_rows = []
            
            for row_num, row in enumerate(reader, start=2):
                # Standardize field names for canonical form
                standardized_row = {}
                for key, value in row.items():
                    if key is None:
                        continue
                    standard_key = key.strip().lower().replace(' ', '_')
                    standard_value = value.strip() if value else ''
                    standardized_row[standard_key] = standard_value
                
                # Compute canonical form
                canonical = json.dumps(standardized_row, sort_keys=True, 
                                     ensure_ascii=True, separators=(',', ':'))
                computed_hash = self.compute_hash(canonical)
                
                # Find recorded hash
                recorded = None
                for r in self.checksums['rows']:
                    if r['row_number'] == row_num:
                        recorded = r
                        break
                
                if recorded:
                    match = computed_hash == recorded['checksum']
                    if row_num <= sample_size or not match:
                        status = "✓" if match else "✗"
                        print(f"{status} Row {row_num}: {'MATCH' if match else 'MISMATCH'}")
                        if not match:
                            print(f"    Expected: {recorded['checksum']}")
                            print(f"    Got:      {computed_hash}")
                        verified_rows.append({
                            'row_number': row_num,
                            'match': match
                        })
                        if not match:
                            all_match = False
        
        self.verification_results['row_checksums'] = verified_rows
        if not all_match:
            self.verification_results['overall_status'] = 'FAIL'
        
        return all_match
    
    def run_verification(self):
        """Run complete verification."""
        print("=" * 70)
        print("TSV FIXITY VERIFICATION")
        print("=" * 70)
        
        if not self.load_checksums():
            return False
        
        print("\n[1] Verifying output file checksum...")
        self.verify_file_checksum()
        
        print("\n[2] Verifying row count...")
        self.verify_row_count()
        
        print("\n[3] Verifying row-level checksums (sample)...")
        self.verify_row_checksums()
        
        print("\n" + "=" * 70)
        if self.verification_results['overall_status'] == 'PASS':
            print("✓ VERIFICATION PASSED - File integrity confirmed")
        else:
            print("✗ VERIFICATION FAILED - File may be corrupted")
        print("=" * 70)
        
        return self.verification_results['overall_status'] == 'PASS'


def main():
    tsv_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    checksums_file = '/mnt/user-data/outputs/checksums.json'
    
    verifier = TSVVerifier(tsv_file, checksums_file)
    verifier.run_verification()


if __name__ == '__main__':
    main()
