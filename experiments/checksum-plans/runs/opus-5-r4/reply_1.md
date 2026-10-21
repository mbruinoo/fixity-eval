Below is a self-contained Python 3 script (`standardize_inventory.py`) that reads a 4‑column TSV (date, title, object number, link), normalizes each field according to common museum-cataloguing conventions, flags anything it can't confidently fix, and writes a clean TSV plus an optional issues report.

```python
#!/usr/bin/env python3
"""
standardize_inventory.py — clean and standardize a museum inventory TSV.

Expected columns (header names are matched loosely, or use --no-header for
positional order): date, title, object number, link

What it does
------------
* Unicode-normalizes (NFC), strips control/zero-width chars, collapses whitespace,
  and removes stray tabs/newlines so the TSV stays well-formed.
* date  : parses messy dates ("ca.1875", "1875-80", "19th c.", "n.d.", "March 4, 1875")
          into a canonical display form, plus optional machine-readable
          date_earliest / date_latest year columns.
* title : trims, fixes spacing/punctuation, unwraps surrounding quotes, converts
          SHOUTING TITLES to smart title case, flags empties.
* object number : normalizes separators and spacing without mangling the identifier;
          flags values that don't look like accession numbers; can de-duplicate.
* link  : adds missing scheme, lowercases host, drops tracking params and fragments,
          removes default ports/duplicate slashes, flags unusable URLs.

Usage
-----
    python standardize_inventory.py in.tsv -o out.tsv
    python standardize_inventory.py in.tsv -o out.tsv --derived-dates --issues-column
    python standardize_inventory.py in.tsv --report issues.tsv --dedupe --sort objnum
    python standardize_inventory.py in.tsv --check --strict      # validate only
    python standardize_inventory.py --selftest

Nothing is overwritten in place: output goes to stdout unless -o is given.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# --------------------------------------------------------------------------
# Configuration constants — edit these to match your institution's house style
# --------------------------------------------------------------------------

OUT_HEADERS = ["date", "title", "object number", "link"]
DERIVED_HEADERS = ["date_earliest", "date_latest"]
ISSUES_HEADER = "issues"

RANGE_SEP = "\u2013"          # en dash between date ranges; use "-" for plain ASCII
CIRCA = "ca. "                # house style for approximate dates
UNDATED = "undated"           # house style for no-date records

CURRENT_YEAR = datetime.date.today().year
EARLIEST_PLAUSIBLE_YEAR = 1000  # below this, dates are flagged for review

# Header aliases -> canonical field key
COLUMN_ALIASES = {
    "date": {"date", "dates", "datemade", "dateofwork", "objectdate", "creationdate",
             "yearmade", "year", "period"},
    "title": {"title", "titles", "objecttitle", "objectname", "name", "worktitle"},
    "object_number": {"objectnumber", "objectno", "objnumber", "objno", "objectid",
                      "accessionnumber", "accessionno", "accno", "accession",
                      "inventorynumber", "invno", "inventoryno", "id", "number"},
    "link": {"link", "links", "url", "uri", "weblink", "permalink", "objecturl",
             "recordurl", "collectionurl", "href", "webpage"},
}

# Query parameters stripped from links
TRACKING_PARAMS = {"fbclid", "gclid", "msclkid", "yclid", "igshid", "mc_cid",
                   "mc_eid", "_ga", "_gl", "ref_src", "ref_url"}
TRACKING_PREFIXES = ("utm_",)

NO_DATE_TOKENS = {"", "-", "--", "n/a", "na", "n.d.", "nd", "no date", "undated",
                  "unknown", "unk", "not dated", "date unknown", "none", "null"}

NO_VALUE_TOKENS = {"", "-", "--", "n/a", "na", "none", "null", "unknown", "tbd"}

# Words kept lowercase when title-casing (first/last word always capitalized)
SMALL_WORDS = {"a", "an", "and", "as", "at", "but", "by", "en", "for", "from", "if",
               "in", "into", "nor", "of", "on", "onto", "or", "over", "per", "the",
               "to", "up", "via", "vs", "with", "de", "del", "della", "des", "di",
               "du", "el", "et", "la", "le", "les", "van", "von", "der", "und"}

MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], start=1)}
MONTHS.update({m[:3]: i for m, i in list(MONTHS.items())})

# --------------------------------------------------------------------------
# Low-level text helpers
# --------------------------------------------------------------------------

CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
ZERO_WIDTH_RE = re.compile(r"[\u200b-\u200f\u2060\ufeff]")
DASH_RE = re.compile(r"[\u2010-\u2015\u2212]")
WS_RE = re.compile(r"\s+")
ROMAN_RE = re.compile(r"^[IVXLCDM]+$", re.I)
WORD_RE = re.compile(r"[^\W\d_]+(?:['\u2019][^\W\d_]+)*", re.UNICODE)


def clean_text(value) -> str:
    """NFC-normalize, strip invisible junk, collapse all whitespace, trim."""
    if value is None:
        return ""
    s = unicodedata.normalize("NFC", str(value))
    s = CONTROL_RE.sub("", s)
    s = ZERO_WIDTH_RE.sub("", s)
    s = WS_RE.sub(" ", s)          # \s also matches NBSP in Unicode mode
    return s.strip()


def straighten_quotes(s: str) -> str:
    return (s.replace("\u2018", "'").replace("\u2019", "'")
             .replace("\u201c", '"').replace("\u201d", '"')
             .replace("\u00ab", '"').replace("\u00bb", '"'))


def natural_key(s: str):
    """Sort key where embedded numbers sort numerically: 1975.2 < 1975.10."""
    return tuple(int(t) if t.isdigit() else t.casefold()
                 for t in re.split(r"(\d+)", s or ""))


def norm_header(h: str) -> str:
    return re.sub(r"[^a-z0-9]", "", clean_text(h).lower())


# --------------------------------------------------------------------------
# DATE
# --------------------------------------------------------------------------

QUALIFIER_PATTERNS = [
    (re.compile(r"^(?:c|ca|cca|circa|approx|approximately|about|around)\b\.?\s*", re.I), CIRCA),
    (re.compile(r"^(?:before|bef|ante|prior to|pre)\b\.?-?\s*", re.I), "before "),
    (re.compile(r"^(?:after|aft|post)\b\.?-?\s*", re.I), "after "),
    (re.compile(r"^(?:probably|possibly|perhaps)\b\.?\s*", re.I), "probably "),
]

CENTURY_RE = re.compile(
    r"^(?:(early|mid|middle|late|first half of(?: the)?|second half of(?: the)?)[\s-]*)?"
    r"(\d{1,2})(?:st|nd|rd|th)?[\s-]*(?:century|cent\.?|c\.)$", re.I)
DECADE_RE = re.compile(r"^(\d{3}0)'?s$")
RANGE_RE = re.compile(r"^(\d{3,4})\s*(?:-|/|to|through|until)\s*(\d{1,4})$", re.I)
ISO_RE = re.compile(r"^(\d{4})-(\d{1,2})(?:-(\d{1,2}))?$")
US_RE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
TEXT_DMY_RE = re.compile(r"^(\d{1,2})\s+([A-Za-z]{3,9})\.?,?\s+(\d{4})$")
TEXT_MDY_RE = re.compile(r"^([A-Za-z]{3,9})\.?\s+(\d{1,2}),?\s+(\d{4})$")
TEXT_MY_RE = re.compile(r"^([A-Za-z]{3,9})\.?,?\s+(\d{4})$")
BCE_RE = re.compile(r"\b(b\.?c\.?e?|bce)\b", re.I)


def _expand_short_year(start: int, tail: str) -> int:
    """1875-80 -> 1880 ; 1898-02 -> 1902 ; 1875-1880 -> 1880."""
    if len(tail) == 4:
        return int(tail)
    prefix = str(start)[: 4 - len(tail)]
    end = int(prefix + tail)
    if end < start:                     # rolled over a century/decade boundary
        end += 10 ** len(tail)
    return end


def normalize_date(raw: str):
    """Return (display, earliest_year, latest_year, [issues])."""
    issues = []
    s = clean_text(raw)
    if not s:
        return "", "", "", ["date-empty"]

    s = DASH_RE.sub("-", straighten_quotes(s))
    if s.lower().strip(" .,;:") in NO_DATE_TOKENS:
        return UNDATED, "", "", []

    if BCE_RE.search(s):                # BCE handling is institution-specific
        return s, "", "", ["date-bce-review"]

    # Peel off leading qualifiers (circa / before / after / probably)
    qualifier, body, changed = "", s, True
    while changed:
        changed = False
        for rx, label in QUALIFIER_PATTERNS:
            m = rx.match(body)
            if m:
                body = body[m.end():]
                qualifier = qualifier or label
                changed = True
    body = body.strip(" ,.;:")
    uncertain = body.endswith("?")
    body = body.rstrip("?").strip()

    def finish(display, lo, hi, extra=()):
        disp = f"{qualifier}{display}".strip()
        if uncertain:
            disp += "?"
        probs = list(extra)
        for y in (lo, hi):
            if y and not (EARLIEST_PLAUSIBLE_YEAR <= y <= CURRENT_YEAR + 1):
                probs.append("date-implausible-year")
        if qualifier == "before ":
            lo = None
        if qualifier == "after ":
            hi = None
        return disp, (lo or ""), (hi or ""), probs

    # Full / partial ISO date
    m = ISO_RE.match(body)
    if m:
        y, mo, d = int(m[1]), int(m[2]), (int(m[3]) if m[3] else None)
        if 1 <= mo <= 12 and (d is None or 1 <= d <= 31):
            disp = f"{y:04d}-{mo:02d}" + (f"-{d:02d}" if d else "")
            return finish(disp, y, y)

    m = US_RE.match(body)               # M/D/YYYY — ambiguous, flagged
    if m:
        a, b, y = int(m[1]), int(m[2]), int(m[3])
        if 1 <= a <= 12 and 1 <= b <= 31:
            return finish(f"{y:04d}-{a:02d}-{b:02d}", y, y,
                          ["date-ambiguous-md"] if b <= 12 else [])

    for rx, order in ((TEXT_DMY_RE, "dmy"), (TEXT_MDY_RE, "mdy")):
        m = rx.match(body)
        if m:
            d, mon, y = (m[1], m[2], m[3]) if order == "dmy" else (m[2], m[1], m[3])
            mo = MONTHS.get(mon.lower()[:3])
            if mo:
                return finish(f"{int(y):04d}-{mo:02d}-{int(d):02d}", int(y), int(y))

    m = TEXT_MY_RE.match(body)
    if m and m[1].lower()[:3] in MONTHS:
        y, mo = int(m[2]), MONTHS[m[1].lower()[:3]]
        return finish(f"{y:04d}-{mo:02d}", y, y)

    m = DECADE_RE.match(body)           # 1870s -> 1870–1879
    if m:
        y = int(m[1])
        return finish(f"{y}s", y, y + 9)

    m = CENTURY_RE.match(body)          # late 19th century -> 1867–1900
    if m:
        mod = (m[1] or "").lower().replace("middle", "mid")
        c = int(m[2])
        lo, hi = (c - 1) * 100 + 1, c * 100
        if mod.startswith("early"):
            hi = lo + 32
        elif mod.startswith("mid"):
            lo, hi = lo + 33, lo + 65
        elif mod.startswith("late"):
            lo = lo + 66
        elif mod.startswith("first half"):
            hi = lo + 49
        elif mod.startswith("second half"):
            lo = lo + 50
        label = f"{mod} " if mod else ""
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(c if c < 20 else c % 10, "th")
        return finish(f"{label}{c}{suffix} century".strip(), lo, hi)

    m = RANGE_RE.match(body)            # 1875-80, 1875/1880
    if m:
        lo = int(m[1])
        hi = _expand_short_year(lo, m[2])
        return finish(f"{lo}{RANGE_SEP}{hi}", lo, hi)

    if re.fullmatch(r"\d{3,4}", body):  # plain year
        y = int(body)
        return finish(str(y), y, y)

    # Unparsed: keep the cleaned text, but salvage any years for the range columns
    years = [int(y) for y in re.findall(r"\b(\d{4})\b", body)
             if EARLIEST_PLAUSIBLE_YEAR <= int(y) <= CURRENT_YEAR + 1]
    lo = min(years) if years else None
    hi = max(years) if years else None
    return finish(body or s, lo, hi, ["date-unparsed"])


# --------------------------------------------------------------------------
# TITLE
# --------------------------------------------------------------------------

def _capitalize_word(w: str, force: bool) -> str:
    if ROMAN_RE.fullmatch(w) and w.upper() != "I" or (w.upper() == "I" and len(w) == 1):
        return w.upper()                      # I, II, IV, XIV ...
    lw = w.lower()
    if not force and lw in SMALL_WORDS:
        return lw
    if lw.startswith("mc") and len(lw) > 3:
        return "Mc" + lw[2].upper() + lw[3:]
    if len(lw) > 2 and lw[1] in "'\u2019":    # O'Keeffe, D'Arcy
        return lw[0].upper() + lw[1] + lw[2].upper() + lw[3:]
    return lw[0].upper() + lw[1:]


def smart_title(text: str) -> str:
    """Heuristic title case; only applied to all-caps/all-lowercase input."""
    out, idx = [], 0
    words = list(WORD_RE.finditer(text))
    for n, m in enumerate(words):
        start, end = m.span()
        before = text[:start].rstrip()
        force = (n == 0 or n == len(words) - 1 or
                 (bool(before) and before[-1] in ":;?!\u2014\u2013-("))
        out.append(text[idx:start])
        out.append(_capitalize_word(m.group(0), force))
        idx = end
    out.append(text[idx:])
    return "".join(out)


def normalize_title(raw: str, fix_caps: bool = True, placeholder: str = ""):
    issues = []
    s = straighten_quotes(clean_text(raw))
    if s.lower() in NO_VALUE_TOKENS:
        s = ""
    if not s:
        return (placeholder or ""), ["title-empty"]

    # Unwrap a title that is entirely wrapped in quotes
    if len(s) > 1 and s[0] == s[-1] == '"':
        s = s[1:-1].strip()

    s = re.sub(r"\s+([,;:.!?])", r"\1", s)      # no space before punctuation
    s = re.sub(r"([,;:])(?=\S)", r"\1 ", s)     # space after punctuation
    s = re.sub(r"\s*\.\.\.\s*", "... ", s).strip()
    s = re.sub(r"\(\s+", "(", s)
    s = re.sub(r"\s+\)", ")", s)

    letters = [c for c in s if c.isalpha()]
    if fix_caps and len(letters) > 3:
        if all(c.isupper() for c in letters) or all(c.islower() for c in letters):
            s = smart_title(s)
            issues.append("title-recased")

    # Trailing period is not kept on titles (but "...", "Mr." etc. are preserved)
    if s.endswith(".") and not s.endswith("...") and not re.search(r"\b[A-Z]\.$", s):
        s = s[:-1].rstrip()

    if len(s) > 255:
        issues.append("title-very-long")
    return s, issues


# --------------------------------------------------------------------------
# OBJECT NUMBER
# --------------------------------------------------------------------------

# Typical accession-number shapes: 1975.1.14a-c, 2001-34, X.123, P.1984.7, 56.9.2 (1)
OBJNUM_OK_RE = re.compile(r"^[A-Za-z0-9]+(?:[.\-/_ ][A-Za-z0-9()]+)*$")


def normalize_object_number(raw: str, uppercase: bool = False):
    issues = []
    s = unicodedata.normalize("NFKC", clean_text(raw))
    if s.lower() in NO_VALUE_TOKENS:
        return "", ["objnum-empty"]

    s = DASH_RE.sub("-", s)
    s = s.replace("\u00a0", " ")
    s = re.sub(r"\s*([./\-])\s*", r"\1", s)   # "1975 . 1 - 3" -> "1975.1-3"
    s = re.sub(r"\s+", " ", s).strip(" .,;")
    s = re.sub(r"^(?:no\.?|number|acc(?:ession)?\.?\s*no\.?)\s*", "", s, flags=re.I)
    if uppercase:
        s = s.upper()
    if not s:
        return "", ["objnum-empty"]
    if not OBJNUM_OK_RE.match(s):
        issues.append("objnum-unusual-format")
    return s, issues


# --------------------------------------------------------------------------
# LINK
# --------------------------------------------------------------------------

def normalize_url(raw: str, force_https: bool = False, keep_fragment: bool = False,
                  strip_trailing_slash: bool = True):
    issues = []
    s = clean_text(raw).strip("<>\"'\u2018\u2019\u201c\u201d")
    if s.lower() in NO_VALUE_TOKENS:
        return "", ["link-empty"]

    if "://" not in s:
        if s.startswith("//"):
            s = "https:" + s
        elif re.match(r"^[\w.-]+\.[A-Za-z]{2,}(?:[:/?#]|$)", s):
            s = "https://" + s
        else:
            return s, ["link-invalid"]

    try:
        parts = urlsplit(s)
    except ValueError:
        return s, ["link-invalid"]

    scheme = parts.scheme.lower()
    if scheme not in ("http", "https"):
        return s, ["link-bad-scheme"]
    if force_https:
        scheme = "https"

    host = (parts.hostname or "").lower().rstrip(".")
    if not host or "." not in host:
        return s, ["link-invalid"]
    try:
        host = host.encode("idna").decode("ascii")
    except Exception:
        issues.append("link-nonascii-host")
    if parts.username:
        issues.append("link-credentials-removed")

    port = parts.port
    netloc = host if port in (None, 80, 443) else f"{host}:{port}"

    path = re.sub(r"/{2,}", "/", parts.path)
    if strip_trailing_slash and len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")

    query_pairs = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                   if k.lower() not in TRACKING_PARAMS
                   and not k.lower().startswith(TRACKING_PREFIXES)]
    query = urlencode(query_pairs, doseq=True)
    fragment = parts.fragment if keep_fragment else ""

    return urlunsplit((scheme, netloc, path, query, fragment)), issues


# --------------------------------------------------------------------------
# Row processing
# --------------------------------------------------------------------------

@dataclass
class Report:
    rows_in: int = 0
    rows_out: int = 0
    changed: Counter = field(default_factory=Counter)
    issues: Counter = field(default_factory=Counter)
    details: list = field(default_factory=list)   # (row_no, objnum, issue, value)

    def log(self, row_no, objnum, issue, value):
        self.issues[issue] += 1
        self.details.append((row_no, objnum, issue, value))


def process_row(row: dict, row_no: int, args, rep: Report) -> dict:
    date_disp, lo, hi, date_issues = normalize_date(row.get("date", ""))
    title, title_issues = normalize_title(row.get("title", ""),
                                          fix_caps=not args.keep_case,
                                          placeholder=args.untitled)
    objnum, obj_issues = normalize_object_number(row.get("object_number", ""),
                                                 uppercase=args.objnum_upper)
    link, link_issues = normalize_url(row.get("link", ""),
                                      force_https=args.force_https,
                                      keep_fragment=args.keep_fragment,
                                      strip_trailing_slash=not args.keep_trailing_slash)

    for key, new in (("date", date_disp), ("title", title),
                     ("object_number", objnum), ("link", link)):
        if clean_text(row.get(key, "")) != new:
            rep.changed[key] += 1

    all_issues = date_issues + title_issues + obj_issues + link_issues
    for issue in all_issues:
        source = {"date": row.get("date", ""), "titl": row.get("title", ""),
                  "objn": row.get("object_number", ""), "link": row.get("link", "")}
        rep.log(row_no, objnum, issue, clean_text(source.get(issue[:4], "")))

    return {"date": date_disp, "title": title, "object_number": objnum, "link": link,
            "date_earliest": str(lo), "date_latest": str(hi),
            "issues": "; ".join(sorted(set(all_issues)))}


# --------------------------------------------------------------------------
# Input / output
# --------------------------------------------------------------------------

def map_columns(header: list, no_header: bool) -> dict:
    """Return {canonical_field: column_index}."""
    if no_header:
        if len(header) < 4:
            sys.exit("ERROR: --no-header requires at least 4 columns "
                     "in the order date, title, object number, link.")
        return {"date": 0, "title": 1, "object_number": 2, "link": 3}

    mapping, used = {}, set()
    normalized = [norm_header(h) for h in header]
    for field_name, aliases in COLUMN_ALIASES.items():
        for i, h in enumerate(normalized):
            if i not in used and h in aliases:
                mapping[field_name] = i
                used.add(i)
                break
    missing = [f for f in COLUMN_ALIASES if f not in mapping]
    if missing:
        if len(header) >= 4:
            print(f"WARNING: could not match header(s) {missing}; "
                  f"falling back to positional order for those columns.",
                  file=sys.stderr)
            for i, f in enumerate(["date", "title", "object_number", "link"]):
                mapping.setdefault(f, i)
        else:
            sys.exit(f"ERROR: missing required column(s): {missing}")
    return mapping


def read_rows(path, no_header):
    opener = (lambda: open(path, newline="", encoding="utf-8-sig")) if path != "-" \
        else (lambda: sys.stdin)
    with opener() as fh:
        reader = csv.reader(fh, delimiter="\t", quotechar='"')
        try:
            first = next(reader)
        except StopIteration:
            return [], {}
        if len(first) == 1 and "," in first[0]:
            print("WARNING: input looks comma-separated, not tab-separated.",
                  file=sys.stderr)
        mapping = map_columns(first, no_header)
        rows = []
        if no_header:
            rows.append(first)
        rows.extend(r for r in reader if any(c.strip() for c in r))
        out = []
        for r in rows:
            out.append({f: (r[i] if i < len(r) else "") for f, i in mapping.items()})
        return out, mapping


def write_rows(rows, path, headers, keys):
    fh = open(path, "w", newline="", encoding="utf-8") if path else sys.stdout
    try:
        if fh is sys.stdout and hasattr(fh, "reconfigure"):
            fh.reconfigure(newline="")
        w = csv.writer(fh, delimiter="\t", lineterminator="\n",
                       quotechar='"', quoting=csv.QUOTE_MINIMAL)
        w.writerow(headers)
        for r in rows:
            w.writerow([r.get(k, "") for k in keys])
    finally:
        if fh is not sys.stdout:
            fh.close()


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", nargs="?", help="input .tsv ('-' for stdin)")
    p.add_argument("-o", "--output", help="output .tsv (default: stdout)")
    p.add_argument("--no-header", action="store_true",
                   help="input has no header row; assume positional column order")
    p.add_argument("--derived-dates", action="store_true",
                   help="add date_earliest / date_latest year columns")
    p.add_argument("--issues-column", action="store_true",
                   help="add an 'issues' column to the output")
    p.add_argument("--report", help="write a TSV of flagged rows to this path")
    p.add_argument("--dedupe", action="store_true",
                   help="drop later rows with a duplicate object number")
    p.add_argument("--sort", choices=["none", "objnum", "date", "title"],
                   default="none", help="sort output rows (default: none)")
    p.add_argument("--keep-case", action="store_true",
                   help="never re-case ALL-CAPS titles")
    p.add_argument("--untitled", default="",
                   help="placeholder for empty titles, e.g. 'Untitled'")
    p.add_argument("--objnum-upper", action="store_true",
                   help="uppercase object numbers")
    p.add_argument("--force-https", action="store_true",
                   help="rewrite http:// links as https://")
    p.add_argument("--keep-fragment", action="store_true",
                   help="keep #fragments in links")
    p.add_argument("--keep-trailing-slash", action="store_true",
                   help="keep trailing slashes in link paths")
    p.add_argument("--check", action="store_true",
                   help="validate and report only; write no output file")
    p.add_argument("--strict", action="store_true",
                   help="exit with status 1 if any issues were found")
    p.add_argument("--quiet", action="store_true", help="suppress the summary")
    p.add_argument("--selftest", action="store_true", help="run built-in tests")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.input:
        build_parser().error("input file required (or use --selftest)")

    rows, _ = read_rows(args.input, args.no_header)
    rep = Report(rows_in=len(rows))

    processed, seen = [], {}
    for n, row in enumerate(rows, start=1 if args.no_header else 2):
        out = process_row(row, n, args, rep)
        key = out["object_number"].casefold()
        if key:
            if key in seen:
                rep.log(n, out["object_number"], "objnum-duplicate",
                        f"first seen on row {seen[key]}")
                if args.dedupe:
                    continue
            else:
                seen[key] = n
        processed.append(out)

    if args.sort == "objnum":
        processed.sort(key=lambda r: natural_key(r["object_number"]))
    elif args.sort == "date":
        processed.sort(key=lambda r: (r["date_earliest"] == "",
                                      r["date_earliest"], natural_key(r["title"])))
    elif args.sort == "title":
        processed.sort(key=lambda r: natural_key(r["title"]))

    rep.rows_out = len(processed)

    keys = ["date", "title", "object_number", "link"]
    headers = list(OUT_HEADERS)
    if args.derived_dates:
        keys += ["date_earliest", "date_latest"]
        headers += DERIVED_HEADERS
    if args.issues_column:
        keys.append("issues")
        headers.append(ISSUES_HEADER)

    if not args.check:
        write_rows(processed, args.output, headers, keys)

    if args.report:
        with open(args.report, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, delimiter="\t", lineterminator="\n")
            w.writerow(["row", "object number", "issue", "original value"])
            w.writerows(rep.details)

    if not args.quiet:
        print(f"rows read: {rep.rows_in}   rows written: {rep.rows_out}",
              file=sys.stderr)
        if rep.changed:
            print("values normalized: " + ", ".join(
                f"{k}={v}" for k, v in sorted(rep.changed.items())), file=sys.stderr)
        if rep.issues:
            print("flags:", file=sys.stderr)
            for issue, count in rep.issues.most_common():
                print(f"  {count:>6}  {issue}", file=sys.stderr)
        else:
            print("no issues flagged.", file=sys.stderr)

    return 1 if (args.strict and rep.issues) else 0


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------

def selftest() -> int:
    cases_date = [
        ("ca.1875", f"{CIRCA}1875", 1875, 1875),
        ("1875-80", f"1875{RANGE_SEP}1880", 1875, 1880),
        ("1898-02", f"1898{RANGE_SEP}1902", 1898, 1902),
        ("n.d.", UNDATED, "", ""),
        ("late 19th c.", "late 19th century", 1867, 1900),
        ("1870s", "1870s", 1870, 1879),
        ("March 4, 1875", "1875-03-04", 1875, 1875),
        ("before 1900", "before 1900", "", 1900),
    ]
    for raw, disp, lo, hi in cases_date:
        d, a, b, _ = normalize_date(raw)
        assert d == disp, (raw, d, disp)
        assert str(a) == str(lo) and str(b) == str(hi), (raw, a, b)

    assert normalize_title("  THE  STARRY   NIGHT ")[0] == "The Starry Night"
    assert normalize_title('"Self-Portrait".')[0] == "Self-Portrait"
    assert normalize_title("VIEW OF O'KEEFFE'S HOUSE")[0] == "View of O'Keeffe's House"

    assert normalize_object_number(" 1975 . 1 . 14a-c ")[0] == "1975.1.14a-c"
    assert normalize_object_number("no. 2001\u201334")[0] == "2001-34"

    assert normalize_url("www.metmuseum.org/art/436532/?utm_source=x")[0] == \
        "https://www.metmuseum.org/art/436532"
    assert normalize_url("HTTPS://Example.ORG:443/A/B//c#top")[0] == \
        "https://example.org/A/B/c"

    print("selftest: all checks passed", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Typical run

```bash
# clean + add machine-readable year columns + an audit trail
python standardize_inventory.py inventory.tsv \
    -o inventory_clean.tsv \
    --derived-dates --issues-column --report issues.tsv --sort objnum
```

```
rows read: 4,812   rows written: 4,812
values normalized: date=1904, link=2380, object_number=311, title=742
flags:
   1204  date-unparsed
     88  link-empty
     31  objnum-unusual-format
      6  objnum-duplicate
```

## Notes on the design choices

- **Nothing is silently discarded.** When a date can't be parsed, the cleaned original text is kept and the row is flagged (`date-unparsed`) rather than blanked — curatorial data loss is worse than untidy data.
- **Object numbers are treated as identifiers**, so only whitespace/separator noise is removed; case changes and re-formatting are opt-in (`--objnum-upper`).
- **Title re-casing only fires on all-caps or all-lowercase titles**, where the original capitalization carries no information. Mixed-case titles are left alone apart from spacing/punctuation fixes.
- **Century conventions** are the common Anglophone ones (19th century = 1801–1900; early/mid/late = thirds). Edit `CENTURY_RE` handling if your institution uses 1800–1899.
- **Round-trip safety:** tabs, newlines, and zero-width characters are stripped from every cell, so the output is always a valid 4-column TSV.
- To adapt it, the top-of-file constants (`RANGE_SEP`, `CIRCA`, `UNDATED`, `COLUMN_ALIASES`, `SMALL_WORDS`, `TRACKING_PARAMS`) are the main knobs; `--selftest` verifies the normalizers still behave after you edit them.
