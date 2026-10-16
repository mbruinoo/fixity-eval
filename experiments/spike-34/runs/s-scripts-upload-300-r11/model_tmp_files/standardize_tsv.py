import pandas as pd
import sys

# Read the TSV file
df = pd.read_csv('/mnt/user-data/uploads/met_inventory.tsv', sep='\t', dtype=str)

print("Original file analysis:")
print(f"Shape: {df.shape}")
print(f"\nColumn names: {list(df.columns)}")
print(f"\nFirst few rows:")
print(df.head())
print(f"\nMissing values per column:")
print(df.isnull().sum())
print(f"\nData types:")
print(df.dtypes)

# Standardization steps
print("\n" + "="*60)
print("STANDARDIZATION STEPS:")
print("="*60)

# 1. Fill empty Title cells with "Untitled" or empty string (depending on preference)
# Let's mark them as "Untitled"
df['Title'] = df['Title'].fillna('').str.strip()
df['Title'] = df['Title'].apply(lambda x: 'Untitled' if x == '' else x)
print(f"✓ Filled missing titles with 'Untitled'")

# 2. Clean up all string columns
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].fillna('').str.strip()
print(f"✓ Trimmed whitespace from all columns")

# 3. Remove any completely empty rows
df = df[(df['Object Date'] != '') | (df['Title'] != 'Untitled') | (df['Object Number'] != '')]
print(f"✓ Removed completely empty rows")

# 4. Standardize URL format (ensure consistency)
df['Link Resource'] = df['Link Resource'].apply(lambda x: x if x.startswith('http') else '')
print(f"✓ Validated URL format")

# 5. Check for and report on any rows with missing critical fields
missing_critical = df[df['Object Number'] == '']
if len(missing_critical) > 0:
    print(f"\n⚠ Warning: {len(missing_critical)} rows have missing Object Numbers")

# 6. Ensure no duplicate headers
df = df.reset_index(drop=True)
print(f"✓ Reset index")

# Save standardized file
output_path = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
df.to_csv(output_path, sep='\t', index=False, quoting=1)  # quoting=1 means QUOTE_ALL
print(f"\n✓ Saved standardized file to {output_path}")

print(f"\nFinal shape: {df.shape}")
print(f"\nFirst few rows of standardized data:")
print(df.head(10))

# Create a summary report
summary = f"""
STANDARDIZATION REPORT
======================
Total records: {len(df)}
Columns: {len(df.columns)}

Column Summary:
- Object Date: {df['Object Date'].notna().sum()} non-empty
- Title: {(df['Title'] != 'Untitled').sum()} with actual titles
- Object Number: {df['Object Number'].notna().sum()} non-empty
- Link Resource: {df['Link Resource'].notna().sum()} non-empty

Actions Performed:
1. Filled empty titles with 'Untitled'
2. Trimmed whitespace from all fields
3. Removed completely empty rows
4. Validated URL format
5. Reset index
"""

with open('/mnt/user-data/outputs/standardization_report.txt', 'w') as f:
    f.write(summary)

print("\n" + summary)
