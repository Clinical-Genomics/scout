# -*- coding: utf-8 -*-
import pytest

from scout.app import AppFactory


@pytest.fixture
def app():
    app = AppFactory()
    return app
