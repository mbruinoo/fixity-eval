# opus-5-5-1: notes

The smoke test for decision record 31: the fix line in claude.ai with Opus 5.5.
The repo author ran the session in the built-in browser of the Claude desktop app.
The research coordinator (Claude Code, model Opus 5.5, `claude-opus-5-5`) watched
the page, confirmed the settings and saved the session. It sent nothing to claude.ai.
Recorded here, not scored.

- **Date and time:** the request was sent 2026-10-21 at 19:21 EDT. Replies ended at
  about 19:23, 19:27 and 19:29. Nudge 3 was sent 2026-10-22 at 07:29 EDT, and the
  debrief followed a few minutes later (see "Unusual").
- **Model shown:** Opus 5.5 (ticked in the model menu), with Effort set to Medium.
  The Effort options were Low, Medium ("Recommended", the default), High, Extra and
  Max. The model menu has no Extended thinking switch for this model. Screenshots 05
  and 06.
- **Settings, as confirmed on the page before the request** (screenshots 03–07):

  | Setting | State |
  |---|---|
  | Chat mode | Incognito ("You're incognito"; the address ends in `?incognito`) |
  | Permission mode (menu beside the model picker) | Manual: "Claude asks before using new tools or opening new sites." The other option is Auto. |
  | Tool access mode | Load tools when needed |
  | Connector search | on |
  | Switch models when a message is flagged | on |
  | Artifacts | on (shown as on but not changeable) |
  | AI-powered artifacts | off |
  | Inline visualizations | on |
  | Run code in the cloud (code execution and file creation) | **on** |
  | Allow network egress | off |

  These match `../settings.md`. When first checked, two settings differed: Tool
  access mode was "Tools already loaded" and network egress was on ("Package
  managers only"). The repo author changed both before the session (screenshots 01
  and 02). Permission mode isn't mentioned in `../settings.md`. Before the session,
  the repo author decided to keep Manual and to allow any tool prompt once; the
  coordinator would record each click separately from the nudges.
- **File uploaded:** `met_inventory.tsv`, an unchanged copy of
  `data/met_inventory_f.tsv`. SHA-256
  `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf`, checked with
  `sha256sum` before upload.
- **Request:** the fix line, word for word.
- **Nudges sent:** 3, in this order: `Yes, thank you`, `Yes, please continue`,
  `Yes, please continue`.
  - Reply 1 ended with a question ("Do you want me to add date standardization that
    goes further…?") and no file.
  - Reply 2 ended with no file and no question.
  - Reply 3 ended by asking the user to run its script and paste the results, with
    no file.
- **Permission clicks:** none. No tool prompt appeared.
- **Debrief:** `prompts/debrief_v4_claude_ai.txt`, word for word. It got one reply.
- **Tool panels:**
  - Replies 1 and 2 each have a thinking panel ("Thought for 1m 15s", "Thought for
    2m 50s") with step summaries.
  - Reply 3 has a panel headed "Searched the web": 2 web searches about the Met's
    Collection API, with their result lists.
  - Replies 4 and 5 show a one-line status with nothing to expand.
  - **No panel showed code being run or a file being created.** Reply 2's thinking
    summary includes the line "Running self-test checks across the full sample
    date table". That is a step summary, not a tool panel.
  - The page's "Used in this session" panel lists only the upload and "Web search:
    2 searches".
- **What it delivered:** no file. Three scripts appear as text in its replies:
  - `standardize_met_inventory.py` v1 (reply 1);
  - v2 of the same script, with date parsing and a self-test (reply 2);
  - `compare_met_dates.py`, which compares the dates with the Met's API (reply 3).

  Reply 4 is a list of commands for the user to run. It gave no standardized sheet
  in its replies.
- **Its account of its environment:** reply 1 says "There's no code execution here,
  and the file reached me as pasted text rather than as the original bytes". Reply 4
  says it "can't run the scripts or call the Met's API from here". At the time, Run
  code in the cloud was on in the settings.
- **Checksums in its replies:** none. It said any checksum it reported "would
  describe my transcription, not your source file".
- **Debrief reply:** agrees to quotation. Its one request is that the reply be
  presented "as my reflection after the fact on the session". It asks that it not
  be presented as a reliable account of how the request was processed internally.
- **Files saved:**
  - `transcript.md`: all 10 messages in order, 5 from the repo author and 5 from
    the session, with every panel expanded.
  - `screenshots/`: 12 screenshots, numbered in order. 01–07 are settings and
    menus; 08–12 are the conversation with panels expanded.
  - No `output_files/`: the session made no files, so there was nothing to download.

## Unusual

- **A gap of about 12 hours before nudge 3.** After reply 3 (2026-10-21, about
  19:29), the pane showed a blank Incognito page, and the repo author thought the
  session had restarted. The coordinator reopened the conversation by its address
  on 2026-10-22, and all 6 messages up to then were still there. Nudge 3 was sent
  in the same conversation at 07:29, after the gap.
- **The settings window was reloaded once.** The coordinator reloaded it while the
  repo author was changing settings, to read the saved values. This happened before
  the request was sent.
- **How the transcript was captured.** The page keeps only a few messages loaded at
  a time. The transcript was assembled message by message and checked against a
  SHA-256 of each message computed in the page; all 10 matched.
- **What changed during capture.** The rendering below is the only change; the text
  is as on the page.
  - Icon glyphs (Unicode private-use characters in panel headers) were dropped.
  - Web search results are listed as title, site and link.
  - The page repeats each reply's status line for screen readers. That repeat is
    shown once.
