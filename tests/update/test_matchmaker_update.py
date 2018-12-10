from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from threading import Thread
import requests

from pathlib import Path
import json

from scout.parse.mme import mme_patients, phenotype_features, genomic_features, omim_disorders
from scout.update.matchmaker import mme_update

TOKEN = 'abcd'

# mock matchmaker server to send responses when it get requests
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


    def test_add_scout_patient(self, real_populated_database, case_obj, user_obj, institute_obj, gene_bulk):

        adapter = real_populated_database
        case_obj = case_obj

        # add a phenotype for this case
        hpo_obj = [{
                'phenotype_id' : 'HP:0000878',
                'feature' : 'A phenotype'
            },
            {
                'phenotype_id' : 'HP:0000878',
                'feature' : 'A phenotype'
            }
        ]
        # update phenotype terms of the case with hpo_obj
        case_obj['phenotype_terms'] = hpo_obj
        features = phenotype_features(case_obj)

        # Add a couple of OMIM diagnoses for this case
        # to create patients disorders for matchmaker
        case_obj['diagnosis_phenotypes'] = [607504, 145590]
        disorders = omim_disorders(case_obj)
        assert len(disorders) == 2

        # make sure that this case contains at least a sample
        a_sample = case_obj['individuals'][0].get('display_name')
        assert a_sample

        # assert that two phenotypes are found when parsing case object
        assert len(features) == 2
        assert 'id' in features[0] # 'id' key must be found
        assert 'label' in features[0] # 'label' key must be found
        assert 'observed' in features[0] # 'observed' key must be found

        ## GIVEN a populated database with variants in a certain gene
        hgnc_id = 3233
        gene_obj = adapter.hgnc_gene(hgnc_id)
        assert gene_obj

        # load a number of variants hitting that gene
        nr_loaded = adapter.load_variants(case_obj=case_obj, variant_type='clinical',
                              category='snv', rank_threshold=None, chrom=None,
                              start=None, end=None, gene_obj=gene_obj)

        gene_variants = list(adapter.variants(case_id=case_obj['_id'], nr_of_variants=-1))
        assert len(gene_variants) > 0

        # collect parsed genomic features for these variants
        g_features = genomic_features(adapter, gene_variants, a_sample, '37')

        # check number and format of the extracted genomic features
        assert len(g_features) == len(gene_variants)
        assert "gene" in g_features[0]
        assert "variant" in g_features[0]
        assert "zygosity" in g_features[0]

        # build test patient based on the above data
        patient = {
            'features' : features,
            'genomicFeatures' : g_features,
            'disorders' : disorders,
            'id' : 'test_patient',
            'contact' : { 'name': 'test_user', 'href' : 'test.email@email.com' }
        }

        # send it to matchmaker server via post request
        url = 'http://localhost:{port}'.format(port=self.mock_server_port)
        response = mme_update( matchmaker_url=url, update_action='add', json_patient=patient, token=TOKEN)
        assert response['status'] == 200
