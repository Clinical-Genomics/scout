from pprint import pprint as pp
from scout.load.transcript import load_transcripts

def test_load_transcripts(adapter, gene_bulk, transcripts_handle):
    # GIVEN a empty database
    assert adapter.all_genes().count() == 0
    assert adapter.transcripts().count() == 0
    
    # WHEN inserting a number of genes and some transcripts
    adapter.load_hgnc_bulk(gene_bulk)

    load_transcripts(adapter, transcripts_lines=transcripts_handle, build='37')

    # THEN assert all genes have been added to the database
    assert adapter.all_genes().count() == len(gene_bulk)
    
    # THEN assert that the transcripts where loaded loaded
    assert adapter.transcripts().count() > 0

def test_load_transcripts_request(adapter, gene_bulk, transcripts_df):
    # GIVEN a empty database
    assert adapter.all_genes().count() == 0
    assert adapter.transcripts().count() == 0
    
    # WHEN inserting a number of genes and some transcripts
    adapter.load_hgnc_bulk(gene_bulk)

    load_transcripts(adapter, transcripts_lines=transcripts_df, build='37')

    # THEN assert all genes have been added to the database
    assert adapter.all_genes().count() == len(gene_bulk)
    
    # THEN assert that the transcripts where loaded loaded
    assert adapter.transcripts().count() > 0
