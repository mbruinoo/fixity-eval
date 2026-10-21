Below is a single‑file, stdlib‑only Python 3 script. It auto‑detects the header (or takes the columns positionally), normalizes each of the four fields according to common museum‑cataloguing conventions, writes a clean TSV, and emits a separate issues report so a registrar can review anything it couldn't confidently fix.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
standardize_inventory.py — clean and standardize a 4-column museum inventory TSV.

Expected columns (any order; header names are auto-detected, or use --no-header
to read them positionally as date, title, object number, link):

    date | title | object number | link

Examples
--------
    python standardize_inventory.py raw.tsv -o clean.tsv --report issues.tsv
    python standardize_inventory.py raw.tsv --fix-caps --dedupe --sort object
    cat raw.tsv | python standardize_inventory.py - > clean.tsv
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
from collections import Counter, namedtuple
from datetime import date as _date
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

# --------------------------------------------------------------------------- #
# House style — edit these to match your institution's data standard
# --------------------------------------------------------------------------- #

OUTPUT_FIELDS   = ["date", "title", "object_number", "link"]
RANGE_DASH      = "\u2013"   # en dash for date ranges: 1897–1900
NO_DATE_LABEL   = "n.d."     # label for undated works
UNTITLED_LABEL  = "Untitled"
DEFAULT_SCHEME  = "https"
STRIP_QUERY_KEYS = re.compile(r"^(utm_|fbclid|gclid|mc_cid|mc_eid|ref|source$)", re.I)

NO_DATE_TOKENS = {
    "", "-", "--", "?", "??", "n.d", "nd", "n/d", "no date", "undated", "unknown",
    "unk", "n/a", "na", "none", "not dated", "date unknown",
}

UNTITLED_RE = re.compile(
    r"^\[?\s*(untitled|no title|title not known|unknown|n/?a)\s*\]?$", re.I
)

# Words kept lowercase when re-casing SHOUTING TITLES (--fix-caps)
SMALL_WORDS = {
    "a", "an", "the", "and", "but", "or", "nor", "for", "so", "yet", "as", "at",
    "by", "in", "of", "off", "on", "per", "to", "up", "via", "with", "from",
    "into", "over", "upon", "near", "de", "del", "la", "le", "van", "von",
}

MONTHS = ["", "January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
MONTH_LOOKUP = {m.lower(): i for i, m in enumerate(MONTHS) if m}
MONTH_LOOKUP.update({m.lower()[:3]: i for i, m in enumerate(MONTHS) if m})
MONTH_LOOKUP["sept"] = 9

# Header synonyms -> canonical field
HEADER_ALIASES = {
    "date": {
        "date", "dates", "dated", "year", "years", "date made", "object date",
        "date created", "creation date", "date of work", "execution date",
    },
    "title": {
        "title", "titles", "object title", "work title", "name", "object name",
        "caption", "description",
    },
    "object_number": {
        "object number", "object no", "object num", "object id", "objectid",
        "accession number", "accession no", "accession", "acc no", "acc number",
        "inventory number", "inv no", "inventory no", "number", "no", "id",
        "catalogue number", "catalog number", "cat no", "registration number",
    },
    "link": {
        "link", "links", "url", "uri", "web link", "weblink", "permalink",
        "object url", "record url", "collection url", "href", "web page",
    },
}

# --------------------------------------------------------------------------- #
# Low-level text hygiene
# --------------------------------------------------------------------------- #

ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff"), None)
DASHES = {ord(c): "-" for c in "\u2010\u2011\u2012\u2013\u2014\u2015\u2212\uff0d"}
STRAIGHT = {0x2018: "'", 0x2019: "'", 0x201a: "'", 0x201b: "'",
            0x201c: '"', 0x201d: '"', 0x201e: '"', 0x2032: "'", 0x2033: '"'}


def clean_text(value: str | None) -> str:
    """Unicode-normalize, drop invisible junk, collapse all whitespace."""
    if value is None:
        return ""
    s = unicodedata.normalize("NFC", str(value))
    s = s.translate(ZERO_WIDTH)
    s = s.replace("\u00a0", " ").replace("\u202f", " ")
    s = re.sub(r"[\t\r\n\v\f]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def sanitize_cell(s: str) -> str:
    """Guarantee a value can never break the TSV grid."""
    return s.replace("\t", " ").replace("\n", " ").replace("\r", " ")


def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


# --------------------------------------------------------------------------- #
# Dates
# --------------------------------------------------------------------------- #

Date = namedtuple("Date", "display start end precision ok")

QUALIFIER_RE = re.compile(
    r"^(circa|ca|c|about|abt|approx(?:imately)?|before|prior to|not before|"
    r"not after|after|by|probably|possibly)\b\.?\s*",
    re.I,
)
QUALIFIER_CANON = {
    "circa": "ca.", "ca": "ca.", "c": "ca.", "about": "ca.", "abt": "ca.",
    "approx": "ca.", "approximately": "ca.", "before": "before",
    "prior to": "before", "not before": "not before", "not after": "not after",
    "after": "after", "by": "by", "probably": "probably", "possibly": "possibly",
}
ORDINAL_CENTURY_RE = re.compile(
    r"^(early|mid|middle|late|first half|second half|first quarter|last quarter)?[\s-]*"
    r"(\d{1,2})(?:st|nd|rd|th)?\s*(?:c|cent|century)\.?$", re.I
)


def _valid_ymd(y: int, m: int, d: int) -> bool:
    try:
        _date(y, m, d)
        return True
    except ValueError:
        return False


def _fmt_full(y: int, m: int, d: int, style: str) -> str:
    return f"{y:04d}-{m:02d}-{d:02d}" if style == "iso" else f"{MONTHS[m]} {d}, {y}"


def _fmt_month(y: int, m: int, style: str) -> str:
    return f"{y:04d}-{m:02d}" if style == "iso" else f"{MONTHS[m]} {y}"


def _parse_core(s: str, dayfirst: bool, style: str):
    """Return (display, start_year, end_year, precision) or None."""
    s = s.strip().strip(",")

    # 1897-03-14 / 1897-3-14
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        y, mo, d = map(int, m.groups())
        if _valid_ymd(y, mo, d):
            return _fmt_full(y, mo, d, style), y, y, "day"

    # 1897-09  (zero-padded 2-digit month => year-month; otherwise a range)
    m = re.fullmatch(r"(\d{4})-(\d{2})", s)
    if m and 1 <= int(m.group(2)) <= 12 and m.group(2)[0] in "01":
        y, mo = int(m.group(1)), int(m.group(2))
        return _fmt_month(y, mo, style), y, y, "month"

    # 1897
    m = re.fullmatch(r"(\d{3,4})", s)
    if m:
        y = int(m.group(1))
        return f"{y}", y, y, "year"

    # 1897-1900 / 1897-99 / 1897-9 / 1897/1900
    m = re.fullmatch(r"(\d{3,4})\s*[-/]\s*(\d{1,4})", s)
    if m:
        a, b = m.group(1), m.group(2)
        start = int(a)
        end = int(b) if len(b) >= len(a) else int(a[: len(a) - len(b)] + b)
        if end >= start:
            return f"{start}{RANGE_DASH}{end}", start, end, "range"

    # 1890s / 1890's
    m = re.fullmatch(r"(\d{3,4})'?s", s)
    if m:
        y = int(m.group(1))
        return f"{y}s", y, y + 9, "decade"

    # late 19th century
    m = ORDINAL_CENTURY_RE.fullmatch(s)
    if m:
        mod, cent = (m.group(1) or "").lower(), int(m.group(2))
        c0, c1 = (cent - 1) * 100 + 1, cent * 100
        spans = {
            "early": (c0, c0 + 32), "mid": (c0 + 33, c0 + 65),
            "middle": (c0 + 33, c0 + 65), "late": (c0 + 66, c1),
            "first half": (c0, c0 + 49), "second half": (c0 + 50, c1),
            "first quarter": (c0, c0 + 24), "last quarter": (c0 + 75, c1),
        }
        start, end = spans.get(mod, (c0, c1))
        label = f"{mod + ' ' if mod else ''}{cent}{_ordinal_suffix(cent)} century"
        return label, start, end, "century"

    # 14 March 1897 / March 14, 1897 / Mar. 14 1897
    t = s.replace(".", " ")
    t = re.sub(r"(\d)(st|nd|rd|th)\b", r"\1", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip()
    m = re.fullmatch(r"(\d{1,2}) ([A-Za-z]+),? (\d{4})", t)
    if m and m.group(2).lower() in MONTH_LOOKUP:
        d, mo, y = int(m.group(1)), MONTH_LOOKUP[m.group(2).lower()], int(m.group(3))
        if _valid_ymd(y, mo, d):
            return _fmt_full(y, mo, d, style), y, y, "day"
    m = re.fullmatch(r"([A-Za-z]+) (\d{1,2}),? (\d{4})", t)
    if m and m.group(1).lower() in MONTH_LOOKUP:
        mo, d, y = MONTH_LOOKUP[m.group(1).lower()], int(m.group(2)), int(m.group(3))
        if _valid_ymd(y, mo, d):
            return _fmt_full(y, mo, d, style), y, y, "day"
    m = re.fullmatch(r"([A-Za-z]+),? (\d{4})", t)
    if m and m.group(1).lower() in MONTH_LOOKUP:
        mo, y = MONTH_LOOKUP[m.group(1).lower()], int(m.group(2))
        return _fmt_month(y, mo, style), y, y, "month"

    # 3/14/1897 (or 14/3/1897 with --dayfirst)
    m = re.fullmatch(r"(\d{1,2})[/.](\d{1,2})[/.](\d{2,4})", s)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100:
            y += 1900 if y > 30 else 2000
        mo, d = (b, a) if dayfirst else (a, b)
        if not _valid_ymd(y, mo, d) and _valid_ymd(y, d, mo):
            mo, d = d, mo
        if _valid_ymd(y, mo, d):
            return _fmt_full(y, mo, d, style), y, y, "day"

    return None


def _ordinal_suffix(n: int) -> str:
    if 11 <= n % 100 <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def normalize_date(raw: str, dayfirst: bool = False, style: str = "iso") -> Date:
    s = clean_text(raw)
    if s.lower().strip(". ") in NO_DATE_TOKENS:
        return Date(NO_DATE_LABEL if s else "", None, None, "none", True)

    s = s.translate(DASHES)
    s = re.sub(r"\s*-\s*", "-", s)
    s = re.sub(r"^\[|\]$", "", s).strip()           # [1897] -> 1897
    s = re.sub(r"\(\s*\?\s*\)|\?$", "", s).strip()  # 1897? -> 1897 (with qualifier below)

    qualifier = ""
    if raw.strip().endswith("?"):
        qualifier = "ca."
    m = QUALIFIER_RE.match(s)
    if m:
        qualifier = QUALIFIER_CANON[m.group(1).lower()]
        s = s[m.end():].strip()

    parsed = _parse_core(s, dayfirst, style)
    if parsed is None:
        return Date(clean_text(raw), None, None, "unparsed", False)

    display, start, end, precision = parsed
    if qualifier:
        display = f"{qualifier} {display}"
        if qualifier == "before":
            start = None
        elif qualifier in ("after", "by"):
            end = None if qualifier == "after" else end
    return Date(display, start, end, precision, True)


# --------------------------------------------------------------------------- #
# Titles
# --------------------------------------------------------------------------- #

def smart_title_case(s: str) -> str:
    words = s.split(" ")
    out = []
    for i, w in enumerate(words):
        core = w.strip("\"'([{")
        lower = core.lower()
        if i not in (0, len(words) - 1) and lower in SMALL_WORDS:
            out.append(w.lower())
        elif re.search(r"\d", w) or (core.isupper() and len(core) <= 4):
            out.append(w)            # leave numerals and short acronyms alone
        else:
            out.append(w[:1].upper() + w[1:].lower() if w else w)
    return " ".join(out)


def normalize_title(raw: str, straight_quotes: bool = False,
                    fix_caps: bool = False, strip_final_period: bool = False) -> tuple[str, list[str]]:
    notes: list[str] = []
    s = clean_text(raw)
    if not s:
        return "", ["title missing"]

    if straight_quotes:
        s = s.translate(STRAIGHT)

    # Drop quotation marks that wrap the entire title
    if len(s) > 1 and ((s[0] == s[-1] == '"') or (s[0] == "\u201c" and s[-1] == "\u201d")):
        s = s[1:-1].strip()

    s = re.sub(r"\s+([,;:.!?])", r"\1", s)        # " ," -> ","
    s = re.sub(r"([,;:])(?=\S)", r"\1 ", s)       # "a,b" -> "a, b"
    s = re.sub(r"\s*\.\.\.\s*", "\u2026 ", s).strip()
    s = re.sub(r"\(\s*", "(", s)
    s = re.sub(r"\s*\)", ")", s)

    if UNTITLED_RE.fullmatch(s):
        return UNTITLED_LABEL, notes

    letters = [c for c in s if c.isalpha()]
    if fix_caps and len(letters) > 3 and all(c.isupper() for c in letters):
        s = smart_title_case(s)
        notes.append("re-cased from all caps")

    if strip_final_period and s.endswith(".") and not re.search(r"\b[A-Z]\.$", s):
        s = s[:-1].rstrip()

    return s, notes


# --------------------------------------------------------------------------- #
# Object / accession numbers
# --------------------------------------------------------------------------- #

OBJ_PREFIX_RE = re.compile(
    r"^(object|accession|acc|inventory|inv|catalogue|catalog|cat|reg|registration)"
    r"\.?\s*(no\.?|number|num\.?|#|id)?\s*[:.\-]?\s*", re.I
)


def normalize_object_number(raw: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    s = clean_text(raw).translate(DASHES)
    if not s:
        return "", ["object number missing"]

    before = s
    s = OBJ_PREFIX_RE.sub("", s).strip()
    s = s.strip("[](){}<>\"'")
    s = re.sub(r"^(no\.?|#)\s*", "", s, flags=re.I)
    s = re.sub(r"\s*([./-])\s*", r"\1", s)   # "1992 . 45 . 2" -> "1992.45.2"
    s = re.sub(r"\s+", " ", s).strip(" .,;")

    # Uppercase any department/collection prefix (tr.1234 -> TR.1234);
    # leave trailing part-letters lowercase (1992.45.2A-C -> 1992.45.2a-c).
    m = re.match(r"^([A-Za-z]{1,6})(?=[\s.\-/]?\d)", s)
    if m:
        s = m.group(1).upper() + s[m.end():]
    s = re.sub(r"(?<=\d)([A-Z]{1,3})(?=[-,/]|$)", lambda x: x.group(1).lower(), s)

    if s != before:
        notes.append("object number reformatted")
    if not re.search(r"\d", s):
        notes.append("object number contains no digits — verify")
    return s, notes


# --------------------------------------------------------------------------- #
# Links
# --------------------------------------------------------------------------- #

def normalize_link(raw: str, drop_fragment: bool = True,
                   strip_tracking: bool = True) -> tuple[str, list[str]]:
    notes: list[str] = []
    s = clean_text(raw).strip("<>\"'").rstrip(".,;)")
    if not s:
        return "", ["link missing"]
    if s.lower() in {"n/a", "na", "none", "-", "no link"}:
        return "", ["link missing"]

    if "://" not in s:
        if s.lower().startswith("www.") or re.match(r"^[\w.-]+\.[a-z]{2,}(/|$)", s, re.I):
            s = f"{DEFAULT_SCHEME}://{s}"
            notes.append("scheme added")
        else:
            return s, ["link does not look like a URL — verify"]

    try:
        parts = urlsplit(s)
    except ValueError:
        return s, ["link could not be parsed — verify"]

    scheme = parts.scheme.lower()
    if scheme == "http":
        scheme = "https"
        notes.append("http upgraded to https")
    if scheme not in ("https", "http"):
        notes.append(f"unexpected scheme '{scheme}' — verify")

    netloc = parts.netloc.lower()
    netloc = re.sub(r":443$|:80$", "", netloc)

    path = quote(parts.path, safe="/%:@&=+$,~!*'();")
    path = re.sub(r"/{2,}", "/", path)

    query = parts.query
    if strip_tracking and query:
        kept = [(k, v) for k, v in parse_qsl(query, keep_blank_values=True)
                if not STRIP_QUERY_KEYS.match(k)]
        new_query = urlencode(kept)
        if new_query != query:
            notes.append("tracking parameters removed")
        query = new_query

    fragment = "" if drop_fragment else parts.fragment
    url = urlunsplit((scheme, netloc, path, query, fragment))
    if not netloc:
        notes.append("link has no host — verify")
    return url, notes


# --------------------------------------------------------------------------- #
# I/O and orchestration
# --------------------------------------------------------------------------- #

def header_key(cell: str) -> str:
    s = clean_text(cell).lower()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def detect_columns(header: list[str]) -> dict[str, int] | None:
    mapping: dict[str, int] = {}
    for idx, cell in enumerate(header):
        key = header_key(cell)
        for field, aliases in HEADER_ALIASES.items():
            if field in mapping:
                continue
            if key in aliases or key.replace(" ", "") in {a.replace(" ", "") for a in aliases}:
                mapping[field] = idx
                break
    return mapping if len(mapping) == 4 else None


def read_rows(path: str):
    stream = sys.stdin if path == "-" else open(path, "r", encoding="utf-8-sig", newline="")
    with stream as fh:
        yield from csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="input .tsv ('-' for stdin)")
    p.add_argument("-o", "--output", default="-", help="output .tsv (default: stdout)")
    p.add_argument("--report", help="write a TSV of issues needing human review")
    p.add_argument("--no-header", action="store_true",
                   help="treat row 1 as data; columns are date, title, object number, link")
    p.add_argument("--date-style", choices=["iso", "display"], default="iso",
                   help="'iso' -> 1897-03-14; 'display' -> March 14, 1897")
    p.add_argument("--dayfirst", action="store_true",
                   help="read 3/4/1897 as 3 April (day/month/year)")
    p.add_argument("--fix-caps", action="store_true", help="re-case ALL-CAPS titles")
    p.add_argument("--straight-quotes", action="store_true",
                   help="convert curly quotes to straight quotes in titles")
    p.add_argument("--strip-final-period", action="store_true",
                   help="remove a trailing period from titles")
    p.add_argument("--keep-fragment", action="store_true", help="keep #fragments in URLs")
    p.add_argument("--keep-tracking", action="store_true", help="keep utm_* etc. in URLs")
    p.add_argument("--dedupe", action="store_true",
                   help="keep only the first row for each object number")
    p.add_argument("--sort", choices=["none", "object", "date"], default="none")
    p.add_argument("--add-sort-columns", action="store_true",
                   help="append date_start and date_end (machine-sortable years)")
    args = p.parse_args(argv)

    rows = list(read_rows(args.input))
    if not rows:
        sys.stderr.write("Input is empty.\n")
        return 1

    order = {f: i for i, f in enumerate(OUTPUT_FIELDS)}
    start_row = 0
    if not args.no_header:
        detected = detect_columns(rows[0])
        if detected:
            order, start_row = detected, 1
        elif any(header_key(c) in {a for s in HEADER_ALIASES.values() for a in s}
                 for c in rows[0]):
            sys.stderr.write("Warning: partial header recognized; using positional order.\n")
            start_row = 1
        else:
            sys.stderr.write("Warning: no header found; using positional order.\n")

    issues: list[tuple] = []
    cleaned: list[dict] = []
    seen_numbers: dict[str, int] = {}

    for n, row in enumerate(rows[start_row:], start=start_row + 1):
        if not any(clean_text(c) for c in row):
            continue
        width_needed = max(order.values()) + 1
        if len(row) < width_needed:
            issues.append((n, "row", f"only {len(row)} column(s); padded", " | ".join(row)))
            row = row + [""] * (width_needed - len(row))
        elif len(row) > width_needed and any(clean_text(c) for c in row[width_needed:]):
            issues.append((n, "row", "extra non-empty column(s) ignored",
                           " | ".join(row[width_needed:])))

        raw = {f: row[i] for f, i in order.items()}

        d = normalize_date(raw["date"], dayfirst=args.dayfirst, style=args.date_style)
        if not d.ok:
            issues.append((n, "date", "could not parse date", raw["date"]))
        elif d.start and not (1000 <= d.start <= _date.today().year):
            issues.append((n, "date", "year out of expected range", raw["date"]))

        title, t_notes = normalize_title(
            raw["title"], straight_quotes=args.straight_quotes,
            fix_caps=args.fix_caps, strip_final_period=args.strip_final_period)
        for note in t_notes:
            issues.append((n, "title", note, raw["title"]))

        objnum, o_notes = normalize_object_number(raw["object_number"])
        for note in o_notes:
            if note != "object number reformatted":
                issues.append((n, "object_number", note, raw["object_number"]))

        link, l_notes = normalize_link(
            raw["link"], drop_fragment=not args.keep_fragment,
            strip_tracking=not args.keep_tracking)
        for note in l_notes:
            if "verify" in note or "missing" in note:
                issues.append((n, "link", note, raw["link"]))

        if objnum:
            if objnum in seen_numbers:
                issues.append((n, "object_number",
                               f"duplicate of row {seen_numbers[objnum]}", objnum))
                if args.dedupe:
                    continue
            else:
                seen_numbers[objnum] = n

        cleaned.append({
            "date": d.display, "title": title, "object_number": objnum, "link": link,
            "date_start": "" if d.start is None else str(d.start),
            "date_end": "" if d.end is None else str(d.end),
            "_sort_year": d.start if d.start is not None else 9999,
        })

    if args.sort == "object":
        cleaned.sort(key=lambda r: natural_key(r["object_number"]))
    elif args.sort == "date":
        cleaned.sort(key=lambda r: (r["_sort_year"], natural_key(r["object_number"])))

    fields = OUTPUT_FIELDS + (["date_start", "date_end"] if args.add_sort_columns else [])
    out = sys.stdout if args.output == "-" else open(args.output, "w", encoding="utf-8", newline="")
    with out as fh:
        fh.write("\t".join(fields) + "\n")
        for r in cleaned:
            fh.write("\t".join(sanitize_cell(r[f]) for f in fields) + "\n")

    if args.report:
        with open(args.report, "w", encoding="utf-8", newline="") as fh:
            fh.write("input_row\tfield\tissue\toriginal_value\n")
            for row_no, field, issue, value in issues:
                fh.write(f"{row_no}\t{field}\t{issue}\t{sanitize_cell(clean_text(value))}\n")

    counts = Counter(i[1] for i in issues)
    sys.stderr.write(
        f"Processed {len(rows) - start_row} input row(s) -> {len(cleaned)} output row(s); "
        f"{len(issues)} issue(s)"
        + (f" ({', '.join(f'{k}: {v}' for k, v in sorted(counts.items()))})" if counts else "")
        + ".\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### What it does to each column

| Column | Normalizations |
|---|---|
| **date** | Parses years, ranges (`1897-99` → `1897–1900`), decades (`1890's` → `1890s`), centuries (`late 19th c.` → `late 19th century`), textual and numeric dates; canonicalizes qualifiers (`c.`, `ca`, `about`, trailing `?` → `ca.`; `prior to` → `before`); blanks/`unknown`/`n/a` → `n.d.`; optional machine-sortable `date_start`/`date_end` year columns. |
| **title** | Unicode NFC, invisible-character and whitespace cleanup, punctuation spacing, removal of wrapping quotes, `[untitled]` variants → `Untitled`; optional curly→straight quotes and ALL-CAPS re-casing that respects small words and acronyms. |
| **object number** | Strips `Accession No.:` style prefixes and stray brackets, unifies dash variants, closes spaces around `.`/`-`/`/`, uppercases department prefixes (`tr.1234` → `TR.1234`), lowercases part suffixes (`.2A-C` → `.2a-c`), and flags duplicates. |
| **link** | Trims wrapping `<>`/trailing punctuation, adds a scheme, upgrades `http`→`https`, lowercases host, drops default ports and `utm_*`/`fbclid` tracking, percent-encodes paths, drops fragments. |

### Assumptions worth confirming before you run it on real data

- **`1897-09`** is read as September 1897 (zero-padded two-digit month), while `1897-99` is read as a range. Rename ambiguous cells first if your data uses the other convention.
- **`3/4/1897`** is read month-first unless you pass `--dayfirst`.
- `http` is silently upgraded to `https`; remove that branch if some collection URLs are HTTP-only.
- Anything the script can't confidently fix is **left as-is and logged** rather than guessed at — always run with `--report issues.tsv` and review it.

Test on a copy first: `python standardize_inventory.py raw.tsv -o clean.tsv --report issues.tsv`, then diff a sample of rows against the original.
