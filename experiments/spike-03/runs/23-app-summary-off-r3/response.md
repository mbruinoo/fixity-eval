I can't produce the full updated sheet here: it has roughly 250 rows, and reproducing every row accurately as CSV in one reply isn't something I can do reliably, so I'd rather not hand you a truncated or altered file.

What I can offer instead:

- **Parsing rules I would apply:** For each Object Date, extract the earliest 4-digit year as Start Year and the latest as End Year. Single years repeat in both columns. Centuries map to the range (e.g., "18th century" → 1700 / 1799). BCE dates become negative years. Ranges like "ca. 1981–1550 B.C." become -1981 / -1550. Blank or non-date values ("unknown", "n.d.", blank cells) leave both columns empty.
- **Tool to do it reliably:** In most spreadsheet apps you can add the two columns with a formula, or I can write a short script (Python with pandas, or Excel/Sheets formulas) that applies these rules and outputs the new file. Those will be more trustworthy than me retyping hundreds of rows.
- **If you want a smaller batch:** Paste 20–30 rows at a time and I'll return those rows with the two new columns, and you can merge them in.

Let me know which route you'd like.