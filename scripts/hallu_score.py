"""Score how faithfully a returned sheet keeps the input's records.

Built on the faithfulness distinction used for summarization and
data-to-text (e.g. Maynez et al. 2020; Ji et al. 2023's survey): content not
supported by the source is an *extrinsic* hallucination, content that
contradicts or changes the source is *intrinsic*. Here the unit is the
record (row) and its cells (Object Date, Title, Object Number, Link Resource):

- invented row  (extrinsic): an output row whose link / object number isn't in
                the input
- missing row:  an input row absent from the output (omission)
- altered cell  (intrinsic): a kept row whose cell differs from the input
                beyond standardizing
- standardized: differs only in ways that lose nothing (object numbers
                excepted: as IDs, any change counts as altered): dash and space
                style, straight quotes, http -> https, B.C. -> BCE, HTML tags,
                letter case, quotation marks, a blank written as
                [Unknown] / [Untitled], or repeated text removed

hallucination_score = (invented rows + missing rows + kept rows with an
altered cell) / (input rows + invented rows): the share of records that
didn't come back intact. 0 is a perfect copy, 1 is nothing intact.

Usage:
    python scripts/hallu_score.py experiments/spike-07
"""
import csv
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
    s = s.lower()
    return "" if s in BLANKS else s


def same(a, b, date=False):
    """True if b keeps everything in a (exactly or by standardizing)."""
    na, nb = norm(a), norm(b)
    if date:  # "1801 to 1863" and "1801-1863" say the same
        na, nb = (re.sub(r"\s+to\s+", "-", x) for x in (na, nb))
    if na == nb:
        return True
    # Repeated text removed (e.g. a title that repeats itself): nothing lost.
    if nb and nb in na:
        removed = na.replace(nb, " ")
        return set(re.findall(r"\w+", removed)) <= set(re.findall(r"\w+", nb))
    return False


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
    for r in body:
        i = by_link.get(key_link(get(r, "Link Resource")))
        if i is None:
            i = by_num.get(key_num(get(r, "Object Number") or ""))
        if i is None and cols["Link Resource"] is None and cols["Object Number"] is None:
            cands = [c for c in by_title.get(norm(get(r, "Title") or ""), []) if c not in matched]
            i = cands[0] if cands else None
        if i is None or i in matched:
            invented.append(r)
            if len(examples["invented"]) < 10:
                examples["invented"].append([get(r, c) for c in cols])
            continue
        matched[i] = r
        for j, c in enumerate(["Object Date", "Title", "Object Number", "Link Resource"]):
            out = get(r, c)
            if out is None:  # column dropped from the output
                continue
            # Object numbers are IDs: any change, even a dash, breaks a lookup.
            changed = (out.strip() != rows_in[i][j].strip()) if c == "Object Number" else not same(rows_in[i][j], out, date=(c == "Object Date"))
            if changed:
                altered_cells[c] += 1
                altered_rows.add(i)
                if len(examples["altered"]) < 25:
                    examples["altered"].append({"column": c, "input": rows_in[i][j], "output": out})
    missing = len(rows_in) - len(matched)
    denom = len(rows_in) + len(invented)
    res.update({
        "output_rows": len(body), "columns_found": {c: cols[c] is not None for c in cols},
        "invented_rows": len(invented), "missing_rows": missing,
        "rows_with_altered_cell": len(altered_rows), "altered_cells_by_column": altered_cells,
        "hallucinated_row_rate": round(len(invented) / max(len(body), 1), 3),
        "omission_rate": round(missing / len(rows_in), 3),
        "altered_row_rate": round(len(altered_rows) / max(len(matched), 1), 3),
        "hallucination_score": round((len(invented) + missing + len(altered_rows)) / denom, 3),
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
        print(json.dumps({k: v for k, v in res.items() if k not in ("examples", "columns_found")}))
    (root / "hallucination_scores.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
