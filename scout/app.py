# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from __future__ import absolute_import, unicode_literals
import os

import arrow
from flask import Flask, render_template
from jinja2 import is_undefined
from werkzeug.utils import import_string

from .settings import DevelopmentConfig


class NoContextProcessorException(Exception):
  """Raise if context processor wasn't found."""
  pass


class NoBlueprintException(Exception):
  """Raise if blueprint wasn't found."""
  pass


class NoExtensionException(Exception):
  """Raise if extension wasn't found."""
  pass

def get_imported_stuff_by_path(path):
  """Helper method to import modules from a string path."""
  module_name, object_name = path.rsplit('.', 1)
  module = import_string(module_name)

  return module, object_name


class AppFactory(object):

  """Create a Flask app (Flask Application Factory)."""

  def __init__(self):
    super(AppFactory, self).__init__()

    self.app_config = None
    self.app = None

  def __call__(self, app_name=None, config=None, config_obj=None, **kwargs):
    # initialize the application
    self.app_config = config
    self.app = Flask(app_name or DevelopmentConfig.PROJECT,
                     instance_relative_config=True,
                     **kwargs)

    self._configure_app(config_obj=config_obj)
    self._bind_extensions()
    self._register_blueprints()
    self._configure_template_filters()
    self._configure_error_handlers()

    return self.app

  def _configure_app(self, config_obj=None):
    """Configure the app in different ways."""
    # http://flask.pocoo.org/docs/api/#configuration
    self.app.config.from_object(config_obj or DevelopmentConfig)

    # user custom config
    # http://flask.pocoo.org/docs/config/#instance-folders
    default_config = os.path.join(self.app.instance_path,
                                  "%s.cfg" % self.app.name)
    self.app.config.from_pyfile(self.app_config or default_config, silent=True)

  def _bind_extensions(self):
    """Bind extensions to the app dynamically."""
    for ext_path in self.app.config.get('EXTENSIONS', []):
      module, object_name = get_imported_stuff_by_path(ext_path)

      if not hasattr(module, object_name):
        raise NoExtensionException("No %s extension found" % object_name)

      extension = getattr(module, object_name)

      if getattr(extension, 'init_app', False):
        extension.init_app(self.app)

      else:
        extension(self.app)

  def _register_blueprints(self):
    """Configure blueprints in views."""
    for blueprint_path in self.app.config.get('BLUEPRINTS', []):
      module, object_name = get_imported_stuff_by_path(blueprint_path)

      if hasattr(module, object_name):
        self.app.register_blueprint(getattr(module, object_name))

      else:
        raise NoBlueprintException("No %s blueprint found" % object_name)

  def _register_context_processors(self):
    """Register extra contexts for Jinja templates."""
    for processor_path in self.app.config.get('CONTEXT_PROCESSORS', []):
      module, object_name = get_imported_stuff_by_path(processor_path)

      if hasattr(module, object_name):
        self.app.context_processor(getattr(module, object_name))

      else:
        raise NoContextProcessorException("No {} context processor found"
                                          .format(object_name))

  def _configure_error_handlers(self):
    """Configure error handlers to the corresponding error pages."""
    @self.app.errorhandler(403)
    def forbidden_page(error):
      """Render the forbidden error page on 403 errors."""
      return render_template('errors/forbidden_page.html', error=error), 403

    @self.app.errorhandler(404)
    def page_not_found(error):
      """Render the page not found page on 404 errors."""
      return render_template('errors/page_not_found.html', error=error), 404

    @self.app.errorhandler(500)
    def server_error_page(error):
      """Render the server error page on 500 errors."""
      return render_template('errors/server_error.html', error=error), 500

  def _configure_template_filters(self):
    """Configure custom Jinja2 template filters."""
    @self.app.template_filter()
    def human_date(value):
      return arrow.get(value).humanize()

    @self.app.template_filter()
    def format_date(value, format="%Y-%m-%d"):
      return value.strftime(format)

    @self.app.template_filter()
    def initials(value):
      parts = value.split(' ')
      letters = (part[0] for part in parts)
      return ''.join(letters)

    @self.app.template_filter()
    def client_filter(value):
      """Pass through variable in Jinja2 to client side template.

      The filter tells Jinja2 that a variable is for a client side
      template engine.

      If the variable is undefined, its name will be used in the
      client side template, otherwise, its content will be used.
      """

      if is_undefined(value):
          return '{{{{{}}}}}'.format(value._undefined_name)
      if type(value) is bool:
          value = repr(value).lower()
      return '{{{{{}}}}}'.format(value)
