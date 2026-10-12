I can't realistically produce the full updated spreadsheet by hand. This file has roughly 1,000+ rows, and transcribing every row with two newly derived year columns would mean reproducing an enormous amount of text with a high chance of errors, dropped rows, or altered data. A partial or silently truncated CSV would be worse than none.

Here's what I can do that will actually work for you:

**Option 1: Spreadsheet formulas (no code)**
Keep your original file and add the columns directly in Excel, Google Sheets, or LibreOffice. The Object Date column is free text, so you'd extract years with a formula. For example, in cell F2 (Start Year) you could use:

```
=IFERROR(VALUE(REGEXTRACT(A2,"\d{4}")),"")
```

(In Excel, use a formula with `MID`/`SEARCH` or the newer `TEXTAFTER`/`REGEXEXTRACT` functions; Excel 365 supports `REGEXTRACT` as `=REGEXTRACT`-style via `LET` workarounds, so Google Sheets is the easiest for this.)

Then fill down. Ranges like "1760–70" or "ca. 2030–1640 B.C." and BCE dates will need a few extra cases, and you'll want to spot-check the results.

**Option 2: Paste it back in chunks**
If you send the data in batches of roughly 100 rows, I can return each batch as a complete CSV with Start Year and End Year filled in, and you can paste the batches together.

**Option 3: Rules I'd apply, so you can check my work**
- Single date ("1857") → Start = End = 1857
- Range ("1760–70", "late 19th–early 20th century") → Start and End from the endpoints; for centuries, use the century bounds (e.g., "18th century" → 1700 / 1799)
- "ca." / "probably" / "dated" → use the stated year(s), ignoring qualifiers
- BCE dates → negative numbers (e.g., 450 BCE → -450), or tell me if you'd prefer a different convention
- Blank or unknown → leave empty

Which approach would you like? I'd recommend Option 2 if you want the values filled in by me, or Option 1 if you'd rather keep the work in your own file.