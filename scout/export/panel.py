# -*- coding: utf-8 -*-
CHROMOSOMES = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
               '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 'X',
               'Y', 'MT')


def export_panels(adapter, panels):
    """Export all genes in gene panels"""
    headers = []
    header_string = ("##gene_panel={0},version={1},updated_at={2},display_name={3}")
    contig_string = ("##contig={0}")
    bed_string = ("{0}\t{1}\t{2}\t{3}\t{4}")
    genes = {}
    chromosomes_found = set()
    for panel_id in panels:
        panel_obj = adapter.gene_panel(panel_id)
        headers.append(header_string.format(
            panel_obj.panel_name,
            panel_obj.version,
            panel_obj.date.date(),
            panel_obj.display_name,
        ))
        for gene_symbol in panel_obj.gene_objects:
            gene_obj = panel_obj.gene_objects[gene_symbol]
            genes[gene_symbol] = gene_obj
            chromosomes_found.add(gene_obj.hgnc_gene.chromosome)

    for chrom in CHROMOSOMES:
        if chrom in chromosomes_found:
            headers.append(contig_string.format(chrom))

    headers.append("#chromosome\tgene_start\tgene_stop\thgnc_id\thgnc_symbol")

    for header in headers:
        print(header)

    for gene_symbol in genes:
        gene_obj = genes[gene_symbol]
        hgnc_gene = gene_obj.hgnc_gene
        print(bed_string.format(
            hgnc_gene.chromosome,
            hgnc_gene.start,
            hgnc_gene.end,
            hgnc_gene.id,
            hgnc_gene.hgnc_symbol,
        ))
