from pprint import pprint as pp

from scout.load.hgnc_gene import load_hgnc_genes


def test_load_hgnc_genes(
    adapter,
    genes37_handle,
    hgnc_handle,
    exac_handle,
    mim2gene_handle,
    genemap_handle,
    hpo_genes_handle,
):
    # GIVEN a empty database
    assert sum(1 for i in adapter.all_genes()) == 0

    # WHEN inserting a number of genes
    gene_objects = load_hgnc_genes(
        adapter,
        ensembl_lines=genes37_handle,
        hgnc_lines=hgnc_handle,
        exac_lines=exac_handle,
        mim2gene_lines=mim2gene_handle,
        genemap_lines=genemap_handle,
        hpo_lines=hpo_genes_handle,
        build="37",
    )

    nr_genes = 0
    for gene_info in gene_objects:
        if gene_info.get("chromosome"):
            nr_genes += 1

    # THEN assert all genes have been added to the database
    assert sum(1 for i in adapter.all_genes()) == nr_genes

    # THEN assert that the last gene was loaded
    assert adapter.hgnc_gene(gene_info["hgnc_id"])


def test_load_hgnc_genes_no_omim(
    adapter, genes37_handle, hgnc_handle, exac_handle, hpo_genes_handle
):
    # GIVEN a empty database
    assert sum(1 for i in adapter.all_genes()) == 0

    # WHEN inserting a number of genes
    gene_objects = load_hgnc_genes(
        adapter,
        ensembl_lines=genes37_handle,
        hgnc_lines=hgnc_handle,
        exac_lines=exac_handle,
        hpo_lines=hpo_genes_handle,
        build="37",
    )

    nr_genes = 0
    for gene_info in gene_objects:
        if gene_info.get("chromosome"):
            nr_genes += 1

    # THEN assert all genes have been added to the database
    assert sum(1 for i in adapter.all_genes()) == nr_genes

    # THEN assert that the last gene was loaded
    assert adapter.hgnc_gene(gene_info["hgnc_id"])
