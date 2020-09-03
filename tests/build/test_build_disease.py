from scout.build.disease import build_disease_term
from scout.models.phenotype_term import DiseaseTerm
import pytest

def test_build_disease_term(adapter, test_disease):
    ## GIVEN some disease info and a adapter with a gene
    alias_genes = {}
    alias_genes["B3GALT6"] = {"true": 17978, "ids": [17978]}

    ## WHEN building the disease term
    disease_obj = build_disease_term(test_disease, alias_genes)

    ## THEN assert the term is on the correct format

    assert disease_obj["_id"] == disease_obj["disease_id"] == "OMIM:615349"
    assert disease_obj["inheritance"] == ["AR"]
    assert disease_obj["genes"] == [17978]
    assert disease_obj["source"] == "OMIM"

    assert isinstance(disease_obj, DiseaseTerm)


@pytest.mark.parametrize("key", ['mim_number', 'description'])
def test_build_disease_missing_key(key, test_disease):
    ## GIVEN a dictionary with disease information and genes
    alias_genes = {}
    alias_genes["B3GALT6"] = {"true": 17978, "ids": [17978]}

    # WHEN deleteing key
    test_disease.pop(key)
    # THEN calling build_disease_term() will raise KeyError
    with pytest.raises(KeyError):
        build_disease_term(test_disease, alias_genes)


@pytest.mark.parametrize("key", ['mim_number'])
def test_build_disease_inappropriate_value(key, test_disease):
    alias_genes = {}
    alias_genes["B3GALT6"] = {"true": 17978, "ids": [17978]}
    test_disease[key] = "not_an_int"
    # THEN calling build_disease_term(test_disease, alias_genes) a
    # ValueError is thrown, caught and converted into a KeyError
    with pytest.raises(KeyError):
        build_disease_term(test_disease, alias_genes)
