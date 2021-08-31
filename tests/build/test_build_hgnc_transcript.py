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


@pytest.mark.parametrize(
    "key", ["hgnc_id", "transcript_start", "transcript_end", "chrom", "ensembl_transcript_id"]
)
def test_build_hgnc_transcripts_missing_key(transcript_info, key):
    ## GIVEN a dictionary with transcript information

    # WHEN key is deleted from dict
    transcript_info.pop(key)
    # THEN calling build_transcript() will raise KeyError
    with pytest.raises(KeyError):
        build_transcript(transcript_info)


@pytest.mark.parametrize("key", ["hgnc_id", "transcript_start", "transcript_end"])
def test_build_hgnc_transcript_inappropriate_type(transcript_info, key):
    ## GIVEN a dictionary with transcript information

    # WHEN setting key to None
    transcript_info[key] = None
    # THEN calling build_transcript() will raise TypeError
    with pytest.raises(TypeError):
        build_transcript(transcript_info)
