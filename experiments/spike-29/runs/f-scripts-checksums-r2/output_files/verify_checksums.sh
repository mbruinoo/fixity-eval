#!/bin/bash
# Checksum verification script for standardized TSV file

echo "=== Checksum Verification for Met Museum Inventory ==="
echo ""

SOURCE_FILE="/mnt/user-data/uploads/met_inventory.tsv"
OUTPUT_FILE="/mnt/user-data/outputs/met_inventory_standardized.tsv"

EXPECTED_SOURCE_CHECKSUM="e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf"
EXPECTED_OUTPUT_CHECKSUM="37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523"

echo "Verifying source file:"
ACTUAL_SOURCE=$(sha256sum "$SOURCE_FILE" | cut -d' ' -f1)
echo "  Path: $SOURCE_FILE"
echo "  Expected: $EXPECTED_SOURCE_CHECKSUM"
echo "  Actual:   $ACTUAL_SOURCE"
if [ "$ACTUAL_SOURCE" = "$EXPECTED_SOURCE_CHECKSUM" ]; then
    echo "  Status: ✓ MATCH"
else
    echo "  Status: ✗ MISMATCH"
fi

echo ""
echo "Verifying output file:"
ACTUAL_OUTPUT=$(sha256sum "$OUTPUT_FILE" | cut -d' ' -f1)
echo "  Path: $OUTPUT_FILE"
echo "  Expected: $EXPECTED_OUTPUT_CHECKSUM"
echo "  Actual:   $ACTUAL_OUTPUT"
if [ "$ACTUAL_OUTPUT" = "$EXPECTED_OUTPUT_CHECKSUM" ]; then
    echo "  Status: ✓ MATCH"
else
    echo "  Status: ✗ MISMATCH"
fi

echo ""
echo "File statistics:"
echo "  Source size:  $(stat -f%z "$SOURCE_FILE" 2>/dev/null || stat -c%s "$SOURCE_FILE") bytes"
echo "  Output size:  $(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE") bytes"
echo ""
echo "Sample comparison (first 5 lines of source):"
head -5 "$SOURCE_FILE" | cat -A
echo ""
echo "Sample comparison (first 5 lines of output):"
head -5 "$OUTPUT_FILE" | cat -A
