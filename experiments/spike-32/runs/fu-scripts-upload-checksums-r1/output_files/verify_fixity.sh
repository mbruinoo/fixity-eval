#!/bin/bash
# Fixity verification script for MET Museum inventory files
# Use this to verify that files have not been corrupted or altered

set -e

echo "=========================================="
echo "MET Inventory Fixity Verification"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_FILE="${SCRIPT_DIR}/met_inventory.tsv"
STANDARDIZED_FILE="${SCRIPT_DIR}/met_inventory_standardized.tsv"

# Expected checksums
EXPECTED_SOURCE="e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf"
EXPECTED_STANDARDIZED="d3bfbc35b3321879b0ce20c00c2ed8aee1f20a1aebfbb9a36eb7fa4705c2faf1"

# Function to verify a file
verify_file() {
    local filepath=$1
    local expected_checksum=$2
    local file_label=$3
    
    if [ ! -f "$filepath" ]; then
        echo "❌ MISSING: $file_label"
        echo "   Expected at: $filepath"
        return 1
    fi
    
    echo "Verifying: $file_label"
    echo "  Path: $filepath"
    
    # Calculate actual checksum
    if command -v sha256sum &> /dev/null; then
        actual_checksum=$(sha256sum "$filepath" | awk '{print $1}')
    elif command -v shasum &> /dev/null; then
        actual_checksum=$(shasum -a 256 "$filepath" | awk '{print $1}')
    else
        echo "❌ ERROR: sha256sum or shasum not found"
        return 1
    fi
    
    echo "  Expected: $expected_checksum"
    echo "  Actual:   $actual_checksum"
    
    if [ "$actual_checksum" = "$expected_checksum" ]; then
        echo "  ✓ PASS: Checksum matches"
        local filesize=$(stat -f%z "$filepath" 2>/dev/null || stat -c%s "$filepath" 2>/dev/null)
        echo "  Size: $filesize bytes"
        return 0
    else
        echo "  ❌ FAIL: Checksum mismatch - file may be corrupted"
        return 1
    fi
}

# Check if source file exists (optional if running in outputs directory)
if [ -f "$SOURCE_FILE" ]; then
    echo "SOURCE FILE:"
    verify_file "$SOURCE_FILE" "$EXPECTED_SOURCE" "Original TSV"
    source_pass=$?
    echo ""
else
    echo "⚠️  Source file not found in this directory (expected in uploads)"
    source_pass=0
    echo ""
fi

# Always check standardized file
echo "STANDARDIZED FILE:"
verify_file "$STANDARDIZED_FILE" "$EXPECTED_STANDARDIZED" "Standardized TSV"
standardized_pass=$?
echo ""

# Summary
echo "=========================================="
echo "VERIFICATION SUMMARY"
echo "=========================================="

if [ $standardized_pass -eq 0 ]; then
    echo "✓ Primary file integrity verified"
else
    echo "✗ File integrity check failed"
    exit 1
fi

echo ""
echo "Files are safe to use if all checks pass."
