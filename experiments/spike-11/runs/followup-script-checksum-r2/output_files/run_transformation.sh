#!/bin/bash
# Copy input file and run transformation in output directory
cd /mnt/user-data/outputs
cp /mnt/user-data/uploads/met_inventory.tsv ./
python3 standardize_met_inventory.py
