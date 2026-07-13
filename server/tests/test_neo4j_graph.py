from types import SimpleNamespace

import pytest

from app.neo4j_graph import Neo4jGraphProjection, graph_records


def concept(identifier: str, *, links=(), tags=(), type="Concept"):
    return SimpleNamespace(
        id=identifier,
        title=identifier.rsplit("/", 1)[-1],
        description="test document",
        type=type,
        tags=list(tags),
        resource=None,
        timestamp=None,
        links=list(links),
    )


def test_graph_records_keep_only_internal_known_links_and_metadata():
    records = graph_records(
        [
            concept("concepts/rag", links=["concepts/pgvector", "https://example.com"], tags=["rag", "search"]),
            concept("concepts/pgvector", tags=["database"]),
        ]
    )

    assert records["documents"] == [
        {
            "id": "concepts/pgvector",
            "title": "pgvector",
            "description": "test document",
            "type": "Concept",
            "tags": ["database"],
            "resource": None,
            "timestamp": None,
            "links": [],
        },
        {
            "id": "concepts/rag",
            "title": "rag",
            "description": "test document",
            "type": "Concept",
            "tags": ["rag", "search"],
            "resource": None,
            "timestamp": None,
            "links": ["concepts/pgvector"],
        },
    ]


class RecordingSession:
    def __init__(self):
        self.calls = []

    def run(self, query, **params):
        self.calls.append((query, params))
        return []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class RecordingDriver:
    def __init__(self):
        self.session_instance = RecordingSession()

    def session(self, **_):
        return self.session_instance


def test_projection_rebuilds_only_its_own_graph_namespace():
    driver = RecordingDriver()
    projection = Neo4jGraphProjection(driver=driver, graph_key="knowledge-wiki")

    projection.sync([concept("concepts/rag", tags=["rag"])])

    query, params = driver.session_instance.calls[0]
    assert "MATCH (node {graph: $graph}) DETACH DELETE node" in query
    assert params == {"graph": "knowledge-wiki"}
    assert len(driver.session_instance.calls) == 4
    assert any("[:LINKS_TO {graph: $graph}]" in query for query, _ in driver.session_instance.calls)


def test_projection_graph_uses_neo4j_document_and_link_records():
    class Result:
        def __init__(self, rows):
            self.rows = rows

        def data(self):
            return self.rows

    class ReadSession(RecordingSession):
        def run(self, query, **params):
            self.calls.append((query, params))
            if "RETURN doc.id AS id" in query:
                return Result([{"id": "concepts/rag", "label": "RAG", "type": "Concept", "tags": ["rag"]}])
            return Result([{"source": "concepts/rag", "target": "concepts/pgvector"}])

    driver = RecordingDriver()
    driver.session_instance = ReadSession()
    projection = Neo4jGraphProjection(driver=driver)

    assert projection.graph() == {
        "source": "neo4j",
        "nodes": [{"id": "concepts/rag", "label": "RAG", "type": "Concept", "tags": ["rag"]}],
        "edges": [{"source": "concepts/rag", "target": "concepts/pgvector"}],
    }


def test_projection_factory_uses_bolt_uri_and_authentication():
    calls = []

    def factory(uri, auth):
        calls.append((uri, auth))
        return RecordingDriver()

    from app.neo4j_graph import create_projection

    projection = create_projection("bolt://neo4j:7687", "neo4j", "private-password", driver_factory=factory)

    assert isinstance(projection, Neo4jGraphProjection)
    assert calls == [("bolt://neo4j:7687", ("neo4j", "private-password"))]
