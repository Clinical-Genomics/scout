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
