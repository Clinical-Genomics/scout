# -*- coding: utf-8 -*-
from flask import url_for

from scout import __version__


def test_index(client):
    # GIVEN an anonymous user
    # WHEN accessing the index view
    resp = client.get(url_for("public.index"))
    # THEN the response should be ok and display version information
    assert resp.status_code == 200
    assert __version__.encode() in resp.data


def test_accreditation_badge(app):
    """Test configuration of accreditation bage."""
    # GIVEN initialized app
    with app.test_client() as client:
        resp = client.get(url_for("public.index"))
        # THEN accred badge shuld be displayed by default
        assert b'id="accred-badge"' in resp.data

    # GIVEN initialized app and file is missing
    app.config["ACCREDITATION_BADGE"] = "missing_file.png"
    with app.test_client() as client:
        resp = client.get(url_for("public.index"))
        # THEN accred badge shuld not be displayed
        assert b'id="accred-badge"' not in resp.data

    # GIVEN initialized app and not configured accreditation badge
    del app.config["ACCREDITATION_BADGE"]
    with app.test_client() as client:
        resp = client.get(url_for("public.index"))
        # THEN accred badge shuld not be displayed
        assert b'id="accred-badge"' not in resp.data
