from pprint import pprint as pp

from scout.build.genes.transcript import build_transcript
import pytest

def test_build_hgnc_transcripts(transcripts):
    # GIVEN iterable with parsed transcripts
    
    # WHEN building transcript objects
    for tx_info in transcripts:
        pp(tx_info)
        tx_obj = build_transcript(tx_info)

        # THEN check that the gene models have a hgnc id
        assert tx_obj['ensembl_gene_id']

# def test_build_hgnc_gene():
#     gene_info = {
#         'hgnc_id': 100,
#         'hgnc_symbol': 'TEST',
#         'ensembl_gene_id': 'ENSTEST',
#         'chromosome': '1',
#         'start': 1,
#         'end': 1000,
#     }
#     gene_obj = build_hgnc_gene(gene_info)
#
#     assert gene_obj['hgnc_id'] == gene_info['hgnc_id']
#     assert gene_obj['length'] == gene_info['end'] - gene_info['start']
#
# def test_build_hgnc_gene_no_id():
#     gene_info = {
#         'hgnc_symbol': 'TEST',
#         'ensembl_gene_id': 'ENSTEST',
#         'chromosome': '1',
#         'start': 1,
#         'end': 1000,
#     }
#     with pytest.raises(KeyError):
#         gene_obj = build_hgnc_gene(gene_info)
#
# def test_build_hgnc_gene_wrong_id():
#     gene_info = {
#         'hgnc_id': 'test',
#         'hgnc_symbol': 'TEST',
#         'ensembl_gene_id': 'ENSTEST',
#         'chromosome': '1',
#         'start': 1,
#         'end': 1000,
#     }
#     with pytest.raises(ValueError):
#         gene_obj = build_hgnc_gene(gene_info)
