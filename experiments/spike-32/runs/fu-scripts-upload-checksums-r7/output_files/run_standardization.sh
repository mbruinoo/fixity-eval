#!/bin/bash
# Run TSV standardization with checksum verification

set -e

cd /mnt/user-data/outputs

echo "=== Met Museum Inventory TSV Standardization ==="
echo ""

# Run the Python script
python3 standardize_met_inventory.py

echo ""
echo "=== Files Created ==="
ls -lh met_inventory*.tsv fixity_report.json

echo ""
echo "=== Standardization Complete ==="
echo "All files are in: /mnt/user-data/outputs/"
