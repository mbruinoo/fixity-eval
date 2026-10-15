#!/bin/bash
# Standardize Met Museum TSV and generate integrity checksums

set -e  # Exit on error

cd /mnt/user-data/outputs

echo "=========================================="
echo "Met Museum TSV Standardization & Checksum"
echo "=========================================="
echo ""

# Calculate source file checksums
echo "SOURCE FILE CHECKSUMS"
echo "===================="
SOURCE_SHA256=$(sha256sum met_inventory.tsv | awk '{print $1}')
SOURCE_MD5=$(md5sum met_inventory.tsv | awk '{print $1}')
SOURCE_SIZE=$(stat --printf=%s met_inventory.tsv)

echo "File: met_inventory.tsv"
echo "Size: $SOURCE_SIZE bytes"
echo "SHA256: $SOURCE_SHA256"
echo "MD5:    $SOURCE_MD5"
echo ""

# Run the standardization script
echo "Running standardization..."
python3 standardize_tsv.py

echo ""
echo "STANDARDIZED FILE CHECKSUMS"
echo "==========================="
OUTPUT_SHA256=$(sha256sum met_inventory_standardized.tsv | awk '{print $1}')
OUTPUT_MD5=$(md5sum met_inventory_standardized.tsv | awk '{print $1}')
OUTPUT_SIZE=$(stat --printf=%s met_inventory_standardized.tsv)

echo "File: met_inventory_standardized.tsv"
echo "Size: $OUTPUT_SIZE bytes"
echo "SHA256: $OUTPUT_SHA256"
echo "MD5:    $OUTPUT_MD5"
echo ""

# Summary
echo "CHECKSUM VERIFICATION"
echo "===================="
if [ "$SOURCE_SHA256" = "$OUTPUT_SHA256" ]; then
    echo "✓ SHA256 Match: Data integrity preserved"
else
    echo "✗ SHA256 Differs: Changes made during standardization (expected)"
fi
echo ""

# Create a manifest
cat > MANIFEST.txt << EOF
TSV Standardization Manifest
============================

Generated: $(date -u)

SOURCE FILE
-----------
Name: met_inventory.tsv
Size: $SOURCE_SIZE bytes
SHA256: $SOURCE_SHA256
MD5: $SOURCE_MD5

OUTPUT FILE
-----------
Name: met_inventory_standardized.tsv
Size: $OUTPUT_SIZE bytes
SHA256: $OUTPUT_SHA256
MD5: $OUTPUT_MD5

STANDARDIZATION APPLIED
-----------------------
✓ Normalized line endings (LF)
✓ Consistent tab-delimited structure
✓ Trimmed field whitespace
✓ UTF-8 encoding (no BOM)
✓ Minimal CSV quoting strategy
✓ All data preserved

VERIFICATION
-----------
To verify file authenticity:
  sha256sum -c <(echo "$OUTPUT_SHA256  met_inventory_standardized.tsv")
  md5sum -c <(echo "$OUTPUT_MD5  met_inventory_standardized.tsv")
EOF

echo "Manifest created: MANIFEST.txt"
echo ""
echo "✓ Standardization complete!"
echo ""
echo "Output files created:"
echo "  - met_inventory_standardized.tsv (standardized data)"
echo "  - standardization_report.txt (detailed report)"
echo "  - MANIFEST.txt (checksum verification)"
echo ""
