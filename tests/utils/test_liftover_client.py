"""Tests for ensembl rest api"""

import responses

from scout.utils.broad_liftover_client import LIFTOVER_URL

CHROM = "8"
START = 141310715
END = 141310715
REF = "T"
ALT = "G"
BUILD_FROM = "hg19"
BUILD_TO = "hg38"


@responses.activate
def test_liftover_bcftools(broad_liftover_client, broad_bcftools_liftover_response):
    """Test send request for coordinates liftover - case when variant  ref and alt are available."""

    # GIVEN a mocked response from the Broad liftover service for a requested URL
    FORMAT = "variant"
    URL = f"{LIFTOVER_URL}/?hg={BUILD_FROM}-to-{BUILD_TO}&format={FORMAT}&chrom={CHROM}&pos={START}&end={END}&ref={REF}&alt={ALT}"

    responses.add(
        responses.GET,
        URL,
        json=broad_bcftools_liftover_response,
        status=200,
    )
    client = broad_liftover_client
    # WHEN sending the liftover request the function should return a lift over locus
    result = client.liftover(
        build_from=BUILD_FROM,
        chrom=CHROM,
        start=START,
        end=END,
        ref=REF,
        alt=ALT,
    )
    assert result == broad_bcftools_liftover_response


@responses.activate
def test_liftover_ucsc(broad_liftover_client, broad_ucsc_liftover_response):
    """Test send request for coordinates liftover. Only coordinates liftover."""

    # GIVEN a mocked response from the Broad liftover service for a requested URL
    FORMAT = "interval"
    URL = f"{LIFTOVER_URL}/?hg={BUILD_FROM}-to-{BUILD_TO}&format={FORMAT}&chrom={CHROM}&start={START}&end={END}"

    responses.add(
        responses.GET,
        URL,
        json=broad_ucsc_liftover_response,
        status=200,
    )
    client = broad_liftover_client
    # WHEN sending the liftover request the function should return a lift over locus
    result = client.liftover(build_from=BUILD_FROM, chrom=CHROM, start=START, end=END)
    assert result == broad_ucsc_liftover_response
