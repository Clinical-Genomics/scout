# -*- coding: utf-8 -*-

import pytest
from scout.utils.requests import fetch_refseq_version, get_request

def test_get_request():
    """Test functions that accepts an url and returns decoded data from it"""

    # test function with a url that is not valid
    url = 'fakeyurl'
    with pytest.raises(ValueError) as err:
        # function should raise error
        assert get_request(url)

    # test function with url that exists
    url = 'http://www.ensembl.org'
    decoded_resp = get_request(url)
    assert '<!DOCTYPE html>' in decoded_resp


def test_fetch_refseq_version():
    """Test eutils service from entrez that retrieves refseq version"""

    # fetch complete refseq version for accession that has version
    refseq_acc = 'NM_020533'
    refseq_version = fetch_refseq_version(refseq_acc)

    # entrez eutils might be down the very moment of the test
    if '.' in refseq_version:
        version_n = refseq_version.split('.')[1]
        # make sure that contains version number
        assert version_n.isdigit()

    # fetch complete refseq version for accession without version
    refseq_acc = 'NM_000000'
    refseq_version = fetch_refseq_version(refseq_acc)

    # make sure that contains version number
    assert refseq_version == refseq_acc
