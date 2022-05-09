import logging
import ssl

from flask_ldapconn import LDAPConn
from ldap3 import ALL, SYNC, Server, Tls

LOG = logging.getLogger(__name__)


class LdapManager(LDAPConn):
    """Interface to LDAP login"""

    def init_app(self, app):
        ssl_defaults = ssl.get_default_verify_paths()

        # Default config
        app.config.setdefault("LDAP_SERVER", "localhost")
        app.config.setdefault("LDAP_PORT", 389)
        app.config.setdefault("LDAP_BINDDN", None)
        app.config.setdefault("LDAP_SECRET", None)
        app.config.setdefault("LDAP_CONNECT_TIMEOUT", 10)
        app.config.setdefault("LDAP_READ_ONLY", False)
        app.config.setdefault("LDAP_VALID_NAMES", None)
        app.config.setdefault("LDAP_PRIVATE_KEY_PASSWORD", None)
        app.config.setdefault("LDAP_RAISE_EXCEPTIONS", False)

        app.config.setdefault("LDAP_CONNECTION_STRATEGY", SYNC)

        app.config.setdefault("LDAP_USE_SSL", False)
        app.config.setdefault("LDAP_USE_TLS", True)
        app.config.setdefault("LDAP_TLS_VERSION", ssl.PROTOCOL_TLSv1_2)
        app.config.setdefault("LDAP_REQUIRE_CERT", ssl.CERT_REQUIRED)

        app.config.setdefault("LDAP_CLIENT_PRIVATE_KEY", None)
        app.config.setdefault("LDAP_CLIENT_CERT", None)

        app.config.setdefault("LDAP_CA_CERTS_FILE", ssl_defaults.cafile)
        app.config.setdefault("LDAP_CA_CERTS_PATH", ssl_defaults.capath)
        app.config.setdefault("LDAP_CA_CERTS_DATA", None)

        app.config.setdefault("FORCE_ATTRIBUTE_VALUE_AS_LIST", False)

        self.tls = Tls(
            local_private_key_file=app.config["LDAP_CLIENT_PRIVATE_KEY"],
            local_certificate_file=app.config["LDAP_CLIENT_CERT"],
            validate=app.config["LDAP_REQUIRE_CERT"]
            if app.config.get("LDAP_CLIENT_CERT")
            else ssl.CERT_NONE,
            version=app.config["LDAP_TLS_VERSION"],
            ca_certs_file=app.config["LDAP_CA_CERTS_FILE"],
            valid_names=app.config["LDAP_VALID_NAMES"],
            ca_certs_path=app.config["LDAP_CA_CERTS_PATH"],
            ca_certs_data=app.config["LDAP_CA_CERTS_DATA"],
            local_private_key_password=app.config["LDAP_PRIVATE_KEY_PASSWORD"],
        )

        self.ldap_server = Server(
            host=app.config.get("LDAP_HOST") or app.config.get("LDAP_SERVER"),
            port=app.config["LDAP_PORT"],
            use_ssl=app.config["LDAP_USE_SSL"],
            connect_timeout=app.config["LDAP_CONNECT_TIMEOUT"],
            tls=self.tls,
            get_info=ALL,
        )

        # Store ldap_conn object to extensions
        app.extensions["ldap_conn"] = self

        # Teardown appcontext
        app.teardown_appcontext(self.teardown)
