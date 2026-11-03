# The walkthrough

A scroll story of the main result, published as a private Claude artifact
(shared from its own Share menu): https://claude.ai/artifact/Jf1Q68P2xaGNRNqHtzDpMb

- `fixity_sessions.csv` (one row per session) and `fixity_changes.csv`
  (every counted change in those sessions' sheets, for the hover and
  click-through), made by
  `python scripts/make_walkthrough_data.py analysis/walkthrough/fixity_sessions.csv analysis/walkthrough/fixity_changes.csv`
  from the reviewed scores and changes of stage 1 and the claude.ai check.
  `made_up` marks changes the original doesn't support (the red rings); the
  rule is in the script. It is a screen for the page, checked by hand, not a
  scored measure.
- `fixity_sheets.csv`: every scored sheet, cell for cell, lined up row by row
  with the original, for the side-by-side view, made by
  `python scripts/make_walkthrough_sheets.py analysis/walkthrough/fixity_sessions.csv analysis/walkthrough/fixity_sheets.csv`.
  Rows are lined up for display only; scoring doesn't use this file.
- `page.html`: a copy of the page as published (it runs inside the artifact's
  dashboard, which supplies `dash` and `d3`).
- `first-slide.html`: the first slide on its own, as one file to open in any
  browser and edit in any text editor: its words are plain HTML, its numbers
  fill from the data written into the bottom of the file.
- `docs/` (at the top of the repository): the same page as a standalone website for GitHub
  Pages, built by `python scripts/build_pages.py` from `page.html` and the three data files.
  It supplies what the claude.ai dashboard otherwise provides (its data API, d3, colours, light
  and dark). Rebuild it after any change to the page or the data.
