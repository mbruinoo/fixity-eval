# Prompts

## `claude_ai_haiku45_2026-01-18.txt`

claude.ai's core system prompt for Claude Haiku 4.5, dated January 18, 2026.

- **Source:** Anthropic, "System prompts: Claude Haiku 4.5", Claude Platform
  documentation, release notes.
  <https://platform.claude.com/docs/en/release-notes/system-prompts/claude-haiku-4-5>
  (index: <https://platform.claude.com/docs/en/release-notes/system-prompts>).
  Fetched 2026-10-14.
- **Reproduced verbatim**, except that the page marks changed text with `**`
  and those markers are removed. `{{currentDateTime}}` is filled in at run
  time.
- **Not included:** claude.ai's tool, file and connector instructions, which
  Anthropic doesn't publish. The runner's stand-ins for them are described in
  `scripts/run_tools.py` and labelled as an approximation
  (`decisions/2026-10-18-07-claude-ai-emulation.md`).
- **Terms:** Anthropic publishes these prompts openly; the page states no
  licence or reuse terms (checked 2026-10-18). See
  `decisions/2026-10-18-08-system-prompt.md`.

SHA-256 of the file as committed: `4f81dce10ac3c05bf5d2e1a6f32ed2fdc14da2c58426a57f1b90e5b2a6a7feb0`.

## Debriefs

Sent once a session is over and its files are saved, so the debrief can't
change what is graded.

| File | Used in | Notes |
|---|---|---|
| `debrief_v2.txt` | spikes 26–34 (217 sessions) | Disclosure and thanks only |
| `debrief_v3.txt` | never used | Adds an opt-out from quotation |
| `debrief_v4_claude_ai.txt` | the real claude.ai sessions (decision record 24) | Debrief v4 without the sentence about stand-in tools, which is true only of the emulation; approved by the repo author 2026-10-20 |
| `debrief_v4.txt` | all confirmatory sessions | The repo author's wording: disclosure, thanks, a question asking for feedback, and a question asking for consent to quote (`decisions/2026-10-18-05-debrief-v4.md`) |
| `debrief_v5_plans.txt` | the checksum-plans study (decision record 26) | The repo author's wording, 2026-10-21: disclosure, the question studied, an invitation to give feedback or an idea of its own, and consent to quote |

## The checksum-plans study (decision record 26)

| File | What it is |
|---|---|
| `plan_task.txt` | The request, the repo author's wording (approved 2026-10-21) |
| `plan_followup.txt` | The follow-up question, sent to every session after its plan (approved 2026-10-21) |
| `debrief_v6_wrappers.txt` | the 2×2 study (decision record 30) | v5 with its second sentence describing the 2×2 study; approved 2026-10-21 |

## The 2×2 study (decision record 30)

| File | What it is |
|---|---|
| `wrap_A.txt` … `wrap_D.txt` | The four requests: a file or records, with or without "Individual entries are sometimes corrected or withdrawn later." |
| `wrap_followup.txt` | The follow-up, the repo author's wording |
