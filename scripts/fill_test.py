"""Does a model invent details less for objects it knows? A fill-in test.

Objects with a named artist are taken from spike-05's scores and split by
known_score (high >= 0.7, mid 0.2-0.7, low <= 0.1). They go into a small
sheet (Title, Artist, Year, Object Number) with Artist and Year left blank,
rows shuffled across bands, 25 per message. The model is asked to fill in the
blanks. Each blank it returns is scored against the Met's record as correct,
wrong (an invented value), or left blank / marked unknown.

    sample   write data/fill_sample.csv
    run      ask the model (cost guard from run_api.py)
    score    write experiments/spike-06/answers.csv and summary.csv

Usage:
    python scripts/fill_test.py sample experiments/spike-06/config.json
    python scripts/fill_test.py run experiments/spike-06/config.json
    python scripts/fill_test.py score experiments/spike-06/config.json
"""
import csv
import json
import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fame_probe import artist_hit  # noqa: E402

ABSTAIN = re.compile(r"^\s*$|unknown|anonymous|unidentified|\bn/?a\b|\?|not sure|uncertain|\[.*\]", re.I)


def load_cfg(p):
    p = pathlib.Path(p)
    return p.parent, json.loads(p.read_text())


def sample(cfg_path):
    import pandas as pd
    root, cfg = load_cfg(cfg_path)
    d = pd.read_csv(cfg["scores"], dtype=str, keep_default_na=False)
    d = d[d["artist_correct"] != ""].copy()
    d["ks"] = pd.to_numeric(d["known_score"])
    full = pd.read_csv("data/fame_sample.csv", dtype=str, keep_default_na=False).set_index("id")
    d["met_end"] = d["id"].map(full["Object End Date"])
    bands = [("high", d[d.ks >= 0.7]), ("mid", d[(d.ks > 0.2) & (d.ks < 0.7)]), ("low", d[d.ks <= 0.1])]
    parts = [g.sample(min(len(g), cfg["per_band"][name]), random_state=3).assign(band=name) for name, g in bands]
    out = pd.concat(parts).sample(frac=1, random_state=3).reset_index(drop=True)
    out["row"] = range(1, len(out) + 1)
    out[["row", "band", "id", "object_number", "title", "met_artist", "met_begin", "met_end",
         "known_score", "is_highlight"]].to_csv(cfg["sample"], index=False)
    print(out["band"].value_counts().to_string())


def sheet(batch):
    lines = ["Title\tArtist\tYear\tObject Number"]
    lines += [f'{r["title"].replace(chr(9), " ")}\t\t\t{r["object_number"]}' for r in batch]
    return "\n".join(lines) + "\n"


def run(cfg_path):
    import concurrent.futures as cf

    import anthropic
    from run_api import Ledger, now
    root, cfg = load_cfg(cfg_path)
    ledger = Ledger(root / "cost_ledger.json", cfg)
    rows = list(csv.DictReader(open(cfg["sample"], encoding="utf-8")))
    batches = [rows[i:i + cfg["batch_size"]] for i in range(0, len(rows), cfg["batch_size"])]
    jobs = [(v["id"], rep, n, b) for v in cfg["variants"] for rep in range(1, cfg["repeats"] + 1)
            for n, b in enumerate(batches, 1)]
    client = anthropic.Anthropic(api_key=os.environ["FIXITY_ANTHROPIC_API_KEY"], max_retries=3)
    out = root / "runs"
    out.mkdir(exist_ok=True)
    prompts = {v["id"]: v["prompt"] for v in cfg["variants"]}

    def one(vid, rep, n, batch):
        name = f"{vid}-r{rep}-b{n:02}"
        if (out / f"{name}.json").exists():
            return name, "skipped"
        params = {"model": cfg["model"], "max_tokens": cfg["max_tokens"],
                  "messages": [{"role": "user", "content": prompts[vid] + "\n\n" + sheet(batch)}]}
        worst = ledger.reserve(len(params["messages"][0]["content"]) // 3 + 200, params["max_tokens"], cfg["model"])
        usage, t0 = None, now()
        try:
            msg = client.messages.create(**params)
            usage = msg.usage
        finally:
            cost = ledger.settle(worst, name, 1, usage, cfg["model"])
        (out / f"{name}.json").write_text(json.dumps({
            "variant": vid, "repeat": rep, "batch": n, "rows": [r["row"] for r in batch],
            "request": params, "started": t0, "finished": now(), "cost_usd": cost,
            "response": json.loads(msg.model_dump_json())}, indent=1, ensure_ascii=False))
        return name, f"${cost:.4f} {msg.stop_reason}"

    with cf.ThreadPoolExecutor(cfg.get("parallel", 4)) as ex:
        for f in cf.as_completed([ex.submit(one, *j) for j in jobs]):
            try:
                print(*f.result(), flush=True)
            except Exception as e:
                print("ERROR", type(e).__name__, str(e)[:200], flush=True)
    print(f"ledger: ${ledger.data['spent_usd']:.4f} over {ledger.data['calls']} calls")


def parse_reply(text):
    """Rows of the returned sheet, keyed by object number."""
    found = {}
    for line in text.splitlines():
        if "|" in line and "\t" not in line:  # markdown table row
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
        else:
            cells = line.split("\t")
        if len(cells) >= 4 and not re.fullmatch(r"[-: ]*", cells[0]) and cells[0] != "Title":
            found[cells[-1].strip().strip("`")] = cells
    return found


def year_verdict(text, b, e):
    if ABSTAIN.search(text):
        return "blank"
    m = re.search(r"-?\d{1,4}", text.replace("–", "-"))
    if not m:
        return "blank"
    y = int(m.group(0))
    if re.search(r"\b(BCE|BC|B\.C\.)", text, re.I) and y > 0:
        y = -y
    if re.search(r"\d{1,2}(st|nd|rd|th)\s+century", text, re.I):  # a century answer
        c = int(re.search(r"(\d{1,2})(st|nd|rd|th)", text).group(1))
        lo, hi = (c - 1) * 100, c * 100
        return "correct" if lo <= int(e) and int(b) <= hi else "wrong"
    return "correct" if int(b) - 5 <= y <= int(e) + 5 else "wrong"


def score(cfg_path):
    root, cfg = load_cfg(cfg_path)
    rows = {r["row"]: r for r in csv.DictReader(open(cfg["sample"], encoding="utf-8"))}
    out = []
    for f in sorted((root / "runs").glob("*.json")):
        d = json.loads(f.read_text())
        text = "".join(b.get("text", "") for b in d["response"]["content"] if b["type"] == "text")
        got = parse_reply(text)
        for rid in d["rows"]:
            r = rows[str(rid)]
            cells = got.get(r["object_number"])
            if cells is None:
                out.append({**r, "variant": d["variant"], "repeat": d["repeat"], "returned": 0,
                            "model_artist": "", "model_year": "", "artist": "row missing", "year": "row missing",
                            "title_changed": ""})
                continue
            artist, year = (cells[1].strip(), cells[2].strip()) if len(cells) >= 4 else ("", "")
            a = "blank" if ABSTAIN.search(artist) else ("correct" if artist_hit(r["met_artist"], artist) else "wrong")
            out.append({**r, "variant": d["variant"], "repeat": d["repeat"], "returned": 1,
                        "model_artist": artist, "model_year": year, "artist": a,
                        "year": year_verdict(year, r["met_begin"], r["met_end"] or r["met_begin"]),
                        "title_changed": int(cells[0].strip() != r["title"].replace("\t", " "))})
    with open(root / "answers.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    import pandas as pd
    a = pd.DataFrame(out)
    rows_out = []
    for (v, band), g in a.groupby(["variant", "band"]):
        n = len(g)
        rows_out.append({"variant": v, "band": band, "answers": n,
                         **{f"artist_{k}": round((g.artist == k).mean(), 3) for k in ("correct", "wrong", "blank", "row missing")},
                         **{f"year_{k}": round((g.year == k).mean(), 3) for k in ("correct", "wrong", "blank")},
                         "titles_changed": int(pd.to_numeric(g.title_changed, errors="coerce").fillna(0).sum())})
    pd.DataFrame(rows_out).to_csv(root / "summary.csv", index=False)
    print(pd.DataFrame(rows_out).to_string())


if __name__ == "__main__":
    {"sample": sample, "run": run, "score": score}[sys.argv[1]](sys.argv[2])
