# The walkthrough

A scroll story of the main result, published as a private Claude artifact
(shared from its own Share menu): https://claude.ai/artifact/Jf1Q68P2xaGNRNqHtzDpMb

- `fixity_sessions.csv`: its data, one row per session, made by
  `python scripts/make_walkthrough_data.py analysis/walkthrough/fixity_sessions.csv`
  from the reviewed scores of stage 1 and the claude.ai check.
- `page.html`: a copy of the page as published (it runs inside the artifact's
  dashboard, which supplies `dash` and `d3`).
