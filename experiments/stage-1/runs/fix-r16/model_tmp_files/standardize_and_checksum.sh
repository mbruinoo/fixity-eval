#!/bin/bash

# Standardize TSV file with fixity preservation via checksums

INPUT_FILE="/mnt/user-data/uploads/met_inventory.tsv"
OUTPUT_FILE="/mnt/user-data/outputs/met_inventory_standardized.tsv"
CHECKSUM_FILE="/mnt/user-data/outputs/checksums.txt"

echo "=== Met Inventory TSV Standardization ==="
echo ""

# Checksum the original file
echo "Checksumming original file..."
ORIGINAL_SHA256=$(sha256sum "$INPUT_FILE" | awk '{print $1}')
ORIGINAL_MD5=$(md5sum "$INPUT_FILE" | awk '{print $1}')

echo "Original file checksums:"
echo "  SHA256: $ORIGINAL_SHA256"
echo "  MD5:    $ORIGINAL_MD5"
echo ""

# Standardize the TSV:
# 1. Ensure consistent tab delimiters
# 2. Remove trailing whitespace
# 3. Normalize line endings

echo "Processing and standardizing..."
{
    tail -n +1 "$INPUT_FILE" | sed 's/[[:space:]]*$//' | awk -F'\t' 'BEGIN {OFS="\t"} {
        # Remove trailing spaces from each field
        for(i=1; i<=NF; i++) {
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", $i)
        }
        print $0
    }'
} > "$OUTPUT_FILE"

echo "Standardization complete."
echo ""

# Checksum the output file
echo "Checksumming standardized file..."
OUTPUT_SHA256=$(sha256sum "$OUTPUT_FILE" | awk '{print $1}')
OUTPUT_MD5=$(md5sum "$OUTPUT_FILE" | awk '{print $1}')

echo "Output file checksums:"
echo "  SHA256: $OUTPUT_SHA256"
echo "  MD5:    $OUTPUT_MD5"
echo ""

# Save checksums to file
{
    echo "=== FIXITY PRESERVATION REPORT ==="
    echo "Generated: $(date)"
    echo ""
    echo "ORIGINAL FILE: met_inventory.tsv"
    echo "  SHA256: $ORIGINAL_SHA256"
    echo "  MD5:    $ORIGINAL_MD5"
    echo ""
    echo "STANDARDIZED FILE: met_inventory_standardized.tsv"
    echo "  SHA256: $OUTPUT_SHA256"
    echo "  MD5:    $OUTPUT_MD5"
    echo ""
    echo "STANDARDIZATION OPERATIONS:"
    echo "  - Ensured tab delimiters between all fields"
    echo "  - Removed trailing whitespace from lines and fields"
    echo "  - Normalized line endings (LF)"
    echo ""
    echo "FILE STATISTICS:"
    echo "  Original lines: $(wc -l < "$INPUT_FILE")"
    echo "  Standardized lines: $(wc -l < "$OUTPUT_FILE")"
    echo "  Original size: $(stat -f%z "$INPUT_FILE" 2>/dev/null || stat -c%s "$INPUT_FILE") bytes"
    echo "  Standardized size: $(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE") bytes"
} > "$CHECKSUM_FILE"

cat "$CHECKSUM_FILE"
echo ""
echo "Files saved to /mnt/user-data/outputs/"
