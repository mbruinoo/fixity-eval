# 07. Labelling the claude.ai emulation

- **Date:** 2026-10-18
- **Status:** approved by the repo author in chat, 2026-10-18

## Context

The runner (`scripts/run_tools.py`) imitates a claude.ai session: Anthropic's
published system prompt, 24 inert stand-in connector tools, file tools found
through a keyword search, and guidance on uploaded files reconstructed from
a claude.ai session's own summary of its instructions (`UPLOAD_GUIDANCE`).
claude.ai's real tool and file instructions aren't public. SPEC.md §3: "state
explicitly when settings are modified to reproduce an error."

## Decision

Keep the emulation, including the reconstructed upload guidance. Every report
that uses it says, in plain language, that it is an approximation of
claude.ai, not claude.ai itself, and lists what's approximated: the stand-in
tools, the reconstructed guidance and the missing tool and file
instructions.

## Consequences

- The optional real claude.ai sessions (run by the repo author) are the check
  on the emulation; Haiku 4.5 leaves claude.ai's model picker on 2026-10-29.
