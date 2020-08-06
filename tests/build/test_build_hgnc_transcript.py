from pprint import pprint as pp
import logging

LOG = logging.getLogger(__name__)
import pytest
from scout.build.genes.transcript import build_transcript

{
    "chrom": "1",
    "transcript_start": 1167629,
    "transcript_end": 1170421,
    "mrna": {"NM_080605"},
    "mrna_predicted": set(),
    "nc_rna": set(),
    "ensembl_gene_id": "ENSG00000176022",
    "ensembl_transcript_id": "ENST00000379198",
    "hgnc_id": 17978,
    "primary_transcripts": {"NM_080605"},
}


def test_build_hgnc_transcripts(parsed_transcripts):
    # GIVEN iterable with parsed transcripts

    # WHEN building transcript objects
    for tx_id in parsed_transcripts:
        tx_info = parsed_transcripts[tx_id]
        LOG.debug("tx_info: {}".format(tx_info))
        tx_obj = build_transcript(tx_info)

        # THEN check that the gene models have a hgnc id
        assert tx_obj["hgnc_id"]


@pytest.mark.parametrize("key", ['hgnc_id', 'transcript_start', 'transcript_end', 'chrom', 'ensembl_transcript_id'])
def test_build_hgnc_transcripts_KeyError(test_transcript, key):
    ## GIVEN a dictionary with exon information

    # WHEN key is deleted from dict
    test_transcript.pop(key)
    # THEN calling build_transcript() will raise KeyError
    with pytest.raises(KeyError):
        build_transcript(test_transcript)


@pytest.mark.parametrize("key", ['hgnc_id', 'transcript_start', 'transcript_end'])
def test_build_hgnc_transcript_TypeError(test_transcript, key):
    ## GIVEN a dictionary with exon information

    # WHEN setting key to None
    test_transcript[key] = None
    # THEN calling build_transcript() will raise TypeError
    with pytest.raises(TypeError):
        build_transcript(test_transcript)

