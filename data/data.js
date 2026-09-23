window.EURO_SOURCING_DATA = {
  "meta": {
    "generated_at": "2026-09-23T13:18:36",
    "run_date": "2026-09-23",
    "sources": [
      "EU-Startups",
      "Tech.eu",
      "Sifted"
    ],
    "fetch_errors": [],
    "real": true,
    "notes": [
      "Real data fetched live from the sources listed above. No synthetic or fabricated deals in this file.",
      "This does not read from or write to Affinity, Notion, Box or Slack at runtime."
    ]
  },
  "stats": {
    "scanned": 54,
    "in_scope": 4,
    "excluded_sector": 8,
    "excluded_stage": 10,
    "excluded_not_funding": 32,
    "new_today": 0
  },
  "gaps": [
    {
      "name": "PitchBook",
      "status": "not connected",
      "why": "Needs a paid PitchBook API/export license. Motive already has a PitchBook seat (used in the weekly mv-deal-digest skill) but this MVP does not use it, to keep everything local and credential-free."
    },
    {
      "name": "Crunchbase",
      "status": "not connected",
      "why": "Needs a Crunchbase API key (paid tier for bulk/recent-rounds access)."
    },
    {
      "name": "LinkedIn",
      "status": "intentionally not implemented",
      "why": "Automated scraping of LinkedIn violates its Terms of Service. A compliant path would be LinkedIn's official Talent/Sales Navigator exports (manual) or a licensed data vendor such as Harmonic. Not built here; flagging so it isn't mistaken for an oversight."
    },
    {
      "name": "FinSMEs",
      "status": "blocked",
      "why": "Feed returns HTTP 403 from this environment (bot protection). May work from a different network/IP; worth re-testing."
    },
    {
      "name": "TechFundingNews",
      "status": "blocked",
      "why": "Feed returns HTTP 403 from this environment (bot protection)."
    }
  ],
  "deals": []
};
