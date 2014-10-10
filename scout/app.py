# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from __future__ import absolute_import, unicode_literals
import os

from bson import ObjectId
from flask import Flask, render_template, request
from flask.ext.babel import Babel
from flask.ext.admin.contrib.mongoengine import ModelView
from path import path

from .admin import UserView
from .blueprints.core import core
from .blueprints.frontend import frontend
from .blueprints.login import login
from .config import DefaultConfig
from .database import User, Institute, Role
from .extensions import admin, db, debug_toolbar, login_manager, oauth
from .utils import pretty_date

DEFAULT_BLUEPRINTS = (frontend, login, core)


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


def configure_extensions(app):
  # Flask-Admin
  admin.init_app(app)

  admin.add_view(UserView(User, category='Users'))
  admin.add_view(ModelView(Institute, category='Users'))
  admin.add_view(ModelView(Role, category='Users'))

  # Flask-MongoEngine
  db.init_app(app)

  # Flask-OAuthlib
  oauth.init_app(app)

  # Flask-DebugToolsbar
  debug_toolbar.init_app(app)

  # Flask-Login
  # create user loader function
  @login_manager.user_loader
  def load_user(user_id):
    """Returns the currently active user as an object.

    ============ LEGACY ==================
    Since this app doesn't handle passwords etc. there isn't as much
    incentive to keep pinging the database for every request protected
    by 'login_required'.

    Instead I set the expiration for the session cookie to expire at
    regular intervals.
    """
    return User.objects.get(id=ObjectId(user_id))

  login_manager.login_view = 'login.index'
  login_manager.login_message = 'Please log in to access this page.'
  login_manager.refresh_view = 'login.reauth'

  login_manager.init_app(app)

  # Flask-babel
  babel = Babel(app)

  @babel.localeselector
  def get_locale():
    accept_languages = app.config.get('ACCEPT_LANGUAGES')

    # try to guess the language from the user accept header that
    # the browser transmits.  We support de/fr/en in this example.
    # The best match wins.
    return request.accept_languages.best_match(accept_languages)


def configure_blueprints(app, blueprints):
  """Configure blueprints in views."""

  for blueprint in blueprints:
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
