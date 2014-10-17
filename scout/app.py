# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from __future__ import absolute_import, unicode_literals
from datetime import timedelta
import os

from flask import Flask, render_template, request
from flask.ext.babel import Babel
from path import path

from .blueprints import core, frontend
from .config import DefaultConfig
from .extensions import debug_toolbar
from .utils import pretty_date

DEFAULT_BLUEPRINTS = (core, frontend)


def create_app(config=None, app_name=None, blueprints=None):
  """Create a Flask app (Flask Application Factory)."""
  if app_name is None:
    app_name = DefaultConfig.PROJECT

  if blueprints is None:
    blueprints = DEFAULT_BLUEPRINTS

  # rel. instance_path (not root)
  app = Flask(__name__, instance_relative_config=True)

  configure_app(app, config=config)
  configure_hook(app)
  configure_blueprints(app, blueprints)
  configure_extensions(app)
  configure_logging(app)
  configure_template_filters(app)
  configure_error_handlers(app)

  return app


def configure_app(app, config=None):
  """Configure app in different ways."""
  # http://flask.pocoo.org/docs/api/#configuration
  app.config.from_object(DefaultConfig)

  # http://flask.pocoo.org/docs/config/#instance-folders
  default_config = os.path.join(app.instance_path, "%s.cfg" % app.name)
  app.config.from_pyfile(config or default_config, silent=True)

  # set timeout for session - lost after X days with no user interaction
  # +INFO: http://flask.pocoo.org/docs/api/#flask.Flask.permanent_session_lifetime
  app.permanent_session_lifetime = timedelta(days=app.config['SESSION_DAYS'])


def configure_extensions(app):
  # Flask-DebugToolsbar
  debug_toolbar.init_app(app)

  # Flask-babel
  babel = Babel(app)

  @babel.localeselector
  def get_locale():
    accept_languages = app.config.get('ACCEPT_LANGUAGES')

    # try to guess the language from the user accept header that
    # the browser transmits.  We support de/fr/en in this example.
    # The best match wins.
    return request.accept_languages.best_match(accept_languages)


def configure_blueprints(app, blueprint_modules):
  """Configure blueprints in views."""
  # initialize blueprint dependencies like extensions
  blueprints = (module.init_blueprint(app) for module in blueprint_modules)

  # filter out blueprints that don't requrie registration
  only_blueprints = (bp for bp in blueprints if bp is not None)

  for blueprint in only_blueprints:
    app.register_blueprint(blueprint)


def configure_template_filters(app):
  """Configure custom Jinja2 template filters."""

  @app.template_filter()
  def human_date(value):
    return pretty_date(value)

  @app.template_filter()
  def format_date(value, format="%Y-%m-%d"):
    return value.strftime(format)


def configure_logging(app):
  """Configure file(info) and email(error) logging."""

  app.config['LOG_FOLDER'] = os.path.join(app.instance_path, 'logs')
  path(app.config['LOG_FOLDER']).makedirs_p()

  if app.debug or app.testing:
    # skip debug and test mode - just check standard output
    return

  import logging

  # set info level on logger, which might be overwritten by handers
  # suppress DEBUG messages
  app.logger.setLevel(logging.INFO)

  info_log = os.path.join(app.config['LOG_FOLDER'], 'info.log')
  info_file_handler = logging.handlers.RotatingFileHandler(
    info_log, maxBytes=100000, backupCount=10)
  info_file_handler.setLevel(logging.INFO)
  info_file_handler.setFormatter(
    logging.Formatter(
      "%(asctime)s %(levelname)s: %(message)s "
      "[in %(pathname)s:%(lineno)d]"
    )
  )
  app.logger.addHandler(info_file_handler)


def configure_hook(app):
  @app.before_request
  def before_request():
    pass


def configure_error_handlers(app):

  @app.errorhandler(403)
  def forbidden_page(error):
    return render_template('errors/forbidden_page.html'), 403

  @app.errorhandler(404)
  def page_not_found(error):
    return render_template('errors/page_not_found.html'), 404

  @app.errorhandler(500)
  def server_error_page(error):
    return render_template('errors/server_error.html'), 500
