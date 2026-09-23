"""Local JSON dedupe store and daily history archive. No database server,
no network calls, no writes outside this project's data/ folder."""

import json
import os

import config


def _dedupe_key(classified_item):
    """Prefer the verified PitchBook PBID when enrichment has attached
    one: it is exact, unlike the company_guess regex heuristic. Real
    example this fixes: the same "mika" seed round covered by both
    EU-Startups and Tech.eu with different headline wording produced two
    different company_guess strings and was NOT deduped; both resolve to
    the same PitchBook PBID (541194-49) once enriched."""
    pbid = classified_item.get("pitchbook_pbid")
    if pbid:
        return f"pbid:{pbid}"
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


DISPLAYABLE_DECISIONS = {"in_scope", "needs_review"}


def mark_new_items(classified_items, seen, run_date):
    """Mutates `seen` in place. Returns the subset of in_scope/needs_review
    items whose dedupe key has not been recorded before. needs_review items
    are included, not silently dropped, matching the mv-deal-digest rule of
    flagging borderline calls instead of excluding them."""
    new_items = []
    for item in classified_items:
        if item["decision"] not in DISPLAYABLE_DECISIONS:
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
