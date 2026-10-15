I'll help you standardize this TSV file. Let me first analyze it and then create a script to standardize it while preserving fixity with checksums.

Now let me create a comprehensive standardization script with checksum verification:

Now let me create a bash wrapper script for easier usage:

Now let me create a verification script you can use later:

Finally, let me create comprehensive documentation:

Perfect! I've created a comprehensive standardization toolkit with checksum verification. Here's what you have:

## Summary

I've created **4 files** for standardizing your TSV with fixity preservation:

### Scripts:
1. **`standardize_tsv.py`** - Main Python script that:
   - Calculates SHA-256 checksums of source and output
   - Normalizes line endings, delimiters, encoding
   - Validates row consistency
   - Generates detailed reports

2. **`standardize.sh`** - Bash wrapper for easy command-line use
3. **`verify_checksums.sh`** - Verification script to check integrity later

### Documentation:
4. **`README.md`** - Comprehensive guide covering:
   - How to use the scripts
   - What gets standardized
   - Understanding checksums and fixity
   - Troubleshooting tips
   - Best practices for data preservation

## Key Features:

✓ **Checksum-based fixity** - SHA-256 hashes ensure no data corruption  
✓ **Detailed reporting** - Human and machine-readable output  
✓ **Comprehensive validation** - Detects structural issues  
✓ **Standardization** - Consistent line endings, delimiters, encoding  
✓ **Future verification** - Check file integrity any time

To use it on your `met_inventory.tsv`, simply run:
```bash
python3 standardize_tsv.py met_inventory.tsv
```

All files are ready in `/mnt/user-data/outputs/`!