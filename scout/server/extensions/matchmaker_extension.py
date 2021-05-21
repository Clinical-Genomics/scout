"""Code for MatchMaker Exchange integration
   Tested with PatientMatcher: https://github.com/Clinical-Genomics/patientMatcher
"""
import datetime
import json
import logging

from werkzeug.datastructures import Headers

from scout.utils import scout_requests

LOG = logging.getLogger(__name__)


class MatchMaker:
    """Interface to a MatchMaker Exchange server instance, reachable via REST API"""

    def __init__(self):
        self.host = None
        self.accept = None
        self.token = None
        self.connected_nodes = None

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
            headers["Content-Type"] = content_type
        if accept:
            headers["Accept"] = accept

        # sending data anyway so response will not be cached
        req_data = data or {"timestamp": datetime.datetime.now().timestamp()}
        json_response = None

        if method == "GET":
            json_response = scout_requests.get_request_json(url=url, headers=headers)
        elif method == "DELETE":
            json_response = scout_requests.delete_request_json(url=url, headers=headers)
        elif method == "POST":
            json_response = scout_requests.post_request_json(
                url=url, headers=headers, data=req_data
            )

        return json_response

    def nodes(self):
        """Retrieve all MatchMaker nodes connected to the one described in the config file.

        Returns:
            nodes(list): a list of node disctionaries
        """
        nodes = []
        url = "".join([self.host, "/nodes"])
        resp = self.request(url=url, method="GET", accept="application/json")
        nodes = resp.get("content") or []
        return nodes

    def patient_delete(self, patient_id):
        """Send a DELETE request to MatchMaker server to delete a patient.

        Args:
            patient_id(str): ID of patient to remove from MatchMaker

        Returns:
            server_resp(dict): json-formatted response from server
        """
        url = "".join([self.host, "/patient/delete/", patient_id])
        resp = self.request(url=url, method="DELETE")
        return resp

    def patient_submit(self, patient_obj):
        """Send a POST request with a patient to the MatchMaker add endpoint

        Args:
            patient_obj(dict): a dictionary corresponding to a patient object to save/update

        Return:
            resp(dict): Response from server converted to dictionary
        """
        url = "".join([self.host, "/patient/add"])
        resp = self.request(
            url=url,
            method="POST",
            accept="application/json",
            content_type="application/json",
            data={"patient": patient_obj},
        )
        return resp

    def patient_matches(self, patient_id):
        """Return all matches for a given patient ID

        Args:
            patient_id(str): ID of a patient

        Returns:
            resp(dict)
        """
        url = "".join([self.host, "/matches/", patient_id])
        resp = self.request(url=url, method="GET", accept="application/json")
        return resp

    def match_internal(self, patient_obj):
        """Match a patient dictionary againt all patients on the server

        Args:
            patient_obj(dict): a dictionary corresponding to a patient object to match

        """
        url = "".join([self.host, "/match"])
        resp = self.request(
            url=url,
            method="POST",
            accept=self.accept,
            content_type=self.accept,
            data={"patient": patient_obj},
        )
        return resp

    def match_external(self, patient_id, node_id):
        """Match a patient dictionary agaist one external node

        Args:
            patient_id(str): ID string of a patient already on the server
            node_id(str): ID string of a connected node
        """
        url = "".join([self.host, "/match/external/", patient_id, "?node=", node_id])
        resp = self.request(url=url, method="POST")
        return resp
