"""Fixtures for login blueprints"""

import pytest

from scout.server.app import create_app

SERVER_NAME = "test.server"


@pytest.fixture
def user_adapter(adapter, user_obj, institute_obj):
    """Return a adatper with a user and institute"""
    adapter.add_institute(institute_obj)
    adapter.add_user(user_obj)
    return adapter


@pytest.fixture
def ldap_app(request):
    """app ficture for testing the LDAP login system."""
    config = {
        "TESTING": True,
        "DEBUG": True,
        "SERVER_NAME": SERVER_NAME,
        "LDAP_HOST": "ldap://test_ldap_server",
        "WTF_CSRF_ENABLED": False,
        "MONGO_DBNAME": "testdb",
    }
    app = create_app(config=config)
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture
def google_app(request):
    """app ficture for testing the Google login system."""
    config = {
        "TESTING": True,
        "DEBUG": True,
        "SERVER_NAME": SERVER_NAME,
        "GOOGLE": {
            "client_id": "test",
            "client_secret": "test",
            "discovery_url": "https://test.com",
        },
        "MONGO_DBNAME": "testdb",
    }
    app = create_app(config=config)
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture
def keycloak_app(request):
    """app ficture for testing the Keycloak login system."""
    config = {
        "TESTING": True,
        "DEBUG": True,
        "SERVER_NAME": SERVER_NAME,
        "KEYCLOAK": {
            "client_id": "test",
            "client_secret": "test",
            "discovery_url": "https://test.com",
            "logout_url": "https://test.com/logout",
        },
        "MONGO_DBNAME": "testdb",
    }
    app = create_app(config=config)
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app
