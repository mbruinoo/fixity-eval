import csv
import sys
from pathlib import Path

def standardize_met_inventory(input_file, output_file):
    """
    Standardize the Met Museum inventory TSV file by:
    1. Ensuring consistent tab-separated format
    2. Handling empty fields properly
    3. Removing extra whitespace while preserving data integrity
    4. Validating and standardizing data
    """
    
    rows_read = 0
    rows_written = 0
    issues_found = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile, delimiter='\t')
            
            if reader.fieldnames is None:
                print("Error: Could not read TSV file")
                return
            
            fieldnames = reader.fieldnames
            print(f"Found columns: {fieldnames}")
            
            with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')
                writer.writeheader()
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (accounting for header)
                    rows_read += 1
                    standardized_row = {}
                    
                    for field in fieldnames:
                        value = row.get(field, '').strip()
                        
                        # Remove excessive whitespace but keep single spaces
                        value = ' '.join(value.split())
                        
                        standardized_row[field] = value
                        
                        # Check for potential issues
                        if not value and field not in ['Title']:  # Title can be empty
                            issues_found.append(f"Row {row_num}: Empty {field}")
                    
                    # Check for rows with minimal data
                    non_empty_fields = sum(1 for v in standardized_row.values() if v)
                    if non_empty_fields < 2:
                        issues_found.append(f"Row {row_num}: Very few non-empty fields ({non_empty_fields})")
                    
                    writer.writerow(standardized_row)
                    rows_written += 1
        
        # Print summary
        print(f"\n✓ Standardization complete!")
        print(f"  Rows read: {rows_read}")
        print(f"  Rows written: {rows_written}")
        
        if issues_found:
            print(f"\nData quality issues found ({len(issues_found)}):")
            for issue in issues_found[:20]:  # Show first 20 issues
                print(f"  - {issue}")
            if len(issues_found) > 20:
                print(f"  ... and {len(issues_found) - 20} more issues")
        else:
            print("\nNo data quality issues found!")
    
    except Exception as e:
        print(f"Error processing file: {e}")
        return False
    
    return True

if __name__ == "__main__":
    input_path = "/mnt/user-data/uploads/met_inventory.tsv"
    output_path = "/mnt/user-data/outputs/met_inventory_standardized.tsv"
    
    success = standardize_met_inventory(input_path, output_path)
    if success:
        print(f"\nOutput saved to: {output_path}")
    sys.exit(0 if success else 1)
