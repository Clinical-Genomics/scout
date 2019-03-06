# -*- coding: utf-8 -*-
from flask import url_for

def test_gene_variants(app, user_obj, institute_obj):
    # GIVEN an initialized database
    # WHEN accessing the genes variants page
    # GIVEN an initialized client
    # GIVEN a valid user

    with app.test_client() as client:
        # Login
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # WHEN accessing the dashboard page
        #    resp = urlopen(url_for('dashboard.index',
        #                                    institute_id=institute_obj['internal_id'],
        #                                    _external=True))
        resp = client.get(url_for('cases.gene_variants',
                                  institute_id=institute_obj['internal_id']))

        # THEN it should return a page
        assert resp.status_code == 200
