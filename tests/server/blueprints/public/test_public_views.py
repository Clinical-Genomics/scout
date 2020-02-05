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
