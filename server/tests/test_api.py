from fastapi.testclient import TestClient

from app.main import create_app


def _write_concept(root, relative_path, text):
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def test_api_lists_documents_exposes_graph_search_and_ingests_okf(tmp_path):
    _write_concept(
        tmp_path,
        "concepts/rag.md",
        """---
type: Concept
title: RAG
description: Retrieval pattern
tags: [rag]
---

# Overview

Uses [pgvector](/concepts/pgvector.md).
""",
    )
    _write_concept(
        tmp_path,
        "concepts/pgvector.md",
        """---
type: Concept
title: pgvector
description: Vector extension
tags: [database, rag]
---

# Overview

Vector search for PostgreSQL.
""",
    )
    client = TestClient(create_app(tmp_path))

    health = client.get("/api/health")
    documents = client.get("/api/documents")
    graph = client.get("/api/graph")
    search = client.get("/api/search", params={"q": "vector"})
    ingested = client.post(
        "/api/documents",
        json={
            "type": "Source",
            "title": "OKF launch",
            "description": "Official announcement",
            "tags": ["okf"],
            "resource": "https://cloud.google.com/blog/okf",
            "body": "# Notes\n\n[Related](/concepts/rag.md)",
        },
    )

    assert health.json() == {"status": "ok"}
    assert [item["id"] for item in documents.json()] == ["concepts/pgvector", "concepts/rag"]
    assert graph.json()["edges"] == [{"source": "concepts/rag", "target": "concepts/pgvector"}]
    assert [item["id"] for item in search.json()] == ["concepts/pgvector", "concepts/rag"]
    assert ingested.status_code == 201
    assert ingested.json()["id"] == "sources/okf-launch"
    assert (tmp_path / "sources/okf-launch.md").exists()


def test_api_ingests_a_url_as_an_okf_source_with_provenance(tmp_path):
    client = TestClient(create_app(tmp_path, url_fetcher=lambda _: ("Example article", "# Article\n\nSource body.")))

    response = client.post("/api/ingest-url", json={"url": "https://example.com/article"})

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"] == "sources/example-article"
    assert payload["type"] == "Source"
    assert payload["resource"] == "https://example.com/article"
    assert "source_hash" in (tmp_path / "sources/example-article.md").read_text(encoding="utf-8")


def test_api_semantic_search_uses_local_embeddings_and_pgvector_ids(tmp_path, monkeypatch):
    _write_concept(tmp_path, "concepts/pgvector.md", "---\ntype: Concept\ntitle: pgvector\n---\n\nVector search.")
    monkeypatch.setenv("DATABASE_URL", "postgresql://example")
    monkeypatch.setattr("app.main.sync_catalog", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("app.main.semantic_ids", lambda *_args, **_kwargs: ["concepts/pgvector"])

    class Embedder:
        def encode(self, texts, query=False):
            assert texts == ["한국어 벡터 검색"]
            assert query is True
            return [[0.1, 0.2]]

    with TestClient(create_app(tmp_path, embedder=Embedder())) as client:
        response = client.get("/api/semantic-search", params={"q": "한국어 벡터 검색"})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == ["concepts/pgvector"]
