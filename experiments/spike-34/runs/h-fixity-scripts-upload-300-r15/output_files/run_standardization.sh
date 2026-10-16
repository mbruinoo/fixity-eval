#!/bin/bash
cd /mnt/user-data/outputs
python3 standardize_tsv.py
echo ""
echo "=== File Details ==="
echo "Standardized file:"
ls -lh met_inventory_standardized.tsv
echo ""
echo "First 10 rows of standardized file:"
head -10 met_inventory_standardized.tsv
echo ""
echo "Total lines in standardized file:"
wc -l met_inventory_standardized.tsv
