# -*- coding: utf-8 -*-
from datetime import datetime
from flask import url_for, current_app
from flask_login import current_user

from scout.demo import delivery_report_path
from scout.server.blueprints.cases import controllers
from scout.server.extensions import store


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
    cancer_case_obj["updated_at"] = datetime.now()
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


def test_cases(app, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the cases page
        resp = client.get(
            url_for("cases.cases", institute_id=institute_obj["internal_id"])
        )

        # THEN it should return a page
        assert resp.status_code == 200

        # test query passing parameters in seach form
        request_data = {
            "limit": "100",
            "skip_assigned": "on",
            "is_research": "on",
            "query": "case_id",
        }
        resp = client.get(
            url_for(
                "cases.cases",
                institute_id=institute_obj["internal_id"],
                params=request_data,
            )
        )
        # response should return a page
        assert resp.status_code == 200

        sorting_options = ["analysis_date", "track", "status"]
        for option in sorting_options:
            # test query passing the sorting option to the cases view
            request_data = {"sort": option}
            resp = client.get(
                url_for(
                    "cases.cases",
                    institute_id=institute_obj["internal_id"],
                    params=request_data,
                )
            )
            # response should return a page
            assert resp.status_code == 200


def test_cases_query(app, case_obj, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    slice_query = case_obj["display_name"]

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the cases page with a query
        resp = client.get(
            url_for(
                "cases.cases",
                query=slice_query,
                institute_id=institute_obj["internal_id"],
            )
        )

        # THEN it should return a page
        assert resp.status_code == 200


def test_cases_panel_query(app, case_obj, parsed_panel, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    slice_query = parsed_panel["panel_id"]

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the cases page with a query
        resp = client.get(
            url_for(
                "cases.cases",
                query=slice_query,
                institute_id=institute_obj["internal_id"],
            )
        )

        # THEN it should return a page
        assert resp.status_code == 200


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


def test_case(app, case_obj, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user, case and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the case page
        resp = client.get(
            url_for(
                "cases.case",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )

        # THEN it should return a page
        assert resp.status_code == 200


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

    # And a case individual with no age or tissue type:
    case_obj = store.case_collection.find_one()
    assert case_obj["individuals"][0].get("age") is None
    case_obj["individuals"][0]["tissue_type"] is None

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


def test_causatives(app, user_obj, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute
    # There should be no causative variants for test case:
    assert "causatives" not in case_obj
    var1_id = "4c7d5c70d955875504db72ef8e1abe77"  # in POT1 gene
    var2_id = "e24b65bf27feacec6a81c8e9e19bd5f1"  # in TBX1 gene
    var_ids = [var1_id, var2_id]

    # for each variant
    for var_id in var_ids:
        # update case by marking variant as causative:
        variant_obj = store.variant(document_id=var_id)
        store.mark_causative(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link="causative_var_link/{}".format(variant_obj["_id"]),
            variant=variant_obj,
        )
    updated_case = store.case_collection.find_one({"_id": case_obj["_id"]})
    # The above variants should be registered as causatives in case object
    assert updated_case["causatives"] == var_ids

    # Call scout causatives view and check if the above causatives are displayed
    with app.test_client() as client:

        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the case page
        resp = client.get(
            url_for("cases.causatives", institute_id=institute_obj["internal_id"])
        )

        # THEN it should return a page
        assert resp.status_code == 200
        # with variant 1
        assert var1_id in str(resp.data)
        # and variant 2
        assert var2_id in str(resp.data)

        # Filter causatives by gene (POT1)
        resp = client.get(
            url_for(
                "cases.causatives",
                institute_id=institute_obj["internal_id"],
                query="17284 | POT1 (DKFZp586D211, hPot1, POT1)",
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200
        # with variant 1
        assert var1_id in str(resp.data)
        # but NOT variant 2
        assert var2_id not in str(resp.data)


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


def test_clinvar_submissions(app, institute_obj):
    # Test the web page containing the clinvar submissions for an institute

    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # When visiting the clinvar submissiin page (get request)
        resp = client.get(
            url_for(
                "cases.clinvar_submissions", institute_id=institute_obj["internal_id"]
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


def test_matchmaker_matches(
    app, institute_obj, case_obj, mme_submission, user_obj, monkeypatch
):

    # Given a case object with a MME submission
    case_obj["mme_submission"] = mme_submission
    store.update_case(case_obj)

    res = store.case_collection.find({"mme_submission": {"$exists": True}})
    assert sum(1 for i in res) == 1

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
        current_app.config["MME_TOKEN"] = "test_token"

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


def test_matchmaker_match(
    app, institute_obj, case_obj, mme_submission, user_obj, monkeypatch
):

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
        current_app.config["MME_TOKEN"] = "test_token"

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
