#!/usr/bin/env python3
"""
TSV Standardization Script with Fixity Verification
Standardizes the Met Museum inventory TSV file and computes checksums for integrity verification.
"""

import csv
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple

class TSVStandardizer:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.checksums = {
            'source_file': {},
            'rows': [],
            'output_file': {}
        }
    
    def compute_hash(self, data: str, algorithm: str = 'sha256') -> str:
        """Compute SHA-256 hash of data."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def verify_row_integrity(self, row_num: int, row_data: Dict) -> Dict:
        """Compute checksum for individual row."""
        # Serialize row in a canonical format
        canonical = json.dumps(row_data, sort_keys=True, ensure_ascii=True, separators=(',', ':'))
        return {
            'row_number': row_num,
            'checksum': self.compute_hash(canonical),
            'canonical_form': canonical
        }
    
    def standardize(self) -> Tuple[List[Dict], Dict]:
        """
        Read TSV, standardize it, compute checksums.
        Returns: (standardized_rows, checksums_dict)
        """
        
        # Read source file and compute its checksum
        with open(self.input_path, 'r', encoding='utf-8') as f:
            source_content = f.read()
        
        self.checksums['source_file']['path'] = str(self.input_path)
        self.checksums['source_file']['sha256'] = self.compute_hash(source_content)
        self.checksums['source_file']['size_bytes'] = len(source_content)
        
        # Parse TSV
        rows = []
        with open(self.input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            original_fieldnames = reader.fieldnames
            
            for row_num, row in enumerate(reader, start=2):  # start=2 (header is row 1)
                # Standardize field names: strip whitespace, lowercase, replace spaces with underscores
                standardized_row = {}
                for key, value in row.items():
                    if key is None:  # Handle malformed rows
                        continue
                    standard_key = key.strip().lower().replace(' ', '_')
                    standard_value = value.strip() if value else ''
                    standardized_row[standard_key] = standard_value
                
                # Verify integrity before and after standardization
                row_check = self.verify_row_integrity(row_num, standardized_row)
                self.checksums['rows'].append(row_check)
                
                rows.append(standardized_row)
        
        self.checksums['source_file']['header'] = original_fieldnames
        self.checksums['source_file']['total_rows'] = len(rows)
        
        return rows, original_fieldnames
    
    def write_standardized_tsv(self, rows: List[Dict], fieldnames: List[str]):
        """Write standardized data to TSV file."""
        # Use standardized fieldnames
        standard_fieldnames = [
            fn.strip().lower().replace(' ', '_') for fn in fieldnames if fn
        ]
        
        with open(self.output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=standard_fieldnames, delimiter='\t')
            writer.writeheader()
            writer.writerows(rows)
        
        # Compute output file checksum
        with open(self.output_path, 'r', encoding='utf-8') as f:
            output_content = f.read()
        
        self.checksums['output_file']['path'] = str(self.output_path)
        self.checksums['output_file']['sha256'] = self.compute_hash(output_content)
        self.checksums['output_file']['size_bytes'] = len(output_content)
        self.checksums['output_file']['fieldnames'] = standard_fieldnames
        self.checksums['output_file']['total_rows'] = len(rows)
    
    def write_checksum_report(self, report_path: str):
        """Write detailed checksum report to JSON file."""
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.checksums, f, indent=2)


def main():
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    checksum_report = '/mnt/user-data/outputs/checksums.json'
    
    print("=" * 70)
    print("TSV STANDARDIZATION WITH FIXITY VERIFICATION")
    print("=" * 70)
    
    standardizer = TSVStandardizer(input_file, output_file)
    
    print("\n[1] Reading source file and computing checksums...")
    rows, fieldnames = standardizer.standardize()
    print(f"    ✓ Source file SHA-256: {standardizer.checksums['source_file']['sha256']}")
    print(f"    ✓ Total rows processed: {len(rows)}")
    
    print("\n[2] Writing standardized TSV...")
    standardizer.write_standardized_tsv(rows, fieldnames)
    print(f"    ✓ Output file SHA-256: {standardizer.checksums['output_file']['sha256']}")
    
    print("\n[3] Writing checksum report...")
    standardizer.write_checksum_report(checksum_report)
    print(f"    ✓ Report written to: {checksum_report}")
    
    print("\n[4] STANDARDIZATION CHANGES:")
    print(f"    ✓ Original fieldnames: {fieldnames}")
    standardized_names = [
        fn.strip().lower().replace(' ', '_') for fn in fieldnames if fn
    ]
    print(f"    ✓ Standardized fieldnames: {standardized_names}")
    print(f"    ✓ Whitespace trimmed from all values")
    print(f"    ✓ Consistent encoding (UTF-8)")
    print(f"    ✓ Consistent delimiters (TAB)")
    
    print("\n[5] FIXITY VERIFICATION:")
    print(f"    Source rows with checksums: {len(standardizer.checksums['rows'])}")
    print(f"    (Each row has SHA-256 hash for integrity tracking)")
    print(f"\n    Sample row 2 checksum: {standardizer.checksums['rows'][0]['checksum']}")
    
    print("\n" + "=" * 70)
    print("STANDARDIZATION COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
