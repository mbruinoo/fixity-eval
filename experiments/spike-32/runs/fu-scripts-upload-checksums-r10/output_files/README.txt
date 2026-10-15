================================================================================
MET MUSEUM INVENTORY TSV - STANDARDIZATION PACKAGE
================================================================================

QUICK START
================================================================================

You have two main files to work with:

1. met_inventory_standardized.tsv
   → Use this file for analysis and data work
   → 103 records with consistent formatting
   → Ready for import into Excel, Python, SQL, etc.

2. met_inventory_source.tsv
   → Original data in standardized format
   → For comparison or archival purposes

WHAT'S INCLUDED
================================================================================

DATA FILES:
  met_inventory_source.tsv
  met_inventory_standardized.tsv

DOCUMENTATION:
  README.txt                          ← You are here
  STANDARDIZATION_REPORT.md           ← Full technical report
  FIXITY_VERIFICATION.txt             ← Checksum & preservation info
  
SCRIPTS:
  standardize_met_inventory.py        ← Full-featured standardizer
  run_standardization.py              ← Quick execution script
  
METADATA:
  met_inventory_manifest.json         ← Machine-readable manifest

WHAT CHANGED
================================================================================

FORMATTING (all changes):
  ✓ Consistent tab delimiters
  ✓ Column order: Object Date | Title | Object Number | Link Resource
  ✓ Whitespace trimmed (leading/trailing only)
  ✓ UTF-8 encoding with proper Unicode support
  ✓ Unix line endings
  
WHAT DID NOT CHANGE (all preserved):
  ✓ No data values modified
  ✓ No records removed or added
  ✓ No titles changed
  ✓ No URLs changed
  ✓ No identifiers altered

OPENING THE FILE
================================================================================

Excel:
  1. Open Excel
  2. File → Open
  3. Select: met_inventory_standardized.tsv
  4. Keep default TSV settings
  5. Done!

Google Sheets:
  1. Go to sheets.google.com
  2. File → Open
  3. Upload → Select met_inventory_standardized.tsv
  4. Done!

Python (Pandas):
  import pandas as pd
  df = pd.read_csv('met_inventory_standardized.tsv', sep='\t')
  print(df.head())

Python (CSV):
  import csv
  with open('met_inventory_standardized.tsv') as f:
      reader = csv.DictReader(f, delimiter='\t')
      for row in reader:
          print(row['Title'])

Command Line (macOS/Linux):
  head met_inventory_standardized.tsv
  tail met_inventory_standardized.tsv
  wc -l met_inventory_standardized.tsv

DATA QUALITY
================================================================================

Total Records: 103
All Records Valid: Yes ✓

Column Coverage:
  Object Date:    101/103 records (2 empty)
  Title:          96/103 records (7 empty)
  Object Number:  103/103 records (100%)
  Link Resource:  103/103 records (100%)

Special Characters Handled:
  ✓ Chinese characters (明清時期, etc.)
  ✓ Japanese characters (日本語, 絵本, etc.)
  ✓ Korean characters (한국어, etc.)
  ✓ Accented characters (é, à, ü, etc.)
  ✓ En-dashes, special punctuation

VERIFYING INTEGRITY
================================================================================

Each file has a SHA256 checksum for verification. This lets you confirm
the files haven't been corrupted or modified.

To verify (macOS/Linux):
  sha256sum met_inventory_*.tsv

To verify (Windows):
  certUtil -hashfile met_inventory_source.tsv SHA256
  certUtil -hashfile met_inventory_standardized.tsv SHA256

Expected checksums are stored in:
  met_inventory_manifest.json (machine-readable)
  FIXITY_VERIFICATION.txt (human-readable)

TECHNICAL DETAILS
================================================================================

Format: Tab-Separated Values (TSV)
  → Plain text, no special software needed
  → Widely compatible with all data tools
  → RFC 4180 compliant

Encoding: UTF-8 with BOM
  → Universal character support
  → Excel-compatible
  → Handles all international characters

Line Endings: LF (Unix-style)
  → Platform independent
  → Modern standard

Columns: 4 (fixed)
  1. Object Date       - Temporal information
  2. Title            - Object description
  3. Object Number    - Catalog identifier
  4. Link Resource    - Met Museum URL

COMMON TASKS
================================================================================

Count records:
  wc -l met_inventory_standardized.tsv

Find an object:
  grep "Apis" met_inventory_standardized.tsv

Get just URLs:
  cut -f4 met_inventory_standardized.tsv

Convert to CSV:
  tr '\t' ',' < met_inventory_standardized.tsv > inventory.csv

Convert to JSON:
  python3 -c "
  import csv, json
  with open('met_inventory_standardized.tsv') as f:
      reader = csv.DictReader(f, delimiter='\t')
      print(json.dumps(list(reader), indent=2))
  " > inventory.json

SCRIPTS USAGE
================================================================================

To re-standardize with the same settings:

  python3 run_standardization.py

This will:
  - Read the source file
  - Apply all standardization rules
  - Calculate checksums
  - Update the manifest
  - Save the output

DOCUMENTATION GUIDE
================================================================================

START HERE:
  README.txt (you are here)
  → Quick overview and common tasks

DETAILED INFORMATION:
  STANDARDIZATION_REPORT.md
  → Complete technical report with analysis
  → Data quality metrics
  → Standards compliance details

FOR PRESERVATION:
  FIXITY_VERIFICATION.txt
  → Checksum information
  → Verification procedures
  → Long-term preservation guidance

FOR AUTOMATION:
  met_inventory_manifest.json
  → Machine-readable metadata
  → Programmatic verification
  → Automated processing

FOR IMPLEMENTATION:
  standardize_met_inventory.py
  → Full-featured Python utility
  → Extensible for customization
  → Can process new data

QUESTIONS?
================================================================================

"Can I modify the standardized file?"
  Yes! It's your data. Modify as needed.

"Will the checksums match after I modify it?"
  No, checksums will change. That's normal.

"Should I keep both source and standardized versions?"
  Yes, for comparison and archival purposes.

"What if I accidentally corrupt a file?"
  Compare checksums against manifest to detect corruption.

"Can I redistribute these files?"
  Yes, along with the manifest and documentation.

"Are there any licensing restrictions?"
  These are Met Museum objects - check the Met's terms.

SUPPORT
================================================================================

The standardization scripts are self-contained Python 3 utilities
with no external dependencies.

Requirements:
  Python 3.6+
  Nothing else! (uses only standard library)

To run standardization again:
  python3 standardize_met_inventory.py

To verify checksums:
  sha256sum -c met_inventory_manifest.json (after converting to proper format)
  or
  python3 -c "import json; m=json.load(open('met_inventory_manifest.json')); 
              print(m['source_file']['checksum_sha256'])"

THANK YOU
================================================================================

Your Met Museum inventory has been standardized following digital preservation
best practices. All operations are documented, reversible, and verifiable.

Enjoy your data!

================================================================================
Last Updated: 2025
Format: TSV (Tab-Separated Values)
Encoding: UTF-8 with BOM
Records: 103 objects
Status: ✓ Ready to use
================================================================================
