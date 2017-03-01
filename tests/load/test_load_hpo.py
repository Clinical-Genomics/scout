from scout.load.hpo import (load_hpo, load_disease_terms, load_hpo_terms)

# def test_load_disease_terms(gene_database, hpo_disease_handle):
#     """docstring for test_load_disease_terms"""
#     # GIVEN a populated database with genes
#     gene_objs = {}
#     for gene in gene_database.all_genes():
#         gene_objs[gene['hgnc_symbol']] = gene
#
#     assert len(gene_objs) > 0
#
#     # WHEN loading the disease terms
#     load_disease_terms(
#         adapter=gene_database,
#         hpo_disease_lines=hpo_disease_handle,
#         gene_objs=gene_objs
#     )
#
#     # THEN make sure that the disease terms are in the database
#     disease_objs = gene_database.disease_terms()
#     assert disease_objs.count() > 0
    

def test_load_hpo_terms(gene_database, hpo_terms_handle):
    # GIVEN a populated database with genes
    assert gene_database.hpo_terms().count() == 0
    assert gene_database.all_genes().count() > 0
    
    # WHEN loading the disease terms
    load_hpo_terms(
        adapter=gene_database, 
        hpo_lines=hpo_terms_handle, 
    )
    
    # THEN make sure that the disease terms are in the database
    hpo_terms_objs = gene_database.hpo_terms()
    assert hpo_terms_objs.count() > 0

# def test_load_hpo(gene_database, hpo_terms_handle, hpo_disease_handle):
#     # GIVEN a populated database with genes
#     assert gene_database.hpo_terms().count() == 0
#
#     # WHEN loading the disease and hpo terms
#     load_hpo(
#         adapter=gene_database,
#         hpo_lines=hpo_terms_handle,
#         disease_lines=hpo_disease_handle
#     )
#
#     # THEN make sure that the disease terms are in the database
#     hpo_terms_objs = gene_database.hpo_terms()
#     disease_objs = gene_database.disease_terms()
#
#     assert hpo_terms_objs.count() > 0
#     assert disease_objs.count() > 0
    