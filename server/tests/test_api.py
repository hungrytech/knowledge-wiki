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
