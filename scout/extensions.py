# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory
located in app.py
"""
from __future__ import absolute_import, unicode_literals

# +--------------------------------------------------------------------+
# | Flask-DebugToolbar
# +--------------------------------------------------------------------+
from flask.ext.debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension()

# +--------------------------------------------------------------------+
# | Flask-Admin
# +--------------------------------------------------------------------+
from flask.ext.admin import Admin
from .admin import AdminView
admin = Admin(index_view=AdminView())

# +--------------------------------------------------------------------+
# | Flask-MongoEngine
# +--------------------------------------------------------------------+
from flask.ext.mongoengine import MongoEngine
db = MongoEngine()

# +--------------------------------------------------------------------+
# | Storage-Adapter
# +--------------------------------------------------------------------+
from .ext.backend import VcfAdapter
store = VcfAdapter()

# +--------------------------------------------------------------------+
# | Flask-Login
# +--------------------------------------------------------------------+
from flask.ext.login import LoginManager
login_manager = LoginManager()

# +--------------------------------------------------------------------+
# | Flask-OAuthlib
# +--------------------------------------------------------------------+
from flask_oauthlib.client import OAuth
oauth = OAuth()

# use Google as remote application
# you must configure 3 values from Google APIs console
# https://code.google.com/apis/console
google = oauth.remote_app('google', app_key='GOOGLE')
