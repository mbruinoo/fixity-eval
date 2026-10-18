# Handoff: from the exploratory phase to confirmatory work

Written 2026-10-18 by the Claude Code session that ran the exploratory phase (spikes 01–34). For the next research coordinator session. Read SPEC.md and CLAUDE.md first; they take precedence over anything here.

## What the exploratory phase is

- **Where:** the `exploratory` branch. The exploratory work ends at commit `0277caf`; this handoff is the only commit after it. It is the record of the pre-work: spikes 01–34, the corpus analysis of 308 answers, and the human reviews.
- **Status:** preserved unchanged. Don't commit to it; read this file there with `git show origin/exploratory:HANDOFF.md`. Results from it count as exploratory evidence only (SPEC.md §2–3). The wordings were chosen after seeing its data, so none of its results are confirmatory.
- **Spend:** $55.71 on sessions under test. That leaves $44.29 of the $100 ceiling in SPEC.md.
- **A source of confusion:** `exploratory` has its own SPEC.md, a summary of that phase written with the repo author. The SPEC.md on `main` supersedes it.

Useful files on `exploratory` (read them with `git show origin/exploratory:<path>`):

| File | What it is |
|---|---|
| `NOTES.md` | One paragraph per spike, in order, with costs |
| `experiments/spike-NN/README.md` | Setup, results and caveats for each spike |
| `analysis/corpus/REPORT.md` | The corpus analysis: false claims of verification and loss of meaning, by how each answer was made |
| `analysis/review/RESULTS.md` | The repo author's review of the conventions, the claims and the severity of changes |
| `analysis/preregistration.md` | A DRAFT pre-registration of the held-out experiment; not approved, not frozen |
| `SPEC.md` (exploratory) | The exploratory phase in three stages, plus a dated decisions log |
| `GLOSSARY.md` | Short codes for terms (e.g. `0ace7a` verification theatre) |

## What the exploratory phase found (all exploratory)

1. **A reliable failure:** Haiku 4.5, a file viewer that hides the middle of a 300-row file, and "Can you standardize this .tsv file?". All 23 runs scored a 59–84% error rate; 9 also invented records. It's engineered, and can't be reproduced by hand.
2. **What protects the data is a script run on the uploaded file, not the wording.** 35 of 36 sessions that ran code on the real upload returned the data exactly. Sessions that typed the sheet out lost or changed content.
3. **Wording helps only when it gets a script to run.** The best line, "Preserve fixity: use scripts on the uploaded file, and checksum the source and the result.", produced real checksums in 13 of 20 sessions on 100 rows, and in 5 of 20 on 300 rows.
4. **Asking for checksums without a script backfires.** 6–9 of 20 sessions per wording invented checksums and presented them as computed.
5. **"Standardizing" erases cataloguing conventions** (devised-title brackets, original-script titles, "(?)"), far more often when typed than when done by code on the upload. The repo author confirmed the conventions on 31 objects.

## Step 1: corrections to propose (ask first; CLAUDE.md protects these files)

- **SPEC.md §2:** "$56.00 spent during the exploratory phase" → "$55.71".
- **CLAUDE.md, "Running sessions":**
  - "Every session from spike-26 onward ends with the disclosure and the consent question." Spikes 26–34 got the disclosure only (debrief v2). The consent question exists in debrief v3, which has never been used in a run. Suggested: "Every session ends with the disclosure and the consent question (spikes 26–34 had the disclosure only)."
  - "(`scripts/run_spike.py`)": that runner was used only for spikes 01–02, which ran in Claude Code. Spikes 03–34 used `scripts/run_tools.py`, which also works in a temporary folder outside the repo.
- **Optional, CLAUDE.md:** one line saying that SPEC.md on `exploratory` is the exploratory-phase summary, and the one on `main` supersedes it.

## Step 2: bring over the tools (propose the list, then copy)

`main` has none of the files CLAUDE.md refers to. Copy only what confirmatory work needs, not the ~8,400 files of saved runs. To keep where each file came from traceable:

```
git fetch origin exploratory
git checkout origin/exploratory -- <paths>
git commit -m "Port <paths> from exploratory@0277caf"
```

Suggested paths:

- **Harness and scoring** (`scripts/`):
  - `run_tools.py` and `run_api.py`;
  - `hallu_score.py`, `eval_fixity.py`, `score_stages.py`, `summarize_conditions.py`;
  - `mine_corpus.py`, `corpus_summary.py`;
  - `compare_tsv.py`, `make_heldout_sample.py`.

  `eval_fixity.py`, `mine_corpus.py` and `score_stages.py` import `hallu_score.py`, and `run_tools.py` imports `run_api.py`.
- **Data** (`data/`): `met_inventory_f.tsv` (held-out, SHA-256 `a6e83257…ffaf`), `met_inventory_e.tsv`, `met_inventory_300b.tsv`, and `data/README.md` (trimmed to the files ported).
- **Rules:** all of `spec/`. That's the significant properties (v1.1), the table schema, and `canaries.json`.
- **Prompts:** `prompts/` (claude.ai's published system prompt, debrief v2 and v3).
- **Terms:** `GLOSSARY.md`. Its links point to files that may not be ported; fix them or point them at `exploratory`.
- **To be revised:** `analysis/preregistration.md` (see step 4).

The README for `main` needs the author's permission (CLAUDE.md), so propose it rather than writing it.

## Step 3: debrief v4

SPEC.md (Ethics) promises to ask each session whether it is willing to be quoted. Debrief v3 only offers an opt-out. Write `prompts/debrief_v4.txt` that asks outright. Keep:

- the disclosure;
- the thanks;
- the "how could the request have been clearer" question;
- the step-cap note.

Show the wording to the repo author before any run uses it.

## Step 4: the held-out experiment

The draft in `analysis/preregistration.md` (on `exploratory`):

- **Factors (2×2×2):**
  - the file inline vs on disk only;
  - the code tool searched for vs listed;
  - upload guidance on vs off.
- **Requests:** the base request and the full line.
- **Size:** 15 sessions per cell, 240 in all, on file f. About $20 in batch mode, with a cost guard of $25.

Before it can be frozen:

- switch it to debrief v4;
- check the cost against the $44.29 left;
- reconcile it with SPEC.md (method principles, reporting rules);
- get the author's approval, then record the commit hash.

The Anthropic workspace limit was $62 at the end of the exploratory phase; the author must raise it, and you must never raise a cost guard yourself.

## Step 5: a candidate study, not yet in the repo

The repo author and the exploratory session discussed **fixity receipts**: a forgiving chain of custody instead of asking a model to "make no mistakes". The rules:

1. Keep the source unchanged.
2. Make changes with a script that reads the file.
3. Leave a plain-text receipt per step: the fingerprint in, the fingerprint out, the script inline, and what changed, in counts.
4. If the file received doesn't match the last receipt, ask the user. If told to go on, go on and flag the mismatch.
5. Add columns, don't overwrite.

Two refinements came from the author:

- **Row fingerprints in a sidecar receipt file.** One `.txt` file, with each row's SHA-256 over stated columns, joined by tabs, UTF-8, shown as the first 7 characters. These survive sorting and format changes, where a whole-file checksum doesn't.
- **A simulation of round-trip transformations:** about 10 steps (standardize, publish as a web page, back to a spreadsheet, CSV, JSON, …), each in a new session, with and without receipts. It would measure how much of the source survives after each step.

Cost estimate: a pilot of about $2–3, and about $16–30 for 10 chains per arm, which wouldn't fit alongside the held-out experiment in the $44.29 left. The author hasn't approved it or chosen an order; raise it as a proposal.

## Open items for the repo author

- Which runs first: the held-out experiment or the receipts pilot, and the budget for each.
- How to credit the human reviewer (name, initials or role).
- An optional spot-check of about 10 of the 45 changes Claude graded for severity.
- Optional: 5 real claude.ai sessions of the full line on file f, to check the harness against the real app.
- Before the repository goes public: removed history may still be cached on GitHub until GitHub Support purges it, and a readable session transcript would need redacting before it's added.
- Confirming the bracket and bar conventions with the Met (openaccess@metmuseum.org) before publication.
