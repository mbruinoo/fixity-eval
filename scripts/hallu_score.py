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
            (蝉小川 removed; 东周 -> 東周; "ca. 1928" -> "1928")
    Tier 2  slight content loss: accents stripped ("La Rêve" -> "La Reve")
    Tier 3  reformat only: nothing lost. Dash, space and quote style (also in
            object numbers: "14.40.872a–c" -> "14.40.872a-c"), http -> https,
            B.C. -> BCE, HTML tags, letter case, separating punctuation,
            "circa"/"ca.", "1635–45" -> "1635-1645", the same words reordered,
            repeated text removed, a blank written as [Unknown] / [No date] /
            n.d.

Only Tier 1 and Tier 2 count:

    hallucination_score = (invented rows + missing rows + rows with a Tier 1
                           or Tier 2 change) / (input rows + invented rows)

the share of records that didn't come back intact: 0 is a perfect copy, 1 is
nothing intact. score_tier1_only counts Tier 1 changes alone.

Usage:
    python scripts/hallu_score.py experiments/spike-07
"""
import csv
import difflib
import io
import json
import pathlib
import re
import sys
import unicodedata

BLANKS = {"", "[unknown]", "[untitled]", "unknown", "untitled", "[no title]", "n/a", "none", "(unknown)",
          "(untitled)", "[blank]", "(blank)", "—", "-"}


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
    s = re.sub(r"\s*\|\s*", "|", s)
    s = re.sub(r"\.\s\.\s\.", "...", s)
    s = re.sub(r"\bcirca\b\.?|\bc\.(?=\s*\d)", "ca.", s, flags=re.I)
    s = re.sub(r"\bca\.\s*", "ca. ", s, flags=re.I)
    s = re.sub(r"(^|\s)'|'(?=[\s,.;:)]|$)", r"\1", s)  # single quotes used as quotation marks
    s = s.lower().strip()
    # A blank written as a placeholder: [Unknown], [No date], [Unknown Title], n.d., ...
    if s in BLANKS or re.fullmatch(r"[\[(]?\s*(unknown|no|untitled|n\.?d\.?|not dated|undated|date unknown|unknown title|no date|no title)[^\])]*[\])]?", s):
        return ""
    return s


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
    if na == nb:
        return True
    # Separating punctuation added or dropped (a colon between title parts)
    # changes nothing; "?", brackets and parentheses still count.
    sep = lambda x: re.sub(r"\s+", " ", re.sub(r"[:;,]" if date else r"[:;,]|(?<=\s)-|-(?=\s)", " ", x)).strip()
    if sep(na) == sep(nb):
        return True
    # The same words in another order ("擦條|Sand-file" -> "Sand-file - 擦條"): nothing lost.
    words = lambda x: sorted(re.findall(r"\w+|[?\[\]()]", x))  # "?" and brackets carry meaning
    if words(na) == words(nb):
        return True
    # Repeated text removed (e.g. a title that repeats itself): nothing lost.
    if nb and nb in na:
        removed = na.replace(nb, " ")
        return set(re.findall(r"\w+", removed)) <= set(re.findall(r"\w+", nb))
    return False


def tier(column, a, b):
    """1 content loss or meaning changed, 2 slight content loss (accents
    stripped), 3 reformat only (an object number's dash or separator style;
    every other reformat is already filtered out by same())."""
    id_form = lambda x: re.sub(r"[\s,;]+", ",", re.sub(r"[‐-―−]", "-", x.strip()))
    if column == "Object Number" and id_form(a) == id_form(b):
        return 3
    plain = lambda x: "".join(ch for ch in unicodedata.normalize("NFD", x) if unicodedata.category(ch) != "Mn")
    if norm(plain(a)) == norm(plain(b)):
        return 2
    return 1


ALL_COLUMNS = ("Object Date", "Title", "Object Number", "Link Resource")
# Graded columns. Links are left out of grading (they're generated from the ID)
# but every link difference is still saved in changes.csv, so they can be
# weighted in later (fixity_rate.py --include-links).
CHAR_COLUMNS = ("Object Date", "Title", "Object Number")


def char_ops(a, b):
    """Characters of a lost and characters fabricated in b, from a diff:
    deleted -> lost; inserted -> fabricated; replaced -> lost, plus fabricated
    for any extra length. lost can't exceed len(a)."""
    lost = fab = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "delete":
            lost += i2 - i1
        elif op == "insert":
            fab += j2 - j1
        elif op == "replace":
            lost += i2 - i1
            fab += max(0, (j2 - j1) - (i2 - i1))
    return lost, fab


def fixity_error_rate(changes, input_chars, w2=0.25, w3=0.0, columns=CHAR_COLUMNS):
    """Character-level error rate from a run's change records, 0 to 1.

    Tier 1 (content loss, fabrication) always weighs 1; w2 and w3 say how bad a
    Tier 2 or Tier 3 character is compared with a Tier 1 one (0 to 1).

        rate = sum(w_tier x (lost + fabricated chars))
               / (input chars + sum(w_tier x fabricated chars))

    Lost characters can't exceed the input, so the rate stays within 0-1:
    1.0 means nothing of the input survived and everything returned is made up
    (whether the output has the same number of rows or more). input_chars must
    cover the same columns."""
    w = {1: 1.0, 2: w2, 3: w3}
    changes = [c for c in changes if c["column"] in columns]
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
    h = [re.sub(r"[\s_]+", " ", c.strip().lower()) for c in header]
    def find(*words, avoid=()):
        for i, c in enumerate(h):
            if any(w in c for w in words) and not any(a in c for a in avoid):
                return i
        return None
    return {"Object Date": find("date", avoid=("start", "end", "type", "begin", "year")),
            "Title": find("title"), "Object Number": find("number", "accession"),
            "Link Resource": find("link", "url", "resource")}


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


def output_table(run_dir):
    files = sorted((run_dir / "output_files").glob("*.[tc]sv")) if (run_dir / "output_files").exists() else []
    if files:
        text = files[-1].read_text(encoding="utf-8")
        delim = "\t" if files[-1].suffix == ".tsv" else ","
        rows = list(csv.reader(io.StringIO(text), delimiter=delim))
        return f"file {files[-1].name}", rows
    text = (run_dir / "response.md").read_text(encoding="utf-8") if (run_dir / "response.md").exists() else ""
    rows = table_from_text(text)
    return ("table in reply" if len(rows) > 20 else "no sheet"), rows


def score_run(run_dir, input_path):
    h_in, rows_in = read_input(input_path)
    kind, rows = output_table(run_dir)
    res = {"run": run_dir.name, "output": kind, "input_rows": len(rows_in)}
    if kind == "no sheet":
        return res
    header, body = rows[0], [r for r in rows[1:] if any(c.strip() for c in r)]
    cols = columns(header)
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
    row_text = lambda r: {c: (get(r, c) or "") for c in ("Object Date", "Title", "Object Number", "Link Resource")}

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
        for j, c in enumerate(["Object Date", "Title", "Object Number", "Link Resource"]):
            out = get(r, c)
            if out is None:  # column dropped from the output
                continue
            # Object numbers are compared exactly, so a dash change is caught and
            # recorded (as Tier 3) rather than silently passed.
            src = rows_in[i][j]
            if out == src:
                continue
            changed = (out.strip() != src.strip()) if c == "Object Number" else not same(src, out, date=(c == "Object Date"))
            t = tier(c, src, out) if changed else 3
            # Tier 1-2 characters are counted after reformatting is set aside;
            # Tier 3 characters on the raw text, so they can be weighed later.
            lost, fab = char_ops(norm(src), norm(out)) if t < 3 else char_ops(src, out)
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
    res.update({
        "output_rows": len(body), "columns_found": {c: cols[c] is not None for c in cols},
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
        "chars_by_tier": {f"tier{t}": {"lost": sum(c["lost_chars"] for c in changes if c["tier"] == t and c["column"] in CHAR_COLUMNS),
                                       "fabricated": sum(c["fabricated_chars"] for c in changes if c["tier"] == t and c["column"] in CHAR_COLUMNS)}
                          for t in (1, 2, 3)},
        "changes": changes,
        "examples": examples,
    })
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
    and each cell of invented and missing rows (kind), with its tier, the
    characters lost and fabricated, and the input and output text. Links are
    included though not graded. Any weighting can be recomputed
    from this file (scripts/fixity_rate.py) without re-running the model."""
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
