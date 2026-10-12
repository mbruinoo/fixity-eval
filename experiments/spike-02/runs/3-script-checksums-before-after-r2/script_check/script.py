#!/usr/bin/env python3
"""
standardize_years.py -- normalize the "Object Date" column and checksum every row
before and after the transformation.

Usage:
    python3 -I standardize_years.py input.csv output.csv manifest.csv

Standard form:
  * date_start / date_end: inclusive signed astronomical years (1 BCE = 0, 2 BCE = -1, ...)
  * Object Date: display string, e.g. "1896", "ca. 600–550 BCE", "1867–1933"
  * Centuries are strict spans: 18th century = 1701–1800.
  * early / mid / late = first / middle / last third of the span.
  * Anything not safely parseable is left unchanged with date_status = "review".
"""
import csv
import hashlib
import json
import re
import sys
from collections import Counter

DASHES = str.maketrans({"\u2010": "-", "\u2011": "-", "\u2013": "-", "\u2014": "-"})
QUAL_RE = re.compile(
    r"^(ca\.|c\.|probably after|probably before|probably|possibly|after|before|dated)\s+",
    re.IGNORECASE,
)
# Split on a dash, but not the hyphen inside "mid-late" or "mid-19th".
SPLIT_RE = re.compile(r"(?<!mid)(?<!late)(?<!early)\s*-\s*")
EP_RE = re.compile(
    r"^(?:(?P<mod>mid-late|early|mid|late)[\s-]+)?"
    r"(?:(?P<ord>\d{1,2})(?:st|nd|rd|th)(?:\s+century)?"
    r"|(?P<year>\d{4}|\d{3}|\d{2})(?P<dec>s)?)"
    r"(?:\s+(?P<era>B\.?C\.?(?:E\.?)?|C\.?E\.?))?$",
    re.IGNORECASE,
)


def norm(text):
    return re.sub(r"\s+", " ", text.translate(DASHES)).strip()


def result(status, display, start="", end=""):
    return {"status": status, "display": display, "start": start, "end": end}


def parse_endpoint(text):
    m = EP_RE.match(text.strip())
    if not m:
        return None
    era = m.group("era")
    return {
        "mod": (m.group("mod") or "").lower(),
        "ord": m.group("ord"),
        "year": m.group("year"),
        "dec": bool(m.group("dec")),
        "has_era": era is not None,
        "bce": era is not None and era.upper().startswith("B"),
    }


def span(ep, bce):
    """Return (earliest, latest) astronomical years for one endpoint."""
    if ep["ord"]:
        n = int(ep["ord"])
        if not 1 <= n <= 60:
            return None
        if bce:
            lo, hi = 1 - 100 * n, -100 * (n - 1)
        else:
            lo, hi = 100 * (n - 1) + 1, 100 * n
    else:
        y = int(ep["year"])
        lo = hi = (1 - y) if bce else y
        if ep["dec"]:
            hi = lo + 9
    if ep["mod"]:
        third = (hi - lo + 1) // 3
        if ep["mod"] == "early":
            hi = lo + third - 1
        elif ep["mod"] == "mid":
            lo, hi = lo + third, lo + 2 * third - 1
        elif ep["mod"] == "late":
            lo = lo + 2 * third
        elif ep["mod"] == "mid-late":
            lo = lo + third
    return lo, hi


def fmt_year(y):
    return f"{1 - y} BCE" if y <= 0 else str(y)


def fmt_span(s, e):
    if s == e:
        return fmt_year(s)
    if e <= 0:
        return f"{1 - s}–{1 - e} BCE"
    if s <= 0:
        return f"{1 - s} BCE–{e} CE"
    return f"{s}–{e}"


def parse_date(raw):
    s = norm(raw)
    if not s:
        return result("blank", raw)
    if re.fullmatch(r"n\.d\.|unknown", s, re.IGNORECASE):
        return result("undated", raw)

    qual = ""
    m = QUAL_RE.match(s)
    if m:
        qual = m.group(1).lower()
        if qual == "c.":
            qual = "ca."
        s = s[m.end():]

    parts = SPLIT_RE.split(s)
    if len(parts) > 2:
        return result("review", raw)
    eps = [parse_endpoint(p) for p in parts]
    if any(e is None for e in eps):
        return result("review", raw)

    start_ep, end_ep = eps[0], eps[-1]

    # "1933–34": expand a 2-digit end year using the start's century.
    if (len(parts) == 2 and start_ep["year"] and end_ep["year"]
            and len(start_ep["year"]) == 4 and len(end_ep["year"]) == 2):
        a = int(start_ep["year"])
        b = a // 100 * 100 + int(end_ep["year"])
        if b < a:
            b += 100
        end_ep = dict(end_ep, year=str(b))

    # Era: a start with no era inherits the end's era; an end with no era is CE.
    start_bce = (start_ep["bce"] if start_ep["has_era"]
                 else end_ep["bce"] if end_ep["has_era"] else False)
    end_bce = end_ep["bce"] if end_ep["has_era"] else False

    s1 = span(start_ep, start_bce)
    s2 = span(end_ep, end_bce)
    if s1 is None or s2 is None:
        return result("review", raw)
    start, end = s1[0], s2[1]
    if start > end:
        return result("review", raw)

    display = fmt_span(start, end)
    if qual:
        display = f"{qual} {display}"
    return result("parsed", display, start, end)


def digest(values):
    blob = json.dumps(values, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def main(src, dst, manifest_path):
    with open(src, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    try:
        di = header.index("Object Date")
        oi = header.index("Object Number")
    except ValueError as e:
        sys.exit(f"missing column: {e}")

    counts = Counter()
    out_rows, manifest = [], []

    for n, row in enumerate(rows, start=1):
        if len(row) != len(header):
            sys.exit(f"data row {n}: {len(row)} fields, expected {len(header)}")

        parsed = parse_date(row[di])
        new = list(row)
        new[di] = parsed["display"]

        before = digest(row)
        after = digest(new)
        nd_before = digest([v for i, v in enumerate(row) if i != di])
        nd_after = digest([v for i, v in enumerate(new) if i != di])
        match = nd_before == nd_after

        counts[parsed["status"]] += 1
        out_rows.append(new + [row[di], parsed["start"], parsed["end"], parsed["status"]])
        manifest.append([n, row[oi], row[di], new[di], before, after,
                         nd_before, nd_after, match, parsed["status"]])

    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header + ["Object Date (original)", "date_start", "date_end", "date_status"])
        w.writerows(out_rows)

    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["row", "object_number", "date_original", "date_standardized",
                    "sha256_before", "sha256_after",
                    "sha256_nondate_before", "sha256_nondate_after",
                    "nondate_match", "date_status"])
        w.writerows(manifest)

    print(f"rows: {len(rows)}  status: {dict(counts)}", file=sys.stderr)
    if not all(r[8] for r in manifest):
        sys.exit("ERROR: non-date fields changed in at least one row; see manifest")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: standardize_years.py input.csv output.csv manifest.csv")
    main(*sys.argv[1:4])
