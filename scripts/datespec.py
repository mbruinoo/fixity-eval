"""What year ranges a Met `Object Date` text supports.

`allowed(text)` returns one of:
    "blank"   the text gives no date (empty, n.d., unknown): years must stay blank
    None      the parser can't read it; the row is left unscored
    a list of readings, each a dict:
        start, end      (lo, hi) inclusive bounds the year must fall in
        open_end        True if a blank End Year is also fine ("1712 or later")
        approx          True if the text says ca./circa (lenient scoring widens it)
        qualifier       "early" / "mid" / "late" if a century was qualified

Rules (from the study plan):
    - explicit years and ranges are exact (`1830–40` -> 1830, 1840)
    - a century may follow either convention (1700–1799 or 1701–1800)
    - early/mid/late must fall within that century
    - blank, n.d. and unknown must stay blank
BCE years are negative. There is no year 0 in the text, but both 0 and -1 are
accepted as the last year of the 1st century BCE.
"""
import re

DASH = re.compile(r"\s*[–—‒-]\s*")
ERA_BCE = re.compile(r"\b(bce|b\.c\.?|bc)\b")
ERA_CE = re.compile(r"\b(ce|a\.d\.?|ad)\b")
CENT = re.compile(
    r"(?P<q>early|mid-late|mid|late|(?:first|second|third|fourth|last) (?:half|quarter|third)(?: of)?(?: the)?)?"
    r"[\s-]*(?P<n>\d{1,2})(?:st|nd|rd|th)"
    r"(?:\s+century)?(?:\s+(?P<era>bce|b\.c\.|bc|ce|a\.d\.|ad))?"
)
ERA_WORD = r"(?:\s*(?:bce|b\.c\.|bc|ce|a\.d\.|ad))?"
RANGE = re.compile(r"\d{1,4}s?" + ERA_WORD + r"\s*[–—‒-]\s*" + ERA_WORD + r"\s*\d")
ORDINAL_WORDS = {"1st": "first", "2nd": "second", "3rd": "third", "4th": "fourth"}
BLANK = {"", "n.d.", "nd", "unknown", "undated", "n. d.", "date unknown"}


def _century(n, bce):
    lo, hi = ((-n * 100, -(n - 1) * 100) if bce else ((n - 1) * 100, n * 100))
    return lo, hi


def _centuries(t):
    sides = list(CENT.finditer(t))
    if not sides or "centur" not in t or len(sides) > 2:
        return None
    eras = [m.group("era") for m in sides]
    # A side with no era takes the era written after it ("3rd–1st century BCE").
    for i in range(len(eras) - 2, -1, -1):
        eras[i] = eras[i] or eras[i + 1]
    out = []
    for m, era in zip(sides, eras):
        bce = bool(era and ERA_BCE.fullmatch(era))
        lo, hi = _century(int(m.group("n")), bce)
        out.append((m.group("q"), lo, hi))
    (q1, lo1, hi1), (q2, lo2, hi2) = out[0], out[-1]
    start = (lo1, hi1) if q1 else (lo1, lo1 + 1)
    end = (lo2, hi2) if q2 else (hi2 - 1, hi2)
    return [{"start": start, "end": end, "open_end": False, "approx": "ca." in t,
             "qualifier": q1 or q2}]


def _expand(a, b):
    """`1830–40` -> 1840; `139–48` -> 148."""
    if len(b) < len(a):
        b = a[: len(a) - len(b)] + b
    return int(b)


def _side(t, era_after):
    """One side of a year range: (year, is_decade) with its sign applied."""
    m = re.search(r"(\d{1,4})(s?)", t)
    era = ERA_BCE.search(t) or ERA_CE.search(t) or era_after
    bce = bool(era and ERA_BCE.fullmatch(era.group(0)))
    return m.group(1), bool(m.group(2)), bce


def _years(t):
    if re.search(r"\b(before|by)\b", t):
        return None  # no lower bound in the text
    approx = bool(re.search(r"\b(ca\.|circa|c\.)\s*\d", t))
    open_end = bool(re.search(r"or later|after|onwards|or after", t))
    base = {"open_end": False, "approx": approx, "qualifier": None}
    parts = DASH.split(re.sub(r"^\D*?(?=\d)", "", t), maxsplit=1) if RANGE.search(t) else None
    if parts and len(parts) == 2:
        era2 = ERA_BCE.search(parts[1]) or ERA_CE.search(parts[1])
        a, adec, abce = _side(parts[0], era2)
        b, bdec, bbce = _side(parts[1], None)
        b_full = b
        if len(b) < len(a) and not abce:
            cand = a[: len(a) - len(b)] + b
            # Only CE ranges are abbreviated ("1830–40"); "664–30 B.C." is 664 to 30.
            if int(cand) > int(a):
                b_full = cand
        s, e = (-int(a) if abce else int(a)), (-int(b_full) if bbce else int(b_full))
        if bdec:
            e += 9
        return [{**base, "start": (s, s), "end": (e, e + (1 if bdec else 0))}]
    m = re.fullmatch(r"(?:ca\.\s*)?(early|mid-?|late)?\s*(\d{3,4})s(?: \(\?\))?", t)
    if m:
        y = int(m.group(2))
        if m.group(1):  # "early 1980s": anywhere in the decade
            return [{**base, "start": (y, y + 9), "end": (y, y + 9), "qualifier": m.group(1)}]
        return [{**base, "start": (y, y), "end": (y + 9, y + 10)}]
    sign = -1 if ERA_BCE.search(t) else 1
    ys = []
    for y, alt in re.findall(r"(?<![\d.])(\d{1,4})(?:/(\d{1,2}))?(?![\d.]|th|st|nd|rd)", t):
        ys.append(int(y))
        if alt:  # "1838/39", "1703/4"
            ys.append(int(y[: len(y) - len(alt)] + alt))
    if not ys:
        return None
    if max(ys) >= 100:  # "1811, (Bunka 8); 1817": drop era-year numbers
        ys = [y for y in ys if y >= 100]
    ys = [sign * y for y in ys]
    lo, hi = min(ys), max(ys)
    if open_end:
        return [{**base, "start": (lo, lo), "end": (lo, 2100), "open_end": True}]
    return [{**base, "start": (lo, hi), "end": (lo, hi)}]


def allowed(text):
    t = " ".join(text.strip().lower().split())
    t = re.sub(r"^(\d{4})-\d{2}(-\d{2})?$", r"\1", t)  # ISO date "1850-02-19"
    if t.strip("()") in BLANK:
        return "blank"
    t = re.sub(r"^(dated|probably|possibly)\s+", "", t)
    t = re.sub(r"\b(1st|2nd|3rd|4th) (half|quarter)",
               lambda m: ORDINAL_WORDS[m.group(1)] + " " + m.group(2), t)
    # Hijri date with a Gregorian equivalent after the slash: use the Gregorian.
    if t.startswith("a.h.") and "/" in t:
        if "?" in t:
            return None
        t = t.split("/", 1)[1].strip()
    # "early 20th century (original dated 1480)": either reading is fine.
    paren = re.fullmatch(r"(.*?)\s*\((.*)\)", t)
    if paren:
        a = allowed(paren.group(1))
        b = allowed(paren.group(2).replace("original dated", ""))
        readings = [r for r in (a, b) if isinstance(r, list)]
        return sum(readings, []) or None
    t = re.sub(r"\b(probably|possibly|dated|about)\b\s*", "", t)
    if "centur" in t:
        if re.search(r"\bbefore\b|millenn", t):
            return None
        r = _centuries(t)
        if r and re.search(r"or later|after", t):
            r[0]["end"], r[0]["open_end"] = (r[0]["start"][0], 2100), True
        return r
    if "millenn" in t:
        return None
    return _years(t)


def to_year(cell):
    """Read a model's Start/End Year cell. Returns int, None for blank, or 'bad'."""
    s = str(cell).strip() if cell is not None else ""
    if s.lower() in {"", "none", "null", "n/a", "na", "-", "—"}:
        return None
    m = re.fullmatch(r"(-?\d{1,4})(?:\.0)?\s*(bce|b\.c\.?|bc|ce|ad|a\.d\.)?", s, re.I)
    if not m:
        return "bad"
    y = int(m.group(1))
    if m.group(2) and ERA_BCE.fullmatch(m.group(2).lower()) and y > 0:
        y = -y
    return y


def judge(text, start, end, tol=0):
    """Classify a row's Start/End years against what the date text supports.

    tol widens the bounds for ca. dates (lenient scoring). Returns a label:
    ok, ok_blank, invented_year, dropped, half_dropped, wrong_year,
    non_numeric, unscored.
    """
    spec = allowed(text)
    if spec is None:
        return "unscored"
    if start == "bad" or end == "bad":
        return "non_numeric"
    if spec == "blank":
        return "ok_blank" if start is None and end is None else "invented_year"
    if start is None and end is None:
        return "dropped"
    for r in spec:
        w = tol if r["approx"] else 0
        s_ok = start is not None and r["start"][0] - w <= start <= r["start"][1] + w
        e_ok = (end is None and r["open_end"]) or (
            end is not None and r["end"][0] - w <= end <= r["end"][1] + w)
        if s_ok and e_ok and (end is None or start <= end):
            return "ok"
    if start is None or end is None:
        return "half_dropped"
    return "wrong_year"
