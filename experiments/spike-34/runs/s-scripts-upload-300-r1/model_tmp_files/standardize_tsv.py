import csv
import sys
from pathlib import Path

def standardize_tsv(input_file, output_file):
    """
    Standardize the TSV file by:
    1. Ensuring proper tab-separated format
    2. Removing empty rows
    3. Handling missing Title values (empty cells)
    4. Ensuring consistent column structure
    5. Properly quoting fields with special characters
    """
    
    rows = []
    
    # Read the file with tab delimiter
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            rows.append(row)
    
    # Process rows
    standardized_rows = []
    for i, row in enumerate(rows):
        # Keep header row
        if i == 0:
            standardized_rows.append(row)
            continue
        
        # Skip completely empty rows
        if not any(cell.strip() for cell in row):
            continue
        
        # Ensure we have exactly 4 columns
        while len(row) < 4:
            row.append('')
        row = row[:4]
        
        # Trim whitespace from each cell
        row = [cell.strip() for cell in row]
        
        standardized_rows.append(row)
    
    # Write standardized output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(standardized_rows)
    
    return len(standardized_rows) - 1  # Excluding header

if __name__ == '__main__':
    input_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    
    num_rows = standardize_tsv(input_file, output_file)
    print(f"✓ Standardization complete!")
    print(f"  Input file: {input_file}")
    print(f"  Output file: {output_file}")
    print(f"  Data rows processed: {num_rows}")
