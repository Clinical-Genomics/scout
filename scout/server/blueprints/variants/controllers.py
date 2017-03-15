# -*- coding: utf-8 -*-


def variants(store, variants_query):
    """Pre-process list of variants."""
    for variant_obj in variants_query:
        variant_genes = variant_obj.get('genes')
        if variant_genes is not None:
            gene_data = get_predictions(variant_genes)
            variant_obj.update(gene_data)
        yield variant_obj


def get_predictions(genes):
    """Get sift predictions from genes."""
    data = {
        'sift_predictions': [],
        'polyphen_predictions': [],
    }
    for gene in genes:
        for pred_key in data.keys():
            gene_key = pred_key[:-1]
            if len(genes) == 1:
                value = gene.get(gene_key, '-')
            else:
                value = ':'.join([gene['hgnc_symbol'], gene.get(gene_key, '-')])
            data[pred_key].append(value)
    return data
