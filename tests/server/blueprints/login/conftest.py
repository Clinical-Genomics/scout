"""Fixtures for login blueprints"""

import pytest

from scout.server.app import create_app


@pytest.fixture
def user_adapter(adapter, user_obj, institute_obj):
    """Return a adatper with a user and institute"""
    adapter.add_institute(institute_obj)
    adapter.add_user(user_obj)
    return adapter


@pytest.fixture
def ldap_app(request):
    """app ficture for testing LDAP connections."""
    config = {
        "TESTING": True,
        "DEBUG": True,
        "SERVER_NAME": "fakey.server.name",
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
    """app ficture for testing LDAP connections."""
    config = {
        "TESTING": True,
        "DEBUG": True,
        "SERVER_NAME": "fakey.server.name",
        "GOOGLE": {
            "client_id": "test",
            "client_secret": "test",
            "discovery_url": "http://test.com",
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
