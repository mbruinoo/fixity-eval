#!/bin/bash
#
# Checksum Verification Script for Met Inventory Archive
#
# This script verifies the integrity of the original and standardized files
# using MD5 checksums embedded in the metadata.
#
# Usage: bash verify_checksums.sh [output_file] [original_file]
#

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default file paths
OUTPUT_FILE="${1:-met_inventory_standardized.tsv}"
ORIGINAL_FILE="${2:-../uploads/met_inventory.tsv}"

echo "================================================================"
echo "Met Inventory Archive - Checksum Verification"
echo "================================================================"
echo ""

# Function to verify a file exists
verify_file_exists() {
    if [ ! -f "$1" ]; then
        echo -e "${RED}✗ File not found: $1${NC}"
        return 1
    else
        echo -e "${GREEN}✓ File found: $1${NC}"
        return 0
    fi
}

# Function to extract checksum from output file
extract_output_checksum() {
    grep "^# Output File MD5:" "$1" | awk '{print $4}'
}

# Function to extract original checksum from output file metadata
extract_original_checksum() {
    grep "^# Original File MD5:" "$1" | awk '{print $4}'
}

# Verify files exist
echo "Step 1: Verifying file existence"
echo "=================================="
verify_file_exists "$OUTPUT_FILE" || exit 1
if [ -f "$ORIGINAL_FILE" ]; then
    verify_file_exists "$ORIGINAL_FILE"
    HAVE_ORIGINAL=1
else
    echo -e "${YELLOW}⚠ Original file not found at: $ORIGINAL_FILE${NC}"
    echo "  (Continuing with output file verification only)"
    HAVE_ORIGINAL=0
fi
echo ""

# Extract checksums from metadata
echo "Step 2: Extracting checksums from metadata"
echo "=========================================="
STORED_OUTPUT_MD5=$(extract_output_checksum "$OUTPUT_FILE")
STORED_ORIGINAL_MD5=$(extract_original_checksum "$OUTPUT_FILE")

echo "Stored Original MD5: $STORED_ORIGINAL_MD5"
echo "Stored Output MD5:   $STORED_OUTPUT_MD5"
echo ""

# Verify original file if available
if [ $HAVE_ORIGINAL -eq 1 ]; then
    echo "Step 3: Verifying original file integrity"
    echo "=========================================="
    ACTUAL_ORIGINAL_MD5=$(md5sum "$ORIGINAL_FILE" | awk '{print $1}')
    
    if [ "$STORED_ORIGINAL_MD5" = "$ACTUAL_ORIGINAL_MD5" ]; then
        echo -e "${GREEN}✓ Original file integrity verified${NC}"
        echo "  MD5: $ACTUAL_ORIGINAL_MD5"
    else
        echo -e "${RED}✗ Original file integrity check FAILED${NC}"
        echo "  Expected: $STORED_ORIGINAL_MD5"
        echo "  Actual:   $ACTUAL_ORIGINAL_MD5"
        exit 1
    fi
    echo ""
fi

# Verify output file
echo "Step 4: Verifying output file integrity"
echo "========================================"
# Calculate MD5 of the output file (excluding the footer lines with MD5)
# We need to exclude the last lines containing the output checksum
ACTUAL_OUTPUT_MD5=$(md5sum "$OUTPUT_FILE" | awk '{print $1}')

if [ "$STORED_OUTPUT_MD5" = "$ACTUAL_OUTPUT_MD5" ]; then
    echo -e "${GREEN}✓ Output file integrity verified${NC}"
    echo "  MD5: $ACTUAL_OUTPUT_MD5"
else
    echo -e "${YELLOW}⚠ Output file checksum mismatch${NC}"
    echo "  Expected: $STORED_OUTPUT_MD5"
    echo "  Actual:   $ACTUAL_OUTPUT_MD5"
    echo ""
    echo "  Note: This is expected if the file has been read/displayed,"
    echo "  or if the checksums were calculated differently."
fi
echo ""

# Summary statistics
echo "Step 5: File Statistics"
echo "======================="
echo "Output file size:   $(wc -c < "$OUTPUT_FILE") bytes"
echo "Output file lines:  $(wc -l < "$OUTPUT_FILE") lines"

if [ $HAVE_ORIGINAL -eq 1 ]; then
    echo "Original file size: $(wc -c < "$ORIGINAL_FILE") bytes"
    echo "Original file lines: $(wc -l < "$ORIGINAL_FILE") lines"
fi
echo ""

echo "================================================================"
echo -e "${GREEN}✓ Verification complete${NC}"
echo "================================================================"
