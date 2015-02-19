# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os


class BaseConfig(object):
  """docstring for BaseConfig"""
  PROJECT = 'scout'

  APP_DIR = os.path.abspath(os.path.dirname(__file__))  # this directory
  # get app root path (can also use flask_root_path) => ../../config.py
  PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

  DEBUG = False
  TESTING = False

  # http://flask.pocoo.org/docs/quickstart/#sessions
  SECRET_KEY = 'secret key'

  # Flask-MongoEngine
  MONGODB_SETTINGS = {'db': 'testing'}

  # Flask-mail: http://pythonhosted.org/flask-mail/
  # see: https://bitbucket.org/danjac/flask-mail/issue/3
  MAIL_DEBUG = DEBUG
  MAIL_SERVER = 'smtp.gmail.com'
  MAIL_PORT = 587
  MAIL_USE_TLS = True
  MAIL_USE_SSL = False
  # put real MAIL_USERNAME and MAIL_PASSWORD under instance folder
  MAIL_USERNAME = 'yourmail@gmail.com'
  MAIL_PASSWORD = 'yourpass'
  MAIL_DEFAULT_SENDER = MAIL_USERNAME

  BLUEPRINTS = ['scout.core.core',
                'scout.frontend.frontend',
                'scout.login.login',
                'scout.user.user',
                'scout.api.api',
                'scout.browser.browser']

  EXTENSIONS = ['scout.extensions.store',
                'scout.extensions.toolbar',
                'scout.extensions.admin',
                'scout.extensions.db',
                'scout.extensions.oauth',
                'scout.extensions.login_manager',
                'scout.extensions.ssl',
                'scout.extensions.markdown',
                'scout.extensions.mail',
                'scout.extensions.omim']


class DevelopmentConfig(BaseConfig):
  """docstring for DefaultConfig"""
  DEBUG = True

  # Flask-DebugToolbar
  DEBUG_TB_ENABLED = True
  DEBUG_TB_INTERCEPT_REDIRECTS = False
  DEBUG_TB_PANELS = ['flask_debugtoolbar.panels.versions.VersionDebugPanel',
                     'flask_debugtoolbar.panels.timer.TimerDebugPanel',
                     'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
                     'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
                     'flask_debugtoolbar.panels.template.TemplateDebugPanel',
                     'flask_debugtoolbar.panels.logger.LoggingPanel',
                     'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
                     # add the MongoDB panel
                     'flask.ext.mongoengine.panels.MongoDebugPanel']


class TestConfig(BaseConfig):
  """docstring for TestConfig"""
  TESTING = True
  DEBUG = True
