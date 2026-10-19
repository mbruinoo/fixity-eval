#!/bin/bash

# Standardization script with fixity verification
set -e

cd /mnt/user-data/outputs

echo "=========================================="
echo "Running standardization with checksums..."
echo "=========================================="
echo ""

# Compute input file hash
INPUT_FILE="/mnt/user-data/uploads/met_inventory.tsv"
INPUT_HASH=$(sha256sum "$INPUT_FILE" | awk '{print $1}')
echo "Input file SHA256:"
echo "  $INPUT_HASH"
echo ""

# Run Python standardization script
python3 standardize_met_inventory.py

# Verify output file exists
OUTPUT_FILE="/mnt/user-data/outputs/met_inventory_standardized.tsv"
if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Error: Output file not created"
    exit 1
fi

# Compute output file hash
OUTPUT_HASH=$(sha256sum "$OUTPUT_FILE" | awk '{print $1}')
echo ""
echo "Output file SHA256:"
echo "  $OUTPUT_HASH"
echo ""

# Create checksums file
cat > CHECKSUMS.txt << EOF
Metropolitan Museum Inventory Standardization
Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

SOURCE FILE
-----------
Filename: met_inventory.tsv
Path: $INPUT_FILE
SHA256: $INPUT_HASH

OUTPUT FILE
-----------
Filename: met_inventory_standardized.tsv
Path: $OUTPUT_FILE
SHA256: $OUTPUT_HASH

LOG FILE
--------
Filename: standardization_report.txt
Path: /mnt/user-data/outputs/standardization_report.txt

VERIFICATION
To verify the output file has not been corrupted after download:

  sha256sum -c CHECKSUMS.txt

Or manually verify:

  sha256sum met_inventory_standardized.tsv
  # Should output: $OUTPUT_HASH

EOF

echo "✓ Checksums file created: CHECKSUMS.txt"
echo ""
echo "=========================================="
echo "All files ready in /mnt/user-data/outputs/"
echo "=========================================="
echo ""
echo "Files created:"
ls -lh /mnt/user-data/outputs/met_inventory* /mnt/user-data/outputs/standardization_report.txt /mnt/user-data/outputs/CHECKSUMS.txt 2>/dev/null || true
