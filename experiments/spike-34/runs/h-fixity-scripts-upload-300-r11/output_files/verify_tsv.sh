#!/bin/bash

################################################################################
# TSV Verification Script
# 
# Comprehensive verification of Met Museum inventory TSV files
# 
# Usage:
#   chmod +x verify_tsv.sh
#   ./verify_tsv.sh met_inventory_standardized.tsv
#
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

# Check if file provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <tsv_file>"
    echo "Example: $0 met_inventory_standardized.tsv"
    exit 1
fi

TSV_FILE="$1"

# Verify file exists
if [ ! -f "$TSV_FILE" ]; then
    echo -e "${RED}✗ Error: File not found: $TSV_FILE${NC}"
    exit 1
fi

echo -e "${BLUE}================================================================================${NC}"
echo -e "${BLUE}MET MUSEUM INVENTORY TSV VERIFICATION REPORT${NC}"
echo -e "${BLUE}================================================================================${NC}"
echo ""

# File Information
echo -e "${YELLOW}1. FILE INFORMATION${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"
echo "File: $TSV_FILE"
echo "Size: $(du -h "$TSV_FILE" | cut -f1)"
echo "Last Modified: $(stat -f "%Sm" "$TSV_FILE" 2>/dev/null || stat --format=%y "$TSV_FILE" 2>/dev/null || echo 'N/A')"
echo ""

# Line Count
echo -e "${YELLOW}2. LINE COUNT VERIFICATION${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"
TOTAL_LINES=$(wc -l < "$TSV_FILE")
DATA_LINES=$((TOTAL_LINES - 1))
echo "Total lines: $TOTAL_LINES"
echo "Header rows: 1"
echo "Data rows: $DATA_LINES"

if [ "$TOTAL_LINES" -eq 488 ]; then
    echo -e "${GREEN}✓ Line count matches expected value (488)${NC}"
else
    echo -e "${RED}✗ Line count mismatch! Expected 488, got $TOTAL_LINES${NC}"
fi
echo ""

# Column Verification
echo -e "${YELLOW}3. COLUMN VERIFICATION${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"
HEADER=$(head -1 "$TSV_FILE")
echo "Header row: $HEADER"

COLUMN_COUNT=$(head -1 "$TSV_FILE" | awk -F'\t' '{print NF}')
echo "Column count: $COLUMN_COUNT"

if [ "$COLUMN_COUNT" -eq 4 ]; then
    echo -e "${GREEN}✓ Column count is correct (4 columns)${NC}"
else
    echo -e "${RED}✗ Column count mismatch! Expected 4, got $COLUMN_COUNT${NC}"
fi
echo ""

# Verify all rows have correct column count
echo -e "${YELLOW}4. ROW STRUCTURE VERIFICATION${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"
INCONSISTENT_ROWS=$(awk -F'\t' 'NF != 4 {print NR": "$0}' "$TSV_FILE" | wc -l)

if [ "$INCONSISTENT_ROWS" -eq 0 ]; then
    echo -e "${GREEN}✓ All rows have exactly 4 columns${NC}"
else
    echo -e "${RED}✗ Found $INCONSISTENT_ROWS rows with incorrect column count${NC}"
    awk -F'\t' 'NF != 4 {print "  Row "NR": has "NF" columns"}' "$TSV_FILE" | head -5
fi
echo ""

# Encoding Verification
echo -e "${YELLOW}5. CHARACTER ENCODING VERIFICATION${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"
file "$TSV_FILE"

# Check for UTF-8 encoding
if file "$TSV_FILE" | grep -q "UTF-8"; then
    echo -e "${GREEN}✓ File is UTF-8 encoded${NC}"
else
    echo -e "${YELLOW}⚠ File encoding differs from UTF-8${NC}"
fi
echo ""

# Checksum Verification
echo -e "${YELLOW}6. CHECKSUM CALCULATION${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"

# Determine OS to use correct sha256sum command
if command -v sha256sum &> /dev/null; then
    SHA256=$(sha256sum "$TSV_FILE" | awk '{print $1}')
    echo "SHA256: $SHA256"
elif command -v shasum &> /dev/null; then
    SHA256=$(shasum -a 256 "$TSV_FILE" | awk '{print $1}')
    echo "SHA256: $SHA256"
else
    echo "SHA256: (unable to calculate - command not found)"
fi

if command -v md5sum &> /dev/null; then
    MD5=$(md5sum "$TSV_FILE" | awk '{print $1}')
    echo "MD5:    $MD5"
elif command -v md5 &> /dev/null; then
    MD5=$(md5 "$TSV_FILE" | awk '{print $NF}')
    echo "MD5:    $MD5"
else
    echo "MD5:    (unable to calculate - command not found)"
fi
echo ""

# Sample Records
echo -e "${YELLOW}7. SAMPLE RECORDS${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"
echo "First 3 data rows:"
tail -n +2 "$TSV_FILE" | head -3 | nl -v 1 -s ". "
echo ""

echo "Last 3 data rows:"
tail -3 "$TSV_FILE" | nl -v "$DATA_LINES" -s ". " 
echo ""

# Empty Field Analysis
echo -e "${YELLOW}8. EMPTY FIELD ANALYSIS${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"
EMPTY_DATES=$(awk -F'\t' 'NR>1 && $1=="" {count++} END {print count+0}' "$TSV_FILE")
EMPTY_TITLES=$(awk -F'\t' 'NR>1 && $2=="" {count++} END {print count+0}' "$TSV_FILE")
EMPTY_NUMBERS=$(awk -F'\t' 'NR>1 && $3=="" {count++} END {print count+0}' "$TSV_FILE")
EMPTY_URLS=$(awk -F'\t' 'NR>1 && $4=="" {count++} END {print count+0}' "$TSV_FILE")

echo "Empty Object Dates: $EMPTY_DATES"
echo "Empty Titles: $EMPTY_TITLES"
echo "Empty Object Numbers: $EMPTY_NUMBERS"
echo "Empty URLs: $EMPTY_URLS"

if [ "$EMPTY_DATES" -gt 0 ] || [ "$EMPTY_TITLES" -gt 0 ] || [ "$EMPTY_NUMBERS" -gt 0 ] || [ "$EMPTY_URLS" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Some fields are empty (this may be intentional for untitled items)${NC}"
else
    echo -e "${GREEN}✓ All required fields populated${NC}"
fi
echo ""

# Line Ending Check
echo -e "${YELLOW}9. LINE ENDING VERIFICATION${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"
if file "$TSV_FILE" | grep -q "CRLF"; then
    echo -e "${YELLOW}⚠ File uses Windows line endings (CRLF)${NC}"
elif file "$TSV_FILE" | grep -q "ASCII\|UTF-8"; then
    echo -e "${GREEN}✓ File uses Unix line endings (LF)${NC}"
else
    echo "Line ending type: Unknown"
fi
echo ""

# Tab Delimiter Verification
echo -e "${YELLOW}10. TAB DELIMITER VERIFICATION${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"
TAB_COUNT=$(head -1 "$TSV_FILE" | tr -cd '\t' | wc -c)
echo "Tab characters in header: $TAB_COUNT"
if [ "$TAB_COUNT" -eq 3 ]; then
    echo -e "${GREEN}✓ Correct number of tab delimiters (3 = 4 columns)${NC}"
else
    echo -e "${RED}✗ Incorrect tab count! Expected 3, got $TAB_COUNT${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}================================================================================${NC}"
echo -e "${BLUE}VERIFICATION SUMMARY${NC}"
echo -e "${BLUE}================================================================================${NC}"

PASSED=0
FAILED=0
WARNINGS=0

# Recheck conditions for summary
if [ "$TOTAL_LINES" -eq 488 ]; then ((PASSED++)); else ((FAILED++)); fi
if [ "$COLUMN_COUNT" -eq 4 ]; then ((PASSED++)); else ((FAILED++)); fi
if [ "$INCONSISTENT_ROWS" -eq 0 ]; then ((PASSED++)); else ((FAILED++)); fi
if file "$TSV_FILE" | grep -q "UTF-8\|ASCII"; then ((PASSED++)); else ((WARNINGS++)); fi
if [ "$TAB_COUNT" -eq 3 ]; then ((PASSED++)); else ((FAILED++)); fi

echo -e "Checks Passed:  ${GREEN}$PASSED${NC}"
echo -e "Checks Failed:  ${RED}$FAILED${NC}"
echo -e "Warnings:       ${YELLOW}$WARNINGS${NC}"
echo ""

if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}✓ FILE VERIFICATION SUCCESSFUL${NC}"
    echo "The TSV file is properly formatted and ready for use."
else
    echo -e "${RED}✗ FILE VERIFICATION FAILED${NC}"
    echo "Please check the errors above and re-run standardization if needed."
fi

echo ""
echo "To save this report to a file:"
echo "  $0 $TSV_FILE > verification_report.txt"
echo ""
echo -e "${BLUE}================================================================================${NC}"
