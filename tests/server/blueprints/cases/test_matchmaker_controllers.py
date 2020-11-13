from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from threading import Thread
import requests
import pymongo

from scout.server.blueprints.cases import controllers
from scout.parse.matchmaker import genomic_features, omim_terms, hpo_terms

MME_ACCEPTS = "application/vnd.ga4gh.matchmaker.v1.0+json"
MME_TOKEN = "test_token"

# mock matchmaker server to send responses when it get requests
class MockServerRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def _send_ok(self):
        self._set_headers()
        # return the simplest ok response:
        self.wfile.write(bytes('{"status_code": 200}', "utf-8"))

    def do_POST(self):
        self._send_ok()

    def do_DELETE(self):
        self._send_ok()

    def do_GET(self, match_objs):  # mocks get MME matches
        self._send_ok()


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    address, port = s.getsockname()
    s.close()
    return port


class TestMockMatchMakerServer(object):
    @classmethod
    def setup_class(cls):
        # Configure mock server.
        cls.mock_server_port = get_free_port()
        cls.mock_server = HTTPServer(("localhost", cls.mock_server_port), MockServerRequestHandler)

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()

    def test_mme_add(self, populated_database, user_obj, case_obj, parsed_variant):
        """test calling the controller that submits new patients to Matchmaker"""

        session = requests.Session()
        adapter = populated_database

        # Add an HPO term to this scout case
        assert len(case_obj.get("phenotype_terms")) == 0
        phenotype_term = {
            "phenotype_id": "HP:0011031",
            "feature": "Abnormality of iron homeostasis",
        }
        updated_case = adapter.case_collection.find_one_and_update(
            {"_id": case_obj["_id"]},
            {"$set": {"phenotype_terms": [phenotype_term]}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        assert updated_case["phenotype_terms"][0] == phenotype_term

        # Check that features (HPO) terms are obtained by MME parser
        features = hpo_terms(updated_case)
        assert features

        # Add a couple of OMIM diagnoses to this case
        assert case_obj.get("diagnosis_phenotypes") is None
        updated_case = adapter.case_collection.find_one_and_update(
            {"_id": case_obj["_id"]},
            {"$set": {"diagnosis_phenotypes": [615349, 616833]}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        assert updated_case["diagnosis_phenotypes"]

        # Check that OMIM terms are obtained by MME parser
        diagnoses = omim_terms(updated_case)
        assert diagnoses

        # Add variant containing a gene to database and pin it for this case
        a_gene = adapter.hgnc_collection.find_one()
        assert a_gene["hgnc_id"]
        assert adapter.variant_collection.find_one() is None
        parsed_variant["hgnc_ids"] = [a_gene["hgnc_id"]]
        parsed_variant["samples"] = [
            {  # pretend the affected subject has the allele
                "sample_id": "ADM1059A2",
                "display_name": "NA12882",
                "genotype_call": "0/1",
            }
        ]
        adapter.variant_collection.insert_one(parsed_variant)
        assert adapter.variant_collection.find_one()

        # pin it
        updated_case = adapter.case_collection.find_one_and_update(
            {"_id": case_obj["_id"]},
            {"$set": {"suspects": [parsed_variant["_id"]]}},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        assert updated_case["suspects"] == [parsed_variant["_id"]]

        # Check that genomic features are created correcly by MME parser
        g_feat = genomic_features(adapter, updated_case, "NA12882", "False")
        assert g_feat

        # use controller to send request and collect response
        mme_base_url = "http://localhost:{port}".format(port=self.mock_server_port)

        submitted_info = controllers.mme_add(
            store=adapter,
            user_obj=user_obj,
            case_obj=updated_case,
            add_gender=True,
            add_features=True,
            add_disorders=True,
            genes_only=False,
            mme_base_url=mme_base_url,
            mme_accepts=MME_ACCEPTS,
            mme_token=MME_TOKEN,
        )

        assert submitted_info["server_responses"][0]["patient"]

    def test_mme_delete(self, mme_submission, case_obj):
        """test calling the controller that deletes a patient from MatchMaker"""

        mme_base_url = "http://localhost:{port}".format(port=self.mock_server_port)
        case_obj["mme_submission"] = mme_submission
        server_responses = controllers.mme_delete(case_obj, mme_base_url, MME_TOKEN)

        assert server_responses[0]["patient_id"] == mme_submission["patients"][0]["id"]

    def test_mme_matches(self, case_obj, mme_submission, institute_obj):
        """Testing calling the controller that collects all matches for a patient"""

        mme_base_url = "http://localhost:{port}".format(port=self.mock_server_port)
        case_obj["mme_submission"] = mme_submission
        data = controllers.mme_matches(case_obj, institute_obj, mme_base_url, MME_TOKEN)
        assert data
        assert data["institute"] == institute_obj
        assert data["case"] == case_obj
        query_patient = mme_submission["patients"][0]["id"]
        assert query_patient in data["matches"]

    def test_mme_match(self, case_obj, mme_submission):
        """Testing calling the controller that triggers internal and external MME matches"""

        mme_base_url = "http://localhost:{port}".format(port=self.mock_server_port)
        case_obj["mme_submission"] = mme_submission

        ##  Test function to trigger internal matches:
        server_responses = controllers.mme_match(
            case_obj=case_obj,
            match_type="internal",
            mme_base_url=mme_base_url,
            mme_token=MME_TOKEN,
        )
        # server response will be a list of responses
        assert isinstance(server_responses, list)
        # with one element:
        assert len(server_responses) == 1
        # server response coresponds to the right patient
        assert server_responses[0]["patient_id"] == case_obj["mme_submission"]["patients"][0]["id"]
        # and the node is the internal node
        assert server_responses[0]["server"] == "Local MatchMaker node"

        ## Test Matches against external nodes:
        # Test function to trigger external matches against one node
        nodes = [{"id": "mock_node_1"}]
        server_responses = controllers.mme_match(
            case_obj=case_obj,
            match_type=nodes[0]["id"],
            mme_base_url=mme_base_url,
            mme_token=MME_TOKEN,
            nodes=nodes,
            mme_accepts=MME_ACCEPTS,
        )
        # make sure that a list of server response with one element is returned
        assert isinstance(server_responses, list)
        assert len(server_responses) == 1
        # server response coresponds to the right patient
        assert server_responses[0]["patient_id"] == case_obj["mme_submission"]["patients"][0]["id"]
        # and the node is the external node
        assert server_responses[0]["server"] == "mock_node_1"

        # Test function to trigger external matches against all nodes:
        # add another node:
        nodes.append({"id": "mock_node_2"})
        server_responses = controllers.mme_match(
            case_obj=case_obj,
            match_type="external",
            mme_base_url=mme_base_url,
            mme_token=MME_TOKEN,
            nodes=nodes,
            mme_accepts=MME_ACCEPTS,
        )
        # server response will be a list of responses
        assert isinstance(server_responses, list)
        # there will be one response for each node (2)
        assert len(server_responses) == 2

        node_ids = [node["id"] for node in nodes]
        for i, resp in enumerate(server_responses):
            # matching of patient 1 on each node returns a matching for the right patient
            assert (
                server_responses[i]["patient_id"] == case_obj["mme_submission"]["patients"][0]["id"]
            )
            # both nodes were interrogated
            assert server_responses[i]["server"] in node_ids
