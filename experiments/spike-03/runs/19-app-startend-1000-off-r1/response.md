I can't reproduce the full sheet with the new columns from here: this CSV has over 1,000 rows, and I'd have to rewrite every one to add Start Year and End Year, which is more output than I can reliably produce in one reply without errors.

What I can do is give you a way to add the columns yourself quickly:

- **Start Year** and **End Year** can be derived from the "Object Date" column with a formula, for example in a new column F for Start Year: `=IFERROR(VALUE(REGEXREPLACE(B2,"^.*?(\d{3,4}).*$","$1")),"")`, and similar logic for End Year, taking the second four-digit number when a range is present.
- Alternatively, I can handle a smaller batch: paste 50–100 rows at a time and I'll return those rows with the two new columns filled in, and you can merge them back.

Tell me which approach you'd prefer.