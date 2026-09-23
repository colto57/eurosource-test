"""Turns PitchBook MCP tool output into shapes the rest of this pipeline
already understands (the same item dict shape sources.py produces, and
classify.py consumes), plus a disambiguation helper for pitchbook_search.

This module deliberately does NOT call any MCP tool itself, it can't:
those tools only exist inside a Claude Code session, not in a plain
Python process. This file only parses the JSON/markdown those tools
return, once an agent has already called them. See README "Two source
lanes" for how the pieces fit together and what has to be run by hand
(or by a scheduled agent session) versus what run_daily.py can do alone.
"""

import re


_FUNDING_VERB_RE = re.compile(r"\b(?:raised|raises|secures|closes|closed|nets|lands|bags)\b", re.I)
_EARLY_STAGE_RE = re.compile(r"\b(?:pre-seed|preseed|seed)\b", re.I)
_LATER_STAGE_RE = re.compile(r"\bseries\s+[a-e]\b", re.I)


def is_likely_roundup(text, threshold=2):
    """A retrieved news chunk mentioning 2+ funding verbs, OR both an
    early-stage cue (seed/pre-seed) and a later-stage cue (Series A-E), is
    almost certainly a multi-company roundup (a newsletter digest chunk),
    not a single deal: one company doesn't raise a seed round and a
    Series B in the same article. This matters because citations_to_items
    has no way to split one chunk into per-company items, and letting
    classify.detect_stage pick up a mismatched stage mention from a
    different company in the same chunk is unreliable.

    Real example this caught: a citation titled "Ryft raises £20M Series B
    ..." had chunk text that also described Creem's seed round in passing.
    Before this check, detect_stage matched the bare word "seed" (from the
    Creem aside) ahead of "Series B" and the item was wrongly classified
    in_scope as a seed deal under the "Ryft" title."""
    if len(_FUNDING_VERB_RE.findall(text or "")) >= threshold:
        return True
    text_l = (text or "").lower()
    return bool(_EARLY_STAGE_RE.search(text_l) and _LATER_STAGE_RE.search(text_l))


def citations_to_items(citations, source_label="PitchBook news search"):
    """citations: the `citations` list returned by
    pitchbook_get_news_analysis. Returns a de-duplicated list of item
    dicts shaped like sources.fetch_feed() output, ready for
    classify.classify(). Citations whose retrieved chunk looks like a
    multi-company roundup (see is_likely_roundup) are dropped rather than
    risked as a wrong single-company attribution; callers that want to
    audit what got dropped should log them separately."""
    seen_links = set()
    items = []
    for c in citations or []:
        meta = c.get("documentMetadata", {}) or {}
        link = meta.get("link")
        title = c.get("documentTitle")
        chunk = c.get("chunkContent", "")
        if not link or not title or link in seen_links:
            continue
        if is_likely_roundup(chunk):
            continue
        seen_links.add(link)
        items.append({
            "title": title,
            "link": link,
            "summary": chunk,
            "published": meta.get("date", ""),
            "categories": [],
            "source": source_label,
        })
    return items


_PROFILE_HEADER_RE = re.compile(
    r"^#\s*(?P<kind>Company|Investor|Fund|Person)\s+Profile:\s*(?P<name>.+)$"
)
_FIELD_RE = re.compile(
    r"^\*\s*\*\*(?P<field>[^:]+):\*\*\s*(?P<value>.*)$"
)
_MARKDOWN_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def _clean_value(value):
    # Trailing explanatory notes look like " _(Unique PitchBook identifier
    # (PBID) for this entity)_" and can contain their own nested
    # parentheses, so a balanced regex match is overkill: just truncate
    # at the marker that starts every such note.
    marker = value.find(" _(")
    if marker != -1:
        value = value[:marker]
    # Collapse markdown links like [text](url) down to the link text,
    # since we only need the human-readable value here.
    value = _MARKDOWN_LINK_RE.sub(r"\1", value)
    return value.strip()


def parse_search_markdown(markdown_text):
    """Parses the markdown pitchbook_search returns into a list of
    records: {kind, name, pbid, fields: {field_name: value}}.
    One record per "# <Kind> Profile: <Name>" block, split on "---"."""
    records = []
    current = None
    for line in (markdown_text or "").splitlines():
        line = line.strip()
        if not line or line == "---":
            continue
        header = _PROFILE_HEADER_RE.match(line)
        if header:
            if current:
                records.append(current)
            current = {
                "kind": header.group("kind"),
                "name": header.group("name").strip(),
                "pbid": None,
                "fields": {},
            }
            continue
        field = _FIELD_RE.match(line)
        if field and current is not None:
            field_name = field.group("field").strip()
            value = _clean_value(field.group("value"))
            current["fields"][field_name] = value
            if field_name in ("Company ID", "Investor ID", "Fund ID", "Person ID"):
                current["pbid"] = value
    if current:
        records.append(current)
    return records


def apply_enrichment(classified_items, enrichment_by_link):
    """Mutates and returns classified_items in place. enrichment_by_link
    maps an item's `link` to a dict of verified PitchBook fields:
    {pbid, hq_location, verified_country, note, override_decision?}.

    override_decision lets a verified fact override the keyword
    classifier's decision, e.g. PitchBook confirming a company is
    actually headquartered outside Europe (a real find: Palma.ai, RSS
    text mentioned no country so classify.py left it as
    "country unconfirmed" and in_scope; PitchBook's profile shows
    San Francisco, so the enriched decision should be
    "excluded_not_europe", not in_scope)."""
    for item in classified_items:
        enrichment = enrichment_by_link.get(item.get("link"))
        if not enrichment:
            continue
        item["pitchbook_pbid"] = enrichment.get("pbid")
        item["pitchbook_hq"] = enrichment.get("hq_location")
        item["pitchbook_note"] = enrichment.get("note")
        if enrichment.get("verified_country"):
            item["country"] = enrichment["verified_country"]
        if enrichment.get("override_decision"):
            item["decision"] = enrichment["override_decision"]
    return classified_items


def pick_best_match(records, expected_country=None, sector_keywords=None):
    """Scores each parsed pitchbook_search record against what we already
    know about the candidate (country guessed from the RSS article,
    sector tags already matched) and returns the single best record, or
    None if nothing scores above zero (ambiguous, needs a human).

    This is deliberately conservative: pitchbook_search on a bare company
    name routinely returns unrelated companies that happen to share the
    name (see README/CLAUDE.md, the "mika" example), so a confident match
    requires actual corroborating evidence, not just "a result exists"."""
    best = None
    best_score = 0
    sector_keywords = [kw.lower() for kw in (sector_keywords or [])]
    for record in records:
        if record["kind"] != "Company":
            continue
        score = 0
        hq = (record["fields"].get("HQ Location") or "").lower()
        desc = (record["fields"].get("Description") or "").lower()
        industry = (record["fields"].get("Primary Industry Sector") or "").lower()
        if expected_country and expected_country.lower() in hq:
            score += 2
        if any(kw in desc or kw in industry for kw in sector_keywords):
            score += 1
        if score > best_score:
            best_score = score
            best = record
    return best if best_score > 0 else None
