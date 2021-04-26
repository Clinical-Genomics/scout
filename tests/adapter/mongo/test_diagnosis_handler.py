# -*- coding: utf-8 -*-
import pytest

from scout.exceptions import IntegrityError


def test_add_disease_term(adapter):
    ## GIVEN a empty adapter
    assert len([term for term in adapter.disease_terms()]) == 0

    disease_term = dict(
        _id="OMIM:1",
        disease_id="OMIM:1",
        disease_nr=1,
        source="OMIM",
        description="First disease",
        genes=[1],  # List with integers that are hgnc_ids
    )
    ## WHEN loading a hpo term
    adapter.load_disease_term(disease_term)

    res = adapter.disease_terms()

    ## THEN assert that the term have been loaded
    assert len([term for term in res]) == 1


def test_add_disease_term_twice(adapter):
    ## GIVEN a empty adapter
    assert len([term for term in adapter.disease_terms()]) == 0

    disease_term = dict(
        _id="OMIM:1",
        disease_id="OMIM:1",
        disease_nr=1,
        source="OMIM",
        description="First disease",
        genes=[1],  # List with integers that are hgnc_ids
    )
    ## WHEN loading a hpo term twice
    adapter.load_disease_term(disease_term)

    ## THEN IntegrityError should be raised
    with pytest.raises(IntegrityError):
        adapter.load_disease_term(disease_term)


def test_fetch_disease_term(adapter):
    ## GIVEN a adapter loaded with one disease term
    assert len([term for term in adapter.disease_terms()]) == 0

    disease_term = dict(
        _id="OMIM:1",
        disease_id="OMIM:1",
        disease_nr=1,
        source="OMIM",
        description="First disease",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_disease_term(disease_term)
    ## WHEN fetching a disease term
    res = adapter.disease_term(disease_term["_id"])

    ## THEN assert the correct term was fetched
    assert res["_id"] == disease_term["_id"]


def test_fetch_disease_term_by_number(adapter):
    ## GIVEN a adapter loaded with one disease term
    assert len([term for term in adapter.disease_terms()]) == 0

    disease_term = dict(
        _id="OMIM:1",
        disease_id="OMIM:1",
        disease_nr=1,
        source="OMIM",
        description="First disease",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_disease_term(disease_term)
    ## WHEN fetching a disease term
    res = adapter.disease_term(disease_term["disease_nr"])

    ## THEN assert the correct term was fetched
    assert res["_id"] == disease_term["_id"]


def test_fetch_disease_term_by_hgnc_id(adapter):
    ## GIVEN a adapter loaded with one disease term
    assert len([term for term in adapter.disease_terms()]) == 0

    disease_term = dict(
        _id="OMIM:1",
        disease_id="OMIM:1",
        disease_nr=1,
        source="OMIM",
        description="First disease",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_disease_term(disease_term)

    disease_term["_id"] = "OMIM:2"
    disease_term["disease_id"] = "OMIM:2"
    disease_term["disease_nr"] = "2"
    adapter.load_disease_term(disease_term)

    ## WHEN fetching a disease term
    res = adapter.disease_terms(hgnc_id=1)

    ## THEN assert the correct term was fetched
    assert len([term for term in res]) == 2


def test_fetch_disease_term_by_hgnc_id_again(adapter):
    ## GIVEN a adapter loaded with one disease term
    assert len([term for term in adapter.disease_terms()]) == 0

    disease_term = dict(
        _id="OMIM:1",
        disease_id="OMIM:1",
        disease_nr=1,
        source="OMIM",
        description="First disease",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_disease_term(disease_term)

    disease_term["_id"] = "OMIM:2"
    disease_term["disease_id"] = "OMIM:2"
    disease_term["disease_nr"] = "2"
    disease_term["genes"] = [2]
    adapter.load_disease_term(disease_term)

    ## WHEN fetching a disease term
    res = adapter.disease_terms(hgnc_id=1)

    ## THEN assert the correct term was fetched
    assert len([term for term in res]) == 1


def test_case_omim_diagnoses(adapter, case_obj, test_omim_term):
    """Test search for all complete diagnoses for a case"""

    # GIVEN a database with an OMIN term
    adapter.disease_term_collection.insert_one(test_omim_term)

    # AND a case with BOTH diagnosis_phenotypes and disease genes:
    case_obj["diagnosis_phenotypes"] = [test_omim_term["disease_nr"]]
    case_obj["diagnosis_genes"] = [test_omim_term["disease_nr"]]
    adapter.case_collection.insert_one(case_obj)

    # WHEN the database queried for the case diagnoses
    result = list(adapter.case_omim_diagnoses(case_obj))

    # THEN it should return the OMIM term
    assert result[0] == test_omim_term


def test_omim_genes(adapter, test_omim_term):
    """Test function that collects complete gene info for a given OMIM term"""

    omim_gene_id = test_omim_term["genes"][0]

    # GIVEN a database with a the same gene of the OMIM term
    test_gene = {"hgnc_id": omim_gene_id, "build": "37"}
    adapter.hgnc_collection.insert_one(test_gene)

    # WHEN the database queried for the OMIM genes
    result = list(adapter.omim_to_genes(test_omim_term))

    # THEN it should return the right gene
    assert result[0]["hgnc_id"] == omim_gene_id
