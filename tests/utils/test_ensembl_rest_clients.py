"""Tests for ensembl rest api"""

import responses

from scout.utils.broad_liftover_client import RESTAPI_URL

CHROM = "8"
START = 140300615
END = 140300620
REF = "T"
ALT = "G"
BUILD_FROM = "hg19"
BUILD_TO = "hg38"


@responses.activate
def test_liftover_bcftools():
    """Test send request for coordinates liftover - case when variant  ref and alt are available."""

    # GIVEN a mocked response from the Broad liftover service for a requested URL
    FORMAT = "variant"
    URL = f"{LIFTOVER_URL}/?hg={BUILD_FROM}-to-{BUILD_TO}&format={FORMAT}&chrom={CHROM}&pos={START}&end={END}&ref={REF}&alt={ALT}"
    LIFTOVER_RESPONSE = {
        "hg": "hg19-to-hg38",
        "chrom": "chr8",
        "pos": "140300615",
        "alt": "G",
        "ref": "T",
        "format": "variant",
        "end": "140300615",
        "start": 140300614,
        "output_chrom": "chr8",
        "output_pos": 139288372,
        "output_ref": "T",
        "output_alt": "G",
        "output_reverse_complemented": false,
        "output_ref_alt_swap": null,
        "liftover_tool": "bcftools liftover plugin",
        "normalized_chrom": "chr8",
        "normalized_pos": "140300615",
        "normalized_ref": "T",
        "normalized_alt": "G",
    }

    responses.add(
        responses.GET,
        URL,
        json=LIFTOVER_RESPONSE,
        status=200,
    )
    """
    client = ensembl_rest_client
    # WHEN sending the liftover request the function should return a mapped locus
    mapped_coords = client.liftover("37", "X", 1000000, 1000100)
    assert mapped_coords[0]["mapped"]
    """
    pass


@responses.activate
def test_liftover_ucsc():
    """Test send request for coordinates liftover. Only coordinates liftover."""

    # GIVEN a mocked response from the Broad liftover service for a requested URL
    FORMAT = "interval"
    URL = f"{LIFTOVER_URL}/?hg={BUILD_FROM}-to-{BUILD_TO}&format={FORMAT}&chrom={CHROM}&start={START}&end={END}"
    LIFTOVER_RESPONSE = {
        "hg": "hg19-to-hg38",
        "chrom": "chr8",
        "alt": "G",
        "start": "140300615",
        "format": "interval",
        "ref": "T",
        "end": "140300620",
        "pos": 140300616,
        "output_chrom": "chr8",
        "output_pos": 139288373,
        "output_start": 139288372,
        "output_end": 139288377,
        "output_strand": "+",
        "liftover_tool": "UCSC liftover tool",
    }
