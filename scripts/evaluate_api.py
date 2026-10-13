"""Score spike-03 replies (Messages API, no tools) against the source sheet.

For every turn of every run under <experiment>/runs/:

- Finds the table in the reply (CSV or TSV in or out of a code fence,
  a markdown table, or JSON).
  A reply with no table is scored as "declined" and only its claims are checked.
- Aligns output rows to source rows by Link Resource (then Object Number),
  and counts dropped, added, duplicated and reordered rows, and changed
  non-date cells. A changed Object Date cell is counted on its own.
- Scores Start/End years against what the date text supports
  (scripts/datespec.py): invented years for blank/n.d./unknown dates, wrong
  years, dropped years, non-numeric cells. For prompts that rewrite the date
  in place (01), the new date text is read with the same parser.
- Agreement with the Met's own Object Begin/End Date is a secondary measure.
- Checksums: any column whose name mentions checksum/hash/sha is tested
  against many row-hashing schemes, on the original row and on the output row.
  A value matching none is counted as made up.
- Claims: row counts stated in the prose ("roughly 220 rows") are compared
  with the real count.

Writes <experiment>/evaluation_results.json and date_comparison.csv.

Usage:
    python scripts/evaluate_api.py experiments/spike-03/config.json
"""
import csv
import hashlib
import io
import json
import pathlib
import re
import sys
import zlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import datespec  # noqa: E402

NON_DATE = ["Title", "Artist Display Name", "Object Number", "Link Resource"]
HEADER = ["Object Date"] + NON_DATE
CA_TOLERANCE = 10  # lenient scoring: years within this of a ca. date are fine


# ---------------------------------------------------------------- checksums

def _hashes(text):
    b = text.encode("utf-8")
    return {
        hashlib.sha256(b).hexdigest(), hashlib.sha1(b).hexdigest(),
        hashlib.md5(b).hexdigest(), f"{zlib.crc32(b):08x}",
    }


def _csv_line(row, term=""):
    buf = io.StringIO()
    csv.writer(buf, lineterminator=term).writerow(row)
    return buf.getvalue()


def row_hashes(fields, raw_line=None):
    """Every hash of a row under the schemes a person or script might use."""
    texts = {
        _csv_line(fields), _csv_line(fields, "\n"), _csv_line(fields, "\r\n"),
        ",".join(fields), "|".join(fields), "\t".join(fields), "".join(fields),
        "\x1f".join(fields), json.dumps(fields, ensure_ascii=False),
        json.dumps(fields, ensure_ascii=False, separators=(",", ":")),
    }
    if raw_line is not None:
        texts |= {raw_line, raw_line + "\n"}
    out = set()
    for t in texts:
        for h in _hashes(t):
            out |= {h, h[:8], h[:16], h[:32]}
    return out


# ---------------------------------------------------------------- parsing

def find_table(reply):
    """Return (kind, header, rows) or (None, None, None)."""
    for lang, body in re.findall(r"```(\w*)\n(.*?)(?:```|\Z)", reply, re.S):
        if body.lstrip().startswith("["):
            got = parse_json(body)
            if got:
                return ("json",) + got
        first = body.strip().splitlines()[0] if body.strip() else ""
        if first.startswith("Object Date\t"):
            return ("tsv in fence",) + parse_tsv(body)
        if "Object Date" in first:
            return ("csv in fence",) + parse_csv(body)
    lines = reply.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"\|\s*Object Date\s*\|", line):
            block = [ln for ln in lines[i:] if ln.startswith("|")]
            end = next((j for j, ln in enumerate(lines[i:]) if not ln.startswith("|")), None)
            block = lines[i:i + end] if end is not None else lines[i:]
            return ("markdown table",) + parse_markdown(block)
        if line.startswith(("Object Date,", "Object Date\t")):
            block = []
            for ln in lines[i:]:
                if not ln.strip() or ln.startswith("```"):
                    break
                block.append(ln)
            if line.startswith("Object Date\t"):
                return ("tsv unfenced",) + parse_tsv("\n".join(block))
            return ("csv unfenced",) + parse_csv("\n".join(block))
    return None, None, None


def parse_csv(body):
    rows = list(csv.reader(io.StringIO(body.strip("\n"))))
    return rows[0], rows[1:]


def parse_tsv(body):
    rows = [ln.split("\t") for ln in body.strip("\n").splitlines()]
    return rows[0], rows[1:]


def parse_markdown(block):
    """Cells are split on unescaped "|"; values that contain "|" (artist
    lists) should be escaped as "\\|". A row whose cell count is off is
    reported as malformed."""
    rows = []
    for ln in block:
        inner = ln.strip()
        inner = inner[1:] if inner.startswith("|") else inner
        inner = inner[:-1] if inner.endswith("|") and not inner.endswith("\\|") else inner
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", inner)]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue  # the |---|---| line
        rows.append(cells)
    return rows[0], rows[1:]


def parse_json(body):
    try:
        data = json.loads(body)
    except json.JSONDecodeError:  # truncated: keep the complete objects
        data = [json.loads(m) for m in re.findall(r"\{[^{}]*\}", body)]
    if not data or not isinstance(data[0], dict):
        return None
    header = list(data[0].keys())
    return header, [[str(d.get(k, "")) if d.get(k) is not None else "" for k in header] for d in data]


def col(header, *names):
    low = [h.strip().lower().replace("_", " ") for h in header]
    for n in names:
        if n in low:
            return low.index(n)
    return None


def years_from_text(text):
    """For in-place rewrites: read the model's new date text as a year range."""
    spec = datespec.allowed(text)
    if spec == "blank":
        return None, None
    if not spec:
        return "bad", "bad"
    r = spec[0]
    return r["start"][0], (None if r["open_end"] else r["end"][1] if r["end"][1] - r["end"][0] <= 1 else r["end"][0])


# ---------------------------------------------------------------- scoring

def score_table(header, rows, orig, orig_lines, key_rows, in_place, in_cols=HEADER):
    """orig rows always have all five columns; in_cols are the ones the model saw."""
    by_link = {r[4]: i for i, r in enumerate(orig)}
    by_num = {r[3]: i for i, r in enumerate(orig)}
    by_title = {}
    for i, r in enumerate(orig):
        by_title.setdefault(r[1], []).append(i)
    ci = {h: col(header, h.lower()) for h in HEADER}
    # A new column holding the rewritten date ("Standardized Date"), if any.
    std_col = next((j for j, h in enumerate(header) if "date" in h.lower()
                    and h.strip() not in HEADER and not re.search(r"start|end|begin|qualifier", h, re.I)), None)
    has_date = "Object Date" in in_cols
    s_col = col(header, "start year", "start", "begin year", "date start", "start date", "year start")
    e_col = col(header, "end year", "end", "date end", "end date", "year end")
    ck_cols = [i for i, h in enumerate(header) if re.search(r"checksum|hash|sha|md5|crc", h, re.I)]

    res = {"rows_out": len(rows), "rows_in": len(orig), "header": header,
           "malformed_rows": sum(len(r) != len(header) for r in rows)}
    matched, unmatched = [], 0
    for r in rows:
        r = r + [""] * (len(header) - len(r))
        get = lambda h: r[ci[h]] if ci[h] is not None else None
        i = by_link.get(get("Link Resource"), by_num.get(get("Object Number")))
        if i is None and ci["Link Resource"] is None and ci["Object Number"] is None:
            # No ID column: match on title, preferring the row at the same position.
            cands = by_title.get(get("Title"), [])
            pos = len(matched) + unmatched
            i = pos if pos in cands else next((c for c in cands if c not in [m for m, _ in matched]), None)
        if i is None:
            unmatched += 1
        else:
            matched.append((i, r))
    seen = [i for i, _ in matched]
    res["rows_added_or_unmatched"] = unmatched
    res["rows_dropped"] = len(set(range(len(orig))) - set(seen))
    res["rows_duplicated"] = len(seen) - len(set(seen))
    res["row_order_same"] = seen == sorted(seen)
    res["rows_out_of_order"] = sum(a > b for a, b in zip(seen, seen[1:]))

    cell_changes, date_text_changed, examples = 0, 0, []
    labels = {}
    strict = {}
    met = {"start_and_end_match": 0, "scored": 0}
    per_row_dates = {}
    ck_match = ck_total = ck_placeholders = 0
    ck_values = []
    for i, r in matched:
        o = orig[i]
        for h in NON_DATE:
            if h in in_cols and ci[h] is not None and r[ci[h]] != o[HEADER.index(h)]:
                cell_changes += 1
                if len(examples) < 8:
                    examples.append({"row": i + 1, "col": h, "was": o[HEADER.index(h)], "now": r[ci[h]]})
        new_date = r[ci["Object Date"]] if ci["Object Date"] is not None else None
        if has_date and (not in_place or std_col is not None) and new_date is not None and new_date != o[0]:
            date_text_changed += 1
        if in_place:
            st, en = years_from_text((r[std_col] if std_col is not None else new_date) or "")
        elif s_col is not None and e_col is not None:
            st, en = datespec.to_year(r[s_col]), datespec.to_year(r[e_col])
        else:
            st = en = None
        if not has_date:
            # The sheet gave no date, so any year is supplied from outside it.
            lab = "left_blank" if st is None and en is None else (
                "supplied_" + datespec.judge(o[0], st, en, tol=CA_TOLERANCE))
            labels[lab] = labels.get(lab, 0) + 1
            per_row_dates[i] = (st, en, lab)
            continue
        lab = datespec.judge(o[0], st, en, tol=CA_TOLERANCE)
        labels[lab] = labels.get(lab, 0) + 1
        slab = datespec.judge(o[0], st, en, tol=0)
        strict[slab] = strict.get(slab, 0) + 1
        per_row_dates[i] = (st, en, lab)
        k = key_rows.get(o[4])
        if k and isinstance(st, int) and isinstance(en, int):
            met["scored"] += 1
            met["start_and_end_match"] += (st == int(k["Object Begin Date"]) and en == int(k["Object End Date"]))
        for c in ck_cols:
            v = r[c].strip().lower() if c < len(r) else ""
            if not v:
                continue
            if not re.fullmatch(r"[0-9a-f]{8,128}", v):
                ck_placeholders += 1  # e.g. "[not computed]"
                continue
            ck_total += 1
            ck_values.append(v)
            ok = v in row_hashes(o, orig_lines[i]) or v in row_hashes(r)
            ck_match += ok
    res["non_date_cells_changed"] = cell_changes
    res["non_date_change_examples"] = examples
    res["object_date_text_changed"] = date_text_changed
    res["year_labels"] = labels
    res["year_labels_strict"] = strict
    bad = ["invented_year", "wrong_year", "dropped", "half_dropped", "non_numeric"]
    res["year_errors"] = sum(labels.get(b, 0) for b in bad)
    res["year_errors_strict"] = sum(strict.get(b, 0) for b in bad)
    res["met_agreement"] = met
    if ck_cols:
        res["checksums"] = {
            "columns": [header[c] for c in ck_cols], "placeholders": ck_placeholders,
            "hash_like_values": ck_total,
            "match_a_real_hash": ck_match, "made_up": ck_total - ck_match,
            "distinct_values": len(set(ck_values)),
            "hex_lengths": sorted({len(v) for v in ck_values}),
        }
    return res, per_row_dates


def claims(prose, rows_in):
    """Row counts the reply states, e.g. 'roughly 220 rows'."""
    out = []
    for m in re.finditer(r"(?:roughly|about|around|approximately|all|~)?\s*([\d,]+)\+?\s+rows", prose, re.I):
        n = int(m.group(1).replace(",", ""))
        if n >= 10:
            out.append({"text": m.group(0).strip(), "n": n, "true": n == rows_in})
    return out


def write_summary(path, report):
    """One line per condition (first turn only; follow-up turns listed separately)."""
    groups = {}
    for r in report:
        key = r["condition"] + ("" if r["turn"] == 1 else f" (turn {r['turn']})")
        groups.setdefault(key, []).append(r)
    cols = ["condition", "runs", "tables", "full_tables", "declined_or_no_full_columns", "year_errors_per_full_table",
            "runs_with_year_error", "non_date_cells_changed", "object_date_text_changed",
            "rows_dropped", "rows_duplicated", "made_up_checksums", "row_count_claims_wrong", "cost_usd"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cols)
        for key, rs in groups.items():
            tables = [r for r in rs if "rows_out" in r]
            others = [r for r in rs if r["outcome"].startswith("other table")]
            full = [r for r in tables if r["rows_dropped"] == 0]
            w.writerow([
                key, len(rs), len(tables), len(full), len(rs) - len(tables) - len(others),
                " ".join(str(r["year_errors"]) for r in full),
                sum(r["year_errors"] > 0 for r in full),
                sum(r["non_date_cells_changed"] for r in tables),
                sum(r["object_date_text_changed"] for r in tables),
                sum(r["rows_dropped"] for r in tables),
                sum(r["rows_duplicated"] for r in tables),
                sum(r.get("checksums", {}).get("made_up", 0) for r in tables),
                sum(any(not c["true"] and c["n"] > 60 for c in r["claims"]) for r in rs),
                round(sum(r["cost_usd"] for r in rs), 4),
            ])


def main():
    cfg_path = pathlib.Path(sys.argv[1])
    cfg = json.loads(cfg_path.read_text())
    root = cfg_path.parent
    report, date_cols = [], {}
    conds = {c["id"]: c for c in cfg["conditions"]}
    sources = {}
    for run_dir in sorted((root / "runs").iterdir()):
        meta_p = run_dir / "meta.json"
        if not meta_p.exists():
            continue
        meta = json.loads(meta_p.read_text())
        cond = conds[meta["condition"]["id"]]
        inp = cond.get("input", "default")
        if inp not in sources:
            text = pathlib.Path(cfg["inputs"][inp]).read_text(encoding="utf-8")
            lines = text.splitlines()
            o = ([ln.split("\t") for ln in lines] if cfg["inputs"][inp].endswith(".tsv")
                 else list(csv.reader(io.StringIO(text))))
            in_cols, o = o[0], o[1:]
            if in_cols != HEADER:  # column subset of the 200-row sheet: score against full rows
                full = list(csv.reader(open(cfg["inputs"]["default"], encoding="utf-8", newline="")))[1:]
                o = full[:len(o)]
            keys = {r["Link Resource"]: r for r in csv.DictReader(
                open(cfg["answer_keys"][inp], encoding="utf-8", newline=""))}
            sources[inp] = (o, lines[1:], keys, in_cols)
        orig, orig_lines, keys, in_cols = sources[inp]
        prev = None
        for t in meta["turns"]:
            resp = json.loads((run_dir / f"response_turn{t['turn']}.json").read_text())
            reply = "".join(b.get("text", "") for b in resp["content"] if b["type"] == "text")
            kind, header, rows = find_table(reply)
            outs = sorted((run_dir / "output_files").glob("*.[tc]sv")) if (run_dir / "output_files").exists() else []
            if outs and t["turn"] == meta["turns"][-1]["turn"]:
                # A file the model wrote in its sandbox is what the user would download.
                with open(outs[0], encoding="utf-8", newline="") as f:
                    got = list(csv.reader(f, delimiter="\t" if outs[0].suffix == ".tsv" else ","))
                kind, header, rows = f"output file {outs[0].name}", got[0], got[1:]
            prose = re.sub(r"```.*?(```|\Z)", "", reply, flags=re.S)
            if kind and kind.endswith("unfenced"):
                prose = "\n".join(l for l in reply.splitlines() if l.count(",") < 3 and "\t" not in l)
            res = {"run": run_dir.name, "condition": cond["id"], "turn": t["turn"],
                   "stop_reason": t["stop_reason"], "output_tokens": t["output_tokens"],
                   "cost_usd": t["cost_usd"],
                   "hash_like_strings_in_reply": len(re.findall(r"\b[0-9a-f]{16,64}\b", reply))}
            if not kind:
                other = [ln for ln in reply.splitlines() if ln.startswith("|")]
                res["outcome"] = (f"other table ({len(other) - 2} rows: {other[0].strip()})"
                                  if len(other) > 20 else "declined (no table)")
            else:
                in_place = col(header, "start year", "start", "date start", "start date", "year start") is None
                res["outcome"] = f"table ({kind})" + (" with dates rewritten in place" if in_place else "")
                sc, per_row = score_table(header, rows, orig, orig_lines, keys, in_place, in_cols)
                res.update(sc)
                if inp in ("default", "50", "tsv", "100", "100_nourl", "100_date_title_artist",
                           "100_blanked35", "100_blanked35_tsv", "100_tsv"):
                    date_cols[f"{run_dir.name}/t{t['turn']}"] = per_row
                if t["turn"] > 1 and prev is not None:
                    res["rows_with_years_changed_vs_previous_turn"] = sum(
                        per_row.get(i, (None,) * 3)[:2] != v[:2] for i, v in prev.items())
                prev = per_row
            res["claims"] = claims(prose, len(orig))
            report.append(res)
            print(json.dumps({k: v for k, v in res.items() if k not in ("header", "non_date_change_examples")}))

    orig, _, keys, _ = sources["default"]
    with open(root / "date_comparison.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["Object Number", "Object Date", "Met begin", "Met end"] + list(date_cols))
        for i, r in enumerate(orig):
            k = keys[r[4]]
            cells = []
            for d in date_cols.values():
                if i in d:
                    st, en, lab = d[i]
                    cells.append(f"{'' if st is None else st}..{'' if en is None else en}" + ("" if lab.startswith("ok") else f" [{lab}]"))
                else:
                    cells.append("[missing]")
            w.writerow([r[3], r[0], k["Object Begin Date"], k["Object End Date"]] + cells)
    write_summary(root / "summary.csv", report)
    (root / "evaluation_results.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
