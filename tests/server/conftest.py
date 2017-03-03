# -*- coding: utf-8 -*-
import pytest

from scout.server.app import create_app


@pytest.fixture
def app():
    app = create_app(config=dict(DEBUG_TB_ENABLED=False))
    return app
