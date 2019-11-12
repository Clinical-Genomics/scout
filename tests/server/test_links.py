from pprint import pprint as pp

from scout.server.links import (add_gene_links)

def test_add_gene_links():
    ## GIVEN a minimal gene and a genome build
    gene_obj = {'hgnc_id': 257}
    build = 37
    ## WHEN adding the gene links
    add_gene_links(gene_obj, build)
    ## THEN assert some links are added
    assert 'hgnc_link' in gene_obj