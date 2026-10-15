#!/bin/bash
# Verify integrity of Metropolitan Museum TSV files using MD5 checksums
# Usage: ./verify_checksums.sh

echo "================================================================================"
echo "METROPOLITAN MUSEUM INVENTORY TSV - CHECKSUM VERIFICATION"
echo "================================================================================"
echo ""

SOURCE_FILE="met_inventory.tsv"
OUTPUT_FILE="met_inventory_standardized.tsv"

# Expected checksums
EXPECTED_SOURCE="0c89d1f1f2c6c5a7f3e8d4b9a2c5e7f0"
EXPECTED_OUTPUT="3a8f2c7e5b4d9a1c6e3f8b2a7c5d9e1f"

# Check if files exist
if [ ! -f "$SOURCE_FILE" ]; then
    echo "ERROR: Source file not found: $SOURCE_FILE"
    exit 1
fi

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "ERROR: Output file not found: $OUTPUT_FILE"
    exit 1
fi

echo "Verifying source file..."
SOURCE_CHECKSUM=$(md5sum "$SOURCE_FILE" | awk '{print $1}')
SOURCE_SIZE=$(stat -f%z "$SOURCE_FILE" 2>/dev/null || stat -c%s "$SOURCE_FILE" 2>/dev/null)

echo "  Filename: $SOURCE_FILE"
echo "  File size: $SOURCE_SIZE bytes"
echo "  Computed MD5: $SOURCE_CHECKSUM"
echo "  Expected MD5: $EXPECTED_SOURCE"

if [ "$SOURCE_CHECKSUM" = "$EXPECTED_SOURCE" ]; then
    echo "  Status: ✓ VERIFIED"
    SOURCE_STATUS=0
else
    echo "  Status: ✗ MISMATCH - File may be corrupted or different"
    SOURCE_STATUS=1
fi

echo ""
echo "Verifying output file..."
OUTPUT_CHECKSUM=$(md5sum "$OUTPUT_FILE" | awk '{print $1}')
OUTPUT_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null)

echo "  Filename: $OUTPUT_FILE"
echo "  File size: $OUTPUT_SIZE bytes"
echo "  Computed MD5: $OUTPUT_CHECKSUM"
echo "  Expected MD5: $EXPECTED_OUTPUT"

if [ "$OUTPUT_CHECKSUM" = "$EXPECTED_OUTPUT" ]; then
    echo "  Status: ✓ VERIFIED"
    OUTPUT_STATUS=0
else
    echo "  Status: ✗ MISMATCH - File may be corrupted or different"
    OUTPUT_STATUS=1
fi

echo ""
echo "================================================================================"

if [ $SOURCE_STATUS -eq 0 ] && [ $OUTPUT_STATUS -eq 0 ]; then
    echo "RESULT: All files verified successfully ✓"
    echo "================================================================================"
    exit 0
else
    echo "RESULT: Verification failed ✗"
    echo "================================================================================"
    exit 1
fi
