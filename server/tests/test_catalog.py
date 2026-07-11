from app.catalog import sync_catalog
from app.okf import Concept


class Cursor:
    def __init__(self): self.calls = []
    def execute(self, sql, params=None): self.calls.append((sql, params))
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
