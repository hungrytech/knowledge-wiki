"""Derived Neo4j projection for the Markdown-owned Knowledge Wiki.

The projection intentionally contains graph metadata only. Full document content and
embeddings remain in the local Markdown bundle and PostgreSQL/pgvector respectively.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Protocol

from .okf import Concept


class Neo4jSession(Protocol):
    def run(self, query: str, **params: Any) -> Any: ...

    def __enter__(self) -> "Neo4jSession": ...

    def __exit__(self, *_: Any) -> bool: ...


class Neo4jDriver(Protocol):
    def session(self, **kwargs: Any) -> Neo4jSession: ...


def graph_records(concepts: Iterable[Concept]) -> dict[str, list[dict[str, Any]]]:
    """Return deterministic, metadata-only records with links confined to this corpus."""
    ordered = sorted(concepts, key=lambda concept: concept.id)
    known_ids = {concept.id for concept in ordered}
    documents = [
        {
            "id": concept.id,
            "title": concept.title,
            "description": concept.description,
            "type": concept.type,
            "tags": sorted(set(concept.tags)),
            "resource": concept.resource,
            "timestamp": concept.timestamp,
            "links": sorted({target for target in concept.links if target in known_ids}),
        }
        for concept in ordered
    ]
    return {"documents": documents}
class Neo4jDriverFactory(Protocol):
    def __call__(self, uri: str, *, auth: tuple[str, str]) -> Neo4jDriver: ...


def create_projection(
    uri: str,
    username: str,
    password: str,
    *,
    driver_factory: Neo4jDriverFactory | None = None,
) -> "Neo4jGraphProjection":
    """Create the official driver lazily so local unit tests need no Neo4j package."""
    if driver_factory is None:
        from neo4j import GraphDatabase

        driver_factory = GraphDatabase.driver
    return Neo4jGraphProjection(driver=driver_factory(uri, auth=(username, password)))


class Neo4jGraphProjection:
    """Idempotently rebuild the graph namespace owned by this Wiki only."""

    def __init__(self, driver: Neo4jDriver, graph_key: str = "knowledge-wiki"):
        self.driver = driver
        self.graph_key = graph_key

    def sync(self, concepts: Iterable[Concept]) -> None:
        records = graph_records(concepts)
        documents = records["documents"]
        with self.driver.session() as session:
            session.run(
                "MATCH (node {graph: $graph}) DETACH DELETE node",
                graph=self.graph_key,
            )
            session.run(
                """
                UNWIND $documents AS doc
                CREATE (:Document {
                  graph: $graph, id: doc.id, title: doc.title,
                  description: doc.description, type: doc.type, resource: doc.resource,
                  timestamp: doc.timestamp
                })
                """,
                graph=self.graph_key,
                documents=documents,
            )
            session.run(
                """
                UNWIND $documents AS doc
                MATCH (document:Document {graph: $graph, id: doc.id})
                MERGE (type:DocumentType {graph: $graph, name: doc.type})
                MERGE (document)-[:HAS_TYPE]->(type)
                WITH document, doc
                UNWIND doc.tags AS tag_name
                MERGE (tag:Tag {graph: $graph, name: tag_name})
                MERGE (document)-[:TAGGED_WITH]->(tag)
                """,
                graph=self.graph_key,
                documents=documents,
            )
            session.run(
                """
                UNWIND $documents AS doc
                UNWIND doc.links AS target_id
                MATCH (source:Document {graph: $graph, id: doc.id})
                MATCH (target:Document {graph: $graph, id: target_id})
                MERGE (source)-[:LINKS_TO {graph: $graph}]->(target)
                """,
                graph=self.graph_key,
                documents=documents,
            )

    def graph(self) -> dict[str, list[dict[str, Any]] | str]:
        with self.driver.session() as session:
            nodes = session.run(
                """
                MATCH (doc:Document {graph: $graph})
                OPTIONAL MATCH (doc)-[:TAGGED_WITH]->(tag:Tag {graph: $graph})
                WITH doc, collect(tag.name) AS tags
                RETURN doc.id AS id, doc.title AS label, doc.type AS type, tags
                ORDER BY id
                """,
                graph=self.graph_key,
            ).data()
            edges = session.run(
                """
                MATCH (source:Document {graph: $graph})-[:LINKS_TO]->(target:Document {graph: $graph})
                RETURN source.id AS source, target.id AS target
                ORDER BY source, target
                """,
                graph=self.graph_key,
            ).data()
        return {"source": "neo4j", "nodes": nodes, "edges": edges}
