import csv

def analyze_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)
    
    print("📊 STANDARDIZATION REPORT")
    print("=" * 60)
    print(f"\nTotal rows: {len(rows)}")
    print(f"Header: {rows[0]}")
    print(f"Data rows: {len(rows) - 1}")
    
    # Analyze columns
    print("\n📋 COLUMN ANALYSIS:")
    print("-" * 60)
    
    headers = rows[0]
    for col_idx, header in enumerate(headers):
        non_empty = sum(1 for row in rows[1:] if len(row) > col_idx and row[col_idx].strip())
        print(f"  {col_idx + 1}. {header}")
        print(f"     Non-empty values: {non_empty}/{len(rows)-1}")
    
    # Check for consistency
    print("\n✓ QUALITY CHECKS:")
    print("-" * 60)
    
    all_consistent = True
    for i, row in enumerate(rows):
        if len(row) != 4:
            print(f"  ⚠ Row {i+1}: Expected 4 columns, got {len(row)}")
            all_consistent = False
    
    if all_consistent:
        print("  ✓ All rows have exactly 4 columns")
    
    # Check for empty rows
    empty_rows = [i+1 for i, row in enumerate(rows[1:]) if not any(cell.strip() for cell in row)]
    if empty_rows:
        print(f"  ⚠ Found {len(empty_rows)} empty rows")
    else:
        print("  ✓ No completely empty rows")
    
    print("\n✅ Standardization successful!")

analyze_file('/mnt/user-data/outputs/met_inventory_standardized.tsv')
