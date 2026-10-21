# Museum Inventory TSV Standardizer

This Python script cleans and standardizes a museum inventory spreadsheet with the columns **date**, **title**, **object number**, and **link**. It uses only the standard library.

## What it does

| Column | Standardization |
|---|---|
| **Date** | Converts many formats to a consistent style. Exact dates become ISO 8601 (`1999-03-04`, `1999-03`, `1999`). Circa dates become `ca. 1850`, ranges `1850–1860`, decades `1850s`, centuries `19th century`, and undated entries `n.d.` |
| **Title** | Normalizes Unicode, removes invisible characters, collapses whitespace, and strips stray wrapping quotes. Capitalization is left unchanged. |
| **Object number** | Uppercases, normalizes dashes, and removes stray spaces. Can optionally unify separators (`1999-12-3` → `1999.12.3`). Flags duplicates. |
| **Link** | Adds a missing `https://`, lowercases the domain, removes tracking parameters (`utm_*`, `fbclid`…), encodes spaces, and validates the result. |

It also maps header variants (e.g. `Accession No.`, `URL`, `Object Date`), handles malformed rows, optionally sorts and deduplicates, and writes a **change report** listing every modification and every problem it found.

## The script: `standardize_inventory.py`

```python
#!/usr/bin/env python3
"""
standardize_inventory.py

Standardize a museum inventory TSV with four columns:
    date, title, object number, link

Usage:
    python standardize_inventory.py inventory.tsv
    python standardize_inventory.py inventory.tsv -o clean.tsv -r report.tsv
    python standardize_inventory.py inventory.tsv --dayfirst --sort object --unify-separators
"""

import argparse
import csv
import datetime as dt
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import (urlsplit, urlunsplit, parse_qsl, urlencode, quote)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CANONICAL_HEADERS = ["date", "title", "object_number", "link"]

HEADER_ALIASES = {
    "date": "date", "objectdate": "date", "datecreated": "date",
    "creationdate": "date", "dated": "date", "year": "date",
    "title": "title", "objecttitle": "title", "name": "title",
    "objectname": "title", "worktitle": "title",
    "objectnumber": "object_number", "objectno": "object_number",
    "objnumber": "object_number", "objno": "object_number",
    "accessionnumber": "object_number", "accessionno": "object_number",
    "accession": "object_number", "inventorynumber": "object_number",
    "inventoryno": "object_number", "catalognumber": "object_number",
    "catalogueno": "object_number", "id": "object_number",
    "link": "link", "url": "link", "uri": "link", "weblink": "link",
    "permalink": "link", "webpage": "link", "website": "link",
}

UNDATED = {"n.d.", "n.d", "nd", "undated", "unknown", "no date",
           "date unknown", "?", "-", "--", "s.d.", "unk"}

MONTHS = {}
for i, name in enumerate(["january", "february", "march", "april", "may",
                          "june", "july", "august", "september", "october",
                          "november", "december"], start=1):
    MONTHS[name] = i
    MONTHS[name[:3]] = i
MONTHS["sept"] = 9

TRACKING_PARAMS = re.compile(r"^(utm_\w+|fbclid|gclid|mc_cid|mc_eid|_ga|ref_src)$", re.I)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_text(value):
    """Unicode-normalize, drop invisible chars, collapse whitespace."""
    if value is None:
        return ""
    s = unicodedata.normalize("NFC", str(value))
    s = s.replace("\u00a0", " ").replace("\u200b", "").replace("\ufeff", "")
    s = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", s)  # control characters
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def header_key(h):
    return re.sub(r"[^a-z0-9]", "", clean_text(h).lower())


def natural_key(s):
    """Sort '2' before '10' in object numbers like 1999.2 / 1999.10."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

# ---------------------------------------------------------------------------
# Column normalizers -- each returns (standardized_value, [issues])
# ---------------------------------------------------------------------------

def normalize_date(raw, dayfirst=False):
    s = clean_text(raw)
    issues = []
    if not s:
        return "", ["missing date"]
    if s.lower() in UNDATED:
        return "n.d.", []

    work = s.strip()
    circa = False
    uncertain = False

    m = re.match(r"^(c\.|ca\.?|c(?=\s*\d)|circa|about|approx\.?|approximately|~)\s*",
                 work, re.I)
    if m:
        circa = True
        work = work[m.end():].strip()
    if work.endswith("?"):
        uncertain = True
        work = work.rstrip("?").strip()
    work = work.strip("[]()").strip()
    work = re.sub(r"[\u2012\u2013\u2014\u2015]", "-", work)  # unify dashes

    result = None

    # Range: 1850-1860, 1850-60, 1850 to 1860, 1850/1860
    m = re.match(r"^(\d{3,4})\s*(?:-|to|/)\s*(\d{1,4})$", work, re.I)
    if m:
        start, end_str = m.group(1), m.group(2)
        if len(end_str) < len(start):  # 1850-60 -> 1860
            end_str = start[: len(start) - len(end_str)] + end_str
        if int(end_str) < int(start):
            issues.append("date range ends before it starts")
            return s, issues
        result = f"{int(start)}–{int(end_str)}"

    # Decade: 1850s, 1850's
    if result is None:
        m = re.match(r"^(\d{3}0)'?s$", work, re.I)
        if m:
            result = f"{m.group(1)}s"

    # Century: 19th c., 19th century, 19th cent.
    if result is None:
        m = re.match(r"^(\d{1,2})\s*(?:st|nd|rd|th)?\s*(?:c\.?|cent\.?|century)$",
                     work, re.I)
        if m:
            result = f"{ordinal(int(m.group(1)))} century"

    # ISO-ish: YYYY-MM-DD, YYYY/MM/DD, YYYY-MM, YYYY
    if result is None:
        m = re.match(r"^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})$", work)
        if m:
            result = _build_date(int(m.group(1)), int(m.group(2)), int(m.group(3)), issues)
    if result is None:
        m = re.match(r"^(\d{4})[-/](\d{1,2})$", work)
        if m and 1 <= int(m.group(2)) <= 12:
            result = f"{int(m.group(1)):04d}-{int(m.group(2)):02d}"
    if result is None and re.match(r"^\d{3,4}$", work):
        result = f"{int(work)}"

    # Numeric: MM/DD/YYYY or DD/MM/YYYY
    if result is None:
        m = re.match(r"^(\d{1,2})[-/.](\d{1,2})[-/.](\d{2,4})$", work)
        if m:
            a, b, y = int(m.group(1)), int(m.group(2)), m.group(3)
            if len(y) != 4:
                issues.append("two-digit year is ambiguous; left unchanged")
                return s, issues
            day, month = (a, b) if dayfirst else (b, a)
            if not dayfirst and a > 12 and b <= 12:   # clearly DD/MM
                day, month = a, b
                issues.append("interpreted as DD/MM/YYYY (first number > 12)")
            elif dayfirst and b > 12 and a <= 12:     # clearly MM/DD
                day, month = b, a
                issues.append("interpreted as MM/DD/YYYY (second number > 12)")
            elif a <= 12 and b <= 12 and a != b:
                issues.append("day/month order ambiguous; check value")
            result = _build_date(int(y), month, day, issues)

    # Month names: "March 4, 1999", "4 March 1999", "Mar. 1999", "March, 1999"
    if result is None:
        w = work.replace(",", " ").replace(".", " ")
        w = re.sub(r"(\d+)(st|nd|rd|th)\b", r"\1", w, flags=re.I)
        w = re.sub(r"\s+", " ", w).strip().lower()
        m = (re.match(r"^([a-z]+) (\d{1,2}) (\d{4})$", w) or None)
        if m and m.group(1) in MONTHS:
            result = _build_date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)), issues)
        if result is None:
            m = re.match(r"^(\d{1,2}) ([a-z]+) (\d{4})$", w)
            if m and m.group(2) in MONTHS:
                result = _build_date(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1)), issues)
        if result is None:
            m = re.match(r"^([a-z]+) (\d{4})$", w)
            if m and m.group(1) in MONTHS:
                result = f"{int(m.group(2)):04d}-{MONTHS[m.group(1)]:02d}"

    if result is None:
        issues.append("unrecognized date format; left unchanged")
        return s, issues

    if circa:
        result = f"ca. {result}"
    if uncertain:
        result = f"{result}?"
    return result, issues


def _build_date(year, month, day, issues):
    try:
        return dt.date(year, month, day).isoformat()
    except ValueError:
        issues.append(f"invalid calendar date ({year}-{month}-{day})")
        return None


def normalize_title(raw):
    s = clean_text(raw)
    issues = []
    if not s:
        return "", ["missing title"]
    # Strip quotes wrapping the entire title: "Title" / “Title” / 'Title'
    pairs = [('"', '"'), ("“", "”"), ("'", "'"), ("‘", "’")]
    for left, right in pairs:
        if len(s) > 1 and s.startswith(left) and s.endswith(right):
            inner = s[1:-1].strip()
            if left not in inner and right not in inner:
                s = inner
            break
    s = re.sub(r"\s+([,;:.!?])", r"\1", s)   # no space before punctuation
    if s.isupper() and len(s) > 3:
        issues.append("title is all caps; review capitalization")
    return s, issues


def normalize_object_number(raw, unify_separators=False):
    s = clean_text(raw)
    issues = []
    if not s:
        return "", ["missing object number"]
    s = re.sub(r"[\u2010-\u2015\u2212]", "-", s)       # unicode dashes -> '-'
    s = s.upper()
    s = re.sub(r"\s*([.\-/:])\s*", r"\1", s)            # spaces around separators
    if unify_separators:
        s = re.sub(r"(?<=[0-9A-Z])[\-/ ](?=\d)", ".", s)
        s = re.sub(r"\.{2,}", ".", s)
    s = s.strip(" .-/:")
    if not re.search(r"\d", s):
        issues.append("object number contains no digits")
    return s, issues


def normalize_link(raw, force_https=True):
    s = clean_text(raw).strip("<>\"' ")
    issues = []
    if not s:
        return "", ["missing link"]
    s = s.replace(" ", "%20")

    if not re.match(r"^[a-z][a-z0-9+.\-]*://", s, re.I):
        if re.match(r"^(www\.)?[a-z0-9\-]+(\.[a-z0-9\-]+)+(/|$|\?)", s, re.I):
            s = "https://" + s
        else:
            return s, ["link is not a valid URL; left unchanged"]

    parts = urlsplit(s)
    scheme = parts.scheme.lower()
    if scheme not in ("http", "https"):
        return s, [f"unsupported URL scheme '{scheme}'"]
    if force_https and scheme == "http":
        scheme = "https"

    netloc = parts.netloc.lower()
    netloc = re.sub(r":80$", "", netloc) if scheme == "http" else re.sub(r":443$", "", netloc)
    if "." not in netloc:
        issues.append("link domain looks invalid")

    query = urlencode([(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                       if not TRACKING_PARAMS.match(k)])
    path = quote(parts.path, safe="/%:@!$&'()*+,;=-._~")
    return urlunsplit((scheme, netloc, path, query, parts.fragment)), issues

# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def read_tsv(path):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, newline="", encoding=encoding) as f:
                return list(csv.reader(f, delimiter="\t")), encoding
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"Could not decode {path}")


def map_headers(header_row):
    """Return {canonical_name: column_index} or None if headers unrecognized."""
    mapping = {}
    for idx, h in enumerate(header_row):
        canon = HEADER_ALIASES.get(header_key(h))
        if canon and canon not in mapping:
            mapping[canon] = idx
    return mapping if len(mapping) >= 2 else None

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Standardize a museum inventory TSV.")
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path, help="output TSV (default: <input>_standardized.tsv)")
    ap.add_argument("-r", "--report", type=Path, help="change report TSV (default: <input>_report.tsv)")
    ap.add_argument("--no-header", action="store_true",
                    help="input has no header row; columns are date, title, object number, link")
    ap.add_argument("--dayfirst", action="store_true", help="treat 03/04/1999 as 3 April (DD/MM/YYYY)")
    ap.add_argument("--unify-separators", action="store_true",
                    help="convert '-', '/' and spaces between digits in object numbers to '.'")
    ap.add_argument("--keep-http", action="store_true", help="don't upgrade http:// links to https://")
    ap.add_argument("--drop-duplicates", action="store_true", help="remove exact duplicate rows")
    ap.add_argument("--sort", choices=["none", "object", "date", "title"], default="none")
    ap.add_argument("--header-style", choices=["snake", "title"], default="title",
                    help="output headers as 'object_number' or 'Object Number'")
    args = ap.parse_args()

    out_path = args.output or args.input.with_name(args.input.stem + "_standardized.tsv")
    rep_path = args.report or args.input.with_name(args.input.stem + "_report.tsv")

    rows, encoding = read_tsv(args.input)
    if not rows:
        sys.exit("Input file is empty.")

    report = []  # (row, column, original, standardized, note)

    if args.no_header:
        col_map = {name: i for i, name in enumerate(CANONICAL_HEADERS)}
        data_rows, first_line = rows, 1
    else:
        col_map = map_headers(rows[0])
        if col_map is None:
            print("Warning: headers not recognized; assuming column order "
                  "date, title, object number, link.", file=sys.stderr)
            col_map = {name: i for i, name in enumerate(CANONICAL_HEADERS)}
        for name in CANONICAL_HEADERS:
            if name not in col_map:
                print(f"Warning: no '{name}' column found; it will be left blank.", file=sys.stderr)
        data_rows, first_line = rows[1:], 2

    normalizers = {
        "date": lambda v: normalize_date(v, dayfirst=args.dayfirst),
        "title": normalize_title,
        "object_number": lambda v: normalize_object_number(v, args.unify_separators),
        "link": lambda v: normalize_link(v, force_https=not args.keep_http),
    }

    cleaned = []
    for offset, row in enumerate(data_rows):
        line_no = first_line + offset
        if not any(cell.strip() for cell in row):
            report.append((line_no, "", "", "", "blank row removed"))
            continue
        expected = max(col_map.values()) + 1
        if len(row) > expected and any(c.strip() for c in row[expected:]):
            report.append((line_no, "", "\t".join(row), "",
                           f"row has {len(row)} fields; extra fields ignored (check for stray tabs)"))

        record = {"_line": line_no}
        for name in CANONICAL_HEADERS:
            idx = col_map.get(name)
            original = row[idx] if idx is not None and idx < len(row) else ""
            value, issues = normalizers[name](original)
            record[name] = value
            if value != original:
                report.append((line_no, name, original, value, "changed"))
            for issue in issues:
                report.append((line_no, name, original, value, issue))
        cleaned.append(record)

    # Exact duplicates
    if args.drop_duplicates:
        seen, unique = set(), []
        for rec in cleaned:
            key = tuple(rec[c] for c in CANONICAL_HEADERS)
            if key in seen:
                report.append((rec["_line"], "", "", "", "exact duplicate row removed"))
            else:
                seen.add(key)
                unique.append(rec)
        cleaned = unique

    # Duplicate object numbers
    by_number = defaultdict(list)
    for rec in cleaned:
        if rec["object_number"]:
            by_number[rec["object_number"]].append(rec["_line"])
    for number, lines in by_number.items():
        if len(lines) > 1:
            for ln in lines:
                others = ", ".join(str(x) for x in lines if x != ln)
                report.append((ln, "object_number", number, number,
                               f"duplicate object number (also on line {others})"))

    # Sorting
    if args.sort == "object":
        cleaned.sort(key=lambda r: natural_key(r["object_number"]))
    elif args.sort == "title":
        cleaned.sort(key=lambda r: r["title"].lower())
    elif args.sort == "date":
        def date_key(r):
            m = re.search(r"\d{3,4}", r["date"])
            return (0, int(m.group()), r["date"]) if m else (1, 0, r["date"])
        cleaned.sort(key=date_key)

    # Write output
    if args.header_style == "title":
        out_headers = ["Date", "Title", "Object Number", "Link"]
    else:
        out_headers = CANONICAL_HEADERS
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(out_headers)
        for rec in cleaned:
            w.writerow([rec[c] for c in CANONICAL_HEADERS])

    report.sort(key=lambda r: (r[0], r[1]))
    with open(rep_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["line", "column", "original", "standardized", "note"])
        w.writerows(report)

    # Summary
    notes = Counter(r[4] if not r[4].startswith("duplicate object") else "duplicate object number"
                    for r in report)
    print(f"Read {len(data_rows)} data rows ({encoding}); wrote {len(cleaned)} rows to {out_path}")
    print(f"Report: {rep_path}")
    for note, count in notes.most_common():
        print(f"  {count:>5}  {note}")


if __name__ == "__main__":
    main()
```

## Example

**Input (`inventory.tsv`):**
```
Object Date	Title	Accession No.	URL
c. 1850	  "Portrait of a Woman"  	1999 - 12 - 3	www.museum.org/collection/1999.12.3?utm_source=x
March 4, 1999	Still Life with Apples	 1999.12.3 	http://museum.org/obj/abc
1850-60	Landscape   at Dusk	ab.2001.7	museum.org/obj/2001 7
1880's	Vase	2004.1	
19th c.	Untitled	2004.10	https://museum.org/obj/2004.10
undated	SKETCH FOR A MURAL	2005.3	not a link
```

**Command:**
```bash
python standardize_inventory.py inventory.tsv --sort object
```

**Output (`inventory_standardized.tsv`):**
```
Date	Title	Object Number	Link
ca. 1850	Portrait of a Woman	1999-12-3	https://www.museum.org/collection/1999.12.3
1999-03-04	Still Life with Apples	1999.12.3	https://museum.org/obj/abc
1880s	Vase	2004.1	
19th century	Untitled	2004.10	https://museum.org/obj/2004.10
n.d.	SKETCH FOR A MURAL	2005.3	not a link
1850–1860	Landscape at Dusk	AB.2001.7	https://museum.org/obj/2001%207
```

With `--unify-separators`, `1999-12-3` would become `1999.12.3`. The report would then flag it as a **duplicate object number** alongside line 3.

**Report (`inventory_report.tsv`):** each change is listed with its line number, the original and new values, and a note. Notes include `changed`, `missing link`, `title is all caps; review capitalization`, and `link is not a valid URL; left unchanged`. You can review it in any spreadsheet program.

## Customizing

- **Date style:** edit the `result = ...` lines in `normalize_date`. For example, output `circa 1850` instead of `ca. 1850`, or use `/` for ranges (EDTF style).
- **Object number conventions:** if your museum uses a fixed pattern (e.g. `YYYY.N.N`), add a regex check in `normalize_object_number` to flag non-conforming numbers.
- **Header names:** add your column names to `HEADER_ALIASES`.
- **Ambiguous dates** (`03/04/1999`) default to US order (MM/DD). Use `--dayfirst` for DD/MM. Either way, ambiguous dates are flagged in the report.

The script never deletes data it can't parse. Unrecognized values are left as-is and flagged in the report for manual review.
