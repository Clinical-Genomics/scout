from flask import json, url_for


def test_api_institutes(app):
    """Test retrieving institutes data from the API"""

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # sending a GET request to the institutes API should return content
        response = client.get("/api/v1/institutes")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data


def test_api_cases(app, institute_obj):
    """Test retrieving institute cases data from the API"""

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # Invoking the API with some args params
        request_data = {
            "limit": "100",
            "skip_assigned": "on",
            "is_research": "on",
            "query": "case_id",
        }
        response = client.get(
            url_for(
                "overview.api_cases",
                institute_id=institute_obj["internal_id"],
                params=request_data,
            )
        )
        # WOULD return a data
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data
