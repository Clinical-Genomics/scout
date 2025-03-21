# -*- coding: utf-8 -*-
import pytest
from flask import redirect, url_for
from flask_login import current_user


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


def test_ldap_login(ldap_app, user_obj, mocker):
    """Test authentication using LDAP"""

    # GIVEN a patched LDAP module
    mocker.patch("scout.server.extensions.ldap_manager.authenticate", return_value=True)

    # GIVEN a patched database containing the user
    mocker.patch("scout.server.blueprints.login.views.store.user", return_value=user_obj)

    # GIVEN an initialized app with LDAP config params
    with ldap_app.test_client() as client:
        # When submitting LDAP username and password
        form_data = {"ldap_user": "test_user", "ldap_password": "test_password"}
        client.post(url_for("login.login"), data=form_data)

        # THEN current user should be authenticated
        assert current_user.is_authenticated


@pytest.mark.parametrize(
    "app_fixture, oauth_provider",
    [
        ("google_app", "google"),
        ("keycloak_app", "keycloak"),
    ],
)
def test_oauth_login(request, app_fixture, oauth_provider, user_obj, mocker):
    """Test authentication using different providers (Google and Keycloak for now)."""

    # Resolve the correct app fixture dynamically
    app = request.getfixturevalue(app_fixture)

    # GIVEN a patched database containing the user
    mocker.patch("scout.server.blueprints.login.views.store.user", return_value=user_obj)

    # GIVEN a set of patched responses from the OAuth provider
    mock_redirect_to_auth = redirect(url_for("login.authorized"))
    mocker.patch(
        f"scout.server.blueprints.login.controllers.oauth_client.{oauth_provider}.authorize_redirect",
        return_value=mock_redirect_to_auth,
    )
    mocker.patch(
        f"scout.server.blueprints.login.controllers.oauth_client.{oauth_provider}.authorize_access_token",
        return_value={"access_token": "fake_access_token"},
    )
    fake_user = {
        "email": user_obj["email"],
        "name": user_obj["name"],
        "locale": "en",
    }
    mocker.patch(
        f"scout.server.blueprints.login.controllers.oauth_client.{oauth_provider}.parse_id_token",
        return_value=fake_user,
    )

    # GIVEN an initialized app with proper config
    with app.test_client() as client:
        # GIVEN that session doesn't contain user data
        with client.session_transaction() as mock_session:
            assert "email" not in mock_session

        with app.app_context():
            # THEN the login should be successful
            resp = client.post(url_for("login.login"), follow_redirects=True)
            assert resp.status_code == 200
            # AND the user should be authenticated
            assert current_user.is_authenticated
