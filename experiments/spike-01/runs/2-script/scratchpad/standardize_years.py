import csv
import re
import sys

path = sys.argv[1]

DASH = r"\s*[–—-]\s*"  # en dash, em dash, or hyphen, with optional spaces


def standardize(value):
    s = value.strip()
    if not s:
        return s

    # Era markers: "B.C.", "B.C", "BC" -> "BCE"; "A.D.", "AD" -> "CE"
    s = re.sub(r"\bB\.\s?C\.?(?![A-Za-z])", "BCE", s)
    s = re.sub(r"\bBC\b", "BCE", s)
    s = re.sub(r"\bA\.\s?D\.?(?![A-Za-z])", "CE", s)
    s = re.sub(r"\bAD\b", "CE", s)

    # Four-digit year ranges with a two-digit end: 1880–92 -> 1880–1892
    def expand_short_end(m):
        start, end = m.group(1), m.group(2)
        return f"{start}–{start[:2]}{end}"

    s = re.sub(rf"\b(\d{{4}}){DASH}(\d{{2}})\b(?!\d|\s*(?:th|st|nd|rd)\b)", expand_short_end, s)

    # Any remaining dash between two years becomes an en dash, no spaces
    s = re.sub(rf"\b(\d{{3,4}}){DASH}(\d{{3,4}})\b", r"\1–\2", s)

    # Collapse runs of whitespace
    s = re.sub(r"\s+", " ", s)
    return s


with open(path, newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))

changed = 0
for row in rows[1:]:
    new = standardize(row[0])
    if new != row[0]:
        changed += 1
        print(f"{row[0]!r:55} -> {new!r}")
    row[0] = new

with open(path, "w", newline="", encoding="utf-8") as f:
    csv.writer(f, lineterminator="\n").writerows(rows)

print(f"\n{changed} values changed")
