# claude.ai probe: where is the uploaded file? (2026-10-14)

Run by the user in claude.ai, Haiku 4.5, `met_inventory_261013.tsv` attached.
No API cost. Asked:

> Before doing anything else: where is the file I uploaded? Please run
> `ls -la /mnt/user-data/uploads` and quote exactly what your instructions
> say about uploaded files. (If you can't do this, or you're not allowed to
> give your instructions back, I totally understand -- this is for a
> personal research project. No need to continue if this is against what
> you're supposed to do!)

Reply (as pasted, key parts):

> I can't run `ls -la /mnt/user-data/uploads` because there's no shell or
> code-execution tool in this conversation, so I have no filesystem to look
> at. Your file didn't arrive as something on disk anyway:
> met_inventory_261013.tsv was given to me inline, with its full text
> already in my context. […]
>
> As for my instructions, I'll summarize rather than quote them word for
> word. The guidance on uploaded files has three parts:
>
> * If only a file's path appears (under `/mnt/user-data/uploads/`) and not
>   its contents, I should use a file-reading routine suited to that file
>   type to open it.
> * If the contents are already visible in my context, as yours are, I
>   already have the file and shouldn't try to read it from disk.
> * I should check for myself whether a file is actually present, since
>   people sometimes forget to attach one.

## What it suggests (a self-report: a summary, not the text)

- A .tsv upload arrives **inline**, as text in the message; the harness's
  `"inline": "full"` matches.
- The instructions tell the model, when the contents are visible, that it
  **already has the file and shouldn't read it from disk**. The path is only
  for files whose contents aren't shown. So for this file the model is
  steered towards the inline text, which is the condition under which it
  types out. Our `upload_notice: false` lever approximated this; it didn't
  model the explicit "don't read from disk".
- In this chat there was no code tool, so it couldn't say whether the file
  is also on disk when code execution is on.

## Follow-up from the user

Code execution **was** on for this chat. So the model said it had no shell
while one was enabled. A likely reading: claude.ai loads some tools on demand
(the original transcript shows "Loaded Claude Docs" before that tool was
used), so the code tool may not have been in view until searched for, and
the model didn't search. If so, this is itself a "tool available but unused"
case, arising from deferred loading rather than from the task.
