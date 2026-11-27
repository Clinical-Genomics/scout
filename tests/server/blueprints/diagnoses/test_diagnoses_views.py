# -*- coding: utf-8 -*-
from flask import url_for

from scout.server.extensions import store


def test_omim_diagnosis(app, test_omim_database_term):
    """Test page that displays an OMIM diagnosis info"""

    # GIVEN a database with at least one gene
    store.disease_term_collection.insert_one(test_omim_database_term)

    # GIVEN an initialized app
    with app.test_client() as client:
        # WHEN accessing the page of one OMIM diagnosis
        resp = client.get(
            url_for("diagnoses.diagnosis", disease_id=test_omim_database_term["disease_id"])
        )

        # THEN it should return a page
        assert resp.status_code == 200


def test_omim_diagnosis_api(app, test_omim_database_term):
    """Test page that displays an OMIM diagnosis info"""

    store.load_disease_term(test_omim_database_term)

    with app.test_client() as client:
        # WHEN asking for a list of all disorders
        response = client.get(url_for("diagnoses.api_diagnoses"))

        # THEN a json response is returned
        assert response.content_type == "application/json"


def test_clingen_mondo_diagnosis(app):
    """Test page that displays a ClinGen MONDO diagnosis with its gene-disease validity curations"""

    # GIVEN a database with a ClinGen MONDO disease term
    store.disease_term_collection.insert_one(
        {
            "_id": "MONDO:0018544",
            "disease_id": "MONDO:0018544",
            "disease_nr": 18544,
            "description": "adrenoleukodystrophy",
            "source": "MONDO",
            "genes": [61],
            "inheritance": ["XL"],
            "clingen_gene_validity": [
                {
                    "hgnc_id": 61,
                    "hgnc_symbol": "ABCD1",
                    "inheritance": "XL",
                    "classification": "Definitive",
                    "online_report": "https://search.clinicalgenome.org/kb/gene-validity/CGGV:x",
                    "date": "2020-12-18T05:00:00.000Z",
                    "gcep": "Peroxisomal Disorders Gene Curation Expert Panel",
                }
            ],
        }
    )

    with app.test_client() as client:
        # WHEN accessing the page of the diagnosis
        resp = client.get(url_for("diagnoses.diagnosis", disease_id="MONDO:0018544"))

        # THEN it should return a page with the curation and a link to ClinGen
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "Definitive" in html
        assert "<strong>Adrenoleukodystrophy</strong>" in html
        assert "Peroxisomal Disorders Gene Curation Expert Panel" in html
        assert "https://search.clinicalgenome.org/kb/conditions/MONDO:0018544" in html
        # THEN the curated gene symbol links to the gene page
        assert url_for("genes.gene", hgnc_id=61) in html
