# -*- coding: utf-8 -*-
from flask import redirect, url_for
from flask_login import current_user

from scout.server.extensions import ldap_manager, store


def test_unathorized_database_login(app):
    """Test failed authentication against scout database"""

    # GIVEN an initialized app
    # WHEN trying tp access scout with the email of an non-existing user
    with app.test_client() as client:
        form_data = {"email": "fakey_user@email.com"}
        resp = client.post(url_for("login.login"), data=form_data)

        # THEN response should redirect to user authentication form (index page)
        assert resp.status_code == 302
        # And current user should NOT be authenticated
        assert current_user.is_authenticated is False


def test_authorized_database_login(app, user_obj):
    """Test successful authentication against scout database"""

    # GIVEN an initialized app
    # WHEN trying to access scout with the email of an existing user
    with app.test_client() as client:
        form_data = {"email": user_obj["email"]}
        resp = client.post(url_for("login.login"), data=form_data)

        # THEN response should redirect to user institutes
        assert resp.status_code == 302
        # And current user should be authenticated
        assert current_user.is_authenticated


def test_ldap_login(ldap_app, user_obj, monkeypatch):
    """Test authentication using LDAP"""

    # Given a MonkeyPatched flask_ldap3_login authenticate functionality
    def validate_ldap(*args, **kwargs):
        return True

    def return_user(*args, **kwargs):
        return user_obj

    monkeypatch.setattr(ldap_manager, "authenticate", validate_ldap)
    monkeypatch.setattr(store, "user", return_user)

    # GIVEN an initialized app with LDAP config params
    with ldap_app.test_client() as client:
        # When submitting LDAP username and password
        form_data = {"ldap_user": "test_user", "ldap_password": "test_password"}
        client.post(url_for("login.login"), data=form_data)

        # THEN current user should be authenticated
        assert current_user.is_authenticated


def test_google_login_request_authentication(google_app, user_obj, mocker):
    """Test authentication using Google credentials, first step - redirect from Google."""

    # GIVEN an initialized app with GOOGLE config params
    with google_app.test_client() as client:

        # GIVEN that session doesn't contain user data
        with client.session_transaction() as mock_session:
            assert "email" not in mock_session

        with google_app.app_context():

            # GIVEN a patched redirect response from Google
            mock_redirect_response = redirect(url_for("login.authorized"))
            mocker.patch(
                "scout.server.blueprints.login.controllers.oauth_client.google.authorize_redirect",
                return_value=mock_redirect_response,
            )

            # THEN the response from login should be a redirect
            resp = client.post(url_for("login.login"))
            assert resp.status_code == 302


def test_google_login_authenticated(google_app, user_obj, mocker):
    """Test authentication using Google credentials, second step - authentication passed."""

    # GIVEN a patched database containing the user
    mocker.patch("scout.server.blueprints.login.views.store.user", return_value=user_obj)

    # GIVEN an initialized app with GOOGLE config params
    with google_app.test_client() as client:

        # GIVEN that the user has been already authenticated
        with client.session_transaction() as mock_session:
            mock_session["email"] = user_obj["email"]

        with google_app.app_context():
            # AFTER the first redirection
            client.post(url_for("login.login"))

            # THEN the user should be authenticated
            assert current_user.is_authenticated
