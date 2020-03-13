"""Tests for scout requests"""

import os
import tempfile

import pytest

from scout.utils import scout_requests
from scout.utils.scout_requests import fetch_refseq_version, get_request

TRAVIS = os.getenv("TRAVIS")


def test_get_request_bad_url():
    """Test functions that accepts an url and returns decoded data from it"""

    # test function with a url that is not valid
    url = "fakeyurl"
    with pytest.raises(ValueError):
        # function should raise error
        assert get_request(url)


def test_get_request(mocker, refseq_response):
    """Test functions that accepts an url and returns decoded data from it"""

    # test function with url that exists
    url = "http://www.github.com"
    mocker.patch.object(scout_requests.urllib.request, "urlopen")
    with tempfile.TemporaryFile() as temp:
        temp.write(refseq_response)
        temp.seek(0)
        scout_requests.urllib.request.urlopen.return_value = temp
        decoded_resp = get_request(url)

    assert "<!DOCTYPE" in decoded_resp


def test_fetch_refseq_version(refseq_response, mocker):
    """Test utils service from entrez that retrieves refseq version"""

    # GIVEN a refseq accession number
    refseq_acc = "NM_020533"

    mocker.patch.object(scout_requests.urllib.request, "urlopen")
    with tempfile.TemporaryFile() as temp:
        temp.write(refseq_response)
        temp.seek(0)
        scout_requests.urllib.request.urlopen.return_value = temp
        # WHEN fetching complete refseq version for accession that has version
        refseq_version = fetch_refseq_version(refseq_acc)
    print(refseq_version)
    # WHEN fetching the refseq version number
    version_n = refseq_version.split(".")[1]
    # THEN assert that the version is a digit
    assert version_n.isdigit()


def test_fetch_refseq_version_non_existing(refseq_response_non_existing, mocker):
    """Test to fetch version for non existing transcript"""
    # GIVEN a accession without refseq version
    refseq_acc = "NM_000000"
    # WHEN fetching the version
    mocker.patch.object(scout_requests.urllib.request, "urlopen")
    with tempfile.TemporaryFile() as temp:
        temp.write(refseq_response_non_existing)
        temp.seek(0)
        scout_requests.urllib.request.urlopen.return_value = temp
        # WHEN fetching complete refseq version for accession that has version
        refseq_version = fetch_refseq_version(refseq_acc)

    # THEN assert that the same ref seq was returned
    assert refseq_version == refseq_acc
