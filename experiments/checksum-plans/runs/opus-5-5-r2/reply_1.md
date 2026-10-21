# Museum Inventory Standardizer

This Python 3.8+ script cleans a 4‑column museum inventory TSV (date, title, object number, link). It uses only the standard library. It writes two files:

1. A **standardized TSV** with a consistent header.
2. An **issues report** that lists every value needing human review.

The script never discards data. If it can't confidently parse a value, it keeps the cleaned original and flags it in the report.

## Standardization rules

| Column | What it does |
|---|---|
| **date** | Converts dates to one convention: `1890-03-04`, `1890-03`, `1890`, `1890/1895` (range), `ca. 1890`, `1890?`, `1890s`, `late 19th century`, `500 BCE`, `before 1900`, `n.d.`. Handles month names, numeric dates (US or day-first), shorthand ranges (`1890-95`), BC/BCE/AD/CE, Excel float/serial artifacts. |
| **title** | Normalizes Unicode and whitespace, removes invisible characters, strips wrapping quotes and stray trailing punctuation, and converts ALL‑CAPS titles to title case (preserving Roman numerals and small words). |
| **object_number** | Uppercases, removes spaces around separators (`1985 . 12 . 3` → `1985.12.3`), optionally unifies separators, detects Excel damage (`1.98E+05`, trailing `.0`), and flags missing and **duplicate** numbers. |
| **link** | Extracts Excel `=HYPERLINK()` formulas, adds a missing `https://`, lowercases scheme and host, removes default ports and tracking parameters (`utm_*`, `fbclid`, …), optionally forces HTTPS, and validates structure. |

## The script: `standardize_inventory.py`

```python
#!/usr/bin/env python3
"""
standardize_inventory.py — Clean and standardize a museum inventory TSV.

Expected columns (any order if a header row is present):
    date, title, object number, link

Usage:
    python standardize_inventory.py inventory.tsv
    python standardize_inventory.py inventory.tsv -o clean.tsv --dayfirst --force-https
    python standardize_inventory.py inventory.tsv --object-separator . --sort-by-object-number

Outputs:
    <input>_standardized.tsv   cleaned data (or the path given with -o; "-" = stdout)
    <output>_issues.tsv        rows/values needing review (disable with --report none)
"""

import argparse
import csv
import datetime as dt
import io
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

OUTPUT_HEADER = ["date", "title", "object_number", "link"]

HEADER_ALIASES = {
    "date": {"date", "dates", "date made", "creation date", "object date",
             "production date", "year", "dated"},
    "title": {"title", "name", "object name", "object title", "work title",
              "description"},
    "object_number": {"object number", "object no", "obj no", "object num",
                      "accession number", "accession no", "accession",
                      "inventory number", "inventory no", "catalog number",
                      "catalogue number", "catalog no", "object id", "id",
                      "number", "objectnumber", "object_number"},
    "link": {"link", "url", "uri", "web link", "weblink", "permalink",
             "web address", "online record", "href"},
}

# ---------------------------------------------------------------------------
# Generic text cleaning
# ---------------------------------------------------------------------------

_INVISIBLE = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff\u00ad"), None)


def clean_text(value):
    """Unicode-normalize, remove invisible chars, collapse all whitespace."""
    if value is None:
        return ""
    s = unicodedata.normalize("NFC", value)
    s = s.translate(_INVISIBLE)
    s = s.replace("\u00a0", " ").replace("\u202f", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------

MONTH_NAMES = ["january", "february", "march", "april", "may", "june", "july",
               "august", "september", "october", "november", "december"]

UNDATED_RE = re.compile(
    r"^(n\.?\s?d\.?|undated|unknown|unk\.?|no date|not dated|date unknown|"
    r"\?+|-+|x+)$")
CIRCA_RE = re.compile(
    r"^(circa|approximately|approx\.?|about|around|ca\.?|c\.|c(?=\s|\d)|~)\s*")
ERA_RE = re.compile(r"\s*(?<![a-z])(bce|bc|ce|ad)$")
ERA_PREFIX_RE = re.compile(r"^(ad|ce)\s+")


def month_from_name(word):
    w = word.lower().rstrip(".")
    if len(w) < 3:
        return None
    for i, name in enumerate(MONTH_NAMES, 1):
        if name.startswith(w):
            return i
    return None


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _point(y, m=None, d=None, bce=False):
    return {"kind": "point", "y": y, "m": m, "d": d, "bce": bce,
            "sort": -y if bce else y}


def _parse_single(t, default_era, dayfirst, notes):
    """Parse a single (non-range) date expression into a dict, or None."""
    t = t.strip()
    era = default_era
    m = ERA_RE.search(t)
    if m:
        era, t = m.group(1), t[:m.start()].strip()
    m = ERA_PREFIX_RE.match(t)
    if m:
        era, t = m.group(1), t[m.end():].strip()
    bce = era in ("bc", "bce")
    has_era = era is not None

    # Centuries: "19th century", "late 19th c.", "5th century bce"
    m = re.fullmatch(r"(?:the\s+)?(?:(early|mid|late)[\s-]+)?(\d{1,2})"
                     r"(?:st|nd|rd|th)[\s-]*(?:century|cent\.?|c\.?)", t)
    if m:
        n = int(m.group(2))
        if n == 0:
            return None
        return {"kind": "century", "n": n, "qual": m.group(1), "bce": bce,
                "sort": -(n * 100) if bce else (n - 1) * 100}

    # Decades: "1890s", "1890's", "early 1890s"
    m = re.fullmatch(r"(?:the\s+)?(?:(early|mid|late)[\s-]+)?(\d{3}0)'?s", t)
    if m and not bce:
        y = int(m.group(2))
        return {"kind": "decade", "y": y, "qual": m.group(1), "bce": False,
                "sort": y}

    y = mo = d = None
    if re.fullmatch(r"\d{4}", t) or (has_era and re.fullmatch(r"\d{1,4}", t)):
        y = int(t)
    elif m := re.fullmatch(r"(\d{4})[-/.](\d{1,2})", t):
        y, mo = int(m.group(1)), int(m.group(2))
    elif m := re.fullmatch(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", t):
        y, mo, d = map(int, m.groups())
    elif m := re.fullmatch(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})", t):
        a, b, y = map(int, m.groups())
        if a > 12 >= b:
            d, mo = a, b
        elif b > 12 >= a:
            mo, d = a, b
        else:
            mo, d = (b, a) if dayfirst else (a, b)
            if a != b:
                notes.append(("warning", "ambiguous day/month order; assumed "
                              + ("DD/MM/YYYY" if dayfirst else "MM/DD/YYYY")))
    elif m := re.fullmatch(r"(\d{1,2})[-/.](\d{4})", t):
        mo, y = int(m.group(1)), int(m.group(2))
    elif m := re.fullmatch(r"([a-z]+)\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})", t):
        mo, d, y = month_from_name(m.group(1)), int(m.group(2)), int(m.group(3))
    elif m := re.fullmatch(r"(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?([a-z]+)\.?,?\s+(\d{4})", t):
        d, mo, y = int(m.group(1)), month_from_name(m.group(2)), int(m.group(3))
    elif m := re.fullmatch(r"([a-z]+)\.?,?\s+(\d{4})", t):
        mo, y = month_from_name(m.group(1)), int(m.group(2))
        if mo is None:
            return None
    else:
        return None

    if (mo is not None and not 1 <= mo <= 12) or (bce and mo):
        return None
    if d is not None:
        if mo is None:
            return None
        try:
            dt.date(y, mo, d)
        except ValueError:
            return None
    return _point(y, mo, d, bce)


def _split_range(t):
    m = re.fullmatch(r"(?:between\s+)?(.+?)\s+(?:to|through|thru|until|till|and)\s+(.+)", t)
    if m:
        return m.group(1), m.group(2)
    for sep in (r"\s+-\s+", r"\s*-\s*", r"\s*/\s*"):
        parts = re.split(sep, t)
        if len(parts) == 2 and all(p.strip() for p in parts):
            return parts[0], parts[1]
    return None


def _render(p, show_ce=False):
    era = " BCE" if p["bce"] else (" CE" if show_ce else "")
    qual = f"{p['qual']} " if p.get("qual") else ""
    if p["kind"] == "century":
        return f"{qual}{ordinal(p['n'])} century{era}"
    if p["kind"] == "decade":
        return f"{qual}{p['y']}s"
    if p["d"]:
        return f"{p['y']:04d}-{p['m']:02d}-{p['d']:02d}"
    if p["m"]:
        return f"{p['y']:04d}-{p['m']:02d}"
    return f"{p['y']}{era}"


def standardize_date(raw, dayfirst=False):
    """Return (standardized_text, notes). Notes are (severity, message)."""
    notes = []
    s = clean_text(raw)
    if not s:
        return "", [("warning", "missing date")]

    t = s.lower()
    t = re.sub(r"[\u2010-\u2015\u2212]", "-", t)          # all dashes -> hyphen
    t = re.sub(r"(?<![a-z])([abc])\.\s?([cde])\.(?:\s?(e)\.)?",  # b.c.e. -> bce
               lambda m: "".join(g for g in m.groups() if g), t)

    m = re.fullmatch(r"\[(.*)\]", t)
    if m:
        t = m.group(1).strip()
        notes.append(("warning", "removed brackets (date was supplied/inferred)"))

    if UNDATED_RE.match(t):
        return "n.d.", notes

    if re.fullmatch(r"\d{4}\.0+", t):                    # Excel float: 1890.0
        t = t.split(".")[0]
    if re.fullmatch(r"\d{5}", t) and 20000 <= int(t) <= 60000:
        converted = dt.date(1899, 12, 30) + dt.timedelta(days=int(t))
        notes.append(("warning", f"interpreted {t} as an Excel serial date"))
        return converted.isoformat(), notes

    uncertain = circa = False
    prefix = ""
    if re.search(r"\s*(\(\?\)|\?)$", t):
        uncertain, t = True, re.sub(r"\s*(\(\?\)|\?)$", "", t)
    m = re.match(r"^(probably|possibly|perhaps)\s+", t)
    if m:
        uncertain, t = True, t[m.end():]
    m = re.match(r"^(before|after|by|not before|not after)\s+", t)
    if m:
        prefix, t = m.group(1) + " ", t[m.end():]
    m = CIRCA_RE.match(t)
    if m:
        circa, t = True, t[m.end():]

    era = None
    m = ERA_RE.search(t)
    if m:
        era, t = m.group(1), t[:m.start()].strip()

    single = _parse_single(t, era, dayfirst, notes)
    if single:
        parts = [single]
    else:
        pieces = _split_range(t)
        if not pieces:
            return s, notes + [("error", "unrecognized date format; left unchanged")]
        a_txt, b_txt = (p.strip() for p in pieces)
        for txt_idx, txt in enumerate((a_txt, b_txt)):
            m = CIRCA_RE.match(txt)
            if m:
                circa = True
                if txt_idx == 0:
                    a_txt = txt[m.end():]
                else:
                    b_txt = txt[m.end():]
        a = _parse_single(a_txt, era, dayfirst, notes)
        if (a and a["kind"] == "point" and not a["m"] and not a["bce"]
                and a["y"] >= 100 and re.fullmatch(r"\d{1,2}", b_txt)):
            width = len(b_txt)                              # shorthand 1890-95
            end = a["y"] - a["y"] % 10 ** width + int(b_txt)
            if end < a["y"]:
                end += 10 ** width
            b = _point(end)
        else:
            b = _parse_single(b_txt, era, dayfirst, notes)
        if not a or not b:
            return s, notes + [("error", "unrecognized date range; left unchanged")]
        if a["sort"] > b["sort"]:
            notes.append(("warning", "date range starts after it ends"))
        parts = [a, b]

    show_ce = len(parts) == 2 and parts[0]["bce"] and not parts[1]["bce"]
    text = "/".join(_render(p, show_ce and i == 1) for i, p in enumerate(parts))
    if circa:
        text = "ca. " + text
    text = prefix + text
    if uncertain:
        text += "?"

    this_year = dt.date.today().year
    if any(p["kind"] == "point" and p["sort"] > this_year for p in parts):
        notes.append(("warning", "date is in the future"))
    return text, notes


# ---------------------------------------------------------------------------
# Titles
# ---------------------------------------------------------------------------

QUOTE_PAIRS = [('"', '"'), ("'", "'"), ("\u201c", "\u201d"),
               ("\u2018", "\u2019"), ("\u00ab", "\u00bb")]
STRAIGHTEN = str.maketrans({"\u201c": '"', "\u201d": '"', "\u201e": '"',
                            "\u2018": "'", "\u2019": "'", "\u201a": "'"})
SMALL_WORDS = {"a", "an", "and", "as", "at", "but", "by", "for", "from", "in",
               "into", "nor", "of", "on", "or", "over", "the", "to", "upon",
               "with", "de", "del", "la", "le", "du", "van", "von", "der"}
ABBREVIATIONS = {"st.", "dr.", "mr.", "mrs.", "ms.", "jr.", "sr.", "co.",
                 "inc.", "ltd.", "no.", "vol.", "etc.", "ca.", "c.", "fig.",
                 "pl.", "esq.", "bros."}
ROMAN_RE = re.compile(r"(?=[MDCLXVI])M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})")


def _cap(part):
    return re.sub(r"^([^a-z]*)([a-z])",
                  lambda m: m.group(1) + m.group(2).upper(), part, count=1)


def smart_title(s):
    words = s.split(" ")
    out = []
    for i, w in enumerate(words):
        bare = re.sub(r"^\W+|\W+$", "", w)
        if bare and ROMAN_RE.fullmatch(bare):
            out.append(w)                                    # keep "II", "XIV"
            continue
        lw = w.lower()
        after_colon = i > 0 and out[-1].endswith((":", "\u2014"))
        if 0 < i < len(words) - 1 and bare.lower() in SMALL_WORDS and not after_colon:
            out.append(lw)
        else:
            out.append("-".join(_cap(p) for p in lw.split("-")))
    return " ".join(out)


def standardize_title(raw, fix_caps=True, straight_quotes=False):
    notes = []
    s = clean_text(raw)
    if not s:
        return "", [("warning", "missing title")]

    for a, b in QUOTE_PAIRS:                                 # "Title" -> Title
        if len(s) >= 2 and s[0] == a and s[-1] == b and a not in s[1:-1] and b not in s[1:-1]:
            s = s[1:-1].strip()
            break
    if straight_quotes:
        s = s.translate(STRAIGHTEN)

    s = re.sub(r"\s+([,;:)\]])", r"\1", s)                  # no space before , ; : )
    s = re.sub(r"([(\[])\s+", r"\1", s)                      # no space after (
    s = re.sub(r"[\s,;:]+$", "", s)                          # trailing junk
    if s.endswith(".") and not s.endswith(".."):
        last = s.split()[-1].lower()
        if last not in ABBREVIATIONS and not re.fullmatch(r"(?:[a-z]\.)+", last):
            s = s[:-1].rstrip()

    if fix_caps and sum(c.isalpha() for c in s) > 3 and s.isupper():
        s = smart_title(s)
        notes.append(("warning", "converted ALL-CAPS title to title case; please verify"))
    return s, notes


# ---------------------------------------------------------------------------
# Object numbers
# ---------------------------------------------------------------------------

def standardize_object_number(raw, separator=None):
    notes = []
    s = clean_text(raw)
    if not s:
        return "", [("error", "missing object number")]
    original = s

    if re.fullmatch(r"\d+(\.\d+)?[eE][+-]?\d+", s):
        return s, [("error", "looks like Excel scientific notation; recover from source")]

    s = s.upper()
    s = re.sub(r"\s*([.\-/:])\s*", r"\1", s)                # "1985 . 12" -> "1985.12"
    s = s.strip(" .-/:")
    if separator is not None:
        s = re.sub(r"(?<=\d)[.\-/](?=\d)", separator, s)

    if re.fullmatch(r"\d+\.0", original):
        notes.append(("warning", "trailing '.0' may be an Excel number artifact"))
    if re.search(r"[^0-9A-Z.\-/: ]", s):
        notes.append(("warning", "contains unusual characters"))
    return s, notes


def natural_key(s):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", s)]


# ---------------------------------------------------------------------------
# Links
# ---------------------------------------------------------------------------

TRACKING_PARAM_RE = re.compile(r"^(utm_\w+|fbclid|gclid|dclid|msclkid|mc_cid|mc_eid|_ga)$", re.I)


def standardize_link(raw, force_https=False):
    notes = []
    s = clean_text(raw)
    if not s:
        return "", [("warning", "missing link")]

    m = re.fullmatch(r'=HYPERLINK\(\s*"([^"]+)".*\)', s, re.I)
    if m:
        s = m.group(1)
        notes.append(("warning", "extracted URL from Excel HYPERLINK formula"))

    s = s.strip("<>\"' ").rstrip(".,;")
    if " " in s:
        s = s.replace(" ", "%20")
        notes.append(("warning", "URL contained spaces; encoded as %20"))

    if not re.match(r"^[a-z][a-z0-9+.\-]*://", s, re.I):
        if re.match(r"^(www\.)?[a-z0-9\-]+(\.[a-z0-9\-]+)+([/?#:]|$)", s, re.I):
            s = "https://" + s
        else:
            return s, notes + [("error", "not a recognizable URL")]

    try:
        parts = urlsplit(s)
        host = parts.hostname
    except ValueError:
        return s, notes + [("error", "malformed URL")]

    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()
    if scheme not in ("http", "https"):
        notes.append(("warning", f"unusual URL scheme '{scheme}'"))
    if force_https and scheme == "http":
        scheme = "https"
    if (scheme == "http" and netloc.endswith(":80")) or (scheme == "https" and netloc.endswith(":443")):
        netloc = netloc.rsplit(":", 1)[0]
    if not host or ("." not in host and host != "localhost"):
        notes.append(("error", "URL has a missing or invalid domain"))

    query = parts.query
    if query:
        pairs = parse_qsl(query, keep_blank_values=True)
        kept = [(k, v) for k, v in pairs if not TRACKING_PARAM_RE.match(k)]
        if len(kept) != len(pairs):
            query = urlencode(kept)

    return urlunsplit((scheme, netloc, parts.path, query, parts.fragment)), notes


# ---------------------------------------------------------------------------
# File handling
# ---------------------------------------------------------------------------

def read_tsv(path, use_quoting=True):
    data = Path(path).read_bytes()
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    reader = csv.reader(io.StringIO(text), delimiter="\t",
                        quoting=csv.QUOTE_MINIMAL if use_quoting else csv.QUOTE_NONE)
    rows = []
    for row in reader:
        rows.append((reader.line_num, row))
    return rows, encoding


def _norm_header(cell):
    return re.sub(r"[\s_\-.#:]+", " ", clean_text(cell).lower()).strip()


def detect_columns(first_row):
    """Return (mapping {field: index}, has_header)."""
    mapping = {}
    for i, cell in enumerate(first_row):
        name = _norm_header(cell)
        for field, aliases in HEADER_ALIASES.items():
            if field not in mapping and name in aliases:
                mapping[field] = i
                break
    if len(mapping) >= 2:
        unused = [i for i in range(len(first_row)) if i not in mapping.values()]
        for field in OUTPUT_HEADER:
            if field not in mapping and unused:
                mapping[field] = unused.pop(0)
        return mapping, True
    return {field: i for i, field in enumerate(OUTPUT_HEADER)}, False


def main():
    ap = argparse.ArgumentParser(description="Standardize a museum inventory TSV "
                                             "(date, title, object number, link).")
    ap.add_argument("input", help="input .tsv file")
    ap.add_argument("-o", "--output", help="output path (default: <input>_standardized.tsv; '-' for stdout)")
    ap.add_argument("-r", "--report", help="issues report path (default: <output>_issues.tsv; 'none' to disable)")
    ap.add_argument("--dayfirst", action="store_true", help="interpret ambiguous numeric dates as DD/MM/YYYY")
    ap.add_argument("--force-https", action="store_true", help="upgrade http:// links to https://")
    ap.add_argument("--object-separator", metavar="SEP",
                    help="unify separators between digits in object numbers (e.g. '.')")
    ap.add_argument("--keep-caps", action="store_true", help="do not convert ALL-CAPS titles")
    ap.add_argument("--straight-quotes", action="store_true", help="convert curly quotes in titles to straight quotes")
    ap.add_argument("--sort-by-object-number", action="store_true", help="sort output by object number (natural order)")
    ap.add_argument("--no-quoting", action="store_true", help="treat quote characters in the input literally")
    args = ap.parse_args()

    in_path = Path(args.input)
    out_path = args.output or str(in_path.with_name(in_path.stem + "_standardized.tsv"))
    if args.report:
        report_path = None if args.report.lower() == "none" else args.report
    elif out_path == "-":
        report_path = str(in_path.with_name(in_path.stem + "_issues.tsv"))
    else:
        report_path = str(Path(out_path).with_name(Path(out_path).stem + "_issues.tsv"))

    rows, encoding = read_tsv(in_path, use_quoting=not args.no_quoting)
    if not rows:
        sys.exit("Input file is empty.")

    mapping, has_header = detect_columns(rows[0][1])
    data_rows = rows[1:] if has_header else rows

    issues = []            # (line, column, severity, original, standardized, message)
    output = []            # (line, [date, title, object_number, link])
    changed = Counter()
    sev_counts = defaultdict(Counter)

    def note(line, col, orig, new, notes):
        for severity, msg in notes:
            issues.append((line, col, severity, clean_text(orig), new, msg))
            sev_counts[col][severity] += 1

    for line, row in data_rows:
        if not any(c.strip() for c in row):
            continue
        get = lambda f: row[mapping[f]] if mapping[f] < len(row) else ""

        raw = {f: get(f) for f in OUTPUT_HEADER}
        date, n1 = standardize_date(raw["date"], args.dayfirst)
        title, n2 = standardize_title(raw["title"], not args.keep_caps, args.straight_quotes)
        objnum, n3 = standardize_object_number(raw["object_number"], args.object_separator)
        link, n4 = standardize_link(raw["link"], args.force_https)

        for col, new, notes in (("date", date, n1), ("title", title, n2),
                                ("object_number", objnum, n3), ("link", link, n4)):
            note(line, col, raw[col], new, notes)
            if new != raw[col].strip():
                changed[col] += 1

        extra = [c for i, c in enumerate(row) if i not in mapping.values() and c.strip()]
        if extra:
            note(line, "row", "\t".join(row), "",
                 [("warning", f"{len(extra)} extra non-empty column(s) ignored: {' | '.join(extra)[:120]}")])

        output.append((line, [date, title, objnum, link]))

    # Duplicate object numbers
    counts = Counter(r[2] for _, r in output if r[2])
    dupes = {k for k, v in counts.items() if v > 1}
    for line, r in output:
        if r[2] in dupes:
            note(line, "object_number", r[2], r[2],
                 [("error", f"duplicate object number (appears {counts[r[2]]} times)")])

    if args.sort_by_object_number:
        output.sort(key=lambda x: (x[1][2] == "", natural_key(x[1][2])))

    # Write output (values contain no tabs/newlines after cleaning)
    out = sys.stdout if out_path == "-" else open(out_path, "w", encoding="utf-8", newline="")
    try:
        out.write("\t".join(OUTPUT_HEADER) + "\n")
        for _, r in output:
            out.write("\t".join(r) + "\n")
    finally:
        if out is not sys.stdout:
            out.close()

    if report_path:
        issues.sort(key=lambda x: (x[0], x[1]))
        with open(report_path, "w", encoding="utf-8", newline="") as f:
            f.write("line\tcolumn\tseverity\toriginal\tstandardized\tmessage\n")
            for line, col, sev, orig, new, msg in issues:
                f.write("\t".join([str(line), col, sev, clean_text(orig), clean_text(new), msg]) + "\n")

    # Summary
    err = sys.stderr
    print(f"Processed {len(output):,} rows (encoding: {encoding}, "
          f"header {'detected' if has_header else 'not detected; assumed date/title/object number/link order'})",
          file=err)
    for col in OUTPUT_HEADER + ["row"]:
        if col == "row" and not sev_counts[col]:
            continue
        print(f"  {col:<14} {changed[col]:>6,} changed  "
              f"{sev_counts[col]['error']:>5,} errors  {sev_counts[col]['warning']:>5,} warnings", file=err)
    if dupes:
        print(f"  {len(dupes):,} object number(s) are duplicated", file=err)
    if out_path != "-":
        print(f"Output: {out_path}", file=err)
    if report_path:
        print(f"Issues: {report_path} ({len(issues):,} entries)", file=err)


if __name__ == "__main__":
    main()
```

## Example

**Input (`inventory.tsv`):**
```
Date	Title	Object No.	URL
c. 1890	"Portrait of a Woman."	1985 . 12 . 3	www.museum.org/objects/1985.12.3?utm_source=x
March 3, 1890	STILL LIFE WITH FRUIT II	1985.12.4	http://Museum.org/objects/1985.12.4
1890-95	  Landscape,	1985.12.4	museum.org/objects/x
19th c.	Untitled	l-2001-5	not a link
500-300 BC	Amphora	1.98E+05	
[1920?]	Vase	2001.5.0	https://museum.org/objects/2001.5
```

**Run:**
```bash
python standardize_inventory.py inventory.tsv --force-https
```

**Output (`inventory_standardized.tsv`):**
```
date	title	object_number	link
ca. 1890	Portrait of a Woman	1985.12.3	https://www.museum.org/objects/1985.12.3
1890-03-03	Still Life with Fruit II	1985.12.4	https://museum.org/objects/1985.12.4
1890/1895	Landscape	1985.12.4	https://museum.org/objects/x
19th century	Untitled	L-2001-5	not a link
500 BCE/300 BCE	Amphora	1.98E+05	
1920?	Vase	2001.5.0	https://museum.org/objects/2001.5
```

**Issues report (`inventory_standardized_issues.tsv`)** flags these items for review:
- The ALL‑CAPS title conversion.
- The duplicate `1985.12.4`.
- The invalid link `not a link`.
- The Excel‑corrupted `1.98E+05`.
- The missing link.
- The bracketed (inferred) date.

## Notes and customization

- **Date convention:** Ranges use `/` (ISO 8601 interval style), so `1890/1895` can't be confused with year‑month `1890-11`. To get `1890–1895` instead, change the `"/".join(...)` line in `standardize_date`.
- **Ambiguous numeric dates** such as `03/04/1890` default to US `MM/DD`. Use `--dayfirst` for European data. Ambiguous cases are always flagged.
- **Object numbers** are institution‑specific, so the script only makes safe changes by default. Use `--object-separator .` if your institution uses one consistent separator.
- **Nothing is silently lost:** unparseable values are kept, extra columns are reported, and the report includes both the original and standardized values so a registrar can review the changes.
