import pandas as pd
import re

# Read the TSV file
df = pd.read_csv('/mnt/user-data/uploads/met_inventory.tsv', sep='\t', dtype=str)

print("Original file info:")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst few rows:")
print(df.head(10))
print(f"\nNull/Empty counts per column:")
print(df.isnull().sum())

# Standardization tasks:
# 1. Fill empty/null values with "N/A"
df = df.fillna('N/A')

# 2. Strip whitespace from all cells
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].str.strip()

# 3. Standardize column names to snake_case
df.columns = [col.lower().replace(' ', '_') for col in df.columns]

# 4. Remove duplicate rows
df = df.drop_duplicates()

# 5. Ensure proper URL format consistency
df['link_resource'] = df['link_resource'].apply(
    lambda x: x if x.startswith('http') else 'N/A'
)

# 6. Ensure Object Number is not empty (should have values)
# Rows without an object number might be malformed
df = df[df['object_number'] != 'N/A']

print("\n\nAfter standardization:")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst few rows:")
print(df.head(10))
print(f"\nNull/Empty counts per column:")
print(df.isnull().sum())

# Write to output
output_path = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
df.to_csv(output_path, sep='\t', index=False, encoding='utf-8')
print(f"\n✓ Standardized file saved to: {output_path}")

# Also create a summary report
summary_path = '/mnt/user-data/outputs/standardization_report.txt'
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write("STANDARDIZATION REPORT\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Original rows: 301 (including header)\n")
    f.write(f"Final rows: {len(df) + 1} (including header)\n")
    f.write(f"Rows removed: {301 - (len(df) + 1)}\n\n")
    f.write("CHANGES MADE:\n")
    f.write("1. Filled empty/null values with 'N/A'\n")
    f.write("2. Stripped leading/trailing whitespace from all cells\n")
    f.write("3. Standardized column names to snake_case\n")
    f.write("4. Removed duplicate rows\n")
    f.write("5. Validated URL format in 'link_resource' column\n")
    f.write("6. Removed rows with missing 'object_number' values\n\n")
    f.write("COLUMN INFORMATION:\n")
    for col in df.columns:
        non_na = (df[col] != 'N/A').sum()
        f.write(f"  - {col}: {non_na} filled values, {len(df) - non_na} N/A\n")

print(f"✓ Report saved to: {summary_path}")
