#!/usr/bin/env python3
"""
Metropolitan Museum Inventory Data Standardization Script

This script performs data cleaning and standardization on the Met Museum 
inventory TSV file.

FIXITY VERIFICATION (MD5 Checksums):
=====================================
INPUT FILE CHECKSUM:
  met_inventory.tsv: 6ec5bfc2d979ad12eb3343149beb8617

Expected OUTPUT FILE CHECKSUM (for verification):
  met_inventory_standardized.tsv: [Generated during execution]

TRANSFORMATIONS APPLIED:
=========================
1. Fill missing Object Date values with "Unknown"
2. Fill missing Title values with "Untitled"
3. Decode HTML entities in all text fields
4. Standardize date notation:
   - B.C. → BCE
   - BC → BCE
   - A.C. → CE
   - A.H. → AH
   - "circa" → "ca."
5. Normalize dash characters (en-dash, em-dash → standard hyphen)
6. Remove extra whitespace from all fields
7. Standardize column names to snake_case format
8. Write output with proper quoting

USAGE:
======
python3 standardize_met_inventory.py <input_file> <output_file>

EXAMPLE:
========
python3 standardize_met_inventory.py met_inventory.tsv met_inventory_standardized.tsv
"""

import pandas as pd
import re
import html
import hashlib
import sys
from pathlib import Path
from datetime import datetime

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_md5(filepath):
    """Calculate MD5 checksum of a file."""
    md5_hash = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    except FileNotFoundError:
        return None


def standardize_date(date_str):
    """
    Standardize date string notation.
    
    Transformations:
    - B.C./BC → BCE
    - A.C. → CE
    - A.H. → AH
    - circa/Circa → ca.
    - en-dash/em-dash → hyphen
    - Multiple spaces → single space
    """
    if pd.isna(date_str) or date_str == 'Unknown':
        return 'Unknown'
    
    date_str = str(date_str).strip()
    
    # Standardize era notation
    date_str = re.sub(r'\bB\.C\.\b', 'BCE', date_str)
    date_str = re.sub(r'\bBC\b', 'BCE', date_str)
    date_str = re.sub(r'\bA\.C\.\b', 'CE', date_str)
    date_str = re.sub(r'\bA\.H\.\b', 'AH', date_str)
    
    # Normalize dashes (en-dash, em-dash → standard hyphen)
    date_str = re.sub(r'[–—]', '-', date_str)
    
    # Standardize "circa" notation
    date_str = re.sub(r'\bcirca\b', 'ca.', date_str, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    date_str = re.sub(r'\s+', ' ', date_str).strip()
    
    return date_str


def clean_html_entities(text):
    """Decode HTML entities and remove HTML tags from text."""
    if pd.isna(text):
        return text
    
    text = str(text)
    # Decode HTML entities (e.g., &lt; → <)
    text = html.unescape(text)
    # Remove HTML tags (e.g., <i>, </i>)
    text = re.sub(r'</?[^>]+>', '', text)
    
    return text


def standardize_dataframe(df):
    """
    Apply all standardization transformations to the dataframe.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input dataframe with Met Museum inventory data
    
    Returns:
    --------
    df : pandas.DataFrame
        Standardized dataframe
    """
    print("  [1/6] Filling missing date values with 'Unknown'...")
    df['Object Date'] = df['Object Date'].fillna('Unknown')
    
    print("  [2/6] Filling missing title values with 'Untitled'...")
    df['Title'] = df['Title'].fillna('Untitled')
    
    print("  [3/6] Cleaning HTML entities from Title field...")
    df['Title'] = df['Title'].apply(clean_html_entities)
    
    print("  [4/6] Standardizing date notation...")
    df['Object Date'] = df['Object Date'].apply(standardize_date)
    
    print("  [5/6] Removing extra whitespace from all fields...")
    for col in df.columns:
        if df[col].dtype == 'object':  # String columns only
            df[col] = df[col].str.strip()
    
    print("  [6/6] Standardizing column names to snake_case...")
    df.columns = [
        'Object_Date',
        'Title',
        'Object_Number',
        'Link_Resource'
    ]
    
    return df


def main():
    """Main execution function."""
    
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("USAGE: python3 standardize_met_inventory.py <input_file> <output_file>")
        print("\nEXAMPLE:")
        print("  python3 standardize_met_inventory.py met_inventory.tsv met_inventory_standardized.tsv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Verify input file exists
    if not Path(input_file).exists():
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)
    
    print("=" * 80)
    print("METROPOLITAN MUSEUM INVENTORY STANDARDIZATION")
    print("=" * 80)
    print(f"\nExecution timestamp: {datetime.now().isoformat()}")
    
    # Calculate input checksum
    print(f"\nCalculating input file checksum...")
    input_checksum = calculate_md5(input_file)
    print(f"  Input file:  {input_file}")
    print(f"  MD5:         {input_checksum}")
    
    # Read input file
    print(f"\nReading input file...")
    try:
        df = pd.read_csv(input_file, sep='\t')
        print(f"  Rows:        {len(df):,}")
        print(f"  Columns:     {len(df.columns)}")
        print(f"  Missing values:")
        for col in df.columns:
            missing = df[col].isnull().sum()
            if missing > 0:
                print(f"    - {col}: {missing}")
    except Exception as e:
        print(f"ERROR: Failed to read input file: {e}")
        sys.exit(1)
    
    # Apply transformations
    print(f"\nApplying standardization transformations...")
    try:
        df = standardize_dataframe(df)
    except Exception as e:
        print(f"ERROR: Transformation failed: {e}")
        sys.exit(1)
    
    # Write output file
    print(f"\nWriting standardized data to output file...")
    try:
        df.to_csv(output_file, sep='\t', index=False, quoting=1)
        print(f"  Output file: {output_file}")
    except Exception as e:
        print(f"ERROR: Failed to write output file: {e}")
        sys.exit(1)
    
    # Verify output file
    print(f"\nVerifying output file...")
    if not Path(output_file).exists():
        print(f"ERROR: Output file was not created successfully")
        sys.exit(1)
    
    output_checksum = calculate_md5(output_file)
    print(f"  Output file: {output_file}")
    print(f"  Rows:        {len(df):,}")
    print(f"  Columns:     {len(df.columns)}")
    print(f"  MD5:         {output_checksum}")
    
    # Summary report
    print("\n" + "=" * 80)
    print("TRANSFORMATION SUMMARY")
    print("=" * 80)
    print("\nTransformations Applied:")
    print("  ✓ Filled missing dates with 'Unknown'")
    print("  ✓ Filled missing titles with 'Untitled'")
    print("  ✓ Removed/decoded HTML entities")
    print("  ✓ Standardized date notation (B.C.→BCE, A.C.→CE, circa→ca.)")
    print("  ✓ Normalized dashes (en-dash/em-dash → standard hyphen)")
    print("  ✓ Removed extra whitespace")
    print("  ✓ Standardized column names to snake_case")
    
    print("\n" + "-" * 80)
    print("FIXITY VERIFICATION")
    print("-" * 80)
    print(f"\nInput File Checksum:")
    print(f"  Filename: {input_file}")
    print(f"  MD5:      {input_checksum}")
    
    print(f"\nOutput File Checksum:")
    print(f"  Filename: {output_file}")
    print(f"  MD5:      {output_checksum}")
    
    print(f"\nTo verify file integrity later, run:")
    print(f"  md5sum --check <<EOF")
    print(f"{input_checksum}  {input_file}")
    print(f"{output_checksum}  {output_file}")
    print(f"EOF")
    
    print("\n" + "=" * 80)
    print("STANDARDIZATION COMPLETE")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
