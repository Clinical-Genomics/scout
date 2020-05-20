# -*- coding: utf-8 -*-
import logging

# from urllib.request import urlopen

from flask import url_for
from flask_login import current_user
from scout.server.blueprints.login.models import LoginUser

log = logging.getLogger(__name__)


def test_dashboard(app, user_obj, institute_obj):
    # GIVEN an initialized client
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        our_current_user = current_user.name
        log.debug("Current user %s", our_current_user)
        log.debug("Current user institutes {}".format(current_user.institutes))

        # WHEN accessing the dashboard page
        resp = client.get(url_for("dashboard.index", institute_id=institute_obj["internal_id"]))

        # THEN it should return a page
        assert resp.status_code == 200
