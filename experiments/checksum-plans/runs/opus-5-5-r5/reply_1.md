# Museum Inventory TSV Standardizer

This Python 3 script uses only the standard library. It cleans a 4-column inventory file (date, title, object number, link), writes a standardized TSV, and reports every value it changed or couldn't handle so a person can review it.

## What it does

| Column | Standardization |
|---|---|
| **Date** | Rewrites dates in a consistent style: `1923-05-04`, `1923-05`, `1923`, `1920s`, `19th century`, `1910–1912`, `ca. 1920`, `500–450 BCE`, `n.d.`. It keeps qualifiers such as circa, `?`, `[ ]`, and early/mid/late. It can optionally add sortable start and end year columns. |
| **Title** | Cleans whitespace and Unicode, removes quotes that wrap the whole title, and standardizes "Untitled". It can optionally fix ALL-CAPS titles. |
| **Object number** | Trims spaces and punctuation, makes dashes consistent, removes spaces around separators, strips prefixes like `No.` or `#`, and flags duplicates. |
| **Link** | Adds `https://` where it is missing, lowercases the host, removes tracking parameters (`utm_*`, `fbclid`, and similar), and flags malformed links. It can optionally upgrade http to https. |

## The script: `standardize_inventory.py`

```python
#!/usr/bin/env python3
"""
standardize_inventory.py - Clean and standardize a museum inventory TSV.

Expected columns (any order if a header row is present):
    date, title, object number, link

Usage:
    python standardize_inventory.py inventory.tsv -o inventory_clean.tsv
    python standardize_inventory.py inventory.tsv -o clean.tsv --report issues.tsv \
        --add-year-columns --sort-by object_number --force-https
"""

import argparse
import csv
import io
import re
import sys
import unicodedata
from datetime import date as Date
from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# --------------------------------------------------------------------------
# Header handling
# --------------------------------------------------------------------------

CANONICAL = ["date", "title", "object_number", "link"]
OUTPUT_HEADERS = {"date": "Date", "title": "Title",
                  "object_number": "Object Number", "link": "Link"}

HEADER_ALIASES = {
    "date": {"date", "dates", "date made", "creation date", "object date",
             "dated", "date created", "production date"},
    "title": {"title", "name", "object name", "object title", "work title"},
    "object_number": {"object number", "object no", "object no.", "object #",
                      "accession number", "accession no", "accession no.",
                      "accession #", "accession", "inventory number",
                      "inventory no", "inventory no.", "obj no", "obj. no.",
                      "id", "catalog number", "catalogue number"},
    "link": {"link", "url", "uri", "web link", "permalink", "website",
             "web address", "online record"},
}


def norm_header(h):
    h = clean_text(h).lower().replace("_", " ")
    return re.sub(r"\s+", " ", h).strip()


def map_header(row):
    """Return {canonical: column_index} if row looks like a header, else None."""
    mapping = {}
    for idx, cell in enumerate(row):
        key = norm_header(cell)
        for canon, aliases in HEADER_ALIASES.items():
            if key in aliases and canon not in mapping:
                mapping[canon] = idx
    return mapping if len(mapping) >= 2 else None


# --------------------------------------------------------------------------
# Generic text cleanup
# --------------------------------------------------------------------------

def clean_text(s):
    if s is None:
        return ""
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\u00a0", " ")                      # non-breaking space
    s = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", s)  # zero-width chars
    s = re.sub(r"\s+", " ", s)                        # tabs/newlines/multiple spaces
    return s.strip()


# --------------------------------------------------------------------------
# Dates
# --------------------------------------------------------------------------

UNDATED = {"n.d", "nd", "undated", "unknown", "no date", "date unknown",
           "s.d", "not dated", "?", "-", "—", "–"}

CIRCA_RE = re.compile(
    r"^(?:c\.|ca\.?|circa|approx\.?|approximately|about|around|c(?=\s*\d))\s*",
    re.I)
QUALIFIER_RE = re.compile(r"^(early|mid|late)[\s-]+", re.I)
BCE_RE = re.compile(r"\s*(?:B\.?C\.?E\.?|B\.?C\.?)$", re.I)
CE_SUFFIX_RE = re.compile(r"\s*(?:C\.E\.|CE|A\.D\.|AD)$")
AD_PREFIX_RE = re.compile(r"^(?:A\.D\.|AD)\s+")
CENTURY_RE = re.compile(
    r"^(\d{1,2})(?:st|nd|rd|th)?[\s-]*(?:century|cent\.?|c\.?)$", re.I)
DECADE_RE = re.compile(r"^(\d{2,3}0)'?s$", re.I)
RANGE_SEP_RE = re.compile(r"\s*(?:–|—|-|\bto\b|\buntil\b|\bthrough\b)\s*", re.I)
BETWEEN_RE = re.compile(r"^between\s+(.+?)\s+and\s+(.+)$", re.I)

TEXT_DAY_FORMATS = ["%B %d %Y", "%b %d %Y", "%d %B %Y", "%d %b %Y",
                    "%Y %B %d", "%Y %b %d"]
TEXT_MONTH_FORMATS = ["%B %Y", "%b %Y"]


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def _valid_ymd(y, m, d):
    try:
        Date(y, m, d)
        return True
    except ValueError:
        return False


def parse_single(s, dayfirst=False):
    """
    Parse a single (non-range) date expression.
    Returns (display, lo_year, hi_year, kind) or None.
    """
    s = s.strip()

    # Year only: 1923, 79, 500
    if re.fullmatch(r"\d{1,4}", s):
        y = int(s)
        return str(y), y, y, "year"

    # Decade: 1920s, 1920's
    m = DECADE_RE.fullmatch(s)
    if m:
        y = int(m.group(1))
        return f"{y}s", y, y + 9, "decade"

    # Century: 19th century, 19th c., 19th-century, 19c
    m = CENTURY_RE.fullmatch(s)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 21:
            lo = (n - 1) * 100
            return f"{ordinal(n)} century", lo, lo + 99, "century"

    # ISO-like: 1923-05-04, 1923/5/4, 1923.05.04
    m = re.fullmatch(r"(\d{4})[/.\-](\d{1,2})[/.\-](\d{1,2})", s)
    if m:
        y, mo, d = map(int, m.groups())
        if _valid_ymd(y, mo, d):
            return f"{y:04d}-{mo:02d}-{d:02d}", y, y, "day"

    # Numeric: 5/4/1923 or 4.5.1923 (order set by --dayfirst; auto-fixed if impossible)
    m = re.fullmatch(r"(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{4})", s)
    if m:
        a, b, y = map(int, m.groups())
        mo, d = (b, a) if dayfirst else (a, b)
        if not _valid_ymd(y, mo, d):
            mo, d = d, mo
        if _valid_ymd(y, mo, d):
            return f"{y:04d}-{mo:02d}-{d:02d}", y, y, "day"

    # Month/year numeric: 5/1923
    m = re.fullmatch(r"(\d{1,2})/(\d{4})", s)
    if m:
        mo, y = int(m.group(1)), int(m.group(2))
        if 1 <= mo <= 12:
            return f"{y:04d}-{mo:02d}", y, y, "month"

    # Text months: "May 4, 1923", "4th May 1923", "Sept. 1923"
    t = s.replace(",", " ")
    t = re.sub(r"(\d+)(?:st|nd|rd|th)\b", r"\1", t, flags=re.I)
    t = re.sub(r"\bSept\b", "Sep", t, flags=re.I)
    t = t.replace(".", " ")
    t = re.sub(r"\s+", " ", t).strip()
    for fmt in TEXT_DAY_FORMATS:
        try:
            dt = datetime.strptime(t, fmt)
            return dt.strftime("%Y-%m-%d"), dt.year, dt.year, "day"
        except ValueError:
            pass
    for fmt in TEXT_MONTH_FORMATS:
        try:
            dt = datetime.strptime(t, fmt)
            return dt.strftime("%Y-%m"), dt.year, dt.year, "month"
        except ValueError:
            pass

    return None


def parse_range(s, dayfirst=False, range_sep="–"):
    """Parse ranges like 1920-1925, 1910-12, May 1920 to June 1921, between X and Y."""
    candidates = []
    m = BETWEEN_RE.fullmatch(s)
    if m:
        candidates.append((m.group(1), m.group(2)))
    for sep in RANGE_SEP_RE.finditer(s):
        candidates.append((s[:sep.start()], s[sep.end():]))

    for left, right in candidates:
        left, right = left.strip(), right.strip()
        if not left or not right:
            continue
        a = parse_single(left, dayfirst)
        if not a:
            continue

        # Abbreviated end year: 1920-25, 1898-02, 1920-5
        if a[3] == "year" and re.fullmatch(r"\d{1,2}", right) and a[1] >= 100:
            start = a[1]
            if len(right) == 2:
                end = start // 100 * 100 + int(right)
                if end < start:
                    # "1920-05" is more likely ISO year-month than a range.
                    if 1 <= int(right) <= 12 and end + 100 - start > 50:
                        return f"{start:04d}-{int(right):02d}", start, start
                    end += 100
            else:
                end = start // 10 * 10 + int(right)
                if end < start:
                    continue
            return f"{start}{range_sep}{end}", start, end

        b = parse_single(right, dayfirst)
        if not b:
            continue
        lo, hi = min(a[1], b[1]), max(a[2], b[2])
        return f"{a[0]}{range_sep}{b[0]}", lo, hi

    return None


def standardize_date(raw, dayfirst=False, range_sep="–"):
    """Returns (value, lo_year, hi_year, issue_or_None)."""
    s = clean_text(raw)
    if not s:
        return "", None, None, "missing date"
    if s.lower().strip(" .") in UNDATED or s in UNDATED:
        return "n.d.", None, None, None

    bracketed = s.startswith("[") and s.endswith("]")
    if bracketed:
        s = s[1:-1].strip()

    uncertain = s.endswith("?")
    s = s.rstrip("?").strip()

    circa = False
    m = CIRCA_RE.match(s)
    if m:
        circa = True
        s = s[m.end():].strip()

    bce = False
    m = BCE_RE.search(s)
    if m:
        bce = True
        s = s[:m.start()].strip()
    else:
        s = CE_SUFFIX_RE.sub("", s)
        s = AD_PREFIX_RE.sub("", s).strip()

    qualifier = None
    m = QUALIFIER_RE.match(s)
    if m:
        qualifier = m.group(1).lower()
        s = s[m.end():].strip()

    parsed = parse_single(s, dayfirst)
    if parsed:
        core, lo, hi = parsed[0], parsed[1], parsed[2]
    else:
        r = parse_range(s, dayfirst, range_sep)
        if not r:
            return clean_text(raw), None, None, "unrecognized date format (left unchanged)"
        core, lo, hi = r

    if bce:
        lo, hi = -hi, -lo

    out = core
    if qualifier:
        out = ("mid-" if qualifier == "mid" else qualifier + " ") + out
    if bce:
        out += " BCE"
    if circa:
        out = "ca. " + out
    if uncertain:
        out += "?"
    if bracketed:
        out = f"[{out}]"
    return out, lo, hi, None


# --------------------------------------------------------------------------
# Titles
# --------------------------------------------------------------------------

UNTITLED = {"untitled", "[untitled]", "(untitled)", "no title", "[no title]",
            "title unknown", "untitled."}
SMALL_WORDS = {"a", "an", "and", "as", "at", "but", "by", "for", "from", "in",
               "into", "nor", "of", "on", "or", "the", "to", "with", "de",
               "la", "le", "van", "von", "der", "du"}
WRAP_QUOTES_RE = re.compile(r'^["“”\'‘’«](.*)["“”\'‘’»]$')


def smart_title_case(s):
    words = s.lower().split(" ")
    out = []
    for i, w in enumerate(words):
        if 0 < i < len(words) - 1 and w in SMALL_WORDS:
            out.append(w)
        else:
            out.append(w[:1].upper() + w[1:])
    return " ".join(out)


def standardize_title(raw, fix_caps=False):
    """Returns (value, issue_or_None)."""
    s = clean_text(raw)
    if not s:
        return "", "missing title"
    m = WRAP_QUOTES_RE.fullmatch(s)
    if m and m.group(1).strip():
        s = m.group(1).strip()
    if s.lower() in UNTITLED:
        return "Untitled", None
    letters = [c for c in s if c.isalpha()]
    if fix_caps and len(letters) > 3 and all(c.isupper() for c in letters):
        return smart_title_case(s), "converted from ALL CAPS (check acronyms/names)"
    return s, None


# --------------------------------------------------------------------------
# Object numbers
# --------------------------------------------------------------------------

DASHES_RE = re.compile(r"[\u2010\u2011\u2012\u2013\u2014\u2015\u2212]")
OBJNUM_PREFIX_RE = re.compile(
    r"^(?:(?:acc(?:ession)?|obj(?:ect)?|inv(?:entory)?)\.?\s*)?(?:no\.?|number|#)\s*",
    re.I)


def standardize_object_number(raw, upper=False):
    """Returns (value, issue_or_None)."""
    s = clean_text(raw)
    if not s:
        return "", "missing object number"
    s = OBJNUM_PREFIX_RE.sub("", s)
    s = DASHES_RE.sub("-", s)
    s = re.sub(r"\s*([.\-/:,])\s*", r"\1", s)  # "1999 . 12 - 3" -> "1999.12-3"
    s = s.strip(" .,;:")
    if upper:
        s = s.upper()
    issue = None
    if not re.search(r"\d", s):
        issue = "object number contains no digits"
    return s, issue


def natural_key(s):
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r"(\d+)", s or "")]


# --------------------------------------------------------------------------
# Links
# --------------------------------------------------------------------------

TRACKING_PARAM_RE = re.compile(
    r"^(?:utm_.*|fbclid|gclid|dclid|msclkid|mc_cid|mc_eid|_ga|igshid)$", re.I)


def standardize_link(raw, force_https=False):
    """Returns (value, issue_or_None)."""
    s = clean_text(raw).strip("<>\"' ")
    if not s:
        return "", None  # links are often optional; not flagged
    s = s.replace(" ", "%20")

    if not re.match(r"^[a-z][a-z0-9+.\-]*://", s, re.I):
        if re.match(r"^(?:www\.)?[\w\-]+(?:\.[\w\-]+)+(?::\d+)?(?:[/?#]|$)", s):
            s = "https://" + s
        else:
            return s, "unrecognized link (left unchanged)"

    try:
        parts = urlsplit(s)
    except ValueError:
        return s, "malformed link (left unchanged)"

    scheme = parts.scheme.lower()
    if scheme not in ("http", "https"):
        return s, f"unexpected URL scheme '{scheme}'"
    if force_https and scheme == "http":
        scheme = "https"

    netloc = parts.netloc.lower()
    if (scheme == "https" and netloc.endswith(":443")) or \
       (scheme == "http" and netloc.endswith(":80")):
        netloc = netloc.rsplit(":", 1)[0]
    if "." not in netloc and not netloc.startswith("localhost"):
        return s, "link host looks invalid"

    query_pairs = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                   if not TRACKING_PARAM_RE.match(k)]
    query = urlencode(query_pairs, doseq=True)
    return urlunsplit((scheme, netloc, parts.path, query, parts.fragment)), None


# --------------------------------------------------------------------------
# I/O
# --------------------------------------------------------------------------

def read_tsv(path):
    with open(path, "rb") as f:
        data = f.read()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = data.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    rows = list(csv.reader(io.StringIO(text, newline=""), delimiter="\t"))
    return rows, enc


def main():
    ap = argparse.ArgumentParser(description="Standardize a museum inventory TSV.")
    ap.add_argument("input", help="Input .tsv file")
    ap.add_argument("-o", "--output", help="Output .tsv (default: <input>_standardized.tsv)")
    ap.add_argument("--report", help="Write a TSV of all changes/issues to this path")
    ap.add_argument("--no-header", action="store_true",
                    help="Input has no header row (columns assumed: date, title, object number, link)")
    ap.add_argument("--dayfirst", action="store_true",
                    help="Interpret numeric dates like 04/05/1923 as day/month/year")
    ap.add_argument("--range-sep", default="–", help="Separator for date ranges (default: en dash)")
    ap.add_argument("--add-year-columns", action="store_true",
                    help="Add 'Earliest Year' and 'Latest Year' columns for sorting/search")
    ap.add_argument("--fix-caps", action="store_true", help="Convert ALL-CAPS titles to title case")
    ap.add_argument("--upper-object-numbers", action="store_true",
                    help="Uppercase object numbers (off by default; part suffixes like 'a-b' are often lowercase)")
    ap.add_argument("--force-https", action="store_true", help="Upgrade http:// links to https://")
    ap.add_argument("--drop-duplicate-rows", action="store_true",
                    help="Remove rows identical after standardization")
    ap.add_argument("--sort-by", choices=["object_number", "date", "title"],
                    help="Sort output rows")
    ap.add_argument("--bom", action="store_true", help="Write UTF-8 BOM (helps Excel detect encoding)")
    args = ap.parse_args()

    rows, encoding = read_tsv(args.input)
    if not rows:
        sys.exit("Input file is empty.")

    # Determine column mapping
    mapping = None if args.no_header else map_header(rows[0])
    if mapping:
        data_rows = rows[1:]
        start_line = 2
        missing = [c for c in CANONICAL if c not in mapping]
        if missing:
            print(f"Warning: header missing column(s): {', '.join(missing)}", file=sys.stderr)
    else:
        if not args.no_header:
            print("No recognizable header found; assuming column order: "
                  "date, title, object number, link", file=sys.stderr)
        mapping = {c: i for i, c in enumerate(CANONICAL)}
        data_rows = rows
        start_line = 1

    issues = []
    changes = {c: 0 for c in CANONICAL}
    out_rows = []

    def log(line, field, original, new, msg):
        issues.append({"line": line, "field": field, "original": original,
                       "standardized": new, "issue": msg})

    for offset, row in enumerate(data_rows):
        line = start_line + offset
        if not any(cell.strip() for cell in row):
            continue  # skip blank rows

        width = max(mapping.values()) + 1
        if len(row) > width and any(c.strip() for c in row[width:]):
            log(line, "(row)", "\t".join(row), "", f"row has {len(row)} columns; extra columns ignored")

        def get(col):
            idx = mapping.get(col)
            return row[idx] if idx is not None and idx < len(row) else ""

        orig = {c: get(c) for c in CANONICAL}

        date_val, lo, hi, d_issue = standardize_date(orig["date"], args.dayfirst, args.range_sep)
        title_val, t_issue = standardize_title(orig["title"], args.fix_caps)
        obj_val, o_issue = standardize_object_number(orig["object_number"], args.upper_object_numbers)
        link_val, l_issue = standardize_link(orig["link"], args.force_https)

        new = {"date": date_val, "title": title_val,
               "object_number": obj_val, "link": link_val}
        found = {"date": d_issue, "title": t_issue,
                 "object_number": o_issue, "link": l_issue}

        for c in CANONICAL:
            changed = new[c] != orig[c]
            if changed:
                changes[c] += 1
            if found[c]:
                log(line, c, orig[c], new[c], found[c])
            elif changed and clean_text(orig[c]) != new[c]:
                # Only log substantive changes, not whitespace-only fixes
                log(line, c, orig[c], new[c], "changed")

        out_rows.append({"line": line, **new, "lo": lo, "hi": hi})

    # Duplicate detection
    if args.drop_duplicate_rows:
        seen, deduped = set(), []
        for r in out_rows:
            key = tuple(r[c] for c in CANONICAL)
            if key in seen:
                log(r["line"], "(row)", "", "", "exact duplicate row removed")
                continue
            seen.add(key)
            deduped.append(r)
        out_rows = deduped

    by_objnum = {}
    for r in out_rows:
        if r["object_number"]:
            by_objnum.setdefault(r["object_number"].lower(), []).append(r["line"])
    for num, lines in by_objnum.items():
        if len(lines) > 1:
            for ln in lines:
                log(ln, "object_number", "", num,
                    f"duplicate object number (lines {', '.join(map(str, lines))})")

    # Sorting
    if args.sort_by == "object_number":
        out_rows.sort(key=lambda r: natural_key(r["object_number"]))
    elif args.sort_by == "date":
        out_rows.sort(key=lambda r: (r["lo"] is None, r["lo"] or 0, r["hi"] or 0))
    elif args.sort_by == "title":
        out_rows.sort(key=lambda r: r["title"].lower())

    # Write output
    out_path = args.output or re.sub(r"(\.tsv|\.txt)?$", "_standardized.tsv",
                                     args.input, count=1, flags=re.I)
    header = [OUTPUT_HEADERS[c] for c in CANONICAL]
    if args.add_year_columns:
        header += ["Earliest Year", "Latest Year"]

    with open(out_path, "w", encoding="utf-8-sig" if args.bom else "utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        for r in out_rows:
            vals = [r[c] for c in CANONICAL]
            if args.add_year_columns:
                vals += ["" if r["lo"] is None else r["lo"],
                         "" if r["hi"] is None else r["hi"]]
            w.writerow(vals)

    # Report
    issues.sort(key=lambda i: (i["line"], i["field"]))
    if args.report:
        with open(args.report, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["line", "field", "original", "standardized", "issue"],
                               delimiter="\t", lineterminator="\n")
            w.writeheader()
            w.writerows(issues)

    problems = [i for i in issues if i["issue"] != "changed"]
    print(f"Read {len(data_rows)} rows (encoding: {encoding}); wrote {len(out_rows)} rows to {out_path}",
          file=sys.stderr)
    print("Values modified: " + ", ".join(f"{c}={n}" for c, n in changes.items()), file=sys.stderr)
    print(f"Issues needing review: {len(problems)}", file=sys.stderr)
    if not args.report:
        for i in problems[:25]:
            print(f"  line {i['line']} [{i['field']}]: {i['issue']} -> {i['original']!r}",
                  file=sys.stderr)
        if len(problems) > 25:
            print(f"  ... and {len(problems) - 25} more (use --report to see all)", file=sys.stderr)


if __name__ == "__main__":
    main()
```

## Usage

```bash
# Basic
python standardize_inventory.py inventory.tsv -o inventory_clean.tsv

# Full options: review report, sort columns, sorted by accession number
python standardize_inventory.py inventory.tsv -o clean.tsv \
    --report review.tsv --add-year-columns --sort-by object_number \
    --force-https --fix-caps --bom
```

## Example

**Input**

```
Date	Title	Object No.	Link
c 1920	  "Portrait of a Woman"	1999 . 12 . 3a	www.museum.org/objects/123?utm_source=x
May 4th, 1923	THE RIVER AT DAWN	No. 2001–45	http://museum.org/obj/456
1910-12	untitled	1985.7	museum.org/obj/789
19th c.	Teapot	1985.7	https://museum.org/obj/790
500-450 BC	Amphora	L2010.1.1	
undated	Bowl	2003.4.15	ftp://old.server/bowl
```

**Output** (with `--fix-caps --add-year-columns`)

```
Date	Title	Object Number	Link	Earliest Year	Latest Year
ca. 1920	Portrait of a Woman	1999.12.3a	https://www.museum.org/objects/123	1920	1920
1923-05-04	The River at Dawn	2001-45	http://museum.org/obj/456	1923	1923
1910–1912	Untitled	1985.7	https://museum.org/obj/789	1910	1912
19th century	Teapot	1985.7	https://museum.org/obj/790	1800	1899
500–450 BCE	Amphora	L2010.1.1		-500	-450
n.d.	Bowl	2003.4.15	ftp://old.server/bowl		
```

The review report flags several of these rows:
- The duplicate object number `1985.7` (lines 4 and 5).
- The ALL-CAPS title conversion, so you can check names and acronyms.
- The `ftp://` link.

## Design choices you may want to adjust

- **Values the script can't parse are never deleted or guessed at.** They stay unchanged and are listed in the report.
- **Object numbers are not uppercased by default.** Many collections use lowercase part suffixes (`1999.12.3a-b`). If your numbering scheme is all caps, use `--upper-object-numbers`.
- **Numeric dates are read as month-first by default.** Use `--dayfirst` for European-style data. Impossible dates such as `25/12/1923` are corrected automatically either way.
- **`1910-12` is read as the range 1910–1912,** which is the usual meaning in catalog records, rather than December 1910.
- **Date style:** the script follows common museum cataloging conventions (`ca.`, `n.d.`, en-dash ranges). If you need machine-readable EDTF (e.g. `1920~`, `1910/1912`), `standardize_date()` is the one place to change.
- **Empty links are allowed silently,** but empty dates, titles, and object numbers are flagged.
