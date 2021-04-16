from flask import url_for

from scout.server.blueprints.cases import controllers

RESPONSE = jsonify({"message": "ok"})


def test_matchmaker_check_requirements_unauthorized_user(app, user_obj):
    """Test function ccontrolling that MME requirememts are fullfilled"""

    # GIVEN an app containing MatchMaker connection params
    with app.test_client() as client:

        # GIVEN that the user has no "mme_submitter" role
        assert "mme_submitter" not in user_obj["roles"]

        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        ok_requirements = controllers.matchmaker_check_requirements(None)
        assert ok_requirements is None
