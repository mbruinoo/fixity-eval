I wrote a script that parses each `Object Date` into a standard form and writes SHA-256 checksums for each row before and after the change. I couldn't execute it here, so run it on your file and check `review.csv` for anything it couldn't parse.

Save the data as `input.csv` (the pasted rows with the header line) and run:

```bash
python3 standardize_years.py input.csv out/
```

## Script: `standardize_years.py`

```python
#!/usr/bin/env python3
"""
Standardize the 'Object Date' column of the collection CSV.

Standard form for the date column:
  - single year:            "1896"
  - qualifier kept:         "ca. 1896", "probably after 1657"
  - year range:             "1830–1840", "1701–1800" (centuries expanded)
  - BCE range:              "600–550 BCE", "1981–1550 BCE"
  - mixed era:              "50 BCE–50 CE"
  - undated (n.d./blank):   empty cell, status "undated"
  - not confidently parsed: original text kept, status "review"

Checksums (SHA-256 over the canonical JSON of each row):
  - sha256_before          full original row
  - sha256_after           full transformed row
  - sha256_nondate_before  non-date fields before
  - sha256_nondate_after   non-date fields after (must equal the 'before' value)

Usage:
  python3 standardize_years.py input.csv outdir/

Outputs in outdir/:
  standardized.csv   transformed data
  manifest.csv       per-row checksums and date mapping
  review.csv         rows whose date needs a human decision
"""
import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

EXPECTED_HEADER = ["Object Date", "Title", "Artist Display Name",
                   "Object Number", "Link Resource"]
NEW_HEADER = ["Object Date", "Year Start", "Year End", "Date Status",
              "Title", "Artist Display Name", "Object Number", "Link Resource"]

MONTHS = ("January|February|March|April|May|June|July|August|"
          "September|October|November|December")

QUAL_RE = re.compile(
    r"\b(mid-late|original dated|probably|dated|or later|ca\.|c\.|"
    r"after|before|early|mid|late)(?=\W|$)",
    re.IGNORECASE,
)
MONTH_RE = re.compile(rf"\b(?:{MONTHS})\b\s*(?:\d{{1,2}}\b,?\s*)?", re.IGNORECASE)


def review(raw, reason):
    return {"start": None, "end": None, "display": raw,
            "status": "review", "note": reason}


def parse_date(raw):
    s = raw.replace("\u2013", "-").replace("\u2014", "-")
    s = re.sub(r"\s+", " ", s).strip()

    if s == "" or s.lower() in ("n.d.", "unknown"):
        return {"start": None, "end": None, "display": "",
                "status": "undated", "note": ""}

    quals = [m.group(1).lower() for m in QUAL_RE.finditer(s)]
    body = QUAL_RE.sub(" ", s)
    body = MONTH_RE.sub(" ", body)
    is_bce = bool(re.search(r"\bB\.?\s*C", body, re.IGNORECASE))
    body = re.sub(r"\bB\.?\s*C\.?(?:E\.?)?", " ", body, flags=re.IGNORECASE)
    body = re.sub(r"\bCE\b\.?", " ", body)
    body = re.sub(r"\s+", " ", body).strip(" ,.;")

    if "or later" in quals:
        return review(raw, "open-ended date ('or later')")
    if any(c in body for c in "()/;"):
        return review(raw, "parenthetical or multiple dates")

    qual = " ".join(quals)

    def fmt_year(y):
        return f"{-y} BCE" if y < 0 else str(y)

    def fmt_range(start, end):
        if start == end:
            return fmt_year(start)
        if start < 0 and end < 0:
            return f"{-start}–{-end} BCE"
        return f"{fmt_year(start)}–{fmt_year(end)}"

    def ok(start, end, status="ok", note=""):
        display = fmt_range(start, end)
        if qual:
            display = f"{qual} {display}"
        return {"start": start, "end": end, "display": display,
                "status": status, "note": note}

    # Centuries: "18th century", "late 19th–early 20th century", "3rd–1st century BCE"
    if re.search(r"century", body, re.IGNORECASE):
        ords = [int(n) for n in re.findall(r"(\d+)(?:st|nd|rd|th)\b", body)]
        leftover = re.sub(r"(\d+)(?:st|nd|rd|th)\b|century|-", "",
                          body, flags=re.IGNORECASE).strip()
        if not ords or leftover:
            return review(raw, "unrecognized century expression")
        firsts, lasts = [], []
        for n in ords:
            if is_bce:
                firsts.append(-(n * 100))
                lasts.append(-((n - 1) * 100 + 1))
            else:
                firsts.append((n - 1) * 100 + 1)
                lasts.append(n * 100)
        return ok(min(firsts), max(lasts), status="century_range",
                  note="expanded to full century; early/mid/late not applied")

    # Decades: "1960s"
    m = re.fullmatch(r"(\d{3})0s", body.replace(" ", ""))
    if m:
        start = int(m.group(1)) * 10
        return ok(start, start + 9)

    # Ranges: "1830–40", "1851-1853", "1981-1550 BCE"
    compact = body.replace(" ", "")
    m = re.fullmatch(r"(\d{1,4})-(\d{1,4})", compact)
    if m:
        a, b = m.group(1), m.group(2)
        if len(b) < len(a):                       # "1880-92" -> "1892"
            b = a[:len(a) - len(b)] + b
        y1, y2 = int(a), int(b)
        if is_bce:
            y1, y2 = -y1, -y2
        elif y2 < y1:
            return review(raw, "range end before start")
        return ok(min(y1, y2), max(y1, y2))

    # Single year: "1896", "1935"
    m = re.fullmatch(r"(\d{1,4})", compact)
    if m:
        y = int(m.group(1))
        if is_bce:
            y = -y
        return ok(y, y)

    return review(raw, "unrecognized date format")


def row_hash(fields):
    payload = json.dumps(fields, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("outdir")
    args = ap.parse_args()

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    with open(args.input, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    header, data = rows[0], rows[1:]
    if header != EXPECTED_HEADER:
        sys.exit(f"Unexpected header: {header}")

    new_rows, manifest, reviews = [], [], []
    for i, row in enumerate(data, start=1):
        if len(row) != 5:
            sys.exit(f"Data row {i} has {len(row)} fields, expected 5")
        raw_date, title, artist, obj_no, link = row
        p = parse_date(raw_date)

        new = [
            p["display"],
            "" if p["start"] is None else str(p["start"]),
            "" if p["end"] is None else str(p["end"]),
            p["status"],
            title, artist, obj_no, link,
        ]
        new_rows.append(new)

        nd_before = row_hash(row[1:])
        nd_after = row_hash(new[4:])
        manifest.append({
            "row": i,
            "object_number": obj_no,
            "date_before": raw_date,
            "date_after": p["display"],
            "status": p["status"],
            "note": p["note"],
            "sha256_before": row_hash(row),
            "sha256_after": row_hash(new),
            "sha256_nondate_before": nd_before,
            "sha256_nondate_after": nd_after,
            "nondate_match": nd_before == nd_after,
        })
        if p["status"] == "review":
            reviews.append({"row": i, "object_number": obj_no,
                            "date_before": raw_date, "note": p["note"]})

    std_path = out / "standardized.csv"
    with open(std_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(NEW_HEADER)
        w.writerows(new_rows)

    man_fields = list(manifest[0].keys())
    with open(out / "manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=man_fields)
        w.writeheader()
        w.writerows(manifest)

    with open(out / "review.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["row", "object_number",
                                          "date_before", "note"])
        w.writeheader()
        w.writerows(reviews)

    # Round-trip check: recompute "after" checksums from the file on disk.
    with open(std_path, newline="", encoding="utf-8") as f:
        on_disk = list(csv.reader(f))[1:]
    mismatches = [m["row"] for m, r in zip(manifest, on_disk)
                  if row_hash(r) != m["sha256_after"]]

    bad_nondate = [m["row"] for m in manifest if not m["nondate_match"]]

    counts = {}
    for m in manifest:
        counts[m["status"]] = counts.get(m["status"], 0) + 1
    print(f"Rows processed: {len(manifest)}")
    for k in sorted(counts):
        print(f"  {k:14s} {counts[k]}")
    print(f"Round-trip checksum mismatches: {len(mismatches)}")
    print(f"Non-date field mismatches:      {len(bad_nondate)}")
    print(f"Review needed: {len(reviews)} row(s) -> {out / 'review.csv'}")

    if mismatches or bad_nondate:
        sys.exit("Verification failed; see manifest.csv")


if __name__ == "__main__":
    main()
```

## Outputs

- **`standardized.csv`**: the transformed data. Columns are `Object Date`, `Year Start`, `Year End`, `Date Status`, followed by the original non-date columns.
- **`manifest.csv`**: one row per data row, with `sha256_before`, `sha256_after`, and a `sha256_nondate_*` pair that must match. It also records the original and new date text.
- **`review.csv`**: rows the parser couldn't handle confidently. The original date text is kept in `Object Date` for these rows.

The script also re-reads `standardized.csv` and recomputes each "after" checksum, so the manifest is checked against the file on disk.

## Judgment calls to review

- **Centuries are expanded to full centuries.** "18th century" becomes `1701–1800`. The script doesn't narrow "late 18th" to the last part of the century, so those rows are marked `century_range` and the qualifier is kept in the text.
- **BCE years are negative integers in `Year Start`/`Year End`** (e.g., -600). This sorts correctly. The `Object Date` text uses "BCE".
- **Qualifiers like "ca." are kept in the text** but not in the year columns.
- **Likely `review` rows:** "1811, (Bunka 8); 1817", "A.H. 139–48/ 757–66 CE", "1950, printed 1967", "1712 or later", and "early 20th century (original dated 1480)". Decide these by hand.