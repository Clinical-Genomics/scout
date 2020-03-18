"""Fixtures for login blueprints"""

import pytest


@pytest.fixture
def user_adapter(adapter, user_obj, institute_obj):
    """Return a adatper with a user and institute"""
    adapter.add_institute(institute_obj)
    adapter.add_user(user_obj)
    return adapter
