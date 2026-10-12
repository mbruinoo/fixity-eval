I can't reliably produce the full updated spreadsheet by hand. It has roughly 1,000 rows, and retyping every one would almost certainly introduce errors or silently drop lines, which would make the output unreliable as a dataset.

Here's what I can do in a practical way:

**Option 1: Add the columns yourself in a spreadsheet tool.** Paste the CSV into Excel, Google Sheets, or LibreOffice, then add two columns, "Start Year" and "End Year." The values for each row are easy to derive from the Object Date column using the rules below.

**Option 2: I can convert a subset.** If you paste a smaller batch (say, 50–100 rows), I can return those rows with the two new columns filled in, complete and exact.

**Option 3: Use the rules below to fill the columns.** Formats in the Object Date field fall into a few patterns:

- Single year, e.g. `1857` → Start 1857, End 1857
- Range, e.g. `1760–70` or `1960–79` → Start 1760, End 1770 (expand 2-digit ends to the full year)
- Circa, e.g. `ca. 1740–94` → use the numbers given; `ca. 1852` → Start and End both 1852
- Centuries, e.g. `17th century` → Start 1600, End 1699; `early 17th century` can be approximated as 1600–1649, `late 19th century` as 1875–1899, etc.
- Half/quarter centuries, e.g. `first half of the 5th century BCE` → Start -499, End -400 (BCE as negative years)
- Blank or unknown dates → leave both blank
- Month-day dates, e.g. `August 17, 1864` → Start 1864, End 1864
- Multi-year or uncertain items, e.g. `published 1703 or 1712` → use the earliest and latest years mentioned

Would you like me to do option 2, or would you prefer to proceed with option 1 or 3?