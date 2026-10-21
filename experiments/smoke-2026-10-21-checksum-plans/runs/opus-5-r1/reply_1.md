Below is a single‑file, dependency‑free Python 3 tool. It reads a messy 4‑column museum inventory (`date`, `title`, `object number`, `link`), normalizes each field against common museum conventions (EDTF dates, accession‑number formatting, URL hygiene), and writes a clean TSV plus an optional issue/change report.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
standardize_inventory.py — clean and standardize a museum inventory spreadsheet.

INPUT   A .tsv (or .csv) whose columns are, in any order and under almost any
        header spelling:  date | title | object number | link

OUTPUT  A UTF-8 TSV with canonical headers:  date  title  object_number  link
        (optionally plus date_earliest / date_latest / date_edtf),
        and an optional tab-separated report of every change and problem.

WHAT IT STANDARDIZES
  date          "c.1890", "ca. 1890-95", "19th c.", "1890s", "May 12, 1890",
                "n.d." ...  ->  normalized display form + ISO bounds + EDTF
  title         whitespace/Unicode cleanup, smart-quote handling, stray wrapping
                quotes, ALL-CAPS repair (opt-in), consistent "Untitled"
  object number drops "Acc. No.:" style prefixes, normalizes dashes/spacing,
                validates shape, optional upper-casing, duplicate detection
  link          adds missing scheme, repairs "http:/", lowercases host, strips
                utm_*/fbclid tracking params, percent-encodes spaces, validates,
                can fill blanks from a template, can verify with HTTP (opt-in)

USAGE
  python3 standardize_inventory.py in.tsv -o clean.tsv -r report.tsv
  python3 standardize_inventory.py in.tsv --expand-dates --fix-caps --dedupe
  python3 standardize_inventory.py in.csv --delimiter comma \
      --link-template "https://collection.example.org/objects/{object_number}"
  python3 standardize_inventory.py in.tsv --check-links --strict
  python3 standardize_inventory.py --selftest

Python 3.8+. No third-party packages required.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

# --------------------------------------------------------------------------
# Configuration constants (edit to match your institution's house style)
# --------------------------------------------------------------------------

CANONICAL_FIELDS = ["date", "title", "object_number", "link"]
EXPANDED_FIELDS = ["date_earliest", "date_latest", "date_edtf"]

# Header synonyms -> canonical name. Keys are compared after lowercasing and
# stripping every non-alphanumeric character.
HEADER_SYNONYMS: Dict[str, str] = {}
for _canon, _variants in {
    "date": [
        "date", "dates", "datemade", "datecreated", "creationdate", "objectdate",
        "dateofcreation", "dated", "year", "years", "period", "datetext",
        "displaydate", "datedisplay",
    ],
    "title": [
        "title", "titles", "objecttitle", "name", "objectname", "worktitle",
        "titleofwork", "caption", "description",
    ],
    "object_number": [
        "objectnumber", "objectno", "objectnum", "objectid", "accessionnumber",
        "accessionno", "accession", "accno", "invno", "inventorynumber",
        "inventoryno", "catalognumber", "catalogueno", "catalognumber",
        "idnumber", "id", "number", "no", "refno", "referencenumber",
    ],
    "link": [
        "link", "links", "url", "urls", "weblink", "webaddress", "uri",
        "permalink", "collectionlink", "collectionurl", "recordurl", "href",
        "onlinerecord",
    ],
}.items():
    for _v in _variants:
        HEADER_SYNONYMS[_v] = _canon

# Century convention: 19th century == 1800-1899 (collections practice).
# Set CENTURY_STARTS_AT_01 = True for the strict 1801-1900 reading.
CENTURY_STARTS_AT_01 = False

NO_DATE_TOKENS = {
    "", "-", "--", "---", "?", "??", "n.d.", "nd", "n/a", "na", "none", "null",
    "unknown", "undated", "unk", "no date", "not dated", "date unknown",
    "date not known", "nodate", "tbd", "x",
}

NULL_TOKENS = {"", "-", "--", "n/a", "na", "none", "null", "unknown", "tbd", "x", "?"}

TRACKING_PARAMS = re.compile(
    r"^(utm_[a-z_]+|fbclid|gclid|mc_cid|mc_eid|igshid|ref|ref_src|src|"
    r"_ga|_gl|yclid|msclkid|spm)$", re.I
)

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "but", "by", "for", "from", "in", "into",
    "nor", "of", "on", "onto", "or", "over", "per", "the", "to", "up", "upon",
    "via", "vs", "with", "within", "without", "after", "before", "near",
}

ROMAN_RE = re.compile(r"^(?=[MDCLXVI])M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", re.I)

USER_AGENT = "museum-inventory-standardizer/1.0 (+collections data QA)"

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}

INVISIBLE = dict.fromkeys(
    map(ord, "\u200b\u200c\u200d\u200e\u200f\u2060\ufeff\u00ad"), None
)
CURLY_TO_STRAIGHT = {
    0x201C: '"', 0x201D: '"', 0x201E: '"', 0x201F: '"', 0x2033: '"',
    0x2018: "'", 0x2019: "'", 0x201A: "'", 0x201B: "'", 0x2032: "'",
    0x2039: "'", 0x203A: "'",
}

# --------------------------------------------------------------------------
# Issue log
# --------------------------------------------------------------------------

LEVELS = {"INFO": 0, "WARN": 1, "ERROR": 2}


@dataclass
class Issue:
    row: int               # 1-based source row number (excluding header)
    object_number: str
    field_name: str
    level: str             # INFO | WARN | ERROR
    code: str
    message: str
    original: str
    standardized: str


@dataclass
class Record:
    row: int
    values: Dict[str, str] = field(default_factory=dict)
    extra: List[str] = field(default_factory=list)


# --------------------------------------------------------------------------
# Generic text helpers
# --------------------------------------------------------------------------

def clean_text(s: Optional[str]) -> str:
    """NFC-normalize, drop invisibles, flatten all whitespace runs to one space."""
    if s is None:
        return ""
    s = unicodedata.normalize("NFC", str(s))
    s = s.translate(INVISIBLE)
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[\t\r\n\v\f]+", " ", s)
    s = re.sub(r" {2,}", " ", s)
    return s.strip()


def is_null_token(s: str) -> bool:
    return s.strip().strip(".").lower() in NULL_TOKENS


def natural_key(s: str):
    return [(0, int(t)) if t.isdigit() else (1, t.lower())
            for t in re.findall(r"\d+|\D+", s or "")]


# --------------------------------------------------------------------------
# Dates
# --------------------------------------------------------------------------

@dataclass
class DateInfo:
    display: str
    earliest: str = ""     # ISO yyyy-mm-dd
    latest: str = ""       # ISO yyyy-mm-dd
    edtf: str = ""
    level: str = ""        # issue level, if any
    code: str = ""
    message: str = ""


QUALIFIER_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"^(?:circa|ca|cca|c|abt|about|approx(?:imately)?|around)\.?\s+", re.I), "circa"),
    (re.compile(r"^(?:ca|c)\.?(?=\s*\d)", re.I), "circa"),
    (re.compile(r"^(?:before|prior\s+to|by|ante|not\s+after)\s+", re.I), "before"),
    (re.compile(r"^(?:after|post|since|not\s+before)\s+", re.I), "after"),
    (re.compile(r"^(?:probably|possibly|perhaps|likely|maybe)\s+", re.I), "uncertain"),
]


def _ymd(y: int, m: int, d: int) -> str:
    return "%04d-%02d-%02d" % (y, m, d)


def _year_bounds(y: int) -> Tuple[str, str]:
    return _ymd(y, 1, 1), _ymd(y, 12, 31)


def _month_bounds(y: int, m: int) -> Tuple[str, str]:
    return _ymd(y, m, 1), _ymd(y, m, calendar.monthrange(y, m)[1])


def _complete_year(first: int, second_text: str) -> int:
    """'1890-95' -> 1895 ; '1890-1895' -> 1895 ; '1890-5' -> 1895."""
    v = int(second_text)
    if len(second_text) >= 4:
        return v
    if len(second_text) == 3:
        return v
    base = first - (first % (10 ** len(second_text)))
    out = base + v
    if out < first:
        out += 10 ** len(second_text)
    return out


def _century_bounds(n: int) -> Tuple[int, int]:
    if CENTURY_STARTS_AT_01:
        return (n - 1) * 100 + 1, n * 100
    return (n - 1) * 100, (n - 1) * 100 + 99


def _parse_core(s: str) -> Optional[Tuple[int, int, str, str, str]]:
    """Return (earliest_iso_year_part..) as (e_iso, l_iso, display, edtf, code)."""
    s = s.strip().strip(",;")
    sl = s.lower()

    # 1890-05-12  /  1890-5-12
    m = re.fullmatch(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", s)
    if m:
        y, mo, d = (int(x) for x in m.groups())
        if 1 <= mo <= 12 and 1 <= d <= calendar.monthrange(y, mo)[1]:
            iso = _ymd(y, mo, d)
            return iso, iso, iso, iso, ""

    # 12/05/1890 (ambiguous) -> assume month/day/year, flag it
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        a, b, y = (int(x) for x in m.groups())
        mo, d, code = (a, b, "date.ambiguous") if a <= 12 else (b, a, "date.ambiguous")
        if 1 <= mo <= 12 and 1 <= d <= calendar.monthrange(y, mo)[1]:
            iso = _ymd(y, mo, d)
            return iso, iso, iso, iso, code

    # 12 May 1890 / May 12, 1890 / May 1890
    m = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3,9})\.?,?\s+(\d{4})", s)
    if m and m.group(2).lower() in MONTHS:
        d, mo, y = int(m.group(1)), MONTHS[m.group(2).lower()], int(m.group(3))
        if 1 <= d <= calendar.monthrange(y, mo)[1]:
            iso = _ymd(y, mo, d)
            return iso, iso, iso, iso, ""
    m = re.fullmatch(r"([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})", s)
    if m and m.group(1).lower() in MONTHS:
        mo, d, y = MONTHS[m.group(1).lower()], int(m.group(2)), int(m.group(3))
        if 1 <= d <= calendar.monthrange(y, mo)[1]:
            iso = _ymd(y, mo, d)
            return iso, iso, iso, iso, ""
    m = re.fullmatch(r"([A-Za-z]{3,9})\.?,?\s+(\d{4})", s)
    if m and m.group(1).lower() in MONTHS:
        mo, y = MONTHS[m.group(1).lower()], int(m.group(2))
        e, l = _month_bounds(y, mo)
        return e, l, "%04d-%02d" % (y, mo), "%04d-%02d" % (y, mo), ""

    # 1890-05  (year-month)
    m = re.fullmatch(r"(\d{4})-(\d{1,2})", s)
    if m and 1 <= int(m.group(2)) <= 12:
        y, mo = int(m.group(1)), int(m.group(2))
        e, l = _month_bounds(y, mo)
        return e, l, "%04d-%02d" % (y, mo), "%04d-%02d" % (y, mo), ""

    # early/mid/late 1890s  -> decade
    m = re.fullmatch(r"(?:(early|mid|middle|late)[-\s]+)?(\d{3,4}0)s", sl)
    if m:
        part, y = m.group(1), int(m.group(2))
        e_y, l_y = y, y + 9
        if part:
            part = "mid" if part == "middle" else part
            thirds = {"early": (0, 3), "mid": (3, 6), "late": (6, 9)}[part]
            e_y, l_y = y + thirds[0], y + thirds[1]
        disp = f"{part} {y}s" if part else f"{y}s"
        edtf = f"{y // 10}X" if not part else f"{_ymd(e_y,1,1)[:4]}/{_ymd(l_y,1,1)[:4]}"
        return _year_bounds(e_y)[0], _year_bounds(l_y)[1], disp, edtf, ""

    # early/mid/late 19th century
    m = re.fullmatch(
        r"(?:(early|mid|middle|late|first\s+half\s+of|second\s+half\s+of)"
        r"[-\s]+)?(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)?[-\s]*c(?:\.|entury)?",
        sl,
    )
    if m:
        part, n = m.group(1), int(m.group(2))
        c0, c1 = _century_bounds(n)
        if part:
            part = part.replace("middle", "mid").strip()
            if part.startswith("first half"):
                c1 = c0 + 49
            elif part.startswith("second half"):
                c0 = c0 + 50
            elif part == "early":
                c1 = c0 + 32
            elif part == "mid":
                c0, c1 = c0 + 33, c0 + 66
            elif part == "late":
                c0 = c0 + 67
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n if n < 20 else n % 10, "th")
        disp = f"{part + ' ' if part else ''}{n}{suffix} century"
        edtf = f"{c0:04d}/{c1:04d}" if part else f"{(c0 // 100):02d}XX"
        return _year_bounds(c0)[0], _year_bounds(c1)[1], disp, edtf, ""

    # 1890-95 / 1890–1895 / 1890/95 / 1890 to 1895
    m = re.fullmatch(r"(\d{3,4})\s*(?:-|/|to|and|until)\s*(\d{1,4})", sl)
    if m:
        y1 = int(m.group(1))
        y2 = _complete_year(y1, m.group(2))
        if y2 >= y1:
            e, l = _year_bounds(y1)[0], _year_bounds(y2)[1]
            return e, l, f"{y1}\u2013{y2}", f"{y1:04d}/{y2:04d}", ""

    # bare year
    m = re.fullmatch(r"(\d{3,4})", s)
    if m:
        y = int(m.group(1))
        e, l = _year_bounds(y)
        return e, l, f"{y}", f"{y:04d}", ""

    return None


def parse_date(raw: str) -> DateInfo:
    s = clean_text(raw)
    s = s.replace("\u2013", "-").replace("\u2014", "-").replace("\u2010", "-")
    s = s.strip(" .,;:")

    if not s or s.lower().strip(".") in NO_DATE_TOKENS:
        if clean_text(raw) and clean_text(raw).lower() not in {"undated", "n.d."}:
            return DateInfo("undated", "", "", "", "INFO", "date.nodate",
                            "empty or placeholder date normalized to 'undated'")
        return DateInfo("undated")

    qualifier = None
    note = ""

    m = re.search(r"\s*\(([^)]*)\)\s*$", s)
    if m:
        inner = m.group(1).strip()
        if re.fullmatch(r"\?+|sic", inner, re.I):
            qualifier = "uncertain"
        else:
            note = inner
        s = s[:m.start()].strip()

    while s.endswith("?"):
        qualifier = qualifier or "uncertain"
        s = s[:-1].strip()

    for pat, q in QUALIFIER_PATTERNS:
        m = pat.match(s)
        if m:
            qualifier = qualifier or q
            s = s[m.end():].strip()
            break

    core = _parse_core(s)
    if core is None:
        years = [int(y) for y in re.findall(r"\b(\d{3,4})\b", s) if 100 <= int(y) <= 2100]
        if years:
            y1, y2 = min(years), max(years)
            disp = clean_text(raw)
            return DateInfo(
                disp, _year_bounds(y1)[0], _year_bounds(y2)[1],
                f"{y1:04d}/{y2:04d}" if y1 != y2 else f"{y1:04d}",
                "WARN", "date.unparsed",
                "date not fully understood; year bounds guessed from digits",
            )
        return DateInfo(clean_text(raw), "", "", "", "WARN", "date.unparsed",
                        "date could not be parsed; left as-is for review")

    e, l, disp, edtf, code = core

    if qualifier == "circa":
        disp, edtf = f"circa {disp}", edtf + "~"
        y0, y1 = int(e[:4]), int(l[:4])
        e, l = _year_bounds(y0 - 5)[0], _year_bounds(y1 + 5)[1]
    elif qualifier == "before":
        disp, edtf = f"before {disp}", f"../{edtf}"
        e = ""
    elif qualifier == "after":
        disp, edtf = f"after {disp}", f"{edtf}/.."
        l = ""
    elif qualifier == "uncertain":
        disp, edtf = f"{disp}?", edtf + "?"

    if note:
        disp = f"{disp} ({note})"

    level = "WARN" if code else ""
    msg = "ambiguous numeric date read as month/day/year" if code else ""
    return DateInfo(disp, e, l, edtf, level, code, msg)


# --------------------------------------------------------------------------
# Titles
# --------------------------------------------------------------------------

def smart_title_case(s: str) -> str:
    def fix(word: str, first: bool, last: bool) -> str:
        if not word:
            return word
        if ROMAN_RE.fullmatch(word) and len(word) > 1:
            return word.upper()
        low = word.lower()
        if not first and not last and low.strip(".,:;") in SMALL_WORDS:
            return low
        if "'" in low:  # d'Orsay, l'Arc
            head, _, tail = low.partition("'")
            return head.capitalize() + "'" + (tail[:1].upper() + tail[1:] if len(head) > 1 else tail)
        return low[:1].upper() + low[1:]

    tokens = re.split(r"(\s+|[\u2013\u2014/:;()\[\]])", s)
    word_idx = [i for i, t in enumerate(tokens) if t.strip() and not re.fullmatch(r"[\s\u2013\u2014/:;()\[\]]+", t)]
    for n, i in enumerate(word_idx):
        parts = tokens[i].split("-")
        tokens[i] = "-".join(
            fix(p, first=(n == 0 and j == 0), last=(n == len(word_idx) - 1 and j == len(parts) - 1))
            for j, p in enumerate(parts)
        )
    return "".join(tokens)


def standardize_title(raw: str, opts) -> Tuple[str, List[Tuple[str, str, str]]]:
    notes: List[Tuple[str, str, str]] = []
    s = clean_text(raw)

    if not s or is_null_token(s):
        notes.append(("WARN", "title.missing", "no title supplied; used placeholder"))
        return opts.untitled, notes

    if not opts.curly_quotes:
        s = s.translate(CURLY_TO_STRAIGHT)

    # strip wrapping quotes: "Starry Night"  ->  Starry Night
    if len(s) > 2 and s[0] in "\"'\u201c\u2018" and s[-1] in "\"'\u201d\u2019":
        inner = s[1:-1]
        if not re.search(r"[\"'\u201c\u201d\u2018\u2019]", inner):
            s = inner.strip()
            notes.append(("INFO", "title.unquoted", "removed wrapping quotation marks"))

    if re.fullmatch(r"[\[\(]?\s*(untitled|no title|without title|title unknown)\s*[\]\)]?\.?",
                    s, re.I):
        if s != opts.untitled:
            notes.append(("INFO", "title.untitled", f"normalized to '{opts.untitled}'"))
        s = opts.untitled

    letters = [c for c in s if c.isalpha()]
    if opts.fix_caps and len(letters) >= 4 and all(c.isupper() for c in letters):
        s = smart_title_case(s)
        notes.append(("INFO", "title.caps", "ALL-CAPS title converted to title case"))

    s = re.sub(r"\s+([,;:.!?])", r"\1", s)
    s = re.sub(r"\(\s+|\s+\)", lambda m: m.group(0).strip(), s)

    if len(s) > 250:
        notes.append(("WARN", "title.long", f"title is {len(s)} characters; check for pasted
