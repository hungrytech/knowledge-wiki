from app.catalog import semantic_ids, sync_catalog
from app.okf import Concept


class Cursor:
    def __init__(self): self.calls = []; self.rows = []
    def execute(self, sql, params=None): self.calls.append((sql, params))
    def fetchall(self): return self.rows
    def __enter__(self): return self
    def __exit__(self, *_): pass


class Connection:
    def __init__(self): self.cursor_instance = Cursor(); self.committed = False
    def cursor(self): return self.cursor_instance
    def commit(self): self.committed = True
    def __enter__(self): return self
    def __exit__(self, *_): pass


def test_sync_catalog_projects_okf_concepts_and_links(monkeypatch):
    connection = Connection()
    monkeypatch.setattr('app.catalog.psycopg.connect', lambda _: connection)
    concepts = [Concept('concepts/rag', 'Concept', 'RAG', 'Retrieval', ['rag'], None, None, 'Links [pgvector](/concepts/pgvector.md).', ['concepts/pgvector'])]

    sync_catalog('postgresql://example', concepts)

    statements = [call[0] for call in connection.cursor_instance.calls]
    assert any('INSERT INTO documents' in statement for statement in statements)
    assert any('INSERT INTO links' in statement for statement in statements)
    assert connection.committed is True
    assert any('DELETE FROM documents' in statement for statement in statements)


def test_sync_catalog_persists_local_embedding_vectors(monkeypatch):
    connection = Connection()
    monkeypatch.setattr('app.catalog.psycopg.connect', lambda _: connection)
    concepts = [Concept('concepts/rag', 'Concept', 'RAG', 'Retrieval', ['rag'], None, None, 'Search context.', [])]

    sync_catalog('postgresql://example', concepts, embed=lambda _: [[0.1, 0.2]])

    document_call = next(call for call in connection.cursor_instance.calls if 'INSERT INTO documents' in call[0])
    assert 'embedding' in document_call[0]
    assert '[0.1,0.2]' in document_call[1]


def test_semantic_ids_orders_by_pgvector_distance(monkeypatch):
    connection = Connection()
    connection.cursor_instance.rows = [("concepts/okf",), ("concepts/pgvector",)]
    monkeypatch.setattr('app.catalog.psycopg.connect', lambda _: connection)

    ids = semantic_ids('postgresql://example', [0.1, 0.2], limit=5)

    assert ids == ["concepts/okf", "concepts/pgvector"]
    assert '<=>' in connection.cursor_instance.calls[0][0]
