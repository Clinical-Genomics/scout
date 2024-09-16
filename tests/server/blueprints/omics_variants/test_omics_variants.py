from flask import url_for


def test_omics_variants(app, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the outliers page
        resp = client.get(
            url_for(
                "omics_variants.outliers",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200


def test_filter_export_omics_variants(app, institute_obj, case_obj):
    """Test the variant export functionality in -omics page"""

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the outliers page with a POST request and
        form_data = {
            "export": "test",
        }

        # WHEN downloading the variants
        resp = client.post(
            url_for(
                "omics_variants.outliers",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=form_data,
        )
        # THEN it should return a valid response
        assert resp.status_code == 200
        # containing a CSV file
        assert resp.mimetype == "text/csv"
