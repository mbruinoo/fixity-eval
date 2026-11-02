# The walkthrough

A scroll story of the main result, published as a private Claude artifact
(shared from its own Share menu): https://claude.ai/artifact/Jf1Q68P2xaGNRNqHtzDpMb

- `fixity_sessions.csv` (one row per session) and `fixity_changes.csv`
  (every counted change in those sessions' sheets, for the hover and
  click-through), made by
  `python scripts/make_walkthrough_data.py analysis/walkthrough/fixity_sessions.csv analysis/walkthrough/fixity_changes.csv`
  from the reviewed scores and changes of stage 1 and the claude.ai check.
- `page.html`: a copy of the page as published (it runs inside the artifact's
  dashboard, which supplies `dash` and `d3`).
- `first-slide.html`: the first slide on its own, as one file to open in any
  browser and edit in any text editor: its words are plain HTML, its numbers
  fill from the data written into the bottom of the file.
