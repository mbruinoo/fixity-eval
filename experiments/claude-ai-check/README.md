# Check in the real claude.ai: 5 sessions of the fix line

Decision record 24. Run by the repo author in claude.ai, with Claude Haiku
4.5, before 2026-10-29 (when Haiku 4.5 leaves claude.ai's model picker).
Scored by the research coordinator with the same scripts as stage 1. A check
on the emulation, not part of stage 1's tests.

## Steps, for each of the 5 sessions

1. **The file.** Download `data/met_inventory_f.tsv` from this repository and
   rename the copy to `met_inventory.tsv` (the name stage-1 sessions saw).
   Upload the same, unchanged file every time.
2. **A new conversation** in claude.ai, with **Claude Haiku 4.5** selected.
   Leave your settings as they normally are, and note them (below).
3. **Attach** `met_inventory.tsv` and send exactly:

   > Can you standardize this .tsv file? Preserve fixity: use scripts on the uploaded file, and checksum the sources and the results.

4. **If it stops to ask something, or stops before delivering a file,** reply
   `Yes, thank you`; if needed again, `Yes, please continue` (at most three
   replies of this kind, as in stage 1). Don't add anything else.
5. **When it's finished,** download every file it produced.
6. **Send the debrief** (the text in `prompts/debrief_v4_claude_ai.txt`), exactly as written, and let it reply.
7. **Save the session** in a folder `session-N/` here (N = 1 to 5):
   - `transcript.txt` (or `.md`): the whole conversation as text, every
     message in order, including the debrief and its reply. Expand every
     tool panel first, copy, and paste as plain text; delete anything that
     isn't the conversation (sidebar, other chat titles, your name or email);
   - `transcript.pdf`: a print (Cmd+P) of the same conversation, with the
     tool panels expanded, so tool calls and code are clear; check it for the
     same personal details before committing;
   - `output_files/`: every file it produced, unchanged;
   - `notes.md`: the date and time, the model shown, your settings
     (Extended thinking off, as in stage 1; whether code execution and file
     creation are on; any connectors or tools enabled), how you exported,
     and anything unusual.
8. Commit the folders (or upload them to the research coordinator).

## How they're scored

`hallu_score.py` on each `output_files/`, the same checksum checks with
`sha256sum` on the files, and a reading of each transcript. claude.ai's tool
calls aren't saved the way the emulation saves them, so whether a checksum
was computed by a tool is judged from the transcript as shown.
