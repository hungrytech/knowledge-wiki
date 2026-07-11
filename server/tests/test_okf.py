from app.okf import Concept, parse_concept, render_concept


def test_parse_concept_reads_required_type_and_markdown_links():
    source = """---
type: Concept
title: pgvector
description: PostgreSQL vector search
tags: [rag, database]
---

# Overview

See [RAG](/concepts/rag.md) and [Local](./local.md).
"""

    concept = parse_concept("concepts/pgvector.md", source)

    assert concept.id == "concepts/pgvector"
    assert concept.type == "Concept"
    assert concept.title == "pgvector"
    assert concept.tags == ["rag", "database"]
    assert concept.links == ["concepts/rag", "concepts/local"]


def test_parse_concept_ignores_external_markdown_urls():
    concept = parse_concept("concepts/okf.md", "---\ntype: Concept\n---\n\n[spec](https://example.com/SPEC.md)")

    assert concept.links == []


def test_render_concept_emits_okf_frontmatter_and_body():
    concept = Concept(
        id="concepts/rag",
        type="Concept",
        title="RAG",
        description="Retrieval augmented generation",
        tags=["rag"],
        resource=None,
        timestamp="2026-07-11T00:00:00Z",
        body="# Overview\n\nSearch before answering.",
        links=[],
    )

    rendered = render_concept(concept)

    assert rendered.startswith("---\ntype: Concept\ntitle: RAG")
    assert "tags:\n- rag" in rendered
    assert rendered.endswith("# Overview\n\nSearch before answering.\n")


def test_parse_concept_rejects_missing_type():
    source = "---\ntitle: Missing type\n---\n\nBody"

    try:
        parse_concept("concepts/bad.md", source)
    except ValueError as error:
        assert "type" in str(error)
    else:
        raise AssertionError("Expected missing type to be rejected")
