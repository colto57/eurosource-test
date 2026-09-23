"""Fetches real RSS feeds. Stdlib only, no third-party deps.

Deliberately simple: this reads standard RSS 2.0 <item> blocks. It is not a
general-purpose feed parser (no Atom support, no encoding sniffing beyond
UTF-8) because the three sources in config.SOURCES are all plain RSS.
"""

import html
import re
import urllib.request
import xml.etree.ElementTree as ET

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text):
    if not text:
        return ""
    text = TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_feed(url, timeout=10):
    """Returns a list of raw items: {title, link, summary, published, categories}.

    Raises the underlying exception on network/parse failure; callers decide
    whether one bad source should stop the whole run.
    """
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()

    root = ET.fromstring(raw)
    items = []
    for item in root.iter("item"):
        title = _strip_html(item.findtext("title") or "")
        link = (item.findtext("link") or "").strip()
        summary = _strip_html(
            item.findtext("description") or item.findtext("summary") or ""
        )
        published = (item.findtext("pubDate") or "").strip()
        categories = [
            (c.text or "").strip() for c in item.findall("category") if c.text
        ]
        if title and link:
            items.append({
                "title": title,
                "link": link,
                "summary": summary,
                "published": published,
                "categories": categories,
            })
    return items


def fetch_all(sources):
    """Returns (items, errors). Never raises; a broken source is recorded,
    not fatal to the run."""
    items = []
    errors = []
    for src in sources:
        try:
            fetched = fetch_feed(src["url"])
            for it in fetched:
                it["source"] = src["name"]
            items.extend(fetched)
        except Exception as exc:  # noqa: BLE001 - one bad feed shouldn't kill the run
            errors.append({"source": src["name"], "url": src["url"], "error": str(exc)})
    return items, errors
