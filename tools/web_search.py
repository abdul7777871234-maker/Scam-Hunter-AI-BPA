from __future__ import annotations

import re
from html import unescape
from urllib.parse import quote_plus

from cache.search_cache import SearchCache


class WebSearch:
    def __init__(self, settings):
        self.settings = settings
        self.cache = SearchCache(settings.cache_dir, settings.search_ttl_hours)

    def search(self, query: str):
        query = self._clean_query(query)

        if not query:
            return [], False

        cached = self.cache.get(query)
        if cached:
            return self._normalize(cached), True

        errors = []

        try:
            from ddgs import DDGS

            results = []
            with DDGS(timeout=12) as ddgs:
                for item in ddgs.text(
                    query,
                    max_results=max(1, int(self.settings.max_web_results)),
                ):
                    results.append(item)

            results = self._normalize(results)
            if results:
                self.cache.put(query, results)
                return results, False

            errors.append("DDGS returned no results")

        except Exception as exc:
            errors.append(f"DDGS: {self._safe_error(exc)}")

        # Bing HTML fallback is useful when DDGS/DuckDuckGo is blocked on
        # managed hosting such as Streamlit Cloud.
        try:
            results = self._search_bing_html(query)
            if results:
                self.cache.put(query, results)
                return results, False
            errors.append("Bing returned no results")
        except Exception as exc:
            errors.append(f"Bing: {self._safe_error(exc)}")

        try:
            results = self._search_duckduckgo_html(query)
            if results:
                self.cache.put(query, results)
                return results, False

            errors.append("DuckDuckGo HTML returned no results")

        except Exception as exc:
            errors.append(f"DuckDuckGo HTML: {self._safe_error(exc)}")

        # Never cache an empty/failed lookup. Temporary network or provider
        # failures must be retried on the next investigation.
        raise RuntimeError(
            "Web search providers returned no usable results. "
            + " | ".join(errors)
        )

    @staticmethod
    def _clean_query(query: str) -> str:
        value = re.sub(r"\s+", " ", str(query or "")).strip()
        return value[:1200]

    @staticmethod
    def _normalize(items: list) -> list:
        output = []
        seen = set()

        for item in items or []:
            if not isinstance(item, dict):
                continue

            title = str(item.get("title") or "").strip()
            url = str(
                item.get("href")
                or item.get("url")
                or item.get("link")
                or ""
            ).strip()
            snippet = str(
                item.get("body")
                or item.get("snippet")
                or item.get("description")
                or ""
            ).strip()

            if not url.startswith(("http://", "https://")):
                continue

            key = url.lower()
            if key in seen:
                continue

            seen.add(key)
            output.append(
                {
                    "title": title or url,
                    "url": url,
                    "snippet": snippet,
                }
            )

        return output

    def _search_bing_html(self, query: str) -> list:
        import requests
        import xml.etree.ElementTree as ET

        url = "https://www.bing.com/search?format=rss&q=" + quote_plus(query)
        response = requests.get(
            url,
            timeout=12,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/131 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        response.raise_for_status()

        root = ET.fromstring(response.content)
        results = []

        for item in root.findall(".//item"):
            title = item.findtext("title") or ""
            link = item.findtext("link") or ""
            description = item.findtext("description") or ""

            if link:
                results.append(
                    {
                        "title": unescape(title).strip(),
                        "url": unescape(link).strip(),
                        "snippet": unescape(description).strip(),
                    }
                )

            if len(results) >= max(1, int(self.settings.max_web_results)):
                break

        return self._normalize(results)

    def _search_duckduckgo_html(self, query: str) -> list:
        import requests
        from html.parser import HTMLParser

        class ResultParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.results = []
                self._current = None
                self._capture = None

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                classes = set((attrs.get("class") or "").split())

                if tag == "a" and "result__a" in classes:
                    self._current = {
                        "title": "",
                        "url": attrs.get("href") or "",
                        "snippet": "",
                    }
                    self._capture = "title"

                elif self._current and "result__snippet" in classes:
                    self._capture = "snippet"

            def handle_data(self, data):
                if self._current and self._capture:
                    self._current[self._capture] += data

            def handle_endtag(self, tag):
                if self._current and tag == "a" and self._capture == "title":
                    self._capture = None
                elif self._current and self._capture == "snippet":
                    self.results.append(self._current)
                    self._current = None
                    self._capture = None

        url = "https://html.duckduckgo.com/html/?q=" + quote_plus(query)

        response = requests.get(
            url,
            timeout=12,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/131 Safari/537.36"
                )
            },
        )
        response.raise_for_status()

        parser = ResultParser()
        parser.feed(response.text)

        for item in parser.results:
            item["title"] = unescape(
                re.sub(r"\s+", " ", item["title"])
            ).strip()
            item["snippet"] = unescape(
                re.sub(r"\s+", " ", item["snippet"])
            ).strip()

        return self._normalize(parser.results)

    @staticmethod
    def _safe_error(exc: Exception) -> str:
        message = str(exc).lower()
        if "timeout" in message or "timed out" in message:
            return "provider timeout"
        if any(x in message for x in ("403", "429", "blocked", "forbidden")):
            return "search provider access/rate-limit error"
        return "search provider request error"
