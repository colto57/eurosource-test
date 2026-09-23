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

# Sources that would add coverage but are not wired up. Kept here so the
# gap is visible in the app rather than silently missing. See README.
KNOWN_GAPS = [
    {
        "name": "PitchBook",
        "status": "not connected",
        "why": "Needs a paid PitchBook API/export license. Motive already has a "
               "PitchBook seat (used in the weekly mv-deal-digest skill) but this "
               "MVP does not use it, to keep everything local and credential-free.",
    },
    {
        "name": "Crunchbase",
        "status": "not connected",
        "why": "Needs a Crunchbase API key (paid tier for bulk/recent-rounds access).",
    },
    {
        "name": "LinkedIn",
        "status": "intentionally not implemented",
        "why": "Automated scraping of LinkedIn violates its Terms of Service. "
               "A compliant path would be LinkedIn's official Talent/Sales "
               "Navigator exports (manual) or a licensed data vendor such as "
               "Harmonic. Not built here; flagging so it isn't mistaken for "
               "an oversight.",
    },
    {
        "name": "FinSMEs",
        "status": "blocked",
        "why": "Feed returns HTTP 403 from this environment (bot protection). "
               "May work from a different network/IP; worth re-testing.",
    },
    {
        "name": "TechFundingNews",
        "status": "blocked",
        "why": "Feed returns HTTP 403 from this environment (bot protection).",
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
        "artificial intelligence", " ai ", "ai startup", "ai-powered",
        "machine learning", "generative ai", "foundation model",
        "large language model", "llm ",
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
        "compute infrastructure", "neocloud", "gpu capacity",
    ],
}

# Phrases that indicate the article is a funding announcement at all.
FUNDING_SIGNAL_WORDS = [
    "raises", "raised", "secures", "closes", "lands", "nets", "bags",
    "scores", "has raised", "funding round", "seed round", "investment from",
    "backed by",
]

# Stage detection, checked in this order. First match wins.
STAGE_PATTERNS = [
    ("pre-seed", ["pre-seed", "preseed", "pre seed"]),
    ("seed", ["seed round", "seed funding", "seed extension", "seed raise",
              "in seed", "€ seed", "seed capital", "raises seed"]),
    ("series a+", ["series a", "series b", "series c", "series d",
                    "series e", "growth round", "growth funding"]),
]

# In-scope stages for the daily digest. Everything else is still recorded
# (for the audit trail / stats) but excluded from the "new deals" list.
IN_SCOPE_STAGES = {"pre-seed", "seed"}

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
