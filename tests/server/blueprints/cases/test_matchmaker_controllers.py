from flask import request, url_for
from flask_login import current_user

from scout.server.blueprints.cases.controllers import matchmaker_check_requirements
from scout.server.extensions import matchmaker, store


def test_matchmaker_check_requirements_wrong_settings(app):
    """Test that the matchmaker_check_requirements redirects if app settings requirements are not met"""
    # GIVEN an app that is not properly configured and it's missing either
    # matchmaker.host, matchmaker.accept, matchmaker.token
    with app.test_client() as client:
        del matchmaker.host

        # GIVEN a user that is logged in but doesn't have access to MatchMaker
        client.get(url_for("auto_login"))
        # THEN the matchmaker_check_requirements function should redirect to the previous page
        resp = matchmaker_check_requirements(request)
        assert resp.status_code == 302


def test_matchmaker_check_requirements_unauthorized_user(app, user_obj):
    """Test redirect when a user is not authorized to access MatchMaker functionality"""
    # GIVEN an app containing MatchMaker connection params
    with app.test_client() as client:
        # GIVEN a user that is logged in but doesn't have access to MatchMaker
        client.get(url_for("auto_login"))
        # THEN the matchmaker_check_requirements function should redirect to the previous page
        resp = matchmaker_check_requirements(request)
        assert resp.status_code == 302


def test_matchmaker_check_requirements_authorized_user(app, user_obj):
    """Test a user with MatchMaker content access does not get redirected to previous page"""
    # GIVEN an app containing MatchMaker connection params
    with app.test_client() as client:
        # Given a user which is registered as a MatchMaker submitter
        store.user_collection.find_one_and_update(
            {"email": user_obj["email"]}, {"$set": {"roles": ["mme_submitter"]}}
        )
        # AND a user that is logged in but doesn't have access to MatchMaker
        client.get(url_for("auto_login"))
        # THEN the matchmaker_check_requirements function should redirect to the previous page
        resp = matchmaker_check_requirements(request)
        assert resp is None
