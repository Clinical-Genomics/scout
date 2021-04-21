from flask import request, url_for
from flask_login import current_user

from scout.server.blueprints.cases.controllers import matchmaker_check_requirements


def test_matchmaker_check_requirements_unauthorized_user(app, user_obj, case_obj):
    """Test function controlling that MME requirememts are fullfilled"""

    # GIVEN an app containing MatchMaker connection params
    with app.test_client() as client:

        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # GIVEN a request received from case
        referer = f"/{case_obj['owner']}/{case_obj['display_name']}"
        with app.test_request_context("url", headers={"referer": referer}):

            resp = matchmaker_check_requirements(request)
            assert resp.status_code == 302
