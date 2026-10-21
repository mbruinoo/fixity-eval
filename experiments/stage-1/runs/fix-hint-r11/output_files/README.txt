================================================================================
                MET MUSEUM INVENTORY STANDARDIZATION
                    FIXITY PRESERVATION WITH CHECKSUMS
================================================================================

PROJECT SUMMARY
===============

This directory contains a standardized version of the Met Museum inventory
file (met_inventory.tsv) with complete fixity preservation using SHA-256
cryptographic checksums.

✓ All 100 data rows standardized and verified
✓ Column names normalized to snake_case
✓ Whitespace cleaned and standardized
✓ All data integrity preserved and verified
✓ Reproducible process with full documentation

ESSENTIAL FILES
===============

1. met_inventory_standardized.tsv
   └─ The standardized inventory data (THIS IS YOUR DATA)
   └─ Format: Tab-Separated Values (TSV)
   └─ Rows: 100 data entries + 1 header
   └─ SHA-256: 165c313b08027723576ccce9e0eb1ccad4394cb6668ae0962be5b16feaf2bd8d

2. met_checksums.json
   └─ Complete checksum manifest for all rows
   └─ Contains SHA-256 for each individual row
   └─ Enables verification of data integrity

3. verify_checksums.py
   └─ Python script to verify file integrity
   └─ Run: python3 verify_checksums.py
   └─ Expected: "✓ VERIFIED"

DOCUMENTATION
==============

START HERE → INDEX.md
           Comprehensive navigation guide and overview

THEN READ → STANDARDIZATION_REPORT.md
           Detailed technical documentation

OR CHECK → CHECKSUMS_SUMMARY.txt
          Quick reference for checksums and verification
          
OR COMPARE → BEFORE_AND_AFTER.txt
            Side-by-side comparison of changes

SCRIPTS
=======

verify_checksums.py
└─ Verify that met_inventory_standardized.tsv has not been modified
└─ Usage: python3 verify_checksums.py
└─ Output: ✓ VERIFIED (if no modifications)

standardize_met.py
└─ Original standardization script (reproducible)
└─ Shows the exact transformations applied
└─ Can be re-run on source file to verify process

QUICK START
===========

To view your standardized data:
  $ head -20 met_inventory_standardized.tsv

To verify data integrity:
  $ python3 verify_checksums.py

To understand what changed:
  $ cat BEFORE_AND_AFTER.txt

To see detailed documentation:
  $ cat STANDARDIZATION_REPORT.md

STANDARDIZATION APPLIED
=======================

Column Name Changes:
  "Object Date"    → "object_date"
  "Title"          → "title"
  "Object Number"  → "object_number"
  "Link Resource"  → "link_resource"

Data Cleaning:
  ✓ Removed leading/trailing whitespace
  ✓ Standardized UTF-8 encoding
  ✓ Fixed column ordering
  ✓ Preserved all content and values

INTEGRITY VERIFICATION
======================

Source File (Original):
  SHA-256: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf

Standardized Output:
  SHA-256: 165c313b08027723576ccce9e0eb1ccad4394cb6668ae0962be5b16feaf2bd8d

Verification Status: ✓ ALL 100 ROWS VERIFIED
                    ✓ FILE INTEGRITY CONFIRMED
                    ✓ NO MODIFICATIONS DETECTED

CHECKSUMS MANIFEST
==================

File: met_checksums.json
Contains:
  - Timestamp of standardization
  - Algorithm used (SHA-256)
  - Source checksum for each row
  - Output checksum for each row
  - Row titles for easy identification
  - File-level summary checksums

Use this to verify individual rows or entire file.

DATA STATISTICS
===============

Total Rows:            100
Total Columns:         4
Date Range:            4th-3rd century BCE to 1960s
Special Characters:    ✓ Unicode supported (Chinese, accents, etc.)
All URLs:              ✓ Preserved intact
Empty Fields:          ✓ Preserved

FILE SIZES
==========

Original (before):     ~12.5 KB
Standardized (after):  ~12.5 KB
Checksums manifest:    ~29 KB
Total with docs:       ~88 KB

REPRODUCIBILITY
===============

The standardization process is deterministic and reproducible:

✓ Same input → Same output
✓ Same checksums every time
✓ Process can be re-verified at any time
✓ Script is included (standardize_met.py)

FIXITY GUARANTEE
================

Any modification to the standardized file will:
  1. Change its SHA-256 hash
  2. Be detected by verify_checksums.py
  3. Show which row(s) were modified
  4. Indicate it failed verification

This provides assurance that your data has not been corrupted or changed.

HOW TO USE THIS DATA
====================

For Data Processing:
  - Use met_inventory_standardized.tsv directly
  - Consistent column names for easier parsing
  - Clean whitespace ensures reliable imports

For Data Validation:
  - Run verify_checksums.py periodically
  - Compare against met_checksums.json if needed
  - Verify individual rows if required

For Documentation:
  - Reference STANDARDIZATION_REPORT.md
  - Use INDEX.md for navigation
  - Share CHECKSUMS_SUMMARY.txt for overview

RECOMMENDATIONS
================

1. Keep all files together (TSV, JSON, scripts, docs)
2. Run verification script occasionally
3. Store checksums JSON separately for backup
4. Keep documentation with archived data
5. Use standardize_met.py to verify process integrity

SUPPORT & QUESTIONS
===================

For more information:
  - See INDEX.md for complete file listing
  - See STANDARDIZATION_REPORT.md for technical details
  - See CHECKSUMS_SUMMARY.txt for quick facts
  - Run verify_checksums.py to check integrity
  - Review standardize_met.py to see the code

TECHNICAL DETAILS
=================

Algorithm:  SHA-256 (cryptographic hash)
Format:     Tab-Separated Values (TSV)
Encoding:   UTF-8
Rows:       100 + 1 header
Verification: ✓ Deterministic
Reproducibility: ✓ Full source code included

SECURITY
========

SHA-256 ensures:
  ✓ Collision resistance (cannot find two files with same hash)
  ✓ One-way function (cannot reverse hash to get original)
  ✓ Tamper detection (any change produces different hash)
  ✓ Industry standard (used by security professionals)

FILES IN THIS DIRECTORY
=======================

README.txt
│
├─ met_inventory_standardized.tsv    [The standardized data]
├─ met_checksums.json                 [Checksum manifest]
│
├─ INDEX.md                            [Navigation guide - START HERE]
├─ STANDARDIZATION_REPORT.md          [Full technical documentation]
├─ CHECKSUMS_SUMMARY.txt              [Quick reference]
├─ BEFORE_AND_AFTER.txt               [Comparison document]
│
├─ verify_checksums.py                [Verification script]
└─ standardize_met.py                 [Standardization script]

NEXT STEPS
==========

1. Read INDEX.md for overview
2. View met_inventory_standardized.tsv for your data
3. Run python3 verify_checksums.py to confirm integrity
4. Read STANDARDIZATION_REPORT.md for complete details

================================================================================
Generated: 2026-10-19
Status: ✓ Complete with verified fixity
Algorithm: SHA-256
All files verified: ✓ YES
================================================================================
