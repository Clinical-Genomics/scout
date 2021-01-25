# -*- coding: utf-8 -*-
import datetime
import requests
from flask import url_for, current_app, jsonify
from flask_login import current_user

from bson.objectid import ObjectId

from scout.demo import delivery_report_path
from scout.server.blueprints.cases import controllers
from scout.server.extensions import store
from scout.server.extensions import mail
from scout.server.blueprints.cases.views import (
    parse_raw_gene_symbols,
    parse_raw_gene_ids,
)

TEST_TOKEN = "test_token"


def test_rerun(app, institute_obj, case_obj, monkeypatch):
    """test case rerun function"""

    # GIVEN an initialized app
    # GIVEN a valid user

    def send_email(*args, **kwargs):
        return True

    monkeypatch.setattr(mail, "send", send_email)

    # GIVEN a test case without rerun pending
    test_case = store.case_collection.find_one()
    assert test_case.get("rerun_requested") is False

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN rerun request is sent
        resp = client.post(
            url_for(
                "cases.rerun",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        assert resp.status_code == 302
        updated_case = store.case_collection.find_one()

        # THEN the case should be updated
        assert updated_case["rerun_requested"] is True
        rerun_event = store.event_collection.find_one()

        # AND a rerun event should be created
        assert rerun_event.get("verb") == "rerun"


def test_parse_raw_gene_symbols(app):
    """Test parse gene symbols"""

    # GIVEN a list of autocompleted gene symbols
    gene_symbols = ["MUTYH |POT1", "POT1 0.1|APC|PMS2"]

    # WHEN converting to hgnc_ids
    hgnc_symbols = parse_raw_gene_symbols(gene_symbols)

    # THEN the appropriate set of hgnc_symbols should be returned
    assert hgnc_symbols == {"APC", "MUTYH", "PMS2", "POT1"}


def test_parse_raw_gene_ids(app):
    """ Test parse gene symbols"""

    # GIVEN a list of autocompleted gene symbols
    gene_symbols = ["1234 | SYM (OLDSYM, SYM)", "4321 | MYS (OLDMYS, MYS)"]

    # WHEN converting to hgnc_ids
    hgnc_ids = parse_raw_gene_ids(gene_symbols)

    # THEN the appropriate set of hgnc_ids should be returned
    assert hgnc_ids == {1234, 4321}


def test_update_cancer_case_sample(app, user_obj, institute_obj, cancer_case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    # And a cancer case with cancer samples data
    old_tumor_purity = cancer_case_obj["individuals"][0]["tumor_purity"]
    old_tumor_type = cancer_case_obj["individuals"][0]["tumor_type"]
    old_tissue_type = "unknown"
    assert old_tumor_purity
    assert old_tumor_type

    cancer_case_obj["individuals"][0]["tissue_type"] = old_tissue_type
    cancer_case_obj["updated_at"] = datetime.datetime.now()
    store.case_collection.insert_one(cancer_case_obj)

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN posting a request with info for updating one of the case samples:
        ind_id = cancer_case_obj["individuals"][0]["individual_id"]

        form_data = {
            "update_ind": ind_id,
            ".".join(["tumor_type.", ind_id]): "Desmoid Tumor",
            ".".join(["tissue_type", ind_id]): "cell line",
            ".".join(["tumor_purity", ind_id]): "0.4",
        }

        resp = client.post(
            url_for(
                "cases.update_cancer_sample",
                institute_id=institute_obj["internal_id"],
                case_name=cancer_case_obj["display_name"],
            ),
            data=form_data,
        )

        # THEN the returned HTML page should redirect
        assert resp.status_code == 302

        # AND sample in case obj should have been updated
        updated_case = store.case_collection.find_one({"_id": cancer_case_obj["_id"]})
        updated_sample = updated_case["individuals"][0]

        assert updated_sample["tumor_purity"] != old_tumor_purity
        assert updated_sample["tumor_type"] != old_tumor_type
        assert updated_sample["tissue_type"] != old_tissue_type


def test_institutes(app):
    # GIVEN an initialized app
    # GIVEN a valid user

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the institutes page
        resp = client.get(url_for("cases.index"))

        # THEN it should return a page
        assert resp.status_code == 200


def test_case_outdated_panel(app, institute_obj, case_obj, dummy_case):
    """Test case displaying an outdated panel warning badge"""

    # GIVEN an adapter with a case with a gene panel of version 1
    case_panel = case_obj["panels"][0]
    assert case_panel["version"] == 1

    # AND an updated version of the same panel in the database
    updated_panel = {
        "panel_name": case_panel["panel_name"],
        "display_name": case_panel["display_name"],
        "version": 2,
        "genes": [{"symbol": "POT1", "hgnc_id": 17284}],
    }
    store.panel_collection.insert_one(updated_panel)

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # WHEN case page is loaded
        resp = client.get(
            url_for(
                "cases.case",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # THEN it should return a valid page
        assert resp.status_code == 200

        # WITH a tooltip explaining that the gene panel is outdated
        assert "Panel version used in the analysis (1.0) is outdated." in str(resp.data)


def test_case_sma(app, case_obj, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user, case and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the case SMN CN page
        resp = client.get(
            url_for(
                "cases.sma",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )

        # THEN it should return a page
        assert resp.status_code == 200


def test_update_individual(app, user_obj, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    # And a case individual with no age (tissue type is default blood):
    case_obj = store.case_collection.find_one()
    assert case_obj["individuals"][0].get("age") is None
    assert case_obj["individuals"][0]["tissue_type"] == "blood"

    with app.test_client() as client:

        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN posting a request with info for updating one of the case samples:
        ind_id = case_obj["individuals"][0]["individual_id"]
        form_data = {
            "update_ind": ind_id,
            "_".join(["age", ind_id]): "2.5",
            "_".join(["tissue", ind_id]): "muscle",
        }

        resp = client.post(
            url_for(
                "cases.update_individual",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=form_data,
        )

        # THEN the returned HTML page should redirect
        assert resp.status_code == 302

        # Then case obj should have been updated:
        updated_case = store.case_collection.find_one({"_id": case_obj["_id"]})
        updated_ind = updated_case["individuals"][0]
        assert updated_ind["individual_id"] == ind_id
        assert updated_ind["age"] == 2.5
        assert updated_ind["tissue_type"] == "muscle"

        # And an associated event should have been created in the database
        assert store.event_collection.find_one(
            {"case": updated_case["_id"], "verb": "update_individual"}
        )


def test_case_synopsis(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        req_data = {"synopsis": "test synopsis"}

        # WHEN updating the synopsis of a case
        resp = client.post(
            url_for(
                "cases.case_synopsis",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                data=req_data,
            )
        )
        # then it should return a redirected page
        assert resp.status_code == 302


def test_update_case_comment(app, institute_obj, case_obj, user_obj):
    """Test the functionality that allows updating of case-specific comments"""

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        ## GIVEN a case with a comment
        store.create_event(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link="a link",
            category="case",
            verb="comment",
            subject=case_obj["display_name"],
            level="specific",
        )
        comment = store.event_collection.find_one({"verb": "comment"})
        assert comment

        # WHEN a user updates the comment via the modal form
        form_data = {"event_id": comment["_id"], "updatedContent": "an updated comment", "edit": ""}
        resp = client.post(
            url_for(
                "cases.events",
                institute_id=institute_obj["_id"],
                case_name=case_obj["display_name"],
                event_id=comment["_id"],
            ),
            data=form_data,
        )
        # THEN it should redirect to case page
        assert resp.status_code == 302

        # The comment should be updated
        updated_comment = store.event_collection.find_one({"_id": comment["_id"]})
        assert updated_comment["content"] == "an updated comment"

        # And a comment updated event should have been created in the event collection
        updated_var_event = store.event_collection.find_one({"verb": "comment_update"})
        # With the same subject of the comment
        assert updated_var_event["subject"] == updated_comment["subject"]


def test_add_case_group(app, case_obj, institute_obj):
    """Test adding a case group."""

    ### GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # WHEN we invoke the add group endpoint with GET
        resp = client.get(
            url_for(
                "cases.add_case_group",
                institute_id=institute_obj["_id"],
                case_name=case_obj["display_name"],
            )
        )

        # THEN the response should be a redirect
        assert resp.status_code == 302


def test_remove_case_group(app, case_obj, institute_obj):
    """Test removing a case group."""
    ### GIVEN an initialized app
    group_id = ObjectId("101010101010101010101010")
    result = store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"group": [group_id]}}
    )

    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # WHEN we invoke the add group endpoint with GET
        resp = client.get(
            url_for(
                "cases.remove_case_group",
                institute_id=institute_obj["_id"],
                case_name=case_obj["display_name"],
                case_group=group_id,
            )
        )

        # THEN the response should be a redirect
        assert resp.status_code == 302


def test_download_hpo_genes(app, case_obj, institute_obj):
    """Test the endpoint that downloads the dynamic gene list for a case"""

    # GIVEN a case containing a dynamic gene list
    dynamic_gene_list = [
        {"hgnc_symbol": "ACTA2", "hgnc_id": 130, "description": "actin alpha 2, smooth muscle"},
        {"hgnc_symbol": "LMNB2", "hgnc_id": 6638, "description": "lamin B2"},
    ]

    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"dynamic_gene_list": dynamic_gene_list}}
    )

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # WHEN the endpoint for downloading the case dynamic gene list is invoked
        resp = client.get(
            url_for(
                "cases.download_hpo_genes",
                institute_id=institute_obj["_id"],
                case_name=case_obj["display_name"],
            )
        )
        # THEN the response should be successful
        assert resp.status_code == 200
        # And should download a PDF file
        assert resp.mimetype == "application/pdf"


def test_case_report(app, institute_obj, case_obj):
    # Test the web page containing the general case report

    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # When clicking on 'general' button on case page
        resp = client.get(
            url_for(
                "cases.case_report",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # a successful response should be returned
        assert resp.status_code == 200


def test_case_diagnosis(app, institute_obj, case_obj):
    # Test the web page containing the general case report

    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        req_data = {"omim_term": "OMIM:615349"}

        # When updating an OMIM diagnosis for a case
        resp = client.post(
            url_for(
                "cases.case_diagnosis",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=req_data,
        )
        # Response should be redirected to case page
        assert resp.status_code == 302


def test_pdf_case_report(app, institute_obj, case_obj):
    # Test the web page containing the general case report

    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # When clicking on 'Download PDF' button on general report page
        resp = client.get(
            url_for(
                "cases.pdf_case_report",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # a successful response should be returned
        assert resp.status_code == 200


def test_mt_report(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # When clicking on 'mtDNA report' on case page
        resp = client.get(
            url_for(
                "cases.mt_report",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # a successful response should be returned
        assert resp.status_code == 200
        # and it should contain a zipped file, not HTML code
        assert resp.mimetype == "application/zip"


def test_matchmaker_add(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the case page
        resp = client.post(
            url_for(
                "cases.matchmaker_add",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # page redirects in the views anyway, so it will return a 302 code
        assert resp.status_code == 302


def test_matchmaker_matches(app, institute_obj, case_obj, mme_submission, user_obj, monkeypatch):

    # Given a case object with a MME submission
    case_obj["mme_submission"] = mme_submission
    store.update_case(case_obj)

    res = store.case_collection.find({"mme_submission": {"$exists": True}})
    assert res

    # Monkeypatch response with MME matches
    def mock_matches(*args, **kwargs):
        return {"institute": institute_obj, "case": case_obj, "matches": {}}

    monkeypatch.setattr(controllers, "mme_matches", mock_matches)

    # GIVEN an initialized app
    # GIVEN a valid institute and a user with mme_submitter role
    store.user_collection.update_one(
        {"_id": user_obj["_id"]}, {"$set": {"roles": ["mme_submitter"]}}
    )

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # Given mock MME connection parameters
        current_app.config["MME_URL"] = "http://fakey_mme_url:fakey_port"
        current_app.config["MME_TOKEN"] = TEST_TOKEN

        # WHEN accessing the case page
        resp = client.get(
            url_for(
                "cases.matchmaker_matches",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )

        # Then a successful response should be generated
        assert resp.status_code == 200


def test_matchmaker_match(app, institute_obj, case_obj, mme_submission, user_obj, monkeypatch):

    # Given a case object with a MME submission
    case_obj["mme_submission"] = mme_submission
    store.update_case(case_obj)

    res = store.case_collection.find({"mme_submission": {"$exists": True}})
    assert sum(1 for i in res) == 1

    # Monkeypatch response with MME match
    def mock_match(*args, **kwargs):
        return [{"status_code": 200}]

    monkeypatch.setattr(controllers, "mme_match", mock_match)

    # GIVEN an initialized app
    # GIVEN a valid institute and a user with mme_submitter role
    store.user_collection.update_one(
        {"_id": user_obj["_id"]}, {"$set": {"roles": ["mme_submitter"]}}
    )
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # Given mock MME connection parameters
        current_app.config["MME_URL"] = "http://fakey_mme_url:fakey_port"
        current_app.config["MME_TOKEN"] = TEST_TOKEN

        # WHEN sending a POST request to match a patient
        resp = client.post(
            url_for(
                "cases.matchmaker_match",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                target="mock_node_id",
            )
        )
        # page redirects in the views anyway, so it will return a 302 code
        assert resp.status_code == 302


def test_matchmaker_delete(app, institute_obj, case_obj, mme_submission):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # add MME submission to case object
        store.case_collection.find_one_and_update(
            {"_id": case_obj["_id"]}, {"$set": {"mme_submission": mme_submission}}
        )
        res = store.case_collection.find({"mme_submission": {"$exists": True}})
        assert sum(1 for i in res) == 1

        # WHEN accessing the case page
        resp = client.post(
            url_for(
                "cases.matchmaker_delete",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # page redirects in the views anyway, so it will return a 302 code
        assert resp.status_code == 302


def test_status(app, institute_obj, case_obj, user_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # make sure test case status is inactive
        assert case_obj["status"] == "inactive"

        # use status view to update status for test case
        request_data = {"status": "prioritized"}
        resp = client.post(
            url_for(
                "cases.status",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                params=request_data,
            )
        )

        assert resp.status_code == 302  # page should be redirected


def test_html_delivery_report(app, institute_obj, case_obj, user_obj):

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # AND the case has a delivery report
        store.case_collection.update_one(
            {"_id": case_obj["_id"]},
            {"$set": {"delivery_report": delivery_report_path}},
        )

        # WHEN accessing the delivery report page
        resp = client.get(
            url_for(
                "cases.delivery_report",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )

        # THEN the endpoint should return the delivery report HTML page
        assert "Leveransrapport Clinical Genomics" in str(resp.data)


def test_pdf_delivery_report(app, institute_obj, case_obj, user_obj):

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # AND the case has a delivery report
        store.case_collection.update_one(
            {"_id": case_obj["_id"]},
            {"$set": {"delivery_report": delivery_report_path}},
        )

        # WHEN accessing the delivery report page with the format=pdf param
        resp = client.get(
            url_for(
                "cases.delivery_report",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                format="pdf",
            )
        )

        # a successful response should be returned
        assert resp.status_code == 200
        # and it should contain a pdf file, not HTML code
        assert resp.mimetype == "application/pdf"


def test_caselist(app, case_obj):
    """Test the API return of cases for autocompletion"""

    # GIVEN a case
    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN the API is invoked with a query string containing part of the case term description
        resp = client.get(
            url_for(
                "cases.caselist", institute_id=case_obj["owner"], query=case_obj["display_name"]
            )
        )
        # THEN it should return a valid response
        assert resp.status_code == 200

        # containing the case display name
        assert case_obj["display_name"] in str(resp.data)


def test_omimterms(app, test_omim_term):
    """Test The API which returns all OMIM terms when queried from case page"""

    # GIVEN a database containing at least one OMIM term
    store.disease_term_collection.insert_one(test_omim_term)

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN the API is invoked with a query string containing part of the OMIM term description
        resp = client.get(url_for("cases.omimterms", query="5-oxo"))
        # THEN it should return a valid response
        assert resp.status_code == 200

        # containing the OMIM term
        assert test_omim_term["_id"] in str(resp.data)


def test_beacon_submit_wrong_config(app, case_obj):
    """Test saving variants to a Beacon server when Beacon connection parameters are not set"""

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        form_data = {
            "case": case_obj["_id"],
            "samples": "affected",
            "vcf_files": ["vcf_snv_research", "vcf_snv"],
        }
        # WHEN case page is loaded
        resp = client.post(
            url_for("cases.beacon_submit"),
            data=form_data,
        )
        # THEN it should redirect to case page
        assert resp.status_code == 302
        updated_case = store.case_collection.find_one()
        # and submission should not be saved in case object
        assert "beacon" not in updated_case


def test_beacon_submit(app, case_obj, monkeypatch, mocked_beacon):
    """Test submitting variants to a Beacon server"""

    # GIVEN a mocked Beacon server
    def mock_response(*args, **kwargs):
        return mocked_beacon

    monkeypatch.setattr(requests, "post", mock_response)

    # GIVEN an initialized app containing the right config settings
    current_app.config["BEACON_URL"] = mocked_beacon.url
    current_app.config["BEACON_TOKEN"] = mocked_beacon.token

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        form_data = {
            "case": case_obj["_id"],
            "samples": "affected",
            "vcf_files": ["vcf_snv_research", "vcf_snv"],
        }
        # WHEN users submits a POST request to Beacon
        resp = client.post(
            url_for("cases.beacon_submit"),
            data=form_data,
        )
        # THEN it should redirect to case page
        assert resp.status_code == 302
        updated_case = store.case_collection.find_one()
        # and submissions details should be saved in case object
        assert "beacon" in updated_case
        assert updated_case["beacon"]["samples"]
        assert updated_case["beacon"]["vcf_files"] == form_data["vcf_files"]


def test_beacon_remove(app, case_obj, monkeypatch, mocked_beacon):
    """Test removing variants submitted to Beacon for test case"""

    # GIVEN a mocked Beacon server
    def mock_response(*args, **kwargs):
        return mocked_beacon

    monkeypatch.setattr(requests, "post", mock_response)

    # GIVEN a case with variants saved to Beacon
    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"beacon": {"samples": ["ADM1059A2"]}}}
    )
    case_obj = store.case_collection.find_one()
    assert case_obj["beacon"]

    # GIVEN an initialized app containing the right config settings
    current_app.config["BEACON_URL"] = mocked_beacon.url
    current_app.config["BEACON_TOKEN"] = mocked_beacon.token

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN users submits a GET request to remove data from Beacon
        resp = client.get(
            url_for(
                "cases.beacon_remove",
                case_id=case_obj["_id"],
            )
        )
        # THEN it should redirect to case page
        assert resp.status_code == 302

        # And case should no more have an associated Beacon submission
        updated_case = store.case_collection.find_one()
        assert "beacon" not in updated_case
