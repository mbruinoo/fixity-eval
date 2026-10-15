#!/bin/bash
# Checksum Verification Utility
# Verifies the integrity of standardized files using stored checksums

set -e

CHECKSUM_LOG="checksums.json"
VERIFICATION_REPORT="checksum_verification_report.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_header() {
    echo -e "\n${BLUE}$1${NC}"
    echo "================================"
}

verify_file() {
    local file_path=$1
    local expected_hash=$2
    
    if [ ! -f "$file_path" ]; then
        log_error "File not found: $file_path"
        return 1
    fi
    
    local actual_hash=$(sha256sum "$file_path" | awk '{print $1}')
    
    if [ "$expected_hash" = "$actual_hash" ]; then
        log_info "File verified: $file_path"
        echo "  Expected: $expected_hash" | tee -a "$VERIFICATION_REPORT"
        echo "  Actual:   $actual_hash" | tee -a "$VERIFICATION_REPORT"
        echo "  Status:   ✓ MATCH" | tee -a "$VERIFICATION_REPORT"
        return 0
    else
        log_error "Checksum mismatch: $file_path"
        echo "  Expected: $expected_hash" | tee -a "$VERIFICATION_REPORT"
        echo "  Actual:   $actual_hash" | tee -a "$VERIFICATION_REPORT"
        echo "  Status:   ✗ MISMATCH - File may have been modified!" | tee -a "$VERIFICATION_REPORT"
        return 1
    fi
}

show_usage() {
    echo "Checksum Verification Utility"
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -c, --checksum LOG      Use specified checksum log (default: checksums.json)"
    echo "  -v, --verbose           Show verbose output"
    echo "  --html                  Generate HTML report"
    echo ""
    echo "Examples:"
    echo "  $0                          # Verify using default checksums.json"
    echo "  $0 --checksum my_checks.json # Use custom checksum log"
    echo "  $0 --verbose                # Show detailed output"
}

generate_html_report() {
    local html_file="checksum_verification_report.html"
    local timestamp=$(date)
    
    cat > "$html_file" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Checksum Verification Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
        .section { margin-top: 20px; }
        .verified { color: green; font-weight: bold; }
        .failed { color: red; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .monospace { font-family: 'Courier New', monospace; word-break: break-all; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Checksum Verification Report</h1>
        <p>Generated: TIMESTAMP</p>
    </div>
EOF
    
    # Add verification results
    if [ -f "$VERIFICATION_REPORT" ]; then
        echo "    <div class='section'>" >> "$html_file"
        echo "        <h2>Verification Results</h2>" >> "$html_file"
        echo "        <pre>" >> "$html_file"
        cat "$VERIFICATION_REPORT" >> "$html_file"
        echo "        </pre>" >> "$html_file"
        echo "    </div>" >> "$html_file"
    fi
    
    cat >> "$html_file" << 'EOF'
</body>
</html>
EOF
    
    sed -i "s/TIMESTAMP/$(date)/" "$html_file"
    echo "HTML report generated: $html_file"
}

main() {
    # Parse arguments
    VERBOSE=0
    GENERATE_HTML=0
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -c|--checksum)
                CHECKSUM_LOG="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=1
                shift
                ;;
            --html)
                GENERATE_HTML=1
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Clear previous report
    > "$VERIFICATION_REPORT"
    
    # Check if checksum log exists
    if [ ! -f "$CHECKSUM_LOG" ]; then
        log_error "Checksum log not found: $CHECKSUM_LOG"
        echo "Please run standardization first or use -c to specify the log file."
        exit 1
    fi
    
    # Display header
    clear
    log_header "CHECKSUM VERIFICATION UTILITY"
    
    {
        echo "Checksum Verification Report"
        echo "Generated: $(date)"
        echo "Checksum Log: $CHECKSUM_LOG"
        echo ""
    } | tee -a "$VERIFICATION_REPORT"
    
    # Extract data from JSON
    echo "Loading checksums from $CHECKSUM_LOG..." | tee -a "$VERIFICATION_REPORT"
    
    # Check if jq is available for JSON parsing
    if command -v jq &> /dev/null; then
        source_file=$(jq -r '.source_file' "$CHECKSUM_LOG")
        source_hash=$(jq -r '.source_checksum_sha256' "$CHECKSUM_LOG")
        output_file=$(jq -r '.output_file' "$CHECKSUM_LOG")
        output_hash=$(jq -r '.output_checksum_sha256' "$CHECKSUM_LOG")
        timestamp=$(jq -r '.timestamp' "$CHECKSUM_LOG")
        algorithm=$(jq -r '.algorithm' "$CHECKSUM_LOG")
    else
        # Fallback to grep if jq not available
        log_warning "jq not found, using grep for parsing"
        source_file=$(grep '"source_file"' "$CHECKSUM_LOG" | cut -d'"' -f4)
        source_hash=$(grep '"source_checksum_sha256"' "$CHECKSUM_LOG" | head -1 | cut -d'"' -f4)
        output_file=$(grep '"output_file"' "$CHECKSUM_LOG" | cut -d'"' -f4)
        output_hash=$(grep '"output_checksum_sha256"' "$CHECKSUM_LOG" | cut -d'"' -f4)
        timestamp=$(grep '"timestamp"' "$CHECKSUM_LOG" | cut -d'"' -f4)
        algorithm=$(grep '"algorithm"' "$CHECKSUM_LOG" | cut -d'"' -f4)
    fi
    
    {
        echo "Algorithm: $algorithm"
        echo "Standardization Timestamp: $timestamp"
        echo ""
    } | tee -a "$VERIFICATION_REPORT"
    
    # Verify source file
    log_header "Verifying Source File"
    {
        echo "File: $source_file"
        echo ""
    } | tee -a "$VERIFICATION_REPORT"
    
    SOURCE_VALID=0
    if verify_file "$source_file" "$source_hash"; then
        SOURCE_VALID=1
        echo "" | tee -a "$VERIFICATION_REPORT"
    else
        echo "" | tee -a "$VERIFICATION_REPORT"
        log_warning "Source file verification failed - file may have been modified"
    fi
    
    # Verify output file
    log_header "Verifying Output File"
    {
        echo "File: $output_file"
        echo ""
    } | tee -a "$VERIFICATION_REPORT"
    
    OUTPUT_VALID=0
    if verify_file "$output_file" "$output_hash"; then
        OUTPUT_VALID=1
        echo "" | tee -a "$VERIFICATION_REPORT"
    else
        echo "" | tee -a "$VERIFICATION_REPORT"
        log_warning "Output file verification failed - file may have been modified"
    fi
    
    # Summary
    log_header "VERIFICATION SUMMARY"
    
    {
        echo ""
        if [ $SOURCE_VALID -eq 1 ] && [ $OUTPUT_VALID -eq 1 ]; then
            echo "✓ ALL FILES VERIFIED SUCCESSFULLY"
            echo "  Both source and output files match their stored checksums."
            echo "  Data integrity is confirmed."
        else
            echo "✗ VERIFICATION FAILED"
            if [ $SOURCE_VALID -eq 0 ]; then
                echo "  ✗ Source file checksum mismatch"
            fi
            if [ $OUTPUT_VALID -eq 0 ]; then
                echo "  ✗ Output file checksum mismatch"
            fi
            echo ""
            echo "This may indicate:"
            echo "  - Files have been modified or corrupted"
            echo "  - Files have been moved or renamed"
            echo "  - Checksum log is for different files"
        fi
        echo ""
    } | tee -a "$VERIFICATION_REPORT"
    
    # Generate HTML if requested
    if [ $GENERATE_HTML -eq 1 ]; then
        echo "" | tee -a "$VERIFICATION_REPORT"
        generate_html_report
    fi
    
    # Show report location
    log_info "Detailed report saved to: $VERIFICATION_REPORT"
    
    # Return appropriate exit code
    if [ $SOURCE_VALID -eq 1 ] && [ $OUTPUT_VALID -eq 1 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main "$@"
