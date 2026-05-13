"""Tests for ensembl rest api"""

import responses

from scout.utils.broad_liftover_client import LIFTOVER_URL

CHROM = "8"
START = 141310715
END = 141310720
REF = "T"
ALT = "G"
BUILD_FROM = "hg19"
BUILD_TO = "hg38"


@responses.activate
def test_liftover_bcftools(broad_liftover_client):
    """Test send request for coordinates liftover - case when variant  ref and alt are available."""

    # GIVEN a mocked response from the Broad liftover service for a requested URL
    FORMAT = "variant"
    URL = f"{LIFTOVER_URL}/?hg={BUILD_FROM}-to-{BUILD_TO}&format={FORMAT}&chrom={CHROM}&pos={START}&end={END}&ref={REF}&alt={ALT}"
    LIFTOVER_RESPONSE = {
        "hg": "hg19-to-hg38",
        "chrom": "chr8",
        "pos": "141310715",
        "alt": "G",
        "ref": "T",
        "format": "variant",
        "end": "141310715",
        "start": 141310714,
        "output_chrom": "chr8",
        "output_pos": 140300616,
        "output_ref": "T",
        "output_alt": "G",
        "output_reverse_complemented": "false",
        "output_ref_alt_swap": "null",
        "liftover_tool": "bcftools liftover plugin",
        "normalized_chrom": "chr8",
        "normalized_pos": "141310715",
        "normalized_ref": "T",
        "normalized_alt": "G",
    }

    responses.add(
        responses.GET,
        URL,
        json=LIFTOVER_RESPONSE,
        status=200,
    )
    client = broad_liftover_client
    # WHEN sending the liftover request the function should return a lift over locus
    result = client.liftover(
        build_from=BUILD_FROM,
        build_to=BUILD_TO,
        chrom=CHROM,
        start=START,
        end=END,
        ref=REF,
        alt=ALT,
    )
    assert result == LIFTOVER_RESPONSE


@responses.activate
def test_liftover_ucsc(broad_liftover_client):
    """Test send request for coordinates liftover. Only coordinates liftover."""

    # GIVEN a mocked response from the Broad liftover service for a requested URL
    FORMAT = "interval"
    URL = f"{LIFTOVER_URL}/?hg={BUILD_FROM}-to-{BUILD_TO}&format={FORMAT}&chrom={CHROM}&start={START}&end={END}"
    LIFTOVER_RESPONSE = {
        "hg": "hg19-to-hg38",
        "chrom": "chr8",
        "alt": "G",
        "start": "141310715",
        "format": "interval",
        "ref": "T",
        "end": "141310720",
        "pos": 141310716,
        "output_chrom": "chr8",
        "output_pos": 140300617,
        "output_start": 140300616,
        "output_end": 140300621,
        "output_strand": "+",
        "liftover_tool": "UCSC liftover tool",
    }

    responses.add(
        responses.GET,
        URL,
        json=LIFTOVER_RESPONSE,
        status=200,
    )
    client = broad_liftover_client
    # WHEN sending the liftover request the function should return a lift over locus
    result = client.liftover(
        build_from=BUILD_FROM, build_to=BUILD_TO, chrom=CHROM, start=START, end=END
    )
    assert result == LIFTOVER_RESPONSE
