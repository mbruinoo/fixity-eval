#!/usr/bin/env python3
import pandas as pd
import re

# Read the TSV file
df = pd.read_csv('/mnt/user-data/uploads/met_inventory.tsv', sep='\t', dtype=str)

# Display original structure
print("=" * 60)
print("ORIGINAL FILE ANALYSIS")
print("=" * 60)
print(f"Columns: {df.columns.tolist()}")
print(f"Shape: {df.shape}")
print(f"Missing values:\n{df.isnull().sum()}\n")

# Standardize column names
df.columns = ['Object_Date', 'Title', 'Object_Number', 'Link_Resource']

# Clean up whitespace in all cells using map (pandas 2.1+ compatible)
df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

# Handle empty strings as NaN for consistency
df = df.replace('', None)

# Standardize the Link_Resource column
df['Link_Resource'] = df['Link_Resource'].str.strip()

# Remove duplicate whitespace within cells
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].str.replace(r'\s+', ' ', regex=True)

# Sort by Object_Date
def extract_sort_key(date_str):
    """Extract a sortable year from various date formats"""
    if pd.isna(date_str):
        return (9999, 0)  # Put unknown dates at the end
    
    date_str = str(date_str).lower()
    
    # Handle BCE/BC dates
    if 'bce' in date_str or 'b.c' in date_str:
        years = re.findall(r'\d{1,4}', date_str)
        if years:
            return (0, -int(years[0]))  # BCE dates sorted first, in reverse order
    
    # Extract first year found
    years = re.findall(r'\d{1,4}', date_str)
    if years:
        year = int(years[0])
        return (1, year)  # CE dates after BCE
    
    return (9999, 0)

df['sort_key'] = df['Object_Date'].apply(extract_sort_key)
df = df.sort_values('sort_key').drop('sort_key', axis=1)
df = df.reset_index(drop=True)

# Add row numbers
df.insert(0, 'Row_ID', range(1, len(df) + 1))

# Save standardized file
output_path = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
df.to_csv(output_path, sep='\t', index=False)

print("=" * 60)
print("STANDARDIZATION COMPLETE")
print("=" * 60)
print(f"Output file: {output_path}")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nMissing values by column:")
print(df.isnull().sum())
print(f"\nFirst 15 rows of standardized data:")
print(df.head(15).to_string())
