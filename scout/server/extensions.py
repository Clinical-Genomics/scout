# -*- coding: utf-8 -*-
import logging
from pymongo.errors import (ConnectionFailure)

from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension()

from flask_bootstrap import Bootstrap
bootstrap = Bootstrap()

from scout.adapter import MongoAdapter
store = MongoAdapter()

from flask_login import LoginManager
from flask_ldap3_login import LDAP3LoginManager
from flask_oauthlib.client import OAuth

login_manager = LoginManager()
ldap_manager = LDAP3LoginManager()

oauth = OAuth()
# use Google as remote application
# you must configure 3 values from Google APIs console
# https://code.google.com/apis/console
google = oauth.remote_app('google', app_key='GOOGLE')

from flask_mail import Mail
mail = Mail()

from scout.adapter.client import get_connection

LOG = logging.getLogger(__name__)


class LoqusDB():
    def init_app(self, app):
        """Initialize from Flask."""
        LOG.info("Connecting to loqusdb")
        return
    
    def _fetch_variant(self, loqus_id):
        """Query loqusdb for variant information
        
        Args:
            loqus_id(str): The variant id in loqusdb format
        
        Returns:
            res
        """
        res = {}
        res = {
            '_id': '1_879537_T_C', 
            'homozygote': 2, 
            'hemizygote': 0, 
            'observations': 2, 
            'chrom': '1', 
            'start': 879537, 
            'end': 879538, 
            'ref': 'T', 
            'alt': 'C', 
            'families': ['recessive_trio', 'help']
        }
        return res
    
    def get_variant(self, variant_info):
        """Return information for a variant from loqusdb
        
        
        Args:
            variant_info(dict)
        
        Returns:
            loqus_variant(dict)
        """
        loqus_variant = self._fetch_variant(variant_info['_id'])
        loqus_variant['total'] = self._case_count()
        
        return loqus_variant

    def _case_count(self):
        """Return number of cases that the observation is based on
        
        Returns:
            nr_cases(int)
        """
        nr_cases = 754
        return nr_cases

class MongoDB(object):

    def init_app(self, app):
        """Initialize from flask"""
        uri = app.config.get("MONGO_URI", None)

        db_name = app.config.get("MONGO_DBNAME", 'scout')

        try:
            client = get_connection(
                host = app.config.get("MONGO_HOST", 'localhost'),
                port=app.config.get("MONGO_PORT", 27017),
                username=app.config.get("MONGO_USERNAME", None),
                password=app.config.get("MONGO_PASSWORD", None),
                uri=uri,
                mongodb= db_name
            )
        except ConnectionFailure:
            context.abort()

        app.config["MONGO_DATABASE"] = client[db_name]
        app.config['MONGO_CLIENT'] = client



loqusdb = LoqusDB()
mongo = MongoDB()
