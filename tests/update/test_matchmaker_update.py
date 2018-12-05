from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from threading import Thread
import requests
import re

from pathlib import Path
import json

from nose.tools import assert_true

from scout.parse.mme import mme_patients
from scout.update.matchmaker import mme_update

TOKEN = 'abcd'

# mock matchbox server to send responses when it get requests
class MockServerRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        self._set_headers()
        # return the simplest ok response:
        self.wfile.write(bytes("{\"status\": 200}", "utf-8"))

    def do_DELETE(self):
        self._set_headers()
        # return the simplest ok response:
        self.wfile.write(bytes("{\"status\": 200}", "utf-8"))


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


class TestMockMatchMakerServer(object):
    @classmethod
    def setup_class(cls):
        # Configure mock server.
        cls.mock_server_port = get_free_port()
        cls.mock_server = HTTPServer(('localhost', cls.mock_server_port), MockServerRequestHandler)

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()


    def test_add_patient(self, temp_json_file, matchmaker_patients):

        # collect mock json file
        assert temp_json_file

        # write test patient data to file
        with temp_json_file.open('w') as f:
            json.dump(matchmaker_patients, f)

        json_patients = mme_patients(Path(temp_json_file).resolve())

        # number of patients should be 2
        assert len(json_patients) == 2

        url = 'http://localhost:{port}'.format(port=self.mock_server_port)

        # for each patient
        for patient in json_patients:
            # send a POST request with patient data
            response = mme_update( matchmaker_url=url, update_action='add', json_patient=patient, token=TOKEN)
            assert response['status'] == 200


    def test_delete_patient(self):

        # much easier, just send a DELETE request with the patient ID
        url = 'http://localhost:{port}'.format(port=self.mock_server_port)

        response = mme_update( matchmaker_url=url, update_action='delete', json_patient='patient_id', token=TOKEN)
        assert response['status'] == 200
