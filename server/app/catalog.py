from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Sequence

import psycopg

from .okf import Concept


def _vector_literal(vector: list[float] | None) -> str | None:
    if vector is None:
        return None
    return "[" + ",".join(str(value) for value in vector) + "]"


def _concept_text(concept: Concept) -> str:
    return "\n".join(part for part in [concept.title, concept.title_ko or "", concept.description or "", concept.description_ko or "", concept.body, concept.body_ko or ""] if part)


def fuse_ranked_ids(*rankings: Sequence[str], limit: int = 10, k: int = 60) -> list[str]:
    """Fuse independently ranked document IDs with reciprocal rank fusion."""
    scores: dict[str, float] = defaultdict(float)
    first_seen: dict[str, int] = {}
    for ranking in rankings:
        for rank, document_id in enumerate(ranking):
            scores[document_id] += 1 / (k + rank + 1)
            first_seen.setdefault(document_id, len(first_seen))
    ordered = sorted(scores, key=lambda document_id: (-scores[document_id], first_seen[document_id]))
    return ordered[:limit]


def sync_catalog(
    database_url: str,
    concepts: list[Concept],
    embed: Callable[[list[str]], list[list[float]]] | None = None,
) -> None:
    """Project filesystem-owned OKF data into the local PostgreSQL catalog."""
    vectors = embed([_concept_text(concept) for concept in concepts]) if embed and concepts else [None] * len(concepts)
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM links")
            cursor.execute("DELETE FROM documents WHERE NOT (id = ANY(%s))", ([concept.id for concept in concepts],))
            for concept, vector in zip(concepts, vectors, strict=True):
                cursor.execute(
                    """
                    INSERT INTO documents (id, type, title, description, tags, resource, timestamp, body, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
                    ON CONFLICT (id) DO UPDATE SET
                      type = EXCLUDED.type, title = EXCLUDED.title,
                      description = EXCLUDED.description, tags = EXCLUDED.tags,
                      resource = EXCLUDED.resource, timestamp = EXCLUDED.timestamp,
                      body = EXCLUDED.body, embedding = EXCLUDED.embedding, indexed_at = NOW()
                    """,
                    (concept.id, concept.type, concept.title, concept.description, concept.tags, concept.resource, concept.timestamp, concept.body, _vector_literal(vector)),
                )
                for target in concept.links:
                    cursor.execute(
                        "INSERT INTO links (source_id, target_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        (concept.id, target),
                    )
        connection.commit()


def semantic_ids(database_url: str, query_vector: list[float], limit: int = 10) -> list[str]:
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM documents WHERE embedding IS NOT NULL ORDER BY embedding <=> %s::vector LIMIT %s",
                (_vector_literal(query_vector), limit),
            )
            return [row[0] for row in cursor.fetchall()]
