#!/bin/bash
#
# Verify integrity of standardized TSV file
# Generates SHA-256 checksums for both source and output files
#

echo "=================================================="
echo "Met Museum Inventory TSV - Integrity Verification"
echo "=================================================="
echo

# Check if files exist
if [ ! -f "met_inventory.tsv" ]; then
    echo "ERROR: Source file 'met_inventory.tsv' not found"
    exit 1
fi

if [ ! -f "met_inventory_standardized.tsv" ]; then
    echo "ERROR: Output file 'met_inventory_standardized.tsv' not found"
    exit 1
fi

echo "Source file found: met_inventory.tsv"
echo "Output file found: met_inventory_standardized.tsv"
echo

# Calculate SHA-256 checksums
echo "Calculating SHA-256 checksums..."
echo

SOURCE_SHA=$(sha256sum met_inventory.tsv | awk '{print $1}')
OUTPUT_SHA=$(sha256sum met_inventory_standardized.tsv | awk '{print $1}')

echo "SOURCE FILE (met_inventory.tsv)"
echo "SHA-256: $SOURCE_SHA"
echo

echo "OUTPUT FILE (met_inventory_standardized.tsv)"
echo "SHA-256: $OUTPUT_SHA"
echo

# File statistics
echo "FILE STATISTICS"
echo "==============="
echo "Source file:"
wc -l met_inventory.tsv | awk '{print "  Total lines: " $1}'
du -h met_inventory.tsv | awk '{print "  File size: " $1}'
echo

echo "Output file:"
wc -l met_inventory_standardized.tsv | awk '{print "  Total lines: " $1}'
du -h met_inventory_standardized.tsv | awk '{print "  File size: " $1}'
echo

# Verify data integrity
echo "DATA INTEGRITY CHECKS"
echo "===================="
SOURCE_RECORDS=$(tail -n +2 met_inventory.tsv | wc -l)
OUTPUT_RECORDS=$(tail -n +2 met_inventory_standardized.tsv | wc -l)

echo "Source data rows: $SOURCE_RECORDS"
echo "Output data rows: $OUTPUT_RECORDS"

if [ "$SOURCE_RECORDS" -eq "$OUTPUT_RECORDS" ]; then
    echo "✓ Record count matches"
else
    echo "✗ Record count mismatch!"
fi
echo

# Check for valid UTF-8
echo "CHARACTER ENCODING VERIFICATION"
echo "==============================="
if file met_inventory_standardized.tsv | grep -q "UTF-8"; then
    echo "✓ Output file is UTF-8 encoded"
else
    echo "? Output file encoding: $(file met_inventory_standardized.tsv)"
fi
echo

# Save checksums to file
echo "Saving checksums to checksum file..."
cat > met_inventory_checksums.txt << EOF
Metropolitan Museum Inventory TSV Standardization
Integrity Verification Report
Generated: $(date)

Source file: met_inventory.tsv
SHA-256: $SOURCE_SHA

Output file: met_inventory_standardized.tsv
SHA-256: $OUTPUT_SHA

Record Count:
  Source: $SOURCE_RECORDS records
  Output: $OUTPUT_RECORDS records
  Status: $([ "$SOURCE_RECORDS" -eq "$OUTPUT_RECORDS" ] && echo "PASS" || echo "FAIL")

Verification Instructions:
To verify file integrity, run:
  sha256sum -c met_inventory_checksums.txt

EOF

echo "Checksums saved to: met_inventory_checksums.txt"
echo

echo "=================================================="
echo "Verification Complete"
echo "=================================================="
