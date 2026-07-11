from __future__ import annotations

import ipaddress
import re
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        if self._in_title:
            self.title += text
        self.parts.append(text)


def _validate_public_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only absolute http(s) URLs are supported")
    if parsed.hostname == "localhost":
        raise ValueError("Local URLs are not allowed")
    try:
        address = ipaddress.ip_address(parsed.hostname)
    except ValueError:
        return
    if not address.is_global:
        raise ValueError("Private network URLs are not allowed")


def title_from_markdown(body: str) -> str | None:
    match = re.search(r"^#\s+(.+?)\s*$", body, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def fetch_url(url: str) -> tuple[str, str]:
    _validate_public_url(url)
    response = httpx.get(url, follow_redirects=True, timeout=20, headers={"User-Agent": "KnowledgeWiki/0.1"})
    response.raise_for_status()
    markdown = response.text
    if str(response.url).split("?", 1)[0].endswith(".md") or "text/markdown" in response.headers.get("content-type", ""):
        title = title_from_markdown(markdown) or urlparse(str(response.url)).hostname or "Untitled source"
        return title, markdown
    parser = _TextExtractor()
    parser.feed(markdown)
    title = parser.title or urlparse(str(response.url)).hostname or "Untitled source"
    body = "\n\n".join(parser.parts)
    return title, body
