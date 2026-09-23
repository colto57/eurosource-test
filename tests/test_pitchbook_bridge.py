#!/usr/bin/env python3
"""Tests for pitchbook_bridge.py, using fixture text taken from the real
pitchbook_search("mika") and pitchbook_get_news_analysis(...) responses
received in session (trimmed, not fabricated wording)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pitchbook_bridge  # noqa: E402

passed = 0
failed = 0


def check(label, condition):
    global passed, failed
    if condition:
        passed += 1
    else:
        failed += 1
        print(f"FAIL: {label}")


MIKA_SEARCH_MARKDOWN = """
# Company Profile: Mitra Keluarga Karyasehat
* **Company ID:** 163337-95 _(Unique PitchBook identifier (PBID) for this entity)_
* **Description:** PT Mitra Keluarga Karyasehat Tbk operates a hospital network.
* **Primary Industry Sector:** Healthcare _(The main industry/sector)_
* **HQ Location:** Bekasi Timur, Indonesia
---
# Company Profile: Mika Health
* **Company ID:** 277720-57 _(Unique PitchBook identifier (PBID) for this entity)_
* **Description:** Developer of a digital therapy application designed to guide cancer patients during their illness and treatment.
* **Website:** [de.mika.health](de.mika.health)
* **Primary Industry Sector:** Healthcare _(The main industry/sector)_
* **HQ Location:** Berlin, Germany
---
# Company Profile: Mika AI
* **Company ID:** 541194-49 _(Unique PitchBook identifier (PBID) for this entity)_
* **Description:** Developer of an artificial intelligence-based accounting platform designed to help users take care of their books.
* **Website:** [www.getmika.de](www.getmika.de)
* **Primary Industry Sector:** Information Technology _(The main industry/sector)_
* **HQ Location:** Berlin, Germany
---
# Company Profile: Mika
* **Company ID:** 582278-86 _(Unique PitchBook identifier (PBID) for this entity)_
* **Description:** The company primarily operates in the Distributors/Wholesale industry.
* **Primary Industry Sector:** Business Products and Services (B2B) _(The main industry/sector)_
* **HQ Location:** Andria, Italy
---
"""

records = pitchbook_bridge.parse_search_markdown(MIKA_SEARCH_MARKDOWN)
check("parses all 4 company records", len(records) == 4)
check("extracts PBID for Mika AI", any(r["pbid"] == "541194-49" for r in records))
check("extracts HQ Location for Mika AI", any(
    r["name"] == "Mika AI" and r["fields"].get("HQ Location") == "Berlin, Germany"
    for r in records
))
check("strips the parenthetical PBID annotation from the field value", all(
    "_(" not in r["fields"].get("Company ID", "") for r in records
))
check("collapses the markdown website link to plain text", any(
    r["fields"].get("Website") == "www.getmika.de" for r in records
))

match = pitchbook_bridge.pick_best_match(
    records, expected_country="Germany", sector_keywords=["ai", "accounting"]
)
check("disambiguates to Mika AI given country + sector hints", match is not None and match["pbid"] == "541194-49")

no_match = pitchbook_bridge.pick_best_match(
    records, expected_country="France", sector_keywords=["biotech"]
)
check("returns None when nothing corroborates (no false confident match)", no_match is None)

weak_match = pitchbook_bridge.pick_best_match(records, expected_country="Germany", sector_keywords=[])
check(
    "country alone can still surface a candidate (score > 0), even without a sector hint",
    weak_match is not None,
)

CITATIONS_FIXTURE = [
    {
        "documentTitle": "Boxd raises $2M to build cloud infrastructure for AI coding agents",
        "documentMetadata": {
            "link": "https://www.li-holdings.co.uk/boxd-raises-2m-to-build-cloud-infrastructure-for-ai-coding-agents-tech-eu/",
            "date": "2026-09-16T09:49:23Z",
        },
        "chunkContent": "Dutch startup Boxd has raised $2 million in a pre-seed funding round.",
    },
    {
        "documentTitle": "Student startup Expanse raises $5m for sustainable compute",
        "documentMetadata": {
            "link": "https://angelcapital.scot/news/student-startup-expanse-raises-5m-for-sustainable-compute/",
            "date": "2026-09-17T10:35:19Z",
        },
        "chunkContent": "A company founded by four University of Edinburgh graduates raised $5.3m in seed funding.",
    },
    {
        # Duplicate link, should be dropped by de-dup.
        "documentTitle": "Student startup Expanse raises $5m for sustainable compute",
        "documentMetadata": {
            "link": "https://angelcapital.scot/news/student-startup-expanse-raises-5m-for-sustainable-compute/",
            "date": "2026-09-17T10:35:19Z",
        },
        "chunkContent": "Duplicate chunk of the same article, different retrieval hit.",
    },
]

# Real regression case: a citation titled about a Series B company
# ("Ryft") whose retrieved chunk also mentions a different company's seed
# round in passing (Creem). Must be dropped as a roundup, not ingested as
# if the seed-stage company were Ryft.
MIXED_STAGE_CHUNK = (
    "Creem, the Tallinn payments startup building billing for AI companies, "
    "raised a €5M seed led by Inovo VC on 17 September, the entry end of the "
    "same wave Ryft is now riding at Series B."
)
check("mixed seed + Series B chunk is flagged as a roundup", pitchbook_bridge.is_likely_roundup(MIXED_STAGE_CHUNK))

RYFT_CREEM_CITATIONS = [{
    "documentTitle": "Ryft raises £20M Series B to take marketplace payments beyond the UK",
    "documentMetadata": {"link": "https://example.com/ryft-series-b", "date": "2026-09-18T12:26:06Z"},
    "chunkContent": MIXED_STAGE_CHUNK,
}]
check(
    "citations_to_items drops the Ryft/Creem mixed-stage citation entirely",
    pitchbook_bridge.citations_to_items(RYFT_CREEM_CITATIONS) == [],
)

items = pitchbook_bridge.citations_to_items(CITATIONS_FIXTURE)
check("de-dupes citations pointing at the same link", len(items) == 2)
check("tags items with the PitchBook news search source label", all(i["source"] == "PitchBook news search" for i in items))
check("preserves the article link", items[0]["link"] == CITATIONS_FIXTURE[0]["documentMetadata"]["link"])

print(f"{passed} of {passed + failed} checks passed")
if failed:
    sys.exit(1)
