# -*- coding: utf-8 -*-
import logging

import pytest
import pymongo

from flask import request
from flask_login import login_user, logout_user

from scout.server.blueprints.login.models import LoginUser
from scout.server.app import create_app
from scout.adapter import MongoAdapter
from scout.load.hgnc_gene import load_hgnc_genes
from scout.load.hpo import load_hpo

log = logging.getLogger(__name__)

@pytest.fixture
def app(real_database_name, real_variant_database, user_obj):

    app = create_app(config=dict(TESTING=True, DEBUG=True, MONGO_DBNAME=real_database_name,
                                 DEBUG_TB_ENABLED=False, LOGIN_DISABLED=True))

    @app.route('/auto_login')
    def auto_login():
        log.debug('Got request for auto login for {}'.format(user_obj))
        user_inst = LoginUser(user_obj)
        assert login_user(user_inst, remember=True)
        return "ok"

    return app


@pytest.fixture
def institute_info():
    _institute_info = dict(internal_id='cust000', display_name='test_institute')
    return _institute_info


@pytest.fixture
def user_info(institute_info):
    _user_info = dict(email='john@doe.com', name='John Doe', roles=['admin','mme_submitter'],
                      institutes=[institute_info['internal_id']])
    return _user_info
