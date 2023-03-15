# -*- coding: utf-8 -*-
from flask import url_for

from scout.server.extensions import store


def test_panel_api_json(client, real_panel_database):
    # GIVEN a panel in the database
    panel_obj = real_panel_database.gene_panels()[0]
    panel_name = panel_obj["panel_name"]

    # WHEN querying the gene panels api endpoint
    resp = client.get(url_for("panels.api_panels", panel_name=panel_name))
    # THEN it should JSON response with the target gene panel included
    assert len(resp.json) > 0
    assert panel_name in str(resp.json)


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


def test_panel_update_description(app):
    """Test the endpoint that updates gene panel description"""

    # GIVEN a panel in the database
    panel_obj = store.gene_panels()[0]
    assert panel_obj.get("description") is None

    form_data = {
        "update_description": True,  # This is the submit button of the form
        "panel_description": "Some description",  # This is the text field
    }

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # WHEN posting an update description request to panel page
        resp = client.post(
            url_for("panels.panel", panel_id=panel_obj["_id"]),
            data=form_data,
        )
        # THEN the panel object should be updated with the new description:
        panel_obj = store.gene_panels()[0]
        assert panel_obj["description"] == "Some description"


def test_panel_modify_genes(app, real_panel_database):
    """Test the functionality to modify genes in a gene panel"""

    # GIVEN a panel in the database
    panel_obj = store.gene_panels()[0]

    # WHEN posting a delete gene request to panel page
    a_gene = panel_obj["genes"][0]  # first gene of the panel
    form_data = {"action": "delete", "hgnc_id": a_gene["hgnc_id"]}
    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        resp = client.post(
            url_for("panels.panel", panel_id=panel_obj["_id"]),
            data=form_data,
        )
        # THEN the pending actions of panel should be updated:
        panel_obj = store.gene_panels()[0]
        assert panel_obj["pending"][0]["action"] == "delete"
        assert panel_obj["pending"][0]["hgnc_id"] == a_gene["hgnc_id"]

        # WHEN removing that gene using the client
        new_version = panel_obj["version"] + 1
        form_data = {"action": "submit", "version": new_version}

        resp = client.post(
            url_for("panels.panel_update", panel_id=panel_obj["_id"]),
            data=form_data,
        )

        # THEN the new panel object should have the correct new version
        new_panel_obj = store.gene_panel(panel_obj["panel_name"])
        assert new_panel_obj["version"] == new_version

        # remove gene from panel object using adapter:
        panel_obj["genes"] = panel_obj["genes"][1:]
        updated_panel = store.update_panel(panel_obj)

        # WHEN posting an add gene request to panel page
        form_data = {"action": "add", "hgnc_id": a_gene["hgnc_id"]}
        resp = client.post(
            url_for("panels.panel", panel_id=updated_panel["_id"]),
            data=form_data,
        )
        # Then response should redirect to gene edit page
        assert resp.status_code == 302


# This test is slow since pdf rendering is slow
def test_delete_panel(app, real_panel_database):
    adapter = real_panel_database
    # GIVEN a panel in the database
    panel_obj = adapter.panel_collection.find_one()
    assert True

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        # WHEN accessing the panel view
        resp = client.post(url_for("panels.panel_delete", panel_id=panel_obj["_id"]))
        # THEN it should display the panel with all the genes
        assert resp.status_code == 302
        # assert panel is hidden in database
        panel_obj = adapter.panel_collection.find_one({"_id": panel_obj["_id"]})
        assert panel_obj.get("hidden")


def test_panels(app):
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


def test_gene_panel_export_txt(client, real_panel_database):
    """Test the endpoint that exports gene panels in TXT format"""

    adapter = real_panel_database
    # GIVEN a panel in the database
    panel_obj = adapter.panel_collection.find_one()
    # WHEN using the panels.panel_export_txt endpoint
    resp = client.get(url_for("panels.panel_export_txt", panel_id=panel_obj["_id"]))
    # THEN it should download the panel in the right format
    assert resp.status_code == 200
    assert resp.mimetype == "text/txt"


def test_panel_export_pdf(client, real_panel_database):
    """Test the endpoint that exports gene panels in PDF format"""

    adapter = real_panel_database
    # GIVEN a panel in the database
    panel_obj = adapter.panel_collection.find_one()
    # WHEN using the panels.panel_export_pdf endpoint
    resp = client.get(url_for("panels.panel_export_pdf", panel_id=panel_obj["_id"]))
    # THEN it should download the panel in PDF format
    assert resp.status_code == 200
    assert resp.mimetype == "application/pdf"


def test_panel_export_case_hits(app, real_panel_database):
    """Test function used for exporting all genes with variant hits for a case"""

    # GIVEN a case and a gene panel in the database
    adapter = real_panel_database
    panel_obj = adapter.panel_collection.find_one()
    case_obj = adapter.case_collection.find_one()

    # GIVEN an initialized app and a valid user
    with app.test_client() as client:
        client.get(url_for("auto_login"))

        # WHEN downloading the case variants hits report
        form_data = {"case_name": " - ".join([case_obj["owner"], case_obj["display_name"]])}
        resp = client.post(
            url_for("panels.panel_export_case_hits", panel_id=panel_obj["_id"]), data=form_data
        )
        # THEN the response should be successful
        assert resp.status_code == 200
        # And should download a PDF file
        assert resp.mimetype == "application/pdf"


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
