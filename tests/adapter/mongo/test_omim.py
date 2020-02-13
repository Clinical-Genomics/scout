# -*- coding: utf-8 -*-
import datetime
import pymongo

def test_omim_term(adapter, test_omim_term):
    """Test search for one OMIM term"""

    # GIVEN a database with at least one OMIM term
    adapter.disease_term_collection.insert_one(test_omim_term)

    # WHEN the database is interrogated using the adapter
    result = adapter.omim_term(test_omim_term["_id"])

    # THEN the term should be returned
    result = test_omim_term


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
    """"Test function that collects complete gene info for a given OMIM term"""

    omim_gene_id = test_omim_term["genes"][0]

    # GIVEN a database with a the same gene of the OMIM term
    test_gene = {"hgnc_id": omim_gene_id, "build" : "37"}
    adapter.hgnc_collection.insert_one(test_gene)

    # WHEN the database queried for the OMIM genes
    result = list(adapter.omim_genes(test_omim_term["genes"]))

    # THEN it should return the right gene
    assert result[0]["hgnc_id"] == omim_gene_id
