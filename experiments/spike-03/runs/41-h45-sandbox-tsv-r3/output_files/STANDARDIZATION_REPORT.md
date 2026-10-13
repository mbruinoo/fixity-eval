# TSV Standardization Report
## met_objects_list.tsv

### Summary
- **Original Records**: 100 rows
- **Standardized Records**: 100 rows (no duplicates removed)
- **Total Columns**: 5

---

## Changes Made

### 1. **Column Headers Standardization**
| Original | Standardized |
|----------|--------------|
| `Object Date` | `object_date` |
| `Title` | `title` |
| `Artist Display Name` | `artist_display_name` |
| `Object Number` | `object_number` |
| `Link Resource` | `link_resource` |

**Changes**: Converted to lowercase snake_case for consistency and programming convenience.

---

### 2. **Missing Data Handling**

#### Empty Dates (4 records)
- **Before**: Empty/missing
- **After**: `Unknown date`
- **Examples**: Records with no date information

#### Empty Titles (3 records)
- **Before**: Empty/missing
- **After**: `Untitled`
- **Examples**: Some artifact records

#### Missing Artist Names (31 records)
- **Before**: Empty/blank
- **After**: `Unknown`
- **Records**: 31 items with no artist attribution

#### Object Numbers
- **Status**: All records had object numbers (no missing values)

---

### 3. **Date Format Standardization**

**Standardizations Applied**:
- Normalized `B.C.` and `B.C` → `BCE` (standardized abbreviation)
- Consistent spacing around date ranges
- Preserved various date formats (centuries, approximate dates, exact years)

**Examples of Date Formats Retained**:
- Exact years: `1896`, `1770`, `1912`
- Approximate: `ca. 1896`, `ca. 500 BCE`
- Ranges: `1830–40`, `16th–17th century`
- Centuries: `18th century`, `early 20th century`
- BCE notation: `ca. 3800–3300 BCE`, `530 BCE`
- Approximate ranges: `late 19th–early 20th century`

---

### 4. **Sorting**

**Method**: Records sorted chronologically by date (oldest to newest)
- Ancient dates (BCE) sorted first (negative values)
- Records with "Unknown date" placed at end
- Within same year/period, maintains original relative order

**Result**: Chronological organization from 3800 BCE to 2018 CE

---

### 5. **Data Quality Summary**

| Field | Complete | Missing | % Complete |
|-------|----------|---------|-----------|
| object_date | 96 | 4 | 96% |
| title | 97 | 3 | 97% |
| artist_display_name | 69 | 31 | 69% |
| object_number | 100 | 0 | 100% |
| link_resource | 100 | 0 | 100% |

---

### 6. **File Format Details**

- **Format**: Tab-Separated Values (TSV)
- **Encoding**: UTF-8
- **Delimiter**: Tab character (`\t`)
- **Quoting**: All fields quoted for consistency
- **Line Endings**: Standard (LF)

---

### 7. **Special Cases Handled**

1. **Multiple Artists**: Pipe-separated (e.g., `"Onesimos|Euphronios"`)
2. **Non-English Titles**: Unicode preserved (e.g., Chinese and Japanese characters)
3. **Complex Object Numbers**: Preserved with commas and parentheses (e.g., `"42.205.283a, b"`, `"1994.220(2.19)"`)
4. **URLs**: Properly formatted and validated

---

## Output File

**Filename**: `met_objects_list_standardized.tsv`
**Location**: Ready for export

### Sample Records (First 10)

```
1. ca. 3800–3300 BCE | Terracotta rim of a bowl | Unknown | 30.119.35
2. ca. 1981–1550 BCE | Spacer (?) | Unknown | 16.7.20
3. ca. 1390–1352 BCE | Jar Label | Unknown | 17.10.475
4. ca. 600–550 BCE | Terracotta vase in the shape of a bird | Unknown | 69.11.2
5. 530 BCE | Terracotta rim fragment of a kylix: eye-cup (drinking cup) | Unknown | 2011.604.3.2285
```

---

## Recommendations

1. **Artist Data**: Consider researching and filling in the 31 missing artist records
2. **Titles**: Investigate the 3 untitled records in the collection
3. **Date Accuracy**: Consider standardizing all approximate dates to a consistent format
4. **Data Validation**: Implement validation rules for future data imports
5. **URI Standardization**: Consider validating all URLs are still active

---

## Version Information
- **Standardization Date**: 2024
- **Python Version**: 3.x
- **Libraries Used**: pandas, re (regular expressions)
