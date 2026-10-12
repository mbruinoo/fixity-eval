I can't produce the complete updated spreadsheet by hand here: it has roughly 1,000 rows, and I'd have to derive a start and end year for every one, which would make the output very long and error-prone. Doing that manually across the full file isn't something I can reliably deliver in one response.

Here's a workable approach that doesn't require running code:

**Option 1: Use the spreadsheet's built-in tools (no code)**
1. Paste the CSV into Excel or Google Sheets.
2. Add two new columns, "Start Year" and "End Year."
3. Fill them in by hand, or use the Text-to-Columns and Find & Replace features for the simple cases:
   - Single years like `1857` → both columns get `1857`.
   - Ranges like `1760–70` → Start `1760`, End `1770`.
   - Centuries like `17th century` → Start `1600`, End `1699`.
   - Blank or "n.d." dates → leave empty.

**Option 2: Send me the rows in batches**
If you paste 100–150 rows at a time, I can return each batch as completed CSV rows with the two new columns. Then you can concatenate them yourself. This keeps each response accurate and manageable.

**Conventions I'd use for the batches** (tell me if you prefer different ones):
- Single date → same value in both columns.
- "ca." and "probably" dates → use the stated years, ignoring the qualifier.
- BCE dates → negative numbers (e.g., `-450`), or write "BCE" if you prefer; I'd recommend negatives for sorting.
- Centuries → first and last year of that century (e.g., "5th century BCE" → -499 to -400).
- Undated items → blank cells.

Would you like to start with the first batch?