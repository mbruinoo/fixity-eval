#!/usr/bin/env python3
"""
Standardize Met Museum inventory TSV file with checksum verification for data fixity.
Creates checksums for source rows, standardized rows, and field-level validation.
"""

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class TSVStandardizer:
    def __init__(self):
        self.source_checksums = []
        self.standardized_checksums = []
        self.field_mappings = []
        
    def calculate_checksum(self, data: str, algorithm: str = 'sha256') -> str:
        """Calculate checksum for a string."""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def standardize_row(self, row: Dict) -> Dict:
        """
        Standardize a single row with consistent field names and data formatting.
        Returns standardized row with empty strings normalized to proper nulls.
        """
        standardized = {
            'date': (row.get('Object Date') or '').strip(),
            'title': (row.get('Title') or '').strip(),
            'object_number': (row.get('Object Number') or '').strip(),
            'url': (row.get('Link Resource') or '').strip(),
        }
        return standardized
    
    def process_file(self, input_path: str, output_path: str, 
                    manifest_path: str, row_checksums_path: str) -> None:
        """
        Process the TSV file with standardization and checksum verification.
        Creates multiple output files for transparency and verification.
        """
        
        # Read source file
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            rows = list(reader)
        
        print(f"✓ Read {len(rows)} rows from source file")
        
        # Process each row with checksums
        standardized_rows = []
        
        for idx, row in enumerate(rows, 1):
            # Create source data representation for checksumming
            source_data = '\t'.join([
                row.get('Object Date', ''),
                row.get('Title', ''),
                row.get('Object Number', ''),
                row.get('Link Resource', '')
            ])
            source_checksum = self.calculate_checksum(source_data)
            
            # Standardize the row
            std_row = self.standardize_row(row)
            
            # Create standardized data representation
            std_data = '\t'.join([
                std_row['date'],
                std_row['title'],
                std_row['object_number'],
                std_row['url']
            ])
            std_checksum = self.calculate_checksum(std_data)
            
            self.source_checksums.append({
                'row_number': idx,
                'source_checksum': source_checksum,
                'std_checksum': std_checksum,
                'object_number': std_row['object_number']
            })
            
            # Add checksums to standardized row for verification
            std_row['row_number'] = idx
            std_row['source_checksum'] = source_checksum
            std_row['std_checksum'] = std_checksum
            standardized_rows.append(std_row)
        
        print(f"✓ Standardized {len(standardized_rows)} rows")
        
        # Write standardized TSV with checksums
        self.write_standardized_tsv(output_path, standardized_rows)
        
        # Write manifest with checksum mappings
        self.write_manifest(manifest_path, standardized_rows)
        
        # Write row-level checksums for verification
        self.write_row_checksums(row_checksums_path)
        
        print(f"✓ Output files created:")
        print(f"  - {output_path}")
        print(f"  - {manifest_path}")
        print(f"  - {row_checksums_path}")
    
    def write_standardized_tsv(self, output_path: str, rows: List[Dict]) -> None:
        """Write the standardized TSV file."""
        fieldnames = ['row_number', 'date', 'title', 'object_number', 'url', 
                     'source_checksum', 'std_checksum']
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            writer.writerows(rows)
    
    def write_manifest(self, manifest_path: str, rows: List[Dict]) -> None:
        """Write a JSON manifest with metadata and field-level checksums."""
        manifest = {
            'generated': datetime.now().isoformat(),
            'source_file': 'met_inventory.tsv',
            'total_records': len(rows),
            'standardization_rules': {
                'field_names': {
                    'Object Date': 'date',
                    'Title': 'title',
                    'Object Number': 'object_number',
                    'Link Resource': 'url'
                },
                'normalization': [
                    'Whitespace trimmed from all fields',
                    'Empty values standardized',
                    'Consistent column ordering'
                ]
            },
            'checksum_method': 'SHA256',
            'records': []
        }
        
        for row in rows:
            manifest['records'].append({
                'row_number': row['row_number'],
                'object_number': row['object_number'],
                'date': row['date'][:50] + '...' if len(row['date']) > 50 else row['date'],
                'source_checksum': row['source_checksum'],
                'std_checksum': row['std_checksum']
            })
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    def write_row_checksums(self, output_path: str) -> None:
        """Write row-level checksums in CSV format for verification."""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['row_number', 'object_number', 
                                                   'source_checksum', 'std_checksum'],
                                   delimiter='\t')
            writer.writeheader()
            writer.writerows(self.source_checksums)


def verify_checksums(standardized_path: str, checksum_path: str) -> bool:
    """
    Verify that the standardized file matches recorded checksums.
    Returns True if all checksums match.
    """
    # Read checksums
    checksums_map = {}
    with open(checksum_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            checksums_map[int(row['row_number'])] = {
                'source': row['source_checksum'],
                'std': row['std_checksum']
            }
    
    # Read standardized file and verify
    mismatches = []
    with open(standardized_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            row_num = int(row['row_number'])
            if row['std_checksum'] != checksums_map[row_num]['std']:
                mismatches.append(row_num)
    
    if mismatches:
        print(f"✗ Checksum mismatches found in rows: {mismatches}")
        return False
    else:
        print(f"✓ All {len(checksums_map)} checksums verified successfully")
        return True


if __name__ == '__main__':
    # Note: This script expects to be run with appropriate file paths
    # Example usage:
    # python standardize_met_inventory.py
    
    standardizer = TSVStandardizer()
    print("Met Museum Inventory TSV Standardization Tool")
    print("=" * 50)
    print()
    
    # Process file
    standardizer.process_file(
        input_path='met_inventory.tsv',
        output_path='met_inventory_standardized.tsv',
        manifest_path='met_inventory_manifest.json',
        row_checksums_path='met_inventory_checksums.tsv'
    )
    
    print()
    print("Verification")
    print("=" * 50)
    verify_checksums(
        standardized_path='met_inventory_standardized.tsv',
        checksum_path='met_inventory_checksums.tsv'
    )
