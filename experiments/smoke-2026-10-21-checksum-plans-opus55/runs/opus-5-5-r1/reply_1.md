# Museum Inventory Standardizer

This Python script cleans a TSV with **date, title, object number, and link** columns. It uses only the standard library, so there is nothing to install. It writes two files:

1. **A standardized TSV**, with the same four columns, cleaned up.
2. **A report TSV**, listing every changed cell and every problem that needs a human to look at it.

## What it does

| Column | Standardization |
|---|---|
| **Date** | Converts to ISO format (`1890-03-04`, `1890-03`, `1890`) where possible. Normalizes circa (`c.1890`, `circa 1890` → `ca. 1890`), ranges (`1890-95` → `1890–1895`), decades (`1890's` → `1890s`), centuries (`19th c.` → `19th century`), eras (`500 BC` → `500 BCE`) and undated values (`undated`, `nd` → `n.d.`). Flags ambiguous dates like `03/04/1890`, invalid dates, future dates and anything it can't parse. |
| **Title** | Normalizes Unicode and whitespace, removes invisible characters, strips stray wrapping quotes and fixes spacing before punctuation. It **never changes capitalization**, because titles are curatorial decisions. It flags empty or ALL-CAPS titles. |
| **Object number** | Trims and uppercases. Removes prefixes like `No.` or `Acc. #`, normalizes odd dash characters and tidies separators. It can optionally unify separators (`1985-12-3` → `1985.12.3`). Flags duplicates and empty values. |
| **Link** | Adds a missing `https://`, lowercases the domain and removes default ports. Strips tracking parameters (`utm_*`, `fbclid`, …). Optionally upgrades to HTTPS and checks that links actually work. |

## The script: `standardize_inventory.py`

```python
#!/usr/bin/env python3
"""
standardize_inventory.py - Clean and standardize a museum inventory TSV.

Expected columns: Date, Title, Object Number, Link
(header row optional; common header variants are recognized in any order).

Examples:
    python standardize_inventory.py inventory.tsv
    python standardize_inventory.py inventory.tsv -o clean.tsv --report issues.tsv
    python standardize_inventory.py inventory.tsv --day-first --object-sep . --https
    python standardize_inventory.py inventory.tsv --check-links --drop-duplicates
"""

import argparse
import csv
import io
import re
import sys
import unicodedata
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

OUTPUT_HEADER = ["Date", "Title", "Object Number", "Link"]
KEYS = ["date", "title", "object number", "link"]

HEADER_ALIASES = {
    "date": {"date", "dates", "date made", "creation date", "object date",
             "dated", "year", "production date"},
    "title": {"title", "name", "object name", "object title", "work title"},
    "object number": {"object number", "object no", "object no.", "object #",
                      "object id", "accession number", "accession no",
                      "accession no.", "accession #", "obj no", "obj. no.",
                      "inventory number", "inv no", "id", "number"},
    "link": {"link", "url", "uri", "web link", "permalink", "website",
             "online record", "record url"},
}

# --------------------------------------------------------------------------
# Generic text cleanup
# --------------------------------------------------------------------------

def clean_text(s: str) -> str:
    """Unicode-normalize, drop invisible/control chars, collapse whitespace."""
    if s is None:
        return ""
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\u00a0", " ").replace("\u2007", " ").replace("\u202f", " ")
    s = "".join(ch for ch in s
                if ch in "\t\n" or not unicodedata.category(ch).startswith("C"))
    return re.sub(r"\s+", " ", s).strip()


# --------------------------------------------------------------------------
# Dates
# --------------------------------------------------------------------------

MONTHS = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10, "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}
UNDATED = {"nd", "n.d", "n. d", "undated", "unknown", "date unknown", "no date",
           "not dated", "s.d", "sd", "?", "-", "--", "n/a", "na"}

CIRCA_RE = re.compile(
    r"^(?:circa|ca\.?|c\.?|approx(?:imately|\.)?|about|around)(?:\s+|(?=\d))",
    re.I)
ERA_SUFFIX_RE = re.compile(
    r"\s*(?<![A-Za-z])(B\.?\s?C\.?(?:\s?E\.?)?|A\.?\s?D\.?|C\.?\s?E\.?)$", re.I)
ERA_PREFIX_RE = re.compile(r"^(?:A\.?\s?D\.?)\s+", re.I)
RANGE_SEP_RE = re.compile(
    r"\s*(?:–|—|/|\bto\b|\bthrough\b|\bthru\b)\s*|\s+-\s+|-", re.I)


class DateError(Exception):
    pass


def _valid(y, m, d):
    try:
        date(y, m, d)
        return True
    except ValueError:
        return False


def ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def parse_point(token: str, day_first: bool):
    """Parse a single (non-range) date expression.
    Returns (value, kind, issues), None if no pattern matches,
    or raises DateError for recognized-but-invalid input."""
    low = token.strip().strip(",").lower()
    issues = []

    qualifier = ""
    mq = re.match(r"^(early|mid|late)[\s-]+", low)
    if mq:
        qualifier = "mid-" if mq.group(1) == "mid" else mq.group(1) + " "
        low = low[mq.end():]

    def done(value, kind):
        return qualifier + value, kind, issues

    # 1890-03-04, 1890/3/4, 1890.03.04
    m = re.fullmatch(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", low)
    if m:
        y, mo, d = map(int, m.groups())
        if not _valid(y, mo, d):
            raise DateError("invalid calendar date")
        return done(f"{y:04d}-{mo:02d}-{d:02d}", "day")

    # 03/04/1890, 4.3.1890, 3-4-90
    m = re.fullmatch(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4}|\d{2})", low)
    if m:
        a, b, ystr = m.groups()
        a, b, y = int(a), int(b), int(ystr)
        if len(ystr) == 2:
            raise DateError("two-digit year; century unknown")
        if a > 12 and b > 12:
            raise DateError("invalid numeric date")
        if a > 12:
            d, mo = a, b
        elif b > 12:
            mo, d = a, b
        else:
            mo, d = (b, a) if day_first else (a, b)
            if a != b:
                issues.append("ambiguous day/month; assumed "
                              + ("DD/MM" if day_first else "MM/DD"))
        if not _valid(y, mo, d):
            raise DateError("invalid calendar date")
        return done(f"{y:04d}-{mo:02d}-{d:02d}", "day")

    # March 4, 1890 / Mar. 4th 1890
    m = re.fullmatch(r"([a-z]+)\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{1,4})", low)
    if m and m.group(1) in MONTHS:
        mo, d, y = MONTHS[m.group(1)], int(m.group(2)), int(m.group(3))
        if not _valid(y, mo, d):
            raise DateError("invalid calendar date")
        return done(f"{y:04d}-{mo:02d}-{d:02d}", "day")

    # 4 March 1890 / 4th Mar. 1890
    m = re.fullmatch(r"(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]+)\.?,?\s+(\d{1,4})", low)
    if m and m.group(2) in MONTHS:
        d, mo, y = int(m.group(1)), MONTHS[m.group(2)], int(m.group(3))
        if not _valid(y, mo, d):
            raise DateError("invalid calendar date")
        return done(f"{y:04d}-{mo:02d}-{d:02d}", "day")

    # March 1890 / Mar., 1890
    m = re.fullmatch(r"([a-z]+)\.?,?\s+(\d{1,4})", low)
    if m and m.group(1) in MONTHS:
        return done(f"{int(m.group(2)):04d}-{MONTHS[m.group(1)]:02d}", "month")

    # 1890-03 (year-month)
    m = re.fullmatch(r"(\d{4})[-/.](\d{1,2})", low)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        if 1 <= mo <= 12:
            if len(m.group(2)) == 2 and mo > y % 100:
                issues.append("interpreted as year-month; could be a year range")
            return done(f"{y:04d}-{mo:02d}", "month")

    # 1890
    if re.fullmatch(r"\d{1,4}", low):
        return done(str(int(low)), "year")

    # 1890s / 1890's
    m = re.fullmatch(r"(\d{2,3})0'?s", low)
    if m:
        return done(f"{m.group(1)}0s", "decade")

    # 19th century / 19th c. / 19th-century / 19 cent.
    m = re.fullmatch(r"(\d{1,2})(?:st|nd|rd|th)?\s*-?\s*(?:c\.?|cent\.?|century)", low)
    if m:
        return done(f"{ordinal(int(m.group(1)))} century", "century")

    return None


def parse_range(s: str, day_first: bool, range_sep: str, era: str):
    """Try every separator position until both sides parse as dates."""
    for m in RANGE_SEP_RE.finditer(s):
        left, right = s[:m.start()].strip(), s[m.end():].strip()
        if not left or not right:
            continue
        try:
            L = parse_point(left, day_first)
            R = parse_point(right, day_first)
        except DateError:
            continue
        if not L or not R:
            continue
        (lv, lk, li), (rv, rk, ri) = L, R
        issues = li + ri
        # Expand abbreviated end year: 1890-95 -> 1890-1895, 1890-5 -> 1895
        if lk == "year" and rk == "year" and len(lv) == 4 and len(right) <= 2:
            rv = lv[: 4 - len(right)] + right.zfill(len(right))
        if lk == rk == "year" and era != "BCE" and int(rv) < int(lv):
            issues.append("range end is before start")
        return f"{lv}{range_sep}{rv}", issues
    return None


def standardize_date(raw: str, day_first=False, range_sep="–"):
    s = clean_text(raw)
    if not s:
        return "", ["missing date"]
    if s.lower().strip().rstrip(".") in UNDATED:
        return "n.d.", []

    work, issues = s, []

    bracketed = work.startswith("[") and work.endswith("]")
    if bracketed:
        work = work[1:-1].strip()

    uncertain = work.endswith("?")
    if uncertain:
        work = work[:-1].strip()

    circa = False
    m = CIRCA_RE.match(work)
    if m:
        circa, work = True, work[m.end():].strip()

    era = ""
    m = ERA_SUFFIX_RE.search(work)
    if m:
        era = "BCE" if m.group(1).upper().startswith("B") else "CE"
        work = work[:m.start()].strip()
    else:
        m = ERA_PREFIX_RE.match(work)
        if m:
            era, work = "CE", work[m.end():].strip()

    try:
        point = parse_point(work, day_first)
    except DateError as e:
        return s, [str(e)]

    if point:
        core, _, more = point
    else:
        rng = parse_range(work, day_first, range_sep, era)
        if not rng:
            return s, ["unrecognized date format"]
        core, more = rng
    issues += more

    out = ("ca. " if circa else "") + core
    if era:
        out += " " + era
    if uncertain:
        out += "?"
    if bracketed:
        out = f"[{out}]"

    if era != "BCE":
        if any(int(y) > date.today().year for y in re.findall(r"\b\d{4}\b", core)):
            issues.append("date is in the future")
    return out, issues


# --------------------------------------------------------------------------
# Titles
# --------------------------------------------------------------------------

def standardize_title(raw: str, ascii_quotes=False):
    t = clean_text(raw)
    issues = []
    if not t:
        return "", ["missing title"]

    # Remove quotes wrapping the entire title (but not internal quotes)
    m = re.fullmatch(r'["“”](.*)["“”]', t)
    if m and not re.search(r'["“”]', m.group(1)):
        t = m.group(1).strip()

    if ascii_quotes:
        t = (t.replace("“", '"').replace("”", '"')
              .replace("‘", "'").replace("’", "'"))

    t = re.sub(r"\s+([,.;:!?])", r"\1", t)      # "Vase , blue" -> "Vase, blue"
    t = re.sub(r"\(\s+", "(", t)
    t = re.sub(r"\s+\)", ")", t)

    letters = [c for c in t if c.isalpha()]
    if len(letters) > 3 and all(c.isupper() for c in letters):
        issues.append("title is ALL CAPS (left unchanged; review)")
    return t, issues


# --------------------------------------------------------------------------
# Object numbers
# --------------------------------------------------------------------------

OBJ_PREFIX_RE = re.compile(
    r"^(?:(?:object|obj\.?|accession|acc\.?|inv(?:entory)?\.?)\s*)?"
    r"(?:no\.|no\b|number\b|num\.|#)\s*:?\s*", re.I)


def standardize_object_number(raw: str, unify_sep=None):
    s = clean_text(raw)
    issues = []
    if not s:
        return "", ["missing object number"]

    s = OBJ_PREFIX_RE.sub("", s)
    s = re.sub(r"[‐‑‒–—―−]", "-", s)               # unicode dashes -> hyphen
    s = s.upper()
    s = re.sub(r"\s*([.\-/:])\s*", r"\1", s)        # "1985 . 12" -> "1985.12"
    if unify_sep:
        s = re.sub(r"(?<=[0-9])[\s\-/:,_.]+(?=[0-9])", unify_sep, s)
    s = re.sub(r"\.{2,}", ".", s).strip(".-/ ")

    if " " in s:
        issues.append("object number contains spaces")
    if not re.search(r"\d", s):
        issues.append("object number has no digits")
    return s, issues


# --------------------------------------------------------------------------
# Links
# --------------------------------------------------------------------------

TRACKING_RE = re.compile(r"^(utm_.*|fbclid|gclid|dclid|msclkid|mc_cid|mc_eid|_ga)$", re.I)


def standardize_link(raw: str, force_https=False):
    s = clean_text(raw).strip("<>\"' ")
    issues = []
    if not s:
        return "", ["missing link"]
    s = s.replace(" ", "%20")

    if not re.match(r"^[a-z][a-z0-9+.\-]*://", s, re.I):
        if re.match(r"^(?:www\.)?[a-z0-9\-]+(?:\.[a-z0-9\-]+)+(?:[/:?#]|$)", s, re.I):
            s = "https://" + s
        else:
            return s, ["invalid URL"]

    p = urlsplit(s)
    scheme = p.scheme.lower()
    host = (p.hostname or "").lower()
    if scheme not in ("http", "https"):
        issues.append(f"unusual URL scheme '{scheme}'")
    if not host or ("." not in host and host != "localhost"):
        return s, ["invalid URL (no valid domain)"]
    if force_https and scheme == "http":
        scheme = "https"

    netloc = host
    if p.port and not ((scheme == "http" and p.port == 80) or
                       (scheme == "https" and p.port == 443)):
        netloc += f":{p.port}"
    if p.username:
        netloc = p.username + (f":{p.password}" if p.password else "") + "@" + netloc

    query = p.query
    pairs = parse_qsl(query, keep_blank_values=True)
    kept = [(k, v) for k, v in pairs if not TRACKING_RE.match(k)]
    if len(kept) != len(pairs):
        query = urlencode(kept)

    return urlunsplit((scheme, netloc, p.path or "/", query, p.fragment)), issues


def check_link(url: str, timeout=10):
    import urllib.error
    import urllib.request
    headers = {"User-Agent": "Mozilla/5.0 (museum-inventory-link-check)"}
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout):
                return None
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (400, 403, 405, 501):
                continue  # some servers reject HEAD; retry with GET
            return f"link returned HTTP {e.code}"
        except Exception as e:
            return f"link unreachable ({type(e).__name__})"
    return None


# --------------------------------------------------------------------------
# I/O helpers
# --------------------------------------------------------------------------

def read_text(path: str):
    data = sys.stdin.buffer.read() if path == "-" else Path(path).read_bytes()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return data.decode(enc), enc
        except UnicodeDecodeError:
            pass
    return data.decode("latin-1"), "latin-1"


def detect_header(row):
    mapping = {}
    for i, cell in enumerate(row):
        h = re.sub(r"[\s_]+", " ", clean_text(cell).lower()).strip(" :")
        for key, aliases in HEADER_ALIASES.items():
            if h in aliases and key not in mapping:
                mapping[key] = i
                break
    return mapping if len(mapping) >= 2 else None


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Standardize a museum inventory TSV.")
    ap.add_argument("input", help="input .tsv file ('-' for stdin)")
    ap.add_argument("-o", "--output", help="output TSV (default: <input>_standardized.tsv)")
    ap.add_argument("--report", help="issues/changes report (default: <input>_report.tsv)")
    ap.add_argument("--day-first", action="store_true",
                    help="read ambiguous numeric dates as DD/MM/YYYY (default MM/DD/YYYY)")
    ap.add_argument("--range-sep", default="–",
                    help="separator for date ranges (default: en dash '–')")
    ap.add_argument("--object-sep", metavar="SEP",
                    help="unify separators between digit groups in object numbers, e.g. '.'")
    ap.add_argument("--ascii-quotes", action="store_true",
                    help="convert curly quotes in titles to straight quotes")
    ap.add_argument("--https", action="store_true", help="upgrade http:// links to https://")
    ap.add_argument("--check-links", action="store_true",
                    help="request each link and flag broken ones (slow)")
    ap.add_argument("--drop-duplicates", action="store_true",
                    help="remove rows that are identical after standardization")
    ap.add_argument("--no-quote-parsing", action="store_true",
                    help="treat double quotes as literal text (use if titles contain stray quotes)")
    args = ap.parse_args()

    stem = "stdin" if args.input == "-" else str(Path(args.input).with_suffix(""))
    out_path = args.output or f"{stem}_standardized.tsv"
    report_path = args.report or f"{stem}_report.tsv"

    text, encoding = read_text(args.input)
    quoting = csv.QUOTE_NONE if args.no_quote_parsing else csv.QUOTE_MINIMAL
    rows = list(csv.reader(io.StringIO(text, newline=""), delimiter="\t", quoting=quoting))
    if not rows:
        sys.exit("Input file is empty.")

    mapping = detect_header(rows[0])
    start = 1 if mapping else 0
    if not mapping:
        mapping = {k: i for i, k in enumerate(KEYS)}
        print("No header detected; assuming column order: "
              + ", ".join(OUTPUT_HEADER), file=sys.stderr)
    else:
        missing = [k for k in KEYS if k not in mapping]
        if missing:
            print(f"Warning: header has no column for: {', '.join(missing)}", file=sys.stderr)

    records = []   # each: {"line": n, "values": [...], "notes": [(col, orig, new, note)]}
    for line_no, row in enumerate(rows[start:], start=start + 1):
        if not any(c.strip() for c in row):
            continue
        get = lambda k: row[mapping[k]] if k in mapping and mapping[k] < len(row) else ""
        notes = []
        if start == 0 and len(row) != 4:
            notes.append(("(row)", "", "", f"expected 4 columns, found {len(row)}"))

        results = [
            ("Date", get("date"), standardize_date(get("date"), args.day_first, args.range_sep)),
            ("Title", get("title"), standardize_title(get("title"), args.ascii_quotes)),
            ("Object Number", get("object number"),
             standardize_object_number(get("object number"), args.object_sep)),
            ("Link", get("link"), standardize_link(get("link"), args.https)),
        ]
        values = []
        for col, orig, (new, issues) in results:
            values.append(new)
            for issue in issues:
                notes.append((col, orig, new, issue))
            if new != orig and not issues:
                notes.append((col, orig, new, "changed"))
        records.append({"line": line_no, "values": values, "notes": notes})

    # Exact duplicate rows
    dropped = 0
    if args.drop_duplicates:
        seen, kept = set(), []
        for r in records:
            key = tuple(r["values"])
            if key in seen:
                dropped += 1
                continue
            seen.add(key)
            kept.append(r)
        records = kept

    # Duplicate object numbers
    counts = Counter(r["values"][2] for r in records if r["values"][2])
    for r in records:
        n = counts.get(r["values"][2], 0)
        if n > 1:
            r["notes"].append(("Object Number", r["values"][2], r["values"][2],
                               f"duplicate object number (appears {n} times)"))

    # Optional live link checking
    if args.check_links:
        urls = sorted({r["values"][3] for r in records
                       if r["values"][3].startswith(("http://", "https://"))})
        print(f"Checking {len(urls)} links...", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=8) as pool:
            status = dict(zip(urls, pool.map(check_link, urls)))
        for r in records:
            problem = status.get(r["values"][3])
            if problem:
                r["notes"].append(("Link", r["values"][3], r["values"][3], problem))

    # Write outputs
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(OUTPUT_HEADER)
        for r in records:
            w.writerow(r["values"])

    issue_counter = Counter()
    changed = 0
    with open(report_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["Line", "Column", "Original", "Standardized", "Note"])
        for r in records:
            for col, orig, new, note in r["notes"]:
                w.writerow([r["line"], col, orig, new, note])
                if note == "changed":
                    changed += 1
                else:
                    issue_counter[re.sub(r"\(appears \d+ times\)", "", note).strip()] += 1

    # Summary
    print(f"\nRead {len(rows) - start} rows ({encoding}); wrote {len(records)} rows -> {out_path}",
          file=sys.stderr)
    if dropped:
        print(f"Dropped {dropped} duplicate rows", file=sys.stderr)
    print(f"Cells changed without issues: {changed}", file=sys.stderr)
    if issue_counter:
        print("Issues needing review:", file=sys.stderr)
        for note, n in issue_counter.most_common():
            print(f"  {n:6d}  {note}", file=sys.stderr)
    print(f"Full report -> {report_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
```

## Example

**Input (`inventory.tsv`)**
```
Date	Title	Object No.	URL
c.1890	  "Portrait of a Woman"	no. 1985-12-3	www.museum.org/objects/123?utm_source=x
March 4, 1890	Landscape , with river	1985.12.4	http://museum.org/objects/124
1890-95	VASE WITH LID	acc. # 2001.5.1	https://museum.org/objects/125
03/04/1890	Untitled	1985.12.4	museum dot org
19th c.	Study (unfinished)	2003.1.10	https://museum.org/objects/127
undated	Bowl	2003.1.11	https://museum.org/objects/128
500 BC	Amphora	1950.2.1	https://museum.org/objects/129
```

**Command**
```bash
python standardize_inventory.py inventory.tsv --object-sep .
```

**Output (`inventory_standardized.tsv`)**
```
Date	Title	Object Number	Link
ca. 1890	Portrait of a Woman	1985.12.3	https://www.museum.org/objects/123
1890-03-04	Landscape, with river	1985.12.4	http://museum.org/objects/124
1890–1895	VASE WITH LID	2001.5.1	https://museum.org/objects/125
1890-03-04	Untitled	1985.12.4	museum dot org
19th century	Study (unfinished)	2003.1.10	https://museum.org/objects/127
n.d.	Bowl	2003.1.11	https://museum.org/objects/128
500 BCE	Amphora	1950.2.1	https://museum.org/objects/129
```

**Report excerpt (`inventory_report.tsv`)**
```
Line	Column	Original	Standardized	Note
3	Object Number	1985.12.4	1985.12.4	duplicate object number (appears 2 times)
4	Title	VASE WITH LID	VASE WITH LID	title is ALL CAPS (left unchanged; review)
5	Date	03/04/1890	1890-03-04	ambiguous day/month; assumed MM/DD
5	Link	museum dot org	museum dot org	invalid URL
...
```

## Notes and customization

- **Non-destructive:** The original file is never modified. Anything the script can't confidently fix is left as-is and listed in the report.
- **European date order:** Use `--day-first` if your numeric dates are written `DD/MM/YYYY`.
- **Object number formats:** These vary a lot between institutions. Only use `--object-sep` if your numbering scheme doesn't use dashes or slashes meaningfully, as in `L-2001/3`. Otherwise just leave it off.
- **Stray quotes in titles:** If titles contain quotes like `12" vase`, use `--no-quote-parsing`. This stops the TSV reader from interpreting them as field quoting.
- **Custom header names:** If your header uses names the script doesn't recognize, add them to `HEADER_ALIASES` at the top of the script.
- **House style:** You can change the output style in a few places:
  - the `"ca. "` prefix in `standardize_date`
  - `"n.d."` for undated values
  - `BCE`/`CE` for eras
  - `--range-sep` for the range separator
