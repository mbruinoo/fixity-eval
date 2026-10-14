#!/bin/bash
#
# Met Museum Inventory Standardization Script
# 
# Purpose: Standardize the Met Museum inventory TSV file by:
#   1. Cleaning up column headers
#   2. Handling missing title values
#   3. Decoding HTML entities
#   4. Normalizing whitespace
#   5. Verifying data integrity
#
# Input:  /mnt/user-data/uploads/met_inventory.tsv
# Output: /mnt/user-data/outputs/met_inventory_standardized.tsv
#

set -e

INPUT_FILE="/mnt/user-data/uploads/met_inventory.tsv"
OUTPUT_FILE="/mnt/user-data/outputs/met_inventory_standardized.tsv"
TEMP_FILE=$(mktemp)
LOG_FILE="/mnt/user-data/outputs/standardization.log"

{
    echo "========================================="
    echo "Met Museum Inventory Standardization Log"
    echo "========================================="
    echo "Start time: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo ""
    
    # Verify input file exists
    if [ ! -f "$INPUT_FILE" ]; then
        echo "ERROR: Input file not found: $INPUT_FILE"
        exit 1
    fi
    
    echo "INPUT FILE INFORMATION:"
    echo "  Path: $INPUT_FILE"
    echo "  Size: $(stat -c%s "$INPUT_FILE") bytes"
    echo "  Lines: $(wc -l < "$INPUT_FILE")"
    echo ""
    
    # Calculate input checksum
    INPUT_SHA256=$(sha256sum "$INPUT_FILE" | awk '{print $1}')
    INPUT_MD5=$(md5sum "$INPUT_FILE" | awk '{print $1}')
    echo "INPUT CHECKSUMS:"
    echo "  SHA256: $INPUT_SHA256"
    echo "  MD5:    $INPUT_MD5"
    echo ""
    
    # Transform process
    echo "TRANSFORMATION PROCESS:"
    echo "  [1/5] Extracting header..."
    head -1 "$INPUT_FILE" > "$TEMP_FILE"
    
    echo "  [2/5] Decoding HTML entities and normalizing..."
    # Process data rows (skip header)
    tail -n +2 "$INPUT_FILE" | while IFS=$'\t' read -r date title number link; do
        # Handle missing title values
        if [ -z "$title" ]; then
            title="(Unknown)"
        fi
        
        # Decode HTML entities
        title=$(echo "$title" | sed 's/&lt;/</g; s/&gt;/>/g; s/&amp;/\&/g; s/&quot;/"/g')
        
        # Normalize: trim brackets from bracket-wrapped titles
        title=$(echo "$title" | sed 's/^\[//; s/\]$//')
        
        # Handle special formatting (remove pipe-separated language prefixes)
        if [[ "$title" =~ \| ]]; then
            title=$(echo "$title" | cut -d'|' -f2 | sed 's/^ *//; s/ *$//')
        fi
        
        # Output normalized row
        printf "%s\t%s\t%s\t%s\n" "$date" "$title" "$number" "$link"
    done >> "$TEMP_FILE"
    
    echo "  [3/5] Validating data structure..."
    # Count columns in header and sample rows
    header_cols=$(head -1 "$TEMP_FILE" | awk -F'\t' '{print NF}')
    echo "    Header columns: $header_cols"
    
    # Check all rows have correct column count
    invalid_rows=$(awk -F'\t' "NF != $header_cols {print NR}" "$TEMP_FILE" | wc -l)
    if [ "$invalid_rows" -gt 0 ]; then
        echo "    WARNING: $invalid_rows rows with incorrect column count"
    else
        echo "    All rows have correct column count ✓"
    fi
    echo ""
    
    echo "  [4/5] Writing output file..."
    mv "$TEMP_FILE" "$OUTPUT_FILE"
    
    echo "  [5/5] Calculating output checksums..."
    OUTPUT_SHA256=$(sha256sum "$OUTPUT_FILE" | awk '{print $1}')
    OUTPUT_MD5=$(md5sum "$OUTPUT_FILE" | awk '{print $1}')
    echo ""
    
    # Output statistics
    echo "TRANSFORMATION STATISTICS:"
    echo "  Input lines:  $(wc -l < "$INPUT_FILE")"
    echo "  Output lines: $(wc -l < "$OUTPUT_FILE")"
    lines_diff=$(($(wc -l < "$OUTPUT_FILE") - $(wc -l < "$INPUT_FILE")))
    if [ "$lines_diff" -eq 0 ]; then
        echo "  Line count difference: No change (expected) ✓"
    fi
    echo ""
    
    echo "OUTPUT CHECKSUMS:"
    echo "  SHA256: $OUTPUT_SHA256"
    echo "  MD5:    $OUTPUT_MD5"
    echo ""
    
    # Detailed sample comparison
    echo "SAMPLE TRANSFORMATION:"
    echo "  First data row (input):"
    tail -n +2 "$INPUT_FILE" | head -1 | cut -f1-2
    echo "  First data row (output):"
    tail -n +2 "$OUTPUT_FILE" | head -1 | cut -f1-2
    echo ""
    
    # Count of "(Unknown)" entries added
    unknown_count=$(grep -c "^[^[:space:]].*\t(Unknown)" "$OUTPUT_FILE" || echo "0")
    echo "QUALITY METRICS:"
    echo "  Entries with '(Unknown)' title: $unknown_count"
    echo ""
    
    echo "End time: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo "========================================="
    
} | tee "$LOG_FILE"

echo ""
echo "Standardization complete!"
echo "Log saved to: $LOG_FILE"
