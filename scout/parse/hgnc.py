import logging

logger = logging.getLogger(__name__)


def parse_hgnc_line(line, header):
    """Parse an hgnc formated line

        Args:
            line(list): A list with hgnc gene info
            header(list): A list with the header info

        Returns:
            hgnc_info(dict): A dictionary with the relevant info
    """
    hgnc_gene = {}
    line = line.rstrip().split('\t')
    raw_info = dict(zip(header, line))
    if 'Withdrawn' not in raw_info['status']:
        hgnc_symbol = raw_info['symbol']
        hgnc_gene['hgnc_symbol'] = hgnc_symbol
        hgnc_gene['hgnc_id'] = int(raw_info['hgnc_id'].split(':')[-1])
        hgnc_gene['description'] = raw_info['name']
        # We want to have the current symbol as an alias
        aliases = set([hgnc_symbol, hgnc_symbol.upper()])
        # We then need to add both the previous symbols and
        # alias symbols
        previous_names = raw_info['prev_symbol']
        if previous_names:
            for alias in previous_names.strip('"').split('|'):
                aliases.add(alias)

        alias_symbols = raw_info['alias_symbol']
        if alias_symbols:
            for alias in alias_symbols.strip('"').split('|'):
                aliases.add(alias)

        hgnc_gene['previous'] = list(aliases)

        omim_id = raw_info.get('omim_id')
        if omim_id:
            hgnc_gene['omim_ids'] = omim_id.strip('"').split('|')
        else:
            hgnc_gene['omim_ids'] = []

        entrez_id = hgnc_gene['entrez_id'] = raw_info.get('entrez_id')
        if entrez_id:
            hgnc_gene['entrez_id'] = int(entrez_id)
        else:
            hgnc_gene['entrez_id'] = None

        ref_seq = raw_info.get('refseq_accession')
        if ref_seq:
            hgnc_gene['ref_seq'] = ref_seq.strip('"').split('|')
        else:
            hgnc_gene['ref_seq'] = []

        uniprot_ids = raw_info.get('uniprot_ids')
        if uniprot_ids:
            hgnc_gene['uniprot_ids'] = uniprot_ids.strip('""').split('|')
        else:
            hgnc_gene['uniprot_ids'] = []

        ucsc_id = raw_info.get('ucsc_id')
        if ucsc_id:
            hgnc_gene['ucsc_id'] = ucsc_id
        else:
            hgnc_gene['ucsc_id'] = None

        vega_id = raw_info.get('vega_id')
        if vega_id:
            hgnc_gene['vega_id'] = vega_id
        else:
            hgnc_gene['vega_id'] = None

    return hgnc_gene


def parse_hgnc_genes(lines):
    """Parse lines with hgnc formated genes

        This is designed to take a dump with genes from HGNC.
        This is downloaded from:
        ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/hgnc_complete_set.txt

        Args:
            lines(iterable(str)): An iterable with HGNC formated genes
        Yields:
            hgnc_gene(dict): A dictionary with the relevant information
    """
    header = []
    logger.info("Parsing hgnc genes...")
    for index, line in enumerate(lines):
        if index == 0:
            header = line.split('\t')
        else:
            hgnc_gene = parse_hgnc_line(line=line, header=header)
            if hgnc_gene:
                yield hgnc_gene
