# -*- coding: utf-8 -*-


def gene(store, hgnc_id):
    """Parse information about a gene."""
    res = {'builds': {'37': None, '38': None}, 'symbol': None, 'description': None, 'ensembl_id': None}
    
    for build in res['builds']:
        record = store.hgnc_gene(hgnc_id, build=build)
        if record:
            record['position'] = "{this[chromosome]}:{this[start]}-{this[end]}".format(this=record)
            res['builds'][build] = record
            res['symbol'] = record['hgnc_symbol']
            res['description'] = record['description']
            res['ensembl_id'] = record['ensembl_id']
            
            for transcript in record['transcripts']:
                transcript['position'] = ("{chrom}:{this[start]}-{this[end]}"
                                          .format(chrom=record['chromosome'], this=transcript))
    
    # If none of the genes where found
    if not any(res.values()):
        raise ValueError

    return res



def genes_to_json(store, query):
    """Fetch matching genes and convert to JSON."""
    gene_query = store.hgnc_genes(query, search=True)
    json_terms = [{'name': "{} | {} ({})".format(gene['hgnc_id'], gene['hgnc_symbol'],
                                                 ', '.join(gene['aliases'])),
                   'id': gene['hgnc_id']} for gene in gene_query]
    return json_terms
