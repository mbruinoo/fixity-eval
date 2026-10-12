I can't fill in every row reliably. Many entries have no date at all (blank "Object Date" cells), and others use ranges, approximations ("ca."), or non-year text ("unknown", "n.d.", "18th century"). Inventing Start and End Year values for those would put fabricated dates into an import database, which is worse than a rejected cell. Also, the full sheet is about 300 rows, and reproducing it all in one response risks truncation.

What I can do:

1. **Parse the dates that are explicit.** For example, "1770" gives Start 1770 and End 1770; "1830–40" gives Start 1830 and End 1840; "ca. 600–550 BCE" gives Start -600 and End -550 (using negative numbers for BCE).
2. **Use century bounds for century-only entries.** "18th century" gives Start 1700 and End 1799. "late 19th–early 20th century" gives Start 1875 and End 1925 (or another range you specify).
3. **Flag the rest.** Rows with no date, "unknown", or "n.d." can't be given a defensible year without a source. For these, you could (a) use a placeholder your database accepts, such as 0 or 9999, and mark them with a note column, or (b) look up the date on the Met's collection page using the Link Resource URL, which usually lists a dated object record.

Tell me which convention you want for BCE years, what to use for century ranges, and what placeholder your database accepts for unknown dates. With those decisions, I can return the full CSV with both new columns filled in for every row.