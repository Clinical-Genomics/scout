from pprint import pprint as pp

import pymongo

from scout.load.exon import load_exons
from scout.load.transcript import load_transcripts
from scout.utils.handle import get_file_handle


def test_load_exons(adapter, gene_bulk, transcripts_file, exons_handle):
    # GIVEN a empty database
    assert sum(1 for i in adapter.all_genes()) == 0
    assert sum(1 for i in adapter.transcripts()) == 0
    assert sum(1 for i in adapter.exons()) == 0

    # WHEN inserting a number of genes and some transcripts and the exons
    adapter.load_hgnc_bulk(gene_bulk)

    transcripts_handle = get_file_handle(transcripts_file)
    load_transcripts(adapter, transcripts_handle, build="37")

    adapter.transcript_collection.create_index(
        [("build", pymongo.ASCENDING), ("hgnc_id", pymongo.ASCENDING)]
    )

    load_exons(adapter, exons_handle, build="37", nr_exons=19826)

    assert sum(1 for i in adapter.exons()) > 1
