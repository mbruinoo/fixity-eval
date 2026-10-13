#!/usr/bin/env python3
"""
Met Museum Inventory TSV Standardization Script
================================================

Purpose: Standardize the Metropolitan Museum inventory TSV file by:
  - Removing HTML entities
  - Standardizing date formats (B.C. → BCE, etc.)
  - Removing unnecessary quotation marks and brackets
  - Removing Asian character duplicates from titles
  - Ensuring consistent tab separation
  - Validating data integrity with checksums

Input File:  met_inventory.tsv
Output File: met_inventory_standardized.tsv

Execution Date: 2024
Author: Data Standardization Pipeline
"""

import hashlib
import sys
import re
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

INPUT_FILE = "met_inventory.tsv"
OUTPUT_FILE = "met_inventory_standardized.tsv"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_file_checksum(filepath):
    """
    Calculate SHA-256 checksum of a file.
    
    Args:
        filepath (str): Path to the file
        
    Returns:
        str: Hexadecimal SHA-256 hash
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

def remove_html_entities(text):
    """
    Remove or decode common HTML entities.
    
    Args:
        text (str): Text containing HTML entities
        
    Returns:
        str: Cleaned text
    """
    # Replace common HTML entities
    replacements = {
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&#39;': "'",
    }
    
    result = text
    for entity, char in replacements.items():
        result = result.replace(entity, char)
    
    return result

def standardize_date_format(text):
    """
    Standardize date notations (B.C. → BCE, etc.).
    
    Args:
        text (str): Text containing date information
        
    Returns:
        str: Standardized text
    """
    # Replace B.C. with BCE
    result = text.replace('B.C.', 'BCE')
    # Replace A.D. with CE
    result = result.replace('A.D.', 'CE')
    
    return result

def remove_brackets(text):
    """
    Remove square brackets used for alternative titles/descriptions.
    
    Args:
        text (str): Text containing brackets
        
    Returns:
        str: Text without brackets
    """
    # Remove square brackets but keep content
    result = text.replace('[', '').replace(']', '')
    return result

def remove_quotes(text):
    """
    Remove unnecessary leading/trailing quotes from titles.
    
    Args:
        text (str): Text potentially containing quotes
        
    Returns:
        str: Text without unnecessary quotes
    """
    # Remove leading and trailing double quotes
    if text.startswith('"') and text.endswith('"'):
        result = text[1:-1]
    else:
        result = text
    
    return result

def remove_asian_duplicates(title):
    """
    Remove Asian character duplicates from titles (keeping only English part).
    
    Common pattern: "中文|English Translation"
    
    Args:
        title (str): Title potentially containing Asian characters
        
    Returns:
        str: Title with only English part
    """
    # Pattern: non-Latin characters followed by pipe separator
    if '|' in title:
        parts = title.split('|')
        # Return the part without Asian characters (typically the last part)
        for part in reversed(parts):
            part_clean = part.strip()
            # Check if this part is primarily Latin characters
            if part_clean and any(ord(c) < 128 for c in part_clean):
                return part_clean
        # If no Latin part found, return first part
        return parts[0].strip()
    
    return title

def standardize_title(title):
    """
    Apply all title standardization transformations.
    
    Args:
        title (str): Raw title text
        
    Returns:
        str: Standardized title
    """
    if not title or title.strip() == '':
        return ''
    
    # Apply transformations in sequence
    result = title.strip()
    result = remove_html_entities(result)
    result = remove_brackets(result)
    result = remove_quotes(result)
    result = remove_asian_duplicates(result)
    result = result.strip()
    
    return result

def standardize_date(date_str):
    """
    Apply all date standardization transformations.
    
    Args:
        date_str (str): Raw date text
        
    Returns:
        str: Standardized date
    """
    if not date_str or date_str.strip() == '':
        return ''
    
    result = date_str.strip()
    result = standardize_date_format(result)
    
    return result

def process_row(row_data):
    """
    Process a single row of TSV data.
    
    Args:
        row_data (list): List of column values
        
    Returns:
        list: Processed row data
    """
    if len(row_data) < 4:
        return row_data
    
    # Unpack columns
    object_date, title, object_number, link_resource = row_data[0], row_data[1], row_data[2], row_data[3]
    
    # Apply transformations
    object_date = standardize_date(object_date)
    title = standardize_title(title)
    object_number = object_number.strip()
    link_resource = link_resource.strip()
    
    return [object_date, title, object_number, link_resource]

# ============================================================================
# MAIN PROCESSING
# ============================================================================

def main():
    """Main processing function."""
    
    print("=" * 80)
    print("MET MUSEUM INVENTORY TSV STANDARDIZATION")
    print("=" * 80)
    print()
    
    # Step 1: Verify input file exists and calculate checksum
    print(f"[1] Calculating input file checksum...")
    if not Path(INPUT_FILE).exists():
        print(f"    Error: Input file not found: {INPUT_FILE}")
        sys.exit(1)
    
    input_checksum = calculate_file_checksum(INPUT_FILE)
    print(f"    Input file: {INPUT_FILE}")
    print(f"    SHA-256:    {input_checksum}")
    print()
    
    # Step 2: Read and process input file
    print(f"[2] Reading and processing input file...")
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"    Error reading file: {e}")
        sys.exit(1)
    
    # Parse header and data rows
    if len(lines) == 0:
        print("    Error: Input file is empty")
        sys.exit(1)
    
    header_line = lines[0].rstrip('\n\r')
    header_columns = header_line.split('\t')
    print(f"    Header: {header_columns}")
    print(f"    Total rows (including header): {len(lines)}")
    
    processed_rows = [header_line]  # Keep original header
    data_rows = lines[1:]
    
    transformation_stats = {
        'total_rows_processed': 0,
        'empty_titles_preserved': 0,
        'html_entities_removed': 0,
        'brackets_removed': 0,
        'quotes_removed': 0,
        'asian_duplicates_removed': 0,
        'date_standardizations': 0,
    }
    
    for i, line in enumerate(data_rows, start=2):
        line_clean = line.rstrip('\n\r')
        if not line_clean:
            processed_rows.append(line)
            continue
        
        row_data = line_clean.split('\t')
        if len(row_data) != 4:
            # Preserve malformed rows as-is
            processed_rows.append(line)
            continue
        
        # Track transformations
        original_row = row_data.copy()
        processed_row = process_row(row_data)
        
        # Update statistics
        transformation_stats['total_rows_processed'] += 1
        
        if original_row[1] == '' and processed_row[1] == '':
            transformation_stats['empty_titles_preserved'] += 1
        elif original_row[1] != processed_row[1]:
            if '&' in original_row[1]:
                transformation_stats['html_entities_removed'] += 1
            if '[' in original_row[1] or ']' in original_row[1]:
                transformation_stats['brackets_removed'] += 1
            if '"' in original_row[1]:
                transformation_stats['quotes_removed'] += 1
            if '|' in original_row[1]:
                transformation_stats['asian_duplicates_removed'] += 1
        
        if original_row[0] != processed_row[0]:
            transformation_stats['date_standardizations'] += 1
        
        # Reconstruct row with tab separation
        processed_line = '\t'.join(processed_row)
        processed_rows.append(processed_line)
    
    print(f"    Data rows processed: {transformation_stats['total_rows_processed']}")
    print()
    
    # Step 3: Write output file
    print(f"[3] Writing standardized output file...")
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for row in processed_rows:
                f.write(row)
                if not row.endswith('\n'):
                    f.write('\n')
    except Exception as e:
        print(f"    Error writing file: {e}")
        sys.exit(1)
    
    print(f"    Output file: {OUTPUT_FILE}")
    print()
    
    # Step 4: Calculate output file checksum
    print(f"[4] Calculating output file checksum...")
    output_checksum = calculate_file_checksum(OUTPUT_FILE)
    print(f"    SHA-256: {output_checksum}")
    print()
    
    # Step 5: Transformation summary
    print(f"[5] Transformation Summary:")
    print(f"    Total rows processed:           {transformation_stats['total_rows_processed']}")
    print(f"    Empty titles preserved:        {transformation_stats['empty_titles_preserved']}")
    print(f"    HTML entities removed:         {transformation_stats['html_entities_removed']}")
    print(f"    Brackets removed:              {transformation_stats['brackets_removed']}")
    print(f"    Quotes removed:                {transformation_stats['quotes_removed']}")
    print(f"    Asian duplicates removed:      {transformation_stats['asian_duplicates_removed']}")
    print(f"    Date standardizations:         {transformation_stats['date_standardizations']}")
    print()
    
    # Step 6: Output summary
    print("=" * 80)
    print("FIXITY CHECK - FILE INTEGRITY VERIFICATION")
    print("=" * 80)
    print(f"Input File:      {INPUT_FILE}")
    print(f"Input SHA-256:   {input_checksum}")
    print()
    print(f"Output File:     {OUTPUT_FILE}")
    print(f"Output SHA-256:  {output_checksum}")
    print()
    print("Checksums allow for verification of:")
    print("  - Data integrity (no corruption)")
    print("  - Archive authenticity (bit-for-bit verification)")
    print("  - Long-term preservation validation")
    print()
    print("=" * 80)
    print("PROCESSING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
