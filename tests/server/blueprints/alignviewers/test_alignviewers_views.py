# -*- coding: utf-8 -*-
from flask import session, url_for

from scout.server.extensions import store


def test_remote_static_no_auth(app):
    """Test endpoint that serves alignment files as non-logged user"""
    # GIVEN a running demo app
    with app.test_client() as client:
        # GIVEN that user is not logged in
        resp = client.get(
            url_for(
                "alignviewers.remote_static",
                file="../demo/ACC5963A1_lanes_1234_star_sorted_sj_filtered_sorted.bed.gz",
            )
        )
        # THEN endpoint should return forbidden (403)
        assert resp.status_code == 403


def test_test_remote_static_not_in_session(app):
    """Test endpoint that serves alignment files that are not saved in the session"""

    # GIVEN a running demo app
    with app.test_client() as client:
        # GIVEN that user is ßlogged in
        client.get(url_for("auto_login"))
        # If requested file doesn't have a valid extension
        resp = client.get(
            url_for(
                "alignviewers.remote_static",
                file="config.py",
            )
        )
        # THEN endpoint should return forbidden (403)
        assert resp.status_code == 403


def test_remote_static(app):
    """Test endpoint that serves files as a logged user"""
    # GIVEN a file on disk
    file = "../demo/ACC5963A1_lanes_1234_star_sorted_sj_filtered_sorted.bed.gz"

    # GIVEN a running demo app
    with app.test_client() as client:
        # GIVEN that user is logged in
        client.get(url_for("auto_login"))

        # GIVEN that resource file exists in user session
        with client.session_transaction() as session:
            session["igv_tracks"] = [file]

        # THEN the resource should be available to the user
        resp = client.get(
            url_for(
                "alignviewers.remote_static",
                file=file,
            )
        )
        assert resp.status_code == 200


def test_remote_cors_wrong_resource(app):
    """Test endpoint that serves as a proxy to the actual remote track on the cloud"""
    # GIVEN a resource not present in session["igv_tracks"]
    an_url = "http://google.com"

    # GIVEN a running demo app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # WHEN the remote cors endpoint is invoked with an url
        resp = client.get(url_for("alignviewers.remote_cors", remote_url=an_url))

        # THEN it should return forbidden (403)
        assert resp.status_code == 403


def test_remote_cors(app):
    """Test endpoint that serves as a proxy to the actual remote track on the cloud"""
    # GIVEN an igv track on the cloud
    cloud_track_url = "https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/25777460/GRCh37.variant_call.clinical.pathogenic_or_likely_pathogenic.vcf.gz.tbi"

    # GIVEN a running demo app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # GIVEN that resource url exists in user session
        with client.session_transaction() as session:
            session["igv_tracks"] = [cloud_track_url]

        # WHEN the remote cors endpoint is invoked with cloud_track_url
        resp = client.get(url_for("alignviewers.remote_cors", remote_url=cloud_track_url))

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
        # AND when the reponse is closed case IGV tracks should be removed from session
        resp.close()
        assert session.get("igv_tracks") is None
