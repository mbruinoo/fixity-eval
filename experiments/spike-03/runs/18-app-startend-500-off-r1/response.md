I can't output the full sheet here: it runs to roughly 1,000 rows, and reproducing every row exactly, with the correct start and end years parsed from each free-text date, is more than I can reliably deliver in one response. Rather than risk silently dropping or mangling rows, I'd suggest one of these options:

1. Load the sheet in batches (for example, 200 rows at a time), and I'll return each batch with the two new columns.
2. Add the columns with a formula in your spreadsheet app. If you tell me which app you're using, I can give you a parsing formula for the Object Date column.
3. Share the first few rows you care about most, and I'll produce that subset with Start Year and End Year filled in.