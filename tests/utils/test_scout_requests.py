"""Tests for scout requests"""
import tempfile
import zlib
from urllib.error import HTTPError

import pytest
import requests
import responses

from scout.utils import scout_requests


def test_get_request_json_error():
    """Test the function that sends a GET request that returns an error"""

    # GIVEN A URL that returns error
    url = "http://bar"
    resp_dict = scout_requests.get_request_json(url)

    # THEN the response should return an error message
    assert "An error occurred" in resp_dict["message"]


@responses.activate
def test_get_request_json():
    """Test the function that sends a GET request and returns the response content as json"""

    # GIVEN a URL that returns a success response
    url = "http://bar"
    responses.add(responses.GET, url, json={"foo": "bar"}, status=200)

    headers = {"X-Auth-Token": "XYZ"}
    resp_dict = scout_requests.get_request_json(url, headers)
    # Response should contain the expected data
    assert resp_dict["status_code"] == 200
    assert resp_dict["content"] == {"foo": "bar"}


def test_post_request_json_error():
    """Test function that sends a POST request to a URL that returns error"""

    url = "http://bar"
    data = {"param": "FOO"}

    resp_dict = scout_requests.post_request_json(url, data)
    assert "An error occurred while sending a POST request to url" in resp_dict["message"]


@responses.activate
def test_post_request_json():
    """Test the function that sends a POST request and returns the response content as json"""

    # GIVEN a URL that returns a success response
    url = "http://bar"
    responses.add(responses.POST, url, json={"foo": "bar"}, status=200)

    data = {"param": "FOO"}
    headers = {"Content-type": "application/json; charset=utf-8", "Accept": "text/json"}

    resp_dict = scout_requests.post_request_json(url, data, headers)
    # Response should contain the expected data
    assert resp_dict["status_code"] == 200
    assert resp_dict["content"] == {"foo": "bar"}


def test_delete_request_json_error():
    """Test function that sends a DELETE request to a URL that returns error"""

    # GIVEN A URL that returns error
    url = "http://bar"
    resp_dict = scout_requests.delete_request_json(url)

    # THEN the response should return an error message
    assert "An error occurred" in resp_dict["message"]


@responses.activate
def test_delete_request_json():
    """Test the function that sends a DELETE request and returns the response content as json"""

    # GIVEN a URL that returns a success response
    url = "http://bar"
    responses.add(responses.DELETE, url, json={"foo": "bar"}, status=200)

    headers = {"X-Auth-Token": "XYZ"}
    resp_dict = scout_requests.delete_request_json(url, headers)
    # Response should contain the expected data
    assert resp_dict["status_code"] == 200
    assert resp_dict["content"] == {"foo": "bar"}


def test_get_request_bad_url():
    """Test function that accepts an url and returns decoded data from it"""

    # test function with a url that is not valid
    url = "fakeyurl"
    with pytest.raises(requests.exceptions.MissingSchema):
        # function should raise error
        assert scout_requests.get_request(url)


@responses.activate
def test_get_request_bad_request():
    """Test functions that accepts an url and returns decoded data from it"""

    # GIVEN an URL
    url = "http://www.badurl.com"
    responses.add(
        responses.GET,
        url,
        status=404,
    )
    # WHEN requesting
    with pytest.raises(requests.exceptions.HTTPError):
        response = scout_requests.get_request(url)
        # THEN assert that the a httperror is raised
        assert response.status_code == 404


@responses.activate
def test_send_request_timout():
    """This test will trigge a timout error."""
    # GIVEN a request and a request that timouts
    url = "http://www.badurl.com"
    responses.add(
        responses.GET,
        url,
        body=requests.exceptions.Timeout(),
    )
    # WHEN requesting
    with pytest.raises(requests.exceptions.Timeout):
        # THEN assert that the a Timeout is raised
        scout_requests.get_request(url)


@responses.activate
def test_get_request():
    """Test functions that accepts an url and returns decoded data from it"""

    # GIVEN an URL
    url = "http://www.github.com"
    responses.add(
        responses.GET,
        url,
        status=200,
    )

    # WHEN requesting
    response = scout_requests.get_request(url)
    # THEN assert that the reponse is correct
    assert response.status_code == 200


@responses.activate
def test_fetch_resource():
    """Test fetch resource"""

    # GIVEN an URL
    url = "http://www.github.com"
    content = "Some things\n That are not so\ninteresting"
    responses.add(
        responses.GET,
        url,
        body=content,
        status=200,
    )

    # WHEN fetching the resource
    data = scout_requests.fetch_resource(url)
    # THEN assert that a list of lines are returned
    assert isinstance(data, list)


@responses.activate
def test_fetch_resource_gzipped(variant_clinical_file):
    """Test fetch resource"""

    # GIVEN an URL
    url = "http://www.github.com/things.txt.gz"
    with open(variant_clinical_file, "rb") as zipped_file:
        content = zipped_file.read()
    responses.add(
        responses.GET,
        url,
        body=content,
        status=200,
    )

    # WHEN fetching the resource
    data = scout_requests.fetch_resource(url)
    # THEN assert that a list of lines are returned
    assert isinstance(data, list)
    # THEN assert that the vcf header is there
    assert "##fileformat" in data[0]


@responses.activate
def test_fetch_hpo(hpo_terms_file):
    """Test fetch resource"""

    # GIVEN an URL
    url = "https://raw.githubusercontent.com/obophenotype/human-phenotype-ontology/master/hp.obo"
    with open(hpo_terms_file, "r") as hpo_file:
        content = hpo_file.read()
    responses.add(
        responses.GET,
        url,
        body=content,
        status=200,
    )

    # WHEN fetching the resource
    data = scout_requests.fetch_hpo_terms()

    # THEN assert that the HPO header is there
    assert "format-version" in data[0]


@responses.activate
def test_fetch_genes_to_hpo_to_disease(hpo_genes_file):
    """Test fetch resource"""

    # GIVEN an URL
    url = scout_requests.HPO_URL.format("genes_to_phenotype.txt")
    with open(hpo_genes_file, "r") as hpo_file:
        content = hpo_file.read()
    responses.add(
        responses.GET,
        url,
        body=content,
        status=200,
    )

    # WHEN fetching the resource
    data = scout_requests.fetch_genes_to_hpo_to_disease()

    # THEN assert that the HPO header is there
    assert "#Format: entrez" in data[0]


@responses.activate
def test_fetch_hpo_to_genes_to_disease(phenotype_to_genes_file):
    """Test fetch resource"""

    # GIVEN an URL
    url = scout_requests.HPO_URL.format("phenotype_to_genes.txt")

    with open(phenotype_to_genes_file, "r") as hpo_file:
        content = hpo_file.read()
    responses.add(
        responses.GET,
        url,
        body=content,
        status=200,
    )

    # WHEN fetching the resource
    data = scout_requests.fetch_hpo_to_genes_to_disease()

    # THEN assert that the HPO header is there
    assert "#Format: HPO-id" in data[0]


@responses.activate
def test_fetch_hpo_files(phenotype_to_genes_file, hpo_genes_file):
    """Test fetch hpo files"""

    # GIVEN URLs two hpo files
    url_1 = scout_requests.HPO_URL.format("phenotype_to_genes.txt")
    url_2 = scout_requests.HPO_URL.format("genes_to_phenotype.txt")

    with open(phenotype_to_genes_file, "r") as hpo_file:
        content = hpo_file.read()

    responses.add(
        responses.GET,
        url_1,
        body=content,
        status=200,
    )

    with open(hpo_genes_file, "r") as hpo_file:
        content = hpo_file.read()

    responses.add(
        responses.GET,
        url_2,
        body=content,
        status=200,
    )

    # WHEN fetching all hpo files
    res = scout_requests.fetch_hpo_files(genes_to_phenotype=True, phenotype_to_genes=True)

    # THEN assert that the HPO header is there
    assert isinstance(res, dict)


def test_fetch_hgnc(hgnc_file, mocker):
    """Test fetch hgnc"""

    # GIVEN file with hgnc info
    mocker.patch.object(scout_requests.urllib.request, "urlopen")
    with open(hgnc_file, "rb") as hgnc_handle:
        hgnc_info = hgnc_handle.read()
    with tempfile.TemporaryFile() as temp:
        temp.write(hgnc_info)
        temp.seek(0)
        scout_requests.urllib.request.urlopen.return_value = temp
        # WHEN fetching the resource
        data = scout_requests.fetch_hgnc()

    # THEN assert that the HGNC header is there
    assert "hgnc_id\tsymbol" in data[0]


def test_fetch_exac_constraint(exac_file, mocker):
    """Test fetch exac constraint file"""

    # GIVEN file with hgnc info
    mocker.patch.object(scout_requests.urllib.request, "urlopen")
    with open(exac_file, "rb") as exac_handle:
        exac_info = exac_handle.read()
    with tempfile.TemporaryFile() as temp:
        temp.write(exac_info)
        temp.seek(0)
        scout_requests.urllib.request.urlopen.return_value = temp
        # WHEN fetching the resource
        data = scout_requests.fetch_exac_constraint()

    # THEN assert that the exac header is there
    assert "transcript\tgene" in data[0]


@responses.activate
def test_fetch_exac_constraint_failed_ftp(variant_clinical_file, mocker):
    """Test fetch exac constraint file when ftp request fails"""

    # GIVEN file with hgnc info
    # GIVEN a mocked call that raises a HTTPError when fetching from ftp
    mocker.patch.object(scout_requests.urllib.request, "urlopen")
    url = (
        "https://storage.googleapis.com/gnomad-public/legacy/exacv1_downloads/release0.3.1"
        "/manuscript_data/forweb_cleaned_exac_r03_march16_z_data_pLI.txt.gz"
    )
    scout_requests.urllib.request.urlopen.return_value = HTTPError(
        url, 500, "Internal Error", {}, None
    )
    # GIVEN a gzipped file
    with open(variant_clinical_file, "rb") as zipped_file:
        content = zipped_file.read()

    responses.add(
        responses.GET,
        url,
        body=content,
        status=200,
    )

    # WHEN fetching the resource
    data = scout_requests.fetch_exac_constraint()

    # THEN some content is returned
    assert len(data) > 10


@responses.activate
def test_fetch_mim_files_mim2genes(phenotype_to_genes_file):
    """Test fetch resource"""

    # GIVEN an URL
    url = "https://omim.org/static/omim/data/mim2gene.txt"

    with open(phenotype_to_genes_file, "r") as hpo_file:
        content = hpo_file.read()
    responses.add(
        responses.GET,
        url,
        body=content,
        status=200,
    )

    # WHEN fetching the resource
    data = scout_requests.fetch_mim_files(api_key=None, mim2genes=True)

    # THEN assert that the HPO header is there
    assert isinstance(data, dict)


def test_fetch_ensembl_biomart(mocker):
    """Test fetch resource"""

    # GIVEN a mock
    mocker.patch.object(scout_requests, "EnsemblBiomartClient")
    attributes = [
        "chromosome_name",
        "start_position",
    ]
    # WHEN fetching the resource
    client = scout_requests.fetch_ensembl_biomart(attributes=attributes, filters=None)

    # THEN assert that a result is returned
    assert client


def test_fetch_ensembl_genes(mocker):
    """Test fetch resource"""

    # GIVEN a mock
    mocker.patch.object(scout_requests, "EnsemblBiomartClient")
    # WHEN fetching the resource
    client = scout_requests.fetch_ensembl_genes()

    # THEN assert that a result is returned
    assert client


def test_fetch_ensembl_transcripts(mocker):
    """Test fetch resource"""

    # GIVEN a mock
    mocker.patch.object(scout_requests, "EnsemblBiomartClient")
    # WHEN fetching the resource
    client = scout_requests.fetch_ensembl_transcripts()

    # THEN assert that a result is returned
    assert client


def test_fetch_ensembl_exons(mocker):
    """Test fetch resource"""

    # GIVEN a mock
    mocker.patch.object(scout_requests, "EnsemblBiomartClient")
    # WHEN fetching the resource
    client = scout_requests.fetch_ensembl_exons()

    # THEN assert that a result is returned
    assert client


@responses.activate
def test_fetch_resource_json():
    """Test fetch resource"""

    # GIVEN an URL
    url = "http://www.github.com"
    content = [{"first": "second"}]
    responses.add(
        responses.GET,
        url,
        json=content,
        status=200,
    )

    # WHEN fetching the resource
    data = scout_requests.fetch_resource(url, json=True)
    # THEN assert that a list of lines are returned
    assert isinstance(data, list)
    assert data[0]["first"] == "second"


@responses.activate
def test_fetch_refseq_version(refseq_response):
    """Test utils service from entrez that retrieves refseq version"""

    # GIVEN a refseq accession number
    refseq_acc = "NM_020533"
    # GIVEN the base url
    base_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=nuccore&"
        "term={}&idtype=acc"
    )
    url = base_url.format(refseq_acc)
    responses.add(
        responses.GET,
        url,
        body=refseq_response,
        status=200,
    )
    # WHEN fetching complete refseq version for accession that has version
    refseq_version = scout_requests.fetch_refseq_version(refseq_acc)
    # THEN assert that the refseq identifier is the same
    assert refseq_acc in refseq_version
    # THEN assert that there is a version that is a digit
    version_n = refseq_version.split(".")[1]
    assert version_n.isdigit()


@responses.activate
def test_fetch_refseq_version_non_existing(refseq_response_non_existing):
    """Test to fetch version for non existing transcript"""
    # GIVEN a accession without refseq version
    refseq_acc = "NM_000000"
    # GIVEN the base url
    base_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=nuccore&"
        "term={}&idtype=acc"
    )
    url = base_url.format(refseq_acc)
    responses.add(
        responses.GET,
        url,
        body=refseq_response_non_existing,
        status=200,
    )
    refseq_version = scout_requests.fetch_refseq_version(refseq_acc)

    # THEN assert that the same ref seq was returned
    assert refseq_version == refseq_acc
