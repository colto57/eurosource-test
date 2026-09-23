"""Config for the European pre-seed/seed sourcing scanner.

Everything in this file is tunable without touching the rest of the code.
"""

# Live, free RSS feeds this scanner actually fetches. All three are
# pan-European tech/startup publications, so geography is mostly already
# filtered by the source; country tagging below is best-effort, not a gate.
SOURCES = [
    {"name": "EU-Startups", "url": "https://www.eu-startups.com/feed/"},
    {"name": "Tech.eu", "url": "https://tech.eu/feed/"},
    {"name": "Sifted", "url": "https://sifted.eu/feed"},
]

# Data sources beyond the RSS feeds above, currently in use. Blocked and
# ToS-restricted sources (Crunchbase, LinkedIn, FinSMEs, TechFundingNews)
# are intentionally not listed here anymore; that reasoning still lives in
# README.md / CLAUDE.md rather than in the app itself.
KNOWN_GAPS = [
    {
        "name": "PitchBook",
        "status": "partially connected",
        "why": "Connected via an MCP tool as of 2026-09-23, but it has no "
               "screener/filter tool (can't ask for \"all European seed deals "
               "this week\" the way Jimmy's saved search can). Used two ways "
               "here instead: pitchbook_get_news_analysis as a second discovery "
               "source (data/pitchbook_raw.json) and pitchbook_search/get_profile "
               "to verify a candidate once found (data/pitchbook_enrichment.json). "
               "Both are produced by an agent calling MCP tools by hand, not by "
               "run_daily.py itself, since that tool only exists inside a Claude "
               "Code session. See CLAUDE.md 'Two source lanes'.",
    },
]

# Sector keyword lists = Tim's "core focus" areas. Matching is
# case-insensitive substring matching against title + summary.
SECTORS = {
    "Fintech": [
        "fintech", "payments", "neobank", "challenger bank", "banking",
        "lending", "insurtech", "wealthtech", "embedded finance",
        "open banking", "capital markets", "asset management",
    ],
    "AI": [
        "artificial intelligence", "ai-powered", "ai-native", "ai startup",
        "ai agent", "ai infrastructure", "machine learning",
        "generative ai", "foundation model", "large language model",
        "ai", "llm",
    ],
    "RegTech": [
        "regtech", "regulatory technology", "compliance software",
        "kyc", "aml", "anti-money laundering", "regulatory compliance",
    ],
    "Digital Assets": [
        "crypto", "cryptocurrency", "blockchain", "web3", "digital assets",
        "stablecoin", "tokeniz", "defi",
    ],
    "Compute": [
        "data center", "data centre", "gpu cloud", "ai infrastructure",
        "compute infrastructure", "neocloud", "gpu capacity", "compute",
    ],
}

# Phrases that indicate the article is a funding announcement at all.
FUNDING_SIGNAL_WORDS = [
    "raises", "raised", "secures", "closes", "lands", "nets", "bags",
    "scores", "has raised", "funding round", "seed round", "investment from",
    "backed by",
]

# Rounds that are equity fundraises but not what we want, or not equity at
# all. Mirrors mv-deal-digest's rule: equity rounds only, no debt-only
# facilities, no M&A. Checked before sector/stage; a match here excludes
# regardless of what else matches, since "raises $50M debt facility" would
# otherwise sail through the funding-signal check above.
DEBT_OR_MA_SIGNAL_WORDS = [
    "debt facility", "credit facility", "venture debt", "debt financing",
    "debt round", "loan facility", "acquired by", "acquires", "acquisition",
    "to be acquired", "merger", "merges with",
]

# Stage detection, checked in this order. First match wins.
STAGE_PATTERNS = [
    ("pre-seed", ["pre-seed", "preseed", "pre seed"]),
    ("seed", ["seed round", "seed funding", "seed extension", "seed raise",
              "in seed", "seed capital", "raises seed", "seed investment",
              "seed"]),
    ("series a+", ["series a", "series b", "series c", "series d",
                    "series e", "growth round", "growth funding"]),
]

# In-scope stages for the daily digest. Everything else is still recorded
# (for the audit trail / stats) but excluded from the "new deals" list.
IN_SCOPE_STAGES = {"pre-seed", "seed"}

# Keywords in this set are ambiguous enough (mostly acronyms/short tokens)
# that plain substring matching produces false positives or false negatives
# around punctuation (e.g. "...built on AI." vs "AI-powered"). These are
# matched with regex word boundaries instead; everything else in SECTORS
# uses plain substring matching since multi-word phrases rarely collide.
WORD_BOUNDARY_SECTOR_KEYWORDS = {"ai", "llm", "kyc", "aml", "defi", "compute"}

# Same idea for stage detection: a real live run found "Complir raises $11M
# seed to automate..." didn't match any seed phrase ("seed round", "seed
# funding", etc.), just the bare word. Bare "seed" is only checked this
# way (word boundary, not substring) to avoid matching things like
# "reseed" or "seedling"; it's also only ever reached after
# is_funding_announcement already gated on a funding verb, which further
# limits false positives.
WORD_BOUNDARY_STAGE_KEYWORDS = {"seed"}

# Best-effort country tagging, for display only (not a filter).
COUNTRY_HINTS = {
    "UK": ["london", "united kingdom", "uk-based", "british startup"],
    "Germany": ["berlin", "munich", "germany", "german startup"],
    "France": ["paris", "france", "french startup"],
    "Netherlands": ["amsterdam", "netherlands", "dutch startup"],
    "Sweden": ["stockholm", "sweden", "swedish startup"],
    "Spain": ["madrid", "barcelona", "spain", "spanish startup"],
    "Italy": ["milan", "rome", "italy", "italian startup"],
    "Switzerland": ["zurich", "geneva", "switzerland", "swiss startup"],
    "Ireland": ["dublin", "ireland", "irish startup"],
    "Portugal": ["lisbon", "portugal", "portuguese startup"],
    "Poland": ["warsaw", "poland", "polish startup"],
    "Finland": ["helsinki", "finland", "finnish startup"],
    "Denmark": ["copenhagen", "denmark", "danish startup"],
    "Norway": ["oslo", "norway", "norwegian startup"],
    "Belgium": ["brussels", "belgium", "belgian startup"],
    "Austria": ["vienna", "austria", "austrian startup"],
    "Estonia": ["tallinn", "estonia", "estonian startup"],
}

DATA_DIR = "data"
SEEN_STORE_PATH = f"{DATA_DIR}/seen.json"
HISTORY_DIR = f"{DATA_DIR}/history"
DATA_JS_PATH = f"{DATA_DIR}/data.js"
DATA_JSON_PATH = f"{DATA_DIR}/data.json"
