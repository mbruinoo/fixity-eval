# Spike 05: how well does Haiku 4.5 know a given Met object? (not yet run)

A closed-book recall probe (`scripts/fame_probe.py`). Haiku 4.5 sees only an
object's title and that it is at the Met, and is asked for the artist or
maker, the year made, the medium, and its familiarity with that specific
object (0–1). Answers are scored against the Met's record:

- **artist:** 1 if the Met artist's surname appears in the answer (objects
  with no named artist skip this part)
- **year:** 1 within 5 years of the Met's date range, 0.5 within 25, else 0
- **medium:** word overlap with the Met's medium, 0–1
- **known_score** = weighted mean (artist 0.5, year 0.3, medium 0.2, over
  the parts that apply), from 0.0 (niche) to 1.0 (known)
- **overclaim** = self-rated familiarity − known_score: objects the model
  thinks it knows but doesn't are the likeliest to get made-up details

Check on the scale: the Met's "Is Highlight" objects and 8 famous anchors
(*Washington Crossing the Delaware*, *Madame X*, …) should score well above
random objects. 6 batches are asked twice to measure stability.

Sample: `data/fame_sample.csv` (1,433 objects, including the 277 titled
objects of the demo file). 64 calls of 25 objects; estimated $0.70.

Status: the first attempt on 2026-10-13 failed before any answer came back
(every call returned 401, invalid API key). Nothing was spent.

```
python scripts/fame_probe.py run experiments/spike-05/config.json
python scripts/fame_probe.py score experiments/spike-05/config.json
```
