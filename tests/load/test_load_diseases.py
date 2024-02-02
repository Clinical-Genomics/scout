from scout.load.disease import load_disease_terms


def test_load_disease_terms(
    gene_database, genemap_handle, orpha_to_hpo_lines, orpha_to_genes_lines, orpha_inheritance_lines
):
    adapter = gene_database
    alias_genes = adapter.genes_by_alias()
    # GIVEN a populated database with genes and no disease terms
    assert len([term for term in adapter.disease_terms()]) == 0

    # WHEN loading the disease terms
    load_disease_terms(
        adapter=adapter,
        genemap_lines=genemap_handle,
        genes=alias_genes,
        orpha_to_genes_lines=orpha_to_genes_lines,
        orpha_to_hpo_lines=orpha_to_hpo_lines,
        orpha_inheritance_lines=orpha_inheritance_lines,
    )

    # THEN make sure that the disease terms are in the database
    disease_objs = adapter.disease_terms()

    assert len([disease for disease in disease_objs]) > 0
