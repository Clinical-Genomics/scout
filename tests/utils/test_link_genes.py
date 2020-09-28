from scout.utils.link import link_genes, add_ensembl_info
from pprint import pprint as pp


def test_link_genes(
    genes37_handle,
    hgnc_handle,
    exac_handle,
    mim2gene_handle,
    genemap_handle,
    hpo_genes_handle,
):
    """docstring for test_link_genes"""
    genes = link_genes(
        ensembl_lines=genes37_handle,
        hgnc_lines=hgnc_handle,
        exac_lines=exac_handle,
        mim2gene_lines=mim2gene_handle,
        genemap_lines=genemap_handle,
        hpo_lines=hpo_genes_handle,
    )
    for hgnc_id in genes:
        gene_obj = genes[hgnc_id]
        assert gene_obj["hgnc_symbol"]
        assert gene_obj["hgnc_id"]
        assert gene_obj["chromosome"]
        assert gene_obj["start"]
        assert gene_obj["end"]

        assert gene_obj["hgnc_symbol"] in gene_obj["previous_symbols"]


def test_link_genes_no_omim(genes37_handle, hgnc_handle, exac_handle, hpo_genes_handle):
    ## GIVEN gene informtation without OMIM
    ## WHEN linking the information from the different sources
    genes = link_genes(
        ensembl_lines=genes37_handle,
        hgnc_lines=hgnc_handle,
        exac_lines=exac_handle,
        hpo_lines=hpo_genes_handle,
    )
    ## THEN assert that it works even without omim
    for hgnc_id in genes:
        gene_obj = genes[hgnc_id]
        assert gene_obj["hgnc_symbol"]
        assert gene_obj["hgnc_id"]
        assert gene_obj["chromosome"]
        assert gene_obj["start"]
        assert gene_obj["end"]

        assert gene_obj["hgnc_symbol"] in gene_obj["previous_symbols"]


def test_add_ensembl_info():
    ## GIVEN a dictionary with genes and some ensembl lines
    ensembl_lines = [
        "Chromosome/scaffold name\tGene start (bp)\tGene end (bp)\tGene stable ID\tHGNC symbol\tHGNC ID",
        "1\t100\t150\tENSG01\tAAA\t1",
    ]
    genes = {1: {"hgnc_id": 1}}
    ## WHEN adding ensembl info to the genes
    add_ensembl_info(genes, ensembl_lines)

    ## THEN check that the coordinates where added
    assert genes[1]["chromosome"] == "1"
    assert genes[1]["start"] == 100
    assert genes[1]["end"] == 150
    assert genes[1]["ensembl_gene_id"] == "ENSG01"


def test_add_ensembl_info_no_hgnc_id():
    ## GIVEN a dictionary with genes and ensembl info without hgnc id
    ensembl_lines = [
        "Chromosome/scaffold name\tGene start (bp)\tGene end (bp)\tGene stable ID\tHGNC symbol\tHGNC ID",
        "1\t100\t150\tENSG01\tAAA\t",
    ]
    genes = {1: {"hgnc_id": 1}}
    ## WHEN adding ensembl info to the genes
    add_ensembl_info(genes, ensembl_lines)

    ## THEN check that the coordinates where not added
    assert "chromosome" not in genes[1]
    assert "start" not in genes[1]
    assert "end" not in genes[1]
    assert "ensembl_gene_id" not in genes[1]
