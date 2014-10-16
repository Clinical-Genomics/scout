# -*- coding: utf-8 -*-

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
