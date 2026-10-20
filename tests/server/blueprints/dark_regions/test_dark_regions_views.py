from flask import url_for

from scout.server.extensions import store


def test_dark_regions_sma_dark(app, institute_obj, case_obj):
    """Test SMA dark page loading from dark_regions blueprint."""

    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        resp = client.get(
            url_for(
                "dark_regions.sma",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )

        assert resp.status_code == 200
        assert b'value="hpo"' in resp.data


def test_dark_regions_sma_dark_gene_panel_filter(app, case_obj, institute_obj):
    """Test SMA dark page loading with a selected gene panel filter."""

    selected_panel = case_obj["panels"][0]["panel_name"]

    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        resp = client.get(
            url_for(
                "dark_regions.sma",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                gene_panels=[selected_panel],
            )
        )

        assert resp.status_code == 200
        assert bytes(selected_panel, "utf-8") in resp.data

        selected_option_snippets = [
            f'value="{selected_panel}" selected',
            f'selected value="{selected_panel}"',
            f'value="{selected_panel}" selected="selected"',
            f'selected="selected" value="{selected_panel}"',
        ]
        assert any(bytes(snippet, "utf-8") in resp.data for snippet in selected_option_snippets)


def test_dark_regions_sma_dark_explicit_empty_filter_shows_all(app, case_obj, institute_obj):
    """Explicit empty panel filter should not be replaced by default case panel selection."""

    selected_panel = case_obj["panels"][0]["panel_name"]

    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        resp = client.get(
            url_for(
                "dark_regions.sma",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                panel_filter_applied="1",
            )
        )

        assert resp.status_code == 200
        assert b'aria-controls="collapseFilters"' in resp.data
        assert b'aria-expanded="true"' in resp.data
        assert b'id="collapseFilters"' in resp.data
        assert b"card-body panel-collapse collapse show" in resp.data
        selected_option_snippets = [
            f'value="{selected_panel}" selected',
            f'selected value="{selected_panel}"',
            f'value="{selected_panel}" selected="selected"',
            f'selected="selected" value="{selected_panel}"',
        ]
        assert not any(bytes(snippet, "utf-8") in resp.data for snippet in selected_option_snippets)


def test_case_page_clinical_hpo_dark_link(app, case_obj, institute_obj):
    """Case page should render a direct HPO-filtered dark regions link when dark data exists."""

    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]},
        {
            "$set": {
                "dynamic_gene_list": [{"hgnc_symbol": "ACTA2", "hgnc_id": 130}],
                "paraphrase": {"rccx": {}},
            }
        },
    )

    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        resp = client.get(
            url_for(
                "cases.case",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )

        assert resp.status_code == 200
        assert b"Clinical HPO Dark" in resp.data
        assert b"gene_panels=hpo" in resp.data
        assert b"panel_filter_applied=1" in resp.data
