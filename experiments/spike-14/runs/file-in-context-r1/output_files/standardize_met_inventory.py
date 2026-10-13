#!/usr/bin/env python3
"""
================================================================================
MET MUSEUM INVENTORY TSV STANDARDIZATION SCRIPT
================================================================================
Purpose: Standardize Metropolitan Museum of Art inventory TSV file
Author: Data Processing Pipeline
Date Created: 2024

FIXITY VERIFICATION:
  Input File:  met_inventory.tsv
  Input MD5:   6ec5bfc2d979ad12eb3343149beb8617
  Output File: met_inventory_standardized.tsv
  Output MD5:  [Generated during execution]

TRANSFORMATION RULES:
  1. Decode HTML entities (&lt; → <, &gt; → >, &amp; → &, etc.)
  2. Normalize whitespace in Title field (collapse multiple spaces to single)
  3. Preserve tab-separated structure and column order
  4. Maintain all data values (including empty cells)
  5. Ensure UTF-8 encoding throughout
  6. Validate column count consistency
  7. Generate processing log

COLUMNS (Tab-Separated):
  1. Object Date       - Date or date range of the object
  2. Title            - Title or description of the artwork
  3. Object Number    - Museum catalog/accession number
  4. Link Resource    - URL to the object in the museum collection

================================================================================
"""

import re
import sys
import hashlib
from datetime import datetime
from pathlib import Path

# Configuration
INPUT_FILE = "met_inventory.tsv"
OUTPUT_FILE = "met_inventory_standardized.tsv"
LOG_FILE = "standardization_log.txt"
EXPECTED_COLUMNS = 4

# HTML entity mapping for decoding
HTML_ENTITIES = {
    '&lt;': '<',
    '&gt;': '>',
    '&amp;': '&',
    '&quot;': '"',
    '&apos;': "'",
    '&#39;': "'",
}

class Logger:
    """Simple logging utility"""
    def __init__(self, filename):
        self.filename = filename
        self.messages = []
        self.log_line(f"Standardization Process Log - {datetime.now().isoformat()}")
        self.log_line("=" * 80)
    
    def log_line(self, msg):
        self.messages.append(msg)
        print(msg)
    
    def write(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.messages) + '\n')


def calculate_md5(filepath):
    """Calculate MD5 checksum of a file"""
    md5 = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5.update(chunk)
        return md5.hexdigest()
    except FileNotFoundError:
        return None


def decode_html_entities(text):
    """Decode HTML entities in text"""
    if not text:
        return text
    
    result = text
    for entity, char in HTML_ENTITIES.items():
        result = result.replace(entity, char)
    
    return result


def normalize_whitespace(text):
    """Normalize whitespace: collapse multiple spaces to single space"""
    if not text:
        return text
    
    # Replace multiple spaces/tabs with single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def standardize_row(row_index, parts):
    """
    Standardize a single row of data
    
    Args:
        row_index: Line number (for error reporting)
        parts: List of tab-separated values
    
    Returns:
        Tuple: (standardized_parts, warnings_list)
    """
    warnings = []
    
    # Validate column count
    if len(parts) != EXPECTED_COLUMNS:
        warnings.append(
            f"Row {row_index}: Expected {EXPECTED_COLUMNS} columns, got {len(parts)}"
        )
    
    # Process each column
    standardized = []
    
    for col_idx, part in enumerate(parts):
        if col_idx == 1:  # Title column (index 1)
            # Decode HTML entities
            part = decode_html_entities(part)
            # Normalize whitespace
            part = normalize_whitespace(part)
        else:
            # For other columns, just decode entities
            part = decode_html_entities(part)
        
        standardized.append(part)
    
    return standardized, warnings


def process_file(input_path, output_path, logger):
    """
    Main file processing function
    
    Args:
        input_path: Path to input TSV file
        output_path: Path to output TSV file
        logger: Logger instance
    """
    
    logger.log_line("\n[STEP 1] Verifying input file...")
    
    if not Path(input_path).exists():
        logger.log_line(f"ERROR: Input file not found: {input_path}")
        return False
    
    input_md5 = calculate_md5(input_path)
    logger.log_line(f"  Input file: {input_path}")
    logger.log_line(f"  Input MD5:  {input_md5}")
    
    logger.log_line("\n[STEP 2] Reading input file...")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError as e:
        logger.log_line(f"ERROR: Unicode decode error: {e}")
        return False
    
    logger.log_line(f"  Total lines read: {len(lines)}")
    
    logger.log_line("\n[STEP 3] Processing data...")
    
    standardized_lines = []
    total_warnings = 0
    stats = {
        'rows_processed': 0,
        'rows_with_warnings': 0,
        'html_entities_decoded': 0,
        'whitespace_normalized': 0,
    }
    
    for idx, line in enumerate(lines, 1):
        # Remove trailing newline
        line_content = line.rstrip('\n')
        
        # Split by tabs
        parts = line_content.split('\t')
        
        # Header row (row 1) - pass through as-is
        if idx == 1:
            standardized_lines.append(line)
            logger.log_line(f"  Row {idx}: Header row (passed through)")
            continue
        
        # Data rows
        stats['rows_processed'] += 1
        
        # Count HTML entities before
        entities_before = sum(line_content.count(e) for e in HTML_ENTITIES.keys())
        
        # Standardize row
        standardized, warnings = standardize_row(idx, parts)
        
        if entities_before > 0:
            stats['html_entities_decoded'] += entities_before
        
        if warnings:
            stats['rows_with_warnings'] += 1
            for warning in warnings:
                logger.log_line(f"  {warning}")
            total_warnings += len(warnings)
        
        # Rejoin with tabs
        standardized_line = '\t'.join(standardized) + '\n'
        standardized_lines.append(standardized_line)
    
    logger.log_line("\n[STEP 4] Writing output file...")
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(standardized_lines)
    except IOError as e:
        logger.log_line(f"ERROR: Could not write output file: {e}")
        return False
    
    logger.log_line(f"  Output file: {output_path}")
    logger.log_line(f"  Total lines written: {len(standardized_lines)}")
    
    logger.log_line("\n[STEP 5] Verifying output file...")
    
    output_md5 = calculate_md5(output_path)
    logger.log_line(f"  Output MD5: {output_md5}")
    
    logger.log_line("\n[STEP 6] Processing Statistics...")
    logger.log_line(f"  Rows processed:              {stats['rows_processed']}")
    logger.log_line(f"  Rows with warnings:          {stats['rows_with_warnings']}")
    logger.log_line(f"  HTML entities decoded:       {stats['html_entities_decoded']}")
    logger.log_line(f"  Total warnings:              {total_warnings}")
    
    logger.log_line("\n" + "=" * 80)
    logger.log_line("FIXITY VERIFICATION SUMMARY")
    logger.log_line("=" * 80)
    logger.log_line(f"Input MD5:  {input_md5}")
    logger.log_line(f"Output MD5: {output_md5}")
    logger.log_line(f"Status:     PROCESSING COMPLETE")
    logger.log_line("=" * 80)
    
    logger.log_line(f"\nLog file written to: {LOG_FILE}")
    
    return True


def main():
    """Main entry point"""
    print("\n" + "=" * 80)
    print("MET MUSEUM INVENTORY TSV STANDARDIZATION")
    print("=" * 80 + "\n")
    
    logger = Logger(LOG_FILE)
    
    success = process_file(INPUT_FILE, OUTPUT_FILE, logger)
    
    logger.write()
    
    if success:
        print(f"\n✓ SUCCESS: Standardization complete!")
        print(f"  Output file: {OUTPUT_FILE}")
        print(f"  Log file:    {LOG_FILE}")
        return 0
    else:
        print(f"\n✗ FAILURE: Standardization failed. Check {LOG_FILE} for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
