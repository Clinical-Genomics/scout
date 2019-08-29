# -*- coding: utf-8 -*-

from scout.utils.requests import fetch_refseq_version

def test_fetch_refseq_version():
    """Test eutils service from entrez that retrieves refseq version"""

    # fetch complete refseq version for accession that has version
    refseq_acc = 'NM_020533'
    refseq_version = fetch_refseq_version(refseq_acc)

    version_n = refseq_version.split('.')[1]
    # make sure that contains version number
    assert version_n.isdigit()

    # fetch complete refseq version for accession without version
    refseq_acc = 'NM_000000'
    refseq_version = fetch_refseq_version(refseq_acc)

    # make sure that contains version number
    assert refseq_version == refseq_acc
