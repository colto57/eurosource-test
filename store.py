"""Local JSON dedupe store and daily history archive. No database server,
no network calls, no writes outside this project's data/ folder."""

import json
import os

import config


def _dedupe_key(classified_item):
    return classified_item["company_guess"].strip().lower()


def load_seen():
    if not os.path.exists(config.SEEN_STORE_PATH):
        return {}
    with open(config.SEEN_STORE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_seen(seen):
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(config.SEEN_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(seen, f, indent=2, sort_keys=True)


def mark_new_items(classified_items, seen, run_date):
    """Mutates `seen` in place. Returns the subset of in-scope items whose
    dedupe key has not been recorded before."""
    new_items = []
    for item in classified_items:
        if item["decision"] != "in_scope":
            continue
        key = _dedupe_key(item)
        if key in seen:
            continue
        seen[key] = {"first_seen": run_date, "link": item["link"]}
        new_items.append(item)
    return new_items


def archive_run(run_date, payload):
    os.makedirs(config.HISTORY_DIR, exist_ok=True)
    path = f"{config.HISTORY_DIR}/{run_date}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return path
