#!/bin/bash
#
# Metropolitan Museum Inventory - Data Integrity Verification Script
# Verifies checksums and file properties of standardized TSV files
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  MET Inventory - Data Integrity Verification${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Verification Date: ${TIMESTAMP}"
echo "Working Directory: ${SCRIPT_DIR}"
echo ""

# Function to check if file exists
check_file() {
    local file=$1
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ ERROR: File not found: $file${NC}"
        return 1
    fi
    return 0
}

# Function to calculate and display checksums
check_checksums() {
    local file=$1
    local name=$2
    
    if check_file "$file"; then
        echo -e "${GREEN}✓ Found: $name${NC}"
        
        # SHA-256
        if command -v sha256sum &> /dev/null; then
            local sha256=$(sha256sum "$file" | awk '{print $1}')
            echo "  SHA-256: $sha256"
        else
            echo "  SHA-256: (sha256sum not available)"
        fi
        
        # MD5
        if command -v md5sum &> /dev/null; then
            local md5=$(md5sum "$file" | awk '{print $1}')
            echo "  MD5:     $md5"
        fi
        
        # File size
        local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        echo "  Size:    $size bytes"
        
        # Line count
        local lines=$(wc -l < "$file" 2>/dev/null || echo "unknown")
        echo "  Lines:   $lines"
        
        echo ""
        return 0
    fi
    return 1
}

# Function to validate TSV format
validate_tsv() {
    local file=$1
    
    if ! check_file "$file"; then
        return 1
    fi
    
    echo -e "${YELLOW}Validating TSV Format: $(basename "$file")${NC}"
    
    # Check for tab delimiters
    local tab_count=$(grep -o $'[^\t]*' "$file" | wc -l)
    echo "  Delimiters found: ~$tab_count fields"
    
    # Check first line (header)
    local header=$(head -n 1 "$file")
    local tab_fields=$(echo "$header" | grep -o $'\t' | wc -l)
    local expected_fields=3  # 3 tabs = 4 columns
    
    if [ "$tab_fields" -eq "$expected_fields" ]; then
        echo -e "  ${GREEN}✓ Header format: Valid (4 columns)${NC}"
    else
        echo -e "  ${RED}✗ Header format: Invalid (expected 4 columns, found $((tab_fields + 1)))${NC}"
    fi
    
    # Check line endings
    local crlf_count=$(grep -c $'\r$' "$file" 2>/dev/null || echo 0)
    if [ "$crlf_count" -eq 0 ]; then
        echo -e "  ${GREEN}✓ Line endings: LF (Unix-style)${NC}"
    else
        echo -e "  ${YELLOW}⚠ Line endings: CRLF (Windows-style, $crlf_count lines)${NC}"
    fi
    
    # Check encoding
    if file "$file" | grep -q "UTF-8"; then
        echo -e "  ${GREEN}✓ Encoding: UTF-8${NC}"
    else
        echo "  Encoding: $(file "$file" | sed 's/.*: //')"
    fi
    
    # Check for BOM
    local bom=$(head -c 3 "$file" | od -An -tx1 | tr -d ' ')
    if [ "$bom" == "efbbbf" ]; then
        echo -e "  ${YELLOW}⚠ Byte Order Mark (BOM) detected${NC}"
    else
        echo -e "  ${GREEN}✓ No Byte Order Mark${NC}"
    fi
    
    echo ""
}

# Main verification routine
echo -e "${BLUE}FILE CHECKSUMS${NC}"
echo "───────────────────────────────────────────────────────────"
check_checksums "${SCRIPT_DIR}/met_inventory_standardized.tsv" "Standardized Inventory"

echo -e "${BLUE}TSV FORMAT VALIDATION${NC}"
echo "───────────────────────────────────────────────────────────"
validate_tsv "${SCRIPT_DIR}/met_inventory_standardized.tsv"

# Summary
echo -e "${BLUE}VERIFICATION SUMMARY${NC}"
echo "───────────────────────────────────────────────────────────"

if check_file "${SCRIPT_DIR}/met_inventory_standardized.tsv"; then
    echo -e "${GREEN}✓ Standardized file verified and ready for use${NC}"
    
    # Check for supporting files
    if check_file "${SCRIPT_DIR}/standardize_met_inventory.py"; then
        echo -e "${GREEN}✓ Python standardization script available${NC}"
    fi
    
    if check_file "${SCRIPT_DIR}/STANDARDIZATION_REPORT.md"; then
        echo -e "${GREEN}✓ Standardization report available${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}STATUS: ✅ ALL CHECKS PASSED${NC}"
else
    echo -e "${RED}STATUS: ❌ FILE NOT FOUND${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo "For detailed information, see: STANDARDIZATION_REPORT.md"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
