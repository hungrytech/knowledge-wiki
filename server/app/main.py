from __future__ import annotations

import hashlib
import os
from collections.abc import Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import yaml
import httpx

from .catalog import semantic_ids, sync_catalog
from .embeddings import LocalEmbedder
from .okf import Concept, parse_concept, render_concept
from .sources import fetch_url


def load_concepts(root: Path) -> list[Concept]:
    concepts: list[Concept] = []
    for path in root.rglob("*.md"):
        if path.name in {"index.md", "log.md"}:
            continue
        concepts.append(parse_concept(path.relative_to(root).as_posix(), path.read_text(encoding="utf-8")))
    return sorted(concepts, key=lambda item: item.id)


def concept_slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "untitled"


class IngestRequest(BaseModel):
    type: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str | None = None
    tags: list[str] = []
    resource: str | None = None
    body: str = Field(min_length=1)


class UrlIngestRequest(BaseModel):
    url: str = Field(min_length=1)


def create_app(
    wiki_root: Path | None = None,
    url_fetcher: Callable[[str], tuple[str, str]] = fetch_url,
    embedder: LocalEmbedder | None = None,
) -> FastAPI:
    root = wiki_root or Path(os.environ.get("WIKI_ROOT", str(Path.cwd().parent / "data/wiki")))
    root.mkdir(parents=True, exist_ok=True)
    database_url = os.environ.get("DATABASE_URL")
    local_embedder = embedder or (LocalEmbedder() if database_url else None)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if database_url:
            sync_catalog(database_url, load_concepts(root), embed=local_embedder.encode if local_embedder else None)
        yield

    app = FastAPI(title="Knowledge Wiki API", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_origin_regex=r"^https?://(?:localhost|127\.0\.0\.1|100\.\d{1,3}\.\d{1,3}\.\d{1,3}|[a-z0-9-]+\.tail42a834\.ts\.net)(?::\d+)?$",
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/documents")
    def documents() -> list[dict]:
        return [concept.__dict__ for concept in load_concepts(root)]

    @app.get("/api/graph")
    def graph() -> dict[str, list[dict]]:
        concepts = load_concepts(root)
        ids = {concept.id for concept in concepts}
        return {
            "nodes": [{"id": concept.id, "label": concept.title, "type": concept.type, "tags": concept.tags} for concept in concepts],
            "edges": [
                {"source": concept.id, "target": target}
                for concept in concepts
                for target in concept.links
                if target in ids
            ],
        }

    @app.get("/api/search")
    def search(q: str) -> list[dict]:
        needle = q.casefold().strip()
        if not needle:
            return []
        return [
            concept.__dict__
            for concept in load_concepts(root)
            if needle in " ".join([concept.title, concept.description or "", " ".join(concept.tags), concept.body]).casefold()
        ]

    @app.get("/api/semantic-search")
    def semantic_search(q: str, limit: int = 10) -> list[dict]:
        if not q.strip():
            return []
        if not database_url or not local_embedder:
            raise HTTPException(status_code=503, detail="Semantic index is not configured")
        ids = semantic_ids(database_url, local_embedder.encode([q], query=True)[0], limit=max(1, min(limit, 50)))
        concepts = {concept.id: concept for concept in load_concepts(root)}
        return [concepts[concept_id].__dict__ for concept_id in ids if concept_id in concepts]

    @app.post("/api/documents", status_code=201)
    def ingest(payload: IngestRequest) -> dict:
        directory = re.sub(r"[^a-z0-9]+", "-", payload.type.lower()).strip("-") + "s"
        relative = f"{directory}/{concept_slug(payload.title)}.md"
        target = root / relative
        if target.exists():
            raise HTTPException(status_code=409, detail="A concept with this title already exists")
        concept = Concept(
            id=relative[:-3],
            type=payload.type,
            title=payload.title,
            description=payload.description,
            tags=payload.tags,
            resource=payload.resource,
            timestamp=datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            body=payload.body,
            links=[],
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_concept(concept), encoding="utf-8")
        saved = parse_concept(relative, target.read_text(encoding="utf-8"))
        if database_url:
            sync_catalog(database_url, load_concepts(root), embed=local_embedder.encode if local_embedder else None)
        return saved.__dict__

    @app.post("/api/ingest-url", status_code=201)
    def ingest_url(payload: UrlIngestRequest) -> dict:
        try:
            title, body = url_fetcher(payload.url)
        except (ValueError, httpx.HTTPError) as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        relative = f"sources/{concept_slug(title)}.md"
        target = root / relative
        if target.exists():
            raise HTTPException(status_code=409, detail="This URL title has already been ingested")
        timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        metadata = {
            "type": "Source", "title": title, "description": f"Raw source captured from {payload.url}",
            "resource": payload.url, "timestamp": timestamp,
            "source_hash": f"sha256:{hashlib.sha256(body.encode('utf-8')).hexdigest()}",
        }
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"---\n{yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).strip()}\n---\n\n{body.strip()}\n", encoding="utf-8")
        saved = parse_concept(relative, target.read_text(encoding="utf-8"))
        if database_url:
            sync_catalog(database_url, load_concepts(root), embed=local_embedder.encode if local_embedder else None)
        return saved.__dict__

    return app


app = create_app()
