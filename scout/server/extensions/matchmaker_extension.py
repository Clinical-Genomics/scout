"""Code for MatchMaker Exchange integration
   Tested with PatientMatcher: https://github.com/Clinical-Genomics/patientMatcher
"""
import logging
import datetime
from scout.utils.scout_requests import get_request_json, post_request_json
from werkzeug.datastructures import Headers

LOG = logging.getLogger(__name__)


class MatchMaker:
    """Interface to a MatchMaker Exchange server instance, reachable via REST API"""

    def __init__(self):
        self.host = None
        self.accept = None
        self.token = None

    def init_app(self, app):
        """Initialize the MatchMaker extension and make its parametars available to the app."""
        self.host = app.config.get("MME_URL")
        self.accept = app.config.get("MME_ACCEPTS")
        self.token = app.config.get("MME_TOKEN")
        self.connected_nodes = (
            self.nodes()
        )  # external MatchMaker nodes connected to default MME instance

    def request(self, url, method, content_type=None, accept=None, data=None):
        """Send a request to MatchMaker and return its response

        Args:
            url(str): url to send request to
            method(str): 'GET', 'POST' or 'DELETE'
            content_type(str): example application/json
            accept(str): application/vnd.ga4gh.matchmaker.v1.0+json or application/json
            data(dict): eventual data to send in request

        Returns:
            json_response(dict): server response
        """
        headers = Headers()
        headers = {"X-Auth-Token": self.token}

        if content_type:
            headers["Content-Type"] = content_type or self.accept
        if accept:
            headers["Accept"] = accept or self.accept

        # sending data anyway so response will not be cached
        req_data = data or {"timestamp": datetime.datetime.now().timestamp()}
        json_response = None

        if method == "GET":
            json_response = get_request_json(url=url, headers=headers)
        elif method == "POST":
            json_response = post_request_json(url=url, headers=headers, data=req_data)

        return json_response

    def nodes(self):
        """Retrieve all MatchMaker nodes connected to the one described in the config file.

        Returns:
            nodes(list): a list of node disctionaries
        """
        nodes = []
        url = url = "".join([self.host, "/nodes"])
        mme_response = self.request(url=url, method="GET", accept="application/json")
        nodes = mme_response.get("content") or []
        return nodes
