#!/bin/bash
# Standardization Workflow Script
# - Copies source to outputs for reference
# - Runs Python standardization script
# - Verifies checksums
# - Creates verification manifest

set -e

SOURCE_FILE="/mnt/user-data/uploads/met_inventory.tsv"
OUTPUT_DIR="/mnt/user-data/outputs"
REFERENCE_COPY="$OUTPUT_DIR/met_inventory_source.tsv"
STANDARDIZED_FILE="$OUTPUT_DIR/met_inventory_standardized.tsv"
REPORT_FILE="$OUTPUT_DIR/standardization_report.json"
MANIFEST_FILE="$OUTPUT_DIR/MANIFEST.txt"

echo "=================================================="
echo "MET MUSEUM INVENTORY STANDARDIZATION WORKFLOW"
echo "=================================================="
echo ""

# Step 1: Copy source file to outputs
echo "Step 1: Copying source file to outputs..."
cp "$SOURCE_FILE" "$REFERENCE_COPY"
echo "  ✓ Source backed up to: $(basename $REFERENCE_COPY)"
echo ""

# Step 2: Run standardization Python script
echo "Step 2: Running standardization script..."
python3 "$OUTPUT_DIR/standardize_met_inventory.py"
echo ""

# Step 3: Verify file integrity
echo "Step 3: Verifying file integrity..."
SOURCE_CHECKSUM=$(sha256sum "$REFERENCE_COPY" | awk '{print $1}')
OUTPUT_CHECKSUM=$(sha256sum "$STANDARDIZED_FILE" | awk '{print $1}')

echo "  Source SHA-256: $SOURCE_CHECKSUM"
echo "  Output SHA-256: $OUTPUT_CHECKSUM"
echo ""

# Step 4: Create manifest
echo "Step 4: Creating manifest file..."
cat > "$MANIFEST_FILE" << EOF
MET MUSEUM INVENTORY STANDARDIZATION MANIFEST
================================================

Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')

SOURCE FILE
-----------
Filename: $(basename $REFERENCE_COPY)
Path: $REFERENCE_COPY
Size: $(stat -f%z "$REFERENCE_COPY" 2>/dev/null || stat -c%s "$REFERENCE_COPY") bytes
SHA-256: $SOURCE_CHECKSUM
MD5: $(md5sum "$REFERENCE_COPY" | awk '{print $1}')

OUTPUT FILE
-----------
Filename: $(basename $STANDARDIZED_FILE)
Path: $STANDARDIZED_FILE
Size: $(stat -f%z "$STANDARDIZED_FILE" 2>/dev/null || stat -c%s "$STANDARDIZED_FILE") bytes
SHA-256: $OUTPUT_CHECKSUM
MD5: $(md5sum "$STANDARDIZED_FILE" | awk '{print $1}')

PROCESSING REPORT
-----------------
Detailed report: $(basename $REPORT_FILE)

STANDARDIZATION CHANGES
-----------------------
• Column names normalized to lowercase with underscores
• All whitespace trimmed from field values
• Consistent tab-separated format enforced
• Data validation applied (object_number required, URL format checked)
• Sort order preserved from source

FILES GENERATED
---------------
1. met_inventory_source.tsv - Original source file (reference backup)
2. met_inventory_standardized.tsv - Cleaned and standardized data
3. standardization_report.json - Detailed processing report with validation results
4. MANIFEST.txt - This file

VERIFICATION
------------
To verify file integrity:
  sha256sum -c <<EOF
$OUTPUT_CHECKSUM  $STANDARDIZED_FILE
EOF

To compare source and output:
  diff -u $REFERENCE_COPY $STANDARDIZED_FILE

EOF

echo "  ✓ Manifest created: $(basename $MANIFEST_FILE)"
echo ""

# Step 5: Summary
echo "=================================================="
echo "STANDARDIZATION WORKFLOW COMPLETE"
echo "=================================================="
echo ""
echo "Output files created:"
ls -lh "$OUTPUT_DIR"/met_inventory*.tsv "$OUTPUT_DIR"/*.json "$OUTPUT_DIR"/MANIFEST.txt 2>/dev/null | \
  awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "Next steps:"
echo "  1. Review standardization_report.json for validation details"
echo "  2. Compare source and output if needed"
echo "  3. Verify checksums using MANIFEST.txt"
echo ""
