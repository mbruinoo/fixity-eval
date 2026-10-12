#!/usr/bin/env python3
"""Standardize the Object Date column and add a per-row SHA-256 checksum.

Usage: python3 -I standardize_dates.py input.csv output.csv
Rows whose dates can't be parsed are kept as-is and marked REVIEW.
"""
import csv
import hashlib
import re
import sys

BCE_RE = re.compile(r'\bB\.?\s?C\.?(?:E\.?)?(?![A-Za-z])', re.I)
CE_RE = re.compile(r'\b(?:C\.?E|A\.?D)\.?(?![A-Za-z])', re.I)
QUALIFIERS = [
    (re.compile(r'\b(?:ca\.?|circa)\s*', re.I), 'ca. '),
    (re.compile(r'\bprobably\s*', re.I), 'probably '),
    (re.compile(r'\bafter\s*', re.I), 'after '),
    (re.compile(r'\bdated\s*', re.I), 'dated '),
]
PERIOD = r'(?:(early|mid|late)\s+)?'
CENTURY = re.compile(
    PERIOD + r'(\d+)(?:st|nd|rd|th)'
    r'(?:\s*-\s*' + PERIOD + r'(\d+)(?:st|nd|rd|th))?\s+century', re.I)
YEARS = re.compile(r'(\d{3,4})(?:\s*-\s*(\d{1,4}))?')
DECADE = re.compile(r'(\d{3})0s')
MISSING = ('n.d.', 'unknown')


def ordn(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


def parse(raw):
    """Return (display, start, end), or None if the text can't be parsed.
    Years are astronomical: negative means BCE."""
    s = raw.strip().replace('\u2013', '-').replace('\u2014', '-')
    if not s or s.lower() in MISSING:
        return '', None, None

    bce = bool(BCE_RE.search(s))
    body = CE_RE.sub('', BCE_RE.sub('', s))
    prefix = ''
    for rx, text in QUALIFIERS:
        if rx.search(body):
            prefix += text
            body = rx.sub('', body)
    body = re.sub(r'\s+', ' ', body).strip(' ,')

    m = CENTURY.fullmatch(body)
    if m:
        p1, n1, p2, n2 = m.groups()
        n1 = int(n1)
        n2 = int(n2) if n2 else None
        lo, hi = (min(n1, n2), max(n1, n2)) if n2 else (n1, n1)
        if bce:
            start, end = -(hi * 100), -((lo - 1) * 100 + 1)
        else:
            start, end = (lo - 1) * 100 + 1, hi * 100
        core = f"{p1 + ' ' if p1 else ''}{ordn(n1)}"
        if n2:
            core += f"–{p2 + ' ' if p2 else ''}{ordn(n2)}"
        core += f" century {'BCE' if bce else 'CE'}"
        return prefix + core, start, end

    m = YEARS.fullmatch(body)
    if m:
        a_s, b_s = m.group(1), m.group(2)
        a = int(a_s)
        if b_s:
            # Expand abbreviated ends: 1830–40 -> 1840
            b = int(a_s[:len(a_s) - len(b_s)] + b_s) if len(b_s) < len(a_s) else int(b_s)
            text = f"{a}–{b}"
            lo, hi = min(a, b), max(a, b)
        else:
            text = str(a)
            lo = hi = a
        era = ' BCE' if bce else ''
        start, end = (-hi, -lo) if bce else (lo, hi)
        return prefix + text + era, start, end

    m = DECADE.fullmatch(body)
    if m and not bce:
        start = int(m.group(1)) * 10
        return prefix + f"{start}s", start, start + 9

    return None


def main(src, dst):
    with open(src, newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f))
    header, data = rows[0], rows[1:]
    out_header = ['Object Date', 'Start Year', 'End Year', 'Date Status',
                  'Row Checksum (SHA-256)', 'Original Object Date'] + header[1:]
    review = 0

    with open(dst, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(out_header)
        for row in data:
            # Checksum the original row so it can be verified against the source.
            digest = hashlib.sha256('\x1f'.join(row).encode('utf-8')).hexdigest()[:16]
            fields = row + [''] * (len(header) - len(row))
            raw = fields[0]
            result = parse(raw)
            if result is None:
                std, start, end, status = raw, '', '', 'REVIEW'
                review += 1
            else:
                std, start, end = result
                status = 'MISSING' if std == '' else 'OK'
                start = '' if start is None else start
                end = '' if end is None else end
            w.writerow([std, start, end, status, digest, raw] + fields[1:])

    print(f"{len(data)} rows written, {review} need manual review", file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
