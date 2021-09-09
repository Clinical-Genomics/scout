# -*- coding: utf-8 -*-
import pytest

from scout.exceptions import IntegrityError


def test_convert_diagnoses_format(adapter, case_obj, omim_term):
    """Tests the function that converts case diagnoses from list of integers
    to list of OMIM terms dictionaries"""

    # GIVEN a diagnosis term present in the database
    adapter.disease_term_collection.insert_one(omim_term)

    # AND a case containing diagnoses as a list of integers (OMIM disease_nr)
    case_obj["diagnosis_phenotypes"] = [omim_term["disease_nr"]]
    assert adapter.case_collection.insert_one(case_obj)

    # WHEN diagnoses format is converted using the function
    updated_case = adapter.convert_diagnoses_format(case_obj)

    # THEN case diagnosis_phenotypes should become a list of dictionaries
    case_diagnoses = updated_case["diagnosis_phenotypes"]
    assert case_diagnoses[0]["disease_nr"] == omim_term["disease_nr"]
    assert case_diagnoses[0]["disease_id"] == omim_term["disease_id"]
    assert case_diagnoses[0]["description"] == omim_term["description"]


def test_add_disease_term(adapter, omim_term):
    ## GIVEN a empty adapter
    assert len([term for term in adapter.disease_terms()]) == 0

    ## WHEN loading a hpo term
    adapter.load_disease_term(omim_term)

    res = adapter.disease_terms()

    ## THEN assert that the term have been loaded
    assert len([term for term in res]) == 1


def test_add_disease_term_twice(adapter, omim_term):
    ## GIVEN a empty adapter
    assert len([term for term in adapter.disease_terms()]) == 0

    ## WHEN loading a hpo term twice
    adapter.load_disease_term(omim_term)

    ## THEN IntegrityError should be raised
    with pytest.raises(IntegrityError):
        adapter.load_disease_term(omim_term)


def test_fetch_disease_term(adapter, omim_term):
    ## GIVEN a adapter loaded with one disease term
    assert len([term for term in adapter.disease_terms()]) == 0

    adapter.load_disease_term(omim_term)
    ## WHEN fetching a disease term
    res = adapter.disease_term(omim_term["_id"])

    ## THEN assert the correct term was fetched
    assert res["_id"] == omim_term["_id"]


def test_fetch_disease_term_by_number(adapter, omim_term):
    ## GIVEN a adapter loaded with one disease term
    assert len([term for term in adapter.disease_terms()]) == 0

    adapter.load_disease_term(omim_term)
    ## WHEN fetching a disease term
    res = adapter.disease_term(omim_term["disease_nr"])

    ## THEN assert the correct term was fetched
    assert res["_id"] == omim_term["_id"]


def test_fetch_disease_term_by_hgnc_id(adapter, omim_term):
    ## GIVEN a adapter loaded with one disease term
    assert len([term for term in adapter.disease_terms()]) == 0

    adapter.load_disease_term(omim_term)

    omim_term["_id"] = "OMIM:2"
    omim_term["disease_id"] = "OMIM:2"
    omim_term["disease_nr"] = "2"
    adapter.load_disease_term(omim_term)

    ## WHEN fetching a disease term
    res = adapter.disease_terms(hgnc_id=1)

    ## THEN assert the correct term was fetched
    assert len([term for term in res]) == 2


def test_fetch_disease_term_by_hgnc_id_again(adapter, omim_term):
    ## GIVEN a adapter loaded with one disease term
    assert len([term for term in adapter.disease_terms()]) == 0

    adapter.load_disease_term(omim_term)

    omim_term["_id"] = "OMIM:2"
    omim_term["disease_id"] = "OMIM:2"
    omim_term["disease_nr"] = "2"
    omim_term["genes"] = [2]
    adapter.load_disease_term(omim_term)

    ## WHEN fetching a disease term
    res = adapter.disease_terms(hgnc_id=1)

    ## THEN assert the correct term was fetched
    assert len([term for term in res]) == 1


def test_case_omim_diagnoses(adapter, case_obj, omim_term):
    """Test search for all complete diagnoses for a case"""

    assert "description" in omim_term.keys()

    # GIVEN a database with an OMIN term
    adapter.disease_term_collection.insert_one(omim_term)

    # AND a case with BOTH diagnosis_phenotypes and disease genes:
    disease_info = {
        "disease_id": omim_term["_id"],
        "description": omim_term["description"],
    }
    case_obj["diagnosis_phenotypes"] = [disease_info]

    adapter.case_collection.insert_one(case_obj)

    case_omim_diagnoses = adapter.case_omim_diagnoses(case_obj["diagnosis_phenotypes"])
    assert list(case_omim_diagnoses)[0] == omim_term


def test_omim_genes(adapter, omim_term):
    """Test function that collects complete gene info for a given OMIM term"""

    omim_gene_id = omim_term["genes"][0]

    # GIVEN a database with a the same gene of the OMIM term
    test_gene = {"hgnc_id": omim_gene_id, "build": "37"}
    adapter.hgnc_collection.insert_one(test_gene)

    # WHEN the database queried for the OMIM genes
    result = list(adapter.omim_to_genes(omim_term))

    # THEN it should return the right gene
    assert result[0]["hgnc_id"] == omim_gene_id
