import logging

logger = logging.getLogger(__name__)


def parse_hgnc_genes(lines):
    """Read the genes from a hgnc file and create objects for hgnc map"""
    header = []
    for index, line in enumerate(lines):
        line = line.rstrip().split('\t')
        if index == 0:
            header = line
        else:
            hgnc_gene = {}
            aliases = []
            raw_info = dict(zip(header, line))
            if not 'Withdrawn' in raw_info['status']:
                hgnc_symbol = raw_info['symbol']
                hgnc_gene['hgnc_symbol'] = hgnc_symbol
                aliases.append(hgnc_symbol)
                
                previous_names = raw_info['prev_symbol'].strip('"')
                if previous_names:
                    for alias in previous_names.split('|'):
                        aliases.append(alias)
                hgnc_gene['aliases'] = aliases
                
                yield hgnc_gene
