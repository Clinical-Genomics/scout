# -*- coding: utf-8 -*-


def variants(store, variants_query, page=1, per_page=50):
    """Pre-process list of variants."""
    variant_count = variants_query.count()
    skip_count = per_page * max(page - 1, 0)
    more_variants = True if variant_count > (skip_count + 50) else False

    return {
        'variants': (parse_variant(variant_obj) for variant_obj in
                     variants_query.skip(skip_count).limit(per_page)),
        'more_variants': more_variants,
    }


def parse_variant(variant_obj):
    """Parse information about variants."""
    variant_genes = variant_obj.get('genes')
    if variant_genes is not None:
        gene_data = get_predictions(variant_genes)
        variant_obj.update(gene_data)
    return variant_obj


def get_predictions(genes):
    """Get sift predictions from genes."""
    data = {
        'sift_predictions': [],
        'polyphen_predictions': [],
        'region_annotations': [],
        'functional_annotations': [],
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
