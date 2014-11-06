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
from flask.ext.admin.contrib.mongoengine import ModelView
from .admin.views import AdminView, UserView
from .admin.models import User, Institute, Role

admin = Admin(name='Scout', index_view=AdminView())
admin.add_view(UserView(User))
admin.add_view(ModelView(Institute))
admin.add_view(ModelView(Role))

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
