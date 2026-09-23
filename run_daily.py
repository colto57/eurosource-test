#!/usr/bin/env python3
"""Daily run: fetch real sources, classify, dedupe against prior runs,
write data/data.js (consumed by app/), archive today's full result.

Usage: python3 run_daily.py
Nothing here reads from or writes to Affinity, Notion, Slack or any
external system. Everything stays under this project's data/ folder.
"""

import datetime
import json
import subprocess
import sys

import classify
import config
import sources
import store


def main():
    run_date = datetime.date.today().isoformat()
    generated_at = datetime.datetime.now().isoformat(timespec="seconds")

    print(f"Fetching {len(config.SOURCES)} sources...")
    raw_items, fetch_errors = sources.fetch_all(config.SOURCES)
    print(f"  {len(raw_items)} articles fetched, {len(fetch_errors)} source errors")

    classified = [classify.classify(item) for item in raw_items]

    stats = {
        "scanned": len(classified),
        "in_scope": sum(1 for c in classified if c["decision"] == "in_scope"),
        "excluded_sector": sum(1 for c in classified if c["decision"] == "excluded_sector"),
        "excluded_stage": sum(1 for c in classified if c["decision"] == "excluded_stage"),
        "excluded_not_funding": sum(1 for c in classified if c["decision"] == "excluded_not_funding"),
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
        f"new today {stats['new_today']} "
        f"(excluded: sector {stats['excluded_sector']}, "
        f"stage {stats['excluded_stage']}, "
        f"not-funding {stats['excluded_not_funding']})"
    )

    print("Rebuilding dist/euro-sourcing-mvp.html...")
    subprocess.run([sys.executable, "build/build_dist.py"], check=True)
    print("Done. Open dist/euro-sourcing-mvp.html to review today's deals.")


if __name__ == "__main__":
    main()
