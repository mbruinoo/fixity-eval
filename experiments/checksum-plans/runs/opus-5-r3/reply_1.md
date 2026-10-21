Below is a dependency‑free Python 3 script (`standardize_inventory.py`). It reads a messy 4‑column TSV, normalizes each field, derives machine‑readable date ranges, flags rows that need human review, and writes a clean TSV plus an optional report and review file.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
standardize_inventory.py — clean and standardize a museum inventory TSV.

INPUT  (tab-separated, header row matched loosely by name, or positional with --no-header)
    date | title | object number | link

OUTPUT (tab-separated)
    date_display        cleaned curatorial date text ("ca. 1875", "19th century")
    date_start          ISO YYYY-MM-DD earliest possible day ('' = open/unknown)
    date_end            ISO YYYY-MM-DD latest possible day   ('' = open/unknown)
    date_qualifier      exact | circa | before | after | century | decade | range | unknown
    title               whitespace/unicode-normalized title ('[Untitled]' if empty)
    object_number       normalized accession number
    object_number_sort  zero-padded natural-sort key (digits -> 8 digits)
    link                normalized absolute URL
    flags               ';'-separated review codes (see FLAGS below)

FLAGS
    DATE_UNKNOWN DATE_EMPTY DATE_FUZZY DATE_UNPARSED DATE_UNCERTAIN DATE_BCE
    DATE_REVERSED DATE_FUTURE
    TITLE_EMPTY TITLE_ALLCAPS TITLE_HTML TITLE_TRUNCATED
    OBJNUM_EMPTY OBJNUM_UNUSUAL OBJNUM_DUPLICATE
    LINK_EMPTY LINK_INVALID LINK_NONHTTP LINK_HTTP LINK_SCHEME_ADDED
    LINK_TRACKING_REMOVED LINK_MULTIPLE LINK_DUPLICATE

Examples
    python3 standardize_inventory.py raw.tsv -o clean.tsv --report report.txt
    python3 standardize_inventory.py raw.tsv -o clean.tsv --review needs_review.tsv \
            --circa-years 5 --fix-caps --sort objnum --keep-original
    python3 standardize_inventory.py --selftest
"""

from __future__ import annotations

import argparse
import calendar
import csv
import html
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from datetime import date as _date
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

VERSION = "1.0"
THIS_YEAR = _date.today().year

# ----------------------------------------------------------------------------
# Column detection
# ----------------------------------------------------------------------------

ALIASES = {
    "date": {"date", "dates", "dated", "datecreated", "datemade", "objectdate",
             "creationdate", "daterange", "year", "years", "dateofwork"},
    "title": {"title", "titles", "objecttitle", "objectname", "worktitle",
              "name", "caption"},
    "object_number": {"objectnumber", "objectno", "objectnum", "objno",
                      "accessionnumber", "accessionno", "accessionnum", "accno",
                      "accession", "inventorynumber", "inventoryno", "invno",
                      "idnumber", "objectid", "catalognumber", "catno"},
    "link": {"link", "links", "url", "urls", "uri", "weblink", "webaddress",
             "permalink", "objecturl", "collectionurl", "href"},
}
POSITIONAL = ["date", "title", "object_number", "link"]


def _hkey(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def detect_columns(header):
    """Return {canonical_name: index} or None if the row isn't a header."""
    found = {}
    for i, cell in enumerate(header):
        k = _hkey(cell)
        for canon, names in ALIASES.items():
            if k in names and canon not in found:
                found[canon] = i
    return found if len(found) >= 2 else None


# ----------------------------------------------------------------------------
# Generic text normalization
# ----------------------------------------------------------------------------

ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff"), None)
DASH_MAP = {ord(c): "-" for c in "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"}
QUOTE_MAP = {
    ord("\u2018"): "'", ord("\u2019"): "'", ord("\u201a"): "'", ord("\u201b"): "'",
    ord("\u2032"): "'", ord("\u201c"): '"', ord("\u201d"): '"', ord("\u201e"): '"',
    ord("\u2033"): '"',
}
TAG_RE = re.compile(r"<[^>]{1,80}>")


def norm_text(s) -> str:
    """NFC, drop control/zero-width chars, collapse all whitespace, strip."""
    if s is None:
        return ""
    s = unicodedata.normalize("NFC", str(s))
    s = s.translate(ZERO_WIDTH).replace("\u00a0", " ")
    s = "".join(ch for ch in s if ch in "\t\n\r" or unicodedata.category(ch)[0] != "C")
    return re.sub(r"\s+", " ", s).strip()


def tsv_safe(s: str) -> str:
    """Guarantee a value can never break the TSV grid."""
    return (s or "").replace("\t", " ").replace("\r", " ").replace("\n", " ")


# ----------------------------------------------------------------------------
# Dates
# ----------------------------------------------------------------------------

@dataclass
class DateInfo:
    display: str = ""
    start: str = ""
    end: str = ""
    qualifier: str = "unknown"
    flags: list = field(default_factory=list)


MONTHS = {}
for _i, _m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"], 1):
    MONTHS[_m] = _i
    MONTHS[_m[:3]] = _i
MONTHS["sept"] = 9

NO_DATE_RE = re.compile(
    r"^(n\.?\s*d\.?|no date|not dated|undated|date unknown|unknown|unkn\.?|"
    r"none|null|n/?a|-+|\?+|\.+)$", re.I)

ORD = r"(\d{1,2})(?:st|nd|rd|th)?"
PART = r"(early|mid(?:dle)?|late|first half|second half|1st half|2nd half|turn of the)"
CENT = r"(?:centuries|century|cent\.?|c\.)"
CENTURY_RE = re.compile(
    rf"^(?:{PART}\s*(?:-|\s|of\s+the\s+)?\s*)?{ORD}\s*[-\s]*{CENT}\s*(bce?|ce|ad)?$")
CENTURY_RANGE_RE = re.compile(
    rf"^{ORD}\s*(?:-|to)\s*{ORD}\s*{CENT}\s*(bce?|ce|ad)?$")
DECADE_RE = re.compile(r"^(\d{3})0\s*'?s$")
PARTIAL_DECADE_RE = re.compile(r"^(\d{3})[-_x]$", re.I)
ISO_RE = re.compile(r"^(\d{3,4})(?:-(\d{1,2})(?:-(\d{1,2}))?)?$")
TEXT_DMY = re.compile(r"^(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]+)\.?,?\s+(\d{3,4})$")
TEXT_MDY = re.compile(r"^([a-z]+)\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{3,4})$")
TEXT_MY = re.compile(r"^([a-z]+)\.?,?\s+(\d{3,4})$")
NUM_SLASH = re.compile(r"^(\d{1,2})[/.](\d{1,2})[/.](\d{4})$")
CIRCA_RE = re.compile(r"\b(?:circa|cca|abt|approx(?:imately)?|about|around|ca|c)\b\.?", re.I)
BEFORE_RE = re.compile(r"\b(?:before|prior to|ante|pre|by|not after|b\.)\b-?", re.I)
AFTER_RE = re.compile(r"\b(?:after|post|not before|a\.)\b-?", re.I)
RANGE_SPLIT_RE = re.compile(r"\s*(?:--|-|/|\bto\b|\bthrough\b|\bor\b)\s*")


def _days_in_month(y: int, m: int) -> int:
    return calendar.monthrange(y if y > 0 else 2000, m)[1]


def _iso(y: int, m=None, d=None, end=False) -> str:
    if m is None:
        m, d = (12, 31) if end else (1, 1)
    elif d is None:
        d = _days_in_month(y, m) if end else 1
    m = min(max(int(m), 1), 12)
    d = min(max(int(d), 1), _days_in_month(y, m))
    return f"{y:05d}-{m:02d}-{d:02d}" if y < 0 else f"{y:04d}-{m:02d}-{d:02d}"


def _shift_year(iso_str: str, delta: int, end: bool) -> str:
    if not iso_str:
        return ""
    sign = -1 if iso_str.startswith("-") else 1
    y = sign * int(iso_str.lstrip("-").split("-")[0])
    return _iso(y + delta, end=end)


def _century_span(n: int, part=None, era=None):
    if era and era.lower().startswith("b"):
        start, end = -(n * 100 - 1), -((n - 1) * 100)
    else:
        start, end = (n - 1) * 100, (n - 1) * 100 + 99
    if part:
        p = part.lower().replace("middle", "mid")
        s0, e0 = start, end
        if p == "early":
            end = s0 + 32
        elif p == "mid":
            start, end = s0 + 33, s0 + 66
        elif p == "late":
            start = e0 - 32
        elif p in ("first half", "1st half"):
            end = s0 + 49
        elif p in ("second half", "2nd half"):
            start = e0 - 49
        elif p == "turn of the":
            start, end = s0 - 10, s0 + 10
    return start, end


def _parse_core(t: str, dayfirst: bool, depth: int = 0):
    """Return (start_iso, end_iso, qualifier, flags) for a qualifier-free string."""
    flags = []
    low = t.strip().lower()
    if not low:
        return "", "", "unknown", ["DATE_EMPTY"]

    m = CENTURY_RANGE_RE.match(low)
    if m:
        a, b, era = int(m.group(1)), int(m.group(2)), m.group(3)
        s, _ = _century_span(a, None, era)
        _, e = _century_span(b, None, era)
        if era and era.startswith("b"):
            flags.append("DATE_BCE")
        return _iso(s), _iso(e, end=True), "century", flags

    m = CENTURY_RE.match(low)
    if m:
        part, n, era = m.group(1), int(m.group(2)), m.group(3)
        s, e = _century_span(n, part, era)
        if era and era.startswith("b"):
            flags.append("DATE_BCE")
        return _iso(s), _iso(e, end=True), "century", flags

    m = DECADE_RE.match(low) or PARTIAL_DECADE_RE.match(low)
    if m:
        base = int(m.group(1)) * 10
        return _iso(base), _iso(base + 9, end=True), "decade", flags

    m = NUM_SLASH.match(low)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        mm, dd = (b, a) if dayfirst or a > 12 else (a, b)
        if 1 <= mm <= 12 and 1 <= dd <= 31:
            return _iso(y, mm, dd), _iso(y, mm, dd), "exact", flags

    m = ISO_RE.match(low)
    if m:
        y = int(m.group(1))
        mo = int(m.group(2)) if m.group(2) else None
        d = int(m.group(3)) if m.group(3) else None
        if mo is None or 1 <= mo <= 12:
            if y > THIS_YEAR + 1:
                flags.append("DATE_FUTURE")
            return _iso(y, mo, d), _iso(y, mo, d, end=True), "exact", flags

    for rx, order in ((TEXT_DMY, "dmy"), (TEXT_MDY, "mdy"), (TEXT_MY, "my")):
        m = rx.match(low)
        if not m:
            continue
        if order == "dmy":
            d, name, y = int(m.group(1)), m.group(2), int(m.group(3))
            mo = MONTHS.get(name)
            if mo:
                return _iso(y, mo, d), _iso(y, mo, d), "exact", flags
        elif order == "mdy":
            name, d, y = m.group(1), int(m.group(2)), int(m.group(3))
            mo = MONTHS.get(name)
            if mo:
                return _iso(y, mo, d), _iso(y, mo, d), "exact", flags
        else:
            name, y = m.group(1), int(m.group(2))
            mo = MONTHS.get(name)
            if mo:
                return _iso(y, mo), _iso(y, mo, end=True), "exact", flags

    if depth == 0:
        parts = RANGE_SPLIT_RE.split(low, maxsplit=1)
        if len(parts) == 2 and parts[0] and parts[1]:
            left, right = parts
            ls, le, lq, lf = _parse_core(left, dayfirst, depth + 1)
            if re.fullmatch(r"\d{1,2}", right) and ls:
                ly = int(ls.lstrip("-").split("-")[0])
                ry = (ly // 100) * 100 + int(right) if len(right) == 2 else \
                     (ly // 10) * 10 + int(right)
                if ry < ly:
                    ry += 100 if len(right) == 2 else 10
                return ls, _iso(ry, end=True), "range", lf + flags
            rs, re_, rq, rf = _parse_core(right, dayfirst, depth + 1)
            if ls and re_:
                return ls, re_, "range", sorted(set(lf + rf + flags))

    years = [int(y) for y in re.findall(r"\b(\d{3,4})\b", low)
             if 100 <= int(y) <= THIS_YEAR + 1]
    if years:
        flags.append("DATE_FUZZY")
        return _iso(min(years)), _iso(max(years), end=True), \
            ("range" if len(set(years)) > 1 else "exact"), flags

    return "", "", "unknown", ["DATE_UNPARSED"]


def canon_display(s: str) -> str:
    s = norm_text(s).translate(QUOTE_MAP)
    s = re.sub(r"(?<![\w])(?:circa|ca|c)\.?\s*(?=\d)", "ca. ", s, flags=re.I)
    s = re.sub(r"\bn\.?\s*d\.?$", "n.d.", s, flags=re.I)
    if re.fullmatch(r"\d{3,4}\s*[-\u2013]\s*\d{1,4}", s):
        s = re.sub(r"\s*[-\u2013]\s*", "\u2013", s)
    return s.strip(" ,;")


def parse_date(raw, circa_years: int = 5, dayfirst: bool = False) -> DateInfo:
    src = norm_text(raw)
    display = canon_display(src)
    t = src.translate(DASH_MAP).translate(QUOTE_MAP).strip(" .,;:")
    low = t.lower()

    if not low:
        return DateInfo("", "", "", "unknown", ["DATE_EMPTY"])
    if NO_DATE_RE.match(low):
        return DateInfo(display or "n.d.", "", "", "unknown", ["DATE_UNKNOWN"])

    flags = []
    if "?" in t or re.search(r"\b(probably|possibly|perhaps|uncertain)\b", low):
        flags.append("DATE_UNCERTAIN")
    t = t.replace("?", " ")
    t = re.sub(r"\((?:[^)]*)\)", " ", t)          # drop parenthetical asides
    t = re.sub(r"\b(probably|possibly|perhaps|uncertain|dated|made|created|"
               r"executed|published|printed|designed|cast)\b", " ", t, flags=re.I)

    qualifier_override = None
    if BEFORE_RE.search(t) and not CENTURY_RE.match(t.lower().strip()):
        qualifier_override = "before"
        t = BEFORE_RE.sub(" ", t)
    elif AFTER_RE.search(t) and not CENTURY_RE.match(t.lower().strip()):
        qualifier_override = "after"
        t = AFTER_RE.sub(" ", t)

    is_circa = False
    stripped = CIRCA_RE.sub(" ", t)
    if stripped != t and not re.search(CENT, t.lower()):
        is_circa, t = True, stripped

    t = re.sub(r"\s+", " ", t).strip(" .,;:-")
    start, end, qual, core_flags = _parse_core(t, dayfirst)
    flags += core_flags

    if is_circa and start:
        start = _shift_year(start, -circa_years, end=False)
        end = _shift_year(end, +circa_years, end=True)
        qual = "circa"
    if qualifier_override == "before" and end:
        start, qual = "", "before"
    elif qualifier_override == "after" and start:
        end, qual = "", "after"

    if start and end and start > end:
        start, end = end, start
        flags.append("DATE_REVERSED")

    return DateInfo(display, start, end, qual, sorted(set(flags)))


# ----------------------------------------------------------------------------
# Titles
# ----------------------------------------------------------------------------

SMALL_WORDS = {"a", "an", "and", "as", "at", "but", "by", "for", "from", "in",
               "into", "nor", "of", "on", "onto", "or", "over", "the", "to",
               "up", "with", "via", "de", "del", "la", "le", "les", "du", "des",
               "van", "von", "der", "den", "het", "di", "da", "y"}
ROMAN_RE = re.compile(r"^[IVXLCDM]+$")
UNTITLED_RE = re.compile(r"^[\[\(<]?\s*(untitled|no title|without title)\s*[\]\)>]?$", re.I)


def smart_title(s: str) -> str:
    words = s.split(" ")
    out = []
    for i, w in enumerate(words):
        core = w.strip("([{\"'")
        if ROMAN_RE.match(core) or any(ch.isdigit() for ch in core):
            out.append(w)
            continue
        parts = re.split(r"([-'\u2019])", w.lower())
        rebuilt = "".join(p if p in "-'\u2019" else p.capitalize() for p in parts)
        if 0 < i < len(words) - 1 and w.lower() in SMALL_WORDS:
            rebuilt = w.lower()
        out.append(rebuilt)
    return " ".join(out)


def clean_title(raw, fix_caps: bool = False):
    flags = []
    s = norm_text(raw)
    if TAG_RE.search(s):
        s = norm_text(html.unescape(TAG_RE.sub(" ", s)))
        flags.append("TITLE_HTML")
    s = s.translate(QUOTE_MAP)
    s = re.sub(r"\s*\u2026\s*", "...", s)
    s = re.sub(r"\s+([,;:.!?])", r"\1", s)
    s = re.sub(r"\(\s+|\s+\)", lambda m: m.group().strip(), s)
    if len(s) > 1 and s[0] == s[-1] == '"':
        s = s[1:-1].strip()
    if not s:
        return "[Untitled]", ["TITLE_EMPTY"]
    if UNTITLED_RE.match(s):
        return "[Untitled]", flags
    letters = [c for c in s if c.isalpha()]
    if len(letters) >= 4 and all(c.isupper() for c in letters):
        flags.append("TITLE_ALLCAPS")
        if fix_caps:
            s = smart_title(s)
    if s.endswith(("...", " -", "\u2013")) or len(s) > 300:
        flags.append("TITLE_TRUNCATED")
    return s, flags


# ----------------------------------------------------------------------------
# Object numbers
# ----------------------------------------------------------------------------

OBJNUM_OK_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.\-/_ ()]*$")


def clean_objnum(raw, case: str = "keep"):
    flags = []
    s = norm_text(raw).translate(DASH_MAP).translate(QUOTE_MAP)
    s = s.strip(" .,;:")
    s = re.sub(r"\s*([./\-])\s*", r"\1", s)   # "1975. 1. 23" -> "1975.1.23"
    s = re.sub(r"\s+", " ", s)
    if not s:
        return "", "", ["OBJNUM_EMPTY"]
    if case == "upper":
        s = s.upper()
    elif case == "lower":
        s = s.lower()
    if not OBJNUM_OK_RE.match(s):
        flags.append("OBJNUM_UNUSUAL")
    sort_key = re.sub(r"\d+", lambda m: m.group().zfill(8), s.lower())
    return s, sort_key, flags


# ----------------------------------------------------------------------------
# Links
# ----------------------------------------------------------------------------

TRACKING = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
            "utm_id", "utm_name", "gclid", "fbclid", "msclkid", "yclid", "mc_cid",
            "mc_eid", "igshid", "ref_src", "_ga", "_gl", "wt.mc_id", "s_kwcid"}
BARE_HOST_RE = re.compile(r"^(www\.|[a-z0-9][a-z0-9\-]*\.[a-z]{2,}(?:[/:?]|$))", re.I)


def clean_link(raw, keep_tracking: bool = False):
    flags = []
    s = norm_text(raw)
    if not s:
        return "", ["LINK_EMPTY"]
    s = html.unescape(s).strip("<>\"' ")

    parts = re.split(r"[\s;,|]+(?=https?://|www\.)", s)
    if len(parts) > 1:
        flags.append("LINK_MULTIPLE")
        s = parts[0]
    s = s.rstrip(".,;")
    while s.endswith(")") and s.count("(") < s.count(")"):
        s = s[:-1]

    if re.match(r"^(doi|ark|urn|hdl|info):", s, re.I):
        return s, flags + ["LINK_NONHTTP"]
    if not re.match(r"^[a-z][a-z0-9+.\-]*://", s, re.I):
        if s.startswith("//"):
            s = "https:" + s
        elif BARE_HOST_RE.match(s):
            s = "https://" + s
            flags.append("LINK_SCHEME_ADDED")
        else:
            return s, flags + ["LINK_INVALID"]

    try:
        sp = urlsplit(s)
    except ValueError:
        return s, flags + ["LINK_INVALID"]

    scheme, netloc = sp.scheme.lower(), sp.netloc.lower()
    if scheme == "http":
        flags.append("LINK_HTTP")
    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    if netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]

    query = sp.query
    if query and not keep_tracking:
        kept = [(k, v) for k, v in parse_qsl(query, keep_blank_values=True)
                if k.lower() not in TRACKING]
        new_q = urlencode(kept)
        if new_q != query:
            flags.append("LINK_TRACKING_REMOVED")
        query = new_q

    out = urlunsplit((scheme, netloc, sp.path, query, sp.fragment))
    if scheme not in ("http", "https") or "." not in netloc:
        flags.append("LINK_INVALID")
    return out, flags


# ----------------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------------

OUT_COLUMNS = ["date_display", "date_start", "date_end", "date_qualifier",
               "title", "object_number", "object_number_sort", "link", "flags"]
ORIG_COLUMNS = ["date_original", "title_original",
                "object_number_original", "link_original"]


def process_rows(rows, colmap, args):
    out = []
    for lineno, row in rows:
        def get(name):
            i = colmap.get(name)
            return row[i] if i is not None and i < len(row) else ""

        raw_date, raw_title = get("date"), get("title")
        raw_obj, raw_link = get("object_number"), get("link")

        d = parse_date(raw_date, args.circa_years, args.dayfirst)
        title, tflags = clean_title(raw_title, args.fix_caps)
        objnum, objsort, oflags = clean_objnum(raw_obj, args.objnum_case)
        link, lflags = clean_link(raw_link, args.keep_tracking)

        rec = {
            "_line": lineno,
            "date_display": d.display,
            "date_start": d.start,
            "date_end": d.end,
            "date_qualifier": d.qualifier,
            "title": title,
            "object_number": objnum,
            "object_number_sort": objsort,
            "link": link,
            "flags": d.flags + tflags + oflags + lflags,
            "date_original": norm_text(raw_date),
            "title_original": norm_text(raw_title),
            "object_number_original": norm_text(raw_obj),
            "link_original": norm_text(raw_link),
        }
        out.append(rec)

    # Second pass: duplicates
    obj_counts = Counter(r["object_number"] for r in out if r["object_number"])
    link_counts = Counter(r["link"] for r in out if r["link"])
    for r in out:
        if obj_counts.get(r["object_number"], 0) > 1:
            r["flags"].append("OBJNUM_DUPLICATE")
        if link_counts.get(r["link"], 0) > 1:
            r["flags"].append("LINK_DUPLICATE")
        r["flags"] = ";".join(sorted(set(r["flags"])))
    return out, obj_counts, link_counts


def write_tsv(path, records, columns, bom=False):
    stream = open(path, "w", encoding="utf-8-sig" if bom else "utf-8",
                  newline="") if path else sys.stdout
    try:
        stream.write("\t".join(columns) + "\n")
        for r in records:
            stream.write("\t".join(tsv_safe(str(r.get(c, ""))) for c in columns) + "\n")
    finally:
        if path:
            stream.close()


def build_report(records, obj_counts, link_counts, src):
    flag_counter = Counter()
    for r in records:
        for f in filter(None, r["flags"].split(";")):
            flag_counter[f] += 1
    years = [int(r["date_start"].lstrip("-").split("-")[0])
             for r in records if r["date_start"]]
    lines = [
        f"standardize_inventory v{VERSION}",
        f"source: {src}",
        f"rows processed: {len(records)}",
        f"rows flagged:   {sum(1 for r in records if r['flags'])}",
        "",
        "-- flags --",
    ]
    lines += [f"{n:7d}  {f}" for f, n in flag_counter.most_common()] or ["   none"]
    lines += ["", "-- date qualifiers --"]
    qc = Counter(r["date_qualifier"] for r in records)
    lines += [f"{n:7d}  {q}" for q, n in qc.most_common()]
    if years:
        lines += ["", f"date coverage: {min(years)} – {max(years)}"]
    unparsed = [r for r in records if "DATE_UNPARSED" in r["flags"]][:15]
    if unparsed:
        lines += ["", "-- unparsed dates (sample) --"]
        lines += [f"  line {r['_line']}: {r['date_original']!r}" for r in unparsed]
    dups = [(k, v) for k, v in obj_counts.items() if v > 1][:20]
    if dups:
        lines += ["", "-- duplicate object numbers (sample) --"]
        lines += [f"  {k} ×{v}" for k, v in dups]
    return "\n".join(lines) + "\n"


def selftest():
    cases = [
        ("1875", "1875-01-01", "1875-12-31", "exact"),
        ("c. 1875", "1870-01-01", "1880-12-31", "circa"),
        ("1875-80", "1875-01-01", "1880-12-31", "range"),
        ("1875–1880", "1875-01-01", "1880-12-31", "range"),
        ("19th century", "1800-01-01", "1899-12-31", "century"),
        ("late 19th century", "1867-01-01", "1899-12-31", "century"),
        ("mid-19th century", "1833-01-01", "1866-12-31", "century"),
        ("18th-19th century", "1700-01-01", "1899-12-31", "century"),
        ("1870s", "1870-01-01", "1879-12-31", "decade"),
        ("March 12, 1875", "1875-03-12", "1875-03-12", "exact"),
        ("12 March 1875", "1875-03-12", "1875-03-12", "exact"),
        ("1875-03", "1875-03-01", "1875-03-31", "exact"),
        ("before 1900", "", "1900-12-31", "before"),
        ("after 1900", "1900-01-01", "", "after"),
        ("n.d.", "", "", "unknown"),
        ("", "", "", "unknown"),
    ]
    bad = 0
    for raw, s, e, q in cases:
        d = parse_date(raw, circa_years=5)
        ok = (d.start, d.end, d.qualifier) == (s, e, q)
        bad += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {raw!r:22} -> "
              f"{d.start!r} {d.end!r} {d.qualifier} {d.flags}")
    assert clean_objnum("1975. 1. 23a-b")[0] == "1975.1.23a-b"
    assert clean_link("www.museum.org/obj/1?utm_source=x")[0] == "https://www.museum.org/obj/1"
    assert clean_title("  THE   BLUE  VASE ", fix_caps=True)[0] == "The Blue Vase"
    assert clean_title("[ untitled ]")[0] == "[Untitled]"
    print("\n%d failure(s)" % bad)
    return 1 if bad else 0


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Standardize a 4-column museum inventory TSV "
                    "(date, title, object number, link).")
    p.add_argument("input", nargs="?", help="input .tsv (default: stdin)")
    p.add_argument("-o", "--output", help="output .tsv (default: stdout)")
    p.add_argument("--report", help="write a summary report to this file")
    p.add_argument("--review", help="write only flagged rows to this file")
    p.add_argument("--delimiter", default="\t",
                   help="input delimiter (default: tab; use ',' for CSV)")
    p.add_argument("--no-header", action="store_true",
                   help="input has no header; assume date,title,object number,link")
    p.add_argument("--no-quotes", action="store_true",
                   help="treat quote characters as literal text when reading")
    p.add_argument("--encoding", default="utf-8-sig")
    p.add_argument("--circa-years", type=int, default=5,
                   help="± years applied to 'ca.' dates (default: 5)")
    p.add_argument("--dayfirst", action="store_true",
                   help="read 3/4/1875 as D/M/Y instead of M/D/Y")
    p.add_argument("--fix-caps", action="store_true",
                   help="convert ALL-CAPS titles to title case")
    p.add_argument("--objnum-case", choices=["keep", "upper", "lower"], default="keep")
    p.add_argument("--keep-tracking", action="store_true",
                   help="do not strip utm_*/fbclid/etc. from URLs")
    p.add_argument("--keep-original", action="store_true",
                   help="append the original values as extra columns")
    p.add_argument("--sort", choices=["none", "objnum", "date", "title"], default="none")
    p.add_argument("--excel-bom", action="store_true",
                   help="write a UTF-8 BOM (helps Excel open the file correctly)")
    p.add_argument("--selftest", action="store_true", help="run built-in tests and exit")
    p.add_argument("--version", action="version", version=VERSION)
    args = p.parse_args(argv)

    if args.selftest:
        return selftest()

    fh = open(args.input, "r", encoding=args.encoding, newline="") if args.input \
        else sys.stdin
    try:
        kw = dict(delimiter=args.delimiter)
        if args.no_quotes:
            kw.update(quoting=csv.QUOTE_NONE, quotechar=None)
        reader = csv.reader(fh, **kw)
        raw_rows = [r for r in reader]
    finally:
        if args.input:
            fh.close()

    raw_rows = [r for r in raw_rows if any(c.strip() for c in r)]
    if not raw_rows:
        sys.exit("error: no data rows found")

    if args.no_header:
        colmap = {name: i for i, name in enumerate(POSITIONAL)}
        body = list(enumerate(raw_rows, start=1))
    else:
        colmap = detect_columns(raw_rows[0])
        if colmap is None:
            print("warning: header not recognized; using positional columns "
                  "(date, title, object number, link)", file=sys.stderr)
            colmap = {name: i for i, name in enumerate(POSITIONAL)}
            body = list(enumerate(raw_rows, start=1))
        else:
            missing = [c for c in POSITIONAL if c not in colmap]
            if missing:
                print(f"warning: columns not found in header: {', '.join(missing)}",
                      file=sys.stderr)
            body = list(enumerate(raw_rows[1:], start=2))

    records, obj_counts, link_counts = process_rows(body, colmap, args)

    if args.sort == "objnum":
        records.sort(key=lambda r: (r["object_number_sort"] == "", r["object_number_sort"]))
    elif args.sort == "date":
        records.sort(key=lambda r: (r["date_start"] == "", r["date_start"],
                                    r["object_number_sort"]))
    elif args.sort == "title":
        records.sort(key=lambda r: r["title"].lower())

    columns = OUT_COLUMNS + (ORIG_COLUMNS if args.keep_original else [])
    write_tsv(args.output, records, columns, bom=args.excel_bom)

    if args.review:
        write_tsv(args.review, [r for r in records if r["flags"]],
                  columns, bom=args.excel_bom)

    report = build_report(records, obj_counts, link_counts, args.input or "<stdin>")
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write(report)
    else:
        print(report, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Usage

```bash
# basic clean
python3 standardize_inventory.py raw_inventory.tsv -o clean_inventory.tsv

# full run: report, review file, fix shouting titles, sort by accession number
python3 standardize_inventory.py raw_inventory.tsv \
    -o clean.tsv --review needs_review.tsv --report report.txt \
    --fix-caps --sort objnum --keep-original --excel-bom

# verify the date parser before trusting it on your data
python3 standardize_inventory.py --selftest
```

## What it standardizes

| Column | Treatment |
|---|---|
| **date** | Keeps the curatorial phrasing in `date_display` (lightly canonicalized: `c.1875` → `ca. 1875`) and adds machine-readable `date_start`/`date_end` as full ISO days plus a `date_qualifier`. Handles years, ISO dates, month names, `1875-80`, `1870s`, `19th century`, `late/mid/early/turn of the`, century ranges, `before`/`after`, `ca.` (± `--circa-years`), `n.d.`, BCE, and falls back to extracting any plausible years (`DATE_FUZZY`). |
| **title** | NFC normalization, zero-width/NBSP removal, whitespace collapse, curly→straight quotes, HTML tag/entity stripping, un-wrapping stray quotes, `[Untitled]` canonicalization, optional ALL-CAPS repair that preserves roman numerals and numbers. |
| **object number** | Unicode dash normalization, removal of spaces around `.`/`-`/`/`, optional case folding, plus a `object_number_sort` natural-sort key (digit runs zero-padded to 8) so `1975.2.10` sorts after `1975.2.9`. |
| **link** | Entity decoding, `<>`/quote/trailing-punctuation stripping (parenthesis-aware, so Wikipedia URLs survive), scheme inference for bare hosts, lowercased scheme/host, default-port removal, tracking-parameter removal, validation, and detection of multiple URLs crammed into one cell. |

Duplicates of object numbers and links are flagged across the whole file; nothing is deleted or merged automatically.

## Adapting it to your collection

- **Accession format**: tighten `OBJNUM_OK_RE` to your institution's pattern (e.g. `^\d{4}\.\d+(\.\d+)?[a-z]?(-[a-z])?$`) so malformed numbers get flagged instead of silently passing.
- **Circa width**: registrars often use ±5 for `ca.` on 19th-century material and ±25 for older works — set with `--circa-years`.
- **Century thirds**: `_century_span` uses early = first third, mid = middle third, late = final third; change there if your style guide uses ±30 or quarters.
- **Open bounds**: `before 1900` yields `('', 1900-12-31)` and `after 1900` yields `(1900-01-01, '')`, both inclusive of the named year. If your CMS expects exclusive bounds or a hard floor/ceiling, adjust in `parse_date`.
- **Link checking**: deliberately omitted (no network calls). If you need it, add an optional pass using `urllib.request` with HEAD requests, a timeout, and a delay between hosts.

Always keep the raw export — run with `--keep-original` so every transformation stays auditable against the source.
