# -*- coding: utf-8 -*-
import logging

import click

from pprint import pprint as pp

from scout.load import load_panel
from scout.utils.date import get_date
from scout.utils.handle import get_file_handle

log = logging.getLogger(__name__)

@click.command('convert', short_help='Convert gene panels')
@click.argument('panel',
    required=True,
    type=click.Path(exists=True)
)
@click.pass_context
def convert(context, panel):
    """Convert a gene panel with hgnc symbols to a new one with hgnc ids."""
    # date = get_date(date)

    adapter = context.obj['adapter']

    header = []
    new_header = "#hgnc_id\thgnc_symbol\tdisease_associated_transcripts\t"\
                 "reduced_penetrance\tgenetic_disease_models\tmosaicism\t"\
                 "database_entry_version\toriginal_hgnc"

    f = get_file_handle(panel)
    for line in f:
        line = line.rstrip()
        if line.startswith('#'):
            if not line.startswith('##'):
                header = [word.lower() for word in line[1:].split('\t')]
                print(new_header)
            else:
                print(line)
        else:
            correct_gene = None
            correct_info = ("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}")
            genes_found = []
            gene_info = dict(zip(header,line.split('\t')))
            hgnc_symbol = gene_info.get('hgnc_symbol')
            if not hgnc_symbol:
                pass
            result_genes = [gene for gene in adapter.hgnc_genes(hgnc_symbol)]
            
            for gene in result_genes:
                if hgnc_symbol.upper() == gene['hgnc_symbol'].upper():
                    correct_gene = gene
                    #','.join(correct_gene.aliases),
                    print(correct_info.format(
                        correct_gene.id,
                        correct_gene.hgnc_symbol,
                        gene_info.get('disease_associated_transcripts',''),
                        gene_info.get('reduced_penetrance',''),
                        gene_info.get('genetic_disease_models',''),
                        gene_info.get('mosaicism',''),
                        gene_info.get('database_entry_version',''),
                        hgnc_symbol
                    ))

            if not correct_gene:
                    keep = True
                    for gene in result_genes:
                        if not gene.hgnc_symbol:
                            keep = False
                    if keep:
                        print(correct_info.format(
                            ','.join([str(gene.id) for gene in result_genes]),
                            ','.join([gene.hgnc_symbol for gene in result_genes]),
                            gene_info.get('disease_associated_transcripts',''),
                            gene_info.get('reduced_penetrance',''),
                            gene_info.get('genetic_disease_models',''),
                            gene_info.get('mosaicism',''),
                            gene_info.get('database_entry_version',''),
                            hgnc_symbol,
                        ))
