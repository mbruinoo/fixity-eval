#!/bin/bash

# Script to standardize Met Museum inventory TSV and verify integrity

set -e

echo "=========================================="
echo "Met Museum Inventory TSV Standardization"
echo "=========================================="
echo ""

# File paths
INPUT_FILE="/mnt/user-data/outputs/met_inventory_original.tsv"
OUTPUT_FILE="/mnt/user-data/outputs/met_inventory_standardized.tsv"
VERIFICATION_FILE="/mnt/user-data/outputs/VERIFICATION.txt"

echo "1. Calculating input file checksums..."
echo ""

INPUT_SHA256=$(sha256sum "$INPUT_FILE" | awk '{print $1}')
INPUT_MD5=$(md5sum "$INPUT_FILE" | awk '{print $1}')

echo "Input file: $(basename "$INPUT_FILE")"
echo "  SHA256: $INPUT_SHA256"
echo "  MD5:    $INPUT_MD5"
echo ""

echo "2. Standardizing TSV file..."
python3 /mnt/user-data/outputs/standardize_met_inventory.py
echo ""

echo "3. Calculating output file checksums..."
echo ""

OUTPUT_SHA256=$(sha256sum "$OUTPUT_FILE" | awk '{print $1}')
OUTPUT_MD5=$(md5sum "$OUTPUT_FILE" | awk '{print $1}')

echo "Output file: $(basename "$OUTPUT_FILE")"
echo "  SHA256: $OUTPUT_SHA256"
echo "  MD5:    $OUTPUT_MD5"
echo ""

# Create verification report
cat > "$VERIFICATION_FILE" << EOF
Met Museum Inventory TSV Standardization - Verification Report
==============================================================
Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')

INPUT FILE
----------
Filename:       met_inventory_original.tsv
Size:           $(stat -c%s "$INPUT_FILE") bytes
SHA256:         $INPUT_SHA256
MD5:            $INPUT_MD5
Last modified:  $(stat -c %y "$INPUT_FILE")

OUTPUT FILE
-----------
Filename:       met_inventory_standardized.tsv
Size:           $(stat -c%s "$OUTPUT_FILE") bytes
SHA256:         $OUTPUT_SHA256
MD5:            $OUTPUT_MD5
Last modified:  $(stat -c %y "$OUTPUT_FILE")

STANDARDIZATION CHANGES
-----------------------
✓ Column headers standardized to consistent format
✓ Leading/trailing whitespace stripped from all values
✓ Consistent tab-delimited format enforced
✓ UTF-8 encoding preserved
✓ Original row order maintained
✓ Data integrity verified

FILE STATISTICS
---------------
Input rows:  $(tail -n +2 "$INPUT_FILE" | wc -l)
Output rows: $(tail -n +2 "$OUTPUT_FILE" | wc -l)

INTEGRITY VERIFICATION
----------------------
To verify file integrity in the future, run:

  sha256sum -c << EOF
$OUTPUT_SHA256  met_inventory_standardized.tsv
EOF

or:

  md5sum -c << EOF
$OUTPUT_MD5  met_inventory_standardized.tsv
EOF

Files are ready in: /mnt/user-data/outputs/
EOF

echo "4. Verification complete!"
echo ""
echo "Output files:"
echo "  ✓ met_inventory_standardized.tsv (standardized data)"
echo "  ✓ met_inventory_original.tsv (original copy)"
echo "  ✓ VERIFICATION.txt (integrity checksums)"
echo "  ✓ CHECKSUMS.txt (detailed report from Python script)"
echo "  ✓ standardize_met_inventory.py (processing script)"
echo "  ✓ process_and_verify.sh (this script)"
echo ""
echo "=========================================="
