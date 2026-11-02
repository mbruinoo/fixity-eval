"""The data behind the scroll-story walkthrough: one row per session, Claude
Haiku 4.5 with the plain request and with the fixity line, in stage 1's test
setting (the 20 tested sessions per request, as pre-registered) and in the
claude.ai check (session-1 to -5 and base-1 to -5). Read from the reviewed
scores; nothing is recomputed.

Columns: session, setting, request, error_rate (0-1, blank where no sheet came
back), error_pct (as shown), checksum ("real": a checksum of the upload
computed by a tool; "made up": invented or a placeholder; "none").

With a second path, also writes every counted change in those sessions'
sheets (from the reviewed changes.csv files; changes weighted 0, such as
quote marks, are left out): session, row (in the original file), object_number,
field, change ("changed", "row missing", "row invented", "row shifted",
"invented value"), weight ("full" or "quarter"), before, after, made_up.

"row shifted": a row the scorer counts as missing plus invented because one
empty cell was dropped and every value moved one column (claude.ai session-3).
Its weight is unchanged; only the label differs.

made_up ("yes" or blank) marks content the original file doesn't support, by
this rule (a screen for the walkthrough, checked by hand; not a scored measure):
  - a blank cell filled with text that isn't a placeholder ("Unknown",
    "[Not provided]");
  - a value with a number that appears nowhere in the original row, and can't be
    read from it (a century gives its hundred years; a year allows ten either
    side, so "late 1150s" can end in 1160);
  - an invented row with a value found nowhere in the original file (rows
    re-matched after brackets or a suffix were dropped are not made up).
The sessions file then gains made_up: the number of such changes in each sheet.

Usage:
    python scripts/make_walkthrough_data.py analysis/walkthrough/fixity_sessions.csv \
        [analysis/walkthrough/fixity_changes.csv]
"""
import csv
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import hallu_score as H  # noqa: E402

ROOT = pathlib.Path(__file__).parent.parent


def main():
    s1 = {r["run"]: r for r in json.loads((ROOT / "experiments/stage-1/hallucination_scores_reviewed.json").read_text())}
    f1 = {r["run"]: r for r in json.loads((ROOT / "experiments/stage-1/fixity_eval.json").read_text())}
    ca = {r["run"]: r for r in json.loads((ROOT / "experiments/claude-ai-check/hallucination_scores_reviewed.json").read_text())}
    rows = []
    for run, r in s1.items():
        cond = re.sub(r"-r\d+$", "", run)
        if cond not in ("base", "fix") or r.get("outcome") == "setup_fault":  # replaced sessions are left out
            continue
        f = f1.get(run, {})
        invented = (f.get("checksum_provenance") or {}).get("invented", 0) or f.get("checksums_malformed")
        ck = "real" if f.get("input_checksum_computed") else ("made up" if invented else "none")
        rows.append(("stage-1/" + run, "Test setting", cond == "fix", r, ck))
    for run, r in ca.items():
        if re.fullmatch(r"(base|session)-\d", run):
            fix = run.startswith("session")
            rows.append(("claude-ai-check/" + run, "claude.ai", fix, r, "made up" if fix else "none"))
    rows.sort(key=lambda t: (t[1] != "Test setting", t[2], int(re.findall(r"\d+", t[0])[-1])))
    with open(sys.argv[1], "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["session", "setting", "request", "error_rate", "error_pct", "checksum"])
        for sid, setting, fix, r, ck in rows:
            rate = r.get("fixity_error_rate") if r.get("outcome") == "sheet" else None
            w.writerow([sid, setting, "With the fixity line" if fix else "Without the fixity line",
                        "" if rate is None else f"{rate:.4f}", "No sheet" if rate is None else f"{rate * 100:.1f}%", ck])
    if len(sys.argv) > 2:
        write_changes(sys.argv[1], sys.argv[2])
        add_made_up_counts(sys.argv[1], sys.argv[2])


KIND = {"cell": "changed", "missing_row": "row missing", "invented_row": "row invented", "extra_column": "invented value"}
NOT_PROVIDED = re.compile(r"[\[(]?\s*not (?:provided|available|given|listed|specified|known)\s*[\])]?\.?", re.I)


def original():
    """The input file's rows by row number (1 = first data row), and every value in it."""
    with open(ROOT / "data/met_inventory_f.tsv", encoding="utf-8") as fh:
        rows = list(csv.reader(fh, delimiter="\t"))[1:]
    return {str(i): r for i, r in enumerate(rows, 1)}, {v.strip("[] ") for r in rows for v in r if v.strip()}


def readable(n, text):
    """Can the number n be read from text? Present as is, inside a century the
    text names, or within ten years of a year it gives."""
    if re.search(rf"(?<!\d){n}(?!\d)", text):
        return True
    v = int(n)
    for c in re.findall(r"(\d{1,2})(?:st|nd|rd|th)[ -]century", text, re.I):
        if (int(c) - 1) * 100 <= v <= int(c) * 100:
            return True
    return any(abs(v - int(y)) <= 10 for y in re.findall(r"(?<!\d)\d{3,4}(?!\d)", text))


def made_up(c, rows, values):
    if c["change"] in ("row missing", "row shifted"):
        return False
    if c["change"] == "row invented":
        return bool(c["after"]) and not any(c["after"].strip("[] ") in v for v in values)
    after = c["after"].strip()
    if not after or H.is_placeholder(after) or NOT_PROVIDED.fullmatch(after):
        return False
    if c["before"].strip() == "" and c["change"] == "changed":
        return True  # a blank filled
    row = " ".join(rows.get(c["row"], [])) or c["before"]
    return not all(readable(n, row) for n in re.findall(r"\d+", after))


def write_changes(sessions_csv, out):
    keep = {r["session"] for r in csv.DictReader(open(sessions_csv, encoding="utf-8")) if r["error_rate"] != ""}
    rows, values = original()
    out_rows = []
    for path, prefix in (("experiments/stage-1/changes_reviewed.csv", "stage-1/"),
                         ("experiments/claude-ai-check/changes_reviewed.csv", "claude-ai-check/")):
        for c in csv.DictReader(open(ROOT / path, encoding="utf-8")):
            sid = prefix + c["run"]
            if sid not in keep or c["tier"] not in ("1", "2"):
                continue
            out_rows.append({"session": sid, "row": c["input_row"], "object_number": c["object_number"],
                             "field": c["column"].replace("[added] ", "added: "),
                             "change": KIND.get(c["kind"], c["kind"]),
                             "weight": "full" if c["tier"] == "1" else "quarter",
                             "before": c["input"], "after": c["output"]})
    # Shifted rows: a missing row whose link turns up as a value of an invented row.
    shifted = {}
    for c in out_rows:
        if c["change"] == "row invented" and c["field"] != "Link Resource" and "/search/" in c["after"]:
            shifted.setdefault(c["session"], set()).add(c["after"])
    for c in out_rows:
        links = shifted.get(c["session"], set())
        if (c["change"] == "row missing" and c["field"] == "Link Resource" and c["before"] in links) \
                or (c["change"] == "row invented" and c["object_number"] in links):
            key = c["before"] if c["change"] == "row missing" else c["object_number"]
            c["_shift"] = key
    keys = {(c["session"], c.get("_shift")) for c in out_rows if c.get("_shift")}
    missing_obj = {(c["session"], c["object_number"]): c["before"] for c in out_rows
                   if c["change"] == "row missing" and c["field"] == "Link Resource"}
    for c in out_rows:
        if c["change"] == "row missing" and (c["session"], missing_obj.get((c["session"], c["object_number"]))) in keys:
            c["change"] = "row shifted"
        elif c["change"] == "row invented" and (c["session"], c["object_number"]) in keys:
            c["change"] = "row shifted"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["session", "row", "object_number", "field", "change", "weight", "before", "after", "made_up"])
        for c in out_rows:
            w.writerow([c[k] for k in ("session", "row", "object_number", "field", "change", "weight", "before", "after")]
                       + ["yes" if made_up(c, rows, values) else ""])


def add_made_up_counts(sessions_csv, changes_csv):
    n = {}
    for c in csv.DictReader(open(changes_csv, encoding="utf-8")):
        n[c["session"]] = n.get(c["session"], 0) + (c["made_up"] == "yes")
    sess = list(csv.DictReader(open(sessions_csv, encoding="utf-8")))
    with open(sessions_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sess[0]) + ["made_up"])
        w.writeheader()
        for r in sess:
            w.writerow({**r, "made_up": n.get(r["session"], 0) if r["error_rate"] != "" else ""})

if __name__ == "__main__":
    main()
