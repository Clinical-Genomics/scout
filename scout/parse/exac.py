import logging
from pprint import pprint as pp

logger = logging.getLogger(__name__)


def parse_exac_line(line, header):
    """Parse an exac formated line

    Args:
        line(list): A list with exac gene info
        header(list): A list with the header info

    Returns:
        exac_info(dict): A dictionary with the relevant info
    """
    exac_gene = {}
    splitted_line = line.rstrip().split("\t")
    exac_gene = dict(zip(header, splitted_line))
    exac_gene["hgnc_symbol"] = exac_gene["gene"]
    exac_gene["pli_score"] = float(exac_gene["pLI"])
    exac_gene["raw"] = line

    return exac_gene


def parse_exac_genes(lines):
    """Parse lines with exac formated genes

    This is designed to take a dump with genes from exac.
    This is downloaded from:
        ftp.broadinstitute.org/pub/ExAC_release//release0.3/functional_gene_constraint/
        fordist_cleaned_exac_r03_march16_z_pli_rec_null_data.txt

    Args:
        lines(iterable(str)): An iterable with ExAC formated genes
    Yields:
        exac_gene(dict): A dictionary with the relevant information
    """
    header = []
    logger.info("Parsing exac genes...")
    for index, line in enumerate(lines):
        if index == 0:
            header = line.rstrip().split("\t")
        elif len(line) > 10:
            exac_gene = parse_exac_line(line, header)

            yield exac_gene
