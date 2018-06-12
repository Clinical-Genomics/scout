# -*- coding: utf-8 -*-
from flask import url_for

from scout import __version__


def test_auth(client):
    # GIVEN an anonymous user
    # WHEN accessing the authorized view
    resp = client.get(url_for('login.authorized'))
    # THEN the response should not be ok since no ine is authorized
    assert resp.status_code == 400
