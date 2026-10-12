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

## Experiments

- `experiments/spike-01/`: first pass, four prompt variants, Haiku 5.5 (low),
  CSV input. See its README for setup and results.
