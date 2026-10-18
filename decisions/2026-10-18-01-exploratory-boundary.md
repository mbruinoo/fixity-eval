# 01. Where exploratory work ends and confirmatory work begins

- **Date:** 2026-10-18
- **Status:** approved by the repo author in chat, 2026-10-18

## Context

Spikes 01–34, the corpus study and the human reviews were done on the
`exploratory` branch (October 12–17, 2026). Their wordings were chosen after
seeing their data, so none of their results can confirm anything (SPEC.md §3).
`main` started with only SPEC.md and CLAUDE.md. The exploratory branch also
has its own SPEC.md, a summary of that phase, and a HANDOFF.md from the
session that ran it.

## Decision

- The `exploratory` branch stays frozen. Its work ends at commit `0277caf`;
  HANDOFF.md is the only later commit. Nothing is committed to it.
- Files that confirmatory work needs are copied to `main` unchanged with
  `git checkout 0277caf -- <paths>`, in a commit that names the source
  (`d8d284c`). Any later change to a ported file is a separate commit.
- Exploratory results are exploratory evidence only. `main` cites them by
  commit and path rather than copying them (e.g.
  `exploratory@0277caf:experiments/spike-32/README.md`).
- `main`'s SPEC.md supersedes the SPEC.md on `exploratory`. Where HANDOFF.md
  conflicts with `main`'s SPEC.md or CLAUDE.md, those two win.
- The repo author approved including, as needed: Anthropic's published
  claude.ai system prompt (see record 08), the claude.ai transcript in
  `exploratory:experiments/claude-ai/`, and the upload guidance reconstructed
  in `scripts/run_tools.py` (see record 07).

## Consequences

- Ported: the runner (`run_tools.py`, `run_api.py`), the scoring scripts,
  `datespec.py` (for checking added date columns, record 03), the two
  sampling scripts, data files f, e and 300b, `spec/`, `prompts/`,
  `GLOSSARY.md` and the draft pre-registration.
- Left on `exploratory`: all of `experiments/`, `analysis/corpus/`,
  `analysis/review/`, `NOTES.md`, its README, SPEC.md and HANDOFF.md, the
  other data files and the scripts used only by earlier spikes.
- Confirmatory measures come only from fresh runs on `main`.
