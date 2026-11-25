from scout.load.disease import load_disease_terms


def test_load_disease_terms(
    gene_database,
    genemap_handle,
    orpha_to_hpo_lines,
    orpha_to_genes_lines,
    orpha_inheritance_lines,
    hpo_terms_handle,
    clingen_disease_lines,
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
        hpo_annotation_lines=hpo_terms_handle,
        orpha_to_genes_lines=orpha_to_genes_lines,
        orpha_to_hpo_lines=orpha_to_hpo_lines,
        orpha_inheritance_lines=orpha_inheritance_lines,
        clingen_disease_lines=clingen_disease_lines,
    )

    # THEN make sure that the disease terms are in the database
    disease_objs = adapter.disease_terms()

    assert len([disease for disease in disease_objs]) > 0

    # THEN ClinGen MONDO terms are loaded with their gene-disease validity curations
    mondo_term = adapter.disease_term("MONDO:0018544", filter_project={})
    assert mondo_term["source"] == "MONDO"
    assert mondo_term["genes"] == [61]
    assert mondo_term["inheritance"] == ["XL"]
    assert mondo_term["clingen_gene_validity"][0]["classification"] == "Definitive"
