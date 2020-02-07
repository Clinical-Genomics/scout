from scout.utils.gene import get_correct_gene


def test_get_correct_gene(genes):
    """Test that the get_correct_gene returns the right gene"""

    # GIVEN a list of genes
    gene_list = list(genes.values())
    assert len(gene_list) > 0

    # And a random gene from the list
    random_gene = gene_list[2]

    # THEN the get_correct_gene function should return that gene
    returned_gene = get_correct_gene(random_gene["hgnc_symbol"], gene_list)
    assert returned_gene == random_gene
