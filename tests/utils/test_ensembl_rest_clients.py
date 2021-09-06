"""Tests for ensembl rest api"""

import responses
from requests.exceptions import HTTPError, MissingSchema

from scout.utils import ensembl_rest_clients


@responses.activate
def test_ping_ensemble_37(ensembl_rest_client_37):
    """Test ping ensembl server containing human build 37"""
    # GIVEN a client to the ensembl rest api build 37
    client = ensembl_rest_client_37
    assert client.server == ensembl_rest_clients.RESTAPI_37
    # GIVEN a ping response
    ping_resp = {"ping": 1}
    responses.add(
        responses.GET,
        "/".join([ensembl_rest_clients.RESTAPI_37, ensembl_rest_clients.PING_ENDPOINT]),
        json=ping_resp,
        status=200,
    )
    # WHEN pinging the server
    data = client.ping_server()
    # THEN assert the ping succeded
    assert data == {"ping": 1}


@responses.activate
def test_ping_ensemble_38(ensembl_rest_client_38):
    """Test ping ensembl server containing human build 38"""
    client = ensembl_rest_client_38
    assert client.server == ensembl_rest_clients.RESTAPI_38
    # GIVEN a ping response
    ping_resp = {"ping": 1}
    responses.add(
        responses.GET,
        "/".join([ensembl_rest_clients.RESTAPI_38, ensembl_rest_clients.PING_ENDPOINT]),
        json=ping_resp,
        status=200,
    )
    data = client.ping_server()
    assert data == {"ping": 1}


@responses.activate
def test_send_gene_request(ensembl_gene_response, ensembl_rest_client_37):
    """Test send request with correct params and endpoint"""
    url = "https://grch37.rest.ensembl.org/overlap/id/ENSG00000103591?feature=gene"
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
    url = "https://grch37.rest.ensembl.org/fakeyurl"
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


def test_xml_filters(ensembl_biomart_client_37):
    """test method that creates filter lines for the biomart xml file"""

    # GIVEN a dictionary of biomart filters
    filters = {"string_filter": "string_value", "list_filter": ["1", "X", "MT"]}
    # GIVEN a biomart client
    client = ensembl_biomart_client_37
    xml_lines = client.xml_filters(filters)

    # make sure lines are formatted as they should
    assert (
        '<Filter name = "{0}" value = "{1}"/>'.format("string_filter", "string_value") in xml_lines
    )
    assert '<Filter name = "{0}" value = "{1}"/>'.format("list_filter", "1,X,MT") in xml_lines


def test_xml_attributes(ensembl_biomart_client_37):
    """test method that creates attribute lines for the biomart xml file"""

    # Given a list of  biomart attributes
    name = ["test_name"]
    client = ensembl_biomart_client_37
    # WHEN creating the xml attribute lines
    attribute_lines = client.xml_attributes(name)

    # THEN make sure that attributes lines are formatted as they should
    assert attribute_lines == ['<Attribute name = "test_name" />']


@responses.activate
def test_test_query_biomart_38_xml(ensembl_biomart_xml_query):
    """Prepare a test xml document for the biomart service build 38
    and query the service using it
    """
    # GIVEN client with a xml query for a gene
    build = "38"
    url = "".join([ensembl_rest_clients.BIOMART_38, ensembl_biomart_xml_query])
    response = (
        b"ACTR3\tENST00000263238\n"
        b"ACTR3\tENST00000443297\n"
        b"ACTR3\tENST00000415792\n"
        b"ACTR3\tENST00000446821\n"
        b"ACTR3\tENST00000535589\n"
        b"ACTR3\tENST00000489779\n"
        b"ACTR3\tENST00000484165\n"
        b"ACTR3\tENST00000478928\n"
        b"[success]"
    )
    responses.add(responses.GET, url, body=response, status=200, stream=True)
    # WHEN querying ensembl
    client = ensembl_rest_clients.EnsemblBiomartClient(
        build=build, xml=ensembl_biomart_xml_query, header=False
    )

    # THEN assert that the result is correct
    for line in client:
        # THEN assert that either the correct gene is fetched or that an
        assert "ACTR3" in line


@responses.activate
def test_test_query_biomart_37_no_xml():
    """Prepare a test xml document for the biomart service build 37 and
    query the service using it
    """
    # GIVEN defined biomart filters and attributes
    filters = {"ensembl_gene_id": "ENSG00000115091"}
    attributes = ["hgnc_symbol", "ensembl_transcript_id"]
    url = """http://ensembl.org/biomart/martservice?query=<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "0" count = "" \
datasetConfigVersion = "0.6" completionStamp = "1">

\t<Dataset name = "hsapiens_gene_ensembl" interface = "default" >
\t\t<Filter name = "ensembl_gene_id" value = "ENSG00000115091"/>
\t\t<Attribute name = "hgnc_symbol" />
\t\t<Attribute name = "ensembl_transcript_id" />
\t</Dataset>
</Query>"""

    response = (
        b"ACTR3\tENST00000263238\n"
        b"ACTR3\tENST00000443297\n"
        b"ACTR3\tENST00000415792\n"
        b"ACTR3\tENST00000446821\n"
        b"ACTR3\tENST00000535589\n"
        b"ACTR3\tENST00000489779\n"
        b"ACTR3\tENST00000484165\n"
        b"ACTR3\tENST00000478928\n"
        b"[success]"
    )
    responses.add(responses.GET, url, body=response, status=200, stream=True)
    # WHEN querying ensembl
    client = ensembl_rest_clients.EnsemblBiomartClient(
        build="38", filters=filters, attributes=attributes, header=False
    )

    for line in client:
        # THEN assert that either the correct gene is fetched or that an
        assert "ACTR3" in line
