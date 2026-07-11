from app.sources import title_from_markdown


def test_title_from_markdown_uses_first_heading_for_raw_markdown_sources():
    assert title_from_markdown("# Open Knowledge Format (OKF)\n\nSpecification body.") == "Open Knowledge Format (OKF)"
