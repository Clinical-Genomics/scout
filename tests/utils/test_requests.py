"""Tests for scout requests"""

import pytest
import requests
import responses

from scout.utils import scout_requests


def test_get_request_bad_url():
    """Test functions that accepts an url and returns decoded data from it"""

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
        responses.GET, url, status=404,
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
        responses.GET, url, body=requests.exceptions.Timeout(),
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
        responses.GET, url, status=200,
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
        responses.GET, url, body=content, status=200,
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
        responses.GET, url, body=content, status=200,
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
    url = "http://purl.obolibrary.org/obo/hp.obo"
    with open(hpo_terms_file, "r") as hpo_file:
        content = hpo_file.read()
    responses.add(
        responses.GET, url, body=content, status=200,
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
        responses.GET, url, body=content, status=200,
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
        responses.GET, url, body=content, status=200,
    )

    # WHEN fetching the resource
    data = scout_requests.fetch_hpo_to_genes_to_disease()

    # THEN assert that the HPO header is there
    assert "#Format: HPO-id" in data[0]


@responses.activate
def test_fetch_mim_files_mim2genes(phenotype_to_genes_file):
    """Test fetch resource"""

    # GIVEN an URL
    url = "https://omim.org/static/omim/data/mim2gene.txt"

    with open(phenotype_to_genes_file, "r") as hpo_file:
        content = hpo_file.read()
    responses.add(
        responses.GET, url, body=content, status=200,
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
        responses.GET, url, json=content, status=200,
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
        responses.GET, url, body=refseq_response, status=200,
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
        responses.GET, url, body=refseq_response_non_existing, status=200,
    )
    refseq_version = scout_requests.fetch_refseq_version(refseq_acc)

    # THEN assert that the same ref seq was returned
    assert refseq_version == refseq_acc
