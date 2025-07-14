import ssl
from typing import Optional

from flask import Flask
from ldap3 import ALL, SIMPLE, SYNC, Connection, Server, Tls


class LdapManager:
    def __init__(self, app: Optional[Flask] = None) -> None:
        self.server: Optional[Server] = None
        self.base_dn: Optional[str] = None
        self.user_dn_template: Optional[str] = None
        self.timeout: int = 5
        self.use_ssl: bool = False

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize the LDAP client using Flask app config."""
        self.base_dn = app.config.get("LDAP_BASE_DN")
        if not self.base_dn:
            raise ValueError("LDAP_BASE_DN must be set")

        host: str = app.config.get("LDAP_HOST", "localhost")
        port: int = app.config.get("LDAP_PORT", 636 if app.config.get("LDAP_USE_SSL") else 389)
        self.use_ssl = app.config.get("LDAP_USE_SSL", False)
        self.timeout = app.config.get("LDAP_TIMEOUT", 5)
        self.user_dn_template = app.config.get("LDAP_BIND_USER_DN", "uid=%s")

        tls_config: Optional[Tls] = None
        if self.use_ssl and any(
            app.config.get(k)
            for k in ("LDAP_TLS_CERTFILE", "LDAP_TLS_KEYFILE", "LDAP_TLS_CACERTFILE")
        ):
            tls_config = Tls(
                local_certificate_file=app.config.get("LDAP_TLS_CERTFILE"),
                local_private_key_file=app.config.get("LDAP_TLS_KEYFILE"),
                ca_certs_file=app.config.get("LDAP_TLS_CACERTFILE"),
                validate=(
                    ssl.CERT_REQUIRED
                    if app.config.get("LDAP_TLS_REQUIRE_CERT", True)
                    else ssl.CERT_NONE
                ),
            )

        self.server = Server(
            host,
            port=port,
            use_ssl=self.use_ssl,
            get_info=ALL,
            tls=tls_config,
        )

    def authenticate(self, username: str, password: str) -> bool:
        """
        Attempt to bind with user credentials.
        Return True if credentials are valid, else False.
        """
        if not self.server:
            raise RuntimeError("LDAP server not initialized")

        user_dn: str = self._build_user_dn(username)

        try:
            conn = Connection(
                self.server,
                user=user_dn,
                password=password,
                authentication=SIMPLE,
                client_strategy=SYNC,
                receive_timeout=self.timeout,
                auto_bind=True,
            )
            conn.unbind()
            return True
        except Exception:
            return False

    def _build_user_dn(self, username: str) -> str:
        """
        Build full distinguished name (DN) for the user.
        Example: 'uid=username,dc=example,dc=org'
        """
        if not self.user_dn_template or not self.base_dn:
            raise RuntimeError("User DN template or base DN not configured")

        return f"{self.user_dn_template % username},{self.base_dn}"
