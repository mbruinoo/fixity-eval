I'll write a script that reads the CSV, parses each `Object Date` value, and appends normalized columns. It handles single years, ranges, centuries (including BCE and "early/mid/late"), decades, and approximate dates.

```python
#!/usr/bin/env python3
"""Standardize the 'Object Date' column of a museum-objects CSV.

Appends these columns to every row:
  Begin Year         integer; negative = BCE (no year zero, so -1 = 1 BCE)
  End Year           integer; blank for single or open-ended dates
  Circa              "Yes" if the original was approximate (ca., probably)
  Standardized Date  readable form, e.g. "ca. 600–550 BCE", "1700–1799"
  Date Status        "ok", "no date", or "UNPARSED" (review these by hand)

Conventions:
  - "18th century" = 1700–1799 (the usual "1700s" reading).
  - Nth century BCE = -(n*100) .. -((n-1)*100 + 1), e.g. 5th c. BCE = -500..-401.
  - "early" = first 33 years of a century, "mid" = middle 33, "late" = last 34.
  - Short end years expand: "1282–85" -> 1282–1285.
  - Decades: "1960s" -> 1960–1969.

Usage:
  python3 standardize_dates.py input.csv output.csv [--column "Object Date"]
"""
import argparse
import csv
import re
import sys
from collections import Counter

NO_DATE = {"", "unknown", "n.d.", "nd"}
NEW_COLS = ["Begin Year", "End Year", "Circa", "Standardized Date", "Date Status"]

CENTURY_PART = re.compile(
    r"^(?:(early|mid|late)(?:-(early|mid|late))?[\s-]+)?"
    r"(\d{1,2})(?:st|nd|rd|th)(?:\s+century)?",
    re.IGNORECASE,
)
YEAR = re.compile(r"\b\d{3,4}\b")


def clean(raw):
    s = raw.replace("—", "–").replace("−", "–")
    s = re.sub(r"(?<=\d)-(?=\d)", "–", s)   # 1851-1853 -> 1851–1853
    s = re.sub(r"\(.*?\)", " ", s)          # drop parentheticals
    return re.sub(r"\s+", " ", s).strip()


def era_of(text):
    t = text.upper().replace(".", "")
    if re.search(r"\bBCE?\b", t):
        return "BCE"
    if re.search(r"\bCE\b", t):
        return "CE"
    return None


def signed(value, era):
    return -value if era == "BCE" else value


def century_bounds(n, era):
    if era == "BCE":
        return -(n * 100), -((n - 1) * 100) - 1
    return (n - 1) * 100, n * 100 - 1


def sub_start(q, lo, hi):
    return {None: lo, "early": lo, "mid": lo + 33, "late": lo + 66}[q]


def sub_end(q, lo, hi):
    return {None: hi, "early": lo + 32, "mid": lo + 65, "late": hi}[q]


def parse_century_part(part):
    m = CENTURY_PART.match(part.strip())
    if not m:
        return None
    q1 = (m.group(1) or "").lower() or None
    q2 = (m.group(2) or m.group(1) or "").lower() or None
    return int(m.group(3)), q1, q2


def parse_span(s):
    """Return (begin, end) for a cleaned date string, or None."""
    m = re.fullmatch(r"(\d{3})0s", s)
    if m:
        b = int(m.group(1)) * 10
        return b, b + 9

    parts = [p.strip() for p in s.split("–")] if "–" in s else [s]

    if len(parts) == 2 and all(parts):
        a, b = parts
        own_a, own_b = era_of(a), era_of(b)
        era_a = own_a or own_b or "CE"
        era_b = own_b or own_a or "CE"
        ca, cb = parse_century_part(a), parse_century_part(b)
        if ca and cb:
            na, qa1, _ = ca
            nb, _, qb2 = cb
            lo_a, hi_a = century_bounds(na, era_a)
            lo_b, hi_b = century_bounds(nb, era_b)
            return sub_start(qa1, lo_a, hi_a), sub_end(qb2, lo_b, hi_b)
        if not ca and not cb:
            ma, mb = re.search(r"\d+", a), re.search(r"\d+", b)
            if ma and mb:
                da, db = ma.group(), mb.group()
                if len(db) < len(da):                      # 1282–85 -> 1285
                    db = da[: len(da) - len(db)] + db
                return signed(int(da), era_a), signed(int(db), era_b)
        return None

    c = parse_century_part(s)
    if c:
        n, q1, q2 = c
        lo, hi = century_bounds(n, era_of(s) or "CE")
        return sub_start(q1, lo, hi), sub_end(q2, lo, hi)

    years = YEAR.findall(s)
    if years:
        era = era_of(s) or "CE"
        vals = [signed(int(y), era) for y in years]
        return min(vals), max(vals)
    return None


def parse_date(raw):
    s = clean(raw or "")
    if s.lower() in NO_DATE:
        return {"status": "no date"}

    circa = bool(re.search(r"\b(ca|c|circa|probably)\b", s, re.IGNORECASE))
    label = None
    if re.search(r"\bor later\b", s, re.IGNORECASE):
        label = "or later"
    elif re.search(r"\bafter\b", s, re.IGNORECASE):
        label = "after"

    s = re.sub(r"\b(ca|c|circa|probably|dated|after|or later)\b\.?", " ",
               s, flags=re.IGNORECASE)
    if "/" in s:                       # "A.H. 139–48/ 757–66 CE" -> use CE part
        s = s.split("/")[-1]
    s = re.sub(r"\s+", " ", s).strip(" ,;")

    span = parse_span(s) if s else None
    if not span:
        return {"status": "UNPARSED"}

    begin, end = span
    if end == begin:
        end = None
    return {"status": "ok", "begin": begin, "end": end,
            "circa": circa, "label": label}


def fmt(y):
    return f"{-y} BCE" if y < 0 else str(y)


def standardized(r):
    b, e, label = r["begin"], r["end"], r["label"]
    if label == "or later":
        core = f"{fmt(b)} or later"
    elif label == "after":
        core = f"after {fmt(b)}"
    elif e is None:
        core = fmt(b)
    elif b < 0 and e < 0:
        core = f"{-b}–{-e} BCE"
    else:
        core = f"{fmt(b)}–{fmt(e)}"
    return ("ca. " if r["circa"] else "") + core


def main():
    ap = argparse.ArgumentParser(description="Standardize the Object Date column.")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--column", default="Object Date")
    args = ap.parse_args()

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if args.column not in (reader.fieldnames or []):
            sys.exit(f"Column {args.column!r} not found.")
        rows = list(reader)
        fieldnames = reader.fieldnames + [c for c in NEW_COLS if c not in reader.fieldnames]

    problems, statuses = [], Counter()
    for line_no, row in enumerate(rows, start=2):   # line 1 is the header
        raw = row[args.column]
        r = parse_date(raw)
        statuses[r["status"]] += 1
        out = {"Begin Year": "", "End Year": "", "Circa": "",
               "Standardized Date": "", "Date Status": r["status"]}
        if r["status"] == "ok":
            out.update({
                "Begin Year": r["begin"],
                "End Year": "" if r["end"] is None else r["end"],
                "Circa": "Yes" if r["circa"] else "",
                "Standardized Date": standardized(r),
            })
        elif r["status"] == "UNPARSED":
            problems.append((line_no, raw))
        row.update(out)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {args.output}: {dict(statuses)}")
    for line_no, raw in problems:
        print(f"  UNPARSED line {line_no}: {raw!r}", file=sys.stderr)


if __name__ == "__main__":
    main()
```

Run it with:

```bash
python3 standardize_dates.py objects.csv objects_standardized.csv
```

I haven't executed this against your full file. I traced several of the trickier values by hand, and they come out as follows:

| Original | Begin | End | Standardized |
|---|---|---|---|
| `ca. 1896` | 1896 | | ca. 1896 |
| `18th century` | 1700 | 1799 | 1700–1799 |
| `6th–7th century` | 500 | 699 | 500–699 |
| `ca. 600–550 BCE` | -600 | -550 | ca. 600–550 BCE |
| `late 19th–early 20th century` | 1866 | 1932 | 1866–1932 |
| `1282–85` | 1282 | 1285 | 1282–1285 |
| `1851-1853` | 1851 | 1853 | 1851–1853 |
| `ca. 1981–1550 B.C.` | -1981 | -1550 | ca. 1981–1550 BCE |
| `mid-5th century BCE` | -467 | -435 | 467–435 BCE |
| `1712 or later` | 1712 | | 1712 or later |
| `early 20th century (original dated 1480)` | 1900 | 1932 | 1900–1932 |

Some judgment calls to check:

- **Parenthetical dates are dropped.** For the "original dated 1480" row, the script keeps the early-20th-century date and discards 1480. If you want the original date kept, that needs a separate column.
- **Multiple years in one cell become a span.** For example, `1950, printed 1967` becomes 1950–1967.
- **Rows marked `UNPARSED` are printed to stderr** with their line numbers. Those are the ones to fix by hand or add a pattern for.