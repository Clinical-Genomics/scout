# -*- coding: utf-8 -*-
from scout.server.extensions import store


def test_collection_stats(mock_app):
    """test the function that returns the stats for a database collection"""

    with mock_app.app_context():
        stats = store.collection_stats("case")
        assert "avgObjSize" in stats
