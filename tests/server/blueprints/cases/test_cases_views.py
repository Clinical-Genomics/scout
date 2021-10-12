# -*- coding: utf-8 -*-
import datetime

import requests
from bson.objectid import ObjectId
from flask import current_app, json, url_for
from flask_login import current_user

from scout.demo import delivery_report_path
from scout.server.blueprints.cases import controllers
from scout.server.blueprints.cases.views import parse_raw_gene_ids, parse_raw_gene_symbols
from scout.server.extensions import mail, store

TEST_TOKEN = "test_token"


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


def test_rerun(app, institute_obj, case_obj, monkeypatch, mocker, mock_redirect):
    """test case rerun function"""

    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    # GIVEN an initialized app
    # GIVEN a valid user

    def send_email(*args, **kwargs):
        return True

    monkeypatch.setattr(mail, "send", send_email)

    # GIVEN a test case without rerun pending
    test_case = store.case_collection.find_one()
    assert test_case.get("rerun_requested") is False

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN rerun request is sent
        resp = client.post(
            url_for(
                "cases.rerun",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
        )
        assert resp.status_code == 302
        updated_case = store.case_collection.find_one()

        # THEN the case should be updated
        assert updated_case["rerun_requested"] is True
        rerun_event = store.event_collection.find_one()

        # AND a rerun event should be created
        assert rerun_event.get("verb") == "rerun"


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
    """ "Test that custom images are beign displayed"""
    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

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
        for section_name in case_obj["custom_images"]:
            assert bytes(f"{section_name}-accordion", "utf-8") in dta


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


def test_case_diagnosis(app, institute_obj, case_obj, mocker, mock_redirect):
    # Test the web page containing the general case report

    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        req_data = {"omim_term": "OMIM:615349"}

        # When updating an OMIM diagnosis for a case
        resp = client.post(
            url_for(
                "cases.case_diagnosis",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=req_data,
        )
        # Response should be redirected to case page
        assert resp.status_code == 302


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


def test_gene_fusion_report(app, institute_obj, case_obj):
    """Test the endpoint that allows users to download the PDF file containing the gene fusion report."""
    # GIVEN an initialized app and a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # When clicking on gene fusion report link button on the sidebar
        resp = client.get(
            url_for(
                "cases.gene_fusion_report",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                report_type="gene_fusion_report",
            )
        )
        # a successful response should be returned
        assert resp.status_code == 200
        # And the downloaded file should be a PDF file
        assert resp.mimetype == "application/pdf"


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


def _test_delivery_report(client, institute_obj, case_obj, response_format):
    """Test helper: test report of given format"""

    # WHEN the case has a delivery report
    store.case_collection.update_one(
        {"_id": case_obj["_id"]},
        {"$set": {"delivery_report": delivery_report_path}},
    )

    # WHEN accessing the delivery report page with the format=pdf param
    resp = client.get(
        url_for(
            "cases.delivery_report",
            institute_id=institute_obj["internal_id"],
            case_name=case_obj["display_name"],
            format=response_format,
        )
    )
    return resp


def test_html_delivery_report(app, institute_obj, case_obj, user_obj):

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        resp = _test_delivery_report(client, institute_obj, case_obj, response_format="html")
        # THEN the endpoint should return the delivery report HTML page
        assert "Leveransrapport Clinical Genomics" in str(resp.data)


def test_pdf_delivery_report(app, institute_obj, case_obj, user_obj):

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        resp = _test_delivery_report(client, institute_obj, case_obj, response_format="pdf")
        # a successful response should be returned
        assert resp.status_code == 200
        # and it should contain a pdf file, not HTML code
        assert resp.mimetype == "application/pdf"


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


def test_omimterms(app, test_omim_term):
    """Test The API which returns all OMIM terms when queried from case page"""

    # GIVEN a database containing at least one OMIM term
    store.disease_term_collection.insert_one(test_omim_term)

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN the API is invoked with a query string containing part of the OMIM term description
        resp = client.get(url_for("cases.omimterms", query="5-oxo"))
        # THEN it should return a valid response
        assert resp.status_code == 200

        # containing the OMIM term
        assert test_omim_term["_id"] in str(resp.data)
        assert resp.mimetype == "application/json"


def _test_beacon_submit(client, institute_obj, case_obj, vcf_files, mocker, mock_redirect):
    """Test beacon connection: given client, produce response"""

    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    form_data = {
        "case": case_obj["_id"],
        "samples": "affected",
        "vcf_files": vcf_files,
    }
    # WHEN case page is loaded
    resp = client.post(url_for("cases.beacon_submit"), data=form_data)
    return resp


def test_beacon_submit_wrong_config(app, institute_obj, case_obj, mocker, mock_redirect):
    """Test saving variants to a Beacon server when Beacon connection parameters are not set"""

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        vcf_files = ["vcf_snv_research", "vcf_snv"]
        # WHEN case page is loaded without beacon config settings
        resp = _test_beacon_submit(
            client, institute_obj, case_obj, vcf_files, mocker, mock_redirect
        )

        # THEN it should redirect to case page
        assert resp.status_code == 302
        updated_case = store.case_collection.find_one()
        # but submission should not be saved in case object
        assert "beacon" not in updated_case


def test_beacon_submit(
    app, institute_obj, case_obj, monkeypatch, mocked_beacon, mocker, mock_redirect
):
    """Test submitting variants to a Beacon server"""

    # GIVEN a mocked Beacon server
    def mock_response(*args, **kwargs):
        return mocked_beacon

    monkeypatch.setattr(requests, "post", mock_response)

    # GIVEN an initialized app containing the right config settings
    current_app.config["BEACON_URL"] = mocked_beacon.url
    current_app.config["BEACON_TOKEN"] = mocked_beacon.token

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        vcf_files = ["vcf_snv_research", "vcf_snv"]
        # WHEN case page is loaded
        resp = _test_beacon_submit(
            client,
            institute_obj,
            case_obj,
            vcf_files,
            mocker,
            mock_redirect,
        )

        # THEN it should redirect to case page
        assert resp.status_code == 302
        updated_case = store.case_collection.find_one()
        # and submissions details should be saved in case object
        assert "beacon" in updated_case
        assert updated_case["beacon"]["samples"]
        assert updated_case["beacon"]["vcf_files"] == vcf_files


def test_beacon_remove(
    app, institute_obj, case_obj, monkeypatch, mocked_beacon, mocker, mock_redirect
):
    """Test removing variants submitted to Beacon for test case"""

    mocker.patch("scout.server.blueprints.cases.views.redirect", return_value=mock_redirect)

    # GIVEN a mocked Beacon server
    def mock_response(*args, **kwargs):
        return mocked_beacon

    monkeypatch.setattr(requests, "delete", mock_response)

    # GIVEN a case with variants saved to Beacon
    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"beacon": {"samples": ["ADM1059A2"]}}}
    )
    case_obj = store.case_collection.find_one()
    assert case_obj["beacon"]

    # GIVEN an initialized app containing the right config settings
    current_app.config["BEACON_URL"] = mocked_beacon.url
    current_app.config["BEACON_TOKEN"] = mocked_beacon.token

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN users submits a GET request to remove data from Beacon
        resp = client.get(
            url_for(
                "cases.beacon_remove",
                case_id=case_obj["_id"],
            )
        )
        # THEN it should redirect to case page
        assert resp.status_code == 302

        # And case should no more have an associated Beacon submission
        updated_case = store.case_collection.find_one()
        assert "beacon" not in updated_case
