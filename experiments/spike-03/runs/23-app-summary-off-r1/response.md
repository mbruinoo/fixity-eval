I can't produce the complete updated CSV here: the sheet has roughly 300 rows, and writing out every row with the two new columns computed correctly would run past what I can reliably return in one reply, so I won't risk a truncated or silently altered file. Instead, here is the approach to get the result you need.

To add Start Year and End Year, use formulas in your spreadsheet app rather than rewriting the data. In the new columns (assuming Object Date is in column A, with data starting in row 2), you can extract the years with a formula that handles single years, ranges like "1850–1900" or "ca. 600–550 BCE", and text like "18th century". Because many entries use varied formats, the most reliable path is:

1. Insert two columns to the right of the existing data.
2. Enter a parsing formula in Start Year and End Year, then fill it down to the last row.
3. Review rows the formula returns as blank or error; those are the dates it couldn't convert, and you can count them with a COUNTBLANK or COUNTIF on the column.

If you tell me which convention you want for centuries (for example, "18th century" → 1700 and 1799) and how to treat BCE dates (negative numbers or a separate flag), I can write a precise formula for you to paste in. I can also process the sheet in smaller batches, such as 50 rows at a time, if you'd prefer me to return the CSV in pieces.