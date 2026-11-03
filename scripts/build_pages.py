"""Build the GitHub Pages copy of the walkthrough (docs/) from the page published as a claude.ai artifact.

The artifact's page (analysis/walkthrough/page.html) runs inside a claude.ai dashboard, which supplies the
`dash` data API, d3 and the design tokens. This wraps the same page in a standalone document that supplies
them itself: a small `dash` stand-in that reads the CSVs in docs/data/, d3 from cdnjs, and the tokens in light
and dark. Nothing in the page is changed, so the two stay the same.

Usage:
    python scripts/build_pages.py
writes docs/index.html, docs/data/*.csv and docs/.nojekyll. Run it again after the page or the data change.
"""
import pathlib
import shutil

ROOT = pathlib.Path(__file__).parent.parent
SRC = ROOT / "analysis/walkthrough"
OUT = ROOT / "docs"
DATA = ["sessions", "changes", "sheets"]

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Improving Model Outcomes with Fixity</title>
<link rel="icon" href="data:,">
<meta name="description" content="When asked to use fixity, Claude's median error rate fell from 2.9% to 0.0%. A walkthrough of fixity-eval.">
<style>
  /* The design tokens the claude.ai dashboard supplies, in light and dark. */
  :root {
    color-scheme: light dark;
    --color-fg: #1f1f1c; --color-fg-muted: #6b6a66; --color-bg: #f7f7f5; --cds-page-bg: #f7f7f5; --color-panel: #ffffff;
    --color-border-line: #e3e2de; --cds-border: #e3e2de; --cds-surface-popover: #ffffff;
    --cds-shadow-popover: 0 4px 16px rgb(0 0 0 / .12);
    --cds-chart-status-warning: #d99a1e; --cds-chart-status-critical: #c8322f;
    --font-anthropic-sans: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --cds-font-size-caption: 12px; --cds-font-size-body: 14px; --cds-font-weight-medium: 500;
    --cds-gap-xs: 4px; --cds-gap-sm: 8px; --cds-gap-md: 16px; --cds-gap-xl: 32px;
    --cds-pad-xs: 4px; --cds-pad-sm: 8px; --cds-pad-md: 12px; --cds-pad-lg: 16px;
    --cds-radius: 8px; --cds-dur-slow: 300ms; --cds-ease-out: cubic-bezier(.2, .7, .2, 1);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --color-fg: #ecebe7; --color-fg-muted: #a3a29c; --color-bg: #000000; --cds-page-bg: #000000; --color-panel: #141413;
      --color-border-line: #2e2e2b; --cds-border: #2e2e2b; --cds-surface-popover: #1c1c1a;
      --cds-shadow-popover: 0 4px 16px rgb(0 0 0 / .5);
    }
  }
  html, body { margin: 0; background: var(--cds-page-bg); color: var(--color-fg); font-family: var(--font-anthropic-sans); }
  #dash-root { padding-inline: clamp(16px, 4vw, 48px); }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script>
  // A stand-in for the claude.ai dashboard's `dash` API: the page's data comes from the CSVs in data/.
  (() => {
    const raw = {}, calcs = {}, draws = {}, onData = [];
    let params = { session: null, slot: null }, loaded = false;
    const data = (id) => {
      if (calcs[id]) {
        const ins = calcs[id].inputs.map(data);
        if (ins.some((d) => d.status !== 'ok')) return { status: 'loading', data: [] };
        return { status: 'ok', data: calcs[id].fn(...ins.map((d) => d.data)) };
      }
      return raw[id] ? { status: 'ok', data: raw[id], columns: raw[id].columns } : { status: loaded ? 'missing' : 'loading', data: [] };
    };
    const cache = new Map();
    const memo = (id) => { if (!cache.has(id)) cache.set(id, data(id)); return cache.get(id); };
    const run = () => {
      onData.forEach((f) => f());
      for (const name in draws) document.querySelectorAll(`[data-draw="${name}"]`).forEach((el) => { if (!el.closest('[hidden]')) draws[name](el); });
    };
    window.dash = {
      calc: (id, o) => { calcs[id] = o; },
      draw: (name, fn) => { draws[name] = fn; },
      data: memo,
      onData: (fn) => { onData.push(fn); },
      params: () => params,
      setParams: (p) => { params = { ...params, ...p }; run(); },
      resetParams: () => { params = { session: null, slot: null }; run(); },
      setLink: (id) => { history.replaceState(null, '', '#' + id); },
      colors: ['#3b74d1', '#d9703f'],
    };
    Promise.all(%(files)s.map((f) => fetch('data/fixity_' + f + '.csv').then((r) => r.text()).then((t) => { raw[f] = d3.csvParse(t); })))
      .then(() => { loaded = true; cache.clear(); run(); });
    let last = innerWidth;
    addEventListener('resize', () => { if (innerWidth !== last) { last = innerWidth; run(); } });
    addEventListener('DOMContentLoaded', run);
  })();
</script>
</head>
<body>
<div id="dash-root">
"""

FOOT = """
</div>
</body>
</html>
"""


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "data").mkdir(exist_ok=True)
    for f in DATA:
        shutil.copyfile(SRC / f"fixity_{f}.csv", OUT / "data" / f"fixity_{f}.csv")
    page = (SRC / "page.html").read_text(encoding="utf-8")
    head = HEAD.replace("%(files)s", repr(DATA).replace("'", '"'))
    (OUT / "index.html").write_text(head + page + FOOT, encoding="utf-8")
    (OUT / ".nojekyll").write_text("")  # serve the files as they are, without Jekyll
    print("wrote", OUT / "index.html")


if __name__ == "__main__":
    main()
