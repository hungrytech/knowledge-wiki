from __future__ import annotations

import psycopg

from .okf import Concept


def sync_catalog(database_url: str, concepts: list[Concept]) -> None:
    """Project filesystem-owned OKF data into the local PostgreSQL catalog."""
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM links")
            for concept in concepts:
                cursor.execute(
                    """
                    INSERT INTO documents (id, type, title, description, tags, resource, timestamp, body)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                      type = EXCLUDED.type, title = EXCLUDED.title,
                      description = EXCLUDED.description, tags = EXCLUDED.tags,
                      resource = EXCLUDED.resource, timestamp = EXCLUDED.timestamp,
                      body = EXCLUDED.body, indexed_at = NOW()
                    """,
                    (concept.id, concept.type, concept.title, concept.description, concept.tags, concept.resource, concept.timestamp, concept.body),
                )
                for target in concept.links:
                    cursor.execute(
                        "INSERT INTO links (source_id, target_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        (concept.id, target),
                    )
        connection.commit()
