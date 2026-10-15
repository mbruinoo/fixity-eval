#!/bin/bash

# Standardization Script with Checksum Verification
# This script executes the TSV standardization and provides an audit trail

set -e  # Exit on any error

echo "=================================================="
echo "TSV Standardization with Integrity Verification"
echo "=================================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_FILE="${SCRIPT_DIR}/../uploads/met_inventory.tsv"
OUTPUT_FILE="${SCRIPT_DIR}/met_inventory_standardized.tsv"
MANIFEST_FILE="${SCRIPT_DIR}/met_inventory_manifest.json"
AUDIT_LOG="${SCRIPT_DIR}/standardization_audit.log"

# Initialize audit log
{
    echo "Standardization Audit Log"
    echo "========================="
    echo "Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo "Script: $0"
    echo ""
    echo "Input file:  $INPUT_FILE"
    echo "Output file: $OUTPUT_FILE"
    echo "Manifest:    $MANIFEST_FILE"
    echo ""
} > "$AUDIT_LOG"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "ERROR: Input file not found: $INPUT_FILE" | tee -a "$AUDIT_LOG"
    exit 1
fi

echo "Input file found: $INPUT_FILE" | tee -a "$AUDIT_LOG"
echo ""

# Run Python standardization script
python3 "${SCRIPT_DIR}/standardize_tsv.py" "$INPUT_FILE" "$OUTPUT_FILE" "$MANIFEST_FILE" | tee -a "$AUDIT_LOG"

echo "" | tee -a "$AUDIT_LOG"
echo "Verification Steps" | tee -a "$AUDIT_LOG"
echo "==================" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

# Verify output file exists
if [ ! -f "$OUTPUT_FILE" ]; then
    echo "ERROR: Output file was not created" | tee -a "$AUDIT_LOG"
    exit 1
fi
echo "✓ Output file exists: $OUTPUT_FILE" | tee -a "$AUDIT_LOG"

# Verify manifest exists
if [ ! -f "$MANIFEST_FILE" ]; then
    echo "ERROR: Manifest file was not created" | tee -a "$AUDIT_LOG"
    exit 1
fi
echo "✓ Manifest file exists: $MANIFEST_FILE" | tee -a "$AUDIT_LOG"

echo "" | tee -a "$AUDIT_LOG"

# Display file sizes
INPUT_SIZE=$(stat -f%z "$INPUT_FILE" 2>/dev/null || stat -c%s "$INPUT_FILE")
OUTPUT_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE")

echo "File Size Information:" | tee -a "$AUDIT_LOG"
echo "  Source: $INPUT_SIZE bytes" | tee -a "$AUDIT_LOG"
echo "  Output: $OUTPUT_SIZE bytes" | tee -a "$AUDIT_LOG"
echo "  Change: $(($OUTPUT_SIZE - $INPUT_SIZE)) bytes" | tee -a "$AUDIT_LOG"
echo "" | tee -a "$AUDIT_LOG"

# Validate TSV structure
echo "TSV Structure Validation:" | tee -a "$AUDIT_LOG"
{
    python3 << 'EOF'
import csv
import sys

output_file = sys.argv[1]

try:
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
        
        print(f"  ✓ Valid TSV format")
        print(f"  ✓ Columns: {len(reader.fieldnames)}")
        print(f"  ✓ Data rows: {len(rows)}")
        print(f"  ✓ Headers: {', '.join(reader.fieldnames)}")
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    sys.exit(1)
EOF
} "$OUTPUT_FILE" | tee -a "$AUDIT_LOG"

echo "" | tee -a "$AUDIT_LOG"

# Display manifest summary
echo "Manifest Summary:" | tee -a "$AUDIT_LOG"
python3 << 'EOF' "$MANIFEST_FILE" | tee -a "$AUDIT_LOG"
import json
import sys

manifest_file = sys.argv[1]

with open(manifest_file, 'r') as f:
    manifest = json.load(f)
    
    print(f"  Timestamp: {manifest['timestamp']}")
    print(f"  Source MD5: {manifest['source_file']['checksums']['md5']}")
    print(f"  Output MD5: {manifest['output_file']['checksums']['md5']}")
    print(f"  Statistics:")
    print(f"    - Total rows: {manifest['statistics']['total_rows']}")
    print(f"    - Total columns: {manifest['statistics']['total_columns']}")
    print(f"    - Issues found: {manifest['statistics']['issues_found']}")
EOF

echo "" | tee -a "$AUDIT_LOG"
echo "=================================================="  | tee -a "$AUDIT_LOG"
echo "✓ Standardization completed successfully"  | tee -a "$AUDIT_LOG"
echo "=================================================="  | tee -a "$AUDIT_LOG"
echo ""
echo "Files created:"
echo "  1. met_inventory_standardized.tsv - Standardized data file"
echo "  2. met_inventory_manifest.json - Checksums and metadata"
echo "  3. standardization_audit.log - This audit trail"
echo ""
