"""Keyword classification: sector, funding stage, country, company guess.

This is intentionally simple keyword matching, not NLP. It is meant to be a
fast, auditable pre-filter that a human reviews in the app, not a fully
automated decision-maker. See README "What this does not do".

Ambiguous stage/sector calls are not silently dropped, matching the rule
the existing mv-deal-digest process already follows ("if borderline, flag,
do not silently exclude"): they get decision "needs_review" and stay
visible in the app in their own lane instead of disappearing into the
excluded counts.
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


def _contains_any(text_l, keywords, boundary_words):
    """Word-boundary match for short/ambiguous keywords (avoids the
    "AI." vs "AI-powered" punctuation trap), plain substring for
    everything else (multi-word phrases don't collide the same way)."""
    for kw in keywords:
        if kw in boundary_words:
            if re.search(r"\b" + re.escape(kw) + r"\b", text_l):
                return True
        elif kw in text_l:
            return True
    return False


def match_sectors(text):
    text_l = text.lower()
    return [
        sector
        for sector, keywords in config.SECTORS.items()
        if _contains_any(text_l, keywords, config.WORD_BOUNDARY_SECTOR_KEYWORDS)
    ]


def is_funding_announcement(text):
    text_l = text.lower()
    return any(kw in text_l for kw in config.FUNDING_SIGNAL_WORDS)


def is_debt_or_ma(text):
    text_l = text.lower()
    return any(kw in text_l for kw in config.DEBT_OR_MA_SIGNAL_WORDS)


def detect_stage(text):
    text_l = text.lower()
    for stage, keywords in config.STAGE_PATTERNS:
        if _contains_any(text_l, keywords, config.WORD_BOUNDARY_STAGE_KEYWORDS):
            return stage
    return "unclear"


_AMOUNT_RE = re.compile(
    r"([$€£])\s?(\d+(?:\.\d+)?)\s*(million|m|billion|b)\b", re.I
)
# Rough, fixed rates (same ones mv-deal-digest uses) purely to make deal
# sizes comparable for sorting. Not for financial reporting.
_FX_TO_USD = {"$": 1.0, "€": 1.163, "£": 1.340}


def extract_amount_usd_approx(text):
    """Best-effort round size in approximate USD, for sorting only (so the
    biggest rounds surface first and aren't buried in whatever order the
    RSS feed happened to return). Returns None if no amount pattern is
    found; callers should sort unknowns last, not treat None as zero."""
    m = _AMOUNT_RE.search(text or "")
    if not m:
        return None
    symbol, number, unit = m.groups()
    value = float(number) * (1000 if unit.lower().startswith("b") else 1)
    return round(value * _FX_TO_USD.get(symbol, 1.0), 1)


def detect_country(text):
    """Best-effort only. Returns "country unconfirmed" (not "Europe") when
    no hint matches, deliberately not defaulting to Europe: a real test
    run found a Tech.eu-covered company (Palma.ai) that PitchBook's
    profile shows is headquartered in San Francisco, not Europe at all.
    The RSS snippet never named a country, so silently assuming Europe
    would have let a non-European company into a Europe-only digest."""
    text_l = text.lower()
    for country, keywords in config.COUNTRY_HINTS.items():
        if any(kw in text_l for kw in keywords):
            return country
    return "country unconfirmed"


def classify(item):
    """Takes a raw fetched item, returns an enriched dict with a
    `decision` of one of:
      in_scope             funding announcement, in-scope sector, pre-seed/seed
      needs_review         funding announcement, in-scope sector, but stage is
                            ambiguous (not confidently excluded, not confidently in)
      excluded_stage        confidently a later stage (Series A+)
      excluded_sector        funding announcement but no core-focus sector matched
      excluded_debt_or_ma     debt facility, acquisition or merger, not an equity round
      excluded_not_funding    not a funding announcement at all
    """
    text = f"{item['title']} {item['summary']}"
    funding = is_funding_announcement(text)
    debt_or_ma = is_debt_or_ma(text)
    sectors = match_sectors(text)
    stage = detect_stage(text) if funding else "not_funding"

    if not funding:
        decision = "excluded_not_funding"
    elif debt_or_ma:
        decision = "excluded_debt_or_ma"
    elif not sectors:
        decision = "excluded_sector"
    elif stage in config.IN_SCOPE_STAGES:
        decision = "in_scope"
    elif stage == "unclear":
        decision = "needs_review"
    else:
        decision = "excluded_stage"

    company_guess = guess_company_name(item["title"]) or item["title"][:60]

    return {
        **item,
        "sectors": sectors,
        "stage": stage,
        "country": detect_country(text),
        "company_guess": company_guess,
        "amount_usd_approx": extract_amount_usd_approx(text),
        "decision": decision,
    }
