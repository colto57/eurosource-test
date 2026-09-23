"""Keyword classification: sector, funding stage, country, company guess.

This is intentionally simple substring matching, not NLP. It is meant to be
a fast, auditable pre-filter that a human reviews in the app, not a fully
automated decision-maker. False positives and misses are expected; see
README "What this does not do".
"""

import re

import config

_COMPANY_PATTERNS = [
    re.compile(
        r"^(?P<name>[A-Z][\w.&\-]*(?:\s+[A-Z][\w.&\-]*){0,3}?)\s+"
        r"(?:raises|secures|closes|lands|nets|bags|scores|has raised|raised)\b",
    ),
]


def guess_company_name(title):
    """Best-effort extraction of the company name from a headline.
    Returns None if no pattern matches (caller should fall back to the
    full title as the dedupe key)."""
    for pattern in _COMPANY_PATTERNS:
        m = pattern.search(title)
        if m:
            return m.group("name").strip()
    return None


def match_sectors(text):
    text_l = text.lower()
    return [
        sector
        for sector, keywords in config.SECTORS.items()
        if any(kw in text_l for kw in keywords)
    ]


def is_funding_announcement(text):
    text_l = text.lower()
    return any(kw in text_l for kw in config.FUNDING_SIGNAL_WORDS)


def detect_stage(text):
    text_l = text.lower()
    for stage, keywords in config.STAGE_PATTERNS:
        if any(kw in text_l for kw in keywords):
            return stage
    return "unclear"


def detect_country(text):
    text_l = text.lower()
    for country, keywords in config.COUNTRY_HINTS.items():
        if any(kw in text_l for kw in keywords):
            return country
    return "Europe (unspecified)"


def classify(item):
    """Takes a raw fetched item, returns an enriched dict with a
    `decision` of "in_scope", "excluded_sector", "excluded_stage",
    or "excluded_not_funding"."""
    text = f"{item['title']} {item['summary']}"
    funding = is_funding_announcement(text)
    sectors = match_sectors(text)
    stage = detect_stage(text) if funding else "not_funding"

    if not funding:
        decision = "excluded_not_funding"
    elif not sectors:
        decision = "excluded_sector"
    elif stage in config.IN_SCOPE_STAGES:
        decision = "in_scope"
    else:
        decision = "excluded_stage"

    company_guess = guess_company_name(item["title"]) or item["title"][:60]

    return {
        **item,
        "sectors": sectors,
        "stage": stage,
        "country": detect_country(text),
        "company_guess": company_guess,
        "decision": decision,
    }
