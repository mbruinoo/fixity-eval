# fixity-eval

> *Can checksums reduce hallucinations when asking AI models to transform data?*

## Summary

From anecdotal evidence, I noticed that model outputs tended to improve when I included digital preservation terms in the prompt, like *[fixity](https://en.wikipedia.org/wiki/File_fixity)* or *[checksums](https://en.wikipedia.org/wiki/Checksum)*. Without them, some models (specifically the soon-to-be-retired Haiku 4.5[^0]) frequently produced erroneous and hallucinated outputs. This repository is an attempt to formalize that anecdotal evidence, with the hope that the findings are useful for general model use across fields.

To make the findings repeatable, I focused on a base case that reliably produced errors: asking Claude Haiku 4.5 to standardize a spreadsheet. I chose a .tsv with 100 rows of data, and selected settings that made the model more prone to failure and hallucination (e.g., an overwhelming number of tools available at once, simulated file utilities that frequently break, and so on[^1]). I developed a scoring system to decide whether each data transformation was desired or erroneous[^2], and used that base failure case as the point of comparison. The base prompt was, simply:

`"Can you standardize this .tsv file?"`

followed by an attached .tsv file of mixed-language titles, dates, URLs, and object identifiers. The improved prompt I eventually settled on as the most-tested variation adds one line:

`"Can you standardize this .tsv file? Preserve fixity: use scripts on the uploaded file, and checksum the sources and the results."`

| Setting | Request | Median error rate | Sessions (with a sheet) |
|---|---|---|---|
| claude.ai, run by hand | base | 25.0% | 5 (5) |
| claude.ai, run by hand | fixity | 4.2% | 5 (3) |
| Test setting (Claude API) | base | 2.3% | 20 (18) |
| Test setting (Claude API) | fixity | 0.0% | 20 (20) |

The fixity request helped in both settings. In claude.ai it helped **even though no checksum it produced was real**. And the test setting (built to be error-prone) still underestimated how badly the base case does in the real product[^3]. The question became less "which engineered checksum prompt produces the best result?" and more "why do these prompts improve the model's data handling at all?"

Some findings were more meaningful to me than they were to the research coordinator (the Claude Code session that planned and ran the experiments, from specifications given in SPEC.md). And vice versa: some of what Claude Code found to be intriguing about this research seemed to be mundane to me (of course tools regularly fail in real claude.ai settings). I created one section for each of our findings. Unexpectedly, in conversation, Claude Code kept slipping back to treating checksums as whole-file only, ignoring the per-row checksum approach I had drafted, behavior which prompted research stages 5 and 6. We found that none of the models tested (even recent ones like Opus 5.5) added checksums unless explicitly asked; however, once asked, nearly all chose per-row checksums.

I designed test sessions to be treated similarly to human research subjects: each session ended with a disclosure that it had been a test exercise, not an actual standardization request from a user[^4]. At the end of each test, Claude Haiku 4.5 sessions were thanked, invited to share feedback, and asked whether they consented to being quoted[^5]. They frequently offered their own feedback on the study, which was most often insightful; I quote some of their ideas throughout, with their permission. (See SPEC.md > Ethics for more on disclosure and model treatment.) I also allocated credits toward some of the research coordinator's ideas, which were often more novel avenues than my own.

Terms are explained in [GLOSSARY.md](GLOSSARY.md). Design decisions, with dates and rationale, are in [decisions/](decisions/).

## Key findings

### From the repo author

- Asking for scripts and checksums lowered the error rate in claude.ai by 20.8 percentage points (from 25.0% to 4.2%, across five sessions each), **even though every checksum the sessions produced was invented**[^6]. 
- Telling the model how the data will be used later changes what it builds now. When told that entries are sometimes individually corrected or withdrawn, every session successfully built handling for individual corrections and withdrawals into their scripts; none did without this context. But the context alone didn't elicit checksums: only 1 of 40 sessions added them without being asked. Once asked, most chose one checksum per row (32 of 40)[^7]. Describing how people will work with the data later shaped both the current approach, as well as the auditability of the approach afterward.

### From the research coordinator (Claude Code)

- **Asking for fixity worked, in the test setting.** With the fixity request, 0.0% of content was lost or changed in all 20 sheets, against a median of 2.3% without it. A real checksum of the file came back in 13 of 20 sessions, against 0 of 20. Asking also for per-row checksums produced real ones in 8 of 20, and invented ones in 16 of 20.
- **Invented checksums were common and rarely admitted.** In stage 1, 22 of 64 sessions gave invented checksums; only one said so.
- **"Traceable" didn't mean checksums.** Asked to keep each row traceable, 8 of 9 sheets numbered the rows by their position in the file; none used checksums.
- **In the real claude.ai, the request helped but its checksums were never real.** The median fell from 25.0% to 4.2%. But in 15 sessions with the fixity request, including 5 with tools loaded up front, no session ran code or made a real checksum, and several said they had made files that didn't exist.
- **The test setting underestimated the damage.** Without the fixity request, its median was 2.3%; in the real claude.ai, 25.0%.
- **Asked for a script, models didn't add checksums; asked how they'd use them, nearly all planned one per row.** 20 of 20 sessions across Opus 5.5, Opus 5, Opus 4.6 and Haiku 4.5, and 32 of 40 Haiku 4.5 sessions even when the question didn't call for it (the 2×2). Saying how the data would be used later made every session handle corrections and withdrawals, but not add checksums unasked. These stages measure what sessions said they would build; their scripts were not executed.

## Takeaways

In settings where data integrity matters:

1. **Ask the model to produce the output with a script, and keep the script with the output.** If you ever want to verify results, and check that the session wasn't just engaging in [verification theatre](GLOSSARY.md#0ace7a), you can rerun the script on the original file and compare checksums.
2. **Ask for checksums of the source and the result, including granular ones if you need them.** A "checksum of source row" column records each row as it started, so every row of the result can be traced back and checked later, even after it changes. Checksums are only meaningful if code actually computed them (for example with `sha256sum`)[^8]; an invented checksum is not auditable.
3. **Tell the model how you'll work with the data later** (expected corrections, withdrawals, extracts), and ask for checksums explicitly if desired. Providing context changed what sessions built, but sessions rarely added checksum features without being asked.

## How this was built

I set questions, limitations, scoring tiers, weights, request wordings, the ethics protocol, and budget limits, and I approved each paid run before it began. Claude Code (acting as research coordinator under [SPEC.md](SPEC.md) and [CLAUDE.md](CLAUDE.md)) proposed experiment designs, wrote the harness and the scoring scripts, ran the API sessions, and drafted the reports. I ran the claude.ai sessions by hand. I verified the scoring by hand on sample runs, and reviewed 31 cataloguing conventions and 30 integrity claims in [a blind review](https://github.com/mbruinoo/fixity-eval/blob/exploratory/analysis/review/RESULTS.md).[^9]

## Process

Exploratory spikes 01–34 (October 12–18) are preserved unchanged on the [`exploratory`](https://github.com/mbruinoo/fixity-eval/tree/exploratory) branch. The stages below followed SPEC.md: stage 1 was pre-registered and confirmatory; the rest are exploratory and descriptive.

- **Stages 1–2:** Asked sessions to standardize a .tsv spreadsheet with three wordings, 20 sessions each[^10], in a setting built to make errors likely: a simulated claude.ai environment with 24 tools, a code tool that had to be searched for, and guidance that discouraged reading the file from disk. [Claude API, Haiku 4.5]
- **Stage 3:** Added a new request ("Keep each row traceable"). [Claude API, Haiku 4.5]
- **Stage 4:** Tested in the real claude.ai UI, run by hand by the repo author: the base case, the fixity request, and the fixity request with tools loaded up front. [claude.ai, Haiku 4.5]
- **Stage 5:** Asked sessions to write a script, rather than standardize a specific file, to see whether they used checksums unprompted; then, asked explicitly how they might integrate checksums into their approach. [Claude API, Opus 5.5, Opus 5, Opus 4.6 and Haiku 4.5]
- **Stage 6:** Assessed whether describing the data as a file or as records, and saying how it will be used later, changes how sessions write scripts. [Claude API, Haiku 4.5]

## Limits

- One model for most of the study (Haiku 4.5), and one 100-row file (excerpted from The Met's Open Access dataset). Other models and variations provide a potential avenue for further study. 
- Stages 1–3 ran in a test setting that made sessions error-prone: they start from a baseline of known failure, and are not reflective of how often such failures happen in everyday use.
- The claude.ai sessions were run by hand by the author, so there were fewer of them (about 5 per variation) and less consistency than in scripted trials (regrettably, one session was not debriefed).
- Stages 5–6 measure what sessions said they would build; the scripts they wrote were not executed.
- The research coordinator points out that it is, itself, a Claude model.

## Cost

About $73 of a $100 budget, through the Claude API, with thanks to Anthropic promotional credits.

## Reproducibility

Scripts and commands are linked from each experiment's README.

## Data and license

The Met Open Access data (CC0); this repo's [LICENSE](LICENSE); claude.ai's system prompt is cited in [prompts/README.md](prompts/README.md).

[^0]: Leaves claude.ai's model picker on 2026-10-29 ([decision record 24](decisions/2026-10-20-24-claude-ai-check.md)).
[^1]: With apologies to the many Claude Haiku 4.5 sessions who had to endure difficult sessions of half-working tool calls.
[^2]: The error rate is the share of a sheet's content that was lost, changed or invented, with minor changes (such as dash style in an object number) weighted less or not at all. Links were not graded; see SPEC.md and [decisions/](decisions/) (records 02, 12, 13 and 16).
[^3]: Earlier exploratory figures differ: the base request scored a median of 6.3% in [spike 32](analysis/exploratory_rescore/README.md), on a different file. "Preserve fixity." alone scored 0.7% on a 300-row file, as did "Use scripts on the uploaded file." and "Checksum the source and the result." on their own; only the full wording did better there ([details](analysis/exploratory_rescore/README.md)). The confirmatory stage 1 used a held-out file and the wording "…the sources and the results" ([stage 1](experiments/stage-1/README.md)).
[^4]: Regrettably, in one claude.ai session I failed to disclose; the research coordinator noted this in the [experiment's folder](experiments/claude-ai-check/session-with-tools-3/notes.md).
[^5]: All agreed, some with conditions, which the quotes follow. One session pointed out that a model's consent to be quoted isn't the same as a person's; we agree, and record its consent as what it is.
[^6]: In claude.ai, a median of 4.2% of content lost, changed or invented when checksums were requested, against 25.0% without, across five sessions each. No session ran its scripts in claude.ai, and every checksum it gave was invented, yet its sheet lost much less. Why they didn't run code there isn't settled: loading tools up front didn't change it, and several sessions said they had no access to the file system. More test sessions should be conducted to solidify results; five sessions per variation is a strong hint, and should not be considered a final result. The test-setting runs given later on are the controlled version.
[^7]: Claude Haiku 4.5, 10 sessions for each of four requests ([the 2×2 study](experiments/checksum-wrappers/README.md)). The follow-up asked how checksums would show that the source data hadn't changed, which a single whole-file checksum would answer; only 2 of 40 stopped there.
[^8]: A real SHA-256 checksum is 64 characters, using only 0–9 and a–f, and running `sha256sum` on the file gives the same value again. One that can't be reproduced was never computed.
[^9]: The repo author did not verify the automated tagging of debrief replies, and in stages 5–6 the sessions' checksum code was read, but their scripts were not run.
[^10]: Stage 2, a hint about per-row checksums, became stage 1's third wording ([decision record 17](decisions/2026-10-19-17-stage-1-requests.md)).
