"""Tests for the MatchMaker REST API extension"""

import requests
from scout.server.extensions import matchmaker


class MockNodesResponse(object):
    def __init__():
        self.status_code = 200

    def json(self):
        return [
            {"id": "node1", "description": "This is node 1"},
            {"id": "node2", "description": "This is node 2"},
        ]


def test_matchmaker_config_settings(matchmaker_app):
    """Test that the app is initialized with the correct MatchMaker Exchange settings"""
    # WHEN the app is initialized, it should contain the default MME parameters
    with matchmaker_app.app_context():
        assert matchmaker.host
        assert matchmaker.accept
        assert matchmaker.token
        assert matchmaker.connected_nodes == []


def test_nodes(monkeypatch):
    """Test the function that retrieves MME nodes connected to default MME instance"""

    # GIVEN a patched MatchMaker server
    def mock_get(*args, **kwargs):
        return MockNodesResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    # Calling the "nodes" endpoint should return a list of nodes
    assert isinstance(matchmaker.nodes(), list)
