#!/usr/bin/env python3
"""Standardize the Object Date column and add a CRC32 checksum per row.

Usage: python3 standardize_dates.py input.csv output.csv
Dates that can't be parsed with confidence get Date Status = REVIEW.
"""
import csv
import re
import sys
import zlib

PHASE = {None: (0, 100), "early": (0, 34), "mid": (33, 67), "late": (66, 100)}
ERA = r"(BCE|BC|B\.C\.|CE|AD|C\.E\.)"


def century_span(qual, c, bce):
    lo, hi = (c - 1) * 100 + 1, c * 100          # absolute year numbers
    q0, q1 = PHASE[qual]
    if bce:                                       # BCE runs backwards
        a, b = hi - (q1 - 1), hi - q0
        return -b, -a
    return lo + q0, lo + q1 - 1


def parse_side(text):
    t = text.strip()
    m = re.fullmatch(rf"(?:(early|mid|late) )?(\d+)(?:st|nd|rd|th) century(?: {ERA})?", t, re.I)
    if m:
        return {"kind": "century", "qual": m.group(1) and m.group(1).lower(),
                "c": int(m.group(2)),
                "bce": None if not m.group(3) else m.group(3).upper().startswith("B")}
    m = re.fullmatch(rf"(\d{{1,4}})(s?)(?: {ERA})?", t, re.I)
    if m:
        return {"kind": "year", "y": int(m.group(1)), "decade": m.group(2) == "s",
                "bce": None if not m.group(3) else m.group(3).upper().startswith("B")}
    return None


def to_span(side):
    if side["kind"] == "century":
        return century_span(side["qual"], side["c"], side["bce"])
    y = -side["y"] if side["bce"] else side["y"]
    if side["decade"]:
        return None if side["bce"] else (y, y + 9)
    return (y, y)


def parse_date(raw):
    """Return (start, end, approximate) or None if the value needs review."""
    s = re.sub(r"\(.*?\)", " ", raw)                       # drop parentheticals
    approx = bool(re.match(r"^\s*(ca\.?|c\.|probably|possibly)", s, re.I))
    s = re.sub(r"^\s*(original dated|dated|ca\.?|c\.|probably|possibly)\s*", "", s, flags=re.I)
    s = re.sub(r"\b(early|mid|late)-", r"\1 ", s, flags=re.I)
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return None
    parts = [p.strip() for p in s.split("-")]
    if len(parts) > 2:
        return None
    if len(parts) == 1:
        side = parse_side(parts[0])
        span = to_span(side) if side else None
        return None if span is None else (span[0], span[1], approx)

    left, right = parts
    rs = parse_side(right)
    if rs is None:
        return None
    if rs["kind"] == "century" and parse_side(left) is None:
        left = f"{left} century"                          # "6th–7th century"
    ls = parse_side(left)
    if ls is None:
        return None
    if ls["kind"] == "year" and rs["kind"] == "year" and len(str(rs["y"])) < len(str(ls["y"])):
        digits = str(ls["y"])                             # "1282–85" -> 1285
        rs["y"] = int(digits[: len(digits) - len(str(rs["y"]))] + str(rs["y"]))
    if ls["bce"] is None:
        ls["bce"] = bool(rs["bce"])
    if rs["bce"] is None:
        rs["bce"] = False
    a, b = to_span(ls), to_span(rs)
    if a is None or b is None:
        return None
    return (a[0], b[1], approx)


def fmt_year(y, mixed=False):
    if y < 0:
        return f"{-y} BCE"
    return f"{y} CE" if mixed else str(y)


def display(start, end):
    if start == end:
        return fmt_year(start)
    if start < 0 and end < 0:
        return f"{-start}–{-end} BCE"
    mixed = start < 0 < end
    return f"{fmt_year(start, mixed)}–{fmt_year(end, mixed)}"


def main(src, dst):
    with open(src, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    out_header = (["Object Date (Standard)", "Year Start", "Year End", "Date Status"]
                  + header[1:] + ["Original Object Date", "Row Checksum (CRC32)"])
    counts = {"OK": 0, "REVIEW": 0, "MISSING": 0}

    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(out_header)
        for row in body:
            if not any(field.strip() for field in row):
                continue
            raw = row[0]
            checksum = f"{zlib.crc32(chr(31).join(row).encode('utf-8')):08x}"
            if not raw.strip():
                std, start, end, status = "", "", "", "MISSING"
            else:
                parsed = parse_date(raw)
                if parsed is None:
                    std, start, end, status = "", "", "", "REVIEW"
                else:
                    start, end, approx = parsed
                    std = ("c. " if approx else "") + display(start, end)
                    status = "OK"
            counts[status] += 1
            w.writerow([std, start, end, status] + row[1:] + [raw, checksum])

    print(f"OK: {counts['OK']}  REVIEW: {counts['REVIEW']}  MISSING: {counts['MISSING']}",
          file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
