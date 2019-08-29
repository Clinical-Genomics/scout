# -*- coding: utf-8 -*-

from scout.utils.requests import fetch_refseq_version

def test_fetch_refseq_version():
    """Test eutils service from entrez that retrieves refseq version"""

    refseq_acc = 'NM_020533'
    # fetch complete refseq version
    refseq_version = fetch_refseq_version(refseq_acc)

    version_n = refseq_version.split('.')[1]
    # make sure that contains version number
    assert version_n.isdigit()
