def test_app_human_longint_filter_non_numeric_str(mock_app):
    """Test template filter human_longint when the provided string is 'inf'."""
    assert "human_longint" in mock_app.jinja_env.filters.keys()
    assert mock_app.jinja_env.filters["human_longint"]("inf") == "inf"


def test_app_human_longint_filter_str(mock_app):
    """Test template filter human_longint when the provided string represents a long number."""
    assert "human_longint" in mock_app.jinja_env.filters.keys()
    assert mock_app.jinja_env.filters["human_longint"]("100000") == "100&thinsp;000"


def test_app_human_longint_filter_number(mock_app):
    """Test template filter human_longint with a long integer."""
    assert "human_longint" in mock_app.jinja_env.filters.keys()
    assert mock_app.jinja_env.filters["human_longint"](100000) == "100&thinsp;000"


def test_app_url_args_filter(mock_app):
    """Test the template filter with a URL to parse."""
    # GIVEN a URL as it would be saved in events collection
    url = "/cust000/643594/sv/variants?category=sv&display_name=SVs_clinical&page=1&variant_type=clinical&gene_panels=panel1&_id=65645ef376be6591e1f72cf3"

    # THEN url_args filter should parse and return the link query arguments as a dictionary:
    parsed_url: dict = mock_app.jinja_env.filters["url_args"](url)
    assert isinstance(parsed_url, dict)
    assert parsed_url["category"]
    assert parsed_url["variant_type"]
