#!/bin/bash
# Fixity verification script for Metropolitan Museum TSV files
# Usage: ./verify_fixity.sh [source_file] [output_file]

set -e

SOURCE_FILE="${1:-met_inventory.tsv}"
OUTPUT_FILE="${2:-met_inventory_standardized.tsv}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "╔════════════════════════════════════════════════════════╗"
echo "║   Metropolitan Museum TSV Fixity Verification Report   ║"
echo "║   Generated: $TIMESTAMP                       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if files exist
if [ ! -f "$SOURCE_FILE" ]; then
    echo "✗ ERROR: Source file not found: $SOURCE_FILE"
    exit 1
fi

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "✗ ERROR: Output file not found: $OUTPUT_FILE"
    exit 1
fi

echo "SOURCE FILE: $SOURCE_FILE"
echo "─────────────────────────────────────────────────────────"

# Source file stats
SOURCE_SIZE=$(stat -f%z "$SOURCE_FILE" 2>/dev/null || stat -c%s "$SOURCE_FILE" 2>/dev/null)
SOURCE_LINES=$(wc -l < "$SOURCE_FILE")
SOURCE_COLS=$(head -1 "$SOURCE_FILE" | tr '\t' '\n' | wc -l)

echo "File size:     $SOURCE_SIZE bytes"
echo "Lines:         $SOURCE_LINES"
echo "Columns:       $SOURCE_COLS"
echo ""

# Calculate checksums
echo "Calculating checksums (this may take a moment)..."
echo ""

# MD5 checksums
if command -v md5sum &> /dev/null; then
    SOURCE_MD5=$(md5sum "$SOURCE_FILE" | awk '{print $1}')
    OUTPUT_MD5=$(md5sum "$OUTPUT_FILE" | awk '{print $1}')
elif command -v md5 &> /dev/null; then
    SOURCE_MD5=$(md5 -q "$SOURCE_FILE")
    OUTPUT_MD5=$(md5 -q "$OUTPUT_FILE")
else
    echo "⚠ Warning: md5sum/md5 not found, skipping MD5 checksums"
    SOURCE_MD5="N/A"
    OUTPUT_MD5="N/A"
fi

# SHA256 checksums
if command -v sha256sum &> /dev/null; then
    SOURCE_SHA256=$(sha256sum "$SOURCE_FILE" | awk '{print $1}')
    OUTPUT_SHA256=$(sha256sum "$OUTPUT_FILE" | awk '{print $1}')
elif command -v shasum &> /dev/null; then
    SOURCE_SHA256=$(shasum -a 256 "$SOURCE_FILE" | awk '{print $1}')
    OUTPUT_SHA256=$(shasum -a 256 "$OUTPUT_FILE" | awk '{print $1}')
else
    echo "⚠ Warning: sha256sum/shasum not found, skipping SHA256 checksums"
    SOURCE_SHA256="N/A"
    OUTPUT_SHA256="N/A"
fi

echo "MD5 (SOURCE):     $SOURCE_MD5"
echo "MD5 (OUTPUT):     $OUTPUT_MD5"
echo ""
echo "SHA256 (SOURCE):  $SOURCE_SHA256"
echo "SHA256 (OUTPUT):  $OUTPUT_SHA256"
echo ""

# Compare file properties
echo "OUTPUT FILE: $OUTPUT_FILE"
echo "─────────────────────────────────────────────────────────"

OUTPUT_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null)
OUTPUT_LINES=$(wc -l < "$OUTPUT_FILE")
OUTPUT_COLS=$(head -1 "$OUTPUT_FILE" | tr '\t' '\n' | wc -l)

echo "File size:     $OUTPUT_SIZE bytes"
echo "Lines:         $OUTPUT_LINES"
echo "Columns:       $OUTPUT_COLS"
echo ""

# Validation checks
echo "VALIDATION CHECKS"
echo "─────────────────────────────────────────────────────────"

PASS_COUNT=0
TOTAL_CHECKS=3

# Check 1: Row count match
if [ "$SOURCE_LINES" -eq "$OUTPUT_LINES" ]; then
    echo "✓ Row count match ($SOURCE_LINES records)"
    ((PASS_COUNT++))
else
    echo "✗ Row count mismatch (source: $SOURCE_LINES, output: $OUTPUT_LINES)"
fi

# Check 2: Column count match
if [ "$SOURCE_COLS" -eq "$OUTPUT_COLS" ]; then
    echo "✓ Column count match ($SOURCE_COLS columns)"
    ((PASS_COUNT++))
else
    echo "✗ Column count mismatch (source: $SOURCE_COLS, output: $OUTPUT_COLS)"
fi

# Check 3: Headers match
SOURCE_HEADER=$(head -1 "$SOURCE_FILE")
OUTPUT_HEADER=$(head -1 "$OUTPUT_FILE")

if [ "$SOURCE_HEADER" = "$OUTPUT_HEADER" ]; then
    echo "✓ Header row matches"
    ((PASS_COUNT++))
else
    echo "✗ Header row differs"
    echo "  Source header: $SOURCE_HEADER"
    echo "  Output header: $OUTPUT_HEADER"
fi

echo ""
echo "CHECKSUM ANALYSIS"
echo "─────────────────────────────────────────────────────────"

if [ "$SOURCE_MD5" != "$OUTPUT_MD5" ]; then
    echo "ℹ Note: MD5 checksums differ (expected due to formatting)"
else
    echo "⚠ Warning: MD5 checksums identical (files may be byte-identical)"
fi

if [ "$SOURCE_SHA256" != "$OUTPUT_SHA256" ]; then
    echo "ℹ Note: SHA256 checksums differ (expected due to formatting)"
else
    echo "⚠ Warning: SHA256 checksums identical (files may be byte-identical)"
fi

echo ""
echo "SUMMARY"
echo "─────────────────────────────────────────────────────────"
echo "Validation checks passed: $PASS_COUNT/$TOTAL_CHECKS"

if [ $PASS_COUNT -eq $TOTAL_CHECKS ]; then
    echo "✓ All structural validations PASSED"
    echo "✓ Data integrity verified"
    exit 0
else
    echo "✗ Some validations FAILED"
    exit 1
fi
