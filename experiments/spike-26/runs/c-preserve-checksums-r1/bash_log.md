## call 1

```
cd /mnt/user-data/outputs && python3 << 'EOF'
import csv
import hashlib
from datetime import datetime
import json

# Read the original TSV
input_file = '/tmp/met_inventory.tsv'
output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
metadata_file = '/mnt/user-data/outputs/met_inventory_metadata.json'

# Read data
rows = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        rows.append(row)

# Standardize: clean up whitespace, handle empty values consistently
standardized_rows = []
for row in rows:
    cleaned_row = {
        'Object Date': row.get('Object Date', '').strip(),
        'Title': row.get('Title', '').strip(),
        'Object Number': row.get('Object Number', '').strip(),
        'Link Resource': row.get('Link Resource', '').strip()
    }
    standardized_rows.append(cleaned_row)

# Write standardized TSV with BOM for proper UTF-8 encoding
with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
    fieldnames = ['Object Date', 'Title', 'Object Number', 'Link Resource']
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    writer.writerows(standardized_rows)

# Calculate checksums for fixity
def calculate_file_hash(filepath, algorithm='sha256'):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def calculate_row_hash(row):
    """Calculate hash for each row for integrity verification"""
    row_str = '|'.join([row.get(k, '') for k in ['Object Date', 'Title', 'Object Number', 'Link Resource']])
    return hashlib.sha256(row_str.encode('utf-8')).hexdigest()

# Create metadata with checksums
metadata = {
    'standardization_info': {
        'timestamp': datetime.now().isoformat(),
        'source_file': 'met_inventory.tsv',
        'output_file': 'met_inventory_standardized.tsv',
        'total_records': len(standardized_rows),
        'encoding': 'UTF-8 with BOM',
        'delimiter': 'tab'
    },
    'file_checksums': {
        'sha256': calculate_file_hash(output_file),
        'algorithm': 'SHA-256'
    },
    'record_integrity': {
        'total_rows': len(standardized_rows),
        'row_hashes': [
            {
                'row_number': idx + 1,
                'object_number': row['Object Number'],
                'sha256': calculate_row_hash(row)
            }
            for idx, row in enumerate(standardized_rows)
        ]
    },
    'field_definitions': {
        'Object Date': 'Date range or specific date of object creation/collection',
        'Title': 'Name or description of the object',
        'Object Number': 'Museum accession or catalog number',
        'Link Resource': 'URL to the object in the Met Museum collection database'
    },
    'standardization_changes': [
        'Removed leading/trailing whitespace from all fields',
        'Standardized empty values as empty strings (not null)',
        'Added UTF-8 BOM for better cross-platform compatibility',
        'Verified tab-delimited format',
        'Maintained original character encoding for international text'
    ]
}

# Write metadata
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"✓ Standardized TSV created: {output_file}")
print(f"✓ Metadata with checksums: {metadata_file}")
print(f"\nFile Statistics:")
print(f"  Total records: {len(standardized_rows)}")
print(f"  File SHA-256: {calculate_file_hash(output_file)}")
print(f"\nFirst 3 rows to verify:")
for row in standardized_rows[:3]:
    print(f"  {row['Object Number']}: {row['Title'][:50]}...")

EOF

```

```

Traceback (most recent call last):
  File "<stdin>", line 13, in <module>
FileNotFoundError: [Errno 2] No such file or directory: '/tmp/met_inventory.tsv'

```

