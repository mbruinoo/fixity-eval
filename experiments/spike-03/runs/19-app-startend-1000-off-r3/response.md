I can't reproduce the entire sheet here: it contains roughly 1,000 rows, and I would have to derive a start and end year for each one from free-text dates. Returning every row in full would produce a very long reply, and any error in the transcription would be silently passed back into the sheet.

Here is how I'd suggest proceeding:

1. **Add the columns in the app.** Insert two empty columns after "Object Date" named "Start Year" and "End Year."
2. **Use a formula for the common patterns.** Many entries follow formats like "1760–70," "ca. 1427–1400 B.C.," or "1000 BCE–400 CE." If you have a spreadsheet-style extraction tool, a regex on the Object Date column can handle most of them.
3. **Handle the rest by hand or in batches.** Entries like "17th century," "late 19th to early 20th century," "probably 4th century BCE," and blank dates need manual rules. Negative years for BCE dates should be stored as negative numbers so that sorting works.

If you'd like, paste a smaller batch of rows (say 20 to 50) and I'll return those with the two new columns filled in as CSV, so you can check the approach before applying it to the full set.