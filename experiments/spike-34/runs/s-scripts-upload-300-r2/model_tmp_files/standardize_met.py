#!/usr/bin/env python3
"""
Standardize the Met Museum inventory TSV file
"""

import csv
import html
import re

def clean_title(title):
    """Decode HTML entities and clean up title"""
    if not title:
        return ""
    # Decode HTML entities
    title = html.unescape(title)
    # Clean up whitespace
    title = title.strip()
    return title

def standardize_date(date_str):
    """Standardize date formatting"""
    if not date_str:
        return ""
    date_str = date_str.strip()
    return date_str

def standardize_object_number(obj_num):
    """Clean up object numbers"""
    if not obj_num:
        return ""
    obj_num = obj_num.strip()
    return obj_num

def process_inventory(input_file, output_file):
    """Process and standardize the inventory file"""
    
    rows = []
    skipped = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        headers = next(reader)
        
        print(f"Original headers: {headers}")
        print(f"Number of columns: {len(headers)}\n")
        
        for row_num, row in enumerate(reader, start=2):
            # Ensure we have the right number of columns
            while len(row) < len(headers):
                row.append("")
            
            # Skip completely empty rows
            if all(not cell.strip() for cell in row):
                skipped += 1
                continue
            
            # Standardize the row
            standardized_row = {
                'Object Date': standardize_date(row[0]),
                'Title': clean_title(row[1]),
                'Object Number': standardize_object_number(row[2]),
                'Link Resource': row[3].strip() if len(row) > 3 else ""
            }
            
            rows.append(standardized_row)
    
    # Write standardized output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Object Date', 'Title', 'Object Number', 'Link Resource'], delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Processed {len(rows)} rows")
    print(f"Skipped {skipped} empty rows")
    print(f"\nStandardized file saved to {output_file}")

if __name__ == "__main__":
    input_path = "/mnt/user-data/uploads/met_inventory.tsv"
    output_path = "/mnt/user-data/outputs/met_inventory_standardized.tsv"
    
    process_inventory(input_path, output_path)
    print("✓ Standardization complete!")
