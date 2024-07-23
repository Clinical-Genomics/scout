from scout.load.hgnc_gene import load_hgnc_genes, set_missing_gene_coordinates


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
    assert sum(1 for _ in adapter.all_genes()) == 0

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
    assert sum(1 for _ in adapter.all_genes()) == nr_genes

    # THEN assert that the last gene was loaded
    assert adapter.hgnc_gene(gene_info["hgnc_id"])


def test_load_hgnc_genes_no_omim(
    adapter, genes37_handle, hgnc_handle, exac_handle, hpo_genes_handle
):
    # GIVEN a empty database
    assert sum(1 for _ in adapter.all_genes()) == 0

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
    assert sum(1 for _ in adapter.all_genes()) == nr_genes

    # THEN assert that the last gene was loaded
    assert adapter.hgnc_gene(gene_info["hgnc_id"])


def test_set_missing_gene_coordinates():
    """Test function that sets coordinates for genes without ensembl_gene_id."""

    # GIVEN a gene with blank ensembl_gene_id key:
    gene_dict = {
        "hgnc_id": 5477,
        "hgnc_symbol": "IGH",
        "ensembl_gene_id": "",
        "location": "14q32.33",
    }

    # GIVEN cytoband coordinates containing that specific band:
    cytoband_coords = {"14q32.33": {"chromosome": "14", "start": 104000001, "stop": 107349541}}

    # THEN the set_gene_coordinates function should set coordinates to the genes:
    set_missing_gene_coordinates(gene_data=gene_dict, cytoband_coords=cytoband_coords)

    for coord in ["chromosome", "start", "end"]:
        assert coord in gene_dict

    # THEN Ensembl ID should also be set to None
    assert gene_dict["ensembl_gene_id"] is None
