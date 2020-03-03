# -*- coding: utf-8 -*-
from flask import url_for
from urllib.parse import urlencode

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


def test_panel_get(client, real_panel_database):
    adapter = real_panel_database

    # GIVEN a panel in the database
    panel_obj = adapter.gene_panels()[0]
    # WHEN accessing the panel view
    resp = client.get(url_for("panels.panel", panel_id=panel_obj["_id"]))
    # THEN it should display the panel with all the genes
    assert resp.status_code == 200
    assert panel_obj["panel_name"].encode() in resp.data
    # assert panel_obj['version'] in resp.data
    assert resp.data.count('href="/genes/'.encode()) == len(panel_obj["genes"])


def test_panel_update_description(client, real_panel_database):
    adapter = real_panel_database

    # GIVEN a panel in the database
    panel_obj = adapter.gene_panels()[0]
    assert panel_obj.get("description") is None

    data = urlencode(
        {
            "update_description": True,  # This is the submit button of the form
            "panel_description": "Test description",  # This is the text field
        }
    )
    # WHEN posting an update description request to panel page
    resp = client.post(
        url_for("panels.panel", panel_id=panel_obj["_id"]),
        data=data,
        content_type="application/x-www-form-urlencoded",
    )
    # THEN the panel object should be updated with the new description:
    panel_obj = adapter.gene_panels()[0]
    assert panel_obj["description"] == "Test description"


def test_panel_modify_genes(client, real_panel_database):
    adapter = real_panel_database

    # GIVEN a panel in the database
    panel_obj = adapter.gene_panels()[0]

    # WHEN posting a delete gene request to panel page
    a_gene = panel_obj["genes"][0]  # first gene of the panel
    data = urlencode({"action": "delete", "hgnc_id": a_gene["hgnc_id"]})
    resp = client.post(
        url_for("panels.panel", panel_id=panel_obj["_id"]),
        data=data,
        content_type="application/x-www-form-urlencoded",
    )
    # THEN the pending actions of panel should be updated:
    panel_obj = adapter.gene_panels()[0]
    assert panel_obj["pending"][0]["action"] == "delete"
    assert panel_obj["pending"][0]["hgnc_id"] == a_gene["hgnc_id"]

    # WHEN removing that gene using the client
    new_version = panel_obj["version"] + 1
    data = urlencode({"action": "submit", "version": new_version})

    resp = client.post(
        url_for("panels.panel_update", panel_id=panel_obj["_id"]),
        data=data,
        content_type="application/x-www-form-urlencoded",
    )

    # THEN the new panel object should have the correct new version
    new_panel_obj = adapter.gene_panel(panel_obj["panel_name"])
    assert new_panel_obj["version"] == new_version

    # needs a real app context due to user check. Repeat with app?
    # resp = client.get(url_for('panels.panels'))
    # assert new_version in str(resp.data)

    # remove gene from panel object using adapter:
    panel_obj["genes"] = panel_obj["genes"][1:]
    updated_panel = adapter.update_panel(panel_obj)

    # WHEN posting an add gene request to panel page
    data = urlencode({"action": "add", "hgnc_id": a_gene["hgnc_id"]})
    resp = client.post(
        url_for("panels.panel", panel_id=updated_panel["_id"]),
        data=data,
        content_type="application/x-www-form-urlencoded",
    )
    # Then response should redirect to gene edit page
    assert resp.status_code == 302


def test_panels(app, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the cases page
        resp = client.get(url_for("panels.panels"))

        # THEN it should return a page
        assert resp.status_code == 200


# This test is slow since pdf rendering is slow
def test_panel_export(client, real_panel_database):
    adapter = real_panel_database
    # GIVEN a panel in the database
    panel_obj = adapter.panel_collection.find_one()
    assert True
    # WHEN accessing the panel view
    resp = client.get(url_for("panels.panel_export", panel_id=panel_obj["_id"]))
    # THEN it should display the panel with all the genes
    assert resp.status_code == 200


def test_gene_edit(client, real_panel_database):
    """Test interface that allows gene panel editing, GET method"""
    adapter = real_panel_database

    # GIVEN a panel in the database
    panel_obj = adapter.gene_panels()[0]

    # WITH at least a gene
    gene = panel_obj["genes"][0]
    assert gene

    # WHEN accessing the panel gene_edit view
    resp = client.get(
        url_for("panels.gene_edit", panel_id=panel_obj["_id"], hgnc_id=gene["hgnc_id"])
    )
    # THEN it should return a valid page
    assert resp.status_code == 200
