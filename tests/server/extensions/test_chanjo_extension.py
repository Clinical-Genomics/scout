from scout.server.app import create_app

SQLALCHEMY_DATABASE_URI = "sqlite://"
CHANJO_REPORT_ENDPOINTS = ["/reports/report", "/reports/genes"]


def test_chanjo_create_app():
    """Test initiating the chanjo extension when app config file contains the SQLALCHEMY_DATABASE_URI setting."""

    # GIVEN an app initialized with SQLALCHEMY_DATABASE_URI setting in config file
    test_app = create_app(
        config=dict(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI,
        )
    )

    # THEN it should contain the expected chanjo-report routes
    with test_app.test_client() as client:
        app_routes = [str(rule) for rule in test_app.url_map._rules]

        for endpointt in CHANJO_REPORT_ENDPOINTS:
            assert endpointt in app_routes
