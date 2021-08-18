# -*- coding: utf-8 -*-
from flask import url_for

from scout import __version__
from scout.server.app import create_app


def test_index(client):
    # GIVEN an anonymous user
    # WHEN accessing the index view
    resp = client.get(url_for("public.index"))
    # THEN the response should be ok and display version information
    assert resp.status_code == 200
    assert __version__.encode() in resp.data


def test_accreditation_badge(app):
    """Test configuration of accreditation bage."""

    # GIVEN an initialized app with accreditation badge in settings
    assert app.config["ACCREDITATION_BADGE"]

    with app.test_client() as client:
        resp = client.get(url_for("public.index"))
        # THEN accred badge shuld not be displayed
        assert b'id="accred-badge"' in resp.data
