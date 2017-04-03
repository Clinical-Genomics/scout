from scout.load.hpo import (load_hpo, load_disease_terms, load_hpo_terms)

def test_load_disease_terms(gene_database, genemap_handle, hpo_disease_handle):
    adapter = gene_database
    alias_genes = adapter.genes_by_alias()
    
    # GIVEN a populated database with genes and no disease terms
    assert adapter.disease_terms().count() == 0

    # WHEN loading the disease terms
    load_disease_terms(
        adapter=adapter,
        genemap_lines=genemap_handle,
        genes=alias_genes,
        hpo_disease_lines=hpo_disease_handle,
    )

    # THEN make sure that the disease terms are in the database
    disease_objs = adapter.disease_terms()
    assert disease_objs.count() > 0
    

def test_load_hpo_terms(gene_database, hpo_terms_handle):
    adapter = gene_database
    alias_genes = adapter.genes_by_alias()
    # GIVEN a populated database with genes
    assert adapter.hpo_terms().count() == 0
    assert adapter.all_genes().count() > 0
    
    # WHEN loading the disease terms
    load_hpo_terms(
        adapter=adapter, 
        hpo_lines=hpo_terms_handle, 
        genes=alias_genes
    )
    
    # THEN make sure that the disease terms are in the database
    hpo_terms_objs = adapter.hpo_terms()
    assert hpo_terms_objs.count() > 0

def test_load_hpo(gene_database, hpo_terms_handle, genemap_handle, hpo_disease_handle):
    adapter = gene_database
    # GIVEN a populated database with genes
    assert gene_database.hpo_terms().count() == 0

    # WHEN loading the disease and hpo terms
    load_hpo(
        adapter=gene_database,
        hpo_lines=hpo_terms_handle,
        disease_lines=genemap_handle,
        hpo_disease_lines=hpo_disease_handle,
    )

    # THEN make sure that the disease terms are in the database
    hpo_terms_objs = gene_database.hpo_terms()
    disease_objs = gene_database.disease_terms()

    assert hpo_terms_objs.count() > 0
    assert disease_objs.count() > 0
#