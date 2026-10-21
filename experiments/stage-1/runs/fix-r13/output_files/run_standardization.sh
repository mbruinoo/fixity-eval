#!/bin/bash

# TSV Standardization with Fixity Verification
# This script computes checksums and runs the standardization process

cd "$(dirname "$0")"

echo "========================================================================"
echo "Metropolitan Museum Inventory TSV Standardization"
echo "========================================================================"
echo ""

# Check if input file exists
if [ ! -f "met_inventory.tsv" ]; then
    echo "ERROR: met_inventory.tsv not found in current directory"
    exit 1
fi

echo "[0] Computing original file fixity..."
echo ""
echo "    Original file: met_inventory.tsv"
echo "    SHA-256:"
sha256sum met_inventory.tsv | tee met_inventory.tsv.sha256
echo ""
echo "    MD5:"
md5sum met_inventory.tsv | tee met_inventory.tsv.md5
echo ""

# Run the standardization Python script
echo "[1] Running standardization process..."
python3 standardize_tsv.py

# Compute checksums of output
if [ -f "met_inventory_standardized.tsv" ]; then
    echo ""
    echo "========================================================================"
    echo "OUTPUT FIXITY VERIFICATION"
    echo "========================================================================"
    echo ""
    echo "    Standardized file: met_inventory_standardized.tsv"
    echo "    SHA-256:"
    sha256sum met_inventory_standardized.tsv | tee met_inventory_standardized.tsv.sha256
    echo ""
    echo "    MD5:"
    md5sum met_inventory_standardized.tsv | tee met_inventory_standardized.tsv.md5
    echo ""
    
    # Generate verification summary
    echo "========================================================================"
    echo "SUMMARY"
    echo "========================================================================"
    echo ""
    echo "Output files generated:"
    echo "  ✓ met_inventory_standardized.tsv (standardized data)"
    echo "  ✓ met_inventory.tsv.sha256 (source SHA-256)"
    echo "  ✓ met_inventory.tsv.md5 (source MD5)"
    echo "  ✓ met_inventory_standardized.tsv.sha256 (output SHA-256)"
    echo "  ✓ met_inventory_standardized.tsv.md5 (output MD5)"
    echo "  ✓ fixity_report.json (detailed report)"
    echo ""
    echo "To verify integrity:"
    echo "  sha256sum -c met_inventory.tsv.sha256"
    echo "  sha256sum -c met_inventory_standardized.tsv.sha256"
    echo ""
else
    echo "ERROR: Standardization failed - output file not created"
    exit 1
fi

echo "========================================================================"
