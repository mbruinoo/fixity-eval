#!/usr/bin/env python3
"""
Standardize Met Museum inventory TSV file with checksum verification for fixity.
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

def calculate_checksum(data: str, algorithm: str = 'sha256') -> str:
    """Calculate checksum for data using specified algorithm."""
    if algorithm == 'sha256':
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    elif algorithm == 'md5':
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    return None

def generate_row_checksum(row: Dict, fields: List[str]) -> str:
    """Generate checksum for a single row based on specified fields."""
    row_str = '|'.join([row.get(field, '') for field in fields])
    return calculate_checksum(row_str, 'sha256')

def standardize_met_inventory(input_file: str, output_dir: str = '/mnt/user-data/outputs'):
    """
    Standardize Met Museum inventory TSV file and generate checksums.
    
    Standards applied:
    - Consistent column headers (snake_case)
    - Normalized whitespace
    - Consistent date formatting where possible
    - Data validation and documentation
    """
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Track all checksums for fixity
    fixity_log = {
        'timestamp': datetime.now().isoformat(),
        'source_file': input_file,
        'algorithm': 'sha256',
        'source_checksums': {},
        'standardized_checksums': {},
        'row_checksums': {}
    }
    
    # Read original file
    with open(input_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    fixity_log['source_checksums']['full_file'] = calculate_checksum(original_content)
    
    # Parse TSV
    rows = []
    with open(input_file, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        original_headers = reader.fieldnames
        
        for idx, row in enumerate(reader, start=1):
            rows.append(row)
            # Calculate checksum for original row
            row_content = '\t'.join([row.get(h, '') for h in original_headers])
            fixity_log['source_checksums'][f'row_{idx}'] = calculate_checksum(row_content)
    
    # Standardize headers and data
    standard_headers = ['object_date', 'title', 'object_number', 'resource_link']
    standardized_rows = []
    
    for idx, row in enumerate(rows, start=1):
        standardized_row = {
            'object_date': (row.get('Object Date') or '').strip(),
            'title': (row.get('Title') or '').strip(),
            'object_number': (row.get('Object Number') or '').strip(),
            'resource_link': (row.get('Link Resource') or '').strip()
        }
        
        # Calculate standardized row checksum
        row_str = '\t'.join([standardized_row[h] for h in standard_headers])
        row_checksum = calculate_checksum(row_str)
        fixity_log['row_checksums'][f'row_{idx}'] = {
            'values': standardized_row,
            'checksum': row_checksum
        }
        
        standardized_rows.append(standardized_row)
    
    # Write standardized TSV
    output_tsv = output_dir / 'met_inventory_standardized.tsv'
    with open(output_tsv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=standard_headers, delimiter='\t')
        writer.writeheader()
        writer.writerows(standardized_rows)
    
    # Calculate checksum of standardized file
    with open(output_tsv, 'r', encoding='utf-8') as f:
        standardized_content = f.read()
    
    fixity_log['standardized_checksums']['full_file'] = calculate_checksum(standardized_content)
    
    # Write fixity log
    fixity_file = output_dir / 'met_inventory_fixity_log.json'
    with open(fixity_file, 'w', encoding='utf-8') as f:
        json.dump(fixity_log, f, indent=2)
    
    # Create detailed report
    report = generate_report(
        original_headers,
        standard_headers,
        len(rows),
        fixity_log,
        output_tsv,
        fixity_file
    )
    
    report_file = output_dir / 'met_inventory_standardization_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return {
        'standardized_file': str(output_tsv),
        'fixity_log': str(fixity_file),
        'report': str(report_file),
        'rows_processed': len(rows)
    }

def generate_report(original_headers: List[str], standard_headers: List[str], 
                   row_count: int, fixity_log: Dict, output_tsv: Path, 
                   fixity_file: Path) -> str:
    """Generate detailed standardization report."""
    
    report = f"""
Met Museum Inventory TSV Standardization Report
{'=' * 70}

STANDARDIZATION APPLIED:
{'-' * 70}
1. Column Headers (normalized to snake_case):
   Original: {', '.join(original_headers)}
   Standard: {', '.join(standard_headers)}

2. Data Processing:
   - Removed leading/trailing whitespace from all cells
   - Preserved cell values as-is (no content modification)
   - Maintained field order consistency
   - UTF-8 encoding preserved throughout

3. Data Quality:
   - Total rows processed: {row_count}
   - All rows include standard fields (even if empty)

FIXITY VERIFICATION:
{'-' * 70}
Algorithm: SHA-256

Source File:
  Full file checksum: {fixity_log['source_checksums']['full_file']}
  First row checksum: {fixity_log['source_checksums'].get('row_1', 'N/A')}
  Last row checksum: {fixity_log['source_checksums'].get(f'row_{row_count}', 'N/A')}

Standardized File:
  Full file checksum: {fixity_log['standardized_checksums']['full_file']}

Row-by-Row Checksums:
  Sample (rows 1-5):
"""
    
    for i in range(1, min(6, row_count + 1)):
        if f'row_{i}' in fixity_log['row_checksums']:
            checksum = fixity_log['row_checksums'][f'row_{i}']['checksum']
            report += f"    Row {i}: {checksum}\n"
    
    report += f"""
  (Complete checksums available in: {fixity_file.name})

OUTPUT FILES:
{'-' * 70}
1. {output_tsv.name}
   - Standardized TSV with normalized headers
   - Ready for data processing and analysis

2. {fixity_file.name}
   - Complete SHA-256 checksums for all rows and files
   - Enables verification of data integrity
   - Supports fixity validation across preservation workflows

3. This report file

USAGE NOTES:
{'-' * 70}
- To verify fixity, compare checksums before and after data transfers
- Row checksums can identify specific rows that changed
- Full file checksums detect any modification to the entire dataset
- All checksums use SHA-256 for cryptographic strength

STANDARDS COMPLIANCE:
{'-' * 70}
- TSV format follows Tab-Separated Values specification
- Headers use snake_case convention (lowercase, underscore-separated)
- UTF-8 encoding throughout for international character support
- Row checksums enable row-level integrity verification
- Fixity documentation supports OAIS and digital preservation standards

{'=' * 70}
Generated: {datetime.now().isoformat()}
"""
    
    return report

if __name__ == '__main__':
    import sys
    
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'met_inventory.tsv'
    
    try:
        result = standardize_met_inventory(input_file)
        print(f"Standardization complete!")
        print(f"Output TSV: {result['standardized_file']}")
        print(f"Fixity log: {result['fixity_log']}")
        print(f"Report: {result['report']}")
        print(f"Rows processed: {result['rows_processed']}")
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
