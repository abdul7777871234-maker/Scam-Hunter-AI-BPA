from __future__ import annotations

import re
from urllib.parse import urlparse


class WebResearchAgent:
    """Performs external web research when current evidence is required."""

    def __init__(self, web_search):
        self.web_search = web_search

    def run(self, query: str) -> dict:
        try:
            search_query = self._build_search_query(query)
            items, cached = self.web_search.search(search_query)

            return {
                "items": items or [],
                "cached": cached,
            }

        except Exception as exc:
            return {
                "items": [],
                "cached": False,
                "error": str(exc),
            }

    @staticmethod
    def _build_search_query(text: str) -> str:
        """Turn an investigation message into a focused evidence-search query."""
        value = re.sub(r"\s+", " ", str(text or "")).strip()
        if not value:
            return ""

        urls = re.findall(r'''https?://[^\s<>"']+|www\.[^\s<>"']+''', value, re.I)
        domains = []
        for raw_url in urls:
            candidate = raw_url.rstrip(".,!?;:)]}")
            if not candidate.lower().startswith(("http://", "https://")):
                candidate = "https://" + candidate
            try:
                host = (urlparse(candidate).hostname or "").lower()
                if host and host not in domains:
                    domains.append(host)
            except Exception:
                continue

        # If the user wrapped the suspicious message in quotes, search the
        # message itself rather than the surrounding instruction text.
        quoted = re.findall(r'''["“](.*?)["”]''', value)
        message = max(quoted, key=len, default=value)

        # Remove URLs and common meta-instructions that otherwise dominate
        # search ranking (for example, "I received this message").
        message = re.sub(r'''https?://[^\s<>"']+|www\.[^\s<>"']+''', " ", message, flags=re.I)
        message = re.sub(
            r"\b(?:i received this message|please investigate this message|"
            r"please investigate|analyze this message|check this message|"
            r"the following message|use web evidence where appropriate|"
            r"generate the pdf investigation report)\b",
            " ",
            message,
            flags=re.I,
        )
        message = re.sub(r"\s+", " ", message).strip()

        # Keep searches compact and focused on the externally verifiable claim.
        terms = re.findall(r"[A-Za-z0-9][A-Za-z0-9'_-]{2,}", message)
        stop = {
            "your", "this", "that", "with", "from", "have", "been", "will",
            "within", "because", "please", "message", "account", "here",
            "they", "their", "you", "are", "was", "for", "and", "the",
            "has", "into", "only", "then", "when", "what", "where",
        }
        keywords = []
        for term in terms:
            low = term.lower()
            if low not in stop and low not in keywords:
                keywords.append(low)
        keywords = keywords[:12]

        parts = []
        if domains:
            parts.append(domains[0])
        if keywords:
            parts.extend(keywords[:8])
        parts.extend(["phishing", "scam"])
        return " ".join(parts)[:500]
