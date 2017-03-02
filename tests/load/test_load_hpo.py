from scout.load.hpo import (load_hpo, load_disease_terms, load_hpo_terms)

def test_load_disease_terms(adapter, genemap_handle):
    # GIVEN a populated database with genes and no disease terms
    assert adapter.disease_terms().count() == 0

    # WHEN loading the disease terms
    load_disease_terms(
        adapter=adapter,
        genemap_lines=genemap_handle, 
    )

    # THEN make sure that the disease terms are in the database
    disease_objs = adapter.disease_terms()
    assert disease_objs.count() > 0
    

def test_load_hpo_terms(adapter, hpo_terms_handle):
    # GIVEN a populated database with genes
    assert adapter.hpo_terms().count() == 0
    assert adapter.all_genes().count() > 0
    
    # WHEN loading the disease terms
    load_hpo_terms(
        adapter=adapter, 
        hpo_lines=hpo_terms_handle, 
    )
    
    # THEN make sure that the disease terms are in the database
    hpo_terms_objs = adapter.hpo_terms()
    assert hpo_terms_objs.count() > 0

def test_load_hpo(adapter, hpo_terms_handle, genemap_handle):
    # GIVEN a populated database with genes
    assert gene_database.hpo_terms().count() == 0

    # WHEN loading the disease and hpo terms
    load_hpo(
        adapter=gene_database,
        hpo_lines=hpo_terms_handle,
        disease_lines=genemap_handle
    )

    # THEN make sure that the disease terms are in the database
    hpo_terms_objs = gene_database.hpo_terms()
    disease_objs = gene_database.disease_terms()

    assert hpo_terms_objs.count() > 0
    assert disease_objs.count() > 0
#