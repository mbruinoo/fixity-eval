import csv, hashlib, re, sys

SRC, DST = sys.argv[1], sys.argv[2]

# Non-standard values left as-is on purpose (they carry qualifiers or
# non-Gregorian dating that can't be reduced to one year range).
KEEP = {'unknown', 'n.d.', '', 'January 21, 1800', 'February 19, 1850',
        'A.H. 139–48/ 757–66 CE', '1811, (Bunka 8); 1817', '1950, printed 1967',
        '1712 or later', 'dated 1637', 'probably after 1657', '1712 or later'}

PART = {'early': (0, 32), 'mid': (33, 66), 'late': (67, 99)}

def century(n, part=None):
    """Chronological (lo, hi) for the Nth century; BCE handled by sign."""
    pass

def cent_span(n, era, part=None):
    if era == 'CE':
        lo = (n-1)*100 + 1
        hi = n*100
    else:  # BCE: chronological values are negative
        lo = -n*100
        hi = -((n-1)*100 + 1)
    if part:
        a, b = PART[part]
        return (lo + a, lo + b) if era == 'CE' else (lo + a, lo + b)
    return (lo, hi)

def ordinal(s):
    return int(re.match(r'\d+', s).group())

def fmt_t(t):
    return f'{abs(t)}' if t >= 0 else f'{abs(t)}'

def fmt_pair(lo, hi, ce_ok=True):
    # lo, hi chronological; negative = BCE
    if lo == hi:
        return f'{abs(lo)} BCE' if lo < 0 else f'{lo}'
    if lo < 0 and hi < 0:
        return f'{abs(lo)}–{abs(hi)} BCE'
    if lo < 0 <= hi:
        return f'{abs(lo)} BCE–{hi}'
    return f'{lo}–{hi}'

def parse_century_phrase(s):
    m = re.fullmatch(r'(?:(early|mid|late|mid-late)[ -]?)?(\d+(?:st|nd|rd|th))'
                     r'(?:[–-](?:(early|mid|late)[ -]?)?(\d+(?:st|nd|rd|th)))?'
                     r' century(?: (BCE|CE|BC))?', s)
    if not m:
        return None
    p1, c1, p2, c2, era = m.groups()
    era = (era or 'CE').replace('BC', 'BCE')
    if c2 is None:
        # single century, possibly with a part
        if p1 == 'mid-late':
            lo = cent_span(ordinal(c1), era, 'mid')[0]
            hi = cent_span(ordinal(c1), era, 'late')[1]
        elif p1:
            lo, hi = cent_span(ordinal(c1), era, p1)
        else:
            lo, hi = cent_span(ordinal(c1), era)
        return fmt_pair(lo, hi)
    # century range: first century's start to second century's end
    lo_c, hi_c = cent_span(ordinal(c1), era), cent_span(ordinal(c2), era)
    lo = min(lo_c[0], hi_c[0])
    hi = max(lo_c[1], hi_c[1])
    if p1 in ('late', 'early'):
        lo = cent_span(ordinal(c1), era, p1)[0]
    if p2 in ('late', 'early'):
        hi = cent_span(ordinal(c2), era, p2)[1]
    return fmt_pair(lo, hi)

def std(v):
    s = re.sub(r'\s+', ' ', v).strip()
    if s in KEEP:
        return s
    s = s.replace('—', '–').replace('B.C.', 'BCE').replace('B.C', 'BCE')
    s = re.sub(r'\bBC\b', 'BCE', s)
    s = s.replace('-', '–') if re.fullmatch(r'\d+-\d+', s) else s
    # "1st century BCE" etc.
    ca = ''
    if s.startswith('ca. '):
        ca, s = 'ca. ', s[4:]
    probably = ''
    if s.startswith('probably '):
        probably, s = 'probably ', s[9:]
    r = parse_century_phrase(s)
    if r:
        return ca + probably + r
    # decades: 1960s
    m = re.fullmatch(r'(\d{3})0s', s)
    if m:
        d = int(m.group(1)) * 10
        return ca + f'{d}–{d+9}'
    # plain year or year range, with BCE optional
    m = re.fullmatch(r'(\d{1,4})(?: BCE)?(?:–(\d{1,4}))?( BCE)?', s)
    if m:
        a, b, bce = m.group(1), m.group(2), m.group(3)
        if b and len(b) < len(a):
            b = a[:len(a)-len(b)] + b  # 1880–92 -> 1880–1892
        if bce or s.endswith('BCE'):
            end = ' BCE'
        else:
            end = ''
        return ca + probably + (f'{a}–{b}' if b else a) + end
    # the remaining value is a month/day + year, or a "1700–1938" range
    m = re.fullmatch(r'(March|January|February) (\d{4})', s)
    if m:
        return ca + s
    return ca + probably + s

rows = list(csv.reader(open(SRC, encoding='utf-8', newline='')))
out = []
for r in rows:
    out.append(list(r))
for i in range(1, len(out)):
    out[i][0] = std(out[i][0])

if DST != '-':
    with open(DST, 'w', encoding='utf-8', newline='') as f:
        csv.writer(f, lineterminator='\n').writerows(out)
else:
    for i in range(1, len(rows)):
        if rows[i][0] != out[i][0]:
            print(f'{rows[i][0]!r:42} -> {out[i][0]!r}')
