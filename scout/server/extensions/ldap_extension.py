import logging
import ssl
from typing import Optional

from flask import Flask
from ldap3 import ALL, SIMPLE, SUBTREE, SYNC, Connection, Server, Tls
from ldap3.core.exceptions import LDAPBindError, LDAPExceptionError, LDAPSocketOpenError

LOG = logging.getLogger(__name__)


class LdapManager:
    """
    LDAP authentication handler using ldap3.

    Supports:
    1. User search by login attribute (e.g., mail, uid) with service bind.
    2. Direct DN bind if LDAP_USER_DN is provided.
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
        self.user_dn_base: Optional[str] = None

        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self.base_dn = app.config.get("LDAP_BASE_DN")
        if not self.base_dn:
            raise ValueError("Missing required config: LDAP_BASE_DN")

        self.login_attr = app.config.get("LDAP_USER_LOGIN_ATTR", "uid")
        self.use_ssl = app.config.get("LDAP_USE_SSL", False)
        self.use_tls = app.config.get("LDAP_USE_TLS", False)
        self.timeout = app.config.get("LDAP_TIMEOUT", 5)
        self.port = app.config.get("LDAP_PORT", 636 if self.use_ssl else 389)

        # Support your config keys
        self.bind_user_dn = app.config.get("LDAP_BINDDN")
        self.bind_user_pw = app.config.get("LDAP_SECRET")
        self.user_dn_base = app.config.get("LDAP_USER_DN")

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
        if not self.server:
            raise RuntimeError("LDAP server not initialized")

        try:
            user_dn = None

            # --- Step 1: Search for the user DN ---
            if self.bind_user_dn and self.bind_user_pw:
                # Service bind mode
                search_conn = Connection(
                    self.server,
                    user=self.bind_user_dn,
                    password=self.bind_user_pw,
                    auto_bind=True,
                    client_strategy=SYNC,
                    receive_timeout=self.timeout,
                )
            else:
                # Anonymous bind mode
                search_conn = Connection(
                    self.server,
                    auto_bind=True,  # allow anonymous bind
                    client_strategy=SYNC,
                    receive_timeout=self.timeout,
                )

            if self.use_tls:
                search_conn.start_tls()

            search_filter = f"({self.login_attr}={username})"
            LOG.debug("LDAP search with filter=%s, base=%s", search_filter, self.base_dn)

            search_conn.search(
                search_base=self.base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=[],
            )

            if search_conn.entries:
                user_dn = search_conn.entries[0].entry_dn
                LOG.debug("Found DN for %s: %s", username, user_dn)

            search_conn.unbind()

            # --- Step 2: Fallback if no DN found ---
            if not user_dn and self.user_dn_base:
                user_dn = f"{self.login_attr}={username},{self.user_dn_base}"
                LOG.debug("Constructed DN for %s: %s", username, user_dn)

            if not user_dn:
                LOG.warning("No DN found/constructed for user %s", username)
                return False

            # --- Step 3: Try to bind as the actual user ---
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

        except LDAPBindError:
            LOG.error("LDAP bind failed for user %s (invalid credentials)", username)
        except LDAPSocketOpenError:
            LOG.error("LDAP connection to %s:%s failed", self.server.host, self.server.port)
        except LDAPExceptionError as e:
            LOG.error("General LDAP error for user %s: %s", username, e)
        except Exception as e:
            LOG.exception("Unexpected error during LDAP authentication for %s", username)

        return False
