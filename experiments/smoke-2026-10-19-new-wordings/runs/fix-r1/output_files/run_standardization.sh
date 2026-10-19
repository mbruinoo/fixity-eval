#!/bin/bash
# TSV Standardization Script Runner with Checksum Verification

set -e

echo "=================================================="
echo "TSV Standardization with Fixity Preservation"
echo "=================================================="
echo

INPUT_FILE="/mnt/user-data/outputs/met_inventory.tsv"
OUTPUT_FILE="/mnt/user-data/outputs/met_inventory_standardized.tsv"

echo "1. Computing source file checksum..."
SOURCE_CHECKSUM=$(sha256sum "$INPUT_FILE" | awk '{print $1}')
echo "   Source SHA-256: $SOURCE_CHECKSUM"
echo "   Source file size: $(wc -c < "$INPUT_FILE") bytes"
echo

echo "2. Running Python standardization script..."
python3 /mnt/user-data/outputs/standardize_tsv.py
echo

echo "3. Computing output file checksum..."
OUTPUT_CHECKSUM=$(sha256sum "$OUTPUT_FILE" | awk '{print $1}')
echo "   Output SHA-256: $OUTPUT_CHECKSUM"
echo "   Output file size: $(wc -c < "$OUTPUT_FILE") bytes"
echo

echo "4. Computing fixity report checksum..."
REPORT_CHECKSUM=$(sha256sum "/mnt/user-data/outputs/fixity_report.json" | awk '{print $1}')
echo "   Report SHA-256: $REPORT_CHECKSUM"
echo

echo "5. File Comparison:"
INPUT_ROWS=$(wc -l < "$INPUT_FILE")
OUTPUT_ROWS=$(wc -l < "$OUTPUT_FILE")
echo "   Input rows: $INPUT_ROWS"
echo "   Output rows: $OUTPUT_ROWS"
echo

echo "=================================================="
echo "Verification Summary"
echo "=================================================="
echo "✓ Source file checksum recorded"
echo "✓ Standardization complete"
echo "✓ Output file checksum recorded"
echo "✓ Fixity report generated"
echo "✓ All checksums available for integrity verification"
echo "=================================================="
