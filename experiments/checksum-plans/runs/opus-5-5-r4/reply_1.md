# Museum Inventory Standardizer

This is a Python 3 script that uses only the standard library. It reads a `.tsv` with **date, title, object number, and link** columns and writes two files:

1. **A cleaned TSV** with the same four columns.
2. **A change report** (TSV) that lists every edit and every value that needs a human to review it. Values it can't confidently fix are left unchanged and flagged.

```python
#!/usr/bin/env python3
"""
standardize_inventory.py - Clean and standardize a museum inventory TSV.

Expected columns: date, title, object number, link
(header names are matched flexibly; if there is no header, column order is assumed)

Outputs:
  <input>_standardized.tsv   cleaned data
  <input>_report.tsv         every change + every value flagged for review

Dates are converted to EDTF (Extended Date/Time Format, Library of Congress),
which is sortable and expresses museum-style uncertainty:
  c. 1850 -> 1850~     1850? -> 1850?     1850-60 -> 1850/1860
  1850s   -> 185X      19th century -> 18XX   March 3, 1921 -> 1921-03-03

Usage:
  python standardize_inventory.py inventory.tsv
  python standardize_inventory.py inventory.tsv --dayfirst --objnum-sep . --check-links
"""

import argparse
import csv
import io
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

# --------------------------------------------------------------------------
# Column / header handling
# --------------------------------------------------------------------------

COLUMNS = ["date", "title", "object_number", "link"]
OUTPUT_HEADER = ["date", "title", "object number", "link"]

HEADER_ALIASES = {
    "date": {"date", "dates", "date made", "creation date", "object date",
             "dated", "production date"},
    "title": {"title", "object title", "name", "object name", "work title"},
    "object_number": {"object number", "object no", "object no.", "objectnumber",
                      "object #", "accession number", "accession no",
                      "accession no.", "accession #", "inventory number",
                      "inventory no", "object id", "id", "number", "catalog number"},
    "link": {"link", "url", "uri", "web link", "permalink", "website", "web page"},
}

WS_RE = re.compile(r"\s+")


def norm_header(h: str) -> str:
    h = h.replace("\ufeff", "").replace("_", " ").strip().lower()
    return WS_RE.sub(" ", h)


def clean_text(s: str) -> str:
    """Unicode-normalize, remove invisible chars, collapse all whitespace."""
    s = unicodedata.normalize("NFC", s or "")
    s = s.replace("\u200b", "").replace("\ufeff", "")
    return WS_RE.sub(" ", s).strip()


def read_text(path: Path):
    data = path.read_bytes()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return data.decode(enc), enc
        except UnicodeDecodeError:
            continue
    raise RuntimeError("Could not decode file")


# --------------------------------------------------------------------------
# Dates -> EDTF
# --------------------------------------------------------------------------

MONTH_NAMES = ["january", "february", "march", "april", "may", "june", "july",
               "august", "september", "october", "november", "december"]
MONTHS = {}
for _i, _n in enumerate(MONTH_NAMES, 1):
    MONTHS[_n] = _i
    MONTHS[_n[:3]] = _i
MONTHS["sept"] = 9

UNDATED = {"n.d.", "n.d", "nd", "undated", "unknown", "unk", "?", "n/a", "na",
           "none", "no date", "-", "--", "s.d."}
CIRCA_RE = re.compile(
    r"^(?:circa|ca\.?|c\.?|approx(?:imately|\.)?|about|around)\s*(?=\d)", re.I)
UNCERTAIN_RE = re.compile(r"\s*(?:\(\?\)|\?)$")
EDTF_UNIT = r"(?:\d{4}(?:-\d{2}(?:-\d{2})?)?|\d{3}X|\d{2}XX)[~?%]?"
EDTF_RE = re.compile(rf"{EDTF_UNIT}(?:/{EDTF_UNIT})?")
RANGE_SEP = r"\s*(?:-|–|—|/|to|until|through)\s*"


def _valid_edtf(s: str) -> bool:
    if not EDTF_RE.fullmatch(s):
        return False
    for unit in s.split("/"):
        parts = unit.rstrip("~?%").split("-")
        if len(parts) >= 2 and not 1 <= int(parts[1]) <= 12:
            return False
        if len(parts) == 3:
            try:
                date(int(parts[0]), int(parts[1]), int(parts[2]))
            except ValueError:
                return False
    return True


def _ymd(y, mo, d, note=None):
    try:
        return date(y, mo, d).isoformat(), note
    except ValueError:
        return None, "invalid calendar date; left unchanged"


def _parse_core(w: str, dayfirst: bool):
    """Return (edtf_string, note) or (None, note)."""
    w = WS_RE.sub(" ", w.replace(",", " ")).strip()
    lw = w.lower()

    # between 1850 and 1860
    m = re.fullmatch(r"between (\d{4}) and (\d{4})", lw)
    if m and int(m.group(2)) > int(m.group(1)):
        return f"{m.group(1)}/{m.group(2)}", None

    # 1850-1860, 1850–60, 1850 to 1860
    m = re.fullmatch(rf"(\d{{4}}){RANGE_SEP}(\d{{4}}|\d{{2}})", lw)
    if m:
        a, bs = int(m.group(1)), m.group(2)
        b = int(bs) if len(bs) == 4 else a // 100 * 100 + int(bs)
        if b > a:
            return f"{a:04d}/{b:04d}", ("expanded abbreviated range" if len(bs) == 2 else None)
        if b == a:
            return f"{a:04d}", None
        # otherwise fall through (e.g. "1850/12" may be a month)

    # 1850s-1860s
    m = re.fullmatch(rf"(\d{{3}})0'?s{RANGE_SEP}(\d{{3}})0'?s", lw)
    if m:
        return f"{m.group(1)}X/{m.group(2)}X", None

    # YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD
    m = re.fullmatch(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", w)
    if m:
        return _ymd(*map(int, m.groups()))

    # YYYY-MM
    m = re.fullmatch(r"(\d{4})[-/.](\d{1,2})", w)
    if m and 1 <= int(m.group(2)) <= 12:
        return f"{m.group(1)}-{int(m.group(2)):02d}", None

    # MM/DD/YYYY or DD/MM/YYYY
    m = re.fullmatch(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})", w)
    if m:
        a, b, y = map(int, m.groups())
        note = None
        if a > 12 and b <= 12:
            d, mo = a, b
        elif b > 12 and a <= 12:
            mo, d = a, b
        elif a <= 12 and b <= 12:
            mo, d = (b, a) if dayfirst else (a, b)
            if a != b:
                note = f"ambiguous day/month; read as {'DD/MM' if dayfirst else 'MM/DD'}"
        else:
            return None, "invalid day/month; left unchanged"
        return _ymd(y, mo, d, note)

    if re.fullmatch(r"\d{1,2}[-/.]\d{1,2}[-/.]\d{2}", w):
        return None, "two-digit year (century ambiguous); left unchanged"

    # 3 March 1921 / 3rd March 1921
    m = re.fullmatch(r"(\d{1,2})(?:st|nd|rd|th)? ([a-z]+)\.? (\d{4})", lw)
    if m and m.group(2) in MONTHS:
        return _ymd(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1)))

    # March 3, 1921 / Mar. 3rd 1921
    m = re.fullmatch(r"([a-z]+)\.? (\d{1,2})(?:st|nd|rd|th)? (\d{4})", lw)
    if m and m.group(1) in MONTHS:
        return _ymd(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))

    # March 1921
    m = re.fullmatch(r"([a-z]+)\.? (\d{4})", lw)
    if m and m.group(1) in MONTHS:
        return f"{m.group(2)}-{MONTHS[m.group(1)]:02d}", None

    # 1850s / 1850's
    m = re.fullmatch(r"(\d{3})0'?s", lw)
    if m:
        return f"{m.group(1)}X", None

    # 19th century / 19th c.
    m = re.fullmatch(r"(\d{1,2})(?:st|nd|rd|th) (?:century|cent\.?|c\.?)", lw)
    if m and 1 <= int(m.group(1)) <= 21:
        return f"{int(m.group(1)) - 1:02d}XX", None

    # bare year (3-4 digits)
    m = re.fullmatch(r"\d{3,4}", w)
    if m:
        return f"{int(w):04d}", None

    return None, None


def standardize_date(raw: str, dayfirst: bool = False):
    s = clean_text(raw)
    if not s:
        return "", None
    if s.lower() in UNDATED:
        return "", f"undated marker '{s}' cleared"
    if _valid_edtf(s):  # already standard -> idempotent
        if re.fullmatch(r"\d{4}-\d{2}", s):
            return s, "read as year-month; if this is a range, write YYYY/YYYY"
        return s, None

    notes = []
    work = s.translate(str.maketrans("–—", "--"))
    if work.startswith("[") and work.endswith("]"):
        work = work[1:-1].strip()
        notes.append("brackets removed (supplied/inferred date?)")

    circa = uncertain = False
    m = CIRCA_RE.match(work)
    if m:
        circa = True
        work = work[m.end():]
    if UNCERTAIN_RE.search(work):
        uncertain = True
        work = UNCERTAIN_RE.sub("", work)
    work = work.rstrip(".").strip()

    core, note = _parse_core(work, dayfirst)
    if core is None:
        return s, note or "unrecognized date format; left unchanged"
    if note:
        notes.append(note)

    q = "%" if (circa and uncertain) else "~" if circa else "?" if uncertain else ""
    result = "/".join(part + q for part in core.split("/"))
    return result, "; ".join(notes) or None


# --------------------------------------------------------------------------
# Titles
# --------------------------------------------------------------------------

QUOTE_PAIRS = [('"', '"'), ("“", "”"), ("'", "'"), ("‘", "’")]
ASCII_QUOTES = str.maketrans({"“": '"', "”": '"', "„": '"', "‘": "'", "’": "'"})


def standardize_title(raw: str, ascii_quotes: bool = False):
    s = clean_text(raw)
    notes = []
    for a, b in QUOTE_PAIRS:
        inner = s[1:-1]
        if len(s) >= 2 and s.startswith(a) and s.endswith(b) and a not in inner and b not in inner:
            s = inner.strip()
            break
    if ascii_quotes:
        s = s.translate(ASCII_QUOTES)
    if not s:
        notes.append("missing title")
    elif s.isupper() and len(s) > 3:
        notes.append("ALL CAPS; review casing (not auto-changed)")
    return s, "; ".join(notes) or None


# --------------------------------------------------------------------------
# Object numbers
# --------------------------------------------------------------------------

DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−"), "-")
LABEL_RE = re.compile(
    r"^(?:obj(?:ect)?\.?\s*(?:no\.?|number|#)|acc(?:ession)?\.?\s*(?:no\.?|number|#)"
    r"|inv(?:entory)?\.?\s*(?:no\.?|number|#)|no\.|#)\s*[:#]?\s*", re.I)


def standardize_objnum(raw: str, sep=None, upper=False):
    s = clean_text(unicodedata.normalize("NFKC", raw or "")).translate(DASHES)
    s = LABEL_RE.sub("", s)
    s = re.sub(r"\s*([.\-/])\s*", r"\1", s)  # "1985 . 12" -> "1985.12"
    if sep:
        s = re.sub(r"(?<=[0-9A-Za-z])[.\-/ ](?=[0-9A-Za-z])", sep, s)
    if upper:
        s = s.upper()
    return s, ("missing object number" if not s else None)


# --------------------------------------------------------------------------
# Links
# --------------------------------------------------------------------------

TRACKING_PARAMS = re.compile(r"^(utm_\w+|fbclid|gclid|mc_cid|mc_eid|_ga)$", re.I)
BARE_DOMAIN_RE = re.compile(r"^[\w-]+(\.[\w-]+)+(:\d+)?(/|$)")


def standardize_link(raw: str, force_https: bool = True):
    s = clean_text(raw).strip("<>\"' ").rstrip(".,;")
    if not s:
        return "", None
    s = s.replace(" ", "%20")
    if not re.match(r"^[a-z][a-z0-9+.-]*://", s, re.I):
        if s.lower().startswith("www.") or BARE_DOMAIN_RE.match(s):
            s = "https://" + s
        else:
            return clean_text(raw), "not a recognizable URL; left unchanged"

    p = urlsplit(s)
    if p.scheme.lower() not in ("http", "https") or not p.netloc:
        return clean_text(raw), "invalid URL; left unchanged"

    scheme = "https" if force_https else p.scheme.lower()
    netloc = p.netloc.lower()
    path = quote(p.path, safe="/%:@!$&'()*+,;=-._~")
    query = urlencode([(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
                       if not TRACKING_PARAMS.match(k)])
    return urlunsplit((scheme, netloc, path, query, p.fragment)), None


def check_links(urls, timeout=10.0, workers=8):
    """Return {url: note_or_None}. Uses HEAD, falls back to GET."""
    import urllib.error
    import urllib.request
    from concurrent.futures import ThreadPoolExecutor

    def check(u):
        for method in ("HEAD", "GET"):
            try:
                req = urllib.request.Request(
                    u, method=method,
                    headers={"User-Agent": "Mozilla/5.0 (inventory-link-checker)"})
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    final = r.geturl()
                    return u, (f"redirects to {final}" if final.rstrip("/") != u.rstrip("/") else None)
            except urllib.error.HTTPError as e:
                if method == "HEAD" and e.code in (403, 405, 501):
                    continue
                return u, f"link check failed: HTTP {e.code}"
            except Exception as e:  # noqa: BLE001
                if method == "HEAD":
                    continue
                return u, f"link check failed: {type(e).__name__}"
        return u, "link check failed"

    with ThreadPoolExecutor(max_workers=workers) as ex:
        return dict(ex.map(check, urls))


# --------------------------------------------------------------------------
# Sorting helpers
# --------------------------------------------------------------------------

def natural_key(s: str):
    return [(0, int(t)) if t.isdigit() else (1, t.casefold())
            for t in re.split(r"(\d+)", s) if t]


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Standardize a museum inventory TSV.")
    p.add_argument("input", help="input .tsv file")
    p.add_argument("-o", "--output", help="output TSV (default: <input>_standardized.tsv)")
    p.add_argument("-r", "--report", help="report TSV (default: <input>_report.tsv)")
    p.add_argument("--dayfirst", action="store_true",
                   help="read ambiguous numeric dates as DD/MM/YYYY (default MM/DD/YYYY)")
    p.add_argument("--objnum-sep", metavar="CHAR",
                   help="unify object-number separators (space, -, /, .) to CHAR, e.g. '.'")
    p.add_argument("--objnum-upper", action="store_true",
                   help="uppercase object numbers (off by default: lowercase "
                        "part suffixes like '1985.12.3a' are often meaningful)")
    p.add_argument("--ascii-quotes", action="store_true",
                   help="convert curly quotes in titles to straight quotes")
    p.add_argument("--keep-http", action="store_true",
                   help="don't upgrade http:// links to https://")
    p.add_argument("--check-links", action="store_true",
                   help="request each link and flag broken ones/redirects")
    p.add_argument("--timeout", type=float, default=10.0, help="link-check timeout (s)")
    p.add_argument("--sort", choices=["none", "object_number", "date", "title"],
                   default="none", help="sort output rows")
    return p.parse_args()


def main():
    args = parse_args()
    in_path = Path(args.input)
    out_path = Path(args.output) if args.output else in_path.with_name(in_path.stem + "_standardized.tsv")
    rep_path = Path(args.report) if args.report else in_path.with_name(in_path.stem + "_report.tsv")

    text, enc = read_text(in_path)
    reader = csv.reader(io.StringIO(text, newline=""), delimiter="\t")
    records = [(reader.line_num, r) for r in reader]
    records = [(n, r) for n, r in records if any(c.strip() for c in r)]
    if not records:
        sys.exit("Input file is empty.")

    # --- header detection ---
    first = [norm_header(c) for c in records[0][1]]
    mapping = {}
    for idx, h in enumerate(first):
        for col, aliases in HEADER_ALIASES.items():
            if h in aliases and col not in mapping:
                mapping[col] = idx
                break
    if len(mapping) >= 2:
        missing = [c for c in COLUMNS if c not in mapping]
        if missing:
            sys.exit(f"Header found, but couldn't identify column(s): {', '.join(missing)}. "
                     f"Header was: {records[0][1]}")
        has_header = True
        extra = [records[0][1][i] for i in range(len(first)) if i not in mapping.values()]
        if any(e.strip() for e in extra):
            print(f"Warning: extra columns not included in output: {extra}", file=sys.stderr)
        data = records[1:]
    else:
        has_header = False
        mapping = {c: i for i, c in enumerate(COLUMNS)}
        print("No recognizable header; assuming column order: date, title, object number, link",
              file=sys.stderr)
        data = records

    report = []

    def log(line, col, before, after, note=None):
        if before != after or note:
            report.append([line, col, before, after, note or "standardized"])

    # --- per-row standardization ---
    out_rows = []
    for line, r in data:
        if not has_header and len(r) > 4 and any(c.strip() for c in r[4:]):
            log(line, "(row)", " | ".join(r[4:]), "",
                f"{len(r)} cells found; cells after the 4th were dropped")

        raw = {c: (r[mapping[c]] if mapping[c] < len(r) else "") for c in COLUMNS}
        new = {}

        new["date"], note = standardize_date(raw["date"], args.dayfirst)
        log(line, "date", raw["date"], new["date"], note)

        new["title"], note = standardize_title(raw["title"], args.ascii_quotes)
        log(line, "title", raw["title"], new["title"], note)

        new["object_number"], note = standardize_objnum(raw["object_number"],
                                                        args.objnum_sep, args.objnum_upper)
        log(line, "object_number", raw["object_number"], new["object_number"], note)

        new["link"], note = standardize_link(raw["link"], force_https=not args.keep_http)
        log(line, "link", raw["link"], new["link"], note)

        out_rows.append((line, new))

    # --- duplicate detection ---
    for col in ("object_number", "link"):
        groups = defaultdict(list)
        for line, rec in out_rows:
            if rec[col]:
                groups[rec[col].casefold()].append((line, rec[col]))
        for items in groups.values():
            if len(items) > 1:
                lines = [str(l) for l, _ in items]
                for l, val in items:
                    others = ", ".join(x for x in lines if x != str(l))
                    log(l, col, val, val, f"duplicate {col.replace('_', ' ')} (also on line {others})")

    # --- optional link checking ---
    if args.check_links:
        urls = sorted({rec["link"] for _, rec in out_rows if rec["link"].startswith("http")})
        print(f"Checking {len(urls)} links...", file=sys.stderr)
        results = check_links(urls, timeout=args.timeout)
        for line, rec in out_rows:
            note = results.get(rec["link"])
            if note:
                log(line, "link", rec["link"], rec["link"], note)

    # --- sorting ---
    if args.sort != "none":
        out_rows.sort(key=lambda lr: (lr[1][args.sort] == "", natural_key(lr[1][args.sort])))

    # --- write output ---
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(OUTPUT_HEADER)
        for _, rec in out_rows:
            w.writerow([rec[c] for c in COLUMNS])

    report.sort(key=lambda x: (x[0], COLUMNS.index(x[1]) if x[1] in COLUMNS else -1))
    with rep_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["input line", "column", "original", "standardized", "note"])
        w.writerows(report)

    # --- summary ---
    changed = defaultdict(int)
    flagged = 0
    for _, col, before, after, note in report:
        if before != after:
            changed[col] += 1
        if note != "standardized":
            flagged += 1
    print(f"Read {len(out_rows)} rows (encoding: {enc})")
    for col in COLUMNS:
        print(f"  {col:<14} {changed[col]:>5} values changed")
    print(f"  {flagged} items flagged for review")
    print(f"Output: {out_path}")
    print(f"Report: {rep_path}")


if __name__ == "__main__":
    main()
```

## Usage

```bash
# Basic
python standardize_inventory.py inventory.tsv

# European-style dates, unify accession numbers to dots, verify links, sort
python standardize_inventory.py inventory.tsv --dayfirst --objnum-sep . --check-links --sort object_number
```

## What it does

| Column | Standardization | Flagged for review |
|---|---|---|
| **Date** | `c. 1850` → `1850~` · `1850?` → `1850?` · `1850-60` → `1850/1860` · `1920s` → `192X` · `19th century` → `18XX` · `March 3, 1921` → `1921-03-03` · `n.d.` → blank | Ambiguous `03/04/1921`, two-digit years, "late 19th century" and other unparseable values (these are left unchanged) |
| **Title** | Trims and collapses whitespace, normalizes Unicode, strips wrapping quotes, optionally converts curly quotes to straight ones | Missing titles, ALL CAPS titles (casing is not changed automatically, because artwork titles have their own conventions) |
| **Object number** | Trims whitespace, normalizes dashes, removes labels like "Acc. No.:", tightens `1985 . 12` to `1985.12`, optionally unifies separators | Missing or duplicate numbers |
| **Link** | Adds `https://` to bare domains, lowercases the host, encodes spaces, removes `utm_*`/`fbclid` tracking parameters | Invalid URLs, duplicates, and broken links or redirects (with `--check-links`) |

## Design choices to know about

- **EDTF dates.** EDTF is a Library of Congress standard. It sorts correctly and can express "circa", "uncertain", and ranges, which plain ISO dates cannot.
- **Unparseable values are kept unchanged and flagged.** Nothing is silently lost, and the report shows each original value next to its standardized version.
- **Accession-number case is preserved by default.** Lowercase suffixes like `1985.12.3a` often indicate object parts.
- **Running it twice is safe.** Values that are already standardized pass through unchanged.
- **Not handled:** BCE dates and qualifiers like "early/mid/late 19th century". These are flagged so a person can review them.
