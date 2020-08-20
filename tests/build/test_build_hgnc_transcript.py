from pprint import pprint as pp
import pytest
from scout.build.genes.transcript import build_transcript


def test_build_hgnc_transcripts(parsed_transcripts):
    # GIVEN iterable with parsed transcripts

    # WHEN building transcript objects
    for tx_id in parsed_transcripts:
        tx_info = parsed_transcripts[tx_id]
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
