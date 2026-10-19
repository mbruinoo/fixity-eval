#!/bin/bash

echo "Running TSV standardization with fixity checking..."
echo

cd /mnt/user-data/outputs
python3 standardize_and_checksum.py

echo
echo "Files created in /mnt/user-data/outputs:"
ls -lh /mnt/user-data/outputs/ | grep -E "(met_inventory|fixity_metadata|standardize_and_checksum|run_standardization)"
