import logging

LOG = logging.getLogger(__name__)


def get_correct_gene(hgnc_symbol, genes):
    """Check which of the genes in query result that is the correct one

    If there result is ambigous, that is if non of the genes have the hgnc
    symbol as the primary identifier and two or more genes have the symbol
    as an alias, return all of those results.

    Args:
        hgnc_symbol(str)
        genes(iterable[Gene])

    """
    for gene in genes:
        # if one of the gene matches the hgnc symbol return the correct one
        if hgnc_symbol == gene["hgnc_symbol"]:
            return gene


def parse_raw_gene_symbols(raw_symbols_list):
    """Parse list of concatenated gene symbol list for hgnc_symbols from Phenomizer.

    Arguments:
        raw_symbols(list(string)) - e.g. ("POT1 | MUTYH", "POT1 | ATXN1 | ATXN7")

    Returns:
        hgnc_symbols(set(string)) - set of (unique) gene symbols without intervening chars
    """
    hgnc_symbols = set()

    for raw_symbols in raw_symbols_list:
        # avoid empty lists
        if raw_symbols:
            hgnc_symbols.update(
                raw_symbol.split(" ", 1)[0] for raw_symbol in raw_symbols.split("|")
            )
    return hgnc_symbols


def parse_raw_gene_ids(raw_symbols):
    """Parse raw gene symbols for hgnc_symbols from web form autocompletion.

    Arguments:
        raw_symbol_strings(list(string)) - formated "17284 | POT1 (hPot1, POT1)"

    Returns:
        hgnc_ids(set(int))
    Throws:
        ValueError
    """
    hgnc_ids = set()

    for raw_symbol in raw_symbols:
        LOG.debug("raw gene: {}".format(raw_symbol))
        # avoid empty lists
        if raw_symbol:
            # take the first nubmer before |, and remove any space.
            try:
                hgnc_ids.add(int(raw_symbol.split("|", 1)[0].replace(" ", "")))
            except ValueError:
                raise ValueError
    LOG.debug("Parsed HGNC symbols {}".format(hgnc_ids))

    return hgnc_ids
