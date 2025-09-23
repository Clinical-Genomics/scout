# -*- coding: utf-8 -*-
import responses
from flask import url_for
from flask_login import login_user

from scout.server.app import create_app
from scout.server.blueprints.login.models import LoginUser
from scout.server.extensions import config_igv_tracks, store
from scout.utils.ensembl_rest_clients import RESTAPI_URL


def test_remote_static_no_auth(app, case_obj, institute_obj):
    """Test endpoint that serves alignment files as non-logged user"""
    # GIVEN a running demo app
    with app.test_client() as client:
        # GIVEN that user is not logged in
        resp = client.get(
            url_for(
                "alignviewers.remote_static",
                file="../demo/ACC5963A1_lanes_1234_star_sorted_sj_filtered_sorted.bed.gz",
                case_name=case_obj["display_name"],
                institute_id=institute_obj["_id"],
            )
        )
        # THEN endpoint should return unauthorized (401)
        assert resp.status_code == 401


def test_remote_static_not_in_session(app, case_obj, institute_obj):
    """Test endpoint that serves alignment files that are not saved in the session"""

    # GIVEN a running demo app
    with app.test_client() as client:
        # GIVEN that user is logged in
        client.get(url_for("auto_login"))
        # If requested file is not authorized
        resp = client.get(
            url_for(
                "alignviewers.remote_static",
                file="config.py",
                case_name=case_obj["display_name"],
                institute_id=institute_obj["_id"],
            )
        )
        # THEN endpoint should return forbidden (401)
        assert resp.status_code == 403


def test_remote_static(app, institute_obj):
    """Test endpoint that serves files as a logged user"""
    # GIVEN a file on a case

    # GIVEN a running demo app
    with app.test_client() as client:
        # GIVEN that user is logged in
        client.get(url_for("auto_login"))
        case_obj = store.case_collection.find_one()
        institute_id = case_obj["owner"]
        file = case_obj["individuals"][0]["splice_junctions_bed"]

        # THEN the resource should be available to the user
        resp = client.get(
            url_for(
                "alignviewers.remote_static",
                file=file,
                case_name=case_obj["display_name"],
                institute_id=institute_id,
            )
        )
        assert resp.status_code == 200


def test_remote_cors_wrong_resource(app):
    """Test endpoint that serves as a proxy to the actual remote track on the cloud"""
    # GIVEN a resource not authorized
    an_url = "http://google.com"

    # GIVEN a running demo app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # WHEN the remote cors endpoint is invoked with an url
        resp = client.get(url_for("alignviewers.remote_cors", remote_url=an_url))

        # THEN it should return forbidden (403)
        assert resp.status_code == 403


def test_remote_cors(real_database_name, user_obj):
    """Test endpoint that serves as a proxy to the actual remote track on the cloud"""

    # GIVEN an igv track on the cloud
    # GIVEN app config settings with this custom remote track
    TRACK_NAME = "A custom remote track"
    TRACK_URL = "https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/25777460/GRCh37.variant_call.clinical.pathogenic_or_likely_pathogenic.vcf.gz.tbi"
    TRACK_BUILD = "37"
    track = {
        "name": TRACK_NAME,
        "type": "annotation",
        "format": "bigbed",
        "build": TRACK_BUILD,
        "url": TRACK_URL,
    }

    config = {
        "CUSTOM_IGV_TRACKS": [{"tracks": [track]}],
        "TESTING": True,
        "SERVER_NAME": "test",
        "DEBUG": True,
        "MONGO_DBNAME": real_database_name,
        "DEBUG_TB_ENABLED": False,
        "LOGIN_DISABLED": True,
        "WTF_CSRF_ENABLED": False,
    }

    # THEN the initialized app should create a config_igv_tracks extension
    igv_track_app = create_app(config=config)

    @igv_track_app.route("/auto_login")
    def auto_login():
        user_inst = LoginUser(user_obj)
        assert login_user(user_inst, remember=True)
        return "ok"

    with igv_track_app.test_client() as client:
        # GIVEN that the user could be logged in
        with igv_track_app.app_context():
            client.get(url_for("auto_login"))

            # WHEN a given track is configured for remote CORS
            assert config_igv_tracks.tracks[TRACK_BUILD][0]["url"] == TRACK_URL

            # WHEN the remote cors endpoint is invoked with that track
            resp = client.get(
                url_for(
                    "alignviewers.remote_cors",
                    remote_url=TRACK_URL,
                )
            )

            # THEN response should be successful
            assert resp.status_code == 200


def test_igv_not_authorized(app, user_obj, case_obj, variant_obj):
    """Test view requests and produces igv alignments, when the user dosn't have access to the case"""

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user is logged in but not authorized to see the page
        client.get(url_for("auto_login_not_authorized"))

        # WHEN the igv endpoint is invoked with the right parameters
        resp = client.get(
            url_for(
                "alignviewers.igv",
                institute_id=case_obj["owner"],
                case_name=case_obj["display_name"],
                variant_id=variant_obj["_id"],
            )
        )

        # THEN the response should be "not authorized" (403)
        assert resp.status_code == 403


def test_igv_authorized(app, user_obj, case_obj, variant_obj):
    """Test view requests and produces igv alignments, when the user has access to the case"""

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user is logged in
        client.get(url_for("auto_login"))

        # WHEN the igv endpoint is invoked with the right parameters
        resp = client.get(
            url_for(
                "alignviewers.igv",
                institute_id=case_obj["owner"],
                case_name=case_obj["display_name"],
                variant_id=variant_obj["_id"],
            )
        )

        # THEN the response should be a valid HTML page
        assert resp.status_code == 200


@responses.activate
def test_sashimi_igv(app, user_obj, case_obj, variant_obj, ensembl_liftover_response):
    """Test view requests and produces igv alignments, when the user has access to the case"""

    # GIVEN a mocked response from the Ensembl liftover service
    chromosome = variant_obj["chromosome"]
    position = variant_obj["position"]
    mocked_liftover_url = f"{RESTAPI_URL}/map/human/GRCh37/{chromosome}:{position}..{position}/GRCh38?content-type=application/json"
    responses.add(
        responses.GET,
        mocked_liftover_url,
        json=ensembl_liftover_response,
        status=200,
    )

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user is logged in
        client.get(url_for("auto_login"))

        # WHEN the igv endpoint is invoked with the right parameters
        resp = client.get(
            url_for(
                "alignviewers.sashimi_igv",
                institute_id=case_obj["owner"],
                case_name=case_obj["display_name"],
                variant_id=variant_obj["_id"],
            )
        )

        # THEN the response should be a valid HTML page
        assert resp.status_code == 200
