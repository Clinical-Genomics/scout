# -*- coding: utf-8 -*-

from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension()

from flask_bootstrap import Bootstrap
bootstrap = Bootstrap()

from scout.adapter import MongoAdapter
from flask_pymongo import PyMongo
mongo = PyMongo()
store = MongoAdapter()

from flask_login import LoginManager
from flask_oauthlib.client import OAuth
login_manager = LoginManager()
oauth = OAuth()
# use Google as remote application
# you must configure 3 values from Google APIs console
# https://code.google.com/apis/console
google = oauth.remote_app('google', app_key='GOOGLE')
