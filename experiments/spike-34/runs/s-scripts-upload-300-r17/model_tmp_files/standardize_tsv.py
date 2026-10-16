import pandas as pd
import re

# Read the TSV file
input_file = '/mnt/user-data/uploads/met_inventory.tsv'
output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'

# Read with tab delimiter
df = pd.read_csv(input_file, sep='\t', dtype=str)

print("Original shape:", df.shape)
print("\nColumn names:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head(10))

# Standardization steps
print("\n--- Standardizing ---\n")

# 1. Fill NaN values with empty strings
df = df.fillna('')

# 2. Strip leading/trailing whitespace from all cells
df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

# 3. Rename columns to standard format (remove trailing spaces, standardize naming)
df.columns = df.columns.str.strip()

# 4. Remove completely empty rows
df = df[(df != '').any(axis=1)]

# 5. Ensure no trailing/leading whitespace in the entire dataframe
df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

print("Standardized shape:", df.shape)
print("\nStandardized columns:", df.columns.tolist())
print("\nFirst few rows after standardization:")
print(df.head(10))

# Write to output file
df.to_csv(output_file, sep='\t', index=False, quoting=False)
print(f"\n✓ Standardized file saved to: {output_file}")

# Print summary statistics
print("\n--- Summary Statistics ---")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print(f"\nEmpty cells per column:")
for col in df.columns:
    empty_count = (df[col] == '').sum()
    print(f"  {col}: {empty_count}")

