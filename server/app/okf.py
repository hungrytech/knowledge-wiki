from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
import re
from typing import Any

import yaml

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.DOTALL)
_LINK = re.compile(r"\[[^\]]+\]\(([^)]+\.md)\)")


@dataclass(frozen=True)
class Concept:
    id: str
    type: str
    title: str
    description: str | None
    tags: list[str]
    resource: str | None
    timestamp: str | None
    body: str
    links: list[str]
    title_ko: str | None = None
    description_ko: str | None = None
    body_ko: str | None = None


def _concept_id(path: str) -> str:
    pure_path = PurePosixPath(path)
    if pure_path.suffix != ".md":
        raise ValueError("OKF concept path must end in .md")
    return str(pure_path.with_suffix(""))


def _extract_links(concept_id: str, body: str) -> list[str]:
    result: list[str] = []
    parent = PurePosixPath(concept_id).parent
    for target in _LINK.findall(body):
        if "://" in target or target.startswith("mailto:"):
            continue
        target_path = target.split("#", 1)[0]
        if target_path.startswith("/"):
            resolved = PurePosixPath(target_path[1:]).with_suffix("")
        else:
            resolved = (parent / target_path).with_suffix("")
        normalized = str(resolved)
        while normalized.startswith("../"):
            normalized = normalized[3:]
        if normalized not in result:
            result.append(normalized)
    return result


def parse_concept(path: str, source: str) -> Concept:
    match = _FRONTMATTER.match(source)
    if not match:
        raise ValueError("OKF concept requires YAML frontmatter")
    metadata: dict[str, Any] = yaml.safe_load(match.group(1)) or {}
    concept_type = metadata.get("type")
    if not isinstance(concept_type, str) or not concept_type.strip():
        raise ValueError("OKF concept requires a non-empty type")
    body = match.group(2).strip()
    tags = metadata.get("tags") or []
    if not isinstance(tags, list):
        raise ValueError("tags must be a YAML list")
    concept_id = _concept_id(path)
    return Concept(
        id=concept_id,
        type=concept_type,
        title=str(metadata.get("title") or concept_id.rsplit("/", 1)[-1]),
        description=metadata.get("description"),
        tags=[str(tag) for tag in tags],
        resource=metadata.get("resource"),
        timestamp=metadata.get("timestamp"),
        body=body,
        links=_extract_links(concept_id, body),
        title_ko=metadata.get("title_ko"),
        description_ko=metadata.get("description_ko"),
        body_ko=metadata.get("body_ko"),
    )


def render_concept(concept: Concept) -> str:
    metadata: dict[str, Any] = {"type": concept.type, "title": concept.title}
    for key in ("description", "resource", "tags", "timestamp", "title_ko", "description_ko", "body_ko"):
        value = getattr(concept, key)
        if value not in (None, [], ""):
            metadata[key] = value
    frontmatter = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{frontmatter}\n---\n\n{concept.body.strip()}\n"
