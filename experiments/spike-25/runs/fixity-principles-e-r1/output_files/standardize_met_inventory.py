#!/usr/bin/env python3
"""
Met Museum Inventory TSV Standardization Script

Purpose:
    Standardizes the Met Museum inventory TSV file by applying consistent
    data transformations while preserving the original source file.

Transformations Applied:
    1. Removes extraneous punctuation and quotes from Title field
    2. Normalizes empty cells to "[Unknown]" for clarity
    3. Cleans up nested quotes (e.g., "" becomes ")
    4. Removes uncertainty markers from date fields
    5. Removes brackets around titles
    6. Standardizes whitespace
    7. Preserves all other fields exactly as-is (Object Number, Link Resource)

Input:
    met_inventory_source.tsv (original, unchanged)

Output:
    met_inventory_standardized.tsv (transformed)
    standardization.log (transformation audit log)

Dependencies:
    Python 3.6+, csv module (standard library)
"""

import csv
import re
import sys
from pathlib import Path
from datetime import datetime

# Configuration
SOURCE_FILE = "met_inventory_source.tsv"
OUTPUT_FILE = "met_inventory_standardized.tsv"
LOG_FILE = "standardization.log"


def clean_title(title):
    """
    Clean and standardize title field.
    """
    if not title or title.strip() == "":
        return "[Unknown]"
    
    title = title.strip()
    
    # Remove opening and closing decorative quotes
    title = re.sub(r'^"+', '', title)
    title = re.sub(r'"+$', '', title)
    title = title.strip()
    
    # Replace double internal quotes with single
    title = title.replace('""', '"')
    
    # Remove brackets from around entire title
    if title.startswith('[') and title.endswith(']'):
        title = title[1:-1].strip()
    
    # Clean up excessive spaces
    title = re.sub(r'\s+', ' ', title)
    
    return title if title else "[Unknown]"


def clean_date(date):
    """
    Clean and standardize date field.
    """
    if not date or date.strip() == "":
        return "[Unknown]"
    
    date = date.strip()
    
    # Remove uncertainty markers and bracketed notes
    date = re.sub(r'\s*\(\?\)', '', date)
    date = re.sub(r'\s*\[.*\]', '', date)
    
    date = date.strip()
    
    return date if date else "[Unknown]"


def clean_object_number(obj_num):
    """
    Clean and standardize object number field.
    """
    if not obj_num or obj_num.strip() == "":
        return "[Unknown]"
    return obj_num.strip()


def process_row(row, row_num):
    """
    Process a single row of data.
    Returns cleaned row and list of transformation notes.
    """
    notes = []
    
    if len(row) < 4:
        notes.append(f"Row {row_num}: Insufficient columns (expected 4, got {len(row)})")
        row.extend([''] * (4 - len(row)))
    
    date, title, obj_num, link = row[0], row[1], row[2], row[3]
    
    # Track original values
    original_title = title
    original_date = date
    
    # Clean fields
    cleaned_date = clean_date(date)
    cleaned_title = clean_title(title)
    cleaned_obj_num = clean_object_number(obj_num)
    
    # Log changes
    if original_title != cleaned_title and original_title.strip():
        notes.append(f"Row {row_num}: Title normalized")
    if original_date != cleaned_date and original_date.strip():
        notes.append(f"Row {row_num}: Date normalized")
    
    return [cleaned_date, cleaned_title, cleaned_obj_num, link], notes


def main():
    """Main transformation process."""
    
    # Verify source file exists
    if not Path(SOURCE_FILE).exists():
        print(f"Error: Source file '{SOURCE_FILE}' not found.", file=sys.stderr)
        sys.exit(1)
    
    transformation_count = 0
    total_rows = 0
    
    try:
        # Open log file
        with open(LOG_FILE, 'w', encoding='utf-8') as log:
            log.write(f"Met Museum Inventory Standardization Log\n")
            log.write(f"Generated: {datetime.now().isoformat()}\n")
            log.write(f"Source: {SOURCE_FILE}\n")
            log.write(f"Output: {OUTPUT_FILE}\n")
            log.write("=" * 80 + "\n\n")
            
            with open(SOURCE_FILE, 'r', encoding='utf-8') as infile, \
                 open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as outfile:
                
                reader = csv.reader(infile, delimiter='\t')
                writer = csv.writer(outfile, delimiter='\t', lineterminator='\n')
                
                # Process header
                header = next(reader)
                writer.writerow(header)
                log.write(f"Header: {header}\n\n")
                
                # Process data rows
                for row_num, row in enumerate(reader, start=2):
                    total_rows += 1
                    cleaned_row, notes = process_row(row, row_num)
                    writer.writerow(cleaned_row)
                    
                    if notes:
                        transformation_count += len(notes)
                        for note in notes:
                            log.write(f"{note}\n")
            
            log.write("\n" + "=" * 80 + "\n")
            log.write(f"Summary:\n")
            log.write(f"Total rows processed: {total_rows}\n")
            log.write(f"Total transformations applied: {transformation_count}\n")
            log.write(f"Standardization complete.\n")
    
    except Exception as e:
        print(f"Error during transformation: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Transformation complete")
    print(f"  Source file: {SOURCE_FILE}")
    print(f"  Output file: {OUTPUT_FILE}")
    print(f"  Log file: {LOG_FILE}")
    print(f"  Rows processed: {total_rows}")
    print(f"  Transformations applied: {transformation_count}")


if __name__ == "__main__":
    main()
