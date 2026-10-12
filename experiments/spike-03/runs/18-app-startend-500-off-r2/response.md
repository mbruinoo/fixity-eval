I can't output the full sheet here: it runs to roughly 1,000 rows, and reproducing every row exactly, with the new Start Year and End Year values filled in, would exceed what I can return in one reply. A truncated CSV would silently drop data when the app loads it back in, so I'd rather not send one.

Here's how to get the columns added without losing anything:

- **Use a formula in the app.** If your spreadsheet supports formulas, you can add the columns without retyping any data. Start Year and End Year would be derived from the "Object Date" column, but date strings like "ca. 1427–1400 B.C.", "first half of the 5th century BCE", and "18th–19th century" need careful parsing, so expect some cells to need manual correction.
- **Send me the rows in batches.** If you paste 100 to 150 rows at a time, I can return the complete updated CSV for each batch, and you can combine them.
- **Tell me the parsing rules you want.** For example: use the first year of a range as Start Year and the last as End Year; treat "ca." as the same year; convert BCE to negative numbers; leave blank when no date is given. With those rules settled, I can write out the values for each batch.

Which of these would you like to go with?