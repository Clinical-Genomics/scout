import requests
from scout.utils.matchmaker import mme_nodes


def test_mme_nodes(monkeypatch):
    """ Test the function that returns the connected MatchMaker nodes """

    # GIVEN a monkeypatched connection to a MME server connected with 2 other nodes
    class MockResponse(object):
        def __init__(self):
            self.status_code = 200

        def json(self):
            return [
                {"id": "node1", "description": "This is node 1"},
                {"id": "node2", "description": "This is node 2"},
            ]

    def mock_request(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "request", mock_request)

    # WHEN Scout asks for connected nodes
    mme_base_url = "fakeynode.se"
    token = "test_token"
    nodes = mme_nodes(mme_base_url, token)
    # Then 2 nodes should be returned
    assert len(nodes) == 2
