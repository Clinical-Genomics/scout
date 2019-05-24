# -*- coding: utf-8 -*-
from flask import url_for


# def test_panels(client, real_database, user_info):
#     # GIVEN a user connected to one institute in the database
#     institute_obj = real_database.institute(user_info['institutes'][0])
#     # WHEN accessing the panels overview page
#     resp = client.get(url_for('panels.panels'))
#     # THEN it should list the panels for that institute
#     assert resp.status_code == 200
#     assert institute_obj['display_name'] in resp.data

#     for panel_obj in real_database.panels(institute_id=institute_obj['_id']):
#         assert panel_obj['display_name'] in resp.data

def test_panel(client, real_panel_database, panel_info):
    adapter = real_panel_database

    # GIVEN a panel in the database
    panel_obj = adapter.gene_panels()[0]
    # WHEN accessing the panel view
    resp = client.get(url_for('panels.panel', panel_id=panel_obj['_id']))
    # THEN it should display the panel with all the genes
    assert resp.status_code == 200
    assert panel_obj['panel_name'].encode() in resp.data
    # assert panel_obj['version'] in resp.data
    assert resp.data.count('href="/genes/'.encode()) == len(panel_obj['genes'])


def test_panels(app, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for('auto_login'))
        assert resp.status_code == 200

        # WHEN accessing the cases page
        resp = client.get(url_for('panels.panels'))

        # THEN it should return a page
        assert resp.status_code == 200


def test_panel_export(client, real_panel_database, panel_info):
    adapter = real_panel_database

    # GIVEN a panel in the database
    panel_obj = adapter.gene_panels()[0]
    # WHEN accessing the panel view
    resp = client.get(url_for('panels.panel_export', panel_id=panel_obj['_id']))
    # THEN it should display the panel with all the genes
    assert resp.status_code == 200
