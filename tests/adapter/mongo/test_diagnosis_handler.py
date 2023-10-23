# -*- coding: utf-8 -*-
import pytest

from scout.exceptions import IntegrityError


def test_convert_diagnoses_format(adapter, case_obj, test_omim_term):
    """Tests the function that converts case diagnoses from list of integers
    to list of OMIM terms dictionaries"""

    # GIVEN a diagnosis term present in the database
    adapter.disease_term_collection.insert_one(test_omim_term)

    # AND a case containing diagnoses as a list of integers (OMIM disease_nr)
    case_obj["diagnosis_phenotypes"] = [test_omim_term["disease_nr"]]
    assert adapter.case_collection.insert_one(case_obj)

    # WHEN diagnoses format is converted using the function
    updated_case = adapter.convert_diagnoses_format(case_obj)

    # THEN case diagnosis_phenotypes should become a list of dictionaries
    case_diagnoses = updated_case["diagnosis_phenotypes"]
    assert case_diagnoses[0]["disease_nr"] == test_omim_term["disease_nr"]
    assert case_diagnoses[0]["disease_id"] == test_omim_term["disease_id"]
    assert case_diagnoses[0]["description"] == test_omim_term["description"]


def test_add_disease_term(adapter, test_omim_term):
    ## GIVEN a empty adapter
    assert len([term for term in adapter.disease_terms()]) == 0

    ## WHEN loading a hpo term
    adapter.load_disease_term(test_omim_term)

    res = adapter.disease_terms()

    ## THEN assert that the term have been loaded
    assert len([term for term in res]) == 1


def test_add_disease_term_twice(adapter, test_omim_term):
    ## GIVEN a empty adapter
    assert len([term for term in adapter.disease_terms()]) == 0

    ## WHEN loading a hpo term twice
    adapter.load_disease_term(test_omim_term)

    ## THEN IntegrityError should be raised
    with pytest.raises(IntegrityError):
        adapter.load_disease_term(test_omim_term)


def test_fetch_disease_term(adapter, test_omim_term):
    ## GIVEN a adapter loaded with one disease term
    assert len([term for term in adapter.disease_terms()]) == 0

    adapter.load_disease_term(test_omim_term)
    ## WHEN fetching a disease term
    res = adapter.disease_term(test_omim_term["_id"])

    ## THEN assert the correct term was fetched
    assert res["_id"] == test_omim_term["_id"]


def test_fetch_disease_term_by_number(adapter, test_omim_term):
    ## GIVEN a adapter loaded with one disease term
    assert len([term for term in adapter.disease_terms()]) == 0

    adapter.load_disease_term(test_omim_term)
    ## WHEN fetching a disease term
    res = adapter.disease_term(test_omim_term["disease_nr"])

    ## THEN assert the correct term was fetched
    assert res["_id"] == test_omim_term["_id"]


def test_fetch_disease_term_by_hgnc_id(adapter, test_omim_term):
    ## GIVEN a adapter loaded with one disease term
    assert len([term for term in adapter.disease_terms()]) == 0

    adapter.load_disease_term(test_omim_term)

    ## WHEN fetching a disease term
    res = adapter.disease_terms(hgnc_id=test_omim_term.get("genes")[0])

    ## THEN assert the correct term was fetched
    assert len(res)


def test_case_omim_diagnoses(adapter, case_obj, test_omim_term):
    """Test search for all complete diagnoses for a case"""

    assert "description" in test_omim_term.keys()

    # GIVEN a database with an OMIN term
    adapter.disease_term_collection.insert_one(test_omim_term)

    # AND a case with BOTH diagnosis_phenotypes and disease genes:
    disease_info = {
        "disease_id": test_omim_term["_id"],
        "description": test_omim_term["description"],
    }
    case_obj["diagnosis_phenotypes"] = [disease_info]

    adapter.case_collection.insert_one(case_obj)

    case_omim_diagnoses = adapter.case_omim_diagnoses(
        case_diagnoses=case_obj["diagnosis_phenotypes"], filter_project=None
    )
    assert list(case_omim_diagnoses)[0] == test_omim_term


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
