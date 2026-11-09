"""Tiny Wikipedia client used by the `search_wikipedia` tool.

It calls the public MediaWiki API directly with `requests` and sends a
descriptive User-Agent, which Wikipedia requires from automated clients.
"""

from __future__ import annotations

import os

import requests

API_URL = "https://en.wikipedia.org/w/api.php"
DEFAULT_USER_AGENT = "ai-math-assistant/1.0 (educational LangChain project)"


def search(query: str, max_chars: int = 2000, timeout: float = 10.0) -> str:
    """Return the title and intro summary of the best-matching English Wikipedia article."""
    headers = {"User-Agent": os.getenv("WIKIPEDIA_USER_AGENT", DEFAULT_USER_AGENT)}
    params = {
        "action": "query",
        "format": "json",
        "formatversion": 2,
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": 1,
        "prop": "extracts",
        "exintro": 1,
        "explaintext": 1,
        "redirects": 1,
    }
    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        return f"Wikipedia request failed: {exc}"

    pages = data.get("query", {}).get("pages", [])
    if not pages:
        return f"No Wikipedia article found for {query!r}."

    page = pages[0]
    summary = (page.get("extract") or "").strip()
    if not summary:
        return f"Found the article '{page.get('title')}', but it has no summary."
    return f"{page['title']}:\n{summary[:max_chars]}"
