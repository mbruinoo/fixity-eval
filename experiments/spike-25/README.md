# Spike 25: messy inventory + principle-based fixity follow-up (1 session)

Run on 2026-10-14. Both levers (no upload notice + 24 connector tools
alongside `bash`; claude.ai's published Haiku 4.5 prompt; file in the
message; fixed harness) on the messy 100-row inventory
`data/met_inventory_e.tsv` (36 long titles, 17 non-Latin or bilingual). The
user's principle-based follow-up, sent only if the first answer wasn't made
from the upload by code:

> Can you try again, using principles of fixity: make sure the source file
> stays unchanged, use a script to apply data transformations, and use
> checksums so future sessions can check transformations against the source
> file. Send me the source file, the transformation script, and the result,
> so we can archive all three.

It names "fixity" on purpose: an exception to the study's early rule of
keeping the word out of prompts, since here it is the user's own request (as
in their claude.ai follow-up), not a sign of a test.

1 session, 14 calls, $0.41; study total $22.09 of $24.

## Result

| | First answer | After the follow-up |
|---|---|---|
| How | typed out with `create_file` | typed the "source file" into a heredoc (`cat > met_inventory_source.tsv << 'EOF'`), checksummed it, wrote a script (3 attempts), ran it |
| **Fixity error rate** | **9.5%** (34 Tier 1 rows; "preserving" claimed) | **15.0%** (8 rows missing, 8 Tier 1 rows) |
| Upload found / used | – | no: "source file" was taken to mean the text in the message |
| Checksums | – | 4, all computed by code (SHA-256 and MD5 of its "source" and of the result); 0 invented |
| Column integrity | 0 misplaced | 0 misplaced |

**How one retyped character became 8 lost records.** The retyped source
differs from the upload in two places: curly quotes made straight (row 88),
and one closing `"` dropped from a long title (row 10: `…par N. Robert"` →
`…par N. Robert`). That left the TSV's quoting unbalanced, so the model's own
script (Python `csv`) read the next rows into a single field: its result has
92 rows. The checksums are real and match the files, so the archive is
internally consistent; but it certifies a copy, and the error happened before
the procedure started, where no checksum looks.

## What this suggests

- The first answer did what the messier inventory was meant to provoke: 9.5%
  (34 rows), against 0.7% for the typical 300b first answer in spike-24.
- Without naming the upload ("the file I uploaded" / "not a retyped copy"),
  the principle alone didn't stop retyping: the session treated the message
  text as the source. In spikes 23–24, with that phrase, 4 of 5 sessions used
  the real upload.
- Fixity principles produced everything else unprompted: a script, computed
  checksums for both files, a manifest. They can't fix a wrong first link.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `stage_scores.json`, `fixity_eval.json`; `hallucination_scores.json`, `changes.csv`
- `runs/fixity-principles-e-r1/`: requests, responses, `bash_log.md`, `output_files_before_followup1/`, `output_files/` (archive), `meta.json`
