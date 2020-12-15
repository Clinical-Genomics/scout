"""Fixtures for scout utils"""

import pytest

from scout.utils import ensembl_rest_clients


@pytest.fixture()
def igv_public_track():
    """Return a dictionary coresponding to a public IGV track"""
    public_track = {
        "name": "custom_public_bucket",
        "access": "public",
        "tracks": [
            {
                "name": "Test public track",
                "type": "variant",
                "format": "vcf",
                "build": "37",
                "url": "url/to/public/track",
                "indexURL": "url/to/public/track.index",
            }
        ],
    }
    return public_track


@pytest.fixture
def igv_test_tracks(igv_public_track):
    """Returns a list with test tracks for igv.js"""
    return [igv_public_track]  # this will contain also a private track in the future


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


@pytest.fixture(name="ensembl_biomart_xml_query")
def fixture_ensembl_biomart_xml_query():
    """Fixture for query ensembl biomart with xml"""
    _xml = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE Query>
    <Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "0"\
    count = "" datasetConfigVersion = "0.6" completionStamp = "1">
        <Dataset name = "hsapiens_gene_ensembl" interface = "default" >
            <Filter name = "ensembl_gene_id" value = "ENSG00000115091"/>
            <Attribute name = "hgnc_symbol" />
            <Attribute name = "ensembl_transcript_id" />
        </Dataset>
    </Query>
    """
    return _xml


@pytest.fixture
def ensembl_biomart_client_37():
    """Return a client to the ensembl biomart, build 37"""
    return ensembl_rest_clients.EnsemblBiomartClient("37")


@pytest.fixture
def ensembl_rest_client_37():
    """Return a client to the ensembl rest api, build 37"""
    return ensembl_rest_clients.EnsemblRestApiClient("37")


@pytest.fixture
def ensembl_rest_client_38():
    """Return a client to the ensembl rest api, build 38"""
    return ensembl_rest_clients.EnsemblRestApiClient("38")


@pytest.fixture
def ensembl_gene_response():
    """Return a response from ensembl gene api"""
    _response = [
        {
            "description": (
                "alpha- and gamma-adaptin binding protein " "[Source:HGNC Symbol;Acc:25662]"
            ),
            "logic_name": "ensembl_havana_gene",
            "version": 8,
            "assembly_name": "GRCh37",
            "gene_id": "ENSG00000103591",
            "external_name": "AAGAB",
            "start": 67493371,
            "seq_region_name": "15",
            "feature_type": "gene",
            "end": 67547533,
            "strand": -1,
            "id": "ENSG00000103591",
            "biotype": "protein_coding",
            "source": "ensembl_havana",
        }
    ]
    return _response


@pytest.fixture
def ensembl_transcripts_response():
    """Return a (cropped) response from ensembl tx api"""
    _response = [
        {
            "biotype": "protein_coding",
            "assembly_name": "GRCh38",
            "seq_region_name": "7",
            "feature_type": "transcript",
            "ccdsid": "CCDS5862.1",
            "logic_name": "havana_homo_sapiens",
            "id": "ENST00000476279",
            "Parent": "ENSG00000090266",
            "external_name": "NDUFB2-212",
            "end": 140722790,
            "description": None,
            "transcript_id": "ENST00000476279",
            "start": 140696671,
            "source": "havana",
            "tag": "basic",
            "strand": 1,
            "transcript_support_level": "5",
            "version": 5,
        },
        {
            "strand": 1,
            "transcript_support_level": "3",
            "version": 1,
            "description": None,
            "end": 140721955,
            "external_name": "NDUFB2-203",
            "transcript_id": "ENST00000461457",
            "start": 140696688,
            "source": "havana",
            "tag": "basic",
            "logic_name": "havana_homo_sapiens",
            "Parent": "ENSG00000090266",
            "id": "ENST00000461457",
            "biotype": "protein_coding",
            "assembly_name": "GRCh38",
            "feature_type": "transcript",
            "seq_region_name": "7",
        },
    ]

    return _response
