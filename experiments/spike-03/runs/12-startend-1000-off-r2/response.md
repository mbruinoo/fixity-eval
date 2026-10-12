I can't reliably produce this entire spreadsheet by hand. It has roughly 1,000 rows, and I'd need to parse each date string into a start and end year with no errors, which is not something I can do accurately at that scale without risking silent mistakes.

Here's what I can do instead:

**Option 1: Do it in a spreadsheet app (no code needed).** In Excel or Google Sheets, paste your data into column A, then add two columns and fill them using a helper such as:
- Google Sheets: Use Data > Split text to columns, or ask Google's built-in "Explore" feature to extract years from column A.
- Excel: Flash Fill (Ctrl+E) works well once you type the first few start years by hand. Type the start year for rows 1–3 in the Start Year column, press Ctrl+E, and it will infer the pattern. Do the same for End Year.

**Option 2: Work in batches with me.** Send me 50–100 rows at a time. I'll return the same rows as CSV with Start Year and End Year added, and I'll flag any rows I'm unsure about (blank dates, "probably," "ca.," or BCE ranges) so you can check them.

**Conventions I'd use in either approach:**
- Single year ("1857") → start = end = 1857
- Range ("1760–70") → start 1760, end 1770 (expanded to full century if needed, e.g., "1960–79" → 1960, 1979)
- "17th century" → 1600, 1699
- BCE dates → negative years (e.g., "5th century BCE" → -499 to -400), or tell me if you'd prefer a different convention
- Blank or unparseable → leave empty and flag

Would you like to start with the first batch?