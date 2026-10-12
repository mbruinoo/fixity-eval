I can add those columns, but the spreadsheet has no Start Year or End Year data to pull from. The only date information is the "Object Date" column, which contains free-text values like "ca. 1896", "1770", "ca. 600–550 BCE", "18th century", "late 19th–early 20th century", "A.H. 139–48/ 757–66 CE", and "ca. 1981–1550 B.C.".

Here is what I can do:

1. **Parse the Object Date into Start Year and End Year** using these rules:
   - Single year (e.g., "1770") → Start Year = End Year = 1770
   - Year range (e.g., "1830–40", "1830–1840") → Start 1830, End 1840
   - "ca." dates → use the stated year for both (e.g., "ca. 1896" → 1896 / 1896), or approximate a range if you prefer
   - Century (e.g., "18th century") → Start 1700, End 1799
   - Half-century (e.g., "mid-19th century" → 1825 / 1875; "late 19th–early 20th century" → 1875 / 1930)
   - BCE dates → negative numbers (e.g., "ca. 600–550 BCE" → -600 / -550), or whatever convention you prefer
   - Blank or unknown dates → leave empty, or mark as "Unknown"

2. **Mark uncertain entries** (e.g., "probably 11th century", "dated 1637", "1850–1914") in a separate Notes column if you want to keep track of how each one was interpreted.

Should I proceed with the parsing? Also let me know:
- Whether you want BCE years as negative numbers or as text like "600 BCE"
- How to handle century and "mid/late/early" descriptors (the defaults above are reasonable, but you may have a preference)
- Whether to return the table as CSV, a markdown table, or both

Once you confirm, I'll produce the full table with the two new columns.