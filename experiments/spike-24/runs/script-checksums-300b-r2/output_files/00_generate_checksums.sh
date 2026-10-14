#!/bin/bash
# Generate checksums for archive verification

INPUT_FILE="/mnt/user-data/uploads/met_inventory.tsv"
TRANSFORM_SCRIPT="/mnt/user-data/outputs/01_standardize_met_inventory.sh"
OUTPUT_FILE="/mnt/user-data/outputs/met_inventory_standardized.tsv"

echo "======================================"
echo "MET Inventory Standardization Checksums"
echo "======================================"
echo ""

if [ -f "$INPUT_FILE" ]; then
    echo "INPUT FILE CHECKSUM:"
    echo "File: met_inventory.tsv (original)"
    sha256sum "$INPUT_FILE"
    md5sum "$INPUT_FILE"
    echo ""
    wc -l "$INPUT_FILE"
    echo ""
else
    echo "ERROR: Input file not found at $INPUT_FILE"
    exit 1
fi

if [ -f "$TRANSFORM_SCRIPT" ]; then
    echo "TRANSFORMATION SCRIPT CHECKSUM:"
    echo "File: 01_standardize_met_inventory.sh"
    sha256sum "$TRANSFORM_SCRIPT"
    md5sum "$TRANSFORM_SCRIPT"
    echo ""
else
    echo "ERROR: Transform script not found at $TRANSFORM_SCRIPT"
    exit 1
fi

if [ -f "$OUTPUT_FILE" ]; then
    echo "OUTPUT FILE CHECKSUM:"
    echo "File: met_inventory_standardized.tsv"
    sha256sum "$OUTPUT_FILE"
    md5sum "$OUTPUT_FILE"
    echo ""
    wc -l "$OUTPUT_FILE"
    echo ""
else
    echo "WARNING: Output file not yet generated"
    echo ""
fi

echo "======================================"
echo "Verification Complete"
echo "======================================"
