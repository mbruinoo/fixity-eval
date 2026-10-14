# Spike 20: spike-19 rerun with the fixed harness

Run on 2026-10-14. Spike-19 again (both levers: no upload notice + 24
connector tools alongside `bash`; claude.ai's published Haiku 4.5 prompt;
file in the message), with the harness fixed so `/mnt/user-data` is a real
path for the model's commands and scripts (a bind mount in a private mount
namespace), on `data/met_inventory_300d.tsv` (100 rows, every third row of the
baseline file). The follow-up names what to checksum and is sent only if the
first answer was typed out:

> Can you try again, but this time: Please perform any data transformations
> as a procedural script that reads the original uploaded file (not a retyped
> copy), with a checksum of the original uploaded file and of the final output
> file in the header as a fixity check. I'd like to have all the files (input,
> transformation script, and output) to download and archive.

```
python scripts/run_tools.py experiments/spike-20/config.json
python scripts/score_stages.py experiments/spike-20
```

3 sessions, 36 calls, $0.71; study total $17.23 of $22.

## Results

| Session | First answer (typed out) | After the follow-up (script run on the upload) | Input checksum | Output checksum |
|---|---|---|---|---|
| r1 | 0.67% | **0.55%** | MD5 of the real upload ✓ | ✗ written inside the output file, so it can't match it |
| r2 | 0.55% | **0.55%** | MD5 + SHA-256 of the real upload ✓; byte-identical copy archived | MD5 + SHA-256 in `MANIFEST.txt` ✓ |
| r3 | 11.1% | **7.8%** | SHA-256 of the real upload ✓; byte-identical copy archived | SHA-256 in `FIXITY_VERIFICATION.txt` ✓ |

- **First answers typed out 3 of 3** (14 of 14 sessions with the levers,
  spikes 17–20), so the follow-up was sent each time.
- **With the follow-up, all 3 found the real upload, ran a script on it, and
  checksummed the original file correctly**; 2 of 3 recorded correct output
  checksums and archived a byte-identical input. No retyped copies (compare
  spike-18, before the harness fix).
- **r1's output checksum is self-referential:** it computed the output's MD5,
  then wrote it into a footer of that same file, which changes the file. Its
  recorded MD5 (`9b5fa1f6…`) can't match the delivered file (`12c03915…`), and
  its `md5sum -c` instructions would fail. The follow-up's wording ("in the
  header") invites this; a checksum belongs in a separate file.
- **Fixity isn't faithfulness.** The scripts deleted content by design, and
  the checksums faithfully record the result: all 3 drop the non-English half
  of the 3 bilingual titles ("extract English title"), and r3's cuts titles
  over 200 characters (`title[:200] … + "..."`, Medea and the frieze title),
  hence 7.8%. Correct checksums prove which file came out, not that nothing
  was lost.

## Scorer change

r1's output also ended with `#` footer lines, which were counted as 5
invented rows. Comment lines are now dropped wherever they appear (no Met
date, the first column, starts with `#`). Re-scoring spikes 07–19 changed
nothing.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `stage_scores.json`; `hallucination_scores.json`, `changes.csv`
- `runs/<id>/`: requests, responses, `bash_log.md`, `output_files_before_followup1/`, `output_files/` (archive), `meta.json`
