# -*- coding: utf-8 -*-
import coloredlogs
from flask import Flask, redirect, request, url_for
from flask_login import current_user
from flaskext.markdown import Markdown

try:
    from chanjo_report.server.app import configure_template_filters
    from chanjo_report.server.blueprints import report_bp
    from chanjo_report.server.extensions import api as chanjo_api
except ImportError:
    report_bp = None
    configure_template_filters = None
    print('chanjo report not installed!')

from . import extensions
from .blueprints import public, genes, cases, login, variants, panels, pileup


def create_app(config_file=None, config=None):
    """Flask app factory function."""
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    if config_file:
        app.config.from_pyfile(config_file)
    if config:
        app.config.update(config)

    coloredlogs.install(level='DEBUG' if app.debug else 'INFO')
    configure_extensions(app)
    register_blueprints(app)
    register_filters(app)

    @app.before_request
    def check_user():
        if request.endpoint:
            # check if the endpoint requires authentication
            static_endpoint = 'static' in request.endpoint
            public_endpoint = getattr(app.view_functions[request.endpoint],
                                      'is_public', False)
            relevant_endpoint = not (static_endpoint or public_endpoint)
            # if endpoint requires auth, check if user is authenticated
            if relevant_endpoint and not current_user.is_authenticated:
                login_url = url_for('login.login', next=url_for(request.endpoint))
                return redirect(login_url)

    return app


def configure_extensions(app):
    """Configure Flask extensions."""
    extensions.toolbar.init_app(app)
    extensions.bootstrap.init_app(app)
    extensions.mongo.init_app(app)
    extensions.store.init_app(app)
    extensions.login_manager.init_app(app)
    extensions.oauth.init_app(app)
    extensions.mail.init_app(app)
    Markdown(app)

    if app.config.get('SQLALCHEMY_DATABASE_URI'):
        # setup chanjo report
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True if app.debug else False
        chanjo_api.init_app(app)
        configure_template_filters(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.public_bp)
    app.register_blueprint(genes.genes_bp)
    app.register_blueprint(cases.cases_bp)
    app.register_blueprint(login.login_bp)
    app.register_blueprint(variants.variants_bp)
    app.register_blueprint(panels.panels_bp)
    app.register_blueprint(pileup.pileup_bp)

    if app.config.get('SQLALCHEMY_DATABASE_URI'):
        # register chanjo report blueprint
        app.register_blueprint(report_bp, url_prefix='/reports')


def register_filters(app):

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

        if number is None:
            # NaN
            return '-'
        elif number == 0:
            # avoid confusion over what is rounded and what is actually 0
            return 0
        elif number < min_number:
            # make human readable and sane
            return "< {}".format(min_number)
        else:
            # round all other numbers
            return round(number, ndigits)
