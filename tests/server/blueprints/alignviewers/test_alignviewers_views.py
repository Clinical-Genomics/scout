# -*- coding: utf-8 -*-
import requests

from flask import url_for


def test_remote_cors(app):
    """Test endpoint that servers as a proxy to the actual remote track on the cloud"""
    cloud_track_url = "http://google.com"

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN the remote cors endpoint is invoked with an url
        resp = client.get(url_for("alignviewers.remote_cors", remote_url=cloud_track_url))
        # THEN it should return success response
        assert resp.status_code == 200


def test_igv(app, user_obj, case_obj):
    """Test view which accepts POST requests and produces igv alignments"""

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:

        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # And that the individuals comtain a MT bam file
        samples = []
        bam_files = []
        bai_files = []

        for ind in case_obj["individuals"]:
            mt_bam = ind["mt_bam"]
            bam_files.append(mt_bam)
            bai_files.append(mt_bam.replace(".bam", ".bai"))
            samples.append(ind["individual_id"])

        assert len(bam_files) == len(case_obj["individuals"])
        assert len(bai_files) == len(case_obj["individuals"])
        assert len(samples) == len(case_obj["individuals"])

        # WHEN the requited parameters are passed to the igv view:
        request_data = {
            "sample": ",".join(samples),
            "build": "37",
            "contig": "MT",
            "start": "15326",
            "stop": "15326",
            "mt_bam": ",".join(bam_files),
            "mt_bai": ",".join(bai_files),
            "align": "mt_bam",
        }

        resp = client.post(url_for("alignviewers.igv"), data=request_data)

        # THEN the response should be a valid HTML page
        assert resp.status_code == 200
