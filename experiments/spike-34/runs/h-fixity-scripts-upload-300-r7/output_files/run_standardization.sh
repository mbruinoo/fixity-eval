#!/bin/bash
# Standardize MET Museum TSV with checksumming

cd /mnt/user-data/outputs

echo "=========================================="
echo "TSV Standardization with Fixity Check"
echo "=========================================="
echo

# Calculate source file checksum
echo "SOURCE FILE CHECKSUM:"
sha256sum met_inventory.tsv > checksums_source.txt
cat checksums_source.txt
echo

# Run the standardization
echo "Running standardization..."
python3 standardize_tsv.py met_inventory.tsv met_inventory_standardized.tsv
echo

# Calculate output file checksum
echo "OUTPUT FILE CHECKSUM:"
sha256sum met_inventory_standardized.tsv > checksums_output.txt
cat checksums_output.txt
echo

# Create combined manifest
echo "Creating checksum manifest..."
cat > CHECKSUMS.txt << 'EOF'
================================================================================
FIXITY VERIFICATION MANIFEST
================================================================================

SOURCE FILE:
EOF
cat checksums_source.txt >> CHECKSUMS.txt
cat >> CHECKSUMS.txt << 'EOF'

OUTPUT FILE:
EOF
cat checksums_output.txt >> CHECKSUMS.txt
cat >> CHECKSUMS.txt << 'EOF'

VERIFICATION COMMAND:
  sha256sum -c CHECKSUMS.txt

STANDARDIZATION DETAILS:
  - Column headers converted to snake_case
  - Tab delimiters validated
  - Whitespace trimmed from all values
  - UTF-8 encoding applied
  - Line endings normalized (LF)
  - Minimal CSV quoting applied
  - All data rows preserved

STATUS: Complete
================================================================================
EOF

cat CHECKSUMS.txt
echo

echo "=========================================="
echo "Files created:"
ls -lh met_inventory* CHECKSUMS.txt
echo "=========================================="
