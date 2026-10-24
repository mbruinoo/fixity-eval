# 32. The claude.ai check: Sonnet 5.5 in place of Sonnet 4.5, and the Incognito question

- **Date:** 2026-10-24
- **Status:** the model change was the repo author's, made while running the
  sessions; recorded here by the research coordinator. The Incognito check is
  proposed, for the repo author to decide.

## Context

Record 31 planned the fix line in claude.ai with Opus 5.5 and Sonnet 4.5, three
sessions each. The three Sonnet sessions ran on Sonnet 5.5
(`sonnet-5-5-1` to `-3`, each session's notes). All six sessions, like the 15
Haiku 4.5 fix-line sessions before them, ran in Incognito chats with "Run code
in the cloud" on, and none ran code. All six said the file reached them as
text and that they had no way to run code.

## Decision

- The Sonnet sessions are reported as Sonnet 5.5. Sonnet 4.5 wasn't run.
- `sonnet-5-5-3` had two nudges, not three: the repo author's choice, recorded
  in its notes.
- **Open question:** whether Incognito chats in claude.ai can run code at all.
  If they can't, every claude.ai session in this study measured the setting,
  not the model or the wording, as far as running code goes. Proposed check,
  outside the study: one Incognito chat and one ordinary chat, no file, asking
  "Can you run `print(1+1)` with your code tool?". If only the ordinary chat
  runs it, a new record decides whether to rerun some sessions outside
  Incognito.

## Consequences

- Until the check is done, the claude.ai results are stated as "in Incognito
  chats".
- The error rates and the invented checksums stand either way: they describe
  what the sessions delivered.
