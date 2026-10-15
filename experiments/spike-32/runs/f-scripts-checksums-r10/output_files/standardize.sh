#!/bin/bash
# TSV Standardizer Wrapper Script
# Standardizes Met Museum inventory TSV with checksum preservation

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_FILE="${1:-met_inventory.tsv}"
OUTPUT_FILE="${2:-met_inventory_standardized.tsv}"
CHECKSUM_LOG="checksums.json"
VERIFICATION_LOG="verification.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

verify_checksums() {
    log_info "Verifying checksums..."
    
    if [ ! -f "$CHECKSUM_LOG" ]; then
        log_error "Checksum log not found"
        return 1
    fi
    
    local source_file=$(jq -r '.source_file' "$CHECKSUM_LOG")
    local source_checksum=$(jq -r '.source_checksum_sha256' "$CHECKSUM_LOG")
    local output_file=$(jq -r '.output_file' "$CHECKSUM_LOG")
    local output_checksum=$(jq -r '.output_checksum_sha256' "$CHECKSUM_LOG")
    
    log_info "Verifying source file integrity..."
    local current_source_checksum=$(sha256sum "$source_file" | awk '{print $1}')
    
    if [ "$source_checksum" = "$current_source_checksum" ]; then
        log_info "✓ Source file integrity verified"
        echo "Source file: $source_file" >> "$VERIFICATION_LOG"
        echo "  Expected: $source_checksum" >> "$VERIFICATION_LOG"
        echo "  Actual:   $current_source_checksum" >> "$VERIFICATION_LOG"
        echo "  Status: ✓ VERIFIED" >> "$VERIFICATION_LOG"
    else
        log_error "Source file checksum mismatch!"
        echo "Source file: $source_file" >> "$VERIFICATION_LOG"
        echo "  Expected: $source_checksum" >> "$VERIFICATION_LOG"
        echo "  Actual:   $current_source_checksum" >> "$VERIFICATION_LOG"
        echo "  Status: ✗ MISMATCH" >> "$VERIFICATION_LOG"
        return 1
    fi
    
    log_info "Verifying output file integrity..."
    local current_output_checksum=$(sha256sum "$output_file" | awk '{print $1}')
    
    if [ "$output_checksum" = "$current_output_checksum" ]; then
        log_info "✓ Output file integrity verified"
        echo "Output file: $output_file" >> "$VERIFICATION_LOG"
        echo "  Expected: $output_checksum" >> "$VERIFICATION_LOG"
        echo "  Actual:   $current_output_checksum" >> "$VERIFICATION_LOG"
        echo "  Status: ✓ VERIFIED" >> "$VERIFICATION_LOG"
    else
        log_error "Output file checksum mismatch!"
        echo "Output file: $output_file" >> "$VERIFICATION_LOG"
        echo "  Expected: $output_checksum" >> "$VERIFICATION_LOG"
        echo "  Actual:   $current_output_checksum" >> "$VERIFICATION_LOG"
        echo "  Status: ✗ MISMATCH" >> "$VERIFICATION_LOG"
        return 1
    fi
    
    return 0
}

show_stats() {
    log_info "File Statistics"
    echo "================"
    echo "Source file ($INPUT_FILE):"
    wc -l < "$INPUT_FILE" | xargs -I {} echo "  Lines: {}"
    echo "  Size: $(du -h "$INPUT_FILE" | cut -f1)"
    
    echo ""
    echo "Output file ($OUTPUT_FILE):"
    wc -l < "$OUTPUT_FILE" | xargs -I {} echo "  Lines: {}"
    echo "  Size: $(du -h "$OUTPUT_FILE" | cut -f1)"
}

# Main execution
main() {
    echo "======================================"
    echo "TSV Standardizer with Checksum Preservation"
    echo "======================================"
    echo ""
    
    # Check if input file exists
    if [ ! -f "$INPUT_FILE" ]; then
        log_error "Input file not found: $INPUT_FILE"
        exit 1
    fi
    
    log_info "Input file: $INPUT_FILE"
    log_info "Output file: $OUTPUT_FILE"
    
    # Clear previous verification log
    > "$VERIFICATION_LOG"
    
    # Run Python standardization script
    log_info "Running standardization script..."
    python3 "$SCRIPT_DIR/standardize_tsv.py" "$INPUT_FILE" "$OUTPUT_FILE"
    
    if [ $? -ne 0 ]; then
        log_error "Standardization failed"
        exit 1
    fi
    
    # Show statistics
    echo ""
    show_stats
    
    # Verify checksums
    echo ""
    verify_checksums
    
    if [ $? -eq 0 ]; then
        echo ""
        log_info "All verifications passed!"
        echo ""
        log_info "Checksum verification report saved to: $VERIFICATION_LOG"
        cat "$VERIFICATION_LOG"
    else
        log_warning "Some verifications failed. Check $VERIFICATION_LOG"
    fi
}

# Execute main function
main
