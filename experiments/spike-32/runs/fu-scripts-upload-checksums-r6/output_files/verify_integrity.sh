#!/bin/bash
# Integrity verification script for Met Museum inventory standardization

set -e

echo "=========================================="
echo "Met Museum Inventory - Integrity Verification"
echo "=========================================="
echo ""

# Define files and checksums
STANDARDIZED_FILE="met_inventory_standardized.tsv"
EXPECTED_HASH="37d977d40f2e18da2a216d816e48a1ab0d5d72b8bbab35b022a0914b3a866523"

# Check if file exists
if [ ! -f "$STANDARDIZED_FILE" ]; then
    echo "❌ Error: File not found: $STANDARDIZED_FILE"
    exit 1
fi

echo "Verifying: $STANDARDIZED_FILE"
echo ""

# Calculate actual hash
ACTUAL_HASH=$(sha256sum "$STANDARDIZED_FILE" | awk '{print $1}')

echo "Expected SHA-256: $EXPECTED_HASH"
echo "Actual SHA-256:   $ACTUAL_HASH"
echo ""

# Compare hashes
if [ "$ACTUAL_HASH" = "$EXPECTED_HASH" ]; then
    echo "✓ Verification PASSED"
    echo "  File integrity confirmed!"
    echo ""
    
    # Display file info
    FILE_SIZE=$(stat -f%z "$STANDARDIZED_FILE" 2>/dev/null || stat -c%s "$STANDARDIZED_FILE" 2>/dev/null)
    ROW_COUNT=$(wc -l < "$STANDARDIZED_FILE")
    
    echo "File Details:"
    echo "  Size: $FILE_SIZE bytes"
    echo "  Rows: $ROW_COUNT (including header)"
    echo ""
    echo "=========================================="
    exit 0
else
    echo "❌ Verification FAILED"
    echo "  File integrity check did not match expected hash!"
    echo "  This file may have been modified or corrupted."
    echo ""
    echo "=========================================="
    exit 1
fi
