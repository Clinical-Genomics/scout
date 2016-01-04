# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory
located in app.py
"""
from flask import current_app, request

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
# | Flask-Babel
# +--------------------------------------------------------------------+
from flask.ext.babel import Babel
babel = Babel()

# +--------------------------------------------------------------------+
# | Flask-MongoEngine
# +--------------------------------------------------------------------+
from flask.ext.mongoengine import MongoEngine
db = MongoEngine()

# +--------------------------------------------------------------------+
# | Storage-Adapter
# +--------------------------------------------------------------------+
from .ext.backend import MongoAdapter
store = MongoAdapter()

# +--------------------------------------------------------------------+
# | Flask-Login
# +--------------------------------------------------------------------+
from flask.ext.login import LoginManager
login_manager = LoginManager()

# +--------------------------------------------------------------------+
# | Flask-Markdown
# +--------------------------------------------------------------------+
from flask.ext.markdown import Markdown
markdown = lambda app: Markdown(app)

# +--------------------------------------------------------------------+
# | Flask-Mail
# +--------------------------------------------------------------------+
from flask.ext.mail import Mail
mail = Mail()

# +--------------------------------------------------------------------+
# | Flask-OAuthlib
# +--------------------------------------------------------------------+
from flask_oauthlib.client import OAuth
oauth = OAuth()

# use Google as remote application
# you must configure 3 values from Google APIs console
# https://code.google.com/apis/console
google = oauth.remote_app('google', app_key='GOOGLE')

# +--------------------------------------------------------------------+
# | Flask-OMIM
# +--------------------------------------------------------------------+
from .ext.omim import OMIM
omim = OMIM()

# +--------------------------------------------------------------------+
# | Flask-SSLify
# +--------------------------------------------------------------------+
from flask_sslify import SSLify
from OpenSSL import SSL

# (ext lacks init_app...)
ctx = SSL.Context(SSL.SSLv23_METHOD)


def ssl(app):
  """Proxy function to setup Flask-SSLify extension."""
  # Setup SSL: http://flask.pocoo.org/snippets/111/
  if not app.debug:
    ctx.use_privatekey_file(app.config.get('SSL_KEY_PATH'))
    ctx.use_certificate_file(app.config.get('SSL_CERT_PATH'))

  # https://github.com/kennethreitz/flask-sslify
  # Force SSL. Redirect all incoming requests to HTTPS.
  # Only takes effect when DEBUG=False
  return SSLify(app)
