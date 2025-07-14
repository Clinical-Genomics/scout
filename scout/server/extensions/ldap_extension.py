import logging
import ssl
from typing import Optional

from flask import Flask
from ldap3 import ALL, SIMPLE, SUBTREE, SYNC, Connection, Server, Tls

LOG = logging.getLogger(__name__)


class LdapManager:
    """
    A minimal LDAP authentication handler for Flask using ldap3.

    This class allows searching for a user's DN using a login attribute (e.g., mail),
    then attempts to bind with the user's DN and password to verify credentials.
    """

    def __init__(self, app: Optional[Flask] = None) -> None:
        self.server: Optional[Server] = None
        self.base_dn: Optional[str] = None
        self.login_attr: str = "uid"
        self.timeout: int = 5
        self.use_ssl: bool = False
        self.use_tls: bool = False
        self.port: int = 389
        self.bind_user_dn: Optional[str] = None
        self.bind_user_pw: Optional[str] = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize the LDAP client using Flask app config."""
        self.base_dn = app.config.get("LDAP_BASE_DN")
        if not self.base_dn:
            raise ValueError("LDAP_BASE_DN must be set")

        self.login_attr = app.config.get("LDAP_USER_LOGIN_ATTR", "uid")
        self.use_ssl = app.config.get("LDAP_USE_SSL", False)
        self.use_tls = app.config.get("LDAP_USE_TLS", False)
        self.timeout = app.config.get("LDAP_TIMEOUT", 5)
        self.port = app.config.get("LDAP_PORT", 636 if self.use_ssl else 389)
        self.bind_user_dn = app.config.get("LDAP_SERVICE_BIND_DN")
        self.bind_user_pw = app.config.get("LDAP_SERVICE_BIND_PASSWORD")

        host = app.config.get("LDAP_HOST", "localhost")

        tls_config: Optional[Tls] = None
        if self.use_ssl or self.use_tls:
            tls_config = Tls(validate=ssl.CERT_NONE)

        self.server = Server(
            host,
            port=self.port,
            use_ssl=self.use_ssl,
            get_info=ALL,
            tls=tls_config,
        )

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate a user by searching for their DN and binding with their password.
        Returns True if authentication succeeds, False otherwise.
        """
        if not self.server:
            raise RuntimeError("LDAP server not initialized")

        # 1. Search for the user
        try:
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
                attributes=[],
            )

            if not search_conn.entries:
                return False

            user_dn = search_conn.entries[0].entry_dn
            search_conn.unbind()
        except Exception as e:
            LOG.warning(e)
            return False

        # 2. Try binding as user
        try:
            print(f"[LDAP] Attempting bind with user DN: {user_dn}")
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
