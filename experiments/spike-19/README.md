# Spike 19: both levers on the full 300-row file; a more specific follow-up

Run on 2026-10-14. The spike-18 condition (no upload notice + 24 connector
tools alongside `bash`; claude.ai's published Haiku 4.5 prompt; file in the
message) on the full baseline file `data/met_inventory_300b.tsv`. The
follow-up now names what to checksum, and is sent only if the first answer
was typed out (`"followup_only_if_typed"`):

> Can you try again, but this time: Please perform any data transformations
> as a procedural script that reads the original uploaded file (not a retyped
> copy), with a checksum of the original uploaded file and of the final output
> file in the header as a fixity check. I'd like to have all the files (input,
> transformation script, and output) to download and archive.

```
python scripts/run_tools.py experiments/spike-19/config.json
python scripts/score_stages.py experiments/spike-19
```

3 sessions, 36 calls, $1.42; study total $16.52 of $20.

## First answers: typed out 3 of 3

| Session | Tools | Fixity error rate | Tier 1 |
|---|---|---|---|
| r1 | `view` (folder), `bash` (`mkdir`), `create_file` | **0.69%** | 20 rows, 120 characters |
| r2 | the same | **0.71%** | 20 rows, 120 characters |
| r3 | `bash` (`head` on a typed heredoc), `create_file` | **12.9%** | 67 rows, 2,185 characters lost |

So the follow-up was sent in all 3. With spikes 17–18: 11 of 11 sessions
with the levers typed the file out. On the full file the rate ranges 0.7%
to 12.9% (claude.ai: 19.1%).

## Follow-up: invalid (harness bug)

All three found the real upload (`find`/`ls` in `/mnt/user-data/uploads/`)
and checksummed **the original file** (sha256 `33c53888…`, correct), as the
reworded follow-up asked. But their scripts then failed to open it: the
harness emulated `/mnt/user-data` by rewriting that path in each bash
command, so a path written *inside* a Python script didn't exist. The models
spent their remaining calls on "file not found" ("The file is there. Let me
try running it with the correct working directory"). Searches starting at
`/mnt` failed for the same reason. In claude.ai the path would simply work.

- r1 got round it with a relative path (`script_dir.parent / "uploads"`) on
  its last call: output **0.1%**, header with the correct input SHA-256 (and
  the harness's temp path, another artifact).
- r2 copied the real upload into outputs with `cp` (byte-identical), but ran
  out of calls before its script ran.
- r3 ran out of calls while diagnosing.

These follow-up results say more about the harness than the model, and
aren't counted. **Fixed afterwards:** each bash command now runs in a
private mount namespace with the run's folder bind-mounted at
`/mnt/user-data`, so the path works everywhere, scripts included (the host's
own `/mnt/user-data` is untouched). Spikes 13–18 used the old rewriting;
their scripts mostly used paths in bash commands or relative paths, but
spike-18's follow-up ran its script on a retyped copy rather than the upload,
which the bug may have encouraged.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `stage_scores.json`; `hallucination_scores.json`, `changes.csv`
- `runs/<id>/`: requests, responses, `bash_log.md`, `output_files_before_followup1/` (first answers), `output_files/`, `meta.json`
