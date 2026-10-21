Below is a single-file, dependency-free (stdlib only) Python 3 script. It reads a messy museum inventory TSV with *date, title, object number, link* columns, normalizes each field according to explicit rules, emits a clean TSV with sortable derived date columns and a per-row `flags` column, and prints a QA report.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
standardize_inventory.py — clean and standardize a museum inventory table.

Input : .tsv (or .csv) with columns for date, title, object number, link
        (any order; header optional; extra columns are passed through).
Output: .tsv with normalized fields plus derived, sortable date columns and a
        QA `flags` column. Nothing is silently discarded: anything the script
        cannot parse is kept verbatim and flagged for human review.

Usage
-----
  python3 standardize_inventory.py inventory.tsv -o clean.tsv
  python3 standardize_inventory.py inventory.tsv -o clean.tsv --report qa.txt
  python3 standardize_inventory.py raw.tsv -o clean.tsv \
      --date-format edtf --fix-caps --objnum-case upper --dedupe \
      --sort object --base-url https://collection.example.org/

Columns written
---------------
  date            normalized display date ("1887-04-12", "ca. 1850", "1850s",
                  "19th century", "1850–1860", "undated", …) or EDTF
  date_earliest   ISO date for sorting/filtering (YYYY-MM-DD), may be blank
  date_latest     ISO date for sorting/filtering (YYYY-MM-DD), may be blank
  title           whitespace/punctuation-normalized title
  object_number   separator- and spacing-normalized accession number
  link            absolute, scheme-normalized, tracking-free URL
  [*_original]    optional verbatim originals (--keep-originals)
  [extras…]       any unrecognized input columns, untouched
  flags           semicolon-separated QA codes (suppress with --no-flags)

Public domain / CC0. Adapt the rule constants near the top to local practice.
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import re
import sys
import unicodedata
from collections import Counter
from urllib.parse import parse_qsl, quote, urlencode, urljoin, urlsplit, urlunsplit

# --------------------------------------------------------------------------- #
# Configuration you may want to localize
# --------------------------------------------------------------------------- #

CANON = ["date", "title", "object_number", "link"]

HEADER_ALIASES = {
    "date": {
        "date", "dates", "date made", "datemade", "object date", "date of object",
        "creation date", "date created", "year", "years", "period", "dated",
    },
    "title": {
        "title", "titles", "object title", "object name", "name", "work",
        "work title", "caption", "description",
    },
    "object_number": {
        "object number", "objectnumber", "object no", "object num", "obj number",
        "accession number", "accession no", "accession", "acc no", "acc num",
        "inventory number", "inventory no", "inv no", "inv num", "id",
        "object id", "number", "museum number", "registration number",
    },
    "link": {
        "link", "links", "url", "uri", "weblink", "web link", "web address",
        "permalink", "object url", "collection url", "web page", "webpage", "href",
    },
}

NO_DATE_TOKENS = {
    "n.d.", "nd", "n/d", "n. d.", "no date", "undated", "not dated", "unknown",
    "date unknown", "unknown date", "none", "n/a", "na", "-", "--", "?", "unk",
}

# Lowercased in title case unless first/last word (used only with --fix-caps)
SMALL_WORDS = {
    "a", "an", "and", "as", "at", "but", "by", "en", "for", "from", "if", "in",
    "into", "nor", "of", "off", "on", "onto", "or", "over", "per", "the", "to",
    "up", "via", "vs", "with",
}

DEFAULT_DROP_PARAMS = "utm_*,fbclid,gclid,mc_cid,mc_eid,_ga,ref,referrer,igshid"

# Accession numbers that look like this are considered "normal"
OBJNUM_OK = re.compile(r"^[A-Za-z0-9]+(?:[./\-_][A-Za-z0-9]+)*$")

MONTHS: dict[str, int] = {}
for _i, _names in enumerate(
    [
        ("january", "jan"), ("february", "feb", "febr"), ("march", "mar"),
        ("april", "apr"), ("may",), ("june", "jun"), ("july", "jul"),
        ("august", "aug"), ("september", "sep", "sept"), ("october", "oct"),
        ("november", "nov"), ("december", "dec"),
    ],
    start=1,
):
    for _n in _names:
        MONTHS[_n] = _i
MONTH_RE = "|".join(sorted(MONTHS, key=len, reverse=True))

SEASONS = {  # name -> (start_month, start_day, end_month, end_day, edtf_code)
    "spring": (3, 1, 5, 31, 21), "summer": (6, 1, 8, 31, 22),
    "autumn": (9, 1, 11, 30, 23), "fall": (9, 1, 11, 30, 23),
    "winter": (12, 1, 2, 28, 24),
}

RANGE_SPLIT = re.compile(r"\s*(?:--+|[-\u2010-\u2015\u2212/]|\bto\b|\bthrough\b|\bu/a\b)\s*", re.I)

# --------------------------------------------------------------------------- #
# Text helpers
# --------------------------------------------------------------------------- #

QUOTE_MAP = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'", "\u2032": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u201f": '"', "\u2033": '"',
})


def clean_text(value) -> str:
    """NFC-normalize, kill control/format chars, unify spaces, trim."""
    if value is None:
        return ""
    s = unicodedata.normalize("NFC", str(s_ := value)) if not isinstance(value, str) else unicodedata.normalize("NFC", value)
    s = s.replace("\u00ad", "")                       # soft hyphen
    s = "".join(" " if unicodedata.category(c) == "Zs" else c for c in s)
    s = "".join(c for c in s if unicodedata.category(c)[0] != "C")  # strip CR/LF/controls
    return re.sub(r"\s+", " ", s).strip()


def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s or "")]


def is_shouting(s: str) -> bool:
    letters = [c for c in s if c.isalpha()]
    if len(letters) < 4:
        return False
    return sum(c.isupper() for c in letters) / len(letters) >= 0.9


def _tc_word(word: str, force_cap: bool) -> str:
    m = re.match(r"^([^\w]*)(.*?)([^\w]*)$", word, re.UNICODE)
    pre, core, post = m.group(1), m.group(2), m.group(3)
    if not core:
        return word
    if re.fullmatch(r"[IVXLCDM]{2,}", core):          # roman numerals: XIV, LXX
        return pre + core + post
    if not force_cap and core.lower() in SMALL_WORDS:
        return pre + core.lower() + post
    parts = re.split(r"([-'\u2019])", core.lower())
    out = []
    for i, part in enumerate(parts):
        if i and parts[i - 1] in ("'", "\u2019") and len(part) <= 2:
            out.append(part)                          # women's, O'er -> keep suffix low
        elif part in ("-", "'", "\u2019"):
            out.append(part)
        else:
            out.append(part[:1].upper() + part[1:])
    return pre + "".join(out) + post


def smart_titlecase(s: str) -> str:
    words = s.split(" ")
    n = len(words)
    return " ".join(_tc_word(w, i == 0 or i == n - 1) for i, w in enumerate(words))


# --------------------------------------------------------------------------- #
# Date normalization
# --------------------------------------------------------------------------- #

def _days_in_month(y: int, m: int) -> int:
    if m == 2:
        leap = (y % 4 == 0 and y % 100 != 0) or y % 400 == 0
        return 29 if leap else 28
    return [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]


def _iso(y: int, m: int = 1, d: int = 1) -> str:
    return f"{'-' if y < 0 else ''}{abs(y):04d}-{m:02d}-{d:02d}"


class Point:
    """A parsed date expression: display forms + earliest/latest bounds."""

    __slots__ = ("plain", "edtf", "earliest", "latest")

    def __init__(self, plain, edtf, earliest, latest):
        self.plain, self.edtf, self.earliest, self.latest = plain, edtf, earliest, latest


def _year_point(y: int, era: int = 1) -> Point:
    y *= era
    suffix = " BCE" if y < 0 else ""
    return Point(f"{abs(y)}{suffix}", _edtf_year(y), _iso(y, 1, 1), _iso(y, 12, 31))


def _edtf_year(y: int) -> str:
    return f"{'-' if y < 0 else ''}{abs(y):04d}"


def _parse_point(s: str, flags: list[str], dayfirst: bool = False) -> Point | None:
    s = s.strip().strip(",;")
    if not s:
        return None
    low = s.lower()

    era = 1
    m = re.search(r"\b(b\.?\s?c\.?(\s?e\.?)?|bce)\.?$", low)
    if m:
        era, low = -1, low[: m.start()].strip()
    else:
        m = re.search(r"\b(a\.?\s?d\.?|c\.?e\.?)\.?$", low)
        if m:
            low = low[: m.start()].strip()

    # ISO-ish full date: 1887-04-12 / 1887.04.12
    m = re.fullmatch(r"(-?\d{3,4})[-.](\d{1,2})[-.](\d{1,2})", low)
    if m:
        y, mo, d = int(m.group(1)) * era, int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= _days_in_month(y, mo):
            return Point(_iso(y, mo, d), _iso(y, mo, d), _iso(y, mo, d), _iso(y, mo, d))

    # ISO year-month: 1887-04
    m = re.fullmatch(r"(-?\d{3,4})[-.](\d{1,2})", low)
    if m:
        y, mo = int(m.group(1)) * era, int(m.group(2))
        if 1 <= mo <= 12:
            disp = f"{abs(y):04d}-{mo:02d}"
            return Point(disp, disp, _iso(y, mo, 1), _iso(y, mo, _days_in_month(y, mo)))

    # 12 April 1887 / April 12, 1887 / Apr. 1887
    m = re.fullmatch(rf"(\d{{1,2}})\s*(?:st|nd|rd|th)?\s+({MONTH_RE})\.?,?\s+(\d{{3,4}})", low)
    if m:
        d, mo, y = int(m.group(1)), MONTHS[m.group(2)], int(m.group(3)) * era
        if d <= _days_in_month(y, mo):
            return Point(_iso(y, mo, d), _iso(y, mo, d), _iso(y, mo, d), _iso(y, mo, d))
    m = re.fullmatch(rf"({MONTH_RE})\.?\s+(\d{{1,2}})\s*(?:st|nd|rd|th)?,?\s+(\d{{3,4}})", low)
    if m:
        mo, d, y = MONTHS[m.group(1)], int(m.group(2)), int(m.group(3)) * era
        if d <= _days_in_month(y, mo):
            return Point(_iso(y, mo, d), _iso(y, mo, d), _iso(y, mo, d), _iso(y, mo, d))
    m = re.fullmatch(rf"({MONTH_RE})\.?,?\s+(\d{{3,4}})", low)
    if m:
        mo, y = MONTHS[m.group(1)], int(m.group(2)) * era
        disp = f"{abs(y):04d}-{mo:02d}"
        return Point(disp, disp, _iso(y, mo, 1), _iso(y, mo, _days_in_month(y, mo)))

    # Spring 1850
    m = re.fullmatch(r"(spring|summer|autumn|fall|winter)\s+(\d{3,4})", low)
    if m:
        sm, sd, em, ed, code = SEASONS[m.group(1)]
        y = int(m.group(2)) * era
        ey = y + 1 if m.group(1) == "winter" else y
        if em == 2:
            ed = _days_in_month(ey, 2)
        return Point(f"{m.group(1).capitalize()} {abs(y)}", f"{_edtf_year(y)}-{code}",
                     _iso(y, sm, sd), _iso(ey, em, ed))

    # Numeric slash dates: 4/12/1887, 12.4.1887, 4/12/87
    m = re.fullmatch(r"(\d{1,2})[/.](\d{1,2})[/.](\d{2,4})", low)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if len(m.group(3)) == 2:
            flags.append("date:two_digit_year")
            y += 1900 if y > 30 else 2000
        if a > 12 >= b:
            d, mo = a, b
        elif b > 12 >= a:
            mo, d = a, b
        else:
            d, mo = (a, b) if dayfirst else (b, a)
            flags.append("date:ambiguous_dmy")
        y *= era
        if 1 <= mo <= 12 and 1 <= d <= _days_in_month(y, mo):
            return Point(_iso(y, mo, d), _iso(y, mo, d), _iso(y, mo, d), _iso(y, mo, d))

    # Decade: 1850s, 1850's
    m = re.fullmatch(r"(\d{1,3})0'?s", low)
    if m:
        start = int(m.group(1) + "0") * era
        return Point(f"{abs(start)}s", f"{abs(start)//10:03d}X",
                     _iso(start, 1, 1), _iso(start + 9, 12, 31))

    # Century: 19th century, early 19th c., mid-19th century
    m = re.fullmatch(r"(early|mid|late|first half of|second half of)?[\s-]*"
                     r"(\d{1,2})(?:st|nd|rd|th)?\s*c(?:entury|ent\.?|\.)?", low)
    if m:
        qual, n = m.group(1), int(m.group(2))
        base = (n - 1) * 100
        if era < 0:
            base = -base - 99
        lo, hi = base, base + 99
        if qual in ("early",):
            hi = base + 32
        elif qual == "mid":
            lo, hi = base + 33, base + 66
        elif qual == "late":
            lo = base + 67
        elif qual == "first half of":
            hi = base + 49
        elif qual == "second half of":
            lo = base + 50
        label = f"{(qual + ' ') if qual else ''}{n}{_ord(n)} century{' BCE' if era < 0 else ''}"
        edtf = f"{base//100:02d}XX" if (lo, hi) == (base, base + 99) else f"{_edtf_year(lo)}/{_edtf_year(hi)}"
        return Point(label, edtf, _iso(lo, 1, 1), _iso(hi, 12, 31))

    # Bare year
    m = re.fullmatch(r"(\d{3,4})", low)
    if m:
        return _year_point(int(m.group(1)), era)

    return None


def _ord(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def normalize_date(raw: str, fmt: str = "plain", dayfirst: bool = False,
                   circa_years: int = 0) -> tuple[str, str, str, list[str]]:
    """Return (display, earliest, latest, flags)."""
    flags: list[str] = []
    s = clean_text(raw)
    if not s:
        return "", "", "", ["date:empty"]

    low = s.lower().strip(" .,;")
    if low in NO_DATE_TOKENS or re.fullmatch(r"n\.?\s*d\.?", low):
        return ("undated" if fmt == "plain" else ""), "", "", ["date:undated"]

    approx = uncertain = before = after = False
    while True:
        m = re.match(r"^(?:circa|ca\.|ca\b|c\.|c\b|about|around|approx\.|approx\b|approximately)\s*", low)
        if m:
            approx, low = True, low[m.end():].strip()
            continue
        m = re.match(r"^(?:probably|possibly|perhaps|likely|maybe|attributed to)\s+", low)
        if m:
            uncertain, low = True, low[m.end():].strip()
            continue
        m = re.match(r"^(?:before|prior to|ante|not after|by)\s+", low)
        if m:
            before, low = True, low[m.end():].strip()
            continue
        m = re.match(r"^(?:after|post|not before|from)\s+", low)
        if m:
            after, low = True, low[m.end():].strip()
            continue
        break
    if low.endswith("?"):
        uncertain, low = True, low.rstrip("? ").strip()
    low = re.sub(r"\s*\[.*?\]\s*", " ", low).strip()  # drop bracketed editorial notes

    m = re.match(r"^between\s+(.+?)\s+and\s+(.+)$", low)
    if m:
        low = f"{m.group(1)}/{m.group(2)}"

    point = _parse_point(low, flags, dayfirst)
    if point is None:                                   # try as a range
        parts = [p for p in RANGE_SPLIT.split(low) if p]
        if len(parts) == 2:
            a_txt, b_txt = parts
            if re.fullmatch(r"\d{1,2}", b_txt) and re.fullmatch(r"\d{3,4}", a_txt):
                b_txt = a_txt[: len(a_txt) - len(b_txt)] + b_txt   # 1850-60 -> 1860
            a, b = _parse_point(a_txt, flags, dayfirst), _parse_point(b_txt, flags, dayfirst)
            if a and b:
                point = Point(f"{a.plain}\u2013{b.plain}", f"{a.edtf}/{b.edtf}",
                              a.earliest, b.latest)
                if a.earliest and b.latest and a.earliest > b.latest:
                    flags.append("date:range_reversed")

    if point is None:
        flags.append("date:unparsed")
        return s, "", "", flags

    earliest, latest = point.earliest, point.latest
    if approx and circa_years and earliest and latest:
        ey, ly = int(earliest[:5].lstrip("-") or 0), int(latest[:5].lstrip("-") or 0)
        sign_e = -1 if earliest.startswith("-") else 1
        sign_l = -1 if latest.startswith("-") else 1
        earliest = _iso(sign_e * ey - circa_years, 1, 1)
        latest = _iso(sign_l * ly + circa_years, 12, 31)

    if fmt == "edtf":
        display = point.edtf
        if approx and uncertain:
            display += "%"
        elif approx:
            display += "~"
        elif uncertain:
            display += "?"
        if before:
            display = f"../{point.edtf}"
        if after:
            display = f"{point.edtf}/.."
    else:
        display = point.plain
        if before:
            display = f"before {display}"
        if after:
            display = f"after {display}"
        if approx:
            display = f"ca. {display}"
        if uncertain:
            display += " (?)"

    if before:
        earliest = ""
    if after:
        latest = ""
    if approx:
        flags.append("date:approximate")
    if uncertain:
        flags.append("date:uncertain")
    return display, earliest, latest, flags


# --------------------------------------------------------------------------- #
# Title / object number / link normalization
# --------------------------------------------------------------------------- #

def normalize_title(raw: str, fix_caps: bool, keep_smart_quotes: bool,
                    untitled_label: str) -> tuple[str, list[str]]:
    flags: list[str] = []
    t = clean_text(raw)
    if not keep_smart_quotes:
        t = t.translate(QUOTE_MAP)
    t = re.sub(r"\s+([,;:!?])", r"\1", t)
    t = re.sub(r"(?<=\D),(?=\S)", ", ", t)
    t = re.sub(r"\s*\.\.\.\s*", "\u2026 ", t).strip()
    t = re.sub(r"\(\s+", "(", t)
    t = re.sub(r"\s+\)", ")", t)
    t = re.sub(r"\s+", " ", t).strip(" ;,")

    if not t:
        flags.append("title:empty")
        return (untitled_label, flags) if untitled_label else ("", flags)
    if is_shouting(t):
        if fix_caps:
            t = smart_titlecase(t)
            flags.append("title:recased")
        else:
            flags.append("title:all_caps")
    for op, cl in ("()", "[]", "{}"):
        if t.count(op) != t.count(cl):
            flags.append("title:unbalanced_brackets")
            break
    if t.count('"') % 2:
        flags.append("title:unbalanced_quotes")
    return t, flags


def normalize_objnum(raw: str, case: str) -> tuple[str, list[str]]:
    flags: list[str] = []
    s = clean_text(raw)
    if not s:
        return "", ["objnum:empty"]
    s = re.sub(r"[\u2010-\u2015\u2212]", "-", s)
    s = s.strip(" .,;:")
    s = re.sub(r"\s*([./\-])\s*", r"\1", s)     # 1979 . 123 a -> 1979.123a
    s = re.sub(r"\s+", " ", s)
    if case == "upper":
        s = s.upper()
    elif case == "lower":
        s = s.lower()
    if re.search(r"[,;]| and |\bor\b", s, re.I):
        flags.append("objnum:multiple_values")
    elif not OBJNUM_OK.match(s):
        flags.append("objnum:unusual_format")
    return s, flags


def normalize_link(raw: str, base: str | None, drop_params: list[str],
                   force_https: bool) -> tuple[str, list[str]]:
    flags: list[str] = []
    s = clean_text(raw).strip("<>\"' ")
    s = re.sub(r"[.,;)\]]+$", "", s)
    if not s:
        return "", ["link:empty"]
    if s.lower() in {"n/a", "na", "none", "-"}:
        return "", ["link:empty"]

    if "://" not in s:
        if re.match(r"^(www\.|[\w-]+(\.[\w-]+)+(/|$))", s, re.I):
            s = "https://" + s
        elif base:
            s = urljoin(base, s)
        else:
            flags.append("link:relative")

    parts = urlsplit(s)
    if parts.scheme and parts.scheme.lower() not in ("http", "https"):
        flags.append(f"link:scheme_{parts.scheme.lower()}")
    scheme = parts.scheme.lower() or ("https" if base else "")
    if force_https and scheme == "http":
        scheme = "https"

    netloc = parts.netloc
    if "@" in netloc:
        userinfo, hostport = netloc.rsplit("@", 1)
        netloc = userinfo + "@" + hostport.lower()
        flags.append("link:has_userinfo")
    else:
        netloc = netloc.lower()
    netloc = re.sub(r":(80|443)$", "", netloc)

    path = quote(parts.path, safe="/%:@&=+$,;~()!*'")
    pairs = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if not any(fnmatch.fnmatch(k.lower(), p) for p in drop_params)]
    query = urlencode(pairs, quote_via=quote, safe="")
    url = urlunsplit((scheme, netloc, path, query, parts.fragment))

    if scheme and netloc and "." not in netloc:
        flags.append("link:suspicious_host")
    if not netloc and scheme:
        flags.append("link:no_host")
    return url, flags


# --------------------------------------------------------------------------- #
# I/O
# --------------------------------------------------------------------------- #

def norm_header(h: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", clean_text(h).lower()).strip()


def detect_mapping(header: list[str]) -> dict[int, str]:
    mapping: dict[int, str] = {}
    taken: set[str] = set()
    for idx, cell in enumerate(header):
        n = norm_header(cell)
        if not n:
            continue
        for canon, aliases in HEADER_ALIASES.items():
            if canon in taken:
                continue
            if n in aliases or n.replace(" ", "") in {a.replace(" ", "") for a in aliases}:
                mapping[idx] = canon
                taken.add(canon)
                break
    return mapping


def read_table(path: str, delimiter: str, no_header: bool, column_order: list[str]):
    """Return (rows_as_dicts, extra_column_names)."""
    data = None
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            with open(path, "r", encoding=enc, newline="") as fh:
                data = fh.read()
            break
        except UnicodeDecodeError:
            continue
    if data is None:
        raise SystemExit(f"Could not decode {path}")

    reader = csv.reader(data.splitlines(), delimiter=delimiter)
    table = [r for r in reader if any(c.strip() for c in r)]
    if not table:
        raise SystemExit("Input file is empty.")

    if no_header:
        mapping = {i: c for i, c in enumerate(column_order) if i < len(table[0])}
        header, body = None, table
    else:
        mapping = detect_mapping(table[0])
        if len(mapping) >= 2:
            header, body = table[0], table[1:]
        else:                                   # looks like data, not a header
            mapping = {i: c for i, c in enumerate(column_order) if i < len(table[0])}
            header, body = None, table
            print("Note: no header row detected; assuming column order "
                  f"{', '.join(column_order)}", file=sys.stderr)

    missing = [c for c in CANON if c not in mapping.values()]
    if missing:
        print(f"Warning: no column matched for: {', '.join(missing)}", file=sys.stderr)

    extras = []
    for i in range(max(len(r) for r in body)):
        if i not in mapping:
            name = norm_header(header[i]).replace(" ", "_") if header and i < len(header) else ""
            extras.append(name or f"column_{i + 1}")

    rows = []
    for raw in body:
        rec = {c: "" for c in CANON}
        rec["_extras"] = {}
        e = 0
        for i in range(max(len(raw), len(mapping))):
            val = raw[i] if i < len(raw) else ""
            if i in mapping:
                rec[mapping[i]] = val
            else:
                if e < len(extras):
                    rec["_extras"][extras[e]] = val
                e += 1
        rows.append(rec)
    return rows, extras


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Standardize a museum inventory TSV (date, title, object number, link).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("input", help="input .tsv/.csv file")
    p.add_argument("-o", "--output", default="-", help="output file ('-' for stdout)")
    p.add_argument("-d", "--delimiter", default="\t", help=r"input delimiter (default tab)")
    p.add_argument("--no-header", action="store_true", help="input has no header row")
    p.add_argument("--columns", default=",".join(CANON),
                   help="column order to assume when there is no header")
    p.add_argument("--date-format", choices=["plain", "edtf"], default="plain",
                   help="display form for the normalized date column")
    p.add_argument("--dayfirst", action="store_true",
                   help="read ambiguous 4/12/1887 as D/M/Y instead of M/D/Y")
    p.add_argument("--circa-years", type=int, default=0,
                   help="widen earliest/latest by N years for 'circa' dates")
    p.add_argument("--fix-caps", action="store_true",
                   help="convert ALL-CAPS titles to title case")
    p.add_argument("--keep-smart-quotes", action="store_true",
                   help="keep curly quotes in titles instead of straightening them")
    p.add_argument("--untitled-label", default="",
                   help="value to substitute for empty titles, e.g. '[Untitled]'")
    p.add_argument("--objnum-case", choices=["keep", "upper", "lower"], default="keep",
                   help="case folding for object numbers (keep = non-destructive)")
    p.add_argument("--base-url", default=None,
                   help="base URL used to absolutize relative links")
    p.add_argument("--force-https", action="store_true", help="rewrite http:// as https://")
    p.add_argument("--drop-params", default=DEFAULT_DROP_PARAMS,
                   help="comma-separated query-parameter glob patterns to strip")
    p.add_argument("--keep-originals", action="store_true",
                   help="append *_original columns with the verbatim input")
    p.add_argument("--no-flags", action="store_true", help="omit the flags column")
    p.add_argument("--dedupe", action="store_true",
                   help="drop rows repeating an object number (first wins)")
    p.add_argument("--sort", choices=["none", "object", "date", "title"], default="none")
    p.add_argument("--report", metavar="PATH", help="write the QA report to a file")
    p.add_argument("--quiet", action="store_true", help="suppress the stderr summary")
    p.add_argument("--strict", action="store_true", help="exit 1 if any row is flagged")
    return p.parse_args(argv)


def main(argv=None) -> int:
    a = parse_args(argv)
    column_order = [c.strip() for c in a.columns.split(",")]
    drop_params = [p.strip().lower() for p in a.drop_params.split(",") if p.strip()]

    rows, extras = read_table(a.input, a.delimiter, a.no_header, column_order)

    out_rows, flag_counter = [], Counter()
    seen_objnum: dict[str, int] = {}
    seen_link: dict[str, int] = {}
    dropped = 0

    for lineno, rec in enumerate(rows, start=1):
        flags: list[str] = []

        date_disp, earliest, latest, f = normalize_date(
            rec["date"], a.date_format, a.dayfirst, a.circa_years)
        flags += f
        title, f = normalize_title(rec["title"], a.fix_caps, a.keep_smart_quotes,
                                   a.untitled_label)
        flags += f
        objnum, f = normalize_objnum(rec["object_number"], a.objnum_case)
        flags += f
        link, f = normalize_link(rec["link"], a.base_url, drop_params, a.force_https)
        flags += f

        key = objnum.upper()
        if key:
            if key in seen_objnum:
                flags.append(f"objnum:duplicate_of_row_{seen_objnum[key]}")
                if a.dedupe:
                    dropped += 1
                    flag_counter.update(flags)
                    continue
            else:
                seen_objnum[key] = lineno
        if link:
            if link in seen_link:
                flags.append(f"link:duplicate_of_row_{seen_link[link]}")
            else:
                seen_link[link] = lineno

        row = {
            "date": date_disp,
            "date_earliest": earliest,
            "date_latest": latest,
            "title": title,
            "object_number": objnum,
            "link": link,
        }
        if a.keep_originals:
            row["date_original"] = clean_text(rec["date"])
            row["title_original"] = clean_text(rec["title"])
            row["object_number_original"] = clean_text(rec["object_number"])
            row["link_original"] = clean_text(rec["link"])
        for name in extras:
            row[name] = clean_text(rec["_extras"].get(name, ""))
        if not a.no_flags:
            row["flags"] = "; ".join(flags)

        flag_counter.update(flags)
        out_rows.append(row)

    if a.sort == "object":
        out_rows.sort(key=lambda r: natural_key(r["object_number"]))
    elif a.sort == "date":
        out_rows.sort(key=lambda r: (r["date_earliest"] == "", r["date_earliest"],
                                     natural_key(r["object_number"])))
    elif a.sort == "title":
        out_rows.sort(key=lambda r: re.sub(r"^(the|a|an)\s+", "", r["title"].lower()))

    fields = ["date", "date_earliest", "date_latest", "title", "object_number", "link"]
    if a.keep_originals:
        fields += ["date_original", "title_original", "object_number_original", "link_original"]
    fields += extras
    if not a.no_flags:
        fields.append("flags")

    out = sys.stdout if a.output == "-" else open(a.output, "w", encoding="utf-8", newline="")
    try:
        w = csv.DictWriter(out, fieldnames=fields, delimiter="\t",
                           lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(out_rows)
    finally:
        if out is not sys.stdout:
            out.close()

    flagged = sum(1 for r in out_rows if r.get("flags"))
    lines = [
        "Museum inventory standardization report",
        "=" * 39,
        f"Input file      : {a.input}",
        f"Rows read       : {len(rows)}",
        f"Rows written    : {len(out_rows)}" + (f"  ({dropped} duplicates dropped)" if dropped else ""),
        f"Rows flagged    : {flagged}",
        f"Unique obj. nos.: {len(seen_objnum)}",
        "",
        "Flag counts (highest first):",
    ]
    generic = Counter()
    for flag, n in flag_counter.items():
        generic[re.sub(r"_of_row_\d+$", "", flag)] += n
    lines += [f"  {n:6d}  {flag}" for flag, n in generic.most_common()] or ["  (none)"]
    report = "\n".join(lines) + "\n"

    if a.report:
        with open(a.report, "w", encoding="utf-8") as fh:
            fh.write(report)
    if not a.quiet:
        print(report, file=sys.stderr)

    return 1 if (a.strict and flagged) else 0


if __name__ == "__main__":
    sys.exit(main())
```

### What it does to each column

| Column | Rules applied |
|---|---|
| **date** | Strips qualifiers (`circa/c./ca.`, `probably`, `before`, `after`, trailing `?`), handles ISO dates, `12 April 1887`, `April 12, 1887`, `4/12/1887`, `1850s`, `19th century` (incl. `early/mid/late`), `Spring 1850`, `500 BC`, ranges (`1850–60`, `1850 to 1860`, `between 1850 and 1860`), and `n.d./undated`. Emits a clean display value plus `date_earliest`/`date_latest` ISO bounds so the sheet sorts and filters correctly. `--date-format edtf` emits Library of Congress EDTF (`1850~`, `185X`, `18XX`, `1850/1860`). |
| **title** | Unicode NFC, non-breaking/zero-width space removal, whitespace collapse, punctuation spacing, straightened quotes, unbalanced bracket/quote detection, optional ALL-CAPS → title case with small-word and roman-numeral handling. |
| **object number** | Dash unification, removal of spaces around `.` `-` `/`, trimming of stray punctuation, optional case folding, format sanity check, duplicate detection. |
| **link** | Trims brackets/trailing punctuation, adds missing scheme, resolves relative paths against `--base-url`, lowercases scheme/host, drops default ports and `utm_*`/`fbclid`-style tracking parameters, percent-encodes spaces, flags non-HTTP schemes and duplicates. |

### Examples

```bash
# Dry run to the terminal, see the QA report
python3 standardize_inventory.py inventory.tsv | head

# Full clean with originals retained for audit, sorted by accession number
python3 standardize_inventory.py inventory.tsv -o clean.tsv \
    --keep-originals --sort object --report qa.txt

# Headerless file with a non-standard column order
python3 standardize_inventory.py raw.tsv --no-header \
    --columns object_number,title,date,link -o clean.tsv

# Fail the build/pipeline if anything needs human review
python3 standardize_inventory.py clean.tsv -o /dev/null --strict
```

### Notes on adapting it

- **Nothing is deleted silently.** Unparseable dates pass through verbatim with `date:unparsed`; sort by the `flags` column to get a worklist.
- **`--objnum-case` defaults to `keep`** because suffix letters (`1979.123a` vs `1979.123A`) are significant in some systems; switch to `upper` only if your registrar confirms it is safe.
- **Century convention:** `19th century` → 1800–1899 (matching EDTF `18XX`). If your institution uses 1801–1900, change `base = (n - 1) * 100` in `_parse_point`.
- Add institution-specific header spellings to `HEADER_ALIASES`, and accession-number patterns to `OBJNUM_OK`.
- Always keep the raw export; write output to a new file rather than overwriting.
