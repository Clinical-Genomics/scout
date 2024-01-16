import pytest

from scout.build.disease import build_disease_term


def test_build_disease_term(adapter, test_disease_id, test_disease):
    ## GIVEN some disease info and a adapter with a gene
    alias_genes = {}
    alias_genes["B3GALT6"] = {"true": 17978, "ids": [17978]}

    ## WHEN building the disease term
    disease_obj = build_disease_term(test_disease_id, test_disease, alias_genes)

    ## THEN assert the term is on the correct format

    assert disease_obj["_id"] == disease_obj["disease_id"] == test_disease_id
    assert disease_obj["inheritance"] == ["AR"]
    assert disease_obj["genes"] == [17978]
    assert disease_obj["source"] == "OMIM"

    assert isinstance(disease_obj, dict)


def test_build_disease_wrong_value(test_disease):
    # GIVEN a dictionary with disease information and genes
    alias_genes = {}
    alias_genes["B3GALT6"] = {"true": 17978, "ids": [17978]}
    test_disease_id = "OMIM.615349"
    # WHEN disease number is not an integer
    # THEN calling build_disease_term() will raise ValueError
    with pytest.raises(IndexError):
        build_disease_term(test_disease_id, test_disease, alias_genes)
