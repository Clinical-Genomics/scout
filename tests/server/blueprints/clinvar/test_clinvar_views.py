from flask import url_for

from scout.server.extensions import store

SAVE_ENDPOINT = "clinvar.clinvar_save"
UPDATE_ENDPOINT = "clinvar.clinvar_update_submission"


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


def test_clinvar_submissions(app, institute_obj, case_obj, clinvar_form):
    """Test the page that shows all ClinVar submissions for an institute"""

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # GIVEN that institute has one ClinVar submission
        client.post(
            url_for(
                SAVE_ENDPOINT,
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

        # GIVEN that institute has one ClinVar submission
        client.post(
            url_for(
                SAVE_ENDPOINT,
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


def test_delete_clinvar_object(app, institute_obj, case_obj, clinvar_form):
    """Testing the endpoint used to remove one ClinVar submission object (CaseData or Variant)"""

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # GIVEN that institute has one ClinVar submission
        client.post(
            url_for(
                SAVE_ENDPOINT,
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=clinvar_form,
        )

        subm_obj = store.clinvar_submission_collection.find_one()
        # GIVEN a CaseData document that should be removed from the submission
        casedata_obj = store.clinvar_collection.find_one({"csv_type": "casedata"})

        data = {"delete_object": casedata_obj["_id"]}
        # WHEN form is submitted
        client.post(
            url_for(
                "clinvar.clinvar_delete_object",
                submission=subm_obj["_id"],
                object_type="casedata",
            ),
            data=data,
        )

        # THEN the document should be removed from database, clinvar collection
        assert store.clinvar_submission_collection.find_one({"csv_type": "casedata"}) is None


def test_clinvar_update_submission(app, institute_obj, case_obj, clinvar_form):
    """Test the endpoint resposible for updating a ClinVar submission"""

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # GIVEN that institute has one ClinVar submission
        client.post(
            url_for(
                SAVE_ENDPOINT,
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=clinvar_form,
        )
        subm_obj = store.clinvar_submission_collection.find_one()
        ######### Test setting an official submission ID
        # GIVEN an ID provided by ClinVar
        data = dict(update_submission="register_id", clinvar_id="SUB000")
        # Invoking the endpoint with the right input data
        client.post(
            url_for(
                UPDATE_ENDPOINT,
                institute_id=institute_obj["internal_id"],
                submission=subm_obj["_id"],
            ),
            data=data,
        )
        subm_obj = store.clinvar_submission_collection.find_one()
        # Should result in the ID saved in the database
        assert subm_obj.get("clinvar_subm_id") == "SUB000"

        ######### Test changing the submission status
        # GIVEN that the submission has state "open"
        subm_obj = store.clinvar_submission_collection.find_one()
        assert subm_obj["status"] == "open"

        # WHEN providing update_status = "closed"
        data = dict(update_submission="closed")
        client.post(
            url_for(
                UPDATE_ENDPOINT,
                institute_id=institute_obj["internal_id"],
                submission=subm_obj["_id"],
            ),
            data=data,
        )
        # THEN the submission status should change to closed
        subm_obj = store.clinvar_submission_collection.find_one()
        assert subm_obj["status"] == "closed"

        ######### Test deleting the submission
        # WHEN a submission is closed using the form
        data = dict(update_submission="delete")
        client.post(
            url_for(
                UPDATE_ENDPOINT,
                institute_id=institute_obj["internal_id"],
                submission=subm_obj["_id"],
            ),
            data=data,
        )
        # THEN the submission should be removed from the databasex
        assert store.clinvar_submission_collection.find_one() is None


def test_clinvar_download_csv(app, institute_obj, case_obj, clinvar_form):
    """Test downloading the Variant and CaseData .CSV files from the ClinVar submissions page"""

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # GIVEN that institute has one ClinVar submission
        client.post(
            url_for(
                SAVE_ENDPOINT,
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=clinvar_form,
        )
        subm_obj = store.clinvar_submission_collection.find_one()

        # It should be possible to download the Variant .CSV file
        resp = client.get(
            url_for(
                "clinvar.clinvar_download_csv",
                submission=subm_obj["_id"],
                csv_type="variant_data",
                clinvar_id="SUB000",
            )
        )
        assert resp.status_code == 200
        assert resp.mimetype == "text/csv"

        # AND a a CaseData .CSV file
        resp = client.get(
            url_for(
                "clinvar.clinvar_download_csv",
                submission=subm_obj["_id"],
                csv_type="case_data",
                clinvar_id="SUB000",
            )
        )
        assert resp.status_code == 200
        assert resp.mimetype == "text/csv"
