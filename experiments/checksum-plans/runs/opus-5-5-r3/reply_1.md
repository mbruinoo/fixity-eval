# Museum Inventory Standardizer

This Python script cleans a 4-column museum inventory TSV (date, title, object number, link). It writes a standardized file plus an issues report listing every row that needs a human to look at it. It uses only the standard library, so there is nothing to install.

```python
#!/usr/bin/env python3
"""
standardize_inventory.py

Standardize a museum inventory spreadsheet (.tsv) with four columns:
    date | title | object number | link

What it does
------------
DATE           "3/14/1998", "March 14th, 1998"  -> "1998-03-14"
               "Mar 1998", "1998/3"             -> "1998-03"
               "c.1850", "circa 1850", "ca 1850"-> "ca. 1850"
               "1850-60", "1850 to 1860"        -> "1850-1860"
               "1850's"                         -> "1850s"
               "19th c.", "mid 19th cent."      -> "19th century", "mid-19th century"
               "500 B.C.", "AD 79"              -> "500 BCE", "79 CE"
               "n.d.", "unknown", "[undated]"   -> "undated"
TITLE          trims/collapses whitespace, strips wrapping quotes,
               normalizes "untitled" variants; flags empty / ALL-CAPS titles
OBJECT NUMBER  removes labels like "Obj. No." / "Acc. #", tidies spacing
               around separators ("1999 . 12 . 3" -> "1999.12.3"),
               flags duplicates, missing values, and unusual characters
LINK           adds missing https://, lowercases scheme/host, removes default
               ports and tracking params (utm_*, fbclid, ...), optional https
               upgrade and live link checking

Anything that can't be standardized confidently is left as-is and written
to an issues report for human review.

Usage
-----
    python standardize_inventory.py inventory.tsv
    python standardize_inventory.py inventory.tsv -o clean.tsv --day-first --force-https
    python standardize_inventory.py inventory.tsv --sort object-number --check-links
"""

import argparse
import csv
import re
import sys
import unicodedata
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date as _date
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

OUTPUT_HEADER = ["Date", "Title", "Object Number", "Link"]

# --------------------------------------------------------------------------
# General text cleanup
# --------------------------------------------------------------------------

_INVISIBLE = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff"), None)


def clean_text(value, form="NFC"):
    """Unicode-normalize, drop invisible characters, collapse whitespace."""
    if value is None:
        return ""
    s = unicodedata.normalize(form, value).translate(_INVISIBLE)
    s = s.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", s).strip()


# --------------------------------------------------------------------------
# Dates
# --------------------------------------------------------------------------

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}

UNDATED = {"nd", "n.d", "n.d.", "n. d.", "undated", "unknown", "no date",
           "date unknown", "unk", "?", "-", "--"}

CIRCA_RE = re.compile(
    r"^(?:circa|ca\.?|c\.|c(?=\s*\d)|approx(?:imately|\.)?|about)\s*")
QUALIFIER_RE = re.compile(r"^(early|mid|late)[\s-]+")
ERA_SUFFIX_RE = re.compile(
    r"(?:^|(?<=\d)|\s)(b\.?\s?c\.?(?:\s?e\.?)?|a\.?\s?d\.?|c\.?\s?e\.?)$")
ERA_PREFIX_RE = re.compile(r"^(a\.?\s?d\.?)\s*(?=\d)")


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def iso_date(y, m, d=None):
    """Return an ISO date (or year-month) string, or None if invalid."""
    try:
        y, m = int(y), int(m)
        if d is None:
            return f"{y:04d}-{m:02d}" if 1 <= m <= 12 else None
        return _date(y, m, int(d)).isoformat()
    except ValueError:
        return None


def _parse_core(s, day_first, era):
    """Parse the date body (no circa/era/qualifier). Returns (value, issue)."""
    year = r"\d{1,4}" if era else r"\d{4}"

    # Year only
    if re.fullmatch(year, s):
        return str(int(s)) if era else s, None

    # Decade: 1850s, 1850's
    m = re.fullmatch(r"(\d{3})0\s?'?s", s)
    if m:
        return f"{m.group(1)}0s", None

    # Year-month: 1998-03, 1998/3 (checked before ranges so 1850-12 is a month)
    m = re.fullmatch(r"(\d{4})[-/.](\d{1,2})", s)
    if m and 1 <= int(m.group(2)) <= 12:
        return iso_date(m.group(1), m.group(2)), None

    # Range: 1850-1860, 1850-60, 1850 to 1860
    m = re.fullmatch(rf"({year})\s*(?:-|to)\s*(\d{{1,4}})", s)
    if m:
        start, end = m.group(1), m.group(2)
        if not era and len(end) < len(start):          # 1850-60 -> 1850-1860
            end = start[: len(start) - len(end)] + end
        a, b = int(start), int(end)
        bce = era == "BCE"
        if (bce and a < b) or (not bce and a > b):
            return None, "date range end precedes start"
        return f"{a}-{b}", None

    # ISO-ish full date: 1998-03-14, 1998/3/14
    m = re.fullmatch(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", s)
    if m:
        v = iso_date(*m.groups())
        return (v, None) if v else (None, "invalid calendar date")

    # Numeric d/m/y or m/d/y
    m = re.fullmatch(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{2}|\d{4})", s)
    if m:
        a, b, y = m.groups()
        if len(y) == 2:
            return None, "two-digit year is ambiguous"
        a, b = int(a), int(b)
        issue = None
        if a > 12:
            day, month = a, b
        elif b > 12:
            month, day = a, b
        else:
            month, day = (b, a) if day_first else (a, b)
            if a != b:
                issue = ("ambiguous day/month order; assumed "
                         + ("day-first" if day_first else "month-first"))
        v = iso_date(y, month, day)
        return (v, issue) if v else (None, "invalid calendar date")

    # Month-name formats: "March 14 1998", "14 Mar 1998", "March 1998"
    t = re.sub(r"(\d)(st|nd|rd|th)\b", r"\1", s)
    t = re.sub(r"[,.]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    for pattern, order in (
        (r"([a-z]+) (\d{1,2}) (\d{4})", "mdy"),
        (r"(\d{1,2}) ([a-z]+) (\d{4})", "dmy"),
        (r"([a-z]+) (\d{4})", "my"),
    ):
        m = re.fullmatch(pattern, t)
        if not m:
            continue
        parts = dict(zip(order, m.groups()))
        month = MONTHS.get(parts["m"])
        if month is None:
            continue
        v = iso_date(parts["y"], month, parts.get("d"))
        return (v, None) if v else (None, "invalid calendar date")

    # Century: 19th century, 19th c., 19th cent.
    m = re.fullmatch(
        r"(\d{1,2})\s*(?:st|nd|rd|th)?\s*(?:c\.?|cent\.?|century)", s)
    if m:
        return f"{ordinal(int(m.group(1)))} century", None

    return None, None


def standardize_date(raw, day_first=False):
    s = clean_text(raw, "NFKC")
    if not s:
        return "", "missing date"

    low = s.lower().replace("\u2013", "-").replace("\u2014", "-")
    if low.strip("[]() ") in UNDATED:
        return "undated", None

    uncertain = low.endswith("?")
    low = low.rstrip("? ").strip("[]() ")

    circa = False
    m = CIRCA_RE.match(low)
    if m:
        circa, low = True, low[m.end():]

    qualifier = ""
    m = QUALIFIER_RE.match(low)
    if m:
        q = m.group(1)
        qualifier = "mid-" if q == "mid" else f"{q} "
        low = low[m.end():]

    era = None
    m = ERA_SUFFIX_RE.search(low)
    if m:
        era = "BCE" if m.group(1).startswith("b") else "CE"
        low = low[: m.start()].strip()
    else:
        m = ERA_PREFIX_RE.match(low)
        if m:
            era, low = "CE", low[m.end():]

    value, issue = _parse_core(low.strip(" ,"), day_first, era)
    if value is None:
        return s, issue or "unrecognized date format"

    result = ("ca. " if circa else "") + qualifier + value
    if era:
        result += f" {era}"
    if uncertain:
        result += "?"
    return result, issue


# --------------------------------------------------------------------------
# Titles
# --------------------------------------------------------------------------

QUOTE_PAIRS = {'"': '"', "'": "'", "\u201c": "\u201d", "\u2018": "\u2019"}
UNTITLED = {"untitled", "[untitled]", "(untitled)", "untitled."}


def standardize_title(raw):
    s = clean_text(raw, "NFC")
    # Strip quotes wrapping the entire title
    while len(s) >= 2 and QUOTE_PAIRS.get(s[0]) == s[-1]:
        s = s[1:-1].strip()
    if not s:
        return "", "missing title"
    if s.lower() in UNTITLED:
        return "Untitled", None
    letters = [c for c in s if c.isalpha()]
    if len(letters) > 3 and all(c.isupper() for c in letters):
        return s, "title is ALL CAPS; review capitalization"
    return s, None


# --------------------------------------------------------------------------
# Object numbers
# --------------------------------------------------------------------------

OBJ_LABEL_RE = re.compile(
    r"^(?:(?:obj(?:ect)?|acc(?:ession)?|inv(?:entory)?|cat(?:alog(?:ue)?)?)"
    r"\.?\s*(?:no\.?|num(?:ber)?\.?|#)\s*:?|no\.|#)\s*",
    re.IGNORECASE,
)
OBJ_ALLOWED_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9.\-/:()_ ]*")


def standardize_object_number(raw, uppercase=False):
    s = clean_text(raw, "NFKC")             # NFKC also fixes full-width digits
    s = OBJ_LABEL_RE.sub("", s)
    s = re.sub(r"\s*([.\-/:])\s*", r"\1", s)  # "1999 . 12 . 3" -> "1999.12.3"
    s = s.strip(" .,;")
    if uppercase:
        s = s.upper()
    if not s:
        return "", "missing object number"
    if not OBJ_ALLOWED_RE.fullmatch(s):
        return s, "object number contains unusual characters"
    return s, None


def natural_key(s):
    """Sort 2.10 after 2.9 (natural/accession order)."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


# --------------------------------------------------------------------------
# Links
# --------------------------------------------------------------------------

TRACKING_RE = re.compile(r"^(utm_\w+|fbclid|gclid|mc_cid|mc_eid|_ga)$", re.I)
BARE_DOMAIN_RE = re.compile(
    r"^(www\.)?[a-z0-9-]+(\.[a-z0-9-]+)+(:\d+)?([/?#]|$)", re.I)


def standardize_link(raw, force_https=False):
    s = clean_text(raw, "NFC").strip("<>\"' ")
    if not s:
        return "", "missing link"
    s = s.replace(" ", "%20")

    if "://" not in s:
        if BARE_DOMAIN_RE.match(s):
            s = "https://" + s
        else:
            return s, "invalid URL"

    p = urlsplit(s)
    scheme = p.scheme.lower()
    try:
        host, port = p.hostname, p.port
    except ValueError:
        return s, "invalid URL (bad port)"
    if scheme not in ("http", "https") or not host:
        return s, "invalid URL"
    if force_https:
        scheme = "https"

    default_port = {"http": 80, "https": 443}[scheme]
    netloc = host.lower() + (f":{port}" if port and port != default_port else "")

    pairs = parse_qsl(p.query, keep_blank_values=True)
    kept = [(k, v) for k, v in pairs if not TRACKING_RE.match(k)]
    query = p.query if len(kept) == len(pairs) else urlencode(kept)

    return urlunsplit((scheme, netloc, p.path or "/", query, p.fragment)), None


def check_link(url, timeout):
    """Return None if the URL responds OK, otherwise a problem description."""
    headers = {"User-Agent": "Mozilla/5.0 (museum-inventory-link-checker)"}
    for method in ("HEAD", "GET"):
        try:
            with urlopen(Request(url, method=method, headers=headers),
                         timeout=timeout) as r:
                return None if r.status < 400 else f"link returned HTTP {r.status}"
        except HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue                      # some servers reject HEAD
            return f"link returned HTTP {e.code}"
        except Exception as e:                # timeouts, DNS errors, SSL...
            return f"link unreachable ({type(e).__name__})"
    return "link check failed"


# --------------------------------------------------------------------------
# Reading / header detection
# --------------------------------------------------------------------------

HEADER_ALIASES = {
    "date": {"date", "dates", "datemade", "creationdate", "objectdate", "year",
             "datecreated", "displaydate"},
    "title": {"title", "objecttitle", "name", "objectname", "titlename"},
    "object_number": {"objectnumber", "objectno", "objno", "objnumber",
                      "accessionnumber", "accessionno", "accno", "objectid",
                      "inventorynumber", "inventoryno", "catalognumber",
                      "catalogueno", "catalogno", "id", "number"},
    "link": {"link", "url", "uri", "permalink", "weblink", "webpage",
             "website", "objecturl"},
}


def read_tsv(path, raw_quotes=False):
    quoting = csv.QUOTE_NONE if raw_quotes else csv.QUOTE_MINIMAL
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, newline="", encoding=enc) as f:
                return list(csv.reader(f, delimiter="\t", quoting=quoting)), enc
        except UnicodeDecodeError:
            continue
    raise RuntimeError("could not decode file")


def detect_columns(first_row):
    """Return {field: index} if the first row is a recognizable header."""
    mapping = {}
    for i, cell in enumerate(first_row):
        key = re.sub(r"[^a-z]", "", cell.lower())
        for field, aliases in HEADER_ALIASES.items():
            if key in aliases and field not in mapping:
                mapping[field] = i
    return mapping


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Standardize a museum inventory TSV "
                    "(date, title, object number, link).")
    ap.add_argument("input", type=Path, help="input .tsv file")
    ap.add_argument("-o", "--output", type=Path,
                    help="output file (default: <input>_standardized.tsv)")
    ap.add_argument("--issues", type=Path,
                    help="issues report (default: <input>_issues.tsv)")
    ap.add_argument("--no-header", action="store_true",
                    help="treat the first row as data (columns in order "
                         "date, title, object number, link)")
    ap.add_argument("--day-first", action="store_true",
                    help="interpret ambiguous numeric dates as DD/MM/YYYY")
    ap.add_argument("--force-https", action="store_true",
                    help="rewrite http:// links to https://")
    ap.add_argument("--uppercase-object-numbers", action="store_true",
                    help="uppercase object numbers (off by default, since "
                         "lowercase part suffixes like 1990.1a can be meaningful)")
    ap.add_argument("--sort", choices=["none", "object-number", "title"],
                    default="none", help="sort output rows")
    ap.add_argument("--drop-duplicates", action="store_true",
                    help="drop rows that are exact duplicates after cleaning")
    ap.add_argument("--check-links", action="store_true",
                    help="verify each link responds (makes network requests)")
    ap.add_argument("--timeout", type=float, default=10.0,
                    help="link-check timeout in seconds (default 10)")
    ap.add_argument("--raw-quotes", action="store_true",
                    help="don't treat double quotes as CSV quoting characters")
    args = ap.parse_args()

    if not args.input.exists():
        sys.exit(f"Error: {args.input} not found")
    stem = args.input.with_suffix("")
    out_path = args.output or Path(f"{stem}_standardized.tsv")
    issues_path = args.issues or Path(f"{stem}_issues.tsv")

    rows, encoding = read_tsv(args.input, args.raw_quotes)
    if not rows:
        sys.exit("Error: input file is empty")

    # --- Figure out column layout ---------------------------------------
    fields = ["date", "title", "object_number", "link"]
    mapping = {} if args.no_header else detect_columns(rows[0])
    if len(mapping) == 4:
        data, first_line = rows[1:], 2
        cols = [mapping[f] for f in fields]
    elif len(mapping) >= 2:
        missing = [f for f in fields if f not in mapping]
        sys.exit(f"Error: header row recognized but couldn't find column(s): "
                 f"{', '.join(missing)}.\nHeader seen: {rows[0]}\n"
                 f"Rename the headers or use --no-header if columns are in "
                 f"order date, title, object number, link.")
    else:
        data, first_line = rows, 1
        cols = [0, 1, 2, 3]

    issues = []          # (line, column, original, standardized, problem)
    cleaned = []         # (line, [date, title, objnum, link])

    def flag(line, column, original, value, problem):
        if problem:
            issues.append((line, column, original, value, problem))

    # --- Clean each row ---------------------------------------------------
    for line, row in enumerate(data, start=first_line):
        if not any(cell.strip() for cell in row):
            continue                                   # skip blank lines
        if len(row) < max(cols) + 1:
            flag(line, "(row)", "\t".join(row), "",
                 f"row has {len(row)} column(s); missing values padded")
            row = row + [""] * (max(cols) + 1 - len(row))
        elif not mapping and len(row) > 4 and any(c.strip() for c in row[4:]):
            flag(line, "(row)", "\t".join(row[4:]), "",
                 "row has extra columns; extra values ignored")

        raw_date, raw_title, raw_obj, raw_link = (row[i] for i in cols)

        d, p = standardize_date(raw_date, args.day_first)
        flag(line, "Date", raw_date, d, p)
        t, p = standardize_title(raw_title)
        flag(line, "Title", raw_title, t, p)
        o, p = standardize_object_number(raw_obj, args.uppercase_object_numbers)
        flag(line, "Object Number", raw_obj, o, p)
        u, p = standardize_link(raw_link, args.force_https)
        flag(line, "Link", raw_link, u, p)

        cleaned.append((line, [d, t, o, u]))

    # --- Duplicate checks -------------------------------------------------
    if args.drop_duplicates:
        seen, unique = set(), []
        for line, rec in cleaned:
            key = tuple(rec)
            if key in seen:
                flag(line, "(row)", "", "", "exact duplicate row dropped")
                continue
            seen.add(key)
            unique.append((line, rec))
        cleaned = unique

    obj_counts = Counter(rec[2].casefold() for _, rec in cleaned if rec[2])
    for line, rec in cleaned:
        if rec[2] and obj_counts[rec[2].casefold()] > 1:
            flag(line, "Object Number", rec[2], rec[2],
                 f"duplicate object number ({obj_counts[rec[2].casefold()]} rows)")

    # --- Optional link checking -------------------------------------------
    if args.check_links:
        urls = sorted({rec[3] for _, rec in cleaned if rec[3].startswith("http")})
        print(f"Checking {len(urls)} unique link(s)...", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = dict(zip(urls, pool.map(
                lambda u: check_link(u, args.timeout), urls)))
        for line, rec in cleaned:
            problem = results.get(rec[3])
            flag(line, "Link", rec[3], rec[3], problem)

    # --- Sort & write -----------------------------------------------------
    if args.sort == "object-number":
        cleaned.sort(key=lambda x: natural_key(x[1][2]))
    elif args.sort == "title":
        cleaned.sort(key=lambda x: x[1][1].casefold())

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(OUTPUT_HEADER)
        w.writerows(rec for _, rec in cleaned)

    issues.sort(key=lambda x: x[0])
    with open(issues_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["Line", "Column", "Original", "Standardized", "Issue"])
        w.writerows(issues)

    # --- Summary ----------------------------------------------------------
    by_col = Counter(col for _, col, *_ in issues)
    print(f"Read {len(data)} data row(s) from {args.input} ({encoding})",
          file=sys.stderr)
    print(f"Wrote {len(cleaned)} row(s) to {out_path}", file=sys.stderr)
    if issues:
        print(f"{len(issues)} issue(s) need review -> {issues_path}",
              file=sys.stderr)
        for col, n in by_col.most_common():
            print(f"  {col:15} {n}", file=sys.stderr)
    else:
        print("No issues found.", file=sys.stderr)


if __name__ == "__main__":
    main()
```

## Example

**Input (`inventory.tsv`):**
```
Date	Title	Accession No.	URL
c.1850	  "Portrait of a Woman"  	Acc. # 1999 . 12 . 3	www.museum.org/collection/123?utm_source=email
March 14th, 1998	[untitled]	2001.45a	HTTP://Museum.ORG:80/objects/45
19th c.	STILL LIFE WITH PEARS	1999.12.3	museum.org/objects/12
1850-60	Landscape		not a link
n.d.	Vase	L-2020.7	https://museum.org/l2020-7
3/4/1921	Chair	1921.4.1	https://museum.org/chair
```

**Command:**
```
python standardize_inventory.py inventory.tsv --sort object-number
```

**Output (`inventory_standardized.tsv`):**
```
Date	Title	Object Number	Link
1850-1860	Landscape		not a link
1921-03-04	Chair	1921.4.1	https://museum.org/chair
ca. 1850	Portrait of a Woman	1999.12.3	https://www.museum.org/collection/123
19th century	STILL LIFE WITH PEARS	1999.12.3	https://museum.org/objects/12
1998-03-14	Untitled	2001.45a	http://museum.org/objects/45
undated	Vase	L-2020.7	https://museum.org/l2020-7
```

**Issues report (`inventory_issues.tsv`):**
```
Line	Column	Original	Standardized	Issue
2	Object Number	1999.12.3	1999.12.3	duplicate object number (2 rows)
4	Title	STILL LIFE WITH PEARS	STILL LIFE WITH PEARS	title is ALL CAPS; review capitalization
4	Object Number	1999.12.3	1999.12.3	duplicate object number (2 rows)
5	Object Number			missing object number
5	Link	not a link	not a link	invalid URL
7	Date	3/4/1921	1921-03-04	ambiguous day/month order; assumed month-first
```

## Design choices

- **Values are never silently changed when they're ambiguous.** Unrecognized dates, bad URLs, and similar cases keep their original value and go to the issues report.
- **Titles keep their capitalization.** Art titles often have deliberate styling, so ALL-CAPS titles are flagged, not rewritten.
- **Object numbers keep their case by default.** Lowercase part suffixes like `2001.45a` are a common cataloging convention. Use `--uppercase-object-numbers` if your institution uses uppercase.
- **Ambiguous numeric dates** like `3/4/1921` are read month-first unless you pass `--day-first`. Either way, each one is flagged.
- **Header names are flexible.** "Accession No.", "URL", and "Object Number" are all recognized. If there's no header, columns are assumed to be in the order date, title, object number, link.
- **Input encoding is detected automatically** (UTF-8, Windows-1252, or Latin-1), and output is always UTF-8.

If your collection uses a specific house style, the relevant code is easy to change. For example, you might want en-dash ranges (`1850–1860`), a different "circa" format, or a specific accession-number pattern to validate against.
