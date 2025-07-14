import logging
import ssl
from typing import Optional

from flask import Flask
from ldap3 import ALL, SIMPLE, SUBTREE, SYNC, Connection, Server, Tls

LOG = logging.getLogger(__name__)


class LdapManager:
    """
    LDAP authentication handler using ldap3.

    Supports user search by login attribute (e.g., mail),
    followed by secure bind to validate user password.
    """

    def __init__(self, app: Optional[Flask] = None) -> None:
        """
        Optionally initialize with a Flask app.

        :param app: Flask app instance (optional)
        """
        self.server: Optional[Server] = None
        self.base_dn: Optional[str] = None
        self.login_attr: str = "uid"
        self.timeout: int = 5
        self.use_ssl: bool = False
        self.use_tls: bool = False
        self.port: int = 389
        self.bind_user_dn: Optional[str] = None
        self.bind_user_pw: Optional[str] = None

        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """
        Initialize LDAP settings from Flask app config.

        Required config keys:
        - LDAP_BASE_DN
        - LDAP_HOST
        - LDAP_PORT (optional)
        - LDAP_USER_LOGIN_ATTR (optional, default 'uid')
        - LDAP_USE_SSL / LDAP_USE_TLS (optional)
        - LDAP_SERVICE_BIND_DN / LDAP_SERVICE_BIND_PASSWORD (for search auth)
        """
        self.base_dn = app.config.get("LDAP_BASE_DN")
        if not self.base_dn:
            raise ValueError("Missing required config: LDAP_BASE_DN")

        self.login_attr = app.config.get("LDAP_USER_LOGIN_ATTR", "uid")
        self.use_ssl = app.config.get("LDAP_USE_SSL", False)
        self.use_tls = app.config.get("LDAP_USE_TLS", False)
        self.timeout = app.config.get("LDAP_TIMEOUT", 5)
        self.port = app.config.get("LDAP_PORT", 636 if self.use_ssl else 389)
        self.bind_user_dn = app.config.get("LDAP_SERVICE_BIND_DN")
        self.bind_user_pw = app.config.get("LDAP_SERVICE_BIND_PASSWORD")

        host = app.config.get("LDAP_HOST", "localhost")
        tls_config: Optional[Tls] = (
            Tls(validate=ssl.CERT_NONE) if self.use_ssl or self.use_tls else None
        )

        self.server = Server(
            host=host,
            port=self.port,
            use_ssl=self.use_ssl,
            tls=tls_config,
            get_info=ALL,
        )

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate user by:
        1. Searching for their DN using login attribute
        2. Binding as that DN with the provided password

        :param username: e.g. 'user@example.com'
        :param password: the user's plaintext password
        :return: True if login succeeds, False if invalid
        """
        if not self.server:
            raise RuntimeError("LDAP server not initialized")

        try:
            # Step 1: Search for user's DN
            search_conn = Connection(
                self.server,
                user=self.bind_user_dn,
                password=self.bind_user_pw,
                auto_bind=True,
                client_strategy=SYNC,
                receive_timeout=self.timeout,
            )

            if self.use_tls:
                search_conn.start_tls()

            search_filter = f"({self.login_attr}={username})"
            search_conn.search(
                search_base=self.base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=[],  # no need to request DN directly
            )

            if not search_conn.entries:
                return False

            user_dn = search_conn.entries[0].entry_dn
            search_conn.unbind()

            # Step 2: Attempt to bind as user
            user_conn = Connection(
                self.server,
                user=user_dn,
                password=password,
                auto_bind=True,
                authentication=SIMPLE,
                receive_timeout=self.timeout,
            )

            if self.use_tls:
                user_conn.start_tls()

            user_conn.unbind()
            return True

        except Exception as e:
            LOG.warning(e)
            return False
