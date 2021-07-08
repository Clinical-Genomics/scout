from flask import json, url_for


def test_api_institutes(app):
    """Test retrieving institutes data"""

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # sending a GET request to the institutes API should return content
        response = client.get("/api/v1/institutes")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data
