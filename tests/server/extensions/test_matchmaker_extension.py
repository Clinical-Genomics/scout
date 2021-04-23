"""Tests for the MatchMaker REST API extension"""

import uuid

from scout.server.app import create_app
from scout.server.extensions import matchmaker


class MockNodesResponse(object):
    def __init__():
        self.status_code = 200

    def json(self):
        return [
            {"id": "node1", "description": "This is node 1"},
            {"id": "node2", "description": "This is node 2"},
        ]


def test_matchmaker_config_settings(mocker):
    """Test that the app is initialized with the correct MatchMaker Exchange settings"""
    # WHEN the app is initialized, it should contain the default MME parameters

    # GIVEN a patched MatchMaker server returning a list of connected nodes:
    nodes = [
        {"description": "Node 1", "id": "node1"},
        {"description": "Node 2", "id": "node2"},
    ]
    mocker.patch(
        "scout.utils.scout_requests.get_request_json",
        return_value={"status_code": 200, "content": nodes},
    )

    # WHEN app is created
    test_app = create_app(
        config=dict(
            TESTING=True,
            MME_URL="test_matchmaker.com",
            MME_ACCEPTS="application/vnd.ga4gh.matchmaker.v1.0+json",
            MME_TOKEN=str(uuid.uuid4()),
        )
    )
    # THEN it should contain the expected matchmaker class attributes:
    with test_app.app_context():
        assert matchmaker.host
        assert matchmaker.accept
        assert matchmaker.token
        assert matchmaker.connected_nodes == nodes
