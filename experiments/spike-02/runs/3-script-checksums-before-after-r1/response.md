I wrote the script below but haven't run it. Test it on a copy of your CSV first.

## `standardize_years.py`

```python
#!/usr/bin/env python3
"""
standardize_years.py INPUT.csv OUTPUT.csv MANIFEST.csv

Standardizes the 'Object Date' column and writes a SHA-256 checksum for every
row before and after the transformation.

OUTPUT.csv
  Object Date            "1896", "-600/-550", "1830/1840", or "" if unknown.
                         Single year -> "Y"; range -> "start/end".
                         BCE is negative; no year 0 (1 BCE = -1, 1 CE = 1).
  Date Start, Date End   signed integers, same convention
  Date Qualifier         circa | after | or later | probable (joined with "; ")
  Date Status            ok | review (original kept, needs a human) | unknown
  Object Date (original) source value, untouched

MANIFEST.csv
  row, Object Number, before_sha256, after_sha256,
  nondate_before_sha256, nondate_after_sha256, nondate_unchanged
  before = full source row; after = full output row;
  nondate_* = every column except Object Date (must match).
"""
import csv
import hashlib
import json
import re
import sys

DATE = "Object Date"
MONTHS = r"(January|February|March|April|May|June|July|August|September|October|November|December)"
FILLER = re.compile(r"\b(probably|ca|circa|after|dated|original|or later)\b\.?", re.I)
ERA = re.compile(r"\b(?:B\.C\.E\.|B\.C\.E|B\.C\.|BCE|BC|C\.E\.|CE|A\.D\.|AD)(?=\W|$)")
REVIEW = re.compile(r"A\.H\.|/|\(|printed|,")
THIRDS = {"early": (0, 34), "mid": (34, 67), "late": (67, 100)}  # offsets within a century


def side_interval(text, bce):
    """Return (lo, hi) for one side of a date, e.g. '1896', '1960s', '19th', 'late 19th'."""
    t = text.strip().lower()
    part = None
    m = re.match(r"(early|mid|late)\s*(.*)$", t)
    if m:
        part, t = m.group(1), m.group(2).strip()

    m = re.fullmatch(r"(\d{1,2})(?:st|nd|rd|th)(?: century)?", t)
    if m:
        n = int(m.group(1))
        first, last = (n - 1) * 100 + 1, n * 100
        lo, hi = (-last, -first) if bce else (first, last)
        if part:
            a, b = THIRDS[part]
            lo, hi = lo + a, lo + b - 1
        return lo, hi

    if part is None:
        m = re.fullmatch(r"(\d{3})0s", t)
        if m:
            y = int(m.group(1)) * 10
            return (-(y + 9), -y) if bce else (y, y + 9)
        if re.fullmatch(r"\d{4}", t):
            y = int(t)
            return (-y, -y) if bce else (y, y)

    raise ValueError(text)


def parse_date(raw):
    s = (raw or "").strip()
    low = s.lower()
    if low in ("", "n.d.", "nd", "unknown"):
        return dict(date="", start="", end="", qual="", status="unknown")

    qual = []
    if re.search(r"\bprobably\b", low):
        qual.append("probable")
    if re.search(r"\bca\b|\bcirca\b", low):
        qual.append("circa")
    if re.search(r"\bafter\b", low):
        qual.append("after")
    if re.search(r"\bor later\b", low):
        qual.append("or later")
    qual_s = "; ".join(qual)

    t = FILLER.sub(" ", s)
    t = re.sub(MONTHS + r"\s*(\d{1,2},)?", " ", t)      # "January 21, 1800" -> "1800"
    t = re.sub(r"\b(early|mid|late)-", r"\1 ", t, flags=re.I)  # "mid-5th" -> "mid 5th"
    t = re.sub(r"\s+", " ", t).strip()

    if REVIEW.search(t):
        return dict(date=s, start="", end="", qual=qual_s, status="review")

    bce_whole = bool(re.search(r"\bB\.?C", t))
    sides = re.split(r"\s*[–-]\s*", t)
    if len(sides) > 2:
        return dict(date=s, start="", end="", qual=qual_s, status="review")

    ivs, first_clean = [], None
    try:
        for i, p in enumerate(sides):
            bce = bool(re.search(r"\bB\.?C", p)) if ERA.search(p) else bce_whole
            clean = ERA.sub("", p).strip()
            if i == 0:
                first_clean = clean
            elif re.fullmatch(r"\d{4}", first_clean or "") and re.fullmatch(r"\d{1,3}", clean):
                clean = first_clean[: 4 - len(clean)] + clean   # "1830–40" -> "1840"
            ivs.append(side_interval(clean, bce))
    except ValueError:
        return dict(date=s, start="", end="", qual=qual_s, status="review")

    start = min(lo for lo, _ in ivs)
    end = max(hi for _, hi in ivs)
    date = str(start) if start == end else f"{start}/{end}"
    return dict(date=date, start=start, end=end, qual=qual_s, status="ok")


def digest(values):
    return hashlib.sha256(json.dumps(values, ensure_ascii=False).encode("utf-8")).hexdigest()


def file_digest(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main(inp, outp, manp):
    with open(inp, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    bad = [i for i, r in enumerate(body, 2) if len(r) != len(header)]
    if bad:
        sys.exit(f"column count mismatch at record(s) {bad[:10]}")

    src = [dict(zip(header, r)) for r in body]
    d = header.index(DATE)
    out_fields = (header[:d] + [DATE, "Date Start", "Date End", "Date Qualifier", "Date Status"]
                  + header[d + 1:] + ["Object Date (original)"])
    other = [c for c in header if c != DATE]
    counts = {}

    with open(outp, "w", newline="", encoding="utf-8") as fo, \
         open(manp, "w", newline="", encoding="utf-8") as fm:
        wo, wm = csv.writer(fo), csv.writer(fm)
        wo.writerow(out_fields)
        wm.writerow(["row", "Object Number", "before_sha256", "after_sha256",
                     "nondate_before_sha256", "nondate_after_sha256", "nondate_unchanged"])

        for n, r in enumerate(src, 1):
            p = parse_date(r[DATE])
            new = dict(r)
            new.update({
                DATE: p["date"], "Date Start": p["start"], "Date End": p["end"],
                "Date Qualifier": p["qual"], "Date Status": p["status"],
                "Object Date (original)": r[DATE],
            })
            before = digest([r[c] for c in header])
            after = digest([new[c] for c in out_fields])
            nd_before = digest([r[c] for c in other])
            nd_after = digest([new[c] for c in other])
            wo.writerow([new[c] for c in out_fields])
            wm.writerow([n, r.get("Object Number", ""), before, after,
                         nd_before, nd_after, nd_before == nd_after])
            counts[p["status"]] = counts.get(p["status"], 0) + 1

    print("input  sha256:", file_digest(inp))
    print("output sha256:", file_digest(outp))
    print("manifest:", manp)
    print("status counts:", counts)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
```

## Usage

```bash
python3 standardize_years.py objects.csv objects_standardized.csv manifest.csv
```

Keep the script in the project directory, not `/tmp`.

## Conventions I chose

- **BCE** is negative with no year 0: 600 BCE is `-600`, 1 CE is `1`.
- **Centuries** expand to their full span: "18th century" → `1701/1800`, "1st century BC" → `-100/-1`.
- **Thirds:** "early/mid/late" split a century into 34/33/33-year segments. "late 19th" → 1868–1900 and "early 20th" → 1901–1934.
- **Abbreviated ranges** complete from the start year: "1830–40" → 1830/1840.
- **Reversed ranges** are ordered chronologically: "3rd–1st century BCE" → `-300/-100`.
- **Qualifiers** (`ca.`, `probably`, `after`, `or later`) go in `Date Qualifier` and don't change the years.
- **Review rows** are the ones I can't parse safely: `A.H.` dates, slashes, parenthesized notes, and "1950, printed 1967". They keep their original `Object Date` and get `Date Status = review`. I didn't want to guess at them.

Expected results for some of your rows, worked out by hand:

| Original | Object Date | Start | End | Qualifier | Status |
|---|---|---|---|---|---|
| ca. 1896 | 1896 | 1896 | 1896 | circa | ok |
| 18th century | 1701/1800 | 1701 | 1800 | | ok |
| ca. 600–550 BCE | -600/-550 | -600 | -550 | circa | ok |
| 1830–40 | 1830/1840 | 1830 | 1840 | | ok |
| late 19th–early 20th century | 1868/1934 | 1868 | 1934 | | ok |
| mid-5th century BCE | -466/-434 | -466 | -434 | | ok |
| probably after 1657 | 1657 | 1657 | 1657 | probable; after | ok |
| 1712 or later | 1712 | 1712 | 1712 | or later | ok |
| 1950, printed 1967 | 1950, printed 1967 | | | | review |
| A.H. 139–48/ 757–66 CE | (original) | | | | review |
| (blank) | | | | | unknown |

## Checksums

- **`before_sha256`** hashes the full source row as a JSON array.
- **`after_sha256`** hashes the full output row.
- **`nondate_*`** hashes every column except `Object Date`, and `nondate_unchanged` confirms those columns survived intact. Because the script copies those values directly, this check should always pass. It guards against writer bugs, not parser bugs.

The script also prints SHA-256 digests of the whole input and output files.

## Before you rely on it

Run it and spot-check the review rows and the ~10 examples above. I'd expect a few of the 170+ rows to need manual fixes, mainly the review rows and the ambiguous ranges.