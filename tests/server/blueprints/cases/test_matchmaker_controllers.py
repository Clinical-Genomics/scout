from flask import request, url_for
from flask_login import current_user

import scout.server.blueprints.cases.controllers as controllers
from scout.server.blueprints.cases.controllers import redirect
from scout.server.extensions import matchmaker, store


def test_matchmaker_check_requirements_wrong_settings(app, user_obj, mocker, mock_redirect):
    """Test that the matchmaker_check_requirements redirects if app settings requirements are not met"""

    mocker.patch("scout.server.blueprints.cases.controllers.redirect", return_value=mock_redirect)

    # GIVEN an app that is not properly configured and it's missing either
    # matchmaker.host, matchmaker.accept, matchmaker.token
    with app.test_client() as client:
        del matchmaker.host  # removing host property from matchmaker object

        # GIVEN a user that is logged in
        client.get(url_for("auto_login"))

        # THEN the matchmaker_check_requirements function should redirect to the previous page
        resp = controllers.matchmaker_check_requirements(request)
        assert resp.status_code == 302


def test_matchmaker_check_requirements_unauthorized_user(app, user_obj, mocker, mock_redirect):
    """Test redirect when a user is not authorized to access MatchMaker functionality"""

    mocker.patch("scout.server.blueprints.cases.controllers.redirect", return_value=mock_redirect)

    # GIVEN an app containing MatchMaker connection params
    with app.test_client() as client:
        # GIVEN a user that is logged in but doesn't have access to MatchMaker
        client.get(url_for("auto_login"))
        # THEN the matchmaker_check_requirements function should redirect to the previous page
        resp = controllers.matchmaker_check_requirements(request)
        assert resp.status_code == 302


def test_matchmaker_add_no_genes_no_features(app, user_obj, case_obj, mocker, mock_redirect):
    """Testing adding a case to matchmaker when the case has no set phenotype or candidate gene/variant"""

    mocker.patch("scout.server.blueprints.cases.controllers.redirect", return_value=mock_redirect)

    # GIVEN a case with no phenotype terms:
    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"phenotype_terms": []}}
    )
    # GIVEN a user which is registered as a MatchMaker submitter
    store.user_collection.find_one_and_update(
        {"email": user_obj["email"]}, {"$set": {"roles": ["mme_submitter"]}}
    )

    # GIVEN an app containing MatchMaker connection params
    with app.test_client() as client:
        # AND a user that is logged in but doesn't have access to MatchMaker
        client.get(url_for("auto_login"))

        # WHEN user tries to save this case to MME
        resp = controllers.matchmaker_add(
            request, institute_id=case_obj["owner"], case_name=case_obj["display_name"]
        )
        assert resp.status_code == 302  # redirect

        # AND no MME submission should be saved in the database
        updated_case = store.case_collection.find_one()
        assert "mme_submission" not in updated_case


def test_matchmaker_add(app, user_obj, case_obj, test_hpo_terms, mocker):
    # GIVEN a mocked response from MME server
    mocker.patch(
        "scout.server.extensions.matchmaker.patient_submit",
        return_value={"message": "ok", "status_code": 200},
    )
    # GIVEN an app containing MatchMaker connection params
    with app.test_client() as client:
        # GIVEN a user which is registered as a MatchMaker submitter
        store.user_collection.find_one_and_update(
            {"email": user_obj["email"]}, {"$set": {"roles": ["mme_submitter"]}}
        )
        client.get(url_for("auto_login"))

        # submitting a case with HPO terms and a pinned variant
        test_variant = store.variant_collection.find_one({"hgnc_symbols": ["POT1"]})
        updated_case = store.case_collection.find_one_and_update(
            {"_id": case_obj["_id"]},
            {"$set": {"suspects": [test_variant["_id"]], "phenotype_terms": test_hpo_terms}},
        )

        # WHEN user submits the case using the matchmaker_add controller
        saved_results = controllers.matchmaker_add(
            request, institute_id=case_obj["owner"], case_name=case_obj["display_name"]
        )
        assert saved_results == 1

        # THEN ine case should be uodated and a submission object correctly saved to database
        updated_case = store.case_collection.find_one()
        assert len(updated_case["mme_submission"]["patients"]) == 1


def test_matchmaker_delete(app, mme_submission, user_obj, case_obj, mocker):
    """testing controller function that deletes a case from MatchMaker"""
    # GIVEN a mocked response from MME server
    mocker.patch(
        "scout.server.extensions.matchmaker.patient_delete",
        return_value={"status_code": 200},
    )
    # GIVEN an app containing MatchMaker connection params
    with app.test_client() as client:
        # GIVEN a case with a MatchMaker submission:
        updated_case = store.case_collection.find_one_and_update(
            {"_id": case_obj["_id"]},
            {"$set": {"mme_submission": mme_submission}},
        )
        # GIVEN a user which is registered as a MatchMaker submitter
        store.user_collection.find_one_and_update(
            {"email": user_obj["email"]}, {"$set": {"roles": ["mme_submitter"]}}
        )
        client.get(url_for("auto_login"))

        # WHEN user deletes the case using the matchmaker_delete controller
        controllers.matchmaker_delete(
            request, institute_id=case_obj["owner"], case_name=case_obj["display_name"]
        )

        # THEN the case should be updated and the submission should be gone
        updated_case = store.case_collection.find_one()
        assert updated_case.get("mme_submission") is None


def test_matchmaker_match(app, mme_submission, user_obj, case_obj, mocker):
    """testing controller function to match one patient against other patients from Scout"""
    # GIVEN mocked responses from MME server
    mocker.patch(
        "scout.server.extensions.matchmaker.match_internal", return_value={"status_code": 200}
    )
    mocker.patch(
        "scout.server.extensions.matchmaker.match_external", return_value={"status_code": 200}
    )

    # GIVEN an app containing MatchMaker connection params
    with app.test_client() as client:
        # GIVEN a user which is registered as a MatchMaker submitter
        store.user_collection.find_one_and_update(
            {"email": user_obj["email"]}, {"$set": {"roles": ["mme_submitter"]}}
        )
        client.get(url_for("auto_login"))

        # GIVEN a case with a MatchMaker submission:
        updated_case = store.case_collection.find_one_and_update(
            {"_id": case_obj["_id"]},
            {"$set": {"mme_submission": mme_submission}},
        )

        # WHEN user submits a patient for matching on the Scout node (internal matching)
        ok_responses = controllers.matchmaker_match(
            request, "internal", institute_id=case_obj["owner"], case_name=case_obj["display_name"]
        )
        # The expected response should be succcess
        assert ok_responses > 0

        # WHEN user submits a patient for matching on a connected node (external matching)
        ok_responses = controllers.matchmaker_match(
            request, "external", institute_id=case_obj["owner"], case_name=case_obj["display_name"]
        )
        # The expected response should be not succcess since there are no connected nodes
        assert ok_responses == 0


def test_matchmaker_matches(app, mme_submission, match_objs, user_obj, case_obj, mocker):
    """Test controller that retrieves past matching results from the database and returns it to the view"""
    # GIVEN a mocked response from MME server
    mocker.patch(
        "scout.server.extensions.matchmaker.patient_matches",
        return_value={"status_code": 200, "content": {"matches": match_objs}},
    )

    # GIVEN an app containing MatchMaker connection params
    with app.test_client() as client:
        # GIVEN a user which is registered as a MatchMaker submitter
        store.user_collection.find_one_and_update(
            {"email": user_obj["email"]}, {"$set": {"roles": ["mme_submitter"]}}
        )
        client.get(url_for("auto_login"))

        # GIVEN a case with a MatchMaker submission:
        updated_case = store.case_collection.find_one_and_update(
            {"_id": case_obj["_id"]},
            {"$set": {"mme_submission": mme_submission}},
        )

        # WHEN the controller retrieves the matches data
        data = controllers.matchmaker_matches(
            request, institute_id=case_obj["owner"], case_name=case_obj["display_name"]
        )
        # THEN returned data should contain the expected fields should be as expected
        assert data["case"]["_id"] == updated_case["_id"]
        assert data["matches"]
