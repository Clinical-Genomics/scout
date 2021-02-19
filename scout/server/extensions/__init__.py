"""Code for extensions used by flask"""

from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_ldap3_login import LDAP3LoginManager
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail

from scout.adapter import MongoAdapter
from scout.utils.cloud_resources import AlignTrackHandler

from .loqus_extension import LoqusDB
from .mongo_extension import MongoDB
from .gens_extension import GensViewer


toolbar = DebugToolbarExtension()
bootstrap = Bootstrap()
store = MongoAdapter()
login_manager = LoginManager()
ldap_manager = LDAP3LoginManager()
oauth_client = OAuth()
mail = Mail()
loqusdb = LoqusDB()
mongo = MongoDB()
gens = GensViewer()
cloud_tracks = AlignTrackHandler()
