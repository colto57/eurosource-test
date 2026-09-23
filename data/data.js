window.EURO_SOURCING_DATA = {
  "meta": {
    "generated_at": "2026-09-23T19:13:38",
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
    "needs_review": 3,
    "excluded_sector": 8,
    "excluded_stage": 6,
    "excluded_debt_or_ma": 1,
    "excluded_not_europe": 0,
    "excluded_not_funding": 32,
    "new_today": 7
  },
  "gaps": [
    {
      "name": "PitchBook",
      "status": "partially connected",
      "why": "Connected via an MCP tool as of 2026-09-23, but it has no screener/filter tool (can't ask for \"all European seed deals this week\" the way Jimmy's saved search can). Used two ways here instead: pitchbook_get_news_analysis as a second discovery source (data/pitchbook_raw.json) and pitchbook_search/get_profile to verify a candidate once found (data/pitchbook_enrichment.json). Both are produced by an agent calling MCP tools by hand, not by run_daily.py itself, since that tool only exists inside a Claude Code session. See CLAUDE.md 'Two source lanes'."
    }
  ],
  "deals": [
    {
      "title": "Stockholm\u2019s Spiich raises \u20ac3 million to let AI handle admin work while sales teams focus on customers",
      "link": "https://www.eu-startups.com/2026/09/stockholms-spiich-raises-e3-million-to-let-ai-handle-admin-work-while-sales-teams-focus-on-customers/",
      "summary": "Spiich, a Stockholm-based AI sales agent startup, has raised a \u20ac3 million Seed round. This announcement comes ten months after the company raised a \u20ac600k pre-Seed round, bringing its total funding to \u20ac3.6 million. The funding round was led by Ugly Duckling Ventures, a Copenhagen-based venture firm backing Nordic B2B software and technology companies. The [\u2026] The post Stockholm\u2019s Spiich raises \u20ac3 million to let AI handle admin work while sales teams focus on customers appeared first on EU-Startups .",
      "published": "Wed, 23 Sep 2026 08:26:49 +0000",
      "categories": [
        "Funding",
        "Sweden Startups",
        "Alliance VC",
        "Ampli Ventures",
        "Cherry Ventures",
        "CRM",
        "Dennis Hadzialic",
        "Johan Torssell",
        "Louise Lachmann",
        "sales",
        "Spiich Labs",
        "ugly duckling ventures"
      ],
      "source": "EU-Startups",
      "sectors": [
        "AI"
      ],
      "stage": "pre-seed",
      "country": "Sweden",
      "company_guess": "Stockholm\u2019s Spiich raises \u20ac3 million to let AI handle admin ",
      "amount_usd_approx": 3.5,
      "decision": "in_scope",
      "id": "stockholm\u2019s-spiich-raises-\u20ac3-million-to-let-ai-handle-admin"
    },
    {
      "title": "Germany\u2019s SPRIND and the Netherlands\u2019 NADI launch \u20ac40 million challenge to fast-track European AI chip design",
      "link": "https://www.eu-startups.com/2026/09/germanys-sprind-and-the-netherlands-nadi-launch-e40-million-challenge-to-fast-track-european-ai-chip-design/",
      "summary": "Germany\u2019s Federal Agency for Breakthrough Innovation (SPRIND) and its Dutch counterpart, the National Agency for Disruptive Innovation (NADI), have launched a joint \u20ac40 million programme to fund radical innovations in pan-European chip design. Announced today, the AI-Native Chip Design Challenge marks the first joint-funding initiative between SPRIND and NADI. It aims to cut chip development [\u2026] The post Germany\u2019s SPRIND and the Netherlands\u2019 NADI launch \u20ac40 million challenge to fast-track European AI chip design appeared first on EU-Startups .",
      "published": "Wed, 23 Sep 2026 07:20:28 +0000",
      "categories": [
        "Funding",
        "ASML",
        "Beau Anne-Chilla",
        "deeptech",
        "German Federal Agency for Breakthrough Innovation (SPRIND)",
        "Heleen Herbert",
        "Jano Costard",
        "Jelle Prins",
        "National Agency for Disruptive Innovation (NADI)",
        "Vinnova"
      ],
      "source": "EU-Startups",
      "sectors": [
        "AI"
      ],
      "stage": "unclear",
      "country": "Germany",
      "company_guess": "Germany\u2019s SPRIND and the Netherlands\u2019 NADI launch \u20ac40 millio",
      "amount_usd_approx": 46.5,
      "decision": "needs_review",
      "id": "germany\u2019s-sprind-and-the-netherlands\u2019-nadi-launch-\u20ac40-millio"
    },
    {
      "title": "Berlin-based mika raises \u20ac6 million to scale its AI-native alternative to traditional tax firms",
      "link": "https://www.eu-startups.com/2026/09/berlin-based-mika-raises-e6-million-to-scale-its-ai-native-alternative-to-traditional-tax-firms/",
      "summary": "mika, a Berlin-based vertical AI startup building an AI-native alternative to the traditional tax firm for Germany\u2019s small limited companies (GmbHs and UGs), has raised \u20ac6 million in a Seed funding round to support growth and the further development of the platform. The round was led by Smedvig Ventures, with participation from the Basel-based family [\u2026] The post Berlin-based mika raises \u20ac6 million to scale its AI-native alternative to traditional tax firms appeared first on EU-Startups .",
      "published": "Wed, 23 Sep 2026 07:00:40 +0000",
      "categories": [
        "Funding",
        "Germany-Startups",
        "Agnieszka Walorska",
        "Dennis Bemmann",
        "dutch founders fund",
        "Freddie Kalfayan",
        "Henry M\u00fcssemann",
        "Johannes Ditterich",
        "KEEN Venture Partners",
        "Luke Linnekuhle",
        "Martina Pfeifer",
        "Michael Brehm",
        "mika",
        "Samen Slimmer Alliance",
        "smedvig ventures",
        "Wecken & Cie"
      ],
      "source": "EU-Startups",
      "sectors": [
        "AI"
      ],
      "stage": "seed",
      "country": "Germany",
      "company_guess": "Berlin-based mika raises \u20ac6 million to scale its AI-native a",
      "amount_usd_approx": 7.0,
      "decision": "in_scope",
      "id": "berlin-based-mika-raises-\u20ac6-million-to-scale-its-ai-native-a"
    },
    {
      "title": "German AI startup mika raises \u20ac6M to simplify accounting and tax for SMEs",
      "link": "https://tech.eu/2026/09/23/german-ai-startup-mika-raises-eur6m-to-simplify-accounting-and-tax-for-smes/",
      "summary": "Berlin-basedvertical AI startup mika has raised \u20ac6 million in a seed round led bypan-European investor Smedvig Ventures. Basel-based family office Wecken &Cie. (Care4 AG) also participated, alongs...",
      "published": "Wed, 23 Sep 2026 07:15:00 +0000",
      "categories": [
        "Fintech",
        "Artificial Intelligence",
        "SaaS"
      ],
      "source": "Tech.eu",
      "sectors": [
        "AI"
      ],
      "stage": "seed",
      "country": "Germany",
      "company_guess": "German AI startup mika raises \u20ac6M to simplify accounting and",
      "amount_usd_approx": 7.0,
      "decision": "in_scope",
      "id": "german-ai-startup-mika-raises-\u20ac6m-to-simplify-accounting-and"
    },
    {
      "title": "Palma.ai raises $1.8M to bring governed AI agents to more enterprises",
      "link": "https://tech.eu/2026/09/23/palmaai-raises-18m-to-bring-governed-ai-agents-to-more-enterprises/",
      "summary": "Palma.ai, an enterprise platform for governing AI agents atruntime, has raised $1.8 million in pre-seed funding. The round was led byD11Z, with participation from Plug and Play Ventures, Deel, Scale N...",
      "published": "Wed, 23 Sep 2026 07:09:34 +0000",
      "categories": [
        "Artificial Intelligence"
      ],
      "source": "Tech.eu",
      "sectors": [
        "AI"
      ],
      "stage": "pre-seed",
      "country": "country unconfirmed",
      "company_guess": "Palma.ai",
      "amount_usd_approx": 1.8,
      "decision": "in_scope",
      "id": "palma.ai"
    },
    {
      "title": "Primo raises $8M to bring autonomous AI agents to IT operations",
      "link": "https://tech.eu/2026/09/22/primo-raises-8m-to-bring-autonomous-ai-agents-to-it-operations/",
      "summary": "Primo, an AI platform for managing corporate IT, has raised$8 million in a funding round led by Headline and Global Founders Capital. The company\u2019s investors also include Pennylane co-founder and CEO ...",
      "published": "Tue, 22 Sep 2026 07:30:00 +0000",
      "categories": [
        "Software development",
        "Artificial Intelligence"
      ],
      "source": "Tech.eu",
      "sectors": [
        "AI"
      ],
      "stage": "unclear",
      "country": "country unconfirmed",
      "company_guess": "Primo",
      "amount_usd_approx": 8.0,
      "decision": "needs_review",
      "id": "primo"
    },
    {
      "title": "Magic AI raises \u00a38m to take its AI-powered fitness mirror to the US",
      "link": "https://sifted.eu/articles/magic-ai-fitness-mirror-funding-round/",
      "summary": "",
      "published": "Wed, 23 Sep 2026 15:01:35 GMT",
      "categories": [],
      "source": "Sifted",
      "sectors": [
        "AI"
      ],
      "stage": "unclear",
      "country": "country unconfirmed",
      "company_guess": "Magic AI",
      "amount_usd_approx": 10.7,
      "decision": "needs_review",
      "id": "magic-ai"
    }
  ]
};
