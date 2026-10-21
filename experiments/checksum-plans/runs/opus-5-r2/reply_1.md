Below is a single-file, dependency-free Python 3 script (`standardize_inventory.py`). It reads a messy museum inventory TSV, normalizes the four fields, emits a clean TSV, and writes a separate issue report so a registrar can review anything ambiguous instead of silently losing it.

```python
#!/usr/bin/env python3
"""
standardize_inventory.py — clean up a museum inventory TSV.

Expected columns (header names are matched loosely): date, title, object number, link.
Any additional columns are passed through untouched.

What it does
------------
  date          -> parsed into EDTF-style machine-readable form plus
                   date_start / date_end / date_qualifier columns
                   (e.g. "ca. 1893-95" -> "1893/1895~", 1893, 1895, circa)
  title         -> Unicode NFC, whitespace collapsed, stray wrapping quotes
                   removed, "Untitled" variants unified, optional case repair
  object number -> prefixes like "Acc. No." stripped, Unicode dashes
                   normalized, spaces around separators removed
  link          -> scheme/host lowercased, bare domains given https://,
                   spaces percent-encoded, junk trailing punctuation trimmed
  rows          -> optional de-duplication on object number

Usage
-----
  python3 standardize_inventory.py in.tsv -o clean.tsv --report issues.tsv
  python3 standardize_inventory.py in.tsv -o clean.tsv --dedupe --fix-caps
  cat in.tsv | python3 standardize_inventory.py - -o - > clean.tsv

Nothing is deleted: unparseable values are passed through verbatim and
flagged in the report.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import quote, urlsplit, urlunsplit

# --------------------------------------------------------------------------
# Column recognition
# --------------------------------------------------------------------------

COLUMN_ALIASES = {
    "date": {
        "date", "dates", "datestring", "dateofwork", "datecreated", "creationdate",
        "year", "years", "dated", "objectdate", "displaydate",
    },
    "title": {
        "title", "titles", "objecttitle", "name", "objectname", "caption", "worktitle",
    },
    "object_number": {
        "objectnumber", "objectno", "objectid", "objnumber", "objno",
        "accessionnumber", "accessionno", "accno", "accessionnum",
        "inventorynumber", "inventoryno", "invno", "invnumber", "number", "idnumber",
    },
    "link": {
        "link", "links", "url", "uri", "permalink", "weblink", "webpage",
        "collectionlink", "href", "recordurl", "imagelink", "imageurl",
    },
}

NULL_TOKENS = {
    "", "-", "--", "---", ".", "n/a", "na", "n.a.", "none", "null", "nil",
    "unknown", "[unknown]", "(unknown)", "?", "tbd", "#n/a", "not recorded",
}


def header_key(cell: str) -> str:
    """Reduce a header cell to a comparison key: lowercase, letters+digits only."""
    return re.sub(r"[^a-z0-9]", "", cell.strip().lower())


# --------------------------------------------------------------------------
# Generic text cleaning
# --------------------------------------------------------------------------

DASH_CHARS = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"
DASH_MAP = {ord(c): "-" for c in DASH_CHARS}
QUOTE_MAP = {0x2018: "'", 0x2019: "'", 0x201C: '"', 0x201D: '"', 0x00AB: '"', 0x00BB: '"'}


def clean_text(value: Optional[str]) -> str:
    """NFC-normalize, strip control chars / zero-widths, collapse whitespace."""
    if value is None:
        return ""
    s = unicodedata.normalize("NFC", str(value))
    s = s.replace("\u00a0", " ").replace("\u200b", "").replace("\ufeff", "")
    s = re.sub(r"[\t\r\n\v\f]+", " ", s)
    s = "".join(ch for ch in s if ch == " " or unicodedata.category(ch)[0] != "C")
    return re.sub(r" {2,}", " ", s).strip()


def is_null(value: str) -> bool:
    return value.strip().lower() in NULL_TOKENS


# --------------------------------------------------------------------------
# Dates
# --------------------------------------------------------------------------

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
MONTH_RE = r"(?:" + "|".join(sorted(MONTHS, key=len, reverse=True)) + r")"
DAYS_IN_MONTH = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


@dataclass
class ParsedDate:
    display: str = ""          # normalized, EDTF-flavored string
    start: str = ""            # earliest year (may be negative for BCE)
    end: str = ""              # latest year
    qualifier: str = ""        # circa | before | after | uncertain | undated
    parsed: bool = False
    note: str = ""


def _thirds(lo: int, hi: int, modifier: str) -> tuple[int, int]:
    """Split a century/decade into early / mid / late thirds."""
    span = hi - lo + 1
    step = span // 3
    if modifier == "early":
        return lo, lo + step - 1
    if modifier == "mid":
        return lo + step, lo + 2 * step - 1
    if modifier == "late":
        return lo + 2 * step, hi
    return lo, hi


def _expand_end_year(start: int, end_raw: str) -> int:
    """'1893-95' -> 1895; '1893-5' -> 1895; '1893-1895' -> 1895."""
    end = int(end_raw)
    if len(end_raw) == 4:
        return end
    if len(end_raw) == 2:
        candidate = (start // 100) * 100 + end
        return candidate + 100 if candidate < start else candidate
    candidate = (start // 10) * 10 + end
    return candidate + 10 if candidate < start else candidate


def parse_date(raw: str, dayfirst: bool = False) -> ParsedDate:
    """Parse the free-text date strings that actually show up in museum data."""
    text = clean_text(raw)
    if not text or is_null(text):
        return ParsedDate(display="", qualifier="undated", parsed=True)

    work = text.translate(DASH_MAP).translate(QUOTE_MAP)
    low = work.lower()

    qualifier = ""
    if re.search(r"\bn\.?\s?d\.?\b|undated|no date", low):
        return ParsedDate(display="", qualifier="undated", parsed=True)
    if re.search(r"\b(ca?|circa|approx(?:imately)?|about|around)\b\.?|^c\.", low):
        qualifier = "circa"
    elif re.search(r"\b(before|prior to|ante|by)\b", low):
        qualifier = "before"
    elif re.search(r"\b(after|post)\b", low):
        qualifier = "after"
    elif "?" in low or "probably" in low or "possibly" in low:
        qualifier = "uncertain"

    bce = bool(re.search(r"\b(bce?|b\.c\.(?:e\.)?)\b", low))
    sign = -1 if bce else 1

    # strip qualifier words, era markers and decorative punctuation
    core = re.sub(
        r"\b(ca?|circa|approx(?:imately)?|about|around|before|prior to|ante|by|"
        r"after|post|probably|possibly|dated|made|created|bce?|ce|ad|"
        r"b\.c\.(?:e\.)?|a\.d\.)\b\.?",
        " ", low)
    core = re.sub(r"[?\[\](){}]", " ", core)
    core = re.sub(r"\s+", " ", core).strip(" .,;:")

    def done(display: str, start: int, end: int, note: str = "") -> ParsedDate:
        return ParsedDate(display, str(start), str(end), qualifier, True, note)

    # --- ISO: 1893-03-05 / 1893-03 ---------------------------------------
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", core)
    if m:
        y, mo, d = int(m[1]), int(m[2]), int(m[3])
        if 1 <= mo <= 12 and 1 <= d <= DAYS_IN_MONTH[mo]:
            return done(_edtf(f"{y:04d}-{mo:02d}-{d:02d}", qualifier), sign * y, sign * y)
    m = re.fullmatch(r"(\d{4})-(\d{1,2})", core)
    if m and 1 <= int(m[2]) <= 12:
        y = int(m[1])
        return done(_edtf(f"{y:04d}-{int(m[2]):02d}", qualifier), sign * y, sign * y)

    # --- numeric d/m/y or m/d/y ------------------------------------------
    m = re.fullmatch(r"(\d{1,4})[/.\-](\d{1,2})[/.\-](\d{2,4})", core)
    if m:
        a, b, c = m[1], m[2], m[3]
        if len(a) == 4:                              # 1893/03/05
            y, mo, d = int(a), int(b), int(c)
        else:
            y = int(c) if len(c) == 4 else 1900 + int(c) if int(c) < 100 else int(c)
            mo, d = (int(b), int(a)) if dayfirst else (int(a), int(b))
        if 1 <= mo <= 12 and 1 <= d <= DAYS_IN_MONTH[mo]:
            note = "" if len(a) == 4 else "ambiguous numeric date; assumed %s" % (
                "day/month/year" if dayfirst else "month/day/year")
            return done(_edtf(f"{y:04d}-{mo:02d}-{d:02d}", qualifier), sign * y, sign * y, note)

    # --- "5 March 1893" / "March 5, 1893" / "March 1893" ------------------
    m = re.fullmatch(rf"(\d{{1,2}})\s+({MONTH_RE})\.?,?\s+(\d{{3,4}})", core)
    if m:
        d, mo, y = int(m[1]), MONTHS[m[2]], int(m[3])
        if d <= DAYS_IN_MONTH[mo]:
            return done(_edtf(f"{y:04d}-{mo:02d}-{d:02d}", qualifier), sign * y, sign * y)
    m = re.fullmatch(rf"({MONTH_RE})\.?\s+(\d{{1,2}}),?\s+(\d{{3,4}})", core)
    if m:
        mo, d, y = MONTHS[m[1]], int(m[2]), int(m[3])
        if d <= DAYS_IN_MONTH[mo]:
            return done(_edtf(f"{y:04d}-{mo:02d}-{d:02d}", qualifier), sign * y, sign * y)
    m = re.fullmatch(rf"({MONTH_RE})\.?,?\s+(\d{{3,4}})", core)
    if m:
        mo, y = MONTHS[m[1]], int(m[2])
        return done(_edtf(f"{y:04d}-{mo:02d}", qualifier), sign * y, sign * y)

    # --- centuries: "early 19th century" ---------------------------------
    m = re.fullmatch(r"(early|mid|late)?[\s-]*(\d{1,2})(?:st|nd|rd|th)\s*c(?:ent(?:ury)?)?\.?", core)
    if m:
        cent = int(m[2])
        lo, hi = _thirds((cent - 1) * 100, (cent - 1) * 100 + 99, m[1] or "")
        if bce:
            lo, hi = -hi, -lo
        return done(_edtf(f"{lo:04d}/{hi:04d}" if lo >= 0 else f"{lo}/{hi}", qualifier), lo, hi)

    # --- decades: "1890s", "late 1890s" ----------------------------------
    m = re.fullmatch(r"(early|mid|late)?[\s-]*(\d{3})0'?s", core)
    if m:
        base = int(m[2]) * 10
        lo, hi = _thirds(base, base + 9, m[1] or "")
        return done(_edtf(f"{lo:04d}/{hi:04d}", qualifier), sign * lo, sign * hi)

    # --- ranges: "1893-95", "1893 to 1895" -------------------------------
    m = re.fullmatch(r"(\d{3,4})\s*(?:-|to|/|and)\s*(\d{1,4})", core)
    if m:
        start = int(m[1])
        end = _expand_end_year(start, m[2])
        if end < start:
            start, end = end, start
        if bce:
            start, end = -end, -start
        return done(_edtf(f"{abs(start):04d}/{abs(end):04d}" if not bce
                          else f"{start}/{end}", qualifier), start, end)

    # --- bare year --------------------------------------------------------
    m = re.fullmatch(r"(\d{1,4})", core)
    if m:
        y = sign * int(m[1])
        label = f"{y:04d}" if y >= 0 else str(y)
        if qualifier == "before":
            return done(f"../{label}", y - 25, y, "open-ended: 'before'")
        if qualifier == "after":
            return done(f"{label}/..", y, y + 25, "open-ended: 'after'")
        return done(_edtf(label, qualifier), y, y)

    # --- give up: keep the original text ----------------------------------
    return ParsedDate(display=text, qualifier=qualifier, parsed=False,
                      note="could not parse date; original kept")


def _edtf(base: str, qualifier: str) -> str:
    if qualifier == "circa":
        return base + "~"
    if qualifier == "uncertain":
        return base + "?"
    return base


def display_date(pd: ParsedDate, style: str) -> str:
    """Render the normalized date in the requested style."""
    if style == "edtf" or not pd.parsed:
        return pd.display
    # human-readable style
    if not pd.display:
        return ""
    body = pd.display.rstrip("~?")
    if "/" in body:
        a, b = body.split("/", 1)
        if a == "..":
            body = f"before {b}"
        elif b == "..":
            body = f"after {a}"
        else:
            body = f"{a}\u2013{b}"
    prefix = "ca. " if pd.qualifier == "circa" else ""
    suffix = " (?)" if pd.qualifier == "uncertain" else ""
    return f"{prefix}{body}{suffix}"


# --------------------------------------------------------------------------
# Titles
# --------------------------------------------------------------------------

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "but", "by", "de", "del", "der", "di", "du",
    "en", "et", "for", "from", "in", "la", "le", "nor", "of", "on", "or", "the",
    "to", "van", "von", "with",
}
UNTITLED_RE = re.compile(r"^[\[\(\{]?\s*(untitled|no title|without title)\s*[\]\)\}]?$", re.I)


def smart_title_case(text: str) -> str:
    words = text.split(" ")
    out = []
    for i, word in enumerate(words):
        bare = re.sub(r"[^\w']", "", word)
        if not bare:
            out.append(word)
            continue
        if re.fullmatch(r"[IVXLCDM]+", bare):           # roman numerals
            out.append(word)
            continue
        lower = word.lower()
        if 0 < i < len(words) - 1 and re.sub(r"[^\w']", "", lower) in SMALL_WORDS:
            out.append(lower)
        else:
            out.append(re.sub(r"[a-zA-Z]", lambda m: m.group().upper(), lower, count=1))
    return " ".join(out)


def normalize_title(raw: str, fix_caps: bool = False) -> tuple[str, list[str]]:
    notes: list[str] = []
    s = clean_text(raw).translate(QUOTE_MAP)
    if not s or is_null(s):
        return "[Untitled]", ["empty title; substituted '[Untitled]'"]

    # remove wrapping quotation marks
    if len(s) > 1 and s[0] == s[-1] == '"':
        s = s[1:-1].strip()
        notes.append("removed wrapping quotes")

    s = re.sub(r"\s*\.\.\.\s*$", "\u2026", s)           # trailing ellipsis
    s = re.sub(r"\s+([,;:!?])", r"\1", s)               # no space before punctuation
    s = re.sub(r"\s*\.\s*$", "", s) if s.endswith(" .") else s

    if UNTITLED_RE.match(s):
        return "[Untitled]", notes

    letters = [c for c in s if c.isalpha()]
    if fix_caps and letters and sum(c.isupper() for c in letters) / len(letters) > 0.8 and len(letters) > 4:
        s = smart_title_case(s)
        notes.append("converted ALL CAPS title to title case")
    return s, notes


# --------------------------------------------------------------------------
# Object numbers
# --------------------------------------------------------------------------

PREFIX_RE = re.compile(
    r"^(?:acc(?:ession)?|obj(?:ect)?|inv(?:entory)?|cat(?:alog(?:ue)?)?|reg(?:istration)?)"
    r"\.?\s*(?:no\.?|num(?:ber)?|#)?\s*[:#.\-]?\s*", re.I)
PLAUSIBLE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.\-_/,() ]*$")


def normalize_object_number(raw: str, upper: bool = False) -> tuple[str, list[str]]:
    notes: list[str] = []
    s = clean_text(raw).translate(DASH_MAP).translate(QUOTE_MAP)
    if not s or is_null(s):
        return "", ["missing object number"]

    stripped = PREFIX_RE.sub("", s)
    if stripped != s and stripped:
        notes.append("removed label prefix")
        s = stripped

    s = re.sub(r"\s*([./\-])\s*", r"\1", s)   # "1975 . 1 . 2" -> "1975.1.2"
    s = re.sub(r"\s{2,}", " ", s).strip(" ,;:")
    s = re.sub(r"\.+$", "", s)                # drop trailing full stops
    if upper:
        s = s.upper()
    if not PLAUSIBLE_RE.match(s):
        notes.append("unusual characters in object number")
    return s, notes


# --------------------------------------------------------------------------
# Links
# --------------------------------------------------------------------------

def _strip_trailing_junk(url: str) -> str:
    while url and url[-1] in ".,;:!'\"":
        url = url[:-1]
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1]
    while url.endswith("]") and url.count("]") > url.count("["):
        url = url[:-1]
    return url


def normalize_link(raw: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    s = clean_text(raw).translate(QUOTE_MAP).strip("<>\"' ")
    if not s or is_null(s):
        return "", ["missing link"]

    s = _strip_trailing_junk(s)
    if s.lower().startswith(("http:/", "https:/")) and not s.lower().startswith(("http://", "https://")):
        s = s.replace(":/", "://", 1)
        notes.append("repaired scheme separator")

    if "://" not in s:
        if re.match(r"^(www\.|[a-z0-9-]+\.[a-z]{2,}(/|$))", s, re.I):
            s = "https://" + s
            notes.append("added https:// scheme")
        else:
            return s, ["does not look like a URL; original kept"]

    parts = urlsplit(s)
    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()
    if scheme not in ("http", "https"):
        notes.append(f"non-web scheme '{scheme}'")
    if scheme == "http":
        notes.append("insecure http:// link")
    if not netloc or "." not in netloc:
        notes.append("suspicious host")

    path = quote(parts.path, safe="/%:@&=+$,~!*'()")
    query = quote(parts.query, safe="/%:@&=+$,~!*'()?")
    fragment = quote(parts.fragment, safe="/%:@&=+$,~!*'()?")
    if " " in parts.path or " " in parts.query:
        notes.append("encoded spaces in URL")
    cleaned = urlunsplit((scheme, netloc, path, query, fragment))
    cleaned = cleaned.rstrip("/") if path in ("", "/") and not query and not fragment else cleaned
    return cleaned, notes


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

@dataclass
class Issue:
    row: int
    object_number: str
    field: str
    message: str
    original: str
    normalized: str


@dataclass
class Stats:
    rows_in: int = 0
    rows_out: int = 0
    blank_rows: int = 0
    duplicates: int = 0
    dates_unparsed: int = 0
    issues: list[Issue] = field(default_factory=list)


def map_columns(header: list[str]) -> dict[str, int]:
    found: dict[str, int] = {}
    for idx, cell in enumerate(header):
        key = header_key(cell)
        for canonical, aliases in COLUMN_ALIASES.items():
            if canonical not in found and key in aliases:
                found[canonical] = idx
                break
    return found


def open_stream(path: str, mode: str, encoding: str):
    if path == "-":
        return sys.stdin if "r" in mode else sys.stdout
    return open(path, mode, encoding=encoding, newline="")


def process(args: argparse.Namespace) -> Stats:
    stats = Stats()
    infile = open_stream(args.input, "r", args.encoding)
    try:
        reader = csv.reader(infile, delimiter=args.delimiter, quotechar='"')
        rows = list(reader)
    finally:
        if infile is not sys.stdin:
            infile.close()
    if not rows:
        sys.exit("error: input is empty")

    # --- resolve columns --------------------------------------------------
    if args.no_header:
        colmap = {"date": 0, "title": 1, "object_number": 2, "link": 3}
        extra_headers = [f"extra_{i}" for i in range(4, len(rows[0]))]
        extra_idx = list(range(4, len(rows[0])))
        body = rows
    else:
        header = [clean_text(c) for c in rows[0]]
        colmap = map_columns(header)
        missing = [c for c in ("date", "title", "object_number", "link") if c not in colmap]
        if missing:
            sys.exit(
                "error: could not find column(s): %s\n"
                "        header was: %s\n"
                "        use --no-header if the file has no header row."
                % (", ".join(missing), header))
        used = set(colmap.values())
        extra_idx = [i for i in range(len(header)) if i not in used]
        extra_headers = [header[i] or f"extra_{i}" for i in extra_idx]
        body = rows[1:]

    # --- output setup -----------------------------------------------------
    out_header = ["date", "title", "object_number", "link"]
    if args.derived:
        out_header += ["date_start", "date_end", "date_qualifier"]
    out_header += extra_headers

    outfile = open_stream(args.output, "w", args.encoding)
    writer = csv.writer(outfile, delimiter="\t", lineterminator="\n",
                        quoting=csv.QUOTE_MINIMAL)
    writer.writerow(out_header)

    seen: dict[str, int] = {}
    first_row_no = 1 if args.no_header else 2

    try:
        for offset, raw_row in enumerate(body):
            row_no = first_row_no + offset
            if not any(clean_text(c) for c in raw_row):
                stats.blank_rows += 1
                continue
            stats.rows_in += 1

            def cell(name: str) -> str:
                idx = colmap[name]
                return raw_row[idx] if idx < len(raw_row) else ""

            raw_date, raw_title = cell("date"), cell("title")
            raw_objnum, raw_link = cell("object_number"), cell("link")

            pd = parse_date(raw_date, dayfirst=args.dayfirst)
            date_out = display_date(pd, args.date_style)
            title_out, title_notes = normalize_title(raw_title, fix_caps=args.fix_caps)
            objnum_out, obj_notes = normalize_object_number(raw_objnum, upper=args.upper_object_numbers)
            link_out, link_notes = normalize_link(raw_link)

            def flag(fieldname: str, message: str, original: str, normalized: str):
                stats.issues.append(Issue(row_no, objnum_out, fieldname, message,
                                          clean_text(original), normalized))

            if not pd.parsed:
                stats.dates_unparsed += 1
            if pd.note:
                flag("date", pd.note, raw_date, date_out)
            for note in title_notes:
                flag("title", note, raw_title, title_out)
            for note in obj_notes:
                flag("object_number", note, raw_objnum, objnum_out)
            for note in link_notes:
                flag("link", note, raw_link, link_out)

            # de-duplication on object number
            key = objnum_out.casefold()
            if args.dedupe and key:
                if key in seen:
                    stats.duplicates += 1
                    flag("object_number",
                         f"duplicate of row {seen[key]}; row dropped", raw_objnum, objnum_out)
                    continue
                seen[key] = row_no

            out_row = [date_out, title_out, objnum_out, link_out]
            if args.derived:
                out_row += [pd.start, pd.end, pd.qualifier]
            out_row += [clean_text(raw_row[i]) if i < len(raw_row) else "" for i in extra_idx]
            writer.writerow([c.replace("\t", " ") for c in out_row])
            stats.rows_out += 1
    finally:
        if outfile is not sys.stdout:
            outfile.close()

    # --- issue report -----------------------------------------------------
    if args.report:
        with open(args.report, "w", encoding=args.encoding, newline="") as rf:
            rw = csv.writer(rf, delimiter="\t", lineterminator="\n")
            rw.writerow(["row", "object_number", "field", "issue", "original", "normalized"])
            for issue in stats.issues:
                rw.writerow([issue.row, issue.object_number, issue.field,
                             issue.message, issue.original, issue.normalized])
    return stats


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Standardize a museum inventory TSV (date, title, object number, link).")
    p.add_argument("input", help="input .tsv file, or '-' for stdin")
    p.add_argument("-o", "--output", default="-", help="output .tsv file (default: stdout)")
    p.add_argument("--report", help="write a TSV report of flagged values to this path")
    p.add_argument("--delimiter", default="\t",
                   help="input delimiter (default: tab; use ',' for CSV)")
    p.add_argument("--encoding", default="utf-8-sig", help="file encoding (default: utf-8-sig)")
    p.add_argument("--no-header", action="store_true",
                   help="input has no header row; assume column order date,title,object number,link")
    p.add_argument("--date-style", choices=["edtf", "display"], default="edtf",
                   help="edtf: 1893/1895~  |  display: ca. 1893\u20131895 (default: edtf)")
    p.add_argument("--dayfirst", action="store_true",
                   help="read ambiguous numeric dates as day/month/year (default: month/day/year)")
    p.add_argument("--no-derived", dest="derived", action="store_false",
                   help="do not add date_start / date_end / date_qualifier columns")
    p.add_argument("--fix-caps", action="store_true",
                   help="convert ALL CAPS titles to title case")
    p.add_argument("--upper-object-numbers", action="store_true",
                   help="uppercase object numbers (off by default: part letters like '2a-b' are meaningful)")
    p.add_argument("--dedupe", action="store_true",
                   help="drop later rows that repeat an object number")
    p.add_argument("-q", "--quiet", action="store_true", help="suppress the summary on stderr")
    return p


def main() -> None:
    args = build_parser().parse_args()
    stats = process(args)
    if not args.quiet:
        print(
            f"rows read:        {stats.rows_in}\n"
            f"rows written:     {stats.rows_out}\n"
            f"blank rows:       {stats.blank_rows}\n"
            f"duplicates:       {stats.duplicates}\n"
            f"unparsed dates:   {stats.dates_unparsed}\n"
            f"flagged values:   {len(stats.issues)}"
            + (f"  -> {args.report}" if args.report else "  (use --report to export)"),
            file=sys.stderr)


if __name__ == "__main__":
    main()
```

### Example

Input (`in.tsv`):

| date | Title | Acc. No. | URL |
|---|---|---|---|
| ca. 1893-95 | THE GLEANERS AT DUSK | Acc. No. 1975 . 14 . 2a-b | www.example-museum.org/collection/1975.14.2 |
| March 5, 1893 | "Study for a Fountain" | 1975.15 | https://Example-Museum.org/obj/15?view=full |
| late 19th century | untitled | 1975.16. | |
| sometime in the war years | Portrait of a Lady | 1975.17 | http://example-museum.org/obj/17). |

Run:

```bash
python3 standardize_inventory.py in.tsv -o clean.tsv --report issues.tsv --fix-caps --dedupe
```

Output (`clean.tsv`):

```
date        title                   object_number  link                                              date_start  date_end  date_qualifier
1893/1895~  The Gleaners at Dusk    1975.14.2a-b   https://www.example-museum.org/collection/1975.14.2  1893      1895      circa
1893-03-05  Study for a Fountain    1975.15        https://example-museum.org/obj/15?view=full          1893      1893
1867/1899   [Untitled]              1975.16                                                            1867      1899
sometime in the war years  Portrait of a Lady  1975.17  http://example-museum.org/obj/17                          
```

`issues.tsv` records each intervention — the removed `Acc. No.` prefix, the added scheme, the missing link, the insecure `http://`, and the date it could not parse.

### Assumptions worth confirming before you run it on real data

- **Dates** default to [EDTF](https://www.loc.gov/standards/datetime/) level 1 (`1893/1895~`, `1893?`, `../1893`), which round-trips into TMS/CollectionSpace/Wikidata pipelines. Use `--date-style display` if a human-readable column is wanted instead. "Early/mid/late" century and decade qualifiers are mapped to thirds; change `_thirds()` if your institution uses different conventions.
- **Object numbers** keep their original case by default, since trailing part letters (`.2a-b`) are usually significant. Add `--upper-object-numbers` only if your numbering is genuinely case-insensitive.
- **Nothing is discarded.** Unparseable dates and non-URL links are passed through verbatim and flagged; `--dedupe` is opt-in, and dropped duplicates are logged with the row they collided with.
- **Extra columns** (medium, dimensions, credit line, etc.) are carried through with whitespace cleaned but values otherwise untouched.

If you share a few real rows, I can tune the date patterns, the object-number format check, and the URL rules to your actual collection.
