#!/bin/bash
# Verification script for Met Museum Inventory TSV standardization
# Run this script to verify the integrity of the standardized file

echo "=================================================="
echo "Met Museum Inventory TSV Integrity Verification"
echo "=================================================="
echo ""

# Check if standardized file exists
if [ ! -f "met_inventory_standardized.tsv" ]; then
    echo "ERROR: met_inventory_standardized.tsv not found!"
    exit 1
fi

# Compute SHA-256 of standardized file
COMPUTED_HASH=$(sha256sum met_inventory_standardized.tsv | awk '{print $1}')
EXPECTED_HASH="a573e8c3147d6b2112fed1b4041be0724d562eb2eeb19085c2647b4bbe9b0e93"

echo "File: met_inventory_standardized.tsv"
echo "Expected SHA-256: $EXPECTED_HASH"
echo "Computed SHA-256: $COMPUTED_HASH"
echo ""

if [ "$COMPUTED_HASH" = "$EXPECTED_HASH" ]; then
    echo "✅ VERIFIED: File integrity confirmed!"
    echo "   The standardized file has not been modified."
    exit 0
else
    echo "❌ MISMATCH: File integrity check failed!"
    echo "   The file may have been modified or corrupted."
    exit 1
fi
