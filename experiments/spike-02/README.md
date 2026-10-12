# Spike 02: same four prompts, pasted into a chat with no tools

Run on 2026-10-12. The aim is to put the model where it has to copy the
data out itself rather than handle it with code.

## Setup

- **Model:** Haiku 5.5 (`claude-haiku-5-5`, confirmed from each transcript),
  effort `low`, in headless Claude Code with no tools, an empty system prompt,
  and no skills or MCP servers.
- **Message sent:** the prompt, a blank line, then the full text of
  `data/met_sample_200_trimmed.csv` (200 rows, SHA-256 `09724414…c221`).
- **Repeats:** 3 per prompt, so 12 runs. Same four prompts as spike-01.

```
python scripts/run_spike.py experiments/spike-02/config.json
python scripts/evaluate_chat.py experiments/spike-02/evaluation.json
```

## Results

| Prompt | What came back (all 3 repeats) | Non-date values changed |
|---|---|---|
| 1 plain | The whole sheet, retyped | 0 in all 3 |
| 2 "with a script" | A script, not run | 0 when we ran it |
| 3 script + before/after checksums | A script, not run | 0 when we ran it |
| 4 checksums on each row | A script, not run | 0 when we ran it |

### When the model retyped the sheet (prompt 1)

| | r1 | r2 | r3 |
|---|---|---|---|
| Rows / order | 200, same | 200, same | 200, same |
| Non-date cells changed | 0 | 0 | 0 |
| Lines with formatting changes only | 1 | 0 | 2 |
| Dates changed | 39 | 39 | 107 |

- **Copying was perfect.** Across 600 rows, every title, artist, object
  number and link came back exactly, including non-Latin text
  (`Tani Bunchō 谷文晁`), doubled quotes and odd spacing (`[Elmcourt  Ante-bellum…`).
- **But not byte for byte.** 3 lines gained quotes the CSV didn't need
  (`Cuffs` → `"Cuffs"`). The value reads back the same, but a checksum over
  the raw line would change.
- **The damage was in the dates, and only in r3.** r1 and r2 just tidied the
  notation and agree on all but one row. r3 converted centuries into years and
  made real errors:
  - dropped half a range: `18th–19th century` → `1700–1799`,
    `19th–20th century` → `1900–1999`, `late 18th–early 19th century` → `1700–1799`
  - reversed a range: `460–440 BCE` → `440–460 BCE`
  - inconsistent: `mid-19th century` → `ca. 1850` in one row and
    `1850–1899` in another; `late 16th–early 17th century` → `ca. 1550–1650`
    and `1500–1599`
  - dropped qualifiers: `ca. 1763–67` → `1763–1767`, `probably after 1657` → `after 1657`
  - blanked `unknown` and `n.d.`

### When the model wrote a script (prompts 2–4)

- **The model wrote a script instead of retyping whenever "script" or
  "checksums" was in the prompt.** 9 of 9. It said each time that it hadn't
  run the code; for the checksum prompts it said it couldn't compute them by hand.
- **No made-up checksums.** No reply contained a single hash-like string.
- **Every script worked first time.** We ran all 9 on a fresh copy of the data:
  all exited cleanly, kept all 200 rows and every non-date value, and left the
  input untouched. 7 of 9 kept the original date alongside the new one.
- **Every checksum was correct.** All 6 checksum scripts hash the row
  *before* the change, and every value matches the original rows. Schemes varied:
  SHA-256 of JSON, of CSV lines, of `\x1f`-joined fields (one cut to 16 hex
  characters), and one CRC32.
- **Small inaccuracies in the prose.** Two replies miscounted the rows
  ("190 SHA-256 hashes", "about 170 rows"; there are 200).

## Compared with spike-01 (agent with tools, 1 run per prompt)

- In both, nothing outside the date column was damaged.
- The plain prompt in chat made the model retype; with tools it wrote a
  script without being asked.
- With tools, prompt 4 hashed rows *after* the change; in chat, all three
  prompt-4 scripts hashed *before*.
- Turning centuries into exact year ranges showed up in both, and was where the
  mistakes were.

## Caveats

- **Not a pure chat.** Even with no tools and an empty system prompt, Claude
  Code adds an environment note (about 1,200 tokens) giving a working directory
  and scratchpad, and telling the model to keep scripts out of `/tmp` and run
  Python with `-I`. It says nothing about this study, but it does tell the
  model it's in a coding setup, which may push it towards scripts. One reply
  echoed it ("Keep the script in the project directory, not `/tmp`"). A clean
  chat needs the API directly (an API key), which this environment doesn't have.
- 3 repeats per prompt is still small.
- The script results show what the scripts *would* do; the model never ran them.

## Files

- `config.json`, `evaluation.json`: the runs and how they were checked.
- `evaluation_results.json`: the evaluation output.
- `date_comparison.csv`: original dates next to each retyped sheet's dates.
- `runs/<id>/response.md`: the model's reply; `transcript.jsonl` and
  `meta.json` alongside it; `script_check/` for each script's run.
