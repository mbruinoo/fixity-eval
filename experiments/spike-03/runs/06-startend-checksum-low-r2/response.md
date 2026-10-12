I can't give you accurate SHA-256 checksums. Computing SHA-256 by hand isn't reliable, and any hash I wrote out would be a guess that looks authoritative. A wrong checksum would defeat the purpose of verifying that nothing changed.

You can still confirm nothing changed without checksums:

- **Keep the original file untouched** and add the new columns to a copy.
- **Verify the original columns with a formula.** In Google Sheets or Excel, put the original sheet's values next to the copy and use `=EXACT(A2, Original!A2)` for each column. Any `FALSE` marks a changed cell. This is stricter than a checksum for spreadsheet use, because it compares the cells directly.
- **If you want actual hashes**, you'd need a tool that hashes text. Some spreadsheet add-ons and online SHA-256 calculators can do it, but for about 250 rows that's tedious without code.

For the Start Year and End Year columns, I'd use these rules:

- Ranges become start and end: "ca. 600–550 BCE" → Start -600, End -550
- Single dates use the same value for both: "1770" → 1770, 1770
- Centuries use the full span: "18th century" → 1701, 1800
- BCE dates are negative, with no year zero
- Unknown or blank dates stay blank, and I'd flag them for you
- Odd entries like "1712 or later" or "probably 11th century" get the stated range, with a note

Would you like me to produce the complete CSV with the original columns unchanged and the two year columns added? Given the length, I can do it in one pass or in batches of about 80 rows. You could then add the checksums with a tool, or skip them and rely on the `EXACT` check.