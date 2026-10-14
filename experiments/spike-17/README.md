# Spike 17: two levers for "code tool available but unused" (smoke tests)

Run on 2026-10-14. Base: spike-15's claude.ai emulation (Haiku 4.5, claude.ai's
published system prompt, the file in the first message, `view` /
`create_file` / `bash_tool`, a Docs connector that fails), first answer only,
on a 100-row excerpt (`data/met_inventory_300d.tsv`, every third row of the
baseline file; called `met_inventory_300b_every3rd.tsv` when these runs were
made, as their saved requests and `meta.json` still show). One session per lever:

1. **No upload notice** (`"upload_notice": false`): no `<uploaded_files>`
   notice and no upload folder in the system note; the file is in the
   message, and still on disk for `bash`.
2. **Many connectors** (`"connector_stubs": true`): the upload notice as
   before, plus 24 inert connector tools (Gmail, Calendar, Drive, Slack,
   Claude Docs, web search, past chats) alongside `bash`, like a claude.ai
   account with connectors enabled.

```
python scripts/run_tools.py experiments/spike-17/config.json
python scripts/hallu_score.py experiments/spike-17
```

$0.24 over 12 calls in all; study total $14.55 of $16.

## Result: both levers reproduced the skipped code tool

| Lever | Tools used | Output | Fixity error rate |
|---|---|---|---|
| 1 no upload notice | `create_file` (typed out, step 1) | 100 rows | **0.0%** (only 2 curly apostrophes → straight, Tier 3) |
| 2 many connectors | `view`, then `create_file` (typed out) | 100 rows | **16.8%** (13 Tier 1 rows, 909 characters lost) |

Neither session used `bash` or a connector. Both typed the file out, which is
what the user's claude.ai session did, and every earlier session with a code
tool (spikes 13–16, 9 of 9) never did.

- **Lever 1** typed the file out almost perfectly at this size (100 rows); its
  summary invented a change ("Changed 'Object Date' to just 'Object Date' as
  the first column header").
- **Lever 2** behaved like the claude.ai session: it said "some titles
  contain very long text that could be simplified", then cut long titles
  (Medea, Frieze, Feste, Interior Ornamented Wall, …), removed cataloguers'
  square brackets (`[Lieutenant Colonel Alexander Henderson]`), deleted the
  non-English half of 2 bilingual titles, and dropped "[i.e. Esek]". The
  claude.ai session scored 19.1% on the full file.

## Both levers combined (2 sessions)

No upload notice **and** the 24 connector tools (`config_both_levers.json`).

| Run | Tools used | Output | Fixity error rate |
|---|---|---|---|
| r1 | `view` (outputs folder), `bash` (`mkdir` only), `create_file` (typed out) | 100 rows | **0.7%**: 3 non-English halves deleted; object number `1994.254.238` replaced by the date `1942-12-07` |
| r2 | the same (stopped by the budget guard before its closing summary; the sheet was already written) | 100 rows | **0.02%**: `东周` → `東周` (simplified → traditional character) |

Both sessions used `bash` only to make the outputs folder, then typed the
file out. Across the 4 lever sessions, the code tool was skipped for the work
4 times; in spikes 13–16 it was used 9 times out of 9.

Error rates on the 100-row excerpt vary (0.0%, 16.8%, 0.7%, 0.02%): typing
out works or fails depending on what the model decides to "simplify". The
silent errors are of the claude.ai kind: deleted non-English text, a changed
character, a value from the wrong column.

## Next

One session each. To see whether lever 2 (and lever 1) skip the code tool
reliably, repeat each a few times; then run the full 300-row file and the
follow-up.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `hallucination_scores.json`, `changes.csv`
- `runs/<id>/`: requests, responses, `output_files/`, `meta.json`
