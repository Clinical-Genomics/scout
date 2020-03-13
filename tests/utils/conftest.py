"""Fixtures for scout utils"""

import pytest


@pytest.fixture
def refseq_response():
    """Return the string that is a refseq response"""
    _string = (
        b'<?xml version="1.0" encoding="UTF-8" ?>\n<!DOCTYPE eSearchResult PUBLIC "-//NLM//DTD '
        b'esearch 20060628//EN" "https://eutils.ncbi.nlm.nih.gov/eutils/dtd/20060628/esearch.dtd">'
        b"\n<eSearchResult><Count>1</Count><RetMax>1</RetMax><RetStart>0</RetStart><IdList>\n<Id>"
        b"NM_020533.3</Id>\n</IdList><TranslationSet/><QueryTranslation/></eSearchResult>\n"
    )
    return _string


@pytest.fixture
def refseq_response_non_existing():
    """Return the string that is a refseq response when tx does not exist"""
    _string = (
        b'<?xml version="1.0" encoding="UTF-8" ?>\n<!DOCTYPE eSearchResult PUBLIC "-//NLM//DTD '
        b'esearch 20060628//EN" "https://eutils.ncbi.nlm.nih.gov/eutils/dtd/20060628/esearch.dtd">'
        b"\n<eSearchResult><Count>0</Count><RetMax>0</RetMax><RetStart>0</RetStart><IdList/><Trans"
        b"lationSet/><QueryTranslation>(NM_000000[All Fields])</QueryTranslation><ErrorList><Phras"
        b"eNotFound>NM_000000</PhraseNotFound></ErrorList><WarningList><OutputMessage>No items fou"
        b"nd.</OutputMessage></WarningList></eSearchResult>\n"
    )
    return _string
