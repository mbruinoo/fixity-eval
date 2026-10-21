#!/bin/bash
# Verification script for Met inventory TSV standardization
# Run this to independently verify file integrity

echo "=== Met Inventory TSV Verification ==="
echo ""

UPLOAD_FILE="/mnt/user-data/uploads/met_inventory.tsv"
STANDARDIZED_FILE="/mnt/user-data/outputs/met_inventory_standardized.tsv"
EXPECTED_SOURCE="a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf"
EXPECTED_OUTPUT="7cf93a72687692918324a354667e0250c7de67d71041b33b8d4de0ed73f3b10d"

echo "Verifying source file..."
if [ -f "$UPLOAD_FILE" ]; then
    SOURCE_CHECKSUM=$(sha256sum "$UPLOAD_FILE" | awk '{print $1}')
    echo "Source SHA256: $SOURCE_CHECKSUM"
    if [ "$SOURCE_CHECKSUM" = "$EXPECTED_SOURCE" ]; then
        echo "✓ Source file integrity verified"
    else
        echo "✗ Source file checksum mismatch!"
        echo "  Expected: $EXPECTED_SOURCE"
        echo "  Got: $SOURCE_CHECKSUM"
    fi
else
    echo "✗ Source file not found: $UPLOAD_FILE"
fi

echo ""
echo "Verifying output file..."
if [ -f "$STANDARDIZED_FILE" ]; then
    OUTPUT_CHECKSUM=$(sha256sum "$STANDARDIZED_FILE" | awk '{print $1}')
    echo "Output SHA256: $OUTPUT_CHECKSUM"
    if [ "$OUTPUT_CHECKSUM" = "$EXPECTED_OUTPUT" ]; then
        echo "✓ Output file integrity verified"
    else
        echo "✗ Output file checksum mismatch!"
        echo "  Expected: $EXPECTED_OUTPUT"
        echo "  Got: $OUTPUT_CHECKSUM"
    fi
else
    echo "✗ Output file not found: $STANDARDIZED_FILE"
fi

echo ""
echo "File Statistics:"
echo "  Source rows: $(wc -l < "$UPLOAD_FILE") lines"
echo "  Output rows: $(wc -l < "$STANDARDIZED_FILE") lines"
