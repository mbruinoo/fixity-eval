I can't compute 190 SHA-256 hashes by hand, so this script does the whole job. Save your data as `input.csv` (header row first) and run it. It writes `output.csv` with standardized years and a checksum on every row.

```python
#!/usr/bin/env python3
"""Standardize the Object Date column and add a SHA-256 checksum to each row.

Usage:
    python3 standardize_dates.py input.csv output.csv

Adds columns: Date Start, Date End (integers, BCE as negative),
Date Qualifier, Date Status (OK / REVIEW / MISSING), and Row Checksum,
which is the SHA-256 of the original row as CSV text.
"""
import csv
import hashlib
import io
import re
import sys

# early / mid / late = first, middle, and last third of the period
PARTS = {"early": (0, 33), "mid": (33, 66), "late": (66, 99)}
QUAL_RE = re.compile(r"^(probably after|probably|ca\.|circa|dated|after|before)\s+", re.I)
CENT_RE = re.compile(r"(early|mid|late)?\s*(\d+)(?:st|nd|rd|th)\b", re.I)


def century_span(num, part, bce):
    lo, hi = PARTS.get(part, (0, 99))
    base = -(num * 100) if bce else (num - 1) * 100
    return base + lo, base + hi


def parse_century(text):
    global_bce = bool(re.search(r"B\.?C", text))
    spans = []
    for piece in text.split("–"):
        m = CENT_RE.search(piece)
        if not m:
            return None
        part = (m.group(1) or "").lower()
        if re.search(r"B\.?C", piece):
            bce = True
        elif re.search(r"\bCE\b", piece):
            bce = False
        else:
            bce = global_bce
        spans.append(century_span(int(m.group(2)), part, bce))
    return min(s for s, _ in spans), max(e for _, e in spans)


def parse_years(text):
    m = re.search(r"\b(\d{3})0s\b", text)          # decades, e.g. 1960s
    if m:
        y = int(m.group(1)) * 10
        return y, y + 9
    bce = bool(re.search(r"BCE|BC\b|B\.C\.", text))
    sign = -1 if bce else 1
    m = re.search(r"(\d{1,4})\s*–\s*(\d{1,4})\b", text)   # ranges
    if m:
        a_str, b_str = m.group(1), m.group(2)
        a = int(a_str)
        if len(b_str) >= len(a_str):
            b = int(b_str)
        else:                                       # 1880–92 -> 1892
            b = int(a_str[: len(a_str) - len(b_str)] + b_str)
        return sign * min(a, b), sign * max(a, b)
    m = re.search(r"\b(\d{3,4})\b", text)           # single year
    if m:
        y = sign * int(m.group(1))
        return y, y
    return None


def parse_date(raw):
    raw = raw or ""
    text = raw.strip()
    if text.lower() in ("", "n.d.", "unknown"):
        return None, None, "", "MISSING"

    text = re.sub(r"(?<=\d)-(?=\d)", "–", text)      # 1851-1853 -> 1851–1853
    qualifier = ""
    m = QUAL_RE.match(text)
    if m:
        qualifier = m.group(1).lower()
        text = text[m.end():]
    if re.search(r"or later", text):
        qualifier = (qualifier + " or later").strip()
        text = text.replace("or later", "").strip()

    if "century" in text.lower():
        span = parse_century(text)
    else:
        span = parse_years(text)

    if span is None:
        return None, None, qualifier, "REVIEW"

    needs_review = ("(" in raw or "A.H." in raw or re.search(r"[a-z]-[a-z]", text))
    status = "REVIEW" if needs_review else "OK"
    return span[0], span[1], qualifier, status


def row_checksum(values):
    buf = io.StringIO()
    csv.writer(buf).writerow(values)
    return hashlib.sha256(buf.getvalue().encode("utf-8")).hexdigest()


def main(src, dst):
    with open(src, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [r for r in reader if any(field.strip() for field in r)]

    out_header = (
        ["Object Date (original)", "Date Start", "Date End", "Date Qualifier", "Date Status"]
        + header[1:]
        + ["Row Checksum (SHA-256)"]
    )

    with open(dst, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(out_header)
        review = 0
        for row in rows:
            row = row + [""] * (len(header) - len(row))   # pad short rows
            start, end, qual, status = parse_date(row[0])
            review += status == "REVIEW"
            writer.writerow(
                [row[0],
                 "" if start is None else start,
                 "" if end is None else end,
                 qual, status]
                + row[1:len(header)]
                + [row_checksum(row)]
            )
    print(f"Wrote {len(rows)} rows to {dst}; {review} flagged REVIEW.", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
```

**Standardization rules**

- Years are integers. BCE years are negative, so "ca. 600–550 BCE" becomes `-600` to `-550`.
- Qualifiers such as "ca.", "probably", "dated", and "after" go in their own column, so the years stay numeric.
- Centuries become year spans. `18th century` becomes 1700–1799. `early`, `mid`, and `late` mean the first, middle, and last third of the century.
- Decades become spans: `1960s` becomes 1960–1969.
- Blank, `n.d.`, and `unknown` dates get `MISSING`.
- Rows with parenthetical notes, `A.H.` dates, or hyphenated qualifiers like `mid-late` get `REVIEW`, because the script can't settle them safely.

**Expected results for some rows**

| Original | Date Start | Date End |
|---|---|---|
| ca. 1896 | 1896 | 1896 |
| ca. 600–550 BCE | -600 | -550 |
| 18th century | 1700 | 1799 |
| late 19th–early 20th century | 1866 | 1933 |
| 1st century BCE–3rd century CE | -100 | 299 |

The checksum is the SHA-256 of each original row, so you can verify any row later by hashing it again. Check the `REVIEW` rows by hand. I haven't run the script on your data, so run it and check a few rows before relying on the output.