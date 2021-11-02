from pprint import pprint as pp

from scout.build.genes.hgnc_gene import build_hgnc_gene
import pytest


def test_build_hgnc_genes(genes):
    # GIVEN a dictionary with hgnc genes

    # WHEN building hgnc gene objecs
    for hgnc_id in genes:
        gene_info = genes[hgnc_id]
        gene_obj = build_hgnc_gene(gene_info)
        # THEN check that the gene models have a hgnc id
        assert gene_obj["hgnc_id"]


def test_build_hgnc_gene():
    gene_info = {
        "hgnc_id": 100,
        "hgnc_symbol": "TEST",
        "ensembl_gene_id": "ENSTEST",
        "chromosome": "1",
        "start": 1,
        "end": 1000,
    }
    gene_obj = build_hgnc_gene(gene_info)

    assert gene_obj["hgnc_id"] == gene_info["hgnc_id"]
    assert gene_obj["hgnc_symbol"] == gene_info["hgnc_symbol"]
    assert gene_obj["length"] == gene_info["end"] - gene_info["start"]
    assert gene_obj["ensembl_id"] == gene_info["ensembl_gene_id"]


@pytest.mark.parametrize("key", ["hgnc_id"])
def test_build_hgnc_gene_inappropriate_value(test_gene, key):
    ## GIVEN a dictionary with gene information

    # WHEN setting key to a non-valid value
    test_gene[key] = "cause_error"
    # THEN calling build_hgnc_gene() will raise ValueError
    with pytest.raises(ValueError):
        build_hgnc_gene(test_gene)


@pytest.mark.parametrize("key", ["start", "end"])
def test_build_hgnc_gene_inappropriate_type(test_gene, key):
    ## GIVEN a dictionary with gene information

    # WHEN setting key to None
    test_gene[key] = None
    # THEN calling build_hgnc_gene() will raise TypeError
    with pytest.raises(TypeError):
        build_hgnc_gene(test_gene)


# TODO: are 'ensembl_gene_id' and 'ensembl_id' the same thing? -both seem to be used!
@pytest.mark.parametrize("key", ["hgnc_id", "hgnc_symbol", "chromosome", "start", "end"])
def test_build_hgnc_gene_missing_key(test_gene, key):
    ## GIVEN a dictionary with gene information

    # WHEN deleteing key
    test_gene.pop(key)
    # THEN calling build_hgnc_gene() will raise KeyError
    with pytest.raises(KeyError):
        build_hgnc_gene(test_gene)
