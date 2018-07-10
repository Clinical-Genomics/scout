# -*- coding: utf-8 -*-

from pymongo.errors import (ConnectionFailure)


from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension()

from flask_bootstrap import Bootstrap
bootstrap = Bootstrap()

from scout.adapter import MongoAdapter
store = MongoAdapter()

from flask_login import LoginManager
from flask_oauthlib.client import OAuth
login_manager = LoginManager()
oauth = OAuth()
# use Google as remote application
# you must configure 3 values from Google APIs console
# https://code.google.com/apis/console
google = oauth.remote_app('google', app_key='GOOGLE')

from flask_mail import Mail
mail = Mail()


from loqusdb.plugins import MongoAdapter as LoqusDBMongoAdapter

from scout.adapter.client import get_connection


class LoqusDB(LoqusDBMongoAdapter):
    def init_app(self, app):
        """Initialize from Flask."""
        self.connect(**app.config['LOQUSDB_SETTINGS'])

    def case_count(self):
        return self.db.case.find({}).count()

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
