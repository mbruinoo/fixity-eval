#!/usr/bin/env python3
"""
Met Museum Inventory TSV Standardization Script
================================================

This script standardizes the Met Museum inventory TSV file by:
1. Adding missing data values with placeholders ([Unknown] for titles, [Unknown Date] for dates)
2. Extracting English titles from bilingual entries (Chinese|English format)
3. Ensuring all rows have exactly 4 tab-separated columns
4. Adding a fixity check header with MD5 checksums

Usage:
    python3 standardize_met_inventory.py <input_file> <output_file>

Fixity Check:
    The script computes and includes MD5 checksums for both input and output files
    in the header comments for integrity verification.
"""

import sys
import hashlib
import csv
from datetime import datetime


def compute_md5(filepath):
    """Compute MD5 checksum of a file."""
    md5_hash = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def extract_english_title(title):
    """
    Extract English title from bilingual entries.
    
    Format: "ChineseText|English Title" -> "English Title"
    If no pipe found, returns original title.
    """
    if "|" in title:
        parts = title.split("|")
        return parts[1].strip()
    return title


def standardize_row(row):
    """
    Standardize a single row by filling missing values and cleaning titles.
    
    Args:
        row: List of 4 elements [date, title, object_number, link]
    
    Returns:
        Standardized row with filled values
    """
    date, title, obj_num, link = row
    
    # Fill missing date
    if not date or date.isspace():
        date = "[Unknown Date]"
    
    # Fill missing title and extract English from bilingual
    if not title or title.isspace():
        title = "[Unknown]"
    else:
        title = extract_english_title(title)
    
    # Object number should always be present, but add placeholder if not
    if not obj_num or obj_num.isspace():
        obj_num = "[Unknown Object Number]"
    
    # Link should always be present, but add placeholder if not
    if not link or link.isspace():
        link = "[No URL]"
    
    return [date, title, obj_num, link]


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 standardize_met_inventory.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        # Compute input file checksum
        input_md5 = compute_md5(input_file)
        print(f"Input file MD5: {input_md5}")
        
        # Read and standardize data
        rows = []
        with open(input_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                # Ensure row has exactly 4 columns
                while len(row) < 4:
                    row.append("")
                row = row[:4]
                
                # Standardize the row
                standardized = standardize_row(row)
                rows.append(standardized)
        
        # Write output with fixity header
        with open(output_file, "w", encoding="utf-8", newline="") as f:
            # Write header comments with fixity information
            f.write("# Met Museum Inventory - Standardized\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Input File MD5:  {input_md5}\n")
            
            # Write data
            writer = csv.writer(f, delimiter="\t", lineterminator="\n")
            writer.writerow(["Object Date", "Title", "Object Number", "Link Resource"])
            writer.writerows(rows)
        
        # Compute output file checksum (excluding header comments)
        output_md5 = compute_md5(output_file)
        print(f"Output file MD5: {output_md5}")
        
        # Append output checksum to header
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        lines = content.split("\n")
        # Insert output checksum after input checksum
        lines.insert(3, f"# Output File MD5: {output_md5}\n")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        print(f"\nStandardization complete!")
        print(f"Input rows processed: {len(rows)}")
        print(f"Output file: {output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
