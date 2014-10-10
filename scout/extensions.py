# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory
located in app.py
"""
from __future__ import absolute_import, unicode_literals

# +--------------------------------------------------------------------+
# | Flask-Admin
# +--------------------------------------------------------------------+
from flask.ext.admin import Admin
from .admin import AdminView
admin = Admin(name='Scout', index_view=AdminView())

# +--------------------------------------------------------------------+
# | Flask-MongoEngine
# +--------------------------------------------------------------------+
from flask.ext.mongoengine import MongoEngine
db = MongoEngine()

# +--------------------------------------------------------------------+
# | Flask-DebugToolbar
# +--------------------------------------------------------------------+
from flask.ext.debugtoolbar import DebugToolbarExtension
debug_toolbar = DebugToolbarExtension()

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
