#!/bin/bash
#
# Checksum Verification Script
# Verifies file integrity using SHA-256 checksums
#
# Usage: ./verify_checksums.sh [checksums_file]
#

CHECKSUM_FILE="${1:-checksums.txt}"

if [ ! -f "$CHECKSUM_FILE" ]; then
    echo "Error: Checksum file not found: $CHECKSUM_FILE"
    echo ""
    echo "Usage: $0 [checksums_file]"
    echo "Default: checksums.txt"
    exit 1
fi

echo "Verifying file integrity..."
echo "Checksum file: $CHECKSUM_FILE"
echo ""

# Read and verify each checksum
verified=0
failed=0

while IFS='  ' read -r expected_hash filename; do
    if [ -z "$filename" ]; then
        continue
    fi
    
    if [ ! -f "$filename" ]; then
        echo "✗ MISSING: $filename"
        ((failed++))
        continue
    fi
    
    actual_hash=$(sha256sum "$filename" | awk '{print $1}')
    
    if [ "$expected_hash" = "$actual_hash" ]; then
        echo "✓ OK: $filename"
        ((verified++))
    else
        echo "✗ FAILED: $filename"
        echo "  Expected: $expected_hash"
        echo "  Actual:   $actual_hash"
        ((failed++))
    fi
done < "$CHECKSUM_FILE"

echo ""
echo "Verification Summary"
echo "===================="
echo "Verified: $verified"
echo "Failed:   $failed"

if [ $failed -eq 0 ]; then
    echo ""
    echo "✓ All checksums verified successfully!"
    exit 0
else
    echo ""
    echo "✗ Some files failed verification!"
    exit 1
fi
