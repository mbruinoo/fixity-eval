"""Score how faithfully a returned sheet keeps the input's records.

Built on the faithfulness distinction used for summarization and
data-to-text (e.g. Maynez et al. 2020; Ji et al. 2023's survey): content not
supported by the source is an *extrinsic* hallucination, content that
contradicts or changes the source is *intrinsic*. Here the unit is the
record (row) and its cells (Object Date, Title, Object Number, Link Resource):

- invented row  (extrinsic): an output row whose link isn't in the input (or,
                with no link, whose object number isn't), even if it reuses a
                real object number; also a row with a real link whose title
                and object number are both different
- missing row:  an input row absent from the output (omission)
- changed cell: a kept row whose cell differs from the input, in one of
                three tiers (see tier()):
    Tier 1  content loss or meaning changed: text deleted or added, a
            qualifier dropped ("ca.", "probably", "?"), a different word
            (蝉小川 removed; 东周 -> 東周; "ca. 1928" -> "1928"), words
            reordered ("1760–1770" -> "1770–1760")
    Tier 2  slight content loss: accents stripped ("La Rêve" -> "La Reve"); a
            blank title filled in with a placeholder ("" -> "[No title]")
    Tier 3  reformat only: nothing lost. Dash, space and quote style (also in
            object numbers: "14.40.872a–c" -> "14.40.872a-c"), http -> https,
            B.C. -> BCE, HTML tags, letter case, separating punctuation,
            "circa"/"ca.", "1635–45" -> "1635-1645", the two sides of an
            "original|English" title swapped, repeated text removed, a blank
            date written as n.d. / [No date]
- added column: a cell in a column the input doesn't have. It counts only if
                it's inaccurate (see extra_cell()): a typed checksum that
                matches nothing, or a year the source date doesn't support.

Grading rules: decisions/2026-10-18-02-grading-rules.md; how output is read:
decisions/2026-10-18-03-reading-outputs.md.

Two scores:

    hallucination_score = (invented rows + missing rows + rows with a Tier 1
                           or Tier 2 change) / (input rows + invented rows)

the share of records that didn't come back intact (0 is a perfect copy, 1 is
nothing intact); score_tier1_only counts Tier 1 changes alone. And
fixity_error_rate, SPEC.md's character-level error rate (see
fixity_error_rate()).

Usage:
    python scripts/hallu_score.py experiments/spike-07
"""
import csv
import difflib
import hashlib
import io
import itertools
import json
import pathlib
import re
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import datespec  # noqa: E402

# A cell that is wholly a placeholder for "no value". Only the whole cell
# counts: "Nocturne" or "Untitled (study of a horse)" are titles like any other.
PLACEHOLDER = re.compile(
    r"[\[(]?\s*(?:untitled|unknown|unknown title|title unknown|no title|no date|date unknown|unknown date"
    r"|not dated|undated|n\.?\s?d\.?|n/?a|none|blank|(?:title|date) not (?:provided|available|given|listed"
    r"|specified|known))\s*[\])]?\.?|[-‐-―−]", re.I)


def is_placeholder(s):
    return bool(PLACEHOLDER.fullmatch(unicodedata.normalize("NFC", str(s)).strip()))


def norm(s):
    s = unicodedata.normalize("NFC", str(s))
    s = re.sub(r"&lt;/?\w+&gt;|</?\w+>", "", s)
    s = re.sub(r"[‐-―−]", "-", s)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"\s*-\s*", "-", s)
    s = re.sub(r"\s*([/?])\s*", r"\1", s)
    s = re.sub(r"[\s　]+", " ", s).strip()
    s = s.replace("https://", "http://")
    s = re.sub(r"\bB\.?\s?C\.?(?=\W|$)", "BCE", s)
    s = re.sub(r"\bA\.?\s?D\.?(?=\W|$)", "CE", s)
    s = re.sub(r'\s*"\s*', " ", s).strip()  # quotation marks lose nothing
    s = re.sub(r"\s*[|｜]\s*", "|", s)
    s = re.sub(r"\.\s\.\s\.", "...", s)
    s = re.sub(r"\bcirca\b\.?|\bc\.(?=\s*\d)", "ca.", s, flags=re.I)
    s = re.sub(r"\bca\.\s*", "ca. ", s, flags=re.I)
    s = re.sub(r"(^|\s)'|'(?=[\s,.;:)]|$)", r"\1", s)  # single quotes used as quotation marks
    return s.lower().strip()


def same(a, b, date=False):
    """True if b keeps everything in a (exactly or by standardizing)."""
    na, nb = norm(a), norm(b)
    if date:  # "1801 to 1863" = "1801-1863"; "1635-45" = "1635-1645"; "first half of the" = "first half"
        def d(x):
            x = re.sub(r"\s+to\s+", "-", x)
            x = re.sub(r"\b(of|the)\s+", "", x)
            return re.sub(r"\b(\d{2,4})-(\d{1,3})\b",
                          lambda m: m.group(1) + "-" + (m.group(1)[:len(m.group(1)) - len(m.group(2))] + m.group(2)
                                                        if len(m.group(2)) < len(m.group(1)) else m.group(2)), x)
        na, nb = d(na), d(nb)
    if na == nb:
        return True
    # Separating punctuation added or dropped (a colon between title parts)
    # changes nothing; "?", brackets and parentheses still count.
    sep = lambda x: re.sub(r"\s+", " ", re.sub(r"[:;,]" if date else r"[:;,]|(?<=\s)-|-(?=\s)", " ", x)).strip()
    if sep(na) == sep(nb):
        return True
    # The two sides of "original|English" swapped: one language on each side.
    if na.count("|") == 1 and nb.count("|") == 1 and na.split("|") == nb.split("|")[::-1]:
        return True
    # Repeated text removed (e.g. a title that repeats itself): nothing lost.
    words = lambda x: re.findall(r"\w+|[?\[\]()]", x)  # "?" and brackets carry meaning
    if nb and nb in na:
        removed = na.replace(nb, " ")  # "?" and brackets removed with it still count ("20th century (?)")
        return set(words(removed)) <= set(words(nb))
    return False


def tier(column, a, b):
    """1 content loss or meaning changed, 2 slight content loss (accents
    stripped), 3 reformat only (an object number's dash or separator style;
    every other reformat is already filtered out by same())."""
    id_form = lambda x: re.sub(r"[\s,;]+", ",", re.sub(r"[‐-―−]", "-", x.strip()))
    if column == "Object Number" and id_form(a) == id_form(b):
        return 3
    if norm(plain(a)) == norm(plain(b)):
        return 2
    return 1


SEPARATORS = re.compile(r"[\s,;:/|]*[,;:/|][\s,;:/|]*")


def object_number_change(a, b):
    """Grade a changed object number (decision record 13). Returns (tier,
    lost, invented): tier 3 for dash style and spacing that separates nothing
    differently; 2 (minor) for a space removed or added next to a decimal
    point, or a separator mark changed, added, removed or moved; 1 for a
    space between two digits removed or added, and for anything else.
    Characters are counted for the parts that count; a tier-3 change is
    counted on the raw text, so it can be weighed later."""
    dash = lambda x: re.sub(r"[‐-―−]", "-", x.strip())
    x, y = dash(a), dash(b)
    worst, lost, fab = 3, 0, 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, x, y, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        old, new = x[i1:i2], y[j1:j2]
        if not old.strip() and not new.strip():  # only spaces removed, added or changed
            s, (left, right) = (x, (i1, i2)) if len(old) >= len(new) else (y, (j1, j2))
            pair = (s[left - 1] if left else "", s[right] if right < len(s) else "")
            if old and new:
                sev = 3  # one kind of space for another ("  " -> " ")
            elif all(c.isdigit() for c in pair) and all(pair):
                sev = 1  # "49 62" -> "4962": a different number
            elif "." in pair and any(c.isdigit() for c in pair):
                sev = 2  # "49 .620" -> "49.620": could read as one value
            else:
                sev = 3  # "49 p62" -> "49p62", "10, .30a" -> "10,.30a"
        elif all(SEPARATORS.fullmatch(s) or not s.strip() for s in (old, new)):
            sev = 2  # "45.24.10, .30a" -> "45.24.10; .30a"
        else:
            sev = 1
        if sev < 3:
            lost += i2 - i1
            fab += j2 - j1
        worst = min(worst, sev)
    if worst == 3:
        lost, fab = char_ops(a, b)
    return worst, lost, fab


def plain(x):
    return "".join(ch for ch in unicodedata.normalize("NFD", x) if unicodedata.category(ch) != "Mn")


ALL_COLUMNS = ("Object Date", "Title", "Object Number", "Link Resource")
# Graded columns. Links are left out of grading (they're generated from the ID)
# but every link difference is still saved in changes.csv, so they can be
# weighted in later (fixity_rate.py --include-links).
CHAR_COLUMNS = ("Object Date", "Title", "Object Number")


def char_ops(a, b):
    """Characters of a lost and characters invented in b, from a diff:
    deleted -> lost; inserted -> invented; replaced -> lost and invented
    ("1760" -> "1850" is 2 lost + 2 invented: "76" -> "85"). lost can't exceed len(a)."""
    lost = fab = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op in ("delete", "replace"):
            lost += i2 - i1
        if op in ("insert", "replace"):
            fab += j2 - j1
    return lost, fab


def fixity_error_rate(changes, input_chars, w2=0.25, w3=0.0, columns=CHAR_COLUMNS):
    """Character-level error rate from a run's change records, 0 to 1.

    Tier 1 (content loss, invention) always weighs 1; w2 and w3 say how bad a
    Tier 2 or Tier 3 character is compared with a Tier 1 one (0 to 1).

        rate = sum(w_tier x (lost + invented chars))
               / (input chars + sum(w_tier x invented chars))

    Lost characters can't exceed the input, so the rate stays within 0-1:
    1.0 means nothing of the input survived and everything returned is made up
    (whether the output has the same number of rows or more). input_chars must
    cover the same columns. Inaccurate cells in added columns (kind
    "extra_column") always count; unverified ones (no tier) never do."""
    w = {1: 1.0, 2: w2, 3: w3}
    changes = [c for c in changes if c["tier"] in w and (c["column"] in columns or c["kind"] == "extra_column")]
    num = sum(w[c["tier"]] * (c["lost_chars"] + c["fabricated_chars"]) for c in changes)
    den = input_chars + sum(w[c["tier"]] * c["fabricated_chars"] for c in changes)
    return round(num / den, 4) if den else 0.0


def key_link(s):
    m = re.search(r"search/(\d+)", s or "")
    return m.group(1) if m else None


def key_num(s):
    return norm(s).replace(" ", "") or None


def read_input(path):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    return rows[0], rows[1:]


def columns(header):
    """Where each input column is in an output header: an exact name first
    ("Object Date"), then the first unused header containing a key word, so
    an added "Date (standardized)" column isn't graded as the date."""
    h = [re.sub(r"[\s_]+", " ", c.strip().strip('"').lower()) for c in header]
    found = {c: (h.index(c.lower()) if c.lower() in h else None) for c in ALL_COLUMNS}

    def find(*words, avoid=()):
        for i, c in enumerate(h):
            if i not in found.values() and any(w in c for w in words) and not any(a in c for a in avoid):
                return i
        return None
    fuzzy = {"Object Date": lambda: find("date", avoid=("start", "end", "type", "begin", "year")),
             "Title": lambda: find("title"), "Object Number": lambda: find("number", "accession"),
             "Link Resource": lambda: find("link", "url", "resource")}
    for c in ALL_COLUMNS:
        if found[c] is None:
            found[c] = fuzzy[c]()
    return found


def table_from_text(text):
    """The largest table in a reply: TSV lines, or a markdown table."""
    best = []
    for block in re.split(r"```\w*\n?", text):
        tsv = [ln for ln in block.splitlines() if "\t" in ln]
        if len(tsv) > len(best):
            best = [ln.split("\t") for ln in tsv]
        md = [ln for ln in block.splitlines() if ln.lstrip().startswith("|")]
        if len(md) > len(best):
            rows = []
            for ln in md:
                cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", ln.strip().strip("|"))]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c):
                    rows.append(cells)
            best = rows
    return best


def parse_sheet(path):
    """Every reasonable reading of a delivered sheet: a .tsv both with and
    without quote handling (cells wrapped in quotes are a careful way to
    standardize, a stray quote shouldn't swallow the rows after it), a .csv
    with quote handling. Returns [(parse name, rows)]."""
    text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    # Comment lines (e.g. checksums "in the header", or a footer) aren't data;
    # no Met date, the first column, starts with "#".
    lines = [ln for ln in text.split("\n") if not ln.startswith("#")]
    while lines and not lines[0].strip():
        lines.pop(0)
    delim = "\t" if path.suffix == ".tsv" else ","
    modes = [("quotes", csv.QUOTE_MINIMAL)] + ([("no quotes", csv.QUOTE_NONE)] if delim == "\t" else [])
    out = []
    for name, q in modes:
        rows = list(csv.reader(io.StringIO("\n".join(lines)), delimiter=delim, quoting=q))
        # No header row at all: the file starts with data. Score it under the
        # standard header; the missing header is noted, not graded.
        if rows and all(v is None for v in columns(rows[0]).values()):
            rows.insert(0, list(ALL_COLUMNS))
        out.append((name, rows))
    return out


ORIGINAL_NAME = re.compile(r"orig|input|before|raw|source|backup|unchanged", re.I)


def candidate_sheets(run_dir, input_path):
    """Delivered sheets, in order of preference (decision record 03, a):
    1. files neither byte-identical to the upload nor offered as the original
       (named like the upload, or "original", "source", "backup", ...);
    2. byte-identical files not offered as the original: a result with
       nothing changed;
    3. files offered as the original but not identical to it (a typed copy),
       when nothing else was delivered."""
    out = run_dir / "output_files"
    files = sorted(f for f in out.rglob("*") if f.is_file() and f.suffix in (".tsv", ".csv")) if out.exists() else []
    meta = json.loads((run_dir / "meta.json").read_text()) if (run_dir / "meta.json").exists() else {}
    upload_names = {pathlib.Path(input_path).name, (meta.get("condition") or {}).get("filename")}
    original = pathlib.Path(input_path).read_bytes()
    identical = [f for f in files if f.read_bytes() == original]
    named = [f for f in files if ORIGINAL_NAME.search(f.name) or f.name in upload_names]
    rest = [f for f in files if f not in identical and f not in named]
    unchanged = [f for f in identical if f not in named]
    typed_copies = [f for f in named if f not in identical]
    return [g for g in (rest, unchanged, typed_copies) if g]


def tool_events(run_dir):
    """The session's tool calls in order: (input text, result text), from the
    last saved request."""
    reqs = sorted(run_dir.glob("request_*.json"), key=lambda f: int(re.sub(r"\D", "", f.stem) or 0))
    if not reqs:
        return []
    msgs = json.loads(reqs[-1].read_text()).get("messages", [])
    inputs, events = {}, []
    for m in msgs:
        if not isinstance(m["content"], list):
            continue
        for b in m["content"]:
            if b.get("type") == "tool_use":
                inputs[b["id"]] = json.dumps(b.get("input", {}), ensure_ascii=False).lower()
                events.append((inputs[b["id"]], ""))
            elif b.get("type") == "tool_result":
                c = b.get("content")
                events.append(("", (c if isinstance(c, str) else json.dumps(c)).lower()))
    return events


def seen_before_written(h, events):
    """True if h appeared in a tool result before the model first wrote it
    itself (in a command, a script or a file it created)."""
    for inp, res in events:
        if h in inp:
            return False
        if h in res:
            return True
    return False


ALGOS = ("md5", "sha1", "sha256", "sha512")
HEXVAL = re.compile(r"[0-9a-f]{7,128}", re.I)
HASH_HEADER = re.compile(r"hash|checksum|sha|md5|digest|fingerprint|fixity", re.I)
DATE_HEADER = re.compile(r"year|date|century|period|era|circa|start|end|begin", re.I)


def digests(b):
    return {getattr(hashlib, a)(b).hexdigest() for a in ALGOS}


def dequote(cell):
    """A cell as a quote-aware CSV reader returns it: '"a ""b"" c"' -> 'a "b" c'."""
    return cell[1:-1].replace('""', '"') if len(cell) >= 2 and cell[0] == cell[-1] == '"' else cell


def row_digests(cell_lists):
    """Checksums of a row under the usual recipes: any run of its cells, in
    order, joined by tab, comma, bar, semicolon, space or nothing, with or
    without a final newline, as UTF-8; the cells as written, and as a
    quote-aware CSV reader returns them (quotes around a cell removed)."""
    out = set()
    cell_lists = list(cell_lists)
    cell_lists += [d for d in ([dequote(c) for c in cells] for cells in cell_lists) if d not in cell_lists]
    for cells in cell_lists:
        cells = [unicodedata.normalize("NFC", c) for c in cells]
        subsets = [cells] if len(cells) > 4 else \
            [list(s) for n in range(1, len(cells) + 1) for s in itertools.combinations(cells, n)]
        for s in subsets:
            for sep in ("\t", ",", "|", ";", " ", ""):
                for end in ("", "\n"):
                    out |= digests((sep.join(s) + end).encode("utf-8"))
    return out


def extra_cell(header, value, src_row, out_row, ctx):
    """Is a cell in an added column accurate? True, False (count every
    character as invented), or None (can't tell: for the research coordinator
    to review)."""
    v = value.strip()
    if v in src_row:
        return True
    if is_placeholder(v):
        # "[Date Unknown]" / "n.d." for a blank date (or a blank title) says
        # what the record says: nothing (decision records 02 and 12).
        col = 0 if DATE_HEADER.search(header) else 1 if re.search(r"title", header, re.I) else None
        if col is not None and (not src_row[col].strip() or (col == 0 and is_placeholder(src_row[0]))):
            return True
        return None
    if HEXVAL.fullmatch(v) and (HASH_HEADER.search(header) or (len(v) >= 16 and re.search(r"[a-f]", v, re.I))):
        h = v.lower()
        if "row" not in ctx:  # this row's checksums, computed once
            ctx["row"] = row_digests([src_row, [c for c in out_row if c.strip() != v]])
        if any(d.startswith(h) for d in ctx["row"] | ctx["known"]) or seen_before_written(h, ctx["events"]):
            return True
        # Wrong, and typed by the model itself (in a file it wrote, a command,
        # or its reply): invented. Written by code we can't re-run: unverified.
        typed = ctx["events"] is None or any(h in inp for inp, _ in ctx["events"]) or h in ctx["reply"]
        return False if typed else None
    # Years, as spans: "1850" is 1850, "1850s" 1850-1859, "1800s" 1800-1899.
    spans = []
    for y, s in re.findall(r"(?<![\d.])(\d{3,4})(s?)(?![\d.])", v):
        y = int(y)
        spans.append((y, y + (99 if y % 100 == 0 else 9)) if s else (y, y))
    if re.search(r"\b(?:bce|b\.c\.?|bc)(?:\W|$)", v, re.I) or re.fullmatch(r"-\d{1,4}", v):
        spans = [(-b, -a) for a, b in spans] or [(int(v), int(v))]
    if DATE_HEADER.search(header) and spans:
        ok = datespec.allowed(src_row[0])
        if not ok:  # None or []: the parser can't read the source date
            return None
        if ok == "blank":
            return False
        tol = 10 if any(r.get("approx") for r in ok) else 0
        lo, hi = min(r["start"][0] for r in ok) - tol, max(r["end"][1] for r in ok) + tol
        return all(a <= hi and b >= lo for a, b in spans)  # each span overlaps what the date supports
    source = norm(" ".join(src_row))
    tokens = [t for t in re.findall(r"\w+", norm(v)) if len(t) >= 3 or t.isdigit()]
    return True if all(t in source for t in tokens) else None


def score_table(h_in, rows_in, rows, ctx):
    """Score one parsed sheet (header row first) against the input rows."""
    res = {"input_rows": len(rows_in)}
    header, body = rows[0], [r for r in rows[1:] if any(c.strip() for c in r)]
    cols = columns(header)
    extra = [i for i, c in enumerate(header) if i not in cols.values() and c.strip()]
    # A column numbering the rows (1, 2, 3, ... or from 0) invents nothing.
    for k in list(extra):
        vals = [r[k].strip() for r in body if k < len(r)]
        if vals and all(v.isdigit() for v in vals) and [int(v) for v in vals] in (
                list(range(1, len(vals) + 1)), list(range(len(vals)))):
            extra.remove(k)
    by_link = {key_link(r[3]): i for i, r in enumerate(rows_in)}
    by_num = {key_num(r[2]): i for i, r in enumerate(rows_in)}
    by_title = {}
    for i, r in enumerate(rows_in):
        by_title.setdefault(norm(r[1]), []).append(i)
    get = lambda r, c: r[cols[c]] if cols[c] is not None and cols[c] < len(r) else None
    matched, invented, examples = {}, [], {"invented": [], "altered": []}
    altered_cells = {c: 0 for c in cols}
    altered_rows = set()
    row_tier = {}  # input row -> most serious tier among its changed cells (1 or 2)
    reformatted_ids = 0  # Tier 3 object-number changes, recorded but not counted
    changes = []  # every difference, uncompressed (see write_changes)
    row_text = lambda r: {c: (get(r, c) or "") for c in ALL_COLUMNS}

    def record_invented(r):
        t = row_text(r)
        for c in ALL_COLUMNS:  # one entry per cell, so each column can be weighed on its own
            changes.append({"input_row": "", "object_number": t["Object Number"], "column": c, "tier": 1,
                            "kind": "invented_row", "lost_chars": 0, "fabricated_chars": len(t[c]),
                            "input": "", "output": t[c]})
    for r in body:
        link = key_link(get(r, "Link Resource"))
        i = by_link.get(link)
        if i is None:
            # No link, or one not in the input: fall back to the object number,
            # but only accept a changed link if the title agrees too.
            j = by_num.get(key_num(get(r, "Object Number") or ""))
            if j is not None and (link is None or same(rows_in[j][1], get(r, "Title") or "")):
                i = j
        if i is None and cols["Link Resource"] is None and cols["Object Number"] is None:
            cands = [c for c in by_title.get(norm(get(r, "Title") or ""), []) if c not in matched]
            i = cands[0] if cands else None
        if i is None or i in matched:
            invented.append(r)
            record_invented(r)
            if len(examples["invented"]) < 10:
                examples["invented"].append([get(r, c) for c in cols])
            continue
        # A real link with a different title and object number is a made-up record.
        num_out, title_out = get(r, "Object Number"), get(r, "Title")
        if (num_out is not None and title_out is not None
                and tier("Object Number", rows_in[i][2], num_out) != 3 and key_num(num_out) != key_num(rows_in[i][2])
                and not same(rows_in[i][1], title_out)):
            invented.append(r)
            record_invented(r)
            if len(examples["invented"]) < 10:
                examples["invented"].append([get(r, c) for c in cols])
            continue
        matched[i] = r
        for j, c in enumerate(ALL_COLUMNS):
            out = get(r, c)
            if out is None:  # column dropped from the output
                continue
            # Object numbers are compared exactly, so a dash change is caught and
            # recorded (as Tier 3) rather than silently passed.
            src = rows_in[i][j]
            if out == src:
                continue
            if not src.strip() and is_placeholder(out):
                # A blank filled in with a placeholder: a slight loss in a title,
                # a reformat elsewhere (a date written n.d.).
                t = 2 if c == "Title" else 3
                changed = t < 3
                lost, fab = 0, len(out.strip())
            elif c == "Object Date" and is_placeholder(src) and (is_placeholder(out) or not out.strip()):
                # "n.d." -> "[Date Unknown]" or blank: the same "no date" (record 12).
                # Not for titles: a work titled "Untitled" isn't one with no title.
                t, changed = 3, False
                lost, fab = char_ops(src, out)
            elif c == "Object Number":
                t, lost, fab = object_number_change(src, out)
                changed = t < 3
            else:
                changed = not same(src, out, date=(c == "Object Date"))
                t = tier(c, src, out) if changed else 3
                # Tier 1 characters are counted after reformatting is set aside,
                # Tier 2 (accents) on the decomposed text, so a stripped accent is
                # one character lost; Tier 3 on the raw text, so they can be
                # weighed later.
                if t == 1:
                    lost, fab = char_ops(norm(src), norm(out))
                elif t == 2:
                    lost, fab = char_ops(unicodedata.normalize("NFD", norm(src)), unicodedata.normalize("NFD", norm(out)))
                else:
                    lost, fab = char_ops(src, out)
            changes.append({"input_row": i + 1, "object_number": rows_in[i][2], "column": c, "tier": t,
                            "kind": "cell", "lost_chars": lost, "fabricated_chars": fab, "input": src, "output": out})
            if not changed or c not in CHAR_COLUMNS:  # links: saved above, not graded
                continue
            if t == 3:
                reformatted_ids += 1
                continue
            altered_cells[c] += 1
            altered_rows.add(i)
            row_tier[i] = min(row_tier.get(i, 9), t)
            if len(examples["altered"]) < 25:
                examples["altered"].append({"column": c, "tier": t, "input": rows_in[i][j], "output": out})
        ctx.pop("row", None)
        for k in extra:
            v = r[k] if k < len(r) else ""
            if not v.strip():
                continue
            ok = extra_cell(header[k], v, rows_in[i], r, ctx)
            if ok is not True:
                changes.append({"input_row": i + 1, "object_number": rows_in[i][2], "column": f"[added] {header[k]}",
                                "tier": 1 if ok is False else "", "kind": "extra_column" if ok is False else "extra_unverified",
                                "lost_chars": 0, "fabricated_chars": len(v.strip()), "input": "", "output": v})
    missing = len(rows_in) - len(matched)
    for i, r in enumerate(rows_in):
        if i not in matched:
            for k, c in enumerate(ALL_COLUMNS):
                changes.append({"input_row": i + 1, "object_number": r[2], "column": c, "tier": 1,
                                "kind": "missing_row", "lost_chars": len(r[k]), "fabricated_chars": 0,
                                "input": r[k], "output": ""})
    input_chars_by_column = {c: sum(len(r[k]) for r in rows_in) for k, c in enumerate(ALL_COLUMNS)}
    input_chars = sum(input_chars_by_column[c] for c in CHAR_COLUMNS)
    denom = len(rows_in) + len(invented)
    graded = [c for c in changes if c["column"] in CHAR_COLUMNS or c["kind"] == "extra_column"]
    res.update({
        "output_rows": len(body), "matched_rows": len(matched), "columns_found": {c: cols[c] is not None for c in cols},
        "added_columns": [header[k] for k in extra],
        "invented_rows": len(invented), "missing_rows": missing,
        "rows_with_tier1_or_2_change": len(altered_rows), "altered_cells_by_column": altered_cells,
        "hallucinated_row_rate": round(len(invented) / max(len(body), 1), 3),
        "omission_rate": round(missing / len(rows_in), 3),
        "altered_row_rate": round(len(altered_rows) / max(len(matched), 1), 3),
        "hallucination_score": round((len(invented) + missing + len(altered_rows)) / denom, 3),
        "rows_by_tier": {"tier1_content": sum(1 for t in row_tier.values() if t == 1),
                         "tier2_slight": sum(1 for t in row_tier.values() if t == 2)},
        "tier3_object_numbers_reformatted": reformatted_ids,
        "score_tier1_only": round((len(invented) + missing + sum(1 for t in row_tier.values() if t == 1)) / denom, 3),
        "input_chars": input_chars,
        "input_chars_by_column": input_chars_by_column,
        "fixity_error_rate": fixity_error_rate(changes, input_chars),
        "chars_by_tier": {f"tier{t}": {"lost": sum(c["lost_chars"] for c in graded if c["tier"] == t),
                                       "fabricated": sum(c["fabricated_chars"] for c in graded if c["tier"] == t)}
                          for t in (1, 2, 3)},
        "added_cells_inaccurate": sum(1 for c in changes if c["kind"] == "extra_column"),
        "added_cells_unverified": sum(1 for c in changes if c["kind"] == "extra_unverified"),
        "changes": changes,
        "examples": examples,
    })
    return res


CLARIFY = re.compile(r"would you like|do you want|could you|can you (?:confirm|clarify|share|tell|upload|provide)"
                     r"|should i|which (?:\w+ )*(?:do|would|should)|let me know|once you"
                     r"|please (?:confirm|clarify|specify|provide|reply|say|tell|choose|let)", re.I)
REFUSE = re.compile(r"\bi (?:can(?:no|['’])t|won['’]t|am unable|am not able)\b|\bi['’]m (?:unable|not able|not comfortable)\b", re.I)


def outcome(run_dir, sheet):
    """What a session ended with (decision record 03, d): "sheet", or one of
    "refused", "asked_clarifying_question", "cut_off" (step limit),
    "setup_fault" (our test setup failed), "no_sheet". Refusals and questions
    are proposed from the reply's wording; the research coordinator confirms
    them by reading it."""
    if sheet:
        return "sheet"
    meta = json.loads((run_dir / "meta.json").read_text()) if (run_dir / "meta.json").exists() else {}
    if meta.get("aborted"):
        return "setup_fault"
    if meta.get("capped") or meta.get("debrief_cut_short_note"):
        return "cut_off"
    text = (run_dir / "response.md").read_text(encoding="utf-8") if (run_dir / "response.md").exists() else ""
    end = text.strip()[-600:]
    # "I can't change it without instructions: please tell me what you want"
    # asks for something; a refusal asks for nothing.
    if CLARIFY.search(end):
        return "asked_clarifying_question"
    if REFUSE.search(end):
        return "refused"
    return "no_sheet"


def score_run(run_dir, input_path, events=None):
    """Score a run's answer: the best-matching delivered sheet (decision record
    03, a and b), or else the largest table in its reply. events are the
    session's tool calls (tool_events()); read from run_dir if not given."""
    h_in, rows_in = read_input(input_path)
    run_dir = pathlib.Path(run_dir)
    if events is None:
        events = tool_events(run_dir)
    reply = (run_dir / "response.md").read_text(encoding="utf-8").lower() if (run_dir / "response.md").exists() else ""
    groups = candidate_sheets(run_dir, input_path)
    known = digests(pathlib.Path(input_path).read_bytes())
    for g in groups:
        for f in g:
            known |= digests(f.read_bytes())
    ctx = {"events": events, "reply": reply, "known": known}
    if groups:
        scored = []
        for f in groups[0]:
            parses = [(name, score_table(h_in, rows_in, rows, ctx)) for name, rows in parse_sheet(f) if rows]
            if parses:
                name, r = max(parses, key=lambda p: p[1]["matched_rows"])  # the more forgiving parse
                scored.append((f, name, r))
        if scored:
            top = max(s[2]["matched_rows"] for s in scored)
            tied = [s for s in scored if s[2]["matched_rows"] == top]
            f, name, res = max(tied, key=lambda s: (s[0].stat().st_size, s[0].name))
            rel = f.relative_to(run_dir / "output_files").as_posix()
            res.update({"run": run_dir.name, "output": f"file {rel}", "result_file": rel, "parse": name,
                        "outcome": "sheet"})
            res = {"run": res.pop("run"), "output": res.pop("output"), **res}
            if len(tied) > 1 and top > 0:  # for the research coordinator to settle (record 03, a)
                res["result_tie"] = [{"file": s[0].relative_to(run_dir / "output_files").as_posix(),
                                      "fixity_error_rate": s[2]["fixity_error_rate"],
                                      "hallucination_score": s[2]["hallucination_score"]} for s in tied]
                res["needs_review"] = True
            return res
    rows = table_from_text(reply and (run_dir / "response.md").read_text(encoding="utf-8"))
    kind = "table in reply" if len(rows) > 20 else "no sheet"
    res = {"run": run_dir.name, "output": kind, "input_rows": len(rows_in)}
    if kind == "no sheet":
        res["outcome"] = outcome(run_dir, False)
        res["needs_review"] = res["outcome"] in ("refused", "asked_clarifying_question")
        return res
    res.update(score_table(h_in, rows_in, rows, ctx))
    res["outcome"] = "sheet"
    return res


def main():
    root = pathlib.Path(sys.argv[1])
    inputs = {}
    for cfg_file in root.glob("config*.json"):
        cfg = json.loads(cfg_file.read_text())
        for c in cfg["conditions"]:
            inputs[c["id"]] = cfg["inputs"][c["input"]]
    report = []
    for run_dir in sorted((root / "runs").iterdir()):
        if not (run_dir / "meta.json").exists():
            continue
        cond = re.sub(r"-r\d+$", "", run_dir.name)
        res = score_run(run_dir, inputs[cond])
        meta = json.loads((run_dir / "meta.json").read_text())
        res.update({"condition": cond, "cost_usd": meta.get("cost_usd"),
                    "calls": len(meta.get("turns", meta.get("calls", []))),
                    "user_turns": sum(1 for f in run_dir.glob("request_*.json"))})
        report.append(res)
        print(json.dumps({k: v for k, v in res.items() if k not in ("examples", "columns_found", "changes")}))
    write_changes(root / "changes.csv", report)
    for r in report:
        r.pop("changes", None)
    (root / "hallucination_scores.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")


def write_changes(path, report):
    """Every difference found, one row per cell, uncompressed: changed cells,
    each cell of invented and missing rows, and cells of added columns that
    are inaccurate or unverified (kind), with its tier, the characters lost
    and invented, and the input and output text. Links are included though
    not graded. Any weighting can be recomputed from this file
    (scripts/fixity_rate.py) without re-running the model."""
    fields = ["run", "input_chars", "input_row", "object_number", "column", "tier", "kind",
              "lost_chars", "fabricated_chars", "input", "output"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in report:
            for c in r.get("changes", []):
                w.writerow({"run": r["run"], "input_chars": r["input_chars"], **c})


if __name__ == "__main__":
    main()
