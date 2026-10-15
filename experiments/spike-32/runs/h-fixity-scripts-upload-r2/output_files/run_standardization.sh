#!/bin/bash
# TSV Standardization with Checksum Verification Script

set -e

INPUT_FILE="/mnt/user-data/outputs/met_inventory.tsv"
OUTPUT_FILE="/mnt/user-data/outputs/met_inventory_standardized.tsv"
LOG_FILE="/mnt/user-data/outputs/met_inventory_standardization.log"
CHECKSUM_FILE="/mnt/user-data/outputs/CHECKSUMS.txt"

echo "=========================================="
echo "TSV Standardization with Fixity Verification"
echo "=========================================="
echo ""

# Compute source file checksum
echo "Computing source file checksum..."
SOURCE_SHA256=$(sha256sum "$INPUT_FILE" | awk '{print $1}')
echo "Source file SHA-256: $SOURCE_SHA256"
echo ""

# Run Python standardization script
echo "Running standardization script..."
python3 /mnt/user-data/outputs/standardize_tsv.py "$INPUT_FILE" "$OUTPUT_FILE" "$LOG_FILE"
echo ""

# Compute output file checksum
echo "Computing output file checksum..."
OUTPUT_SHA256=$(sha256sum "$OUTPUT_FILE" | awk '{print $1}')
echo "Output file SHA-256: $OUTPUT_SHA256"
echo ""

# Create comprehensive checksum record
echo "Creating checksum verification file..."
cat > "$CHECKSUM_FILE" << EOF
# TSV Standardization Checksum Verification Record
# Generated: $(date -Iseconds)

## Source File
File: $INPUT_FILE
SHA-256: $SOURCE_SHA256

## Output File
File: $OUTPUT_FILE
SHA-256: $OUTPUT_SHA256

## Verification Instructions
To verify source file integrity:
  sha256sum -c << EOF2
$SOURCE_SHA256  $INPUT_FILE
EOF2

To verify output file integrity:
  sha256sum -c << EOF2
$OUTPUT_SHA256  $OUTPUT_FILE
EOF2

## File Statistics
Source file size: $(stat -f%z "$INPUT_FILE" 2>/dev/null || stat -c%s "$INPUT_FILE") bytes
Output file size: $(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE") bytes

Source file line count: $(wc -l < "$INPUT_FILE") lines
Output file line count: $(wc -l < "$OUTPUT_FILE") lines
EOF

echo "Checksum verification file created: $CHECKSUM_FILE"
echo ""

# Display final summary
echo "=========================================="
echo "Standardization Complete"
echo "=========================================="
echo ""
echo "Files created:"
echo "  - $OUTPUT_FILE"
echo "  - $LOG_FILE"
echo "  - $CHECKSUM_FILE"
echo ""
echo "To verify integrity, run:"
echo "  cat $CHECKSUM_FILE"
