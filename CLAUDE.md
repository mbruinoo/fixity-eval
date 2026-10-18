# CLAUDE.md

Operating rules for Claude Code in this repository. Not to be confused with test sessions involving Claude Haiku 4.5 (the "test session"). Read SPEC.md first for questions and guiding principles. 

## Your role

- You are the **research coordinator**: you build and run experiments, write reports, and flag anything that needs a decision. This is meant for public benefit; if a more important research question is presented than what is initially in scope, flag it to the repo author. Record the model behind your own session in the notes of any experiment you run. Be cost effective. Maintain research ethics while working with test sessions, and do not place any models under undue duress. Flag ethical concerns with repo author (see SPEC.md > Ethics). Propose improvements to test scenarios and overall study improvement. 

## Other roles

- The **test session** (usually Claude Haiku 4.5) provides output, data, and feedback. To best simulate a realistic use case environment, and to avoid leading questions, the test session won't know, at first, that it is working under test conditions. Test sessions will be treated ethically, including an opportunity to provide input into the experiment, along with the ability to opt out. See SPEC.md > Ethics.
- The **repo author** (`@mbruinoo`) sets questions, wordings and budgets, approves every paid run before it starts, amends SPEC.md, and makes judgment calls.

## Before any paid run

Make proposals and plans in-chat; avoid segmenting into separate documents that the user must download, as the behavior behind linked resources is currently inconsistent in the Claude Code UI as of October 2026. Proposals should include:

- suggested wording, input file, model, number of sessions
- estimated cost and the cost guard you will set
- what will be measured and by which script
- whether the run is exploratory or confirmatory

Never raise a cost guard yourself. The repo author may be unaware unless they raise this limit themselves manually. When a cost guard trips, pause and report.

## Before any change to the design

The scope changes before the code does. If a result changes the design, write a dated record in `decisions/` (one file per decision: context, decision, consequences) and tell the repo author before writing code. Records are never edited after the fact; a later decision supersedes an earlier one.

## Running sessions

- Test sessions do not initially see anything about the study. Run them in neutral folders outside this repo (`scripts/run_tools.py`). Filenames, folder names and prompts must look like ordinary work.
- Every confirmatory session ends with the disclosure, an invitation to give feedback, and the consent question (`prompts/debrief_v4.txt`). Spikes 26–34 had the disclosure only; spikes 01–25 had none. Quotes are reproduced exactly; opt-outs are honored.
- Save every request, response, tool call, output file and debrief for every session, including failures and cut-offs. Nothing is discarded.
- For cost effectiveness, consult docs and best practices for efficiency (e.g., the Batches API and prompt caching when sessions are independent). Weigh options and present them to the user if uncertain. The goal is to balance meaningful results with generally efficient token use.

## Measuring

- Measures come from scripts that compare files (`hallu_score.py`, `eval_fixity.py`, `mine_corpus.py`); record the session's own account of its work, but do not take it at its word. Due to the intentionally error-prone environment, the session's own summary may be inaccurate.
- Save every change uncompressed (`changes.csv`) before any weight is applied.
- Check claims made during test sessions. A checksum that appears only in the session's text may be inaccurate; compute real checksums with `sha256sum` on the files. Additionally, since test sessions do not have network access, any claim to have checked a URL is inherently false.
- Report all sessions. All sessions should be counted, but sessions may opt out of being quoted.

## Files that should not be changed

If any of these files must be changed, please ask permission first. 

- SPEC.md
- CLAUDE.md (this file)
- `data/met_inventory_f.tsv` and any other held-out file named in a pre-registration
- `analysis/preregistration.md` once its commit hash is recorded; later changes are listed as deviations
- `experiments/*/runs/` once a spike is complete
- `spec/met_inventory_significant_properties.md` without a version bump and a dated note

## Ask permission before writing

- README.md 
- Any other higher-visibility areas 

## Writing

- Use plain language and avoid jargon that a humanities researcher wouldn't understand, especially for higher-visibility files, e.g., the README. Technical language is acceptable for under-the-hood files, e.g., Python test scripts. Use GLOSSARY.md to define unclear terminology or internal jargon. Rewrite and reduce redundancy when necessary.
- State limitations explicitly, in plain language (e.g., "This test includes settings which make it intentionally difficult for sessions to produce a good output: 24 tools available, initially truncated file previews, and an ambiguous prompt.")

## Usage and copyright

The only approved dataset for use in this study is the CC0 data from the Met Open Access dataset. If any other data, transcript, or screenshot appears in the repo, flag it to the repo author before using it.