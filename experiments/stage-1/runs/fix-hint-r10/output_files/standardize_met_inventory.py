#!/usr/bin/env python3
"""
TSV Standardization Script with Fixity Verification
Standardizes met_inventory.tsv and creates checksums for data integrity

Features:
- Validates TSV structure and column consistency
- Standardizes formatting and whitespace
- Generates SHA-256 checksums for individual rows and cells
- Creates detailed fixity report
"""

import csv
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

def calculate_checksum(text: str, algorithm: str = 'sha256') -> str:
    """Calculate checksum for given text."""
    h = hashlib.sha256() if algorithm == 'sha256' else hashlib.md5()
    h.update(text.encode('utf-8'))
    return h.hexdigest()

def validate_tsv(file_path: Path) -> Tuple[List[List[str]], List[str], List[Dict]]:
    """
    Read and validate TSV file structure.
    Returns: (rows, headers, issues)
    """
    issues = []
    rows = []
    headers = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row_idx, row in enumerate(reader):
            if row_idx == 0:
                headers = row
            else:
                rows.append(row)
                # Check for column count mismatch
                if len(row) != len(headers):
                    issues.append({
                        'type': 'column_mismatch',
                        'row': row_idx + 1,
                        'expected': len(headers),
                        'actual': len(row),
                        'content': row[:3]  # Show first 3 cells
                    })
    
    return rows, headers, issues

def standardize_cell(cell: str) -> str:
    """Standardize individual cell content."""
    # Strip leading/trailing whitespace
    cell = cell.strip()
    # Normalize internal whitespace (but preserve single spaces)
    cell = ' '.join(cell.split())
    return cell

def standardize_row(row: List[str]) -> List[str]:
    """Standardize all cells in a row."""
    return [standardize_cell(cell) for cell in row]

def generate_fixity_data(rows: List[List[str]], headers: List[str]) -> Dict:
    """Generate comprehensive fixity verification data."""
    fixity = {
        'header_checksum': calculate_checksum('\t'.join(headers)),
        'header_cells': {},
        'row_checksums': [],
        'cell_checksums': [],
        'statistics': {
            'total_rows': len(rows),
            'total_columns': len(headers),
            'total_cells': len(rows) * len(headers),
        }
    }
    
    # Header checksums
    for col_idx, header in enumerate(headers):
        fixity['header_cells'][f'col_{col_idx}_{header}'] = calculate_checksum(header)
    
    # Row and cell checksums
    for row_idx, row in enumerate(rows):
        row_content = '\t'.join(row)
        row_checksum = calculate_checksum(row_content)
        
        fixity['row_checksums'].append({
            'row_number': row_idx + 2,  # +2 because row 1 is header, 0-indexed
            'checksum': row_checksum,
            'content_preview': row_content[:80]
        })
        
        # Cell-level checksums
        for col_idx, cell in enumerate(row):
            fixity['cell_checksums'].append({
                'row': row_idx + 2,
                'col': col_idx,
                'col_name': headers[col_idx],
                'value': cell,
                'checksum': calculate_checksum(cell)
            })
    
    return fixity

def create_standardized_file(rows: List[List[str]], headers: List[str], output_path: Path) -> str:
    """Create standardized TSV file and return its checksum."""
    standardized_rows = [standardize_row(row) for row in rows]
    standardized_headers = standardize_row(headers)
    
    # Calculate checksum of standardized content
    all_lines = ['\t'.join(standardized_headers)]
    all_lines.extend(['\t'.join(row) for row in standardized_rows])
    standardized_content = '\n'.join(all_lines)
    content_checksum = calculate_checksum(standardized_content)
    
    # Write file
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerow(standardized_headers)
        writer.writerows(standardized_rows)
    
    return content_checksum

def generate_report(
    input_path: Path,
    output_path: Path,
    original_rows: List[List[str]],
    headers: List[str],
    issues: List[Dict],
    original_fixity: Dict,
    standardized_checksum: str
) -> str:
    """Generate comprehensive standardization report."""
    
    report = []
    report.append("=" * 80)
    report.append("TSV STANDARDIZATION REPORT WITH FIXITY VERIFICATION")
    report.append("=" * 80)
    report.append("")
    
    report.append(f"Generated: {datetime.now().isoformat()}")
    report.append(f"Input File: {input_path.name}")
    report.append(f"Output File: {output_path.name}")
    report.append("")
    
    # Summary
    report.append("SUMMARY")
    report.append("-" * 80)
    report.append(f"Total Rows: {len(original_rows)}")
    report.append(f"Total Columns: {len(headers)}")
    report.append(f"Total Data Cells: {len(original_rows) * len(headers)}")
    report.append(f"Issues Found: {len(issues)}")
    report.append("")
    
    # Column Headers
    report.append("COLUMN HEADERS")
    report.append("-" * 80)
    for idx, header in enumerate(headers):
        report.append(f"Col {idx}: '{header}'")
    report.append("")
    
    # Issues
    if issues:
        report.append("ISSUES FOUND DURING VALIDATION")
        report.append("-" * 80)
        for issue in issues:
            report.append(f"Type: {issue['type']}")
            report.append(f"Row: {issue['row']}")
            report.append(f"Expected columns: {issue['expected']}, Found: {issue['actual']}")
            report.append("")
    else:
        report.append("VALIDATION: No structural issues found")
        report.append("")
    
    # Original Fixity
    report.append("ORIGINAL FILE FIXITY")
    report.append("-" * 80)
    report.append(f"Header Checksum (SHA-256): {original_fixity['header_checksum']}")
    report.append(f"Total Row Checksums: {len(original_fixity['row_checksums'])}")
    report.append(f"Total Cell Checksums: {len(original_fixity['cell_checksums'])}")
    report.append("")
    
    report.append("Sample Row Checksums (First 5 rows):")
    for row_data in original_fixity['row_checksums'][:5]:
        report.append(f"  Row {row_data['row_number']}: {row_data['checksum'][:16]}...")
    report.append("")
    
    # Standardization Changes
    report.append("STANDARDIZATION APPLIED")
    report.append("-" * 80)
    report.append("✓ Whitespace normalization (leading/trailing stripped)")
    report.append("✓ Internal whitespace standardized")
    report.append("✓ Column count validated")
    report.append("✓ UTF-8 encoding preserved")
    report.append("✓ Delimiter consistency (tab-separated)")
    report.append("✓ Line endings normalized (LF)")
    report.append("")
    
    # Standardized File Fixity
    report.append("STANDARDIZED FILE CHECKSUM")
    report.append("-" * 80)
    report.append(f"Full Content Checksum (SHA-256): {standardized_checksum}")
    report.append("")
    
    # Sample Data with Checksums
    report.append("SAMPLE DATA WITH CELL-LEVEL CHECKSUMS (First 3 data rows)")
    report.append("-" * 80)
    sample_cells = [cell for cell in original_fixity['cell_checksums'][:12]]  # First 3 rows
    for cell_data in sample_cells:
        report.append(f"Row {cell_data['row']}, Col {cell_data['col']} ({cell_data['col_name']}):")
        report.append(f"  Value: '{cell_data['value']}'")
        report.append(f"  Checksum: {cell_data['checksum']}")
    report.append("")
    
    report.append("=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)
    
    return '\n'.join(report)

def main():
    """Main execution function."""
    input_path = Path('/mnt/user-data/uploads/met_inventory.tsv')
    output_path = Path('/mnt/user-data/outputs/met_inventory_standardized.tsv')
    report_path = Path('/mnt/user-data/outputs/standardization_report.txt')
    fixity_path = Path('/mnt/user-data/outputs/fixity_checksums.txt')
    
    print("Starting TSV standardization...")
    
    # Validate and read original file
    print("Reading original file...")
    rows, headers, issues = validate_tsv(input_path)
    
    # Generate fixity data for original file
    print("Generating fixity checksums for original file...")
    original_fixity = generate_fixity_data(rows, headers)
    
    # Create standardized file
    print("Creating standardized file...")
    standardized_checksum = create_standardized_file(rows, headers, output_path)
    
    # Generate reports
    print("Generating reports...")
    report = generate_report(
        input_path, output_path, rows, headers, issues,
        original_fixity, standardized_checksum
    )
    
    # Write main report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Write detailed fixity checksums
    with open(fixity_path, 'w', encoding='utf-8') as f:
        f.write("DETAILED FIXITY CHECKSUMS\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("ORIGINAL FILE - HEADER CHECKSUMS\n")
        f.write("-" * 80 + "\n")
        for header_id, checksum in original_fixity['header_cells'].items():
            f.write(f"{header_id}: {checksum}\n")
        f.write("\n")
        
        f.write("ORIGINAL FILE - ROW-LEVEL CHECKSUMS\n")
        f.write("-" * 80 + "\n")
        for row_data in original_fixity['row_checksums']:
            f.write(f"Row {row_data['row_number']}: {row_data['checksum']}\n")
        f.write("\n")
        
        f.write("STANDARDIZED FILE - FULL CONTENT CHECKSUM\n")
        f.write("-" * 80 + "\n")
        f.write(f"{standardized_checksum}\n")
    
    print(f"✓ Standardized file: {output_path}")
    print(f"✓ Report: {report_path}")
    print(f"✓ Fixity checksums: {fixity_path}")
    print("\nDone!")

if __name__ == '__main__':
    main()
