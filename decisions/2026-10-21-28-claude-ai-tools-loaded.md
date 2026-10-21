# 28. The claude.ai check adds 5 fix-line sessions with tools always loaded

- **Date:** 2026-10-21
- **Status:** approved by the repo author in chat, 2026-10-21.

## Context

In record 24's five fix-line sessions, with code execution and file creation
on, no session ran code or made a file, and every checksum was invented or a
placeholder; two said they couldn't write files or had no filesystem access.
The repo author's claude.ai had tool access set to "Load tools when needed",
which keeps tools out of view until a session looks for them, as the
emulation's tool search does (record 19). If that is why no code ran, it
matters beyond this study: a person who asks for checksums can be given
values that look real and aren't.

## Decision

- The repo author runs 5 more fix-line sessions in claude.ai before
  2026-10-29, as in record 24, with one change: tool access mode set to the
  option that loads tools up front instead of "Load tools when needed".
  Everything else (file, request, nudges, debrief) as in record 24; saved as
  `tools-1/` to `tools-5/`.
- Scored with the same scripts; reported beside the other claude.ai sessions.
  Exploratory and descriptive.

## Consequences

- If these sessions run code and the others didn't, that points to the
  tool-access setting, not the request, as the reason; five sessions can
  suggest this, not prove it. Whether and how to tell Anthropic is the repo
  author's call.
- The order of the three sets of sessions (fix, base, tools) isn't
  randomized; stated as a limit.
