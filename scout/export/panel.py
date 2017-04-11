# -*- coding: utf-8 -*-
import logging

CHROMOSOMES = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
               '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 'X',
               'Y', 'MT')
log = logging.getLogger(__name__)


def export_panels(adapter, panels):
    """Export all genes in gene panels"""
    headers = []
    header_string = ("##gene_panel={0},version={1},updated_at={2},display_name={3}")
    contig_string = ("##contig={0}")
    bed_string = ("{0}\t{1}\t{2}\t{3}\t{4}")

    panel_geneids = set()
    chromosomes_found = set()
    hgnc_geneobjs = []

    for panel_id in panels:
        panel_obj = adapter.gene_panel(panel_id)
        headers.append(header_string.format(
            panel_obj['panel_name'],
            panel_obj['version'],
            panel_obj['date'].date(),
            panel_obj['display_name'],
        ))
        for gene_obj in panel_obj['genes']:
            panel_geneids.add(gene_obj['hgnc_id'])

    for hgnc_id in panel_geneids:
        hgnc_geneobj = adapter.hgnc_gene(hgnc_id)
        if hgnc_geneobj is None:
            log.warn("missing HGNC gene: %s", hgnc_id)
            continue
        hgnc_geneobjs.append(hgnc_geneobj)
        chromosomes_found.add(hgnc_geneobj['chromosome'])

    for chrom in CHROMOSOMES:
        if chrom in chromosomes_found:
            headers.append(contig_string.format(chrom))

    headers.append("#chromosome\tgene_start\tgene_stop\thgnc_id\thgnc_symbol")

    for header in headers:
        yield header

    for hgnc_gene in hgnc_geneobjs:
        gene_line = bed_string.format(hgnc_gene['chromosome'], hgnc_gene['start'],
                                      hgnc_gene['end'], hgnc_gene['hgnc_id'],
                                      hgnc_gene['hgnc_symbol'])
        yield gene_line
