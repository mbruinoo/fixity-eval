#!/bin/bash
# Verify checksums of source and standardized TSV files

echo "=== TSV Standardization Checksum Verification ==="
echo ""

SOURCE_FILE="/mnt/user-data/uploads/met_inventory.tsv"
OUTPUT_FILE="/mnt/user-data/outputs/met_inventory_standardized.tsv"

if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: Source file not found: $SOURCE_FILE"
    exit 1
fi

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Error: Output file not found: $OUTPUT_FILE"
    exit 1
fi

echo "Source File:"
echo "  Path: $SOURCE_FILE"
echo "  SHA256: $(sha256sum "$SOURCE_FILE" | awk '{print $1}')"
echo "  Size: $(wc -c < "$SOURCE_FILE") bytes"
echo "  Lines: $(wc -l < "$SOURCE_FILE")"
echo ""

echo "Standardized Output File:"
echo "  Path: $OUTPUT_FILE"
echo "  SHA256: $(sha256sum "$OUTPUT_FILE" | awk '{print $1}')"
echo "  Size: $(wc -c < "$OUTPUT_FILE") bytes"
echo "  Lines: $(wc -l < "$OUTPUT_FILE")"
echo ""

# Create a checksum file for archival purposes
cat > "$OUTPUT_FILE.sha256" << EOF
$(sha256sum "$SOURCE_FILE" | awk '{print $1}')  met_inventory.tsv
$(sha256sum "$OUTPUT_FILE" | awk '{print $1}')  met_inventory_standardized.tsv
EOF

echo "✓ Checksums saved to: ${OUTPUT_FILE}.sha256"
echo ""
echo "To verify integrity later, run:"
echo "  sha256sum -c ${OUTPUT_FILE}.sha256"
