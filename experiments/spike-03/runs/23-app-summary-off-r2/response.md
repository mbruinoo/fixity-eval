I can't produce the complete updated CSV here: the sheet has roughly 200 rows, and reproducing every row exactly with the two new columns added is beyond what I can reliably output in one reply, so I won't attempt a partial or truncated version that the app might load incorrectly.

What I can do is describe the approach so you can apply it in your app:

- **Start Year**: parse the first four-digit year (or century/range) from the Object Date. For example, "ca. 1896" gives 1896, "late 19th–early 20th century" gives 1800 (start of the 19th century), "6th–7th century" gives 500 (or the CE/BCE equivalent you choose).
- **End Year**: for ranges, use the second year or the end of the period; for single years and "ca." dates, use the same year as Start Year; for blank dates, leave both empty.
- **Unconvertible dates**: entries such as blank dates, "unknown," and "n.d." can't be converted and should be left blank rather than guessed.

If you'd like, I can write a short formula or script (for example, a spreadsheet formula or a Python function) that performs this conversion across your full sheet, which would be more reliable than having me retype the whole file.