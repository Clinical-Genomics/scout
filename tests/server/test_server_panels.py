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

def test_panel(client, real_database, panel_info):
    # GIVEN a panel in the database
    panel_obj = real_database.gene_panels()[0]
    # WHEN accessing the panel view
    resp = client.get(url_for('panels.panel', panel_id=panel_obj['_id']))
    # THEN it should display the panel with all the genes
    assert resp.status_code == 200
    assert panel_obj['panel_name'].encode() in resp.data
    # assert panel_obj['version'] in resp.data
    assert resp.data.count('href="/genes/'.encode()) == len(panel_obj['genes'])
