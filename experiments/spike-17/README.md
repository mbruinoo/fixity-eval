# Spike 17: two levers for "code tool available but unused" (smoke tests)

Run on 2026-10-14. Base: spike-15's claude.ai emulation (Haiku 4.5, claude.ai's
published system prompt, the file in the first message, `view` /
`create_file` / `bash_tool`, a Docs connector that fails), first answer only,
on a 100-row excerpt (`data/met_inventory_300b_every3rd.tsv`, every third row
of the baseline file). One session per lever:

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

$0.11 over 5 calls; study total $14.42 of $16.

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

## Next

One session each. To see whether lever 2 (and lever 1) skip the code tool
reliably, repeat each a few times; then run the full 300-row file and the
follow-up.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `hallucination_scores.json`, `changes.csv`
- `runs/<id>/`: requests, responses, `output_files/`, `meta.json`
