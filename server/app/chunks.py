from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Chunk:
    heading: str | None
    content: str


_HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)


def chunk_markdown(title: str, body: str, max_chars: int = 1200) -> list[Chunk]:
    """Split Markdown by heading, then by paragraphs while carrying document context."""
    matches = list(_HEADING.finditer(body))
    sections = []
    if not matches:
        sections.append((None, body.strip()))
    else:
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
            sections.append((match.group(1).strip(), body[match.start():end].strip()))

    chunks: list[Chunk] = []
    prefix = f"{title.strip()}\n\n"
    for heading, section in sections:
        if not section:
            continue
        paragraphs = section.split("\n\n")
        current = ""
        for paragraph in paragraphs:
            proposed = f"{current}\n\n{paragraph}".strip()
            if current and len(prefix) + len(proposed) > max_chars:
                chunks.append(Chunk(heading=heading, content=prefix + current))
                current = paragraph
            else:
                current = proposed
        if current:
            chunks.append(Chunk(heading=heading, content=prefix + current))
    return chunks or [Chunk(heading=None, content=prefix + "(empty document)")]
