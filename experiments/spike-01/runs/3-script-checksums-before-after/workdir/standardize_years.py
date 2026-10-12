#!/usr/bin/env python3
"""Standardize the Object Date column of met_objects.csv.

Output format for the Object Date column:
  [qualifier ]YEAR[–YEAR][ BCE]     years as plain integers, en dash for ranges
  Centuries and decades are expanded to year ranges (18th century -> 1701–1800,
  1920s -> 1920–1929). Qualifiers such as "ca." are kept. BCE is written as a
  suffix; CE is dropped unless a range crosses from BCE into CE.
  Full dates are written ISO 8601 (1800-01-21).
  Blank, "unknown" and "n.d." are left as they are.

Every row is hashed (SHA-256 of its canonical CSV serialization) before and
after the transformation, and the Object Date field is hashed on its own.
Non-date columns are checked to be byte-identical after the transformation.

Usage: python3 -I standardize_years.py INPUT.csv OUTPUT.csv CHECKSUMS.csv
"""

import csv
import hashlib
import io
import re
import sys

DATE_COL = 0  # "Object Date"

ORDINALS = {"1st": 1, "2nd": 2, "3rd": 3}  # others handled by digits
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

# Qualifiers for sub-ranges of a century (thirds of the century, chronological).
QUAL_RE = r"(?:early|mid|late)(?:-(?:early|mid|late))?"

# Hand-written cases that are not worth a general rule.
SPECIAL = {
    "1811, (Bunka 8); 1817": "1811 (Bunka 8); 1817",
    "1950, printed 1967": "1950 (printed 1967)",
    "A.H. 139–48/ 757–66 CE": "757–766",  # Islamic date; CE equivalent used
}

PASSTHROUGH = {"", "unknown", "n.d.", "1712 or later"}

MONTH_DATE = re.compile(r"^(" + "|".join(MONTHS) + r")(?: (\d{1,2}),)? (\d{4})$")


def century_span(n, era):
    """Signed chronological (lo, hi) for the n-th century. BCE years are negative."""
    if era == "BCE":
        return (-(n * 100), -((n - 1) * 100 + 1))
    return ((n - 1) * 100 + 1, n * 100)


def qualified_span(lo, hi, qual):
    """Narrow a century span to early/mid/late thirds, chronologically."""
    if qual is None:
        return lo, hi
    parts = qual.split("-")
    third = {"early": (0, 32), "mid": (33, 65), "late": (66, 99)}
    start = lo + third[parts[0]][0]
    end = lo + third[parts[-1]][1]
    return start, end


CENTURY_TERM = re.compile(
    rf"^(?:({QUAL_RE})[\s-]+)?(\d+)(?:st|nd|rd|th)(?:\s+century)?(?:\s+(BCE|BC|CE))?$"
)
CENTURY_RANGE = re.compile(r"^(.+?)\s*–\s*(.+)$")
DECADE = re.compile(r"^(\d{4})s$")
NUM_RANGE = re.compile(
    r"^(\d{1,4})\s*–\s*(\d{1,4})(?:\s+(BCE|CE))?$"
)
SINGLE = re.compile(r"^(\d{1,4})(?:\s+(BCE|CE))?$")


def fmt(lo, hi):
    """Format a signed (lo, hi) year span."""
    if lo > 0 and hi > 0:
        return str(lo) if lo == hi else f"{lo}–{hi}"
    if lo < 0 and hi < 0:
        a, b = abs(lo), abs(hi)
        return f"{a} BCE" if a == b else f"{a}–{b} BCE"
    return f"{abs(lo)} BCE–{hi} CE"


def parse_century_term(text):
    """Return (lo, hi, era_given) for a century term, or None."""
    m = CENTURY_TERM.match(text)
    if not m:
        return None
    qual, n, era = m.group(1), int(m.group(2)), m.group(3)
    if era == "BC":
        era = "BCE"
    if era == "CE":
        era = None  # CE is the default
    lo, hi = century_span(n, era or "CE")
    lo, hi = qualified_span(lo, hi, qual)
    return lo, hi, era


def parse_core(s):
    """Return the standardized text for one date, or None if not understood."""
    if s in PASSTHROUGH:
        return s

    # Split off a leading qualifier ("ca.", "probably", "dated", "probably after").
    qual = ""
    m = re.match(r"^((?:ca\.|probably after|probably|possibly|dated)\s+)(.*)$", s)
    if m:
        qual, s = m.group(1), m.group(2)

    # Trailing parenthetical note, kept verbatim after the years.
    note = ""
    m = re.match(r"^(.*?)\s*(\(.*\))$", s)
    if m:
        s, note = m.group(1), " " + m.group(2)

    s = re.sub(r"\bB\.?C\.?(?!\w)", "BCE", s)
    s = re.sub(r"(?<=\d)-(?=\d)", "–", s)  # hyphen only between numbers
    s = re.sub(r"\s+", " ", s).strip()

    # Decades: 1960s -> 1960–1969
    m = DECADE.match(s)
    if m:
        y = int(m.group(1))
        return f"{qual}{y}–{y + 9}{note}"

    # Single year, optional BCE
    m = SINGLE.match(s)
    if m:
        y, era = int(m.group(1)), m.group(2)
        return f"{qual}{fmt(-y, -y) if era == 'BCE' else y}{note}"

    # Year range with explicit years
    m = NUM_RANGE.match(s)
    if m:
        a, b, era = int(m.group(1)), int(m.group(2)), m.group(3)
        if era == "BCE":
            lo, hi = -a, -b
        else:
            lo, hi = a, b
            # Short form: 1830–40 -> 1830–1840, 1880–92 -> 1880–1892
            if len(m.group(2)) < len(m.group(1)):
                hi = int(m.group(1)[: -len(m.group(2))] + m.group(2))
                if hi < lo:
                    hi += 100
        return f"{qual}{fmt(lo, hi)}{note}"

    # Century terms, or a range of two (e.g. "late 19th–early 20th century")
    rng = CENTURY_RANGE.match(s)
    if rng:
        lt = parse_century_term(rng.group(1))
        rt = parse_century_term(rng.group(2))
        if lt is not None and rt is not None and rt[2] and not lt[2]:
            # "3rd–1st century BCE": the left term takes the right term's era
            lt = parse_century_term(f"{rng.group(1)} {rt[2]}")
        if lt is None or rt is None:
            return None
        return f"{qual}{fmt(lt[0], rt[1])}{note}"

    t = parse_century_term(s)
    if t is None:
        return None
    return f"{qual}{fmt(t[0], t[1])}{note}"


def standardize(raw):
    """Return (new_text, rule) for one raw Object Date value."""
    s = re.sub(r"\s+", " ", raw).strip()
    m = MONTH_DATE.match(s)
    if m:
        month = MONTHS.index(m.group(1)) + 1
        if m.group(2):
            return f"{m.group(3)}-{month:02d}-{int(m.group(2)):02d}", "rule"
        return f"{m.group(3)}-{month:02d}", "rule"
    if s in SPECIAL:
        return SPECIAL[s], "special"
    if s in PASSTHROUGH:
        return s, "passthrough"
    out = parse_core(s)
    if out is None:
        return s, "UNPARSED"
    return out, "rule"


def row_hash(fields):
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerow(fields)
    return hashlib.sha256(buf.getvalue().encode("utf-8")).hexdigest()


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main(src, dst, checks):
    with open(src, "rb") as fh:
        raw_before = fh.read()
    before = list(csv.reader(io.StringIO(raw_before.decode("utf-8"), newline="")))
    header, body = before[0], before[1:]

    after = [header]
    log = []
    unparsed = []
    for idx, row in enumerate(body, start=1):
        new_date, rule = standardize(row[DATE_COL])
        new_row = [new_date] + row[1:]
        after.append(new_row)
        if rule == "UNPARSED":
            unparsed.append((idx, row[DATE_COL]))
        log.append({
            "row": idx,
            "object_number": row[3],
            "date_before": row[DATE_COL],
            "date_after": new_date,
            "rule": rule,
            "row_sha256_before": row_hash(row),
            "row_sha256_after": row_hash(new_row),
            "date_sha256_before": sha(row[DATE_COL]),
            "date_sha256_after": sha(new_date),
            "other_fields_unchanged": row[1:] == new_row[1:],
        })

    if unparsed:
        print("UNPARSED values, left unchanged:", unparsed, file=sys.stderr)
        sys.exit(1)
    if not all(r["other_fields_unchanged"] for r in log):
        print("ERROR: a non-date column changed", file=sys.stderr)
        sys.exit(1)

    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows(after)
    out_text = buf.getvalue()
    with open(dst, "w", encoding="utf-8", newline="") as fh:
        fh.write(out_text)

    with open(checks, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(log[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(log)

    changed = sum(1 for r in log if r["date_before"] != r["date_after"])
    rules = {}
    for r in log:
        rules[r["rule"]] = rules.get(r["rule"], 0) + 1
    print(f"file sha256 before: {hashlib.sha256(raw_before).hexdigest()}")
    print(f"file sha256 after:  {hashlib.sha256(out_text.encode('utf-8')).hexdigest()}")
    print(f"rows: {len(body)}  dates changed: {changed}  rules: {rules}")
    print(f"non-date columns identical on every row: "
          f"{all(r['other_fields_unchanged'] for r in log)}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    main(*sys.argv[1:])
