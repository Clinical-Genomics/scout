# -*- coding: utf-8 -*-


def gene(record):
    """Parse information about a gene."""
    record['position'] = ("{this[chromosome]}:{this[start]}-{this[end]}".format(this=record))


def genes_to_json(store, query):
    """Fetch matching genes and convert to JSON."""
    gene_query = store.hgnc_genes(query, search=True)
    json_terms = [{'name': "{} | {} ({})".format(gene['hgnc_id'], gene['hgnc_symbol'],
                                                 ', '.join(gene['aliases'])),
                   'id': gene['hgnc_id']} for gene in gene_query]
    return json_terms
