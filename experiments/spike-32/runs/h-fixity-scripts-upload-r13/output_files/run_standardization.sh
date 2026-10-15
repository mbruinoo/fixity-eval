#!/bin/bash

# TSV Standardization Wrapper Script
# Executes the Python standardization script and captures checksums

echo "======================================"
echo "Met Inventory TSV Standardization"
echo "======================================"
echo ""

# Run the Python standardization script
python3 /mnt/user-data/outputs/standardize_tsv.py

# Display results
echo ""
echo "======================================"
echo "Standardization Complete"
echo "======================================"
echo ""
echo "Output files:"
echo "  - met_inventory_standardized.tsv"
echo "  - CHECKSUMS.txt"
echo ""
