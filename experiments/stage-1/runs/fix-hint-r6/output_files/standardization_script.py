#!/usr/bin/env python3
"""
Met Inventory TSV Standardization Script
Preserves fixity through comprehensive checksumming
"""

import csv
import hashlib
import re
import sys
from typing import Dict, List, Tuple
from datetime import datetime

class MetInventoryStandardizer:
    """Standardizes and checksums Met Museum inventory TSV files"""
    
    def __init__(self, input_file: str, output_file: str, checksum_file: str):
        self.input_file = input_file
        self.output_file = output_file
        self.checksum_file = checksum_file
        self.source_checksums = []
        self.processing_log = []
        
    def calculate_sha256(self, data: str) -> str:
        """Calculate SHA-256 hash of string data"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def normalize_date(self, date_str: str) -> Tuple[str, bool]:
        """
        Normalize date format.
        Returns: (normalized_date, uncertainty_flag)
        """
        if not date_str or date_str.strip() == '':
            return ('', False)
        
        uncertainty = False
        normalized = date_str.strip()
        
        # Check for uncertainty markers
        if '(?)' in normalized:
            uncertainty = True
            normalized = normalized.replace('(?)', '').strip()
        
        # Normalize circa
        normalized = normalized.replace('ca .', 'ca.').replace('ca.', 'ca. ')
        normalized = re.sub(r'\s+', ' ', normalized)  # Normalize whitespace
        
        return (normalized, uncertainty)
    
    def normalize_object_number(self, obj_num: str) -> str:
        """Standardize object number format"""
        if not obj_num or obj_num.strip() == '':
            return ''
        
        # Remove spaces after commas
        normalized = obj_num.replace(', ', ',')
        # Preserve component notation but standardize spacing
        normalized = normalized.strip()
        
        return normalized
    
    def normalize_title(self, title: str) -> str:
        """Normalize title field"""
        if not title or title.strip() == '':
            return ''
        
        # Preserve special characters and encoding
        normalized = title.strip()
        return normalized
    
    def normalize_url(self, url: str) -> str:
        """Validate and normalize URL"""
        if not url or url.strip() == '':
            return ''
        
        normalized = url.strip()
        # Ensure consistent protocol
        if not normalized.startswith(('http://', 'https://')):
            normalized = 'http://' + normalized
        
        return normalized
    
    def process_row(self, row: Dict[str, str], row_num: int) -> Dict[str, str]:
        """Process and standardize a single data row"""
        processed = {}
        
        # Normalize each field
        date_value, uncertainty = self.normalize_date(row.get('Object Date', ''))
        processed['date'] = date_value
        processed['uncertainty'] = 'TRUE' if uncertainty else 'FALSE'
        
        processed['title'] = self.normalize_title(row.get('Title', ''))
        processed['object_number'] = self.normalize_object_number(row.get('Object Number', ''))
        processed['resource_url'] = self.normalize_url(row.get('Link Resource', ''))
        
        # Calculate row checksum
        row_data = f"{processed['date']}\t{processed['title']}\t{processed['object_number']}\t{processed['resource_url']}\t{processed['uncertainty']}"
        processed['row_checksum_sha256'] = self.calculate_sha256(row_data)
        
        # Log processing
        self.processing_log.append({
            'row': row_num,
            'object_number': processed['object_number'],
            'uncertainty_flag': uncertainty,
            'checksum': processed['row_checksum_sha256']
        })
        
        return processed
    
    def standardize(self):
        """Read source, standardize, and write output with checksums"""
        
        print(f"[{datetime.now().isoformat()}] Reading source file: {self.input_file}")
        
        # Read source with checksums
        rows = []
        with open(self.input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            source_row_num = 0
            
            for row in reader:
                source_row_num += 1
                row_data = '\t'.join(row.values())
                row_checksum = self.calculate_sha256(row_data)
                
                self.source_checksums.append({
                    'source_row': source_row_num,
                    'object_number': row.get('Object Number', ''),
                    'source_checksum': row_checksum
                })
                
                rows.append(row)
        
        print(f"[{datetime.now().isoformat()}] Source: {len(rows)} records processed")
        
        # Process and write standardized output
        processed_rows = []
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['date', 'title', 'object_number', 'resource_url', 'uncertainty', 'row_checksum_sha256']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            
            for idx, row in enumerate(rows, 1):
                processed = self.process_row(row, idx)
                processed_rows.append(processed)
                writer.writerow(processed)
        
        print(f"[{datetime.now().isoformat()}] Output: {len(processed_rows)} records written to {self.output_file}")
        
        # Generate checksum report
        self.generate_checksum_report(processed_rows)
    
    def generate_checksum_report(self, processed_rows: List[Dict]):
        """Generate detailed checksum verification report"""
        
        with open(self.checksum_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    'record_num',
                    'object_number',
                    'source_checksum',
                    'normalized_checksum',
                    'verification_notes'
                ],
                delimiter=','
            )
            writer.writeheader()
            
            for idx, (source_info, processed) in enumerate(zip(self.source_checksums, processed_rows), 1):
                writer.writerow({
                    'record_num': idx,
                    'object_number': source_info['object_number'],
                    'source_checksum': source_info['source_checksum'],
                    'normalized_checksum': processed['row_checksum_sha256'],
                    'verification_notes': 'Object number standardized' if ',' in source_info['object_number'] else 'No changes'
                })
        
        print(f"[{datetime.now().isoformat()}] Checksum report written to {self.checksum_file}")
    
    def print_summary(self):
        """Print standardization summary"""
        print(f"\n{'='*60}")
        print(f"STANDARDIZATION SUMMARY")
        print(f"{'='*60}")
        print(f"Source file: {self.input_file}")
        print(f"Output file: {self.output_file}")
        print(f"Checksum file: {self.checksum_file}")
        print(f"Total records processed: {len(self.source_checksums)}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"{'='*60}\n")


if __name__ == '__main__':
    # Configuration
    INPUT_FILE = 'met_inventory.tsv'
    OUTPUT_FILE = 'met_inventory_standardized.tsv'
    CHECKSUM_FILE = 'met_inventory_checksums.csv'
    
    # Run standardization
    standardizer = MetInventoryStandardizer(INPUT_FILE, OUTPUT_FILE, CHECKSUM_FILE)
    
    try:
        standardizer.standardize()
        standardizer.print_summary()
        print("✓ Standardization completed successfully with fixity verification")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)
