#!/bin/bash

# TSV Standardization Script with Checksum Verification
# Usage: ./standardize.sh <input.tsv> [output.tsv]

set -e  # Exit on error

if [ $# -lt 1 ]; then
    echo "Usage: $0 <input.tsv> [output.tsv]"
    echo "  If output.tsv is not specified, '_standardized' will be appended"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-$(echo "$INPUT_FILE" | sed 's/\.tsv$/_standardized.tsv/')}"

if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file not found: $INPUT_FILE"
    exit 1
fi

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         TSV STANDARDIZATION WITH FIXITY PRESERVATION           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Input file:  $INPUT_FILE"
echo "Output file: $OUTPUT_FILE"
echo ""

# Calculate source checksum
echo "Calculating source checksum..."
SOURCE_CHECKSUM=$(sha256sum "$INPUT_FILE" | awk '{print $1}')
SOURCE_SIZE=$(wc -c < "$INPUT_FILE")
SOURCE_LINES=$(wc -l < "$INPUT_FILE")

echo "  Size:      $SOURCE_SIZE bytes"
echo "  Lines:     $SOURCE_LINES"
echo "  SHA256:    $SOURCE_CHECKSUM"
echo ""

# Run Python standardization
echo "Standardizing file..."
python3 "$(dirname "$0")/standardize_tsv.py" "$INPUT_FILE" "$OUTPUT_FILE"

echo ""
echo "Calculating output checksum..."
OUTPUT_CHECKSUM=$(sha256sum "$OUTPUT_FILE" | awk '{print $1}')
OUTPUT_SIZE=$(wc -c < "$OUTPUT_FILE")
OUTPUT_LINES=$(wc -l < "$OUTPUT_FILE")

echo "  Size:      $OUTPUT_SIZE bytes"
echo "  Lines:     $OUTPUT_LINES"
echo "  SHA256:    $OUTPUT_CHECKSUM"
echo ""

# Create checksums file
CHECKSUM_FILE="$(dirname "$OUTPUT_FILE")/$(basename "$OUTPUT_FILE" .tsv)_checksums.txt"
cat > "$CHECKSUM_FILE" << EOF
FIXITY RECORD - TSV Standardization
Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

SOURCE FILE
-----------
Path:     $INPUT_FILE
Size:     $SOURCE_SIZE bytes
Lines:    $SOURCE_LINES
SHA256:   $SOURCE_CHECKSUM

OUTPUT FILE
-----------
Path:     $OUTPUT_FILE
Size:     $OUTPUT_SIZE bytes
Lines:    $OUTPUT_LINES
SHA256:   $OUTPUT_CHECKSUM

VERIFICATION COMMANDS
---------------------
# Verify source file integrity
sha256sum -c <<< "$SOURCE_CHECKSUM  $INPUT_FILE"

# Verify output file integrity
sha256sum -c <<< "$OUTPUT_CHECKSUM  $OUTPUT_FILE"

# Compare files
diff "$INPUT_FILE" "$OUTPUT_FILE" || echo "Files differ (expected)"
EOF

echo "Checksum record saved to: $CHECKSUM_FILE"
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    STANDARDIZATION COMPLETE                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
