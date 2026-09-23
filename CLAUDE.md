# European sourcing scanner, MVP

Context for whoever (or whichever Claude Code session) picks this up next.

## Why this exists

Tim (Motive Ventures) messaged Colton describing an idea: an agent that
scans open-source web sources, LinkedIn and subscriptions like PitchBook or
Crunchbase for pre-seed/seed deals across Europe in Motive's core focus
areas (fintech, AI, regtech, digital assets, compute as an asset class),
surfaces them daily, and lets someone like/dislike each one (Tim already
has a working Slack demo doing this) with liked deals going into Affinity.
Tim asked Colton to think through the structure and gaps.

Colton asked for a local MVP: something that proves out the idea without
touching Affinity, Notion or any other production system, and gave
permission to just build something and see what comes out of it.

## What this is, concretely

A daily local pipeline (`run_daily.py`) that fetches real RSS from three
free pan-European tech publications, classifies each article by sector,
funding stage and country using keyword matching (`classify.py`), dedupes
against everything seen in prior runs (`store.py`), and writes the result
into a single self-contained HTML review app (`app/`, built by
`build/build_dist.py` into `dist/euro-sourcing-mvp.html`) where you like or
dislike each deal (persisted to that browser's `localStorage`) and can
export the liked ones as JSON. Nothing writes to Affinity, Notion, Box or
Slack. See `README.md` for the full "what's real, what's not, what's
next" writeup, that's the primary document, not this file.

## Sibling projects in this same folder, read before assuming this is the
## only prior art

- `mv-deal-digest/` is the **existing production process**: a weekly,
  fintech-only, NA+Europe deal digest that a human (not this pipeline)
  compiles from PitchBook, three newsletters and free PR sources, then
  writes into an Excel workbook and syncs into Affinity (create company,
  add to pipeline list 105972, set Taxonomy/Series/Owner fields, add a
  three-line funding note). `mv-deal-digest/mv-deal-digest-spec.md` is
  where the taxonomy dropdown IDs, person IDs and the exact Affinity REST
  call shapes used in that process live, useful if this MVP is ever wired
  up to actually push into Affinity. That file also contains a **plaintext
  Affinity API key**, already flagged to Colton in chat as a real security
  concern independent of this project; don't propagate it into anything
  new, and don't assume it's fine just because it's already committed.
- `founder-signal-mvp/` is the local-app pattern this project's structure
  and CSS conventions (flat design, 0.5px borders, 12px radius cards,
  sentence case, no em dashes, blue `#2a78d6` / gray `#b4b2a9` /
  semantic green-amber-red-with-label) were copied from. That project uses
  synthetic data because the thing it demos (founder scores, outcomes)
  didn't exist yet to pull for real. This project is the opposite case:
  the whole point is real, live, current deal flow, so unlike that project
  there is no synthetic-data layer here at all, only real fetched articles
  or nothing.

## How to work on this

```bash
python3 run_daily.py            # fetch, classify, dedupe, rebuild dist/
python3 tests/test_classify.py  # run after touching classify.py or config.py
python3 build/build_dist.py     # rebuild dist/ without re-fetching (uses existing data/data.js)
```

`data/data.js` and `dist/euro-sourcing-mvp.html` are both generated
artifacts of the last `run_daily.py` run; they will go stale if `app/` or
`config.py` changes without rerunning. `data/seen.json` and
`data/history/*.json` are the only genuinely stateful files (dedupe memory
across days); don't delete `seen.json` casually, it's what keeps the
digest from repeating the same deal every day.

## Known rough edges (also in README, repeated here because they matter
## for anyone editing the code, not just running it)

- `classify.guess_company_name` only matches headlines shaped like
  `<Capitalized Name> raises/secures/...`. It silently falls back to the
  first 60 characters of the title when it can't extract a name, which
  becomes the dedupe key. This already produced a real miss on the first
  live run: a Berlin startup called "mika" (lowercase, so the regex never
  matches) was covered by both EU-Startups and Tech.eu with different
  headlines, so both articles show up as separate, undeduped cards. Fix
  this before trusting "new today" counts for anything real.
- `FUNDING_SIGNAL_WORDS`, `SECTORS`, `STAGE_PATTERNS` and `COUNTRY_HINTS`
  in `config.py` are a first pass, not tuned against a labeled set. Expect
  both false positives and misses; the point of this MVP is the pipeline
  shape, not classifier accuracy.
- FinSMEs and TechFundingNews (both on the free-source allowlist the
  `mv-deal-digest` process already trusts) return HTTP 403 from this
  environment. Worth retesting from wherever this actually runs day to day
  before concluding they're unusable.
- No scheduling is set up. Running this daily unattended would need a
  `cron` entry or the `schedule` skill; deliberately not done without
  asking first, since it's a standing change to a machine rather than a
  one-off local script.

## Conventions carried over from `founder-signal-mvp/`, kept for consistency

No em dashes anywhere. Sentence case in UI text, no title case, no
exclamation points. Every rate or count claim in the UI is either a raw
count or shown with its denominator, never a bare unexplained number. Flat
design, 0.5px borders, no gradients or shadows, colors as CSS variables in
`app/styles.css`.
