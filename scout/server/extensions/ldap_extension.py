import logging

from flask_ldap3_login import LDAP3LoginManager
from ldap3 import ALL, SUBTREE, Connection, Server

LOG = logging.getLogger(__name__)


class LdapManager:
    """Interface to LDAP login using flask-ldap3-login (supports direct or search bind)"""

    def __init__(self):
        self.ldap_manager = LDAP3LoginManager()
        self.app = None

    def init_app(self, app):
        """Initialize LDAP manager with Flask app config."""
        self.app = app

        app.config.setdefault("LDAP_HOST", "localhost")
        app.config.setdefault("LDAP_PORT", 389)
        app.config.setdefault("LDAP_USE_SSL", False)
        app.config.setdefault("LDAP_USE_TLS", True)

        app.config.setdefault("LDAP_BASE_DN", "dc=planetexpress,dc=com")
        app.config.setdefault("LDAP_USER_DN", "ou=people,dc=planetexpress,dc=com")
        app.config.setdefault("LDAP_USER_RDN_ATTR", "uid")
        app.config.setdefault("LDAP_USER_LOGIN_ATTR", "mail")

        app.config.setdefault("LDAP_BINDDN", "cn=admin,dc=planetexpress,dc=com")
        app.config.setdefault("LDAP_SECRET", "admin-secret")

        app.config.setdefault("LDAP_GROUP_DN", None)
        app.config.setdefault("LDAP_BIND_DIRECT_CREDENTIALS", False)

        self.ldap_manager.init_app(app)
        app.extensions["ldap_conn"] = self
        app.teardown_appcontext(self.teardown)

    def ldap_authorized(self, username: str, password: str) -> bool:
        """
        Authenticate a user with LDAP, trying direct bind first if configured,
        then falling back to search+bind.
        """
        try:
            # Attempt direct bind if configured
            if self.app.config.get("LDAP_BIND_DIRECT_CREDENTIALS", False):
                if self._direct_bind(username, password):
                    LOG.info(f"Direct LDAP bind succeeded for {username}")
                    return True
                else:
                    LOG.info(f"Direct LDAP bind failed for {username}, falling back to search+bind")

            # Fallback: search+bind via flask-ldap3-login
            result = self.ldap_manager.authenticate(username, password)
            if not result or not getattr(result, "status", False):
                LOG.warning(f"LDAP search+bind authentication failed for {username}")
                return False

            LOG.info(f"LDAP authentication succeeded for {username}")

            # Optional group membership check
            group_dn = self.app.config.get("LDAP_GROUP_DN")
            if group_dn:
                conn = self.ldap_manager.connection
                user_dn = result.user_dn
                search_filter = f"(member={user_dn})"
                conn.search(group_dn, search_filter, search_scope=SUBTREE, attributes=["dn"])
                if not conn.entries:
                    LOG.info(f"User {username} not in required group {group_dn}")
                    return False

            return True

        except Exception as ex:
            LOG.exception(f"LDAP auth failed for {username}: {ex}")
            return False

    def _direct_bind(self, username: str, password: str) -> bool:
        """Try to bind directly as the user, skipping any search."""
        try:
            user_rdn_attr = self.app.config["LDAP_USER_RDN_ATTR"]
            user_dn_base = self.app.config["LDAP_USER_DN"]
            user_dn = f"{user_rdn_attr}={username},{user_dn_base}"

            server = Server(
                self.app.config["LDAP_HOST"],
                port=self.app.config["LDAP_PORT"],
                use_ssl=self.app.config["LDAP_USE_SSL"],
                get_info=ALL,
            )

            conn = Connection(server, user=user_dn, password=password, auto_bind=True)
            conn.unbind()
            return True
        except Exception as e:
            LOG.debug(f"Direct bind failed for {username}: {e}")
            return False

    def teardown(self, exception):
        """Optional teardown, placeholder for API compatibility"""
        pass
