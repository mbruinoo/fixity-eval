#!/usr/bin/env python3
"""
Standardize Met Museum Inventory TSV file
Preserves fixity through checksums of source and result components
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

class FixityPreserver:
    """Handles checksumming of data components for integrity verification"""
    
    def __init__(self):
        self.checksums = {}
    
    def hash_string(self, text: str, hash_type: str = 'sha256') -> str:
        """Generate SHA256 hash of a string"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def hash_row(self, row_dict: Dict, row_number: int) -> str:
        """Generate hash of a single row"""
        row_str = json.dumps(row_dict, sort_keys=True, ensure_ascii=False)
        return self.hash_string(row_str)
    
    def record_checksum(self, key: str, value: str):
        """Record a checksum with timestamp"""
        self.checksums[key] = {
            'hash': value,
            'timestamp': datetime.now().isoformat()
        }
    
    def export_checksums(self, filepath: str):
        """Export checksums to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.checksums, f, indent=2, ensure_ascii=False)

class MetInventoryStandardizer:
    """Standardize Met Museum inventory data"""
    
    # Define standardized column names
    STANDARD_COLUMNS = [
        'object_date',
        'title',
        'object_number',
        'resource_link'
    ]
    
    def __init__(self):
        self.fixity = FixityPreserver()
        self.source_rows = []
        self.standardized_rows = []
    
    def normalize_date(self, date_str: str) -> str:
        """Normalize date strings for consistency"""
        if not date_str or date_str.strip() == '':
            return ''
        
        date_str = date_str.strip()
        # Already fairly standardized, but trim extra spaces
        return ' '.join(date_str.split())
    
    def normalize_title(self, title: str) -> str:
        """Normalize title field"""
        if not title or title.strip() == '':
            return '[Untitled]'
        
        title = title.strip()
        return title
    
    def normalize_object_number(self, obj_num: str) -> str:
        """Normalize object number"""
        if not obj_num or obj_num.strip() == '':
            return ''
        
        return obj_num.strip()
    
    def normalize_link(self, link: str) -> str:
        """Normalize resource link"""
        if not link or link.strip() == '':
            return ''
        
        link = link.strip()
        # Ensure consistent URL format (already are, but validate)
        if link and not link.startswith('http'):
            return ''
        
        return link
    
    def read_source(self, filepath: str) -> Tuple[List[Dict], str]:
        """Read source TSV file and generate checksum"""
        rows = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            # Read with tab delimiter
            reader = csv.DictReader(f, delimiter='\t')
            
            for row_num, row in enumerate(reader, start=2):  # start=2 for header
                rows.append(row)
                self.source_rows.append(row)
        
        # Generate checksum of source file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            source_hash = self.fixity.hash_string(content)
            self.fixity.record_checksum('source_file', source_hash)
        
        return rows, source_hash
    
    def standardize_rows(self, rows: List[Dict]) -> List[Dict]:
        """Standardize all rows"""
        standardized = []
        row_hashes = {}
        
        for row_num, row in enumerate(rows, start=2):
            # Original row hash
            original_hash = self.fixity.hash_row(row, row_num)
            
            # Standardize
            standardized_row = {
                'object_date': self.normalize_date(row.get('Object Date', '')),
                'title': self.normalize_title(row.get('Title', '')),
                'object_number': self.normalize_object_number(row.get('Object Number', '')),
                'resource_link': self.normalize_link(row.get('Link Resource', ''))
            }
            
            standardized.append(standardized_row)
            self.standardized_rows.append(standardized_row)
            
            # New row hash
            new_hash = self.fixity.hash_row(standardized_row, row_num)
            
            row_hashes[f'row_{row_num}'] = {
                'original_hash': original_hash,
                'standardized_hash': new_hash,
                'object_number': standardized_row['object_number']
            }
        
        self.fixity.checksums['row_transformations'] = row_hashes
        return standardized
    
    def write_output(self, rows: List[Dict], filepath: str) -> str:
        """Write standardized TSV and generate checksum"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.STANDARD_COLUMNS, delimiter='\t')
            writer.writeheader()
            writer.writerows(rows)
        
        # Generate checksum of output
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            output_hash = self.fixity.hash_string(content)
            self.fixity.record_checksum('output_file', output_hash)
        
        return output_hash
    
    def generate_report(self, filepath: str, source_hash: str, output_hash: str):
        """Generate detailed standardization report"""
        report = f"""# Met Museum Inventory Standardization Report

## Summary
- **Standardization Date**: {datetime.now().isoformat()}
- **Source Rows**: {len(self.source_rows)}
- **Output Rows**: {len(self.standardized_rows)}
- **Status**: {'SUCCESS' if len(self.source_rows) == len(self.standardized_rows) else 'WARNING'}

## Fixity Information

### Source File
- **Hash (SHA256)**: {source_hash}
- **Encoding**: UTF-8
- **Format**: Tab-Separated Values (TSV)
- **Original Columns**: Object Date, Title, Object Number, Link Resource

### Output File
- **Hash (SHA256)**: {output_hash}
- **Encoding**: UTF-8
- **Format**: Tab-Separated Values (TSV)
- **Standardized Columns**: object_date, title, object_number, resource_link

## Standardization Rules Applied

1. **Column Names**: Converted to lowercase with underscores
   - "Object Date" → "object_date"
   - "Title" → "title"
   - "Object Number" → "object_number"
   - "Link Resource" → "resource_link"

2. **object_date**: 
   - Trimmed whitespace
   - Normalized internal spacing

3. **title**:
   - Trimmed whitespace
   - Empty titles replaced with "[Untitled]"
   - Preserved original punctuation and special characters

4. **object_number**:
   - Trimmed whitespace
   - Preserved complex numbering schemes (e.g., "36.120.598a, b")

5. **resource_link**:
   - Trimmed whitespace
   - Validated URL format (must start with http)
   - Empty URLs preserved as empty strings

## Data Quality Notes

- **Total Records Processed**: {len(self.source_rows)}
- **Records with Empty Titles**: {sum(1 for r in self.standardized_rows if r['title'] == '[Untitled]')}
- **Records with Missing Object Numbers**: {sum(1 for r in self.standardized_rows if r['object_number'] == '')}
- **Records with Missing Links**: {sum(1 for r in self.standardized_rows if r['resource_link'] == '')}

## Checksum Verification

To verify data integrity:

```bash
# Verify source file
sha256sum met_inventory.tsv

# Verify output file
sha256sum met_inventory_standardized.tsv

# Compare checksums in checksums.json
cat checksums.json
```

Row-level checksums can be used to verify individual records have not been corrupted.

## Files Generated

1. **met_inventory_standardized.tsv** - Standardized data file
2. **checksums.json** - Complete checksum record
3. **standardization_report.md** - This report
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

def main():
    """Main execution"""
    print("Initializing Met Museum Inventory Standardizer...")
    
    standardizer = MetInventoryStandardizer()
    
    # Paths
    input_file = 'met_inventory.tsv'
    output_file = 'met_inventory_standardized.tsv'
    checksums_file = 'checksums.json'
    report_file = 'standardization_report.md'
    
    try:
        # Read source
        print(f"Reading source file: {input_file}")
        rows, source_hash = standardizer.read_source(input_file)
        print(f"  ✓ Read {len(rows)} rows")
        print(f"  ✓ Source hash: {source_hash[:16]}...")
        
        # Standardize
        print("Standardizing rows...")
        standardized = standardizer.standardize_rows(rows)
        print(f"  ✓ Standardized {len(standardized)} rows")
        
        # Write output
        print(f"Writing output file: {output_file}")
        output_hash = standardizer.write_output(standardized, output_file)
        print(f"  ✓ Output hash: {output_hash[:16]}...")
        
        # Save checksums
        print(f"Saving checksums: {checksums_file}")
        standardizer.fixity.export_checksums(checksums_file)
        print(f"  ✓ Checksums saved")
        
        # Generate report
        print(f"Generating report: {report_file}")
        standardizer.generate_report(report_file, source_hash, output_hash)
        print(f"  ✓ Report generated")
        
        print("\n✓ Standardization complete!")
        print(f"\nGenerated files:")
        print(f"  - {output_file}")
        print(f"  - {checksums_file}")
        print(f"  - {report_file}")
        
    except Exception as e:
        print(f"\n✗ Error during standardization: {e}")
        raise

if __name__ == '__main__':
    main()
