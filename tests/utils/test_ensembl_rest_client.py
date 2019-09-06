# -*- coding: UTF-8 -*-
from urllib.error import HTTPError

from scout.utils import ensembl_rest_client

def test_ping_ensemble_37():
    """Test ping ensembl server containing human build 37"""
    client = ensembl_rest_client.EnsemblRestClient()
    data = client.ping_server()
    assert data == {'ping':1}

def test_ping_ensemble_38():
    """Test ping ensembl server containing human build 38"""
    client = ensembl_rest_client.EnsemblRestClient(build='38')
    data = client.ping_server()
    assert data == {'ping':1}

def test_send_wrong_request():
    """Successful requests are tested by other tests in this file.
       This test will trigger errors instead.
    """
    url = 'fakeyurl'
    client = ensembl_rest_client.EnsemblRestClient()
    data = client.send_request(url)
    assert type(data) == ValueError

    url = 'https://grch37.rest.ensembl.org/fakeyurl'
    data = client.send_request(url)
    assert type(data) == HTTPError

def test_use_api():
    """Test the API by retrieving all the available info for a gene,
       including transcripts and exons.
    """
    # default client will be querying agast build 37
    client = ensembl_rest_client.EnsemblRestClient()
    











#def test_perform_rest_action():
#    """Tests the perform_rest_action method of the EnsemblRestClient"""

#    client = ensembl_rest_client.EnsemblRestClient()
