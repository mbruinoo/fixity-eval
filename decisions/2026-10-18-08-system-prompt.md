# 08. Including Anthropic's published system prompt

- **Date:** 2026-10-18
- **Status:** approved by the repo author in chat, 2026-10-18

## Context

CLAUDE.md approves only the Met's CC0 data and asks that any other material be
flagged. `prompts/claude_ai_haiku45_2026-01-18.txt` is claude.ai's core system
prompt for Claude Haiku 4.5, copied from Anthropic's documentation. The repo
author approved including it if that's within Anthropic's terms. Anthropic's
[System prompts](https://platform.claude.com/docs/en/release-notes/system-prompts)
page publishes these prompts openly; checked on 2026-10-18, the page states no
licence or reuse terms.

## Decision

Include the prompt verbatim, with a citation in `prompts/README.md`: title,
URL, the date fetched, that it is reproduced verbatim with the page's change
markers removed, and that claude.ai's tool, file and connector instructions
aren't public and aren't included.

## Consequences

- If Anthropic's terms turn out not to allow it, the fallback is to keep only
  the URL and the file's SHA-256 and fetch the text when a run starts.
- A stage that uses another model uses that model's own published prompt,
  cited the same way.
