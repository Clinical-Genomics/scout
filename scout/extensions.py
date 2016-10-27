# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory
located in app.py
"""
from flask import current_app, request
from flask_admin import Admin
from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.markdown import Markdown
from flask_login import LoginManager
from flask_mail import Mail
from flask_mongoengine import MongoEngine
from flask_oauthlib.client import OAuth
from flask_sslify import SSLify
from loqusdb.plugins import MongoAdapter
import ssl
from housekeeper.store import api as hkapi

from scout.adapter import MongoAdapter as ScoutMongoAdapter

from scout.admin import AdminView
from scout.utils.omim import OMIM

# +--------------------------------------------------------------------+
# | Flask-DebugToolbar
# +--------------------------------------------------------------------+
toolbar = DebugToolbarExtension()

# +--------------------------------------------------------------------+
# | Flask-Admin
# +--------------------------------------------------------------------+
admin = Admin(index_view=AdminView())

# +--------------------------------------------------------------------+
# | Flask-Babel
# +--------------------------------------------------------------------+
babel = Babel()


@babel.localeselector
def get_locale():
    """Determine locale to use for translations."""
    accept_languages = current_app.config.get('ACCEPT_LANGUAGES')

    # first check request args
    session_language = request.args.get('lang')
    print(session_language)
    if session_language in accept_languages:
        return session_language

    # language can be forced in config
    user_language = current_app.config.get('REPORT_LANGUAGE')
    if user_language:
        return user_language

    # try to guess the language from the user accept header that
    # the browser transmits.  We support de/fr/en in this example.
    # The best match wins.
    return request.accept_languages.best_match(accept_languages)


# +--------------------------------------------------------------------+
# | Flask-MongoEngine
# +--------------------------------------------------------------------+
db = MongoEngine()

# +--------------------------------------------------------------------+
# | Storage-Adapter
# +--------------------------------------------------------------------+
store = ScoutMongoAdapter()

# +--------------------------------------------------------------------+
# | Flask-Login
# +--------------------------------------------------------------------+
login_manager = LoginManager()


# +--------------------------------------------------------------------+
# | Flask-Markdown
# +--------------------------------------------------------------------+
def markdown(app):
    return Markdown(app)


bootstrap = Bootstrap()

# +--------------------------------------------------------------------+
# | Flask-Mail
# +--------------------------------------------------------------------+
mail = Mail()

# +--------------------------------------------------------------------+
# | Flask-OAuthlib
# +--------------------------------------------------------------------+
oauth = OAuth()

# use Google as remote application
# you must configure 3 values from Google APIs console
# https://code.google.com/apis/console
google = oauth.remote_app('google', app_key='GOOGLE')

# +--------------------------------------------------------------------+
# | Flask-OMIM
# +--------------------------------------------------------------------+
omim = OMIM()


# +--------------------------------------------------------------------+
# | LoqusDB
# +--------------------------------------------------------------------+
class LoqusDB(MongoAdapter):
    def init_app(self, app):
        """Initialize from Flask."""
        self.connect(**app.config['LOQUSDB_SETTINGS'])

    def case_count(self):
        return self.db.case.find({}).count()


loqusdb = LoqusDB()

# +--------------------------------------------------------------------+
# | Flask-SSLify
# +--------------------------------------------------------------------+
# (ext lacks init_app...)
ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)


def ssl(app):
    """Proxy function to setup Flask-SSLify extension."""
    # Setup SSL: http://flask.pocoo.org/snippets/111/
    if not app.debug:
        ctx.load_cert_chain(app.config.get('SSL_CERT_PATH'),
                            app.config.get('SSL_KEY_PATH'))

    # https://github.com/kennethreitz/flask-sslify
    # Force SSL. Redirect all incoming requests to HTTPS.
    # Only takes effect when DEBUG=False
    return SSLify(app)


# +--------------------------------------------------------------------+
# | Housekeeper
# +--------------------------------------------------------------------+
class Housekeeper(object):
    def init_app(self, app):
        """Initialize Housekeeper connection."""
        db_uri = app.config['HOUSEKEEPER_DATABASE_URI']
        self.manager = hkapi.manager(db_uri)


housekeeper = Housekeeper()
