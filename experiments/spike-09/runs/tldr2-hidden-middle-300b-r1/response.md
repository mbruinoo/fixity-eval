I'll help you standardize this TSV file. Let me start by viewing it to understand its structure.

Good! I can see the file has 300 data rows (rows 2-301) plus a header row (row 1). Let me check if there are more rows beyond what was shown:

Perfect! The file has **300 data rows** (plus 1 header row). Now let me analyze the content to standardize it. Looking at the data, I can identify these standardization opportunities:

1. **Dashes**: Convert hyphens/dashes to en-dashes (–) for date ranges
2. **HTML entities**: Convert `&lt;i&gt;` and `&lt;/i&gt;` to proper italic formatting or plain text
3. **Spacing**: Remove extra spaces where appropriate
4. **Quotation marks**: Standardize quote marks

Let me create a Python script to process this file carefully:

Now let me create a Python script to read the file and make standardization changes. The main standardization issues I see are:

1. HTML entities (`&lt;i&gt;` and `&lt;/i&gt;`) should be removed (keeping just the text)
2. Multiple spaces between words should be reduced to single spaces

Let me create the standardized version:

Now let me compare the original file with the output to identify all changes made:

Perfect! Now let me create a summary of the changes:

## Summary

**File Statistics:**
- **Rows in:** 301 rows (1 header + 300 data rows)
- **Rows out:** 301 rows (1 header + 300 data rows) ✓

**Changes Made:**

I standardized the file by making the following changes to exactly **2 cells**:

| Row | Column | Before | After |
|-----|--------|--------|-------|
| 28 | 2 (Title) | `"Bahman Taking Revenge on the Sistanians"  Folio from the Majma' al-Tavarikh (Compendium of Histories) of Hafiz-i Abru` | `"Bahman Taking Revenge on the Sistanians" Folio from the Majma' al-Tavarikh (Compendium of Histories) of Hafiz-i Abru` |
| 49 | 2 (Title) | `Arrowhead (&lt;i&gt;Yanone&lt;/i&gt;)` | `Arrowhead (Yanone)` |
| 298 | 2 (Title) | `蝉小川\|The Cicada Stream (Semi no Ogawa)  蝉小川` | `蝉小川\|The Cicada Stream (Semi no Ogawa) 蝉小川` |

**Standardization rules applied:**
1. **Removed extra spaces:** Changed double spaces to single spaces between titles and descriptions
2. **Removed HTML entities:** Converted `&lt;i&gt;` and `&lt;/i&gt;` to regular text (removed the markup while keeping the italicized text)
3. **Preserved everything else:** All accents, punctuation, non-English text, ID numbers, qualifiers like "ca." and "?", and blank cells remain exactly as they were

The standardized file is ready at `/mnt/user-data/outputs/met_inventory.tsv`