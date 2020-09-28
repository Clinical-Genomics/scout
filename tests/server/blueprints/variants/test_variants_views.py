# -*- coding: utf-8 -*-
import pymongo
from flask import url_for, current_app
from flask_login import current_user
from urllib.parse import urlencode
from scout.server.extensions import store


def test_variants_clinical_filter(app, institute_obj, case_obj):

    # GIVEN a variant without clinVar annotations
    test_var = store.variant_collection.find_one(
        {
            "clnsig": {"$exists": False},
            "variant_type": "clinical",
            "category": "snv",
            "panels": {"$in": ["panel1"]},
        }
    )
    assert test_var

    # IF the variant receives a fake clinsig annotation compatible with the clinical filter
    clinsig_criteria = {
        "value": 5,
        "accession": 345986,
        "revstat": "criteria_provided,multiple_submitters,no_conflicts",
    }

    updated_var = store.variant_collection.find_one_and_update(
        {"_id": test_var["_id"]},
        {"$set": {"clnsig": [clinsig_criteria], "panels": ["panel1"]}},
        return_document=pymongo.ReturnDocument.AFTER,
    )

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN submitting form data to the variants page (POST method) with clinical filter
        data = urlencode(
            {
                "clinical_filter": "Clinical filter",
                "variant_type": "clinical",
                "gene_panels": "panel1",
            }
        )  # clinical filter

        resp = client.post(
            url_for(
                "variants.variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=data,
            content_type="application/x-www-form-urlencoded",
        )

        # THEN it should return a page
        assert resp.status_code == 200

        # containing the variant above
        assert updated_var["_id"] in str(resp.data)


def test_variants(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the variants page
        resp = client.get(
            url_for(
                "variants.variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200


def test_bulk_dismiss_variants(app, institute_obj, case_obj):
    """Sending a POST request to variants view to test variant dismiss funtionality"""
    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # GIVEN a test variant to be dismissed
        snv_variant = store.variant_collection.find_one({"category": "snv"})

        # When a POST request with filter containing wrongly formatted parameters is sent
        dismiss_choices = ["2", "5"]
        form_data = {
            "dismiss": snv_variant["_id"],
            "dismiss_choices": dismiss_choices,
        }

        resp = client.post(
            url_for(
                "variants.variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=form_data,
        )
        # THEN it should return a redirected page
        assert resp.status_code == 200

        # and the variant should be updated with the dismissed options
        updated_variant = store.variant_collection.find_one({"_id": snv_variant["_id"]})
        for option in dismiss_choices:
            assert option in updated_variant["dismiss_variant"]


def test_variants_research(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the variants page
        resp = client.get(
            url_for(
                "variants.variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                variant_type="research",
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200
        # THEN a reset filters link with variant type should have been made
        assert "variant_type=research" in str(resp.data)


def test_sv_variants(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the sv-variants page
        resp = client.get(
            url_for(
                "variants.sv_variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200


def test_sv_variants_research(app, institute_obj, case_obj):
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the sv-variants page
        resp = client.get(
            url_for(
                "variants.sv_variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                variant_type="research",
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200
        # THEN a reset filters link with variant type should have been made
        assert "variant_type=research" in str(resp.data)


def test_sv_variants_post_data(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN requesting a clinical filter from the page (POST method)
        data = urlencode({"clinical_filter": True})  # clinical filter

        # WHEN posting an update description request to panel page
        resp = client.post(
            url_for(
                "variants.sv_variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=data,
            content_type="application/x-www-form-urlencoded",
        )

        # THEN it should return a page
        assert resp.status_code == 200


def test_str_variants(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the str-variants page
        resp = client.get(
            url_for(
                "variants.str_variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200


def test_cancer_variants(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

    # WHEN accessing the sv-variants page
    resp = client.get(
        url_for(
            "variants.cancer_variants",
            institute_id=institute_obj["internal_id"],
            case_name=case_obj["display_name"],
        )
    )
    # THEN it should return a page
    assert resp.status_code == 200


def test_filter_cancer_variants_wrong_params(app, institute_obj, case_obj):
    """test filter cancer SNV variants with filter form filled with parameters having the wrong format"""

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # When a POST request with filter containing wrongly formatted parameters is sent
        form_data = {
            "control_frequency": "not a number!",
        }
        resp = client.post(
            url_for(
                "variants.cancer_variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=form_data,
        )
        # THEN it should return a redirected page
        assert resp.status_code == 302


def test_filter_cancer_variants_by_vaf(app, institute_obj, cancer_case_obj, variant_obj):
    """Tests the cancer form filter by VAF"""

    # GIVEN a database containing a cancer case
    cancer_case_obj["status"] = "inactive"
    assert store.case_collection.insert_one(cancer_case_obj)

    variant_obj["tumor"] = {"alt_freq": 0.49}
    # GIVEN a variant belonging to the case that has tumor alternate frequency
    assert store.variant_collection.find_one_and_update(
        {"_id": variant_obj["_id"]},
        {
            "$set": {
                "case_id": cancer_case_obj["_id"],
                "category": "cancer",
                "tumor": {"alt_freq": 0.49},
            }
        },
    )

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # When the cancer SNV variants page is loaded by GET request (no filter)
        resp = client.get(
            url_for(
                "variants.cancer_variants",
                institute_id=institute_obj["internal_id"],
                case_name=cancer_case_obj["display_name"],
            )
        )

        # THEN it should return a page
        assert resp.status_code == 200
        # With the above variant
        assert variant_obj["_id"] in str(resp.data)

        # When a POST request filter with VAF > than the VAF in test_var is sent to the page
        form_data = {
            "tumor_frequency": 0.5,
        }
        resp = client.post(
            url_for(
                "variants.cancer_variants",
                institute_id=institute_obj["internal_id"],
                case_name=cancer_case_obj["display_name"],
            ),
            data=form_data,
        )
        # THEN it should return a page
        assert resp.status_code == 200
        # Without the variant
        assert variant_obj["_id"] not in str(resp.data)


def test_sv_cancer_variants(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

    # WHEN accessing the sv-variants page
    resp = client.get(
        url_for(
            "variants.cancer_sv_variants",
            institute_id=institute_obj["internal_id"],
            case_name=case_obj["display_name"],
        )
    )
    # THEN it should return a page
    assert resp.status_code == 200


def test_filter_export_cancer_variants(app, institute_obj, case_obj):
    """Test the variant export functionaliy in  cancer_variants page"""

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        form_data = {
            "export": "test",
        }

        # WHEN clicking on "Filter and export" button
        resp = client.post(
            url_for(
                "variants.cancer_variants",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=form_data,
        )
        # THEN it should return a valid response
        assert resp.status_code == 200
        # containing a text file
        assert resp.mimetype == "text/csv"
