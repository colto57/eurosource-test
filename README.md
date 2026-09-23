# European sourcing scanner, MVP

A local prototype of the idea Tim raised: a daily scan across open sources for
pre-seed and seed deals in Europe, filtered to Motive's core focus areas
(fintech, AI, regtech, digital assets, compute), reviewed with a like/dislike
loop before anything goes near Affinity.

Nothing here reads from or writes to Affinity, Notion, Box or Slack at
runtime. This is deliberately local and disposable so it can be judged on
whether the idea works before any of that gets wired up.

## What is real and what is not

**Real:** the fetch. `run_daily.py` pulls live RSS from three free,
pan-European tech publications (EU-Startups, Tech.eu, Sifted), classifies
every article with keyword matching for sector, funding stage and country,
and shows you only the pre-seed/seed items in the core focus areas that it
has not shown you before. There is no synthetic or fabricated deal data
anywhere in this project. Run it today and you get today's actual news.

**Not connected (real gaps, not oversights):**
- **PitchBook and Crunchbase.** Both need a paid API key/license. Motive
  already has a PitchBook seat, used by the existing weekly
  `mv-deal-digest` skill, but this MVP intentionally doesn't touch that so it
  stays credential-free and local. Wiring PitchBook in would be the single
  biggest coverage improvement, since RSS from three publications is a thin
  slice of everything actually happening.
- **LinkedIn.** Not scraped, on purpose. Automated collection from LinkedIn
  violates its Terms of Service. If LinkedIn signal matters (e.g. "who just
  changed their title to Founder"), the compliant options are LinkedIn's own
  Talent/Sales Navigator exports (manual) or a licensed vendor. Worth
  raising explicitly with Tim rather than quietly building around it.
- **Harmonic**, which Tim mentioned as the vendor already doing this: not
  evaluated here at all. Worth comparing build-vs-buy once this MVP shows
  whether the open-source-only slice is even useful.

The app shows all of this in a "sources not yet connected" panel so the gap
is visible every time you open it, not just in this file.

## Known rough edges

- **Company name extraction is a regex heuristic**, not NLP. It looks for
  `<Capitalized name> raises/secures/closes/...` at the start of a headline.
  It fails on lowercase brand names (real example from today's run: "mika",
  a Berlin AI accounting startup, was reported by both EU-Startups and
  Tech.eu with different headline phrasing, so the two articles were **not**
  deduped and both appear as separate cards). If this goes further, either a
  better name-extraction pass or a fuzzy match on domain/first-few-words is
  worth doing before trusting the "new today" count.
- **Sector and stage detection is substring keyword matching**, checked
  against `config.py`. It will miss anything phrased unusually and will
  false-positive on some borderline cases. It is meant as a fast pre-filter
  a human still reviews, not a final answer. Unlike the existing
  `mv-deal-digest` process (which flags borderline sector calls "yellow for
  Jimmy" instead of silently dropping them), this MVP currently just
  excludes anything that doesn't match, with counts shown, so you can sanity
  check the exclusion rate but not yet inspect what got excluded from inside
  the app. The full classified list, including everything excluded, is
  saved in `data/history/<date>.json` if you want to audit a specific day.
- **The like/dislike loop is a local browser stand-in for Slack**, not
  Slack. Tim already has a working Slack demo; this reuses the same shape
  (see a deal, like or dislike it, only liked ones go forward) without
  needing a Slack app, channel or bot token for this MVP. Decisions live in
  that browser's `localStorage` only, keyed `euro_sourcing_decisions`, and
  are lost if you clear browser storage or open the file in a different
  browser.
- **"Export liked deals" produces a JSON file, it does not touch Affinity.**
  The intent is: you review, you export, a person decides whether and how
  to get liked deals into the pipeline (by hand, or later through the same
  pattern the `mv-deal-digest` skill already uses: search Affinity by
  domain, create the company if missing, add to the pipeline list, set
  Taxonomy/Series/Owner fields, add a funding note). None of that is
  automated here.

## How to run it

```bash
python3 run_daily.py
```

This fetches the sources, classifies every article, skips anything you've
already seen (tracked in `data/seen.json`), archives the full result
(including everything excluded) to `data/history/<date>.json`, writes
`data/data.js`, and rebuilds `dist/euro-sourcing-mvp.html`.

Then open `dist/euro-sourcing-mvp.html` in a browser. That single file is
fully self-contained (no CDN, no server) and safe to share.

Run the tests any time you change `classify.py`:

```bash
python3 tests/test_classify.py
```

To run it daily without opening a terminal yourself, this would need a
`cron` entry or a scheduled task; not set up here since that's a real
standing change to your machine, not something to do without asking first.

## Layout

```
config.py             sector/stage/geography keyword lists, source list, known gaps
sources.py             stdlib-only RSS fetcher (urllib + xml.etree, no deps)
classify.py             keyword classification: sector, stage, country, company-name guess
store.py                 local JSON dedupe store + daily history archive
run_daily.py             orchestrates fetch -> classify -> dedupe -> write data.js -> rebuild dist
data/seen.json           dedupe store, grows every run
data/history/<date>.json  full archive of every run, including excluded items, for audit
data/data.js             latest run's output, window.EURO_SOURCING_DATA, loaded by app/
app/index.html, styles.css, app.js   the review UI: like/dislike, sector filter, export
build/build_dist.py       inlines app/ + data/data.js into dist/euro-sourcing-mvp.html
dist/euro-sourcing-mvp.html   single shareable file
tests/test_classify.py    plain-assert tests on the classifier
```

## If this is worth taking further

In roughly the order that would matter most:
1. Get a read on whether PitchBook's API (or an export Jimmy already pulls)
   can be added as a fourth source, since three RSS feeds is a real but
   thin slice of actual European pre-seed/seed activity.
2. Decide, with Tim, on the LinkedIn question explicitly rather than
   leaving it unimplemented by default.
3. Fix the company-name/dedupe heuristic before trusting "new today" counts
   at scale.
4. If the local like/dislike loop proves useful, decide whether to point it
   at Tim's existing Slack app instead of rebuilding Slack, then design the
   liked-deal-to-Affinity step deliberately (reusing the create-company /
   add-to-pipeline / set-fields / add-note pattern already working in the
   `mv-deal-digest` skill) rather than bolting on a live write here.
5. Compare against just using Harmonic, since Tim already named it as an
   option and buy-vs-build hasn't been evaluated at all yet.
