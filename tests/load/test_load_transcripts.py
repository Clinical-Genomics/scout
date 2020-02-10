from pprint import pprint as pp
from scout.load.transcript import load_transcripts


def test_load_transcripts(adapter, gene_bulk, transcripts_handle):
    # GIVEN a empty database
    assert sum(1 for i in adapter.all_genes()) == 0
    assert sum(1 for i in adapter.transcripts()) == 0

    # WHEN inserting a number of genes and some transcripts
    adapter.load_hgnc_bulk(gene_bulk)

    load_transcripts(adapter, transcripts_lines=transcripts_handle, build="37")

    # THEN assert all genes have been added to the database
    assert sum(1 for i in adapter.all_genes()) == len(gene_bulk)

    # THEN assert that the transcripts where loaded loaded
    assert sum(1 for i in adapter.transcripts()) > 0
