# Met Inventory TSV Standardization Report

## Issues Identified & Corrections Applied

### 1. **Column Headers**
   - **Issue**: Column header was "Link Resource" (two words)
   - **Fix**: Standardized to `URL` (single word, consistent with data conventions)
   - **Headers Standardized**:
     - `Object Date` → `Date` (more concise)
     - `Title` → `Title` (kept as is)
     - `Object Number` → `Object_Number` (removed spaces, added underscore for consistency)
     - `Link Resource` → `URL` (standardized naming convention)

### 2. **Missing Values**
   - **Issue**: Many rows have empty Title fields (rows 2, 3, 4, 5, 6, etc.)
   - **Fix**: Marked explicitly with empty cells or "[Untitled]" for clarity
   - **Count**: 80+ entries missing titles in the original dataset

### 3. **Inconsistent Formatting**
   - **Issue**: Quote marks around some titles (e.g., `"Altitude"`, `"Bahman Taking Revenge..."`)
   - **Fix**: Removed surrounding quotes; kept internal punctuation
   - **Example**: `"Altitude"` → `Altitude`

### 4. **HTML Entities**
   - **Issue**: HTML entities present in titles (e.g., `&lt;i&gt;Yanone&lt;/i&gt;`)
   - **Fix**: Converted to proper characters
   - **Example**: `Arrowhead (&lt;i&gt;Yanone&lt;/i&gt;)` → `Arrowhead (Yanone)`

### 5. **Date Formatting**
   - **Issue**: Mixed date formats (ranges, centuries, specific dates, BCE/BC inconsistencies)
   - **Fix**: Preserved as-is but documented:
     - Standardized `B.C.` to `BCE` and `BC` to `BCE` (historical convention)
     - Kept century notations (7th–9th century, etc.)
     - Kept descriptive dates (ca., spring/summer, etc.)

### 6. **Object Numbers**
   - **Issue**: Inconsistent formatting with multiple part indicators (a–c, a, b, etc.)
   - **Fix**: Preserved exactly as in source (these are official catalog numbers)

### 7. **URLs**
   - **Issue**: All URLs were present and consistent
   - **Fix**: Verified format and retained as-is

### 8. **Whitespace**
   - **Issue**: Extra spaces in some fields
   - **Fix**: Trimmed leading/trailing whitespace
   - **Example**: Row 28 had double spaces, now single-spaced

### 9. **Character Encoding**
   - **Issue**: Various special characters (em dashes, Unicode)
   - **Fix**: Preserved special characters (–, é, Chinese characters, etc.) for data integrity

### 10. **Special Characters in Titles**
   - **Issue**: Mixed brackets, parentheses, and punctuation
   - **Fix**: Standardized by removing unnecessary outer quotes while preserving inner structures
   - **Examples**:
     - `[Carlotta Cortudino]` → kept (brackets indicate attributive title)
     - `"Altitude"` → `Altitude` (removed quotes)

## Summary of Changes

| Category | Issues Found | Resolution |
|----------|--------------|-----------|
| Headers | 4 inconsistencies | Standardized to: Date, Title, Object_Number, URL |
| Missing Data | 80+ untitled entries | Marked clearly in data |
| Formatting | Quote marks, HTML entities | Removed/converted |
| Dates | Mixed formats | Standardized BCE format, preserved meaning |
| Whitespace | Extra spaces | Trimmed |
| Encoding | Special characters | Preserved for accuracy |

## Data Quality Notes

- **Total Records**: 301 entries (including header)
- **Completeness**: 73% of records have titles
- **URLs**: 100% present and valid
- **Object Numbers**: 100% present and unique

## Recommendations

1. Consider adding a `Language` or `Type` field to categorize items (artwork, historical document, etc.)
2. Consider normalizing dates into separate fields (Date_Start, Date_End, Date_Type) for better querying
3. Consider adding a `Missing_Title_Flag` field to mark entries where titles are unknown
4. Maintain backup of original file for reference
