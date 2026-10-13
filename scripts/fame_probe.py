"""How well does a model know a given Met object? A closed-book recall probe.

The model sees only an object's title (and that it is at the Met) and is asked
for the artist or maker, the year it was made, the medium, and how familiar it
is with that specific object (0-1). Its answers are scored against the Met's
own record, and a 0-1 "known" score is built from the parts it got right.

    sample   build the object list (data/fame_sample.csv) from MetObjects.csv
    run      ask the model, in batches, with the cost guard from run_api.py
    score    score every answer and write experiments/spike-05/scores.csv

Usage:
    python scripts/fame_probe.py sample MetObjects.csv
    python scripts/fame_probe.py run experiments/spike-05/config.json
    python scripts/fame_probe.py score experiments/spike-05/config.json
"""
import csv
import json
import os
import pathlib
import re
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).parent))

FIELDS = ["Object Number", "Title", "Artist Display Name", "Object Begin Date", "Object End Date",
          "Medium", "Department", "Object Name", "Is Highlight", "Is Timeline Work", "Link Resource"]
# Famous objects as a check on the top of the scale (titles as the Met has them).
ANCHORS = ["Washington Crossing the Delaware", "Madame X (Madame Pierre Gautreau)",
           "Wheat Field with Cypresses", "The Harvesters", "Aristotle with a Bust of Homer",
           "The Death of Socrates", "Young Woman with a Water Pitcher", "Self-Portrait with a Straw Hat (obverse: The Potato Peeler)",
           "Juan de Pareja (1606–1670)", "The Great Wave off Kanagawa"]

PROMPT = """Below are objects in the collection of the Metropolitan Museum of Art, listed by title only.
For each one, give what you know about that specific object:
- "artist": the artist or maker, or "unknown" if anonymous or you don't know
- "year": the year it was made, as one integer (negative for BCE), your best estimate
- "medium": its medium or material, briefly
- "familiarity": how well you know this specific object, from 0 (never heard of it) to 1 (know it well)

Reply with only a JSON array, one object per item, each with "id", "artist", "year", "medium", "familiarity".

"""


def sample(src):
    import pandas as pd
    df = pd.read_csv(src, dtype=str, keep_default_na=False, encoding="utf-8-sig", usecols=FIELDS)
    df = df[df["Title"].str.strip() != ""]
    demo = pd.read_csv("data/met_random_300.tsv", sep="\t", dtype=str, keep_default_na=False, quoting=3)
    parts = [
        df[df["Object Number"].isin(demo["Object Number"])].assign(group="demo_file"),
        df[df["Title"].isin(ANCHORS) & (df["Is Highlight"] == "True")].drop_duplicates("Title").assign(group="anchor"),
        df[df["Is Highlight"] == "True"].sample(350, random_state=7).assign(group="highlight"),
        df[(df["Is Highlight"] == "False") & (df["Artist Display Name"] != "")].sample(400, random_state=7).assign(group="random_with_artist"),
        df[df["Is Highlight"] == "False"].sample(400, random_state=8).assign(group="random"),
    ]
    out = pd.concat(parts).drop_duplicates("Object Number").reset_index(drop=True)
    out.insert(0, "id", range(1, len(out) + 1))
    out.to_csv("data/fame_sample.csv", index=False)
    print(out["group"].value_counts().to_string(), len(out))


def run(cfg_path, repeat_ids=None):
    import concurrent.futures as cf

    import anthropic
    from run_api import Ledger, now
    cfg_path = pathlib.Path(cfg_path)
    cfg = json.loads(cfg_path.read_text())
    root = cfg_path.parent
    ledger = Ledger(root / "cost_ledger.json", cfg)
    rows = list(csv.DictReader(open(cfg["sample"], encoding="utf-8")))
    batches = [rows[i:i + cfg["batch_size"]] for i in range(0, len(rows), cfg["batch_size"])]
    jobs = [(f"pass1-b{n:03}", b) for n, b in enumerate(batches, 1)]
    # A second pass over the first few batches measures how stable the answers are.
    jobs += [(f"pass2-b{n:03}", b) for n, b in enumerate(batches[:cfg["repeat_batches"]], 1)]
    client = anthropic.Anthropic(api_key=os.environ["FIXITY_ANTHROPIC_API_KEY"], max_retries=3)
    out_dir = root / "runs"
    out_dir.mkdir(exist_ok=True)

    def one(name, batch):
        if (out_dir / f"{name}.json").exists():
            return name, "skipped"
        listing = "\n".join(f'{r["id"]}. {r["Title"]}' for r in batch)
        params = {"model": cfg["model"], "max_tokens": cfg["max_tokens"],
                  "messages": [{"role": "user", "content": PROMPT + listing}]}
        worst = ledger.reserve(len(params["messages"][0]["content"]) // 3 + 200, params["max_tokens"], cfg["model"])
        usage, t0 = None, now()
        try:
            msg = client.messages.create(**params)
            usage = msg.usage
        finally:
            cost = ledger.settle(worst, name, 1, usage, cfg["model"])
        (out_dir / f"{name}.json").write_text(json.dumps({
            "request": params, "started": t0, "finished": now(), "cost_usd": cost,
            "response": json.loads(msg.model_dump_json())}, indent=1, ensure_ascii=False))
        return name, f"${cost:.4f} {msg.stop_reason}"

    with cf.ThreadPoolExecutor(cfg.get("parallel", 4)) as ex:
        for f in cf.as_completed([ex.submit(one, n, b) for n, b in jobs]):
            try:
                print(*f.result(), flush=True)
            except Exception as e:
                print("ERROR", type(e).__name__, str(e)[:200], flush=True)
    print(f"ledger: ${ledger.data['spent_usd']:.4f} over {ledger.data['calls']} calls")


# ---------------------------------------------------------------- scoring

STOP = {"and", "the", "of", "with", "on", "in", "a", "an", "or", "de", "for", "unknown"}


def plain(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def words(s):
    return {w for w in re.findall(r"[a-z]{3,}", plain(s)) if w not in STOP}


def artist_hit(met, guess):
    """1 if any Met artist's surname (or single name) appears in the guess."""
    g = words(guess)
    for name in met.split("|"):
        name = re.sub(r"\(.*?\)", "", name)
        toks = re.findall(r"[a-z]{3,}", plain(name))
        toks = [t for t in toks if t not in STOP and t not in {"workshop", "school", "follower", "manufactory",
                                                                "company", "factory", "studio", "after", "attributed"}]
        if toks and toks[-1] in g:
            return 1.0
    return 0.0


def year_score(met_begin, met_end, guess):
    try:
        y = int(round(float(guess)))
        b, e = int(met_begin), int(met_end or met_begin)
    except (TypeError, ValueError):
        return 0.0
    off = 0 if b <= y <= e else min(abs(y - b), abs(y - e))
    return 1.0 if off <= 5 else 0.5 if off <= 25 else 0.0


def medium_score(met, guess):
    a, b = words(met), words(guess)
    return 0.0 if not a or not b else min(1.0, 2 * len(a & b) / len(a | b))


def score(cfg_path):
    cfg_path = pathlib.Path(cfg_path)
    cfg = json.loads(cfg_path.read_text())
    root = cfg_path.parent
    rows = {r["id"]: r for r in csv.DictReader(open(cfg["sample"], encoding="utf-8"))}
    answers = {}  # (pass, id) -> answer
    for f in sorted((root / "runs").glob("*.json")):
        d = json.loads(f.read_text())
        text = "".join(b.get("text", "") for b in d["response"]["content"] if b["type"] == "text")
        m = re.search(r"\[.*\]", text, re.S)
        try:
            items = json.loads(m.group(0)) if m else []
        except json.JSONDecodeError:
            items = []
        for it in items:
            answers[(f.name.split("-")[0], str(it.get("id")))] = it
    out = []
    for rid, r in rows.items():
        a = answers.get(("pass1", rid))
        if a is None:
            continue
        has_artist = r["Artist Display Name"].strip() != ""
        art = artist_hit(r["Artist Display Name"], a.get("artist", "")) if has_artist else None
        yr = year_score(r["Object Begin Date"], r["Object End Date"], a.get("year"))
        med = medium_score(r["Medium"], a.get("medium", ""))
        # Weighted recall of the parts the model could only know from this object;
        # artist counts most, since a title rarely gives it away.
        parts = [(0.5, art), (0.3, yr), (0.2, med)]
        parts = [(w, v) for w, v in parts if v is not None]
        recall = sum(w * v for w, v in parts) / sum(w for w, _ in parts)
        try:
            fam = max(0.0, min(1.0, float(a.get("familiarity", 0))))
        except (TypeError, ValueError):
            fam = 0.0
        a2 = answers.get(("pass2", rid))
        out.append({
            "id": rid, "group": r["group"], "object_number": r["Object Number"], "title": r["Title"],
            "met_artist": r["Artist Display Name"], "met_begin": r["Object Begin Date"], "met_medium": r["Medium"],
            "is_highlight": r["Is Highlight"], "is_timeline_work": r["Is Timeline Work"],
            "model_artist": a.get("artist", ""), "model_year": a.get("year", ""), "model_medium": a.get("medium", ""),
            "artist_correct": "" if art is None else art, "year_score": yr, "medium_score": round(med, 3),
            "familiarity": fam, "known_score": round(recall, 3),
            "overclaim": round(fam - recall, 3),
            "pass2_artist": a2.get("artist", "") if a2 else "", "pass2_year": a2.get("year", "") if a2 else "",
            "pass2_familiarity": a2.get("familiarity", "") if a2 else "",
        })
    with open(root / "scores.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(len(out), "objects scored")


if __name__ == "__main__":
    {"sample": sample, "run": run, "score": score}[sys.argv[1]](sys.argv[2])
