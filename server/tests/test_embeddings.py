from app.embeddings import prepare_e5_inputs


def test_prepare_e5_inputs_applies_retrieval_prefixes():
    assert prepare_e5_inputs(["한국어 지식 문서"], query=False) == ["passage: 한국어 지식 문서"]
    assert prepare_e5_inputs(["벡터 검색이란?"], query=True) == ["query: 벡터 검색이란?"]
