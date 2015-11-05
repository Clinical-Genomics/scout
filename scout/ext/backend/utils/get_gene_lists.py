import logging
import click

from scout.models import GenePanel
from pprint import pprint as pp

logger = logging.getLogger(__name__)

def get_gene_lists(list_lines, institute):
    """Parse a gene list file and return a list of GenePanels
    
        Args:
            list_lines (iterator): An iterable with gene list lines
            institute (str): The name of the institute
        
        Returns:
            panels (list(GenePanel))
    """
    version = ""
    panels = []
    header = []
    gene_lists = {}

    for line in list_lines:
        line = line.rstrip()
        if line.startswith('#'):
            if line.startswith('##'):
                if "Database" in line:
                    line = line[2:].split(',')
                    complete_name = ''
                    for annotation in line:
                        if 'Acronym' in annotation:
                            panel_name = annotation.split('=')[-1]
                        elif 'Version' in annotation:
                            version = annotation.split('=')[-1]
                        elif 'Date' in annotation:
                            date = annotation.split('=')[-1]
                        elif 'Complete_name' in annotation:
                            complete_name = annotation.split('=')[-1]
                    if not complete_name:
                        complete_name = panel_name
                    
                    gene_lists[panel_name] = {}
                    gene_lists[panel_name]['version'] = version
                    gene_lists[panel_name]['panel_name'] = panel_name
                    gene_lists[panel_name]['date'] = date
                    gene_lists[panel_name]['complete_name'] = complete_name
                    gene_lists[panel_name]['genes'] = []
            else:
                header = line[1:].split('\t')
        else:
            line = line.split('\t')
            gene_info = dict(zip(header, line))
            gene_panels = gene_info.get('Clinical_db_gene_annotation','').split(',')
            hgnc_symbols = gene_info.get('HGNC_symbol','').split(',')
            for panel in gene_panels:
                for hgnc_symbol in hgnc_symbols:
                    gene_lists[panel]['genes'].append(hgnc_symbol)
    
    for panel in gene_lists:
        entry = gene_lists[panel]
        new_panel = GenePanel(
            institute = institute,
            panel_name = entry['panel_name'],
            version = float(entry['version']),
            date = entry['date'],
            display_name = entry['complete_name'],
        )

        new_panel['genes'] = entry['genes']
        
        panels.append(new_panel)
    
    return panels
    
@click.command()
@click.argument('gene_list',
            type=click.File('r'),
)
def cli(gene_list):
    """docstring for cli"""
    gene_panels = get_gene_lists(gene_list, 'CMMS')
    for panel in gene_panels:
        print(panel.panel_name)
        print(panel.display_name)

if __name__ == '__main__':
    cli()