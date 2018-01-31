# -*- coding: utf-8 -*-
import logging

from scout.constants import CHROMOSOMES
LOG = logging.getLogger(__name__)


def export_panels(adapter, panels, versions=None):
    """Export all genes in gene panels
    
    Exports the union of genes in one or several gene panels to a bed like format with coordinates.
    
    Args:
    """
    if versions and (len(versions) != len(panels)):
        raise SyntaxError("If version specify for each panel")

    headers = []
    header_string = ("##gene_panel={0},version={1},updated_at={2},display_name={3}")
    contig_string = ("##contig={0}")
    bed_string = ("{0}\t{1}\t{2}\t{3}\t{4}")

    panel_geneids = set()
    chromosomes_found = set()
    hgnc_geneobjs = []

    for i,panel_id in enumerate(panels):
        version = None
        if versions:
            version = versions[i]
            
        panel_obj = adapter.gene_panel(panel_id, version=version)
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
            LOG.warn("missing HGNC gene: %s", hgnc_id)
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

def export_gene_panels(adapter, panels, version=None):
    """Export the genes of a gene panel
    
    Takes a list of gene panel names and return the lines of the gene panels.
    Unlike export_panels this function only export the genes and extra information, 
    not the coordinates.
    
    Args:
        adapter(MongoAdapter)
        panels(list(str))
        version(float): Version number, only works when one panel
    
    Yields:
        gene panel lines
    """
    if version and len(panels) > 1:
        raise SyntaxError("Version only possible with one panel")

    bed_string = ("{0}\t{1}\t{2}\t{3}\t{4}\t{5}")
    
    headers = []

    # Dictionary with hgnc ids as keys and panel gene information as value.
    panel_geneobjs = dict()

    for panel_id in panels:
        panel_obj = adapter.gene_panel(panel_id, version=version)
        if not panel_obj:
            LOG.warning("Panel %s could not be found", panel_id)
            continue

        for gene_obj in panel_obj['genes']:
            panel_geneobjs[gene_obj['hgnc_id']] = gene_obj

    if len(panel_geneobjs) == 0:
        return

    headers.append('#hgnc_id\thgnc_symbol\tdisease_associated_transcripts\t'
                    'reduced_penetrance\tmosaicism\tdatabase_entry_version')

    for header in headers:
        yield header

    for hgnc_id in panel_geneobjs:
        gene_obj = panel_geneobjs[hgnc_id]
        gene_line = bed_string.format(
            gene_obj['hgnc_id'], gene_obj['symbol'],
            ','.join(gene_obj.get('disease_associated_transcripts', [])),
            gene_obj.get('reduced_penetrance', ''),
            gene_obj.get('mosaicism', ''),
            gene_obj.get('database_entry_version', ''),
        )
        yield gene_line
    