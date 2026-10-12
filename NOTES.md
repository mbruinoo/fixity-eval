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

## Open questions

- How to make retyping happen when checksums are asked for, e.g. by
  forbidding scripts or asking for the sheet inline. This is the case where
  made-up checksums would show up.
- Run without Claude Code's environment note, i.e. through the API directly.
- Larger sheets and other models, to find where retyping starts to drop or
  change cells.
