#!/bin/bash

# Integrity verification script for Met Museum inventory TSV

STANDARDIZED_FILE="met_inventory_standardized.tsv"
VERIFICATION_FILE="VERIFICATION.txt"

echo "=========================================="
echo "Met Museum Inventory - Integrity Checker"
echo "=========================================="
echo ""

if [ ! -f "$STANDARDIZED_FILE" ]; then
    echo "ERROR: $STANDARDIZED_FILE not found!"
    exit 1
fi

if [ ! -f "$VERIFICATION_FILE" ]; then
    echo "ERROR: $VERIFICATION_FILE not found!"
    echo "Please run process_and_verify.sh first"
    exit 1
fi

echo "Verifying: $STANDARDIZED_FILE"
echo ""

# Extract checksums from verification file
SHA256_STORED=$(grep "SHA256:" "$VERIFICATION_FILE" | grep -oE '[a-f0-9]{64}')
MD5_STORED=$(grep "MD5:" "$VERIFICATION_FILE" | grep -oE '[a-f0-9]{32}')

# Calculate current checksums
SHA256_CURRENT=$(sha256sum "$STANDARDIZED_FILE" | awk '{print $1}')
MD5_CURRENT=$(md5sum "$STANDARDIZED_FILE" | awk '{print $1}')

echo "Current Checksums:"
echo "  SHA256: $SHA256_CURRENT"
echo "  MD5:    $MD5_CURRENT"
echo ""

echo "Stored Checksums:"
echo "  SHA256: $SHA256_STORED"
echo "  MD5:    $MD5_STORED"
echo ""

# Verify
SHA256_MATCH=0
MD5_MATCH=0

if [ "$SHA256_CURRENT" = "$SHA256_STORED" ]; then
    echo "✓ SHA256 checksum VERIFIED"
    SHA256_MATCH=1
else
    echo "✗ SHA256 checksum MISMATCH - File may be corrupted!"
fi

if [ "$MD5_CURRENT" = "$MD5_STORED" ]; then
    echo "✓ MD5 checksum VERIFIED"
    MD5_MATCH=1
else
    echo "✗ MD5 checksum MISMATCH - File may be corrupted!"
fi

echo ""

# File statistics
FILE_SIZE=$(stat -c%s "$STANDARDIZED_FILE")
ROW_COUNT=$(tail -n +2 "$STANDARDIZED_FILE" | wc -l)
MOD_TIME=$(stat -c %y "$STANDARDIZED_FILE")

echo "File Statistics:"
echo "  Size:          $FILE_SIZE bytes"
echo "  Rows:          $ROW_COUNT"
echo "  Last modified: $MOD_TIME"
echo ""

if [ $SHA256_MATCH -eq 1 ] && [ $MD5_MATCH -eq 1 ]; then
    echo "=========================================="
    echo "✓ FILE INTEGRITY VERIFIED"
    echo "=========================================="
    exit 0
else
    echo "=========================================="
    echo "✗ FILE INTEGRITY CHECK FAILED"
    echo "=========================================="
    exit 1
fi
