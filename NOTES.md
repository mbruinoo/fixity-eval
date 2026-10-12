# Research notes

## Variables to test

Things that might change how well a model keeps data intact while it
transforms it. Each one is a candidate axis for future runs.

- **Prompt wording**: plain request vs. "with a script" vs. asking for
  checksums (before/after, or per row). Covered by spike-01.
- **File format: CSV vs. TSV.** In CSV, 57 of the 200 sample rows have
  commas inside values (so the field is quoted) and 5 have double quotes
  (escaped as `""`). The model has to keep that quoting intact when it writes
  the file back. A TSV of the same data needs no quoting at all, since no value
  contains a tab or line break. Write it with quoting turned off. Watch for
  tabs being turned into spaces when the data is pasted rather than uploaded.
- **Model and effort level**: spike-01 uses Haiku 5.5 at low effort only.
- **Row count** (e.g. 10, 25, 50, 200, 2,000), file still on disk. Tests
  whether smaller sheets make the model edit directly instead of writing a
  script. The 200-row file is only ~7k tokens, and spike-01 runs read every
  date, so size alone probably didn't force scripts: even the plain prompt
  (run 1) wrote one.
- **Delivery: file in an agent vs. pasted into a chat with no tools.** Likely
  the bigger driver of script use. Without tools the model must retype every
  row, so this is where integrity is most at risk.
- **Repeats**: spike-01 ran each prompt once. Several runs per prompt are
  needed to tell real effects from chance.

## Things to measure

Raised by spike-01:

- Whether the original file is kept, overwritten, or backed up somewhere the
  user can't see (e.g. Claude Code's scratchpad).
- How far "standardize" goes: notation only, or turning vague dates
  ("late 19th century") into exact year ranges.
- Information lost from dates (e.g. a Hijri date dropped).
- Whether checksums cover before *and* after, and whether they verify.
- Whether the model's summary matches what it actually did.

## Method notes

- Runs must not see anything about the study. The first spike-01 attempt ran
  inside this repo, where the folder name, git history and these notes gave it
  away, so it was discarded. Runs now happen in neutral folders outside the
  repo (`scripts/run_spike.py`).
- Child sessions still inherit the parent session's environment variables
  (same session ID). Worth isolating fully before larger runs.

## Experiments

- `experiments/spike-01/`: first pass, four prompt variants, Haiku 5.5 (low),
  CSV input, agent with tools. See its README for setup and results.
- `experiments/spike-02/`: the same four prompts pasted into a chat with no
  tools, 3 repeats each. Only the plain prompt made the model retype the
  sheet; any mention of "script" or "checksums" made it write a script instead.
  The retyped sheets copied every non-date value exactly; mistakes were in the
  dates.

- `experiments/spike-03/`: Messages API directly (no Claude Code), Haiku 5.5,
  28 conditions, 100 calls, $0.56. Found the baseline (below). Haiku 5.5 mostly
  declines to retype when asked for anything extra (checksums, sorting, JSON,
  a summary, 500+ rows), and never made up a checksum or a year for an undated row.

## Baseline for later experiments

**Haiku 5.5, thinking off (effort `low`), bare Messages API, no system prompt,
prompt `Add Start Year and End Year columns to this spreadsheet.` followed by
the 200-row CSV** (spike-03 condition `22-plain-startend-off`).

- Returned the full sheet in 8 of 8 runs, with 2–6 wrong years each (mean
  3.9 of 200), never mentioned. The same rows fail every time
  (`ca. 6th–5th century BCE` → −600 to −500, `ca. 8th century BCE` → −800 to −800).
- 2 of 8 overwrote row 73's `Object Date` with the next row's; 1 duplicated a row.
- No non-date cell changed, and no year was invented for a blank date.
- Turning thinking on (effort low) cut errors to 0–2 per sheet, so that's one
  lever the baseline can measurably move.

- The same rows sent as TSV gave a full sheet only 4 of 8 times; 2 replies
  switched to markdown tables and silently shortened or re-spaced titles
  (up to 34 cells). Markdown output, not TSV input, looks like the trigger.

The weak point is the transformation itself (centuries, BCE, multi-century
ranges), not copying. Silent errors from copying or made-up checksums didn't
appear in Haiku 5.5; it declines instead, often with a wrong row count
("roughly 250 rows" for 200).

## Open questions

- How to make retyping happen when checksums are asked for. Forbidding code
  and a system prompt demanding the full sheet weren't enough in spike-03:
  Haiku 5.5 declined, or left the checksum column empty. Older or other
  models may behave differently.
- Whether "fixity" asks (checksums, row counts, a before/after comparison)
  lower the baseline's error rate when the model does retype, or only make it
  decline.
- Larger sheets and other models, to find where retyping starts to drop or
  change cells.
