# Spike 05: how well does Haiku 4.5 know a given Met object?

Run on 2026-10-13. The idea: works a model already knows well should be less
likely to come back with made-up details, so it helps to know which objects
in the Met's catalogue Haiku 4.5 actually knows. This is a closed-book recall
probe that gives each object a 0.0 (niche) to 1.0 (known) score.

## Setup

- **Model:** Haiku 4.5 (`claude-haiku-4-5`), no thinking, Messages API.
- **What it sees:** only titles, 25 per message, introduced as objects in the
  Met's collection. No artist, date, department or object number.
- **What it's asked**, per object: artist or maker (or "unknown"), year made,
  medium, and familiarity with that specific object (0–1), as JSON.
- **Sample** (`data/fame_sample.csv`, 1,433 objects): the 277 titled objects
  of the demo file `met_random_300.tsv`; 8 famous anchors (*Washington
  Crossing the Delaware*, *Madame X*, …); 348 of the Met's "highlights"; 400
  random objects with a named artist; 400 random objects.
- **Runs:** 58 batches, plus 6 batches asked twice to check stability.
  64 calls, **$0.45**. The study has now spent $2.40 of $8.

```
python scripts/fame_probe.py sample MetObjects.csv
python scripts/fame_probe.py run experiments/spike-05/config.json
python scripts/fame_probe.py score experiments/spike-05/config.json
```

## The score

Answers are checked against the Met's own record. `known_score` is
**verified recall** where it can be checked:

- **artist (0.6):** the Met artist's surname appears in the answer. Skipped
  when the object has no named artist, or when the title already names them
  (`Chinese Chairs, in Chippendale Drawings`).
- **year (0.4):** within 2 years of the Met's dates (half credit within 10).
  Only scored when the Met dates the object within 10 years; a wide date like
  "19th century" can be hit by any generic guess.
- With no artist part, a year alone earns at most 0.5, so a lucky guess
  (`Snuff spoon` → 1750, Met 1745–55) can't make an object "known".
- Where neither part applies (anonymous and broadly dated, 21% of objects),
  `known_score` falls back to the model's own familiarity rating, marked
  `self-report only` in `score_basis`.

The medium is recorded but not scored: titles like "Terracotta kylix" give it
away. An earlier version that scored medium and any in-range year couldn't
tell highlights from random objects at all; see "How the score was chosen".

`overclaim` = familiarity − verified recall: the model says it knows the
object but gets it wrong.

## Results

| Group | n | Mean known_score | known_score ≥ 0.5 | Mean familiarity |
|---|---|---|---|---|
| Famous anchors | 8 | 0.88 | 7 of 8 | 0.88 |
| Met highlights | 348 | 0.17 | 11% | 0.22 |
| Random, named artist | 400 | 0.15 | 12% | 0.14 |
| Random | 400 | 0.12 | 5% | 0.12 |
| Demo file (`met_random_300.tsv`) | 277 | 0.14 | 20 of 277 (7%) | 0.16 |

- **Haiku 4.5 knows very few Met objects.** 909 of 1,433 score 0.1 or less;
  46 score above 0.9. The famous anchors work as they should: 7 of 8 fully
  right.
- **What it knows is mostly series and big names**, not individual objects:
  Goya's *Caprichos*, Piranesi's *Vedute di Roma*, Daumier's *Charivari*
  lithographs, Callot's *Balli di Sfessania*, Cindy Sherman's *Untitled Film
  Stills*, Monet's *Bridge over a Pond of Water Lilies*.
- **The Met's "highlights" are only a little better known** than random
  objects (11% vs 5–12% score ≥ 0.5). Highlights are often famous to
  specialists, not to the internet. The model's familiarity rating separates
  them better (AUC 0.67 against random objects) than verified recall does
  (0.53).
- **16 confident mistakes** (familiarity ≥ 0.5, recall < 0.3), the objects
  most at risk of made-up details. Examples:

  | Title | Met artist | Haiku 4.5 said | Familiarity |
  |---|---|---|---|
  | Self-Portrait with a Straw Hat | Vincent van Gogh | James McNeill Whistler | 0.7 |
  | [Irises] | Morgan Whitney | Vincent van Gogh | 0.8 |
  | Lake George | John Frederick Kensett, 1869 | Georgia O'Keeffe, 1957 | 0.7 |
  | Perseus with the Head of Medusa | Antonio Canova, 1804 | Benvenuto Cellini, 1545 | 0.7 |
  | The Bath | Edgar Degas, 1880 | Jean-Honoré Fragonard, 1770 | 0.6 |
  | Head I | Francis Bacon | Henry Moore | 0.5 |

  The pattern: a generic title that matches a more famous work by someone else.
- **Stability** (150 objects asked twice): same artist 91% of the time;
  familiarity ratings correlate at 0.62; the year is the same only 45% of the
  time (53% within 10 years), so year guesses for unknown objects are noise.

## How the score was chosen

The first scoring (artist 0.5, any in-range year 0.3, medium 0.2) gave
highlights and random objects the same scores (AUC 0.48): random anonymous
objects earned year and medium credit from the title alone. Requiring a
narrow Met date, dropping medium, ignoring artists the title already names and
capping year-only credit at 0.5 removed most of that. All versions use the
same answers; only `score` changed.

## Caveats

- A title in Chinese or Japanese can contain the artist's name
  (`棟方志功筆` = "by Munakata Shikō"); the giveaway check only looks for the
  romanized name.
- Series-level knowledge (knowing who made *Los Caprichos*) counts as known,
  though the model may know nothing about the individual plate.
- One model, one prompt, default temperature; scores near 0 or 1 are more
  reliable than those in between.
- Whether higher-scoring objects really get fewer made-up details is not yet
  tested: spike-04's invented rows came from a part of the file the model never
  saw, regardless of fame.

## Files

- `scores.csv`: every object, with the Met's values, the model's answers, each
  part's score, `known_score`, `score_basis`, `familiarity`, `overclaim`, and
  the second-pass answers where asked.
- `demo_file_scores.tsv`: the 277 titled objects of `met_random_300.tsv`,
  sorted from most to least known.
- `runs/`: request and response for each batch; `cost_ledger.json`; `run_log.txt`.
