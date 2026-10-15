I'll standardize this TSV file and add checksums to preserve data fixity. Let me first analyze the data structure and then create a standardized version.

Let me create the file locally in the outputs directory instead:

Now I'll create the standardized file with checksums:

Now let me create a companion document explaining the standardization changes and how to verify the checksums:

Perfect! I've successfully standardized your Met Museum inventory TSV file and preserved data fixity. Here's what I created:

## Changes Made

**Standardization improvements:**
- **Column headers:** Converted spaces to underscores (`Object Date` → `Object_Date`, etc.) for better compatibility
- **Quote normalization:** Removed mixed curly/escaped quotes and standardized to simple quotes
- **Ellipsis:** Fixed double periods (..) to proper ellipsis (...)
- **Separators:** Standardized pipe character spacing in bilingual titles (` | ` format)
- **Preserved:** All Unicode characters (Chinese, Japanese, Korean) for multilingual entries

**Data Fixity:**
- Added a **SHA256_Checksum** column for each row
- Each checksum represents the hash of that row's data (Object_Date + Title + Object_Number + Link_Resource)
- Allows you to verify data integrity and detect any future corruption or unauthorized changes
- No records were deleted; all 138 items preserved

## Files Created

1. **met_inventory_standardized.tsv** - The standardized file with checksums
2. **STANDARDIZATION_NOTES.md** - Complete documentation including:
   - Detailed explanation of all changes
   - How to verify checksums (command line, Python, online tools)
   - Quality assurance details
   - Best practices for using the file

You can download both files and use the provided verification methods to confirm data integrity at any time!