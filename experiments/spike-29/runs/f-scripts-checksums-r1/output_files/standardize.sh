#!/bin/bash
#
# TSV Standardization Wrapper Script
# Usage: ./standardize.sh <input_file> [output_file]
#

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <input_tsv_file> [output_tsv_file]"
    echo ""
    echo "Example:"
    echo "  $0 met_inventory.tsv"
    echo "  $0 met_inventory.tsv met_inventory_standardized.tsv"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-${INPUT_FILE%.*}_standardized.${INPUT_FILE##*.}}"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file not found: $INPUT_FILE"
    exit 1
fi

echo "TSV Standardization Script"
echo "=========================="
echo ""
echo "Input:  $INPUT_FILE"
echo "Output: $OUTPUT_FILE"
echo ""

# Run the Python script
python3 "$(dirname "$0")/standardize_tsv.py" "$INPUT_FILE" -o "$OUTPUT_FILE"

echo ""
echo "✓ Standardization complete!"
echo ""
echo "Generated files:"
echo "  - $OUTPUT_FILE (standardized TSV)"
echo "  - ${OUTPUT_FILE%.*}_checksum_report.txt (detailed report)"
echo "  - checksums.txt (SHA-256 checksums)"
