I can't reproduce the full sheet as requested, since it runs to roughly 1,000 rows and that's more than I can reliably output in one reply without errors. Instead, here's the approach that will work in your app:

Add two columns, "Start Year" and "End Year", and fill them by parsing the "Object Date" column. For example:
- "17th century" → Start Year 1600, End Year 1699
- "1901 or 1902" → Start Year 1901, End Year 1902
- "1760–70" → Start Year 1760, End Year 1770
- "ca. 1427–1400 B.C." → Start Year -1427, End Year -1400
- "1857" → Start Year 1857, End Year 1857
- Blank dates → leave both empty

If you paste the sheet in smaller batches (say 100 rows at a time), I can return each batch fully converted to CSV with the two new columns, and you can stitch them together in the app.