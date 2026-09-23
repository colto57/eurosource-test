#!/usr/bin/env python3
"""node-style test runner: plain asserts, prints a summary, exits non-zero
on failure. Run with: python3 tests/test_classify.py (from project root or
this folder, path is fixed up below)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import classify  # noqa: E402

passed = 0
failed = 0


def check(label, condition):
    global passed, failed
    if condition:
        passed += 1
    else:
        failed += 1
        print(f"FAIL: {label}")


def item(title, summary=""):
    return {
        "title": title,
        "summary": summary,
        "link": "https://example.com/x",
        "published": "Wed, 23 Sep 2026 00:00:00 +0000",
        "categories": [],
        "source": "test",
    }


# 1. In-scope: European fintech seed round
r = classify.classify(item(
    "Berlin fintech startup Novabank raises seed round to expand payments platform",
    "Novabank, a Berlin-based challenger bank, today announced it has raised a seed "
    "round led by a European VC.",
))
check("fintech seed round is in_scope", r["decision"] == "in_scope")
check("fintech seed sectors include Fintech", "Fintech" in r["sectors"])
check("fintech seed stage detected as seed", r["stage"] == "seed")
check("fintech seed country detected as Germany", r["country"] == "Germany")

# 2. In-scope: AI infra pre-seed
r = classify.classify(item(
    "Paris AI infrastructure startup Compyra raises pre-seed to build GPU cloud",
    "Compyra secures pre-seed funding to build AI infrastructure for European labs.",
))
check("ai pre-seed is in_scope", r["decision"] == "in_scope")
check("ai pre-seed matches AI and Compute sectors", "AI" in r["sectors"] and "Compute" in r["sectors"])
check("ai pre-seed stage detected as pre-seed", r["stage"] == "pre-seed")

# 3. Excluded: wrong stage (Series B)
r = classify.classify(item(
    "London regtech firm Compliq raises $40M Series B",
    "Compliq, a regulatory technology company, raises a Series B round.",
))
check("series B is excluded_stage", r["decision"] == "excluded_stage")

# 4. Excluded: wrong sector (general consumer app, no sector keyword)
r = classify.classify(item(
    "Foodly raises seed round for grocery delivery app",
    "Foodly secures seed funding to expand its grocery delivery service.",
))
check("consumer app is excluded_sector", r["decision"] == "excluded_sector")

# 5. Excluded: not a funding announcement at all
r = classify.classify(item(
    "Fintech regulation in the EU: what changes in 2027",
    "An explainer on upcoming fintech regulatory changes.",
))
check("non-funding article is excluded_not_funding", r["decision"] == "excluded_not_funding")

# 6. Digital assets / crypto seed
r = classify.classify(item(
    "Zurich crypto startup Ledgerly raises seed round for stablecoin infrastructure",
    "Ledgerly raises seed funding to build stablecoin settlement infrastructure.",
))
check("crypto seed is in_scope", r["decision"] == "in_scope")
check("crypto seed matches Digital Assets sector", "Digital Assets" in r["sectors"])
check("crypto seed country detected as Switzerland", r["country"] == "Switzerland")

# 7. company name extraction heuristic
name = classify.guess_company_name("Novabank raises seed round to expand payments platform")
check("company name extraction picks Novabank", name == "Novabank")

name = classify.guess_company_name("A totally unrelated headline with no funding verb")
check("company name extraction returns None when no pattern matches", name is None)

# 8. Ambiguous stage: funding + in-scope sector, but no seed/series wording
# at all. Must NOT be silently dropped (mv-deal-digest rule: flag, don't
# exclude) -> needs_review, not excluded_stage.
r = classify.classify(item(
    "Munich fintech startup Kontoro raises €4 million to expand lending platform",
    "Kontoro secures new funding to expand its lending platform across Germany.",
))
check("ambiguous stage funding+sector is needs_review, not silently dropped", r["decision"] == "needs_review")

# 9. Debt facility should not be treated as an equity seed round even
# though it contains "raises" and a sector keyword.
r = classify.classify(item(
    "Dublin fintech Loantree raises €20 million debt facility to fund lending",
    "Loantree secures a debt facility, structured as a credit facility with a European bank.",
))
check("debt facility is excluded_debt_or_ma, not in_scope", r["decision"] == "excluded_debt_or_ma")

# 10. Acquisition, phrased with a funding-shaped verb ("closes"), should
# still be excluded as M&A rather than counted as a seed round.
r = classify.classify(item(
    "Compliance group closes acquisition of regtech startup Verifai",
    "The compliance group closes its acquisition of Verifai, a regtech seed-stage startup.",
))
check("acquisition is excluded_debt_or_ma, not in_scope", r["decision"] == "excluded_debt_or_ma")

# 11. Word-boundary AI matching: punctuation right after "AI" must still match.
r = classify.classify(item(
    "Oslo startup Nordbrain raises seed round, product built on AI.",
    "Nordbrain raises a seed round for its platform built on AI.",
))
check("AI followed by punctuation still matches AI sector", "AI" in r["sectors"])

# 12. Word-boundary AI matching must not false-positive on unrelated words
# containing "ai" as a substring (e.g. "maintain", "certain").
r = classify.classify(item(
    "Vienna startup Certaly raises seed round to maintain certain compliance workflows",
    "Certaly raises seed funding for a regtech workflow tool to maintain certain processes.",
))
check("'maintain'/'certain' do not false-positive match AI", "AI" not in r["sectors"])

# 13. Amount extraction, used only for sort order (biggest rounds first),
# not for financial reporting.
check("extracts $8M", classify.extract_amount_usd_approx("Company raises $8M seed") == 8.0)
check("extracts and converts €6 million to approx USD", classify.extract_amount_usd_approx("raises €6 million seed") == 7.0)
check("extracts £8m with GBP conversion", classify.extract_amount_usd_approx("raises £8m seed") == 10.7)
check("extracts $1.2 billion as 1200", classify.extract_amount_usd_approx("raises $1.2 billion") == 1200.0)
check("returns None when no amount is present", classify.extract_amount_usd_approx("Magic AI raises seed round") is None)

print(f"{passed} of {passed + failed} checks passed")
if failed:
    sys.exit(1)
