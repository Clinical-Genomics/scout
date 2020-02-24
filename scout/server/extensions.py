"""Code for extensions used by flask"""


from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_ldap3_login import LDAP3LoginManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_oauthlib.client import OAuth

from scout.adapter import MongoAdapter
from scout.adapter.client import get_connection

LOG = logging.getLogger(__name__)


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


class MongoDB:
    """Flask interface to mongodb"""

    @staticmethod
    def init_app(app):
        """Initialize from flask"""
        uri = app.config.get("MONGO_URI", None)

        db_name = app.config.get("MONGO_DBNAME", "scout")

        client = get_connection(
            host=app.config.get("MONGO_HOST", "localhost"),
            port=app.config.get("MONGO_PORT", 27017),
            username=app.config.get("MONGO_USERNAME", None),
            password=app.config.get("MONGO_PASSWORD", None),
            uri=uri,
            mongodb=db_name,
        )

        app.config["MONGO_DATABASE"] = client[db_name]
        app.config["MONGO_CLIENT"] = client


loqusdb = LoqusDB()
mongo = MongoDB()
