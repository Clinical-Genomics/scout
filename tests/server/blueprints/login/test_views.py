# -*- coding: utf-8 -*-
from flask import url_for
from flask_login import current_user

from scout.server.extensions import ldap_manager, store


def test_unathorized_login(app, institute_obj, case_obj):
    """Test failed authentication against scout database"""

    # GIVEN an initialized app
    # WHEN trying tp access scout with the email of an non-existing user
    with app.test_client() as client:
        resp = client.get(url_for("login.login", email="fakey_user@email.com"))

        # THEN response should redirect to user authentication form (index page)
        assert resp.status_code == 302
        # And current user should NOT be authenticated
        assert current_user.is_authenticated is False


def test_authorized_login(app, user_obj):
    """Test successful authentication against scout database"""

    # GIVEN an initialized app
    # WHEN trying to access scout with the email of an existing user
    with app.test_client() as client:
        resp = client.get(url_for("login.login", email=user_obj["email"]))

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
        form_data = {"username": "test_user", "password": "test_password"}
        resp = client.post(url_for("login.login", **form_data))

        # THEN current user should be authenticated
        assert current_user.is_authenticated
