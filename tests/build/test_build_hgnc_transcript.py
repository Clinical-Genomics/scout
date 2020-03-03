from pprint import pprint as pp

from scout.build.genes.transcript import build_transcript


def test_build_hgnc_transcripts(parsed_transcripts):
    # GIVEN iterable with parsed transcripts

    # WHEN building transcript objects
    for tx_id in parsed_transcripts:
        tx_info = parsed_transcripts[tx_id]
        tx_obj = build_transcript(tx_info)

        # THEN check that the gene models have a hgnc id
        assert tx_obj["hgnc_id"]
