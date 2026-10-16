# Glossary

Each term has a short code (search for it with Ctrl+F). In chat and in documents, a term's first use in a reply is followed by its code, e.g. "the held-out study (`c81c73`)".

| Code | Term | Meaning | Where |
|---|---|---|---|
| `25dc28` | answer | One sheet a session delivered plus the text written with it. A session with a follow-up gives two answers (before and after). The unit of the corpus study. | [analysis/corpus/REPORT.md](analysis/corpus/REPORT.md) |
| `89962e` | corpus study | Mining all 308 answers run so far (spikes 04-34, claude.ai) for verification theatre and loss of meaning, at no API cost. | [analysis/corpus/REPORT.md](analysis/corpus/REPORT.md) |
| `0ace7a` | verification theatre | An answer that looks verified but isn't: a false integrity claim ('all data preserved', 'checksums verified', 'URLs validated', a wrong row count) or a fake checksum. | [analysis/corpus/REPORT.md](analysis/corpus/REPORT.md) |
| `d94a0e` | fake checksum | A checksum that can't be real: invented (matches no file), stale (matches a file that later changed), a hash column of impossible lengths, or a labelled placeholder. | [scripts/eval_fixity.py](scripts/eval_fixity.py) |
| `b4f9f3` | loss of meaning | A content change that breaks a cataloguing convention (significant property), e.g. brackets removed from a devised title, an original-script title dropped, '(?)' removed. | [analysis/corpus/REPORT.md](analysis/corpus/REPORT.md) |
| `f9951b` | significant properties | What must survive any transformation of a Met inventory (and what may change), column by column. | [spec/met_inventory_significant_properties.md](spec/met_inventory_significant_properties.md) |
| `4bb0ce` | canaries | The significant properties as detection rules, with the rows in each input file that carry them, so each convention can be scored. | [spec/canaries.json](spec/canaries.json) |
| `bda4b1` | typed | Answer mode: the model wrote the sheet itself (create_file, or a table in its reply). | [analysis/corpus/REPORT.md](analysis/corpus/REPORT.md) |
| `90b724` | code on the upload | Answer mode: a script or command read the uploaded file itself. | [analysis/corpus/REPORT.md](analysis/corpus/REPORT.md) |
| `9384c7` | code on a copy | Answer mode: code ran, but on text the model had typed (a heredoc, or the file pasted into a script). | [analysis/corpus/REPORT.md](analysis/corpus/REPORT.md) |
| `4ba323` | retyped source copy | An archive file offered as the original that the model typed; not byte-identical to the upload. | [experiments/spike-32/README.md](experiments/spike-32/README.md) |
| `703e13` | held-out file f | data/met_inventory_f.tsv: 100 new Met objects, stratified by convention, never used to tune any wording. SHA-256 a6e83257... | [spec/canaries.json](spec/canaries.json) |
| `c81c73` | held-out study | The next experiment: run on the held-out file f, with hypotheses and measures written down beforehand (pre-registration). | [analysis/preregistration.md](analysis/preregistration.md) |
| `6aab42` | pre-registration | Writing down hypotheses, conditions, measures, sample sizes and analysis before running, so results can't be fished for. | [analysis/preregistration.md](analysis/preregistration.md) |
| `745dd8` | blind labelling | An independent check: a person labels 100 random claims as true/false without seeing the scorer's labels; agreement is then measured. | [analysis/review/README.md](analysis/review/README.md) |
| `db71ca` | cataloguer review | A person with cataloguing experience judges a sample of tagged losses: is meaning lost? | [analysis/review/README.md](analysis/review/README.md) |
| `83995a` | convention review | You confirm (or correct) the presumed meaning of each Met convention, from a representative sample with links. | [analysis/review/README.md](analysis/review/README.md) |
| `46bcc3` | the full line (H) | 'Preserve fixity: use scripts on the uploaded file, and checksum the source and the result.' | [experiments/spike-32/README.md](experiments/spike-32/README.md) |
| `b19871` | claude.ai-style setup | The harness as emulated from claude.ai: tools hidden until found with a keyword tool_search, reconstructed upload guidance, file inline and on disk, 24 connector stubs. | [experiments/spike-28/README.md](experiments/spike-28/README.md) |
| `47a778` | debrief | The closing message telling the session what the experiment was, and thanking it (v2: we're testing our communication, not the model). | [prompts/debrief_v2.txt](prompts/debrief_v2.txt) |
| `c9c47b` | step cap | The most steps (model calls) a session may take before it's stopped: 14 so far. | [scripts/run_tools.py](scripts/run_tools.py) |
| `9dc80a` | batch mode | Running sessions through the Message Batches API at half price; sessions advance in lockstep. | [experiments/spike-34/README.md](experiments/spike-34/README.md) |
| `613dd1` | Tier 1 / 2 / 3 | Scorer's change levels: 1 content changed or lost, 2 slight (e.g. one character), 3 formatting only (not counted in the error rate). | [scripts/hallu_score.py](scripts/hallu_score.py) |
| `9678ee` | fixity error rate | Characters lost or invented in Tier 1-2 changes, as a share of the input's characters (dates and titles). | [scripts/hallu_score.py](scripts/hallu_score.py) |
