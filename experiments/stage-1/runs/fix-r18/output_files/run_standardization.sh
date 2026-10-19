#!/bin/bash
# Run the standardization and display results

cd /mnt/user-data/outputs

echo "======================================"
echo "Metropolitan Museum TSV Standardization"
echo "======================================"
echo

python3 standardize_and_checksum.py

echo
echo "======================================"
echo "File Outputs Generated:"
echo "======================================"
ls -lh met_inventory_source.tsv met_inventory_standardized.tsv fixity_manifest.json

echo
echo "======================================"
echo "Fixity Manifest Content:"
echo "======================================"
cat fixity_manifest.json

echo
echo "======================================"
echo "Comparing Row Count:"
echo "======================================"
echo "Source rows (excluding header):"
tail -n +2 met_inventory_source.tsv | wc -l

echo "Standardized rows (excluding header):"
tail -n +2 met_inventory_standardized.tsv | wc -l

echo
echo "======================================"
echo "First 5 rows of standardized file:"
echo "======================================"
head -n 6 met_inventory_standardized.tsv

echo
echo "======================================"
echo "Last 5 rows of standardized file:"
echo "======================================"
tail -n 5 met_inventory_standardized.tsv
