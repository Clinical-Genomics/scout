from scout.build.disease import build_disease_term
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

    assert isinstance(disease_obj, dict)


@pytest.mark.parametrize("key", ["mim_number", "description"])
def test_build_disease_missing_key(key, test_disease):
    ## GIVEN a dictionary with disease information and genes
    alias_genes = {}
    alias_genes["B3GALT6"] = {"true": 17978, "ids": [17978]}

    # WHEN deleting a mandatory key
    test_disease.pop(key)
    # THEN calling build_disease_term() will raise ValueError
    with pytest.raises(ValueError):
        build_disease_term(test_disease, alias_genes)


def test_build_disease_wrong_value(test_disease):
    ## GIVEN a dictionary with disease information and genes
    alias_genes = {}
    alias_genes["B3GALT6"] = {"true": 17978, "ids": [17978]}
    # WHEN disease number is not an integer
    test_disease["mim_number"] = "not_an_int"
    # THEN calling build_disease_term() will raise ValueError
    with pytest.raises(ValueError):
        build_disease_term(test_disease, alias_genes)
