from scout.load.hpo import load_disease_terms, load_hpo, load_hpo_terms
from scout.utils.handle import get_file_handle


def test_load_disease_terms(gene_database, genemap_file, hpo_disease_handle):
    adapter = gene_database
    alias_genes = adapter.genes_by_alias()

    # GIVEN a populated database with genes and no disease terms
    assert len([term for term in adapter.disease_terms()]) == 0
    genemap_handle = get_file_handle(genemap_file)

    # WHEN loading the disease terms
    load_disease_terms(
        adapter=adapter,
        genemap_lines=genemap_handle,
        genes=alias_genes,
        hpo_disease_lines=hpo_disease_handle,
    )

    # THEN make sure that the disease terms are in the database
    disease_objs = adapter.disease_terms()

    assert len([disease for disease in disease_objs]) > 0


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


def test_load_hpo(
    gene_database,
    hpo_terms_handle,
    hpo_disease_handle,
    genemap_file,
):
    adapter = gene_database

    # GIVEN a populated database with genes but no hpo terms
    assert len([term for term in adapter.hpo_terms()]) == 0
    genemap_handle = get_file_handle(genemap_file)

    # WHEN loading the disease and hpo terms
    load_hpo(
        adapter=gene_database,
        hpo_lines=hpo_terms_handle,
        hpo_gene_lines=hpo_disease_handle,
        disease_lines=genemap_handle,
    )

    # THEN make sure that the disease terms are in the database
    hpo_terms_objs = adapter.hpo_terms()
    disease_objs = adapter.disease_terms()

    assert len([term for term in hpo_terms_objs]) > 0
    assert len([disease for disease in disease_objs]) > 0
