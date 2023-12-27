"""Code for flask app"""
import logging
import os
from datetime import timedelta
from typing import Dict, Union
from urllib.parse import parse_qsl, unquote, urlsplit

import coloredlogs
from flask import Flask, current_app, redirect, request, url_for
from flask_babel import Babel
from flask_cors import CORS
from flask_login import current_user
from flaskext.markdown import Markdown
from markupsafe import Markup

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
    panels,
    phenomodels,
    phenotypes,
    public,
    variant,
    variants,
)

LOG = logging.getLogger(__name__)

try:
    from chanjo_report.server.app import configure_template_filters
    from chanjo_report.server.blueprints import report_bp
    from chanjo_report.server.extensions import api as chanjo_api
except ImportError:
    chanjo_api = None
    report_bp = None
    configure_template_filters = None
    LOG.info("chanjo report not installed!")


def create_app(config_file=None, config=None):
    """Flask app factory function."""

    app = Flask(__name__)
    CORS(app)
    app.jinja_env.add_extension("jinja2.ext.do")

    app.config.from_pyfile("config.py")  # Load default config file
    if (
        config
    ):  # Params from an optional .yaml config file provided by the user or created by the app cli
        app.config.update((k, v) for k, v in config.items() if v is not None)
    if config_file:  # Params from an optional .py config file provided by the user
        app.config.from_pyfile(config_file)

    session_timeout_minutes = app.config.get("SESSION_TIMEOUT_MINUTES")
    if session_timeout_minutes:
        session_duration = timedelta(minutes=session_timeout_minutes)
        app.config["PERMANENT_SESSION_LIFETIME"] = session_duration
        app.config["REMEMBER_COOKIE_DURATION"] = session_duration

    app.json.sort_keys = False

    current_log_level = LOG.getEffectiveLevel()
    coloredlogs.install(level="DEBUG" if app.debug else current_log_level)
    configure_extensions(app)
    register_blueprints(app)
    register_filters(app)
    register_tests(app)

    if not (app.debug or app.testing) and app.config.get("MAIL_USERNAME"):
        # setup email logging of errors
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
                # combine visited URL (convert byte string query string to unicode!)
                next_url = "{}?{}".format(request.path, request.query_string.decode())
                login_url = url_for("public.index", next=next_url)
                return redirect(login_url)

    return app


def configure_extensions(app):
    """Configure Flask extensions."""

    extensions.bootstrap.init_app(app)
    extensions.mongo.init_app(app)
    extensions.store.init_app(app)
    extensions.login_manager.init_app(app)
    extensions.mail.init_app(app)

    Markdown(app)

    if app.config.get("SQLALCHEMY_DATABASE_URI"):
        LOG.info("Chanjo extension enabled")
        configure_coverage(app)

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

    if app.config.get("LDAP_HOST"):
        LOG.info("LDAP login enabled")
        # setup connection to server
        extensions.ldap_manager.init_app(app)

    if app.config.get("GOOGLE"):
        LOG.info("Google login enabled")
        # setup connection to google oauth2
        configure_oauth_login(app)

    if app.config.get("CLOUD_IGV_TRACKS"):
        LOG.info("Collecting IGV tracks from cloud resources")
        extensions.cloud_tracks.init_app(app)

    if app.config.get("PHENOPACKET_API_URL"):
        LOG.info("Enable Phenopacket API")
        extensions.phenopacketapi.init_app(app)

    if app.config.get("BIONANO_ACCESS"):
        LOG.info("Enable BioNano Access API")
        extensions.bionano_access.init_app(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.public_bp)
    app.register_blueprint(genes.genes_bp)
    app.register_blueprint(cases.cases_bp)
    app.register_blueprint(clinvar.clinvar_bp)
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


def register_filters(app):
    @app.template_filter()
    def human_longint(value: Union[int, str]) -> str:
        """Convert a long integers int or string representation into a human easily readable number."""
        value = str(value)
        if value.isnumeric():
            return "{:,}".format(int(value)).replace(",", "&thinsp;")
        return value

    @app.template_filter()
    def human_decimal(number, ndigits=4):
        """Return a standard representation of a decimal number.

        Args:
            number (float): number to humanize
            ndigits (int, optional): max number of digits to round to

        Return:
            str: humanized string of the decimal number
        """
        min_number = 10**-ndigits
        if isinstance(number, str):
            number = None
        if number is None:
            # NaN
            return "-"
        if number == 0:
            # avoid confusion over what is rounded and what is actually 0
            return 0
        if number < min_number:
            # make human readable and sane
            return "<{}".format(min_number)

        # round all other numbers
        return round(number, ndigits)

    @app.template_filter()
    def tuple_list_to_dict(tuple_list, key_elem, value_elem):
        """Accepts a list of tuples and returns a dictionary with tuple element = key_elem as keys and tuple element = value_elem as values"""

        return {tup[key_elem]: tup[value_elem] for tup in tuple_list}

    @app.template_filter()
    def url_decode(string):
        """Decode a string with encoded hex values."""
        return unquote(string)

    @app.template_filter()
    def url_args(url: str) -> Dict[str, str]:
        """Return all arguments and values present in a string URL."""
        return dict(parse_qsl(urlsplit(url).query))

    @app.template_filter()
    def cosmic_prefix(cosmicId):
        """If cosmicId is an integer, add 'COSM' as prefix
        otherwise return unchanged"""
        if isinstance(cosmicId, int):
            return "COSM" + str(cosmicId)
        return cosmicId

    @app.template_filter()
    def count_cursor(pymongo_cursor):
        """Count number of returned documents (deprecated pymongo.cursor.count())"""
        # Perform operations on a copy of the cursor so original does not move
        cursor_copy = pymongo_cursor.clone()
        return len(list(cursor_copy))

    @app.template_filter()
    def list_intersect(list1, list2) -> list:
        """Returns the elements that are common in 2 lists"""
        return list(set(list1) & set(list2))

    @app.template_filter()
    def list_remove_none(in_list: list) -> list:
        """Returns a list after removing any None values from it."""
        return [item for item in in_list if item is not None]


def register_tests(app):
    @app.template_test("existing")
    def path_exists(path):
        """Check if file exists. Helper for jinja template."""
        return os.path.exists(path)


def configure_oauth_login(app):
    """Register the Google Oauth login client using config settings"""

    google_conf = app.config["GOOGLE"]
    discovery_url = google_conf.get("discovery_url")
    client_id = google_conf.get("client_id")
    client_secret = google_conf.get("client_secret")

    extensions.oauth_client.init_app(app)

    extensions.oauth_client.register(
        name="google",
        server_metadata_url=discovery_url,
        client_id=client_id,
        client_secret=client_secret,
        client_kwargs={"scope": "openid email profile"},
    )


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


def configure_coverage(app):
    """Setup coverage related extensions."""
    # setup chanjo report
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True if app.debug else False
    if chanjo_api:
        chanjo_api.init_app(app)
        configure_template_filters(app)
        # register chanjo report blueprint
        app.register_blueprint(report_bp, url_prefix="/reports")

    babel = Babel()

    def get_locale():
        """Determine locale to use for translations."""
        accept_languages = current_app.config.get("ACCEPT_LANGUAGES", ["en"])

        # first check request args
        session_language = Markup.escape(request.args.get("lang"))
        if session_language in accept_languages:
            current_app.logger.info("using session language: %s", session_language)
            return session_language

        # language can be forced in config
        user_language = current_app.config.get("REPORT_LANGUAGE")
        if user_language:
            return user_language

        # try to guess the language from the user accept header that
        # the browser transmits.  We support de/fr/en in this example.
        # The best match wins.
        return request.accept_languages.best_match(accept_languages)

    babel.init_app(app, locale_selector=get_locale)
