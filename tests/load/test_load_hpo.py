from scout.load.hpo import load_hpo_terms


def test_load_hpo_terms(gene_database, hpo_terms_handle, hpo_disease_handle):
    adapter = gene_database
    alias_genes = adapter.genes_by_alias()

    # GIVEN a populated database with genes but no hpo terms
    assert len([term for term in adapter.hpo_terms()]) == 0
    assert len([gene for gene in adapter.all_genes()]) > 0

    # WHEN loading the hpo terms
    load_hpo_terms(
        adapter=adapter,
        hpo_lines=hpo_terms_handle,
        hpo_gene_lines=hpo_disease_handle,
        alias_genes=alias_genes,
    )

    # THEN make sure that the disease terms are in the database
    hpo_terms_objs = adapter.hpo_terms()
    assert len([term for term in hpo_terms_objs]) > 0
