import logging

from flask_ldap3_login import LDAP3LoginManager
from ldap3 import SUBTREE

LOG = logging.getLogger(__name__)


class LdapManager:
    """Interface to LDAP login using flask-ldap3-login"""

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
        app.config.setdefault("LDAP_USER_DN", "ou=people")
        app.config.setdefault("LDAP_USER_LOGIN_ATTR", "mail")

        app.config.setdefault("LDAP_BINDDN", "cn=admin,dc=planetexpress,dc=com")
        app.config.setdefault("LDAP_SECRET", "admin-secret")

        # Optional group restriction DN (not a filter, but a specific DN)
        app.config.setdefault("LDAP_GROUP_DN", None)

        self.ldap_manager.init_app(app)

        app.extensions["ldap_conn"] = self
        app.teardown_appcontext(self.teardown)

    def ldap_authorized(self, username: str, password: str) -> bool:
        """
        Authenticate a user with LDAP and optionally check group membership.
        Returns True if credentials are valid and user is allowed.
        """
        try:
            result = self.ldap_manager.authenticate(username, password)

            if not result or not getattr(result, "status", False):
                LOG.warning(f"LDAP authentication failed for user {username}")
                return False

            LOG.info(f"LDAP authentication succeeded for {username}")

            group_dn = self.app.config.get("LDAP_GROUP_DN")
            if group_dn:
                conn = self.ldap_manager.connection
                user_dn = result.user_dn

                # Check whether user_dn appears as a member in the group
                search_filter = f"(member={user_dn})"
                conn.search(group_dn, search_filter, search_scope=SUBTREE, attributes=["dn"])

                if not conn.entries:
                    LOG.info(f"User {username} not in required group {group_dn}")
                    return False

            return True

        except Exception as ex:
            LOG.exception(f"LDAP auth failed for {username}: {ex}")
            return False

    def teardown(self, exception):
        """Optional teardown, placeholder for API compatibility"""
        pass
