# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory
located in app.py
"""
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

from scout.adapter import MongoAdapter as ScoutMongoAdapter

from .admin import AdminView
from .ext.omim import OMIM

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
