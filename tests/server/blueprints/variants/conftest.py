# -*- coding: utf-8 -*-
import logging

import pytest
import pymongo

from scout.server.app import create_app
from scout.adapter import MongoAdapter
from scout.load.hgnc_gene import load_hgnc_genes
from scout.load.hpo import load_hpo


log = logging.getLogger(__name__)


class MockMail:
    _send_was_called = False
    _message = None

    def send(self, message):
        self._send_was_called = True
        self._message = message

@pytest.fixture
def mock_mail():
    return MockMail()

@pytest.fixture
def mock_sender():
    return 'mock_sender'
