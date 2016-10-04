import logging
import click

from codecs import open

from scout.models import GenePanel
from pprint import pprint as pp

logger = logging.getLogger(__name__)

def get_gene_panel(list_file_name, institute_id, panel_id, panel_version,
                    display_name, panel_date):
    """Return a GenePanel object

        Args:
            list_file_name(str): The gene list lines
            institute_id(str)
            panel_id(str)
            panel_version(float)
            display_name(str)
            panel_date(str)
    """
    panel = GenePanel(
        institute = institute_id,
        panel_name = panel_id,
        version = panel_version,
        date = panel_date,
        display_name = display_name,
    )
    list_lines = open(list_file_name, 'r')
    genes = get_genes(list_lines, panel_id)
    panel['genes'] = sorted(genes)
    return panel

def get_genes(list_lines, panel_name):
    """Parse a gene list file and return the genes that belongs
        to the panel in question.

        Args:
            list_lines (iterator): An iterable with gene list lines
            panel_name (str): The name of the panel

        Returns:
            genes(list(str)): A list of gene names
    """
    genes = []
    header = []
    for line in list_lines:
        line = line.rstrip()
        if line.startswith('#'):
            if not line.startswith('##'):
                header = line[1:].split('\t')
        else:
            line = line.split('\t')
            gene_info = dict(zip(header, line))
            #These are the panels that the gene belongs to:
            gene_panels = set(gene_info.get('Clinical_db_gene_annotation','').split(','))
            hgnc_symbols = gene_info.get('HGNC_symbol','').split(',')
            chromosome = gene_info.get('Chromosome')
            start = int(gene_info.get('Gene_start', '0'))
            stop = int(gene_info.get('Gene_stop', '0'))
            ensembl_gene_id = gene_info.get('Ensembl_gene_id')
            description = gene_info.get('Gene_description')
            locus = gene_info.get('Gene_locus')
            # mim_id = gene_info.get('Gene_stop', '0')
            # if mim_id:
            #     mim_id = int(mim_id)
            protein_name = gene_info.get('Protein_name')
            reduced_penetrance = gene_info.get('Reduced_penetrance')
            if reduced_penetrance:
                reduced_penetrance = True
            else:
                reduced_penetrance = False

            if panel_name in gene_panels:
                for hgnc_symbol in hgnc_symbols:
                    genes.append(hgnc_symbol)

    return genes

@click.command()
@click.argument('gene_list',
            type=click.Path(),
)
@click.option('-p', '--panel_name',
            default='FullList',
)
def cli(gene_list, panel_name):
    """docstring for cli"""
    # with open(gene_list, 'r') as list_lines:
    #     genes = get_genes(list_lines, panel_name)
    #     for gene in genes:
    #         print(gene)
    panel = get_gene_panel(
        list_file_name=gene_list,
        institute_id='cust000',
        panel_id=panel_name,
        panel_version=1.0,
        display_name=panel_name,
        panel_date="Today"
    )
    print(panel.panel_name)
    print(panel.genes)
    # for panel in gene_panels:
    #     print(panel.panel_name)
    #     print(panel.display_name)

if __name__ == '__main__':
    cli()
