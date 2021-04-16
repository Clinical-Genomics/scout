import flask
import requests

from scout.server.blueprints.cases import controllers


def test_matchmaker_check_requirements_unauthorized_user(app, user_obj, mocker):
    """Test function ccontrolling that MME requirememts are fullfilled"""

    # GIVEN an app containing MatchMaker connection params
    with app.test_client() as client:

        # GIVEN that the user has no "mme_submitter" role
        assert "mme_submitter" not in user_obj["roles"]

        # GIVEN a mock request to MatchMaker controllers
        s = requests.Session()

        # GIVEN that the user could be logged in
        resp = client.get(flask.url_for("auto_login"))
        assert resp.status_code == 200

        ok_requirements = controllers.matchmaker_check_requirements(s)
        assert ok_requirements is None
