"""Code for flask app"""

import logging
import os
from datetime import timedelta

from flask import Flask, redirect, request, url_for
from flask_cors import CORS
from flask_login import current_user

from scout import __version__
from scout.log import init_log
from scout.utils.config import load_config

from . import extensions
from .blueprints import (
    alignviewers,
    api,
    cases,
    clinvar,
    dashboard,
    diagnoses,
    genes,
    institutes,
    login,
    managed_variants,
    mme,
    omics_variants,
    panels,
    phenomodels,
    phenotypes,
    public,
    variant,
    variants,
)
from .filters import register_template_filters

LOG = logging.getLogger(__name__)

USERS_LOGGER_PATH_PARAM = "USERS_ACTIVITY_LOG_PATH"


def create_app(config_file=None, config=None):
    """Flask app factory function.
    # 1. Always load defaults from config.py
    # 2. Merge everything through load_config
    # 3. Apply session timeout if configured
    # 4. Register app parts
    # 5. Optional email error logging
    """

    app = Flask(__name__)
    CORS(app)
    app.jinja_env.add_extension("jinja2.ext.do")
    app.jinja_env.globals["SCOUT_VERSION"] = __version__

    app.config.from_pyfile("config.py")

    merged_config = load_config(
        cli_options=config,  # when invoked via CLI
        cli_config=None,  # YAML handled upstream - only used for pure CLI commands
        flask_conf=config_file,
    )
    app.config.update({k: v for k, v in merged_config.items() if v is not None})

    session_timeout_minutes = app.config.get("SESSION_TIMEOUT_MINUTES")
    if session_timeout_minutes:
        session_duration = timedelta(minutes=session_timeout_minutes)
        app.config["PERMANENT_SESSION_LIFETIME"] = session_duration
        app.config["REMEMBER_COOKIE_DURATION"] = session_duration

    app.json.sort_keys = False

    init_log(log=LOG, app=app)
    configure_extensions(app)
    register_blueprints(app)
    register_template_filters(app)
    register_tests(app)

    if not (app.debug or app.testing) and app.config.get("MAIL_USERNAME"):
        configure_email_logging(app)

    @app.before_request
    def check_user():
        if not app.config.get("LOGIN_DISABLED") and request.endpoint:
            # check if the endpoint requires authentication
            static_endpoint = "static" in request.endpoint or request.endpoint in [
                "report.report",
                "report.json_chrom_coverage",
            ]
            public_endpoint = getattr(app.view_functions[request.endpoint], "is_public", False)
            relevant_endpoint = not (static_endpoint or public_endpoint)
            # if endpoint requires auth, check if user is authenticated
            if relevant_endpoint and not current_user.is_authenticated:
                return redirect(url_for("public.index"))

    @app.before_request
    def log_users_activity():
        """Log users' navigation to file, if specified in the app setting.s"""
        if USERS_LOGGER_PATH_PARAM not in app.config:
            return
        user = current_user.email if current_user.is_authenticated else "anonymous"
        LOG.info(" - ".join([user, request.path]))

    return app


def configure_extensions(app):
    """Configure Flask extensions."""

    extensions.bootstrap.init_app(app)
    extensions.mongo.init_app(app)
    extensions.store.init_app(app)
    extensions.login_manager.init_app(app)
    extensions.mail.init_app(app)
    extensions.clinvar_api.init_app(app)

    if app.config.get("SQLALCHEMY_DATABASE_URI"):
        extensions.chanjo_report.init_app(app)
        LOG.info("Chanjo extension enabled")

    if app.config.get("CHANJO2_URL"):
        LOG.info("Chanjo2 extension enabled")
        extensions.chanjo2.init_app(app)

    if app.config.get("LOQUSDB_SETTINGS"):
        LOG.info("LoqusDB enabled")
        # setup LoqusDB
        extensions.loqusdb.init_app(app)

    if app.config.get("GENS_HOST"):
        LOG.info("Gens enabled")
        extensions.gens.init_app(app)

    if all(
        [
            app.config.get("MME_URL"),
            app.config.get("MME_ACCEPTS"),
            app.config.get("MME_TOKEN"),
        ]
    ):
        LOG.info("Matchmaker Exchange extension enabled")
        extensions.matchmaker.init_app(app)

    if all(
        [
            app.config.get("BEACON_URL"),
            app.config.get("BEACON_TOKEN"),
        ]
    ):
        LOG.info("Beacon extension enabled")
        extensions.beacon.init_app(app)

    if app.config.get("RERUNNER_API_ENTRYPOINT") and app.config.get("RERUNNER_API_KEY"):
        LOG.info("Rerunner service enabled")
        # setup rerunner service
        extensions.rerunner.init_app(app)

    set_login_system(app)

    if app.config.get("CUSTOM_IGV_TRACKS") or app.config.get("CLOUD_IGV_TRACKS"):
        LOG.info("Collecting IGV tracks from cloud or local resources")
        extensions.config_igv_tracks.init_app(app)

    if app.config.get("PHENOPACKET_API_URL"):
        LOG.info("Enable Phenopacket API")
        extensions.phenopacketapi.init_app(app)

    if app.config.get("BIONANO_ACCESS"):
        LOG.info("Enable BioNano Access API")
        extensions.bionano_access.init_app(app)


def set_login_system(app):
    """Initialize login system: LDAP, Google OAuth, Keycloak. If none of these is set, then simple database user matching is used."""
    if app.config.get("LDAP_HOST"):
        LOG.info("LDAP login enabled")
        extensions.ldap_manager.init_app(app)

    if app.config.get("GOOGLE"):
        LOG.info("Google login enabled")
        configure_google_login(app)

    if app.config.get("KEYCLOAK"):
        LOG.info("keycloak login enabled")
        configure_keycloak_login(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.public_bp)
    app.register_blueprint(genes.genes_bp)
    app.register_blueprint(cases.cases_bp)
    app.register_blueprint(clinvar.clinvar_bp)
    app.register_blueprint(mme.mme_bp)
    app.register_blueprint(login.login_bp)
    app.register_blueprint(variant.variant_bp)
    app.register_blueprint(variants.variants_bp)
    app.register_blueprint(panels.panels_bp)
    app.register_blueprint(dashboard.dashboard_bp)
    app.register_blueprint(api.api_bp)
    app.register_blueprint(alignviewers.alignviewers_bp)
    app.register_blueprint(phenotypes.hpo_bp)
    app.register_blueprint(phenomodels.phenomodels_bp)
    app.register_blueprint(diagnoses.omim_bp)
    app.register_blueprint(institutes.overview)
    app.register_blueprint(managed_variants.managed_variants_bp)
    app.register_blueprint(omics_variants.omics_variants_bp)


def register_tests(app):
    """Register custom Jinja template tests"""

    @app.template_test("existing")
    def path_exists(path):
        """Check if file exists. Helper for jinja template."""
        return os.path.exists(path)


def configure_oidc_login(app: Flask, provider_name: str, config_key: str):
    """Register an OIDC login client using config settings."""
    provider_conf = app.config[config_key]
    extensions.oauth_client.init_app(app)
    extensions.oauth_client.register(
        name=provider_name,
        server_metadata_url=provider_conf.get("discovery_url"),
        client_id=provider_conf.get("client_id"),
        client_secret=provider_conf.get("client_secret"),
        client_kwargs={"scope": "openid email profile"},
    )


def configure_google_login(app):
    """Register the Google Oauth login client using config settings"""
    configure_oidc_login(app, "google", "GOOGLE")


def configure_keycloak_login(app):
    """Register a Keycloak OIDC login client using config settings"""
    configure_oidc_login(app, "keycloak", "KEYCLOAK")


def configure_email_logging(app):
    """Setup logging of error/exceptions to email."""
    import logging

    from scout.log import TlsSMTPHandler

    mongodbname = app.config["MONGO_DBNAME"]
    mail_handler = TlsSMTPHandler(
        mailhost=app.config["MAIL_SERVER"],
        fromaddr=app.config["MAIL_USERNAME"],
        toaddrs=app.config["ADMINS"],
        subject="O_ops... {} failed on db {}!".format(app.name, mongodbname),
        credentials=(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"]),
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
        )
    )
    app.logger.addHandler(mail_handler)
