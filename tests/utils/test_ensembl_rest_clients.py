"""Tests for ensembl rest api"""

import responses
from requests.exceptions import MissingSchema
from requests.models import Response

from scout.utils.ensembl_rest_clients import RESTAPI_37


@responses.activate
def test_liftover(ensembl_rest_client_37, ensembl_liftover_response):
    """Test send request for coordinates liftover"""
    # GIVEN a patched response from Ensembl
    url = f"{RESTAPI_37}/map/human/GRCh37/X:1000000..1000100/GRCh38?content-type=application/json"
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
    url = f"{RESTAPI_37}/overlap/id/ENSG00000103591?feature=gene"
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


def test_send_request_fakey_url(mock_app, ensembl_rest_client_37, mocker):
    """Test the Ensembl REST client with an URL that is raising missing schema error."""

    # GIVEN a completely invalid URL
    url = "fakeyurl"
    # GIVEN patched Ensembl client
    client = ensembl_rest_client_37
    mocker.patch("requests.get", side_effect=MissingSchema("Invalid URL"))

    # THEN the client should return no content
    with mock_app.test_request_context():
        data = client.send_request(url)
        assert data is None


def test_send_request_unavaailable(mock_app, ensembl_rest_client_37, mocker):
    """Test the Ensembl REST client with an URL that is not available (500 error)."""

    url = f"{RESTAPI_37}/fakeyurl"
    # GIVEN patched Ensembl client
    client = ensembl_rest_client_37

    # GIVEN a mocked 550 response from Ensembl
    mock_response = Response()
    mock_response.status_code = 500  # Simulate 500 Internal Server Error
    mock_response._content = b"Internal Server Error"  # Optional: Set error content

    # Mock `requests.get` to return the mock response
    mocker.patch("scout.utils.ensembl_rest_clients.requests.get", return_value=mock_response)

    with mock_app.test_request_context():
        # THEN the client should return no content
        data = client.send_request(url)
        assert data is None
