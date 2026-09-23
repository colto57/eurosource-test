#!/usr/bin/env python3
"""Inlines app/index.html + styles.css + data/data.js + app.js into a single
shareable file: dist/euro-sourcing-mvp.html. No CDN dependency, no network
needed to view it after the daily fetch has run.

Also writes docs/index.html and a root-level index.html (all identical
content) since GitHub Pages can only serve from a repo's root or /docs
folder, not an arbitrary path like /dist, and either one might end up
selected in a given repo's Pages settings."""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*parts):
    with open(os.path.join(ROOT, *parts), "r", encoding="utf-8") as f:
        return f.read()


def main():
    html = read("app", "index.html")

    css = read("app", "styles.css")
    html = html.replace(
        '<link rel="stylesheet" href="styles.css">',
        "<style>\n" + css + "\n</style>",
    )

    data_js = read("data", "data.js")
    html = re.sub(
        r'<script src="\.\./data/data\.js"></script>',
        lambda _m: "<script>\n" + data_js + "\n</script>",
        html,
    )

    app_js = read("app", "app.js")
    html = html.replace(
        '<script src="app.js"></script>',
        "<script>\n" + app_js + "\n</script>",
    )

    out_path = os.path.join(ROOT, "dist", "euro-sourcing-mvp.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {out_path} ({os.path.getsize(out_path)} bytes)")

    pages_path = os.path.join(ROOT, "docs", "index.html")
    os.makedirs(os.path.dirname(pages_path), exist_ok=True)
    with open(pages_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {pages_path} ({os.path.getsize(pages_path)} bytes)")

    root_path = os.path.join(ROOT, "index.html")
    with open(root_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {root_path} ({os.path.getsize(root_path)} bytes)")


if __name__ == "__main__":
    main()
