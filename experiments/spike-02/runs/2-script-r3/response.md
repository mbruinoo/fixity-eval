Here's a script that standardizes the `Object Date` column. It keeps the original value in a new `Original Object Date` column, so you can audit the changes.

```python
#!/usr/bin/env python3
"""Standardize the "Object Date" column of a CSV.

Usage:
    python3 standardize_dates.py input.csv output.csv

Standard forms:
    1896                    ca. 1896
    1830–1840               1975–1976 (short ranges are expanded)
    ca. 600–550 BCE         530 BCE
    18th century            3rd–1st century BCE     mid-5th century BCE
    early 20th century      probably after 1657

Values that can't be parsed are left unchanged and listed on stderr.
"""
import csv
import re
import sys

ORD = r"(\d{1,2})(?:st|nd|rd|th)"
BLANK = {"", "unknown", "n.d.", "nd", "undated"}
ERA_RE = re.compile(r"\s*\b(B\.?\s?C\.?(?:E\.?)?|C\.?E\.?|A\.?D\.?)\s*$", re.I)
QUAL_RE = re.compile(
    r"^(ca\.|c\.|circa|probably after|probably|after|dated|mid|early|late)\s+",
    re.I,
)
CENTURY_RE = re.compile(rf"{ORD}(?:–{ORD})?\s+century", re.I)
YEAR_RANGE_RE = re.compile(r"(\d{1,4})–(\d{1,4})")
YEAR_RE = re.compile(r"(?:[A-Za-z]+\s+)?(?:\d{1,2},\s*)?(\d{1,4})")


def ordinal(n):
    if 11 <= n % 100 <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def prefix_from(quals):
    return "".join("mid-" if q == "mid" else q + " " for q in quals)


def standardize(raw):
    """Return (standardized_value, parsed_ok)."""
    s = re.sub(r"\s+", " ", (raw or "").replace('"', "")).strip()
    if s.lower() in BLANK:
        return "", True

    # Normalize "mid-19th" to "mid 19th" and all dashes to an en dash.
    s = re.sub(r"\b(mid|early|late)\s*-\s*", r"\1 ", s, flags=re.I)
    s = re.sub(r"\s*[-–—]\s*", "–", s)

    # Pull off the era marker. BCE is kept; CE is implied and dropped.
    bce = False
    m = ERA_RE.search(s)
    if m:
        bce = m.group(1).upper().startswith("B")
        s = s[:m.start()].strip()

    # Pull off qualifiers such as "ca.", "probably after", "early".
    quals = []
    while (m := QUAL_RE.match(s)):
        q = m.group(1).lower()
        if q in ("ca.", "c.", "circa"):
            quals.append("ca.")
        elif q != "dated":
            quals.append(q)
        s = s[m.end():]

    prefix = prefix_from(quals)

    if (m := CENTURY_RE.fullmatch(s)):
        nums = [int(g) for g in m.groups() if g]
        body = "–".join(ordinal(n) for n in nums) + " century"
    elif (m := YEAR_RANGE_RE.fullmatch(s)):
        start, end = m.group(1), m.group(2)
        if len(end) < len(start):  # "1975–76" -> "1975–1976"
            end = start[: len(start) - len(end)] + end
        body = f"{start}–{end}"
    elif (m := YEAR_RE.fullmatch(s)):
        body = m.group(1)
    else:
        return raw.strip(), False

    return prefix + body + (" BCE" if bce else ""), True


def main(src, dst):
    with open(src, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ["Original Object Date"]
        rows = list(reader)

    problems = []
    for lineno, row in enumerate(rows, start=2):
        raw = row["Object Date"]
        new, ok = standardize(raw)
        if not ok:
            problems.append((lineno, raw))
        row["Original Object Date"] = raw
        row["Object Date"] = new

    with open(dst, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {dst}", file=sys.stderr)
    if problems:
        print(f"{len(problems)} value(s) need manual review (left unchanged):",
              file=sys.stderr)
        for lineno, raw in problems:
            print(f"  line {lineno}: {raw!r}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
```

Run it with:

```bash
python3 standardize_dates.py spreadsheet.csv spreadsheet_standardized.csv
```

I haven't executed the script against your data, so run it and check the stderr report. I expect it to flag values it doesn't handle, such as:

- Compound ranges like `late 19th–early 20th century` and `1st century BCE–3rd century CE`
- Non-date text like `1811, (Bunka 8); 1817`, `A.H. 139–48/ 757–66 CE`, and `early 20th century (original dated 1480)`
- Decades like `1960s` and approximations like `1712 or later`

Those rows are left as they were. If you want any of them handled differently, such as converting `1960s` to `1960–1969`, tell me which convention you prefer and I'll add the rule.