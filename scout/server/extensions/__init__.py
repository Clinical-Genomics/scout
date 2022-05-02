"""Code for extensions used by flask"""

from authlib.integrations.flask_client import OAuth
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail

from scout.adapter import MongoAdapter
from scout.utils.cloud_resources import AlignTrackHandler

from .beacon_extension import Beacon
from .gens_extension import GensViewer
from .ldap_extension import LdapManager
from .loqus_extension import LoqusDB
from .matchmaker_extension import MatchMaker
from .mongo_extension import MongoDB
from .rerunner_extension import RerunnerError, RerunnerService

bootstrap = Bootstrap()
store = MongoAdapter()
login_manager = LoginManager()
ldap_manager = LdapManager()
oauth_client = OAuth()
mail = Mail()
loqusdb = LoqusDB()
mongo = MongoDB()
gens = GensViewer()
rerunner = RerunnerService()
matchmaker = MatchMaker()
beacon = Beacon()
cloud_tracks = AlignTrackHandler()
