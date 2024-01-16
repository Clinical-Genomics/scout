"""Tests for ensembl rest api"""

import responses
from requests.exceptions import HTTPError, MissingSchema

REST_CLIENT_37_URL = "https://grch37.rest.ensembl.org"


@responses.activate
def test_liftover(ensembl_rest_client_37, ensembl_liftover_response):
    """Test send request for coordinates liftover"""
    # GIVEN a patched response from Ensembl
    url = f"{REST_CLIENT_37_URL}/map/human/GRCh37/X:1000000..1000100/GRCh38?content-type=application/json"
    responses.add(
        responses.GET,
        url,
        json=ensembl_liftover_response,
        status=200,
    )
    client = ensembl_rest_client_37
    # WHEN sending the liftover request the function should return a mapped locus
    mapped_coords = client.liftover("37", "X", 1000000, 1000100)
    assert mapped_coords[0]["mapped"]


@responses.activate
def test_send_gene_request(ensembl_gene_response, ensembl_rest_client_37):
    """Test send request with correct params and endpoint"""
    url = f"{REST_CLIENT_37_URL}/overlap/id/ENSG00000103591?feature=gene"
    client = ensembl_rest_client_37
    responses.add(
        responses.GET,
        url,
        json=ensembl_gene_response,
        status=200,
    )
    data = client.send_request(url)

    # get all gene for the ensembl gene, They should be a list of items
    assert data[0]["assembly_name"] == "GRCh37"
    assert data[0]["external_name"] == "AAGAB"
    assert data[0]["start"]
    assert data[0]["end"]


@responses.activate
def test_send_request_fakey_url(ensembl_rest_client_37):
    """Successful requests are tested by other tests in this file.
    This test will trigger errors instead.
    """
    # GIVEN a completely invalid URL
    url = "fakeyurl"
    # GIVEN a client
    client = ensembl_rest_client_37
    responses.add(
        responses.GET,
        url,
        body=MissingSchema(),
        status=404,
    )
    data = client.send_request(url)
    assert isinstance(data, MissingSchema)


@responses.activate
def test_send_request_wrong_url(ensembl_rest_client_37):
    """Successful requests are tested by other tests in this file.
    This test will trigger errors instead.
    """
    url = f"{REST_CLIENT_37_URL}/fakeyurl"
    client = ensembl_rest_client_37
    responses.add(
        responses.GET,
        url,
        body=HTTPError(),
        status=404,
    )
    data = client.send_request(url)
    assert isinstance(data, HTTPError)


@responses.activate
def test_use_api(ensembl_rest_client_38, ensembl_transcripts_response):
    """Test the use_api method of the EnsemblRestClient"""

    endpoint = "/overlap/id/ENSG00000157764"
    params = {"feature": "transcript"}
    client = ensembl_rest_client_38
    url = client.build_url(endpoint, params)
    responses.add(
        responses.GET,
        url,
        json=ensembl_transcripts_response,
        status=200,
    )

    # get all transctipts for an ensembl gene, They should be a list of items
    data = client.use_api(endpoint, params)
    assert data[0]["assembly_name"] == "GRCh38"
    assert data[0]["feature_type"] == "transcript"
    assert data[0]["id"]
    assert data[0]["start"]
    assert data[0]["strand"]
