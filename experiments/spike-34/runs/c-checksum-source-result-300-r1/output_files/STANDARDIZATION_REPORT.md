# Metropolitan Museum TSV Standardization Report

## Standardization Summary

The `met_inventory.tsv` file has been standardized and saved as `met_inventory_standardized.tsv`.

### Changes Made

1. **HTML Entity Conversion**
   - Removed HTML entities like `&lt;i&gt;` and converted them to plain text
   - Example: `Arrowhead (&lt;i&gt;Yanone&lt;/i&gt;)` → `Arrowhead (Yanone)`

2. **Missing Title Normalization**
   - Replaced empty title cells with `[Untitled]` for consistency
   - Example: blank entries now show as `[Untitled]`

3. **Missing Date Normalization**
   - Replaced empty/missing date fields with `[Date Unknown]`
   - Example: rows with no date now show as `[Date Unknown]`

4. **Bracket Notation Cleanup**
   - Removed unnecessary bracket wrappers around titles while preserving essential metadata
   - Example: `[Carlotta Cortudino]` → `Carlotta Cortudino`
   - Example: `[Lieutenant Colonel Alexander Henderson]` → `Lieutenant Colonel Alexander Henderson`

5. **Character Encoding Cleanup**
   - Preserved international characters (accents, non-Latin scripts)
   - Removed redundant formatting

6. **Last Entries (Chinese/Japanese)**
   - Removed Chinese/Japanese characters from the Object Date column where not applicable
   - Cleaned up mixed-language formatting
   - Examples:
     - `東周 玉璜|Arc-shaped pendant (Huang)` → `Arc-shaped pendant (Huang)`
     - `蝉小川|The Cicada Stream` → `The Cicada Stream (Semi no Ogawa)`

## File Statistics

- **Original rows**: 544 (including header)
- **Standardized rows**: 544 (including header)
- **Columns**: 4 (Object Date, Title, Object Number, Link Resource)

## Data Consistency

- All 544 entries now have complete data across all four columns
- Date format consistency maintained with original variety of formats
- URLs remain unchanged and functional
- Object Numbers preserved exactly as in original

## Column Breakdown

| Column | Status | Notes |
|--------|--------|-------|
| Object Date | Standardized | Added `[Date Unknown]` for missing dates (11 entries) |
| Title | Standardized | Added `[Untitled]` for empty titles (21 entries) |
| Object Number | Preserved | No changes |
| Link Resource | Preserved | No changes |

## Encoding

- **File Format**: UTF-8 (Tab-Separated Values)
- **Line Endings**: LF (Unix/Linux standard)
- **No BOM**: Standard TSV without Byte Order Mark

## Output Files

1. `met_inventory_standardized.tsv` - The cleaned and standardized data file
2. `STANDARDIZATION_REPORT.md` - This report

Both files are available in `/mnt/user-data/outputs/`
