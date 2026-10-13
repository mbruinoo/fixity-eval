#!/bin/bash
################################################################################
# Metropolitan Museum Inventory Standardization - Execution Script
################################################################################
# 
# This script demonstrates how to run the standardization process with
# detailed fixity verification using MD5 checksums.
#
# Usage:
#   bash run_standardization.sh
#
# Requirements:
#   - Python 3.6+
#   - standardize_met_inventory.py in the same directory
#   - met_inventory_ORIGINAL.tsv (input file)
#
################################################################################

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="standardize_met_inventory.py"
INPUT_FILE="met_inventory_ORIGINAL.tsv"
OUTPUT_FILE="met_inventory_STANDARDIZED.tsv"
LOG_FILE="standardization_report.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Met Inventory Standardization Process${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if input file exists
if [ ! -f "$SCRIPT_DIR/$INPUT_FILE" ]; then
    echo -e "${RED}ERROR: Input file not found: $INPUT_FILE${NC}"
    exit 1
fi

# Check if Python script exists
if [ ! -f "$SCRIPT_DIR/$SCRIPT_NAME" ]; then
    echo -e "${RED}ERROR: Python script not found: $SCRIPT_NAME${NC}"
    exit 1
fi

# Start log file
{
    echo "================================================================================"
    echo "Metropolitan Museum Inventory TSV Standardization"
    echo "================================================================================"
    echo ""
    echo "Execution Date: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo "Executor: $USER"
    echo "Working Directory: $SCRIPT_DIR"
    echo ""
    echo "================================================================================"
    echo "PRE-PROCESSING FIXITY CHECK"
    echo "================================================================================"
    echo ""
    
    # Calculate input checksums
    echo "Input File: $INPUT_FILE"
    INPUT_SIZE=$(stat -f%z "$SCRIPT_DIR/$INPUT_FILE" 2>/dev/null || stat -c%s "$SCRIPT_DIR/$INPUT_FILE" 2>/dev/null)
    INPUT_MD5=$(md5sum "$SCRIPT_DIR/$INPUT_FILE" | awk '{print $1}')
    INPUT_LINE_COUNT=$(wc -l < "$SCRIPT_DIR/$INPUT_FILE")
    
    echo "  File Size:  $INPUT_SIZE bytes"
    echo "  Line Count: $INPUT_LINE_COUNT"
    echo "  MD5:        $INPUT_MD5"
    echo ""
    
} > "$SCRIPT_DIR/$LOG_FILE"

echo -e "${GREEN}✓ Input file verified${NC}"

# Run the Python script
echo ""
echo -e "${YELLOW}Running standardization script...${NC}"
echo ""

if python3 "$SCRIPT_DIR/$SCRIPT_NAME" "$SCRIPT_DIR/$INPUT_FILE" "$SCRIPT_DIR/$OUTPUT_FILE" 2>&1 | tee -a "$SCRIPT_DIR/$LOG_FILE"; then
    echo -e "${GREEN}✓ Standardization completed successfully${NC}"
else
    echo -e "${RED}✗ Standardization failed${NC}"
    exit 1
fi

echo ""

# Post-processing fixity check
{
    echo ""
    echo "================================================================================"
    echo "POST-PROCESSING FIXITY CHECK"
    echo "================================================================================"
    echo ""
    
    if [ -f "$SCRIPT_DIR/$OUTPUT_FILE" ]; then
        OUTPUT_SIZE=$(stat -f%z "$SCRIPT_DIR/$OUTPUT_FILE" 2>/dev/null || stat -c%s "$SCRIPT_DIR/$OUTPUT_FILE" 2>/dev/null)
        OUTPUT_MD5=$(md5sum "$SCRIPT_DIR/$OUTPUT_FILE" | awk '{print $1}')
        OUTPUT_LINE_COUNT=$(wc -l < "$SCRIPT_DIR/$OUTPUT_FILE")
        
        echo "Output File: $OUTPUT_FILE"
        echo "  File Size:  $OUTPUT_SIZE bytes"
        echo "  Line Count: $OUTPUT_LINE_COUNT"
        echo "  MD5:        $OUTPUT_MD5"
        echo ""
        
        echo "================================================================================"
        echo "DATA INTEGRITY VERIFICATION"
        echo "================================================================================"
        echo ""
        
        # Calculate size difference
        SIZE_DIFF=$((OUTPUT_SIZE - INPUT_SIZE))
        if [ $SIZE_DIFF -ge 0 ]; then
            echo "Size Change: +$SIZE_DIFF bytes"
        else
            echo "Size Change: $SIZE_DIFF bytes"
        fi
        
        # Calculate line difference
        LINE_DIFF=$((OUTPUT_LINE_COUNT - INPUT_LINE_COUNT))
        echo "Line Count Change: $LINE_DIFF"
        
        echo ""
        echo "Checksums:"
        echo "  Input MD5:  $INPUT_MD5"
        echo "  Output MD5: $OUTPUT_MD5"
        echo ""
        
        if [ "$INPUT_MD5" != "$OUTPUT_MD5" ]; then
            echo "✓ Checksums differ (expected - data was transformed)"
        else
            echo "✗ WARNING: Checksums are identical (data may not have changed)"
        fi
        
        echo ""
        echo "================================================================================"
        echo "ARCHIVE CONTENTS"
        echo "================================================================================"
        echo ""
        
        echo "Files for archival:"
        ls -lh "$SCRIPT_DIR/$INPUT_FILE"
        ls -lh "$SCRIPT_DIR/$OUTPUT_FILE"
        ls -lh "$SCRIPT_DIR/$SCRIPT_NAME"
        ls -lh "$SCRIPT_DIR/$LOG_FILE"
        
        echo ""
        echo "================================================================================"
        echo "COMPLETION"
        echo "================================================================================"
        echo ""
        echo "Processing completed successfully at $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
        echo ""
        
    else
        echo "✗ ERROR: Output file was not created"
        exit 1
    fi
    
} >> "$SCRIPT_DIR/$LOG_FILE"

echo -e "${GREEN}✓ Output file verified${NC}"
echo ""
echo -e "${GREEN}================================================================================${NC}"
echo -e "${GREEN}STANDARDIZATION COMPLETE${NC}"
echo -e "${GREEN}================================================================================${NC}"
echo ""
echo "Generated files ready for archival:"
echo "  • $INPUT_FILE (original input)"
echo "  • $OUTPUT_FILE (standardized output)"
echo "  • $SCRIPT_NAME (transformation script)"
echo "  • $LOG_FILE (processing report with checksums)"
echo ""
echo "For archival purposes, preserve all four files together."
echo ""
