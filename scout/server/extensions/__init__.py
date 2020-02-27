"""Code for extensions used by flask"""

from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_ldap3_login import LDAP3LoginManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_oauthlib.client import OAuth

from scout.adapter import MongoAdapter

from .loqus_extension import LoqusDB
from .mongo_extension import MongoDB

toolbar = DebugToolbarExtension()
bootstrap = Bootstrap()
store = MongoAdapter()
login_manager = LoginManager()
ldap_manager = LDAP3LoginManager()
mail = Mail()

oauth = OAuth()
# use Google as remote application
# you must configure 3 values from Google APIs console
# https://code.google.com/apis/console
google = oauth.remote_app("google", app_key="GOOGLE")


loqusdb = LoqusDB()
mongo = MongoDB()
