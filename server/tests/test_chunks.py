from app.chunks import chunk_markdown


def test_chunk_markdown_preserves_heading_context_and_respects_max_size():
    body = "# Targeting\n\nRules choose an audience.\n\n# SDKs\n\nClients evaluate flags locally."

    chunks = chunk_markdown("Feature flags", body, max_chars=80)

    assert [chunk.heading for chunk in chunks] == ["Targeting", "SDKs"]
    assert chunks[0].content == "Feature flags\n\n# Targeting\n\nRules choose an audience."
    assert chunks[1].content == "Feature flags\n\n# SDKs\n\nClients evaluate flags locally."
