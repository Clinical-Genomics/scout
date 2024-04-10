# -*- coding: utf-8 -*-
import datetime

from bson.objectid import ObjectId
from flask import json, url_for

from scout.constants import CUSTOM_CASE_REPORTS
from scout.server.blueprints.cases.views import parse_raw_gene_ids, parse_raw_gene_symbols
from scout.server.extensions import store

TEST_TOKEN = "test_token"


def test_custom_report(app, institute_obj, case_obj, tmp_path):
    """Test the function that serves custom report data with all types of report in CUSTOM_CASE_REPORTS"""

    def _create_temp_file(report_name, format):
        tmp_name = ".".join(
            [report_name, format.lower()]
        )  # examples : multiqc_rna.html, pipeline_version.yaml
        tmp_file = tmp_path / tmp_name
        tmp_file.touch()
        tmp_file.write_text("content")
        return tmp_file

    # GIVEN a user logged in an initilalized app
    with app.test_client() as client:
        client.get(url_for("auto_login"))
        for _, report_specs in CUSTOM_CASE_REPORTS.items():
            report_type = report_specs["key_name"]
            report_format = report_specs["format"]
            pdf_export = report_specs["pdf_export"]

            # GIVEN a case that contains a report of a certain type=report_type
            tf = _create_temp_file(report_type, report_format)
            if not case_obj.get(report_type):
                store.case_collection.update_one(
                    {"_id": case_obj["_id"]}, {"$set": {report_type: str(tf)}}
                )
            # WHEN displaying the report in an HTML page
            if report_format == "HTML":
                resp = client.get(
                    url_for(
                        "cases.custom_report",
                        institute_id=institute_obj["internal_id"],
                        case_name=case_obj["display_name"],
                        report_type=report_type,
                    )
                )
                # THEN a successful response should be returned
                assert resp.status_code == 200
                assert resp.mimetype == "text/html"

            # WHEN report has the option to be exported in PDF format
            if pdf_export:
                resp = client.get(
                    url_for(
                        "cases.custom_report",
                        institute_id=institute_obj["internal_id"],
                        case_name=case_obj["display_name"],
                        report_type=report_type,
                        report_format="pdf",
                    )
                )
                # THEN the export should work
                assert resp.status_code == 200
                assert resp.mimetype == "application/pdf"


def test_add_individual_phenotype(app, institute_obj):
    """Test adding a phenotype term (HPO) for a case"""

    # GIVEN a database with an HPO term
    phenotype_term = {
        "_id": "HP:666",
        "phenotype_id": "HP:666",
        "description": "A very bad phenotype",
    }
    store.hpo_term_collection.insert_one(phenotype_term)

    # GIVEN a case with no phenotypes
    case_obj = store.case_collection.find_one()
    assert case_obj.get("phenotype_terms") is None

    # GIVEN an individual of a case
    ind = case_obj["individuals"][0]
    ind_id = ind["individual_id"]
    ind_name = ind["display_name"]
    data = {
        "hpo_term": phenotype_term["phenotype_id"],
        "phenotype_inds": [f"{ind_id}|{ind_name}"],
    }

    # WHEN a phenotype term is added for the case individual via POST request
    with app.test_client() as client:
        client.get(url_for("auto_login"))

        resp = client.post(
            url_for(
                "cases.phenotypes",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=data,
        )

    # THEN the case phenotypes should be updated accordingly
    updated_case = store.case_collection.find_one({"_id": case_obj["_id"]})
    assert updated_case["phenotype_terms"] == [
        {
            "phenotype_id": phenotype_term["phenotype_id"],
            "feature": phenotype_term["description"],
            "individuals": [{"individual_id": ind_id, "individual_name": ind_name}],
        }
    ]

    # AND a relatove event with specific HPO term and affected individual should be created in database
    update_event = store.event_collection.find_one()
    assert update_event["hpo_term"] == phenotype_term["phenotype_id"]
    assert update_event["individuals"] == [ind_name]


def test_reanalysis(app, institute_obj, case_obj, mocker, mock_redirect):
    """Test the call to the case reanalysis API"""

    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    # WHEN the rerun is triggered using the reanalysis endpoint
    with app.test_client() as client:
        json_string = '[{"sample_id": "NA12882", "sex": 1, "phenotype": 2}]'
        data = {"sample_metadata": json_string}

        resp = client.post(
            url_for(
                "cases.reanalysis",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=data,
        )

        # It should return redirect to previous page
        assert resp.status_code == 302


def test_rerun_monitor(app, institute_obj, mocker, mock_redirect):
    """test case rerun monitoring function"""

    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    # GIVEN an initialized app
    # GIVEN a valid user
    # GIVEN a test case without rerun monitoring
    a_case = store.case_collection.find_one()
    assert not a_case.get("rerun_monitoring")
    # WHEN setting monitoring to true
    store.case_collection.find_one_and_update(
        {"_id": a_case["_id"]},
        {"$set": {"rerun_monitoring": False}},
    )

    form_data = {"rerun_monitoring": "monitor"}

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN rerun monitor is toggled
        resp = client.post(
            url_for(
                "cases.rerun_monitor",
                institute_id=institute_obj["internal_id"],
                case_name=a_case["display_name"],
            ),
            data=form_data,
        )
        assert resp.status_code == 302
        updated_case = store.case_collection.find_one({"_id": a_case["_id"]})
        # THEN the case should be updated
        assert updated_case["rerun_monitoring"] is True

        # AND an unmonitor event should be created
        rerun_event = store.event_collection.find_one()
        assert rerun_event.get("verb") == "rerun_monitor"


def test_research(app, institute_obj, case_obj, mocker, mock_redirect):
    """Test the endpoint to request research variants for a case"""

    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    # GIVEN a test case without request research pending
    test_case = store.case_collection.find_one()
    assert test_case.get("research_requested") is False

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # WHEN rerun request is sent
        client.post(
            url_for(
                "cases.research",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
        )

        # THEN the updated case should have research_requested set to True
        assert store.case_collection.find_one({"research_requested": True})
        # AND a relative event should have been created in the evens collection
        assert store.event_collection.find_one({"verb": "open_research"})


def test_reset_research(app, institute_obj, case_obj, mocker, mock_redirect):
    """Test the endpoint to cancel the upload of research variants for a case"""

    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # WHEN research variants request is sent
        client.post(
            url_for(
                "cases.research",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
        )
        # GIVEN a test case with request research pending
        assert store.case_collection.find_one({"research_requested": True})

        # WHEN the request for research variants is canceled
        client.get(
            url_for(
                "cases.reset_research",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
        )
        # THEN the updated case should have research_requested set to False
        assert store.case_collection.find_one({"research_requested": False})
        # AND a relative event should have been created in the evens collection
        assert store.event_collection.find_one({"verb": "reset_research"})


def test_parse_raw_gene_symbols(app):
    """Test parse gene symbols"""

    # GIVEN a list of autocompleted gene symbols
    gene_symbols = ["MUTYH |POT1", "POT1 0.1|APC|PMS2"]

    # WHEN converting to hgnc_ids
    hgnc_symbols = parse_raw_gene_symbols(gene_symbols)

    # THEN the appropriate set of hgnc_symbols should be returned
    assert hgnc_symbols == {"APC", "MUTYH", "PMS2", "POT1"}


def test_parse_raw_gene_ids(app):
    """Test parse gene symbols"""

    # GIVEN a list of autocompleted gene symbols
    gene_symbols = ["1234 | SYM (OLDSYM, SYM)", "4321 | MYS (OLDMYS, MYS)"]

    # WHEN converting to hgnc_ids
    hgnc_ids = parse_raw_gene_ids(gene_symbols)

    # THEN the appropriate set of hgnc_ids should be returned
    assert hgnc_ids == {1234, 4321}


def test_update_cancer_case_sample(
    app, user_obj, institute_obj, cancer_case_obj, mocker, mock_redirect
):
    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    # GIVEN an initialized app
    # GIVEN a valid user and institute

    # And a cancer case with cancer samples data
    old_tumor_purity = cancer_case_obj["individuals"][0]["tumor_purity"]
    old_tumor_type = cancer_case_obj["individuals"][0]["tumor_type"]
    old_tissue_type = "unknown"
    assert old_tumor_purity
    assert old_tumor_type

    cancer_case_obj["individuals"][0]["tissue_type"] = old_tissue_type
    cancer_case_obj["updated_at"] = datetime.datetime.now()
    store.case_collection.insert_one(cancer_case_obj)

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN posting a request with info for updating one of the case samples:
        ind_id = cancer_case_obj["individuals"][0]["individual_id"]

        form_data = {
            "update_ind": ind_id,
            ".".join(["tumor_type.", ind_id]): "Desmoid Tumor",
            ".".join(["tissue_type", ind_id]): "cell line",
            ".".join(["tumor_purity", ind_id]): "0.4",
        }

        resp = client.post(
            url_for(
                "cases.update_cancer_sample",
                institute_id=institute_obj["internal_id"],
                case_name=cancer_case_obj["display_name"],
            ),
            data=form_data,
        )

        # THEN the returned HTML page should redirect
        assert resp.status_code == 302

        # AND sample in case obj should have been updated
        updated_case = store.case_collection.find_one({"_id": cancer_case_obj["_id"]})
        updated_sample = updated_case["individuals"][0]

        assert updated_sample["tumor_purity"] != old_tumor_purity
        assert updated_sample["tumor_type"] != old_tumor_type
        assert updated_sample["tissue_type"] != old_tissue_type


def test_institutes(app):
    # GIVEN an initialized app
    # GIVEN a valid user

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the institutes page
        resp = client.get(url_for("cases.index"))

        # THEN it should return a page
        assert resp.status_code == 200


def test_case_custom_images(app, institute_obj, case_obj):
    """Test that custom images are being displayed"""
    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN case page is loaded
        resp = client.get(
            url_for(
                "cases.case",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # THEN it should display the two custom images section
        dta = resp.get_data()
        for section_name in case_obj["custom_images"]["case_images"]:
            assert bytes(f"{section_name}-accordion", "utf-8") in dta


def test_case_by_id(app, case_obj):
    """Test that cases can be retrieved using case_id only"""
    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN case page is loaded
        resp = client.get(
            url_for(
                "cases.case",
                case_id=case_obj["_id"],
            )
        )

        # THEN it should return a valid page
        assert resp.status_code == 200


def test_case_outdated_panel(app, institute_obj, case_obj):
    """Test case displaying an outdated panel warning badge"""

    # GIVEN an adapter with a case with a gene panel of version 1
    case_panel = case_obj["panels"][0]
    assert case_panel["version"] == 1

    # AND an updated version of the same panel in the database
    updated_panel = {
        "panel_name": case_panel["panel_name"],
        "display_name": case_panel["display_name"],
        "version": 2,
        "genes": [{"symbol": "POT1", "hgnc_id": 17284}],
    }
    store.panel_collection.insert_one(updated_panel)

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN case page is loaded
        resp = client.get(
            url_for(
                "cases.case",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # THEN it should return a valid page
        assert resp.status_code == 200

        # WITH a tooltip explaining that the gene panel is outdated
        assert "Panel version used in the analysis (1.0) is outdated." in str(resp.data)


def test_case_sma(app, case_obj, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user, case and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the case SMN CN page
        resp = client.get(
            url_for(
                "cases.sma",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )

        # THEN it should return a page
        assert resp.status_code == 200


def test_case_fusion(app, fusion_case_obj, institute_obj):
    """Test the RNA fusion case page."""

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN a valid user, case and institute
        client.get(url_for("auto_login"))

        # GIVEN a database containing a fusion case object
        assert store.case_collection.insert_one(fusion_case_obj)

        # WHEN accessing the RNA fusion case
        resp = client.get(
            url_for(
                "cases.case",
                institute_id=institute_obj["internal_id"],
                case_name=fusion_case_obj["display_name"],
            )
        )

        # THEN it should return a page
        assert resp.status_code == 200


def test_update_individual(app, user_obj, institute_obj, case_obj, mocker, mock_redirect):
    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    # And a case individual with no age (tissue type is default blood):
    case_obj = store.case_collection.find_one()
    assert case_obj["individuals"][0].get("age") is None
    assert case_obj["individuals"][0]["tissue_type"] == "blood"

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN posting a request with info for updating one of the case samples:
        ind_id = case_obj["individuals"][0]["individual_id"]
        form_data = {
            "update_ind": ind_id,
            "_".join(["age", ind_id]): "2.5",
            "_".join(["tissue", ind_id]): "muscle",
        }

        resp = client.post(
            url_for(
                "cases.update_individual",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=form_data,
        )

        # THEN the returned HTML page should redirect
        assert resp.status_code == 302

        # Then case obj should have been updated:
        updated_case = store.case_collection.find_one({"_id": case_obj["_id"]})
        updated_ind = updated_case["individuals"][0]
        assert updated_ind["individual_id"] == ind_id
        assert updated_ind["age"] == 2.5
        assert updated_ind["tissue_type"] == "muscle"

        # And an associated event should have been created in the database
        assert store.event_collection.find_one(
            {"case": updated_case["_id"], "verb": "update_individual"}
        )


def test_case_synopsis(app, institute_obj, case_obj, mocker, mock_redirect):
    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        req_data = {"synopsis": "test synopsis"}

        # WHEN updating the synopsis of a case
        resp = client.post(
            url_for(
                "cases.case_synopsis",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                data=req_data,
            ),
        )
        # then it should return a redirected page
        assert resp.status_code == 302


def test_update_case_comment(app, institute_obj, case_obj, user_obj, mocker, mock_redirect):
    """Test the functionality that allows updating of case-specific comments"""

    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        ## GIVEN a case with a comment
        store.create_event(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link="a link",
            category="case",
            verb="comment",
            subject=case_obj["display_name"],
            level="specific",
        )
        comment = store.event_collection.find_one({"verb": "comment"})
        assert comment

        # WHEN a user updates the comment via the modal form
        form_data = {
            "event_id": comment["_id"],
            "updatedContent": "an updated comment",
            "edit": "",
        }

        resp = client.post(
            url_for(
                "cases.events",
                institute_id=institute_obj["_id"],
                case_name=case_obj["display_name"],
                event_id=comment["_id"],
            ),
            data=form_data,
        )
        # THEN it should redirect to case page
        assert resp.status_code == 302

        # The comment should be updated
        updated_comment = store.event_collection.find_one({"_id": comment["_id"]})
        assert updated_comment["content"] == "an updated comment"

        # And a comment updated event should have been created in the event collection
        updated_var_event = store.event_collection.find_one({"verb": "comment_update"})
        # With the same subject of the comment
        assert updated_var_event["subject"] == updated_comment["subject"]


def test_add_case_group(app, case_obj, institute_obj):
    """Test adding a case group."""

    ### GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        referer = url_for(
            "cases.case",
            institute_id=institute_obj["internal_id"],
            case_name=case_obj["display_name"],
        )

        # WHEN we invoke the add group endpoint with GET
        resp = client.get(
            url_for(
                "cases.add_case_group",
                institute_id=institute_obj["_id"],
                case_name=case_obj["display_name"],
            ),
            headers={"referer": referer},
        )

        # THEN the response should be a redirect
        assert resp.status_code == 302


def test_remove_case_group(app, case_obj, institute_obj):
    """Test removing a case group."""

    ### GIVEN an initialized app
    group_id = ObjectId("101010101010101010101010")
    result = store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"group": [group_id]}}
    )

    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        referer = url_for(
            "cases.case",
            institute_id=institute_obj["internal_id"],
            case_name=case_obj["display_name"],
        )

        # WHEN we invoke the add group endpoint with GET
        resp = client.get(
            url_for(
                "cases.remove_case_group",
                institute_id=institute_obj["_id"],
                case_name=case_obj["display_name"],
                case_group=group_id,
            ),
            headers={"referer": referer},
        )

        # THEN the response should be a redirect
        assert resp.status_code == 302


def test_download_hpo_genes(app, case_obj, institute_obj):
    """Test the endpoint that downloads the dynamic gene list for a case"""

    # GIVEN a case containing a dynamic gene list
    dynamic_gene_list = [
        {
            "hgnc_symbol": "ACTA2",
            "hgnc_id": 130,
            "description": "actin alpha 2, smooth muscle",
        },
        {"hgnc_symbol": "LMNB2", "hgnc_id": 6638, "description": "lamin B2"},
    ]

    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"dynamic_gene_list": dynamic_gene_list}}
    )

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # WHEN the endpoint for downloading the case dynamic gene list is invoked
        resp = client.get(
            url_for(
                "cases.download_hpo_genes",
                institute_id=institute_obj["_id"],
                case_name=case_obj["display_name"],
                category="research",
            )
        )
        # THEN the response should be successful
        assert resp.status_code == 200
        # And should download a PDF file
        assert resp.mimetype == "application/pdf"


def test_api_case_report(app, institute_obj, case_obj):
    """Test the API returning report case data in json format"""

    # GIVEN a case with a causative variant
    test_variant = store.variant_collection.find_one()
    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"causatives": [test_variant["_id"]]}}
    )

    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))
        # THE api_case_report should return valid json data
        resp = client.get(
            url_for(
                "cases.api_case_report",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        assert resp.status_code == 200
        json_data = json.loads(resp.data)
        data = json_data["data"]
        # case info should be present in the data
        assert data["case"]
        # institute info should be present in the data
        assert data["institute"]
        variant_types = {
            "causatives_detailed": "causatives",
            "suspects_detailed": "suspects",
            "classified_detailed": "acmg_classification",
            "tagged_detailed": "manual_rank",
            "tier_detailed": "cancer_tier",
            "dismissed_detailed": "dismiss_variant",
            "commented_detailed": "is_commented",
        }
        for var_type in variant_types:
            assert var_type in data["variants"]
            # causative variant info should be present in the data
            if var_type == "causatives_detailed":
                assert data["variants"][var_type][0]["_id"] == test_variant["_id"]


def test_case_report(app, institute_obj, case_obj):
    # Test the web page containing the general case report

    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # When clicking on 'general' button on case page
        resp = client.get(
            url_for(
                "cases.case_report",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # a successful response should be returned
        assert resp.status_code == 200


def test_case_diagnosis(
    app, institute_obj, case_obj, test_omim_database_term, mocker, mock_redirect
):
    """Test the cases.case_diagnosis by adding and removing a diagnosis."""

    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    # GIVEN a case with no diagnosis:
    assert case_obj.get("diagnosis_phenotypes") is None
    # And no events in the database
    assert not store.event_collection.find_one()

    # GIVEN a disease term present in the database
    store.disease_term_collection.insert_one(test_omim_database_term)
    disease_id = test_omim_database_term["_id"]

    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        req_data = {"disease_term": disease_id}

        # WHEN updating a diagnosis for a case
        resp = client.post(
            url_for(
                "cases.case_diagnosis",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=req_data,
        )
        # THEN response should be redirected to case page
        assert resp.status_code == 302
        # And case should have a diagnosis:
        case_obj = store.case_collection.find_one({"_id": case_obj["_id"]})
        assert case_obj.get("diagnosis_phenotypes")
        # And a new event should have been saved into the database
        assert store.event_collection.find_one()

        # WHEN using the same endpoint to remove the diagnosis
        req_data = {"disease_term": disease_id}
        resp = client.post(
            url_for(
                "cases.case_diagnosis",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                remove="yes",
            ),
            data=req_data,
        )
        # THEN response should be redirected to case page
        assert resp.status_code == 302
        # And case should have no diagnoses
        case_obj = store.case_collection.find_one({"_id": case_obj["_id"]})
        assert not case_obj.get("diagnosis_phenotypes")
        # And a new event should have been saved into the database
        assert sum(1 for _ in store.event_collection.find()) == 2


def test_pdf_case_report(app, institute_obj, case_obj):
    # Test the web page containing the general case report

    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # When clicking on 'Download PDF' button on general report page
        resp = client.get(
            url_for(
                "cases.pdf_case_report",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # a successful response should be returned
        assert resp.status_code == 200


def test_mt_report(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # When clicking on 'mtDNA report' on case page
        resp = client.get(
            url_for(
                "cases.mt_report",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # a successful response should be returned
        assert resp.status_code == 200
        # and it should contain a zipped file, not HTML code
        assert resp.mimetype == "application/zip"


def test_status(app, institute_obj, case_obj, user_obj, mocker, mock_redirect):
    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # make sure test case status is inactive
        assert case_obj["status"] == "inactive"

        # use status view to update status for test case
        request_data = {"status": "prioritized"}
        resp = client.post(
            url_for(
                "cases.status",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                params=request_data,
            )
        )

        assert resp.status_code == 302  # page should be redirected


def test_caselist(app, case_obj):
    """Test the API return of cases for autocompletion"""

    # GIVEN a case
    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN the API is invoked with a query string containing part of the case term description
        resp = client.get(
            url_for(
                "cases.caselist",
                institute_id=case_obj["owner"],
                query=case_obj["display_name"],
            )
        )
        # THEN it should return a valid response
        assert resp.status_code == 200

        # containing the case display name
        assert case_obj["display_name"] in str(resp.data)


def test_diseaseterms(app, test_omim_database_term):
    """Test The API which returns all disease terms when queried from case page"""

    # GIVEN a database containing at least one OMIM term
    store.disease_term_collection.insert_one(test_omim_database_term)

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN the API is invoked with a query string containing part of the disease term description
        resp = client.get(url_for("cases.diseaseterms", query="5-oxo"))
        # THEN it should return a valid response
        assert resp.status_code == 200

        # containing the disease term
        assert test_omim_database_term["_id"] in str(resp.data)
        assert resp.mimetype == "application/json"


def test_beacon_add_variants(app, institute_obj, case_obj, mocker, mock_redirect):
    """Test Beacon add variants endpoint"""

    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    # GIVEN an app with an authenticated user
    with app.test_client() as client:
        client.get(url_for("auto_login"))

        # THE beacon_add_variants endpoint should work and return page redirect
        data = {}
        resp = client.post(
            url_for(
                "cases.beacon_add_variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=data,
        )
        assert resp.status_code == 302


def test_beacon_remove_variants(app, institute_obj, case_obj, mocker, mock_redirect):
    """Test Beacon remove variants endpoint"""

    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    # GIVEN an app with an authenticated user
    with app.test_client() as client:
        client.get(url_for("auto_login"))

        # THE beacon_add_variants endpoint should work and return page redirect
        data = {}
        resp = client.get(
            url_for(
                "cases.beacon_remove_variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=data,
        )
        assert resp.status_code == 302


def test_host_custom_image_aux(app, institute_obj, case_obj):
    """Test the endpoint that returns a custom image given its path."""

    # GIVEN an app with an authenticated user
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # GIVEN a case with custom images
        custom_image: dict = case_obj["custom_images"]["case_images"]["section_one"][0]
        assert custom_image

        # WHEN retrieving ae custom image using the host_custom_image_aux endpoint
        resp = client.get(
            url_for(
                "cases.host_custom_image_aux",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                image_path=custom_image["path"],
            )
        )

        # THEN it should return an image
        assert resp.status_code == 200
        assert resp.mimetype == "image/png"
