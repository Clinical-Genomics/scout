# -*- coding: utf-8 -*-
from flask import url_for


def test_gene_variants(app, user_obj, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the dashboard page
        resp = client.get(
            url_for("cases.gene_variants", institute_id=institute_obj["internal_id"])
        )

        # THEN it should return a page
        assert resp.status_code == 200
