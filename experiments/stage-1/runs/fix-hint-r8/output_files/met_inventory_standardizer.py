#!/usr/bin/env python3
"""
Metropolitan Museum Inventory Standardizer & Checksum Verifier
Standardizes TSV files and generates/validates SHA256 checksums for data integrity

Usage:
    python met_inventory_standardizer.py --verify <standardized.tsv>
    python met_inventory_standardizer.py --generate <original.tsv> <output.tsv>
"""

import hashlib
import sys
import argparse
import csv
from pathlib import Path
from typing import List, Tuple, Dict


def calculate_row_hash(row_data: List[str]) -> str:
    """
    Calculate SHA256 hash of row data (excluding the hash column itself).
    
    Args:
        row_data: List of field values for the row
        
    Returns:
        Lowercase hex digest of SHA256 hash
    """
    # Join row fields with tabs and encode to UTF-8
    row_string = '\t'.join(str(field) for field in row_data)
    return hashlib.sha256(row_string.encode('utf-8')).hexdigest()[:40]  # 40 chars for readability


def verify_checksums(filepath: str) -> Tuple[int, int, List[str]]:
    """
    Verify checksums in a standardized TSV file.
    
    Args:
        filepath: Path to the TSV file with checksums
        
    Returns:
        Tuple of (total_records, valid_records, list_of_errors)
    """
    errors = []
    valid_count = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            
            # Read header
            header = next(reader)
            if 'Row_SHA256' not in header:
                errors.append("ERROR: Row_SHA256 column not found in header")
                return 0, 0, errors
            
            hash_col_idx = header.index('Row_SHA256')
            
            # Process data rows
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                if len(row) < len(header):
                    errors.append(f"Row {row_num}: Missing columns (got {len(row)}, expected {len(header)})")
                    continue
                
                # Extract stored hash and data
                stored_hash = row[hash_col_idx].strip()
                row_data = row[:hash_col_idx]  # All columns before hash
                
                # Recalculate hash
                calculated_hash = calculate_row_hash(row_data)
                
                if calculated_hash == stored_hash:
                    valid_count += 1
                else:
                    errors.append(
                        f"Row {row_num}: Hash mismatch!\n"
                        f"  Expected: {stored_hash}\n"
                        f"  Calculated: {calculated_hash}\n"
                        f"  Data: {row_data[:3]}..."  # Show first 3 fields
                    )
        
        total_records = row_num - 1  # Subtract header row
        
    except FileNotFoundError:
        errors.append(f"ERROR: File not found: {filepath}")
        return 0, 0, errors
    except Exception as e:
        errors.append(f"ERROR: {str(e)}")
        return 0, 0, errors
    
    return total_records, valid_count, errors


def standardize_and_hash(input_file: str, output_file: str) -> Tuple[int, List[str]]:
    """
    Read original TSV, standardize it, and add checksums.
    
    Args:
        input_file: Path to original TSV file
        output_file: Path for output standardized TSV file
        
    Returns:
        Tuple of (records_processed, list_of_warnings)
    """
    warnings = []
    records_processed = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.reader(infile, delimiter='\t')
            
            # Read original header
            original_header = next(reader)
            
            # Standardize header: replace spaces with underscores, remove special chars
            standardized_header = []
            for col in original_header:
                col = col.replace(' ', '_').strip()
                col = ''.join(c for c in col if c.isalnum() or c == '_')
                standardized_header.append(col)
            
            # Add checksum column
            standardized_header.append('Row_SHA256')
            
            # Write standardized header
            writer = csv.writer(outfile, delimiter='\t', lineterminator='\n')
            writer.writerow(standardized_header)
            
            # Process data rows
            for row_num, row in enumerate(reader, start=2):
                # Ensure row has same number of columns as header
                if len(row) < len(original_header):
                    warnings.append(f"Row {row_num}: Padding {len(original_header) - len(row)} empty fields")
                    row.extend([''] * (len(original_header) - len(row)))
                elif len(row) > len(original_header):
                    warnings.append(f"Row {row_num}: Truncating {len(row) - len(original_header)} extra fields")
                    row = row[:len(original_header)]
                
                # Calculate hash on original row data (without hash column)
                row_hash = calculate_row_hash(row)
                
                # Write standardized row with hash
                writer.writerow(row + [row_hash])
                records_processed += 1
        
        print(f"✓ Successfully processed {records_processed} records")
        print(f"✓ Output saved to: {output_file}")
        
    except FileNotFoundError:
        warnings.append(f"ERROR: Input file not found: {input_file}")
    except Exception as e:
        warnings.append(f"ERROR: {str(e)}")
    
    return records_processed, warnings


def print_file_stats(filepath: str) -> None:
    """Print statistics about a TSV file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            header = next(reader)
            
            row_count = 0
            empty_counts = {col: 0 for col in header}
            
            for row in reader:
                row_count += 1
                for i, cell in enumerate(row):
                    if i < len(header) and cell.strip() == '':
                        empty_counts[header[i]] += 1
            
            print(f"\nFile Statistics: {filepath}")
            print(f"  Total Records: {row_count}")
            print(f"  Total Columns: {len(header)}")
            print(f"  Columns: {', '.join(header)}")
            print(f"\n  Empty Fields by Column:")
            for col, count in empty_counts.items():
                pct = (count / row_count * 100) if row_count > 0 else 0
                print(f"    {col}: {count} ({pct:.1f}%)")
            
    except Exception as e:
        print(f"Error reading file: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Standardize Met Museum inventory TSV and verify checksums'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Verify command
    verify_parser = subparsers.add_parser(
        'verify',
        help='Verify checksums in standardized file'
    )
    verify_parser.add_argument(
        'file',
        help='Path to standardized TSV file to verify'
    )
    verify_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed error information'
    )
    
    # Generate command
    generate_parser = subparsers.add_parser(
        'generate',
        help='Standardize file and generate checksums'
    )
    generate_parser.add_argument(
        'input',
        help='Path to original TSV file'
    )
    generate_parser.add_argument(
        'output',
        help='Path for standardized output TSV file'
    )
    
    # Stats command
    stats_parser = subparsers.add_parser(
        'stats',
        help='Display file statistics'
    )
    stats_parser.add_argument(
        'file',
        help='Path to TSV file'
    )
    
    args = parser.parse_args()
    
    if args.command == 'verify':
        print(f"Verifying checksums: {args.file}")
        total, valid, errors = verify_checksums(args.file)
        
        print(f"\nVerification Results:")
        print(f"  Total Records: {total}")
        print(f"  Valid Records: {valid}")
        print(f"  Invalid Records: {total - valid}")
        
        if errors:
            print(f"\nErrors/Warnings ({len(errors)}):")
            for error in errors:
                print(f"  {error}")
            return 1
        else:
            print("\n✓ All checksums verified successfully!")
            return 0
    
    elif args.command == 'generate':
        print(f"Standardizing: {args.input}")
        records, warnings = standardize_and_hash(args.input, args.output)
        
        if warnings:
            print(f"\nWarnings ({len(warnings)}):")
            for warning in warnings:
                print(f"  {warning}")
        
        print_file_stats(args.output)
        return 0
    
    elif args.command == 'stats':
        print_file_stats(args.file)
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
