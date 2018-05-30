import logging

from datetime import datetime
from pprint import pprint as pp

from click import progressbar
from pandas import DataFrame

from scout.parse.ensembl import (parse_ensembl_exons, parse_ensembl_exon_request)
from scout.build.genes.exon import build_exon

LOG = logging.getLogger(__name__)


def load_exons(adapter, exon_lines, build='37', ensembl_genes=None):
    """Load all the exons
    
    Transcript information is from ensembl.
    Check that the transcript that the exon belongs to exists in the database

    Args:
        adapter(MongoAdapter)
        exon_lines(iterable): iterable with ensembl exon lines
        build(str)
        ensembl_transcripts(dict): Existing ensembl transcripts
    
    """
    # Fetch all genes with ensemblid as keys
    ensembl_genes = ensembl_genes or adapter.ensembl_genes(build)
    hgnc_id_transcripts = adapter.id_transcripts_by_gene(build=build)
    
    if isinstance(exon_lines, DataFrame):
        exons = parse_ensembl_exon_request(exon_lines)
        nr_exons = exon_lines.shape[0]
    else:
        exons = parse_ensembl_exons(exon_lines)
        nr_exons = 1000000
    
    start_insertion = datetime.now()
    loaded_exons = 0
    LOG.info("Loading exons...")
    with progressbar(exons, label="Loading exons", length=nr_exons) as bar:
        for exon in bar:
            ensg_id = exon['gene']
            enst_id = exon['transcript']
            gene_obj = ensembl_genes.get(ensg_id)
            
            if not gene_obj:
                continue
            
            hgnc_id = gene_obj['hgnc_id']

            if not enst_id in hgnc_id_transcripts[hgnc_id]:
                continue

            exon['hgnc_id'] = hgnc_id

            exon_obj = build_exon(exon, build)
            adapter.load_exon(exon_obj)
            loaded_exons += 1

    LOG.info('Number of exons in build {0}: {1}'.format(build, nr_exons))
    LOG.info('Number loaded: {0}'.format(loaded_exons))
    LOG.info('Time to load exons: {0}'.format(datetime.now() - start_insertion))
    