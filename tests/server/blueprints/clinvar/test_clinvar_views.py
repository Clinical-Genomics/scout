from flask import url_for

from scout.server.extensions import store


def test_clinvar_add_variant(app, institute_obj, case_obj, variant_obj):
    """Test endpoint that displays the user form to add a new ClinVar variant"""

    # GIVEN a database with a variant
    assert store.variant_collection.find_one()

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # WHEN sending a post request to add a variant to ClinVar
        data = {"var_id": variant_obj["_id"]}
        resp = client.post(
            url_for(
                "clinvar.clinvar_add_variant",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=data,
        )
        # THEN the form page should work as expected
        assert resp.status_code == 200


def test_clinvar_save(app, institute_obj, case_obj, clinvar_form):
    """Test the second step of saving a new variant to a ClinVar submission object:
    saving to database the fields submitted in the clinvar_add_variant form by the user
    """
    # GIVEN a database with no ClinVar submissions
    assert store.clinvar_submission_collection.find_one() is None
    assert store.clinvar_collection.find_one() is None
    # GIVEN a form submitted by the user

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # WHEN data is submitted to the clinvar_save endpoint
        resp = client.post(
            url_for(
                "clinvar.clinvar_save",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=clinvar_form,
        )
        # THEN the form should be submitted and the page should redirect
        assert resp.status_code == 302

        # AND a general submission should be saved in the database
        assert store.clinvar_submission_collection.find_one()

        # AND 2 submission objects (Variant, Casedata) should be saved in
        subms = list(store.clinvar_collection.find())
        assert len(subms) == 2


def test_clinvar_submissions(app, institute_obj, case_obj, clinvar_form):
    """Test the page that shows all ClinVar submissions for an institute"""

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # GIVEN that institute has at least one ClinVar submission
        client.post(
            url_for(
                "clinvar.clinvar_save",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=clinvar_form,
        )

        # THEN clinvar_submissions endpoint should return a valid page
        resp = client.get(
            url_for(
                "clinvar.clinvar_submissions",
                institute_id=institute_obj["internal_id"],
            ),
        )

        assert resp.status_code == 200


def test_clinvar_rename_casedata(app, institute_obj, case_obj, clinvar_form):
    """Test form to rename case individuals linked to a given variant submission"""

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # GIVEN that institute has at least one ClinVar submission
        client.post(
            url_for(
                "clinvar.clinvar_save",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=clinvar_form,
        )

        # GIVEN a submission object
        subm_obj = store.clinvar_submission_collection.find_one()

        old_ind_name = clinvar_form.get("include_ind")

        form_data = dict(
            new_name="new_name",
        )

        # WHEN the form to rename a submission's individual is used
        referer = url_for("clinvar.clinvar_submissions", institute_id=institute_obj["internal_id"])
        client.post(
            url_for(
                f"clinvar.clinvar_rename_casedata",
                submission=subm_obj["_id"],
                case=case_obj["_id"],
                old_name=old_ind_name,
            ),
            data=form_data,
            headers={"referer": referer},
        )

        # THEN the individual in the submission should be renamed
        casedata_document = store.clinvar_collection.find_one({"csv_type": "casedata"})
        assert casedata_document["individual_id"] == "new_name"
