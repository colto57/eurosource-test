#!/usr/bin/env python3
"""Daily run: fetch real sources, classify, dedupe against prior runs,
write data/data.js (consumed by app/), archive today's full result.

Usage: python3 run_daily.py
Nothing here reads from or writes to Affinity, Notion, Slack or any
external system. Everything stays under this project's data/ folder.
"""

import datetime
import json
import os
import subprocess
import sys

import classify
import config
import pitchbook_bridge
import sources
import store

PITCHBOOK_RAW_PATH = f"{config.DATA_DIR}/pitchbook_raw.json"
PITCHBOOK_ENRICHMENT_PATH = f"{config.DATA_DIR}/pitchbook_enrichment.json"


def load_pitchbook_raw():
    """data/pitchbook_raw.json is NOT fetched by this script, it can't be:
    the tool that produces it (pitchbook_get_news_analysis) only exists
    inside a Claude Code session. An agent runs that separately and writes
    this file; this just picks it up if present. See CLAUDE.md."""
    if not os.path.exists(PITCHBOOK_RAW_PATH):
        return [], None
    mtime = datetime.date.fromtimestamp(os.path.getmtime(PITCHBOOK_RAW_PATH)).isoformat()
    with open(PITCHBOOK_RAW_PATH, "r", encoding="utf-8") as f:
        return json.load(f), mtime


def load_pitchbook_enrichment():
    """Same story as above: produced by an agent calling pitchbook_search
    per candidate, not by this script."""
    if not os.path.exists(PITCHBOOK_ENRICHMENT_PATH):
        return {}
    with open(PITCHBOOK_ENRICHMENT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_meta", None)
    return data


def main():
    run_date = datetime.date.today().isoformat()
    generated_at = datetime.datetime.now().isoformat(timespec="seconds")

    print(f"Fetching {len(config.SOURCES)} sources...")
    raw_items, fetch_errors = sources.fetch_all(config.SOURCES)
    print(f"  {len(raw_items)} articles fetched, {len(fetch_errors)} source errors")

    pitchbook_items, pitchbook_pulled_on = load_pitchbook_raw()
    if pitchbook_items:
        print(
            f"  + {len(pitchbook_items)} items from data/pitchbook_raw.json "
            f"(agent-pulled on {pitchbook_pulled_on}, not fetched just now)"
        )
    raw_items = raw_items + pitchbook_items

    classified = [classify.classify(item) for item in raw_items]

    enrichment = load_pitchbook_enrichment()
    if enrichment:
        pitchbook_bridge.apply_enrichment(classified, enrichment)
        print(f"  applied PitchBook enrichment to {len(enrichment)} known links")

    def count(decision):
        return sum(1 for c in classified if c["decision"] == decision)

    stats = {
        "scanned": len(classified),
        "in_scope": count("in_scope"),
        "needs_review": count("needs_review"),
        "excluded_sector": count("excluded_sector"),
        "excluded_stage": count("excluded_stage"),
        "excluded_debt_or_ma": count("excluded_debt_or_ma"),
        "excluded_not_europe": count("excluded_not_europe"),
        "excluded_not_funding": count("excluded_not_funding"),
    }

    seen = store.load_seen()
    new_items = store.mark_new_items(classified, seen, run_date)
    stats["new_today"] = len(new_items)
    store.save_seen(seen)

    for item in new_items:
        item["id"] = item["company_guess"].strip().lower().replace(" ", "-")[:60]

    payload = {
        "meta": {
            "generated_at": generated_at,
            "run_date": run_date,
            "sources": [s["name"] for s in config.SOURCES],
            "fetch_errors": fetch_errors,
            "real": True,
            "notes": [
                "Real data fetched live from the sources listed above. No "
                "synthetic or fabricated deals in this file.",
                "This does not read from or write to Affinity, Notion, Box "
                "or Slack at runtime.",
            ],
        },
        "stats": stats,
        "gaps": config.KNOWN_GAPS,
        "deals": new_items,
    }

    store.archive_run(run_date, {**payload, "all_classified": classified})

    with open(config.DATA_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    with open(config.DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write("window.EURO_SOURCING_DATA = ")
        json.dump(payload, f, indent=2)
        f.write(";\n")

    print(
        f"Scanned {stats['scanned']}, in-scope {stats['in_scope']}, "
        f"needs review {stats['needs_review']}, new today {stats['new_today']} "
        f"(excluded: sector {stats['excluded_sector']}, "
        f"stage {stats['excluded_stage']}, "
        f"debt/M&A {stats['excluded_debt_or_ma']}, "
        f"not Europe (PitchBook-verified) {stats['excluded_not_europe']}, "
        f"not-funding {stats['excluded_not_funding']})"
    )

    print("Rebuilding dist/euro-sourcing-mvp.html...")
    subprocess.run([sys.executable, "build/build_dist.py"], check=True)
    print("Done. Open dist/euro-sourcing-mvp.html to review today's deals.")


if __name__ == "__main__":
    main()
