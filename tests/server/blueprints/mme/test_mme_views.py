from flask import url_for


def test_mme_submissions(app, institute_obj):
    """Test the page displaying cases with MME submissions for an institute."""

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # THEN MME submissions endpoint should return a valid page
        resp = client.get(
            url_for(
                "mme.mme_submissions",
                institute_id=institute_obj["internal_id"],
            ),
        )

        assert resp.status_code == 200
