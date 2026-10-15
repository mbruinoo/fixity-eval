#!/bin/bash

################################################################################
# TSV File Integrity Verification Script
# 
# Usage: ./verify_integrity.sh [source_file] [standardized_file]
# Example: ./verify_integrity.sh met_inventory.tsv met_inventory_standardized.tsv
#
# This script calculates SHA256 checksums for both files and generates
# an integrity verification report.
################################################################################

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default file names
SOURCE_FILE="${1:-met_inventory.tsv}"
STANDARDIZED_FILE="${2:-met_inventory_standardized.tsv}"
REPORT_FILE="integrity_checksums.txt"

echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}TSV FILE INTEGRITY VERIFICATION${NC}"
echo -e "${BLUE}=================================================================================${NC}"
echo ""

# Check if source file exists
if [ ! -f "$SOURCE_FILE" ]; then
    echo -e "${RED}Error: Source file '$SOURCE_FILE' not found${NC}"
    exit 1
fi

# Check if standardized file exists
if [ ! -f "$STANDARDIZED_FILE" ]; then
    echo -e "${RED}Error: Standardized file '$STANDARDIZED_FILE' not found${NC}"
    exit 1
fi

echo -e "${YELLOW}Processing files...${NC}"
echo ""

# Calculate checksums
echo "Calculating SHA256 checksums..."

SOURCE_CHECKSUM=$(sha256sum "$SOURCE_FILE" | awk '{print $1}')
STANDARDIZED_CHECKSUM=$(sha256sum "$STANDARDIZED_FILE" | awk '{print $1}')

# Get file sizes
SOURCE_SIZE=$(wc -c < "$SOURCE_FILE")
STANDARDIZED_SIZE=$(wc -c < "$STANDARDIZED_FILE")

# Get line counts
SOURCE_LINES=$(wc -l < "$SOURCE_FILE")
STANDARDIZED_LINES=$(wc -l < "$STANDARDIZED_FILE")

# Get creation dates (if available)
SOURCE_DATE=$(stat -f %Sm -t "%Y-%m-%d %H:%M:%S" "$SOURCE_FILE" 2>/dev/null || date)
STANDARDIZED_DATE=$(stat -f %Sm -t "%Y-%m-%d %H:%M:%S" "$STANDARDIZED_FILE" 2>/dev/null || date)

# Generate report
cat > "$REPORT_FILE" << EOF
================================================================================
TSV INTEGRITY VERIFICATION REPORT
Generated: $(date)
================================================================================

SOURCE FILE
-----------
Name:          $SOURCE_FILE
Size:          $SOURCE_SIZE bytes
Lines:         $SOURCE_LINES
Modified:      $SOURCE_DATE
Checksum:      $SOURCE_CHECKSUM
Algorithm:     SHA256

STANDARDIZED FILE
-----------------
Name:          $STANDARDIZED_FILE
Size:          $STANDARDIZED_SIZE bytes
Lines:         $STANDARDIZED_LINES
Modified:      $STANDARDIZED_DATE
Checksum:      $STANDARDIZED_CHECKSUM
Algorithm:     SHA256

FILE COMPARISON
---------------
Size Difference:  $((STANDARDIZED_SIZE - SOURCE_SIZE)) bytes
Line Difference:  $((STANDARDIZED_LINES - SOURCE_LINES)) lines

CHECKSUM VERIFICATION
---------------------

To verify these files in the future, use:
  sha256sum -c << EOF
$SOURCE_CHECKSUM  $SOURCE_FILE
$STANDARDIZED_CHECKSUM  $STANDARDIZED_FILE
EOF

Or verify individual files:
  sha256sum $SOURCE_FILE
  sha256sum $STANDARDIZED_FILE

INTEGRITY STATUS
----------------
Source File:       ✓ Checksummed
Standardized File: ✓ Checksummed
Verification Ready: ✓ Yes

If these checksums are stored in a secure location, they can be used to:
  - Detect accidental data corruption
  - Verify successful file transfer
  - Confirm file authenticity
  - Track version changes over time

================================================================================
EOF

# Display results
echo ""
echo -e "${GREEN}✓ Checksum Calculation Complete${NC}"
echo ""
echo -e "${BLUE}SOURCE FILE: $SOURCE_FILE${NC}"
echo "  Size:  $SOURCE_SIZE bytes"
echo "  Lines: $SOURCE_LINES"
echo -e "  SHA256: ${YELLOW}$SOURCE_CHECKSUM${NC}"
echo ""
echo -e "${BLUE}STANDARDIZED FILE: $STANDARDIZED_FILE${NC}"
echo "  Size:  $STANDARDIZED_SIZE bytes"
echo "  Lines: $STANDARDIZED_LINES"
echo -e "  SHA256: ${YELLOW}$STANDARDIZED_CHECKSUM${NC}"
echo ""
echo -e "${GREEN}✓ Report saved to: $REPORT_FILE${NC}"
echo ""

# Show if files are identical
if [ "$SOURCE_CHECKSUM" = "$STANDARDIZED_CHECKSUM" ]; then
    echo -e "${GREEN}✓ CHECKSUMS MATCH - Files are identical${NC}"
else
    echo -e "${YELLOW}⚠ CHECKSUMS DIFFER - Files have differences${NC}"
    echo "  This is expected if standardization made changes"
    echo ""
    echo "  To see differences, use:"
    echo "    diff $SOURCE_FILE $STANDARDIZED_FILE"
    echo "    wc -l $SOURCE_FILE $STANDARDIZED_FILE"
fi

echo ""
echo -e "${BLUE}=================================================================================${NC}"
echo ""
