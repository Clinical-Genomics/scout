# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os

from .ext.backend import FixtureAdapter


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

  # Flask-DebugToolbar
  DEBUG_TB_ENABLED = False              # disable debug toolbar
  DEBUG_TB_INTERCEPT_REDIRECTS = False
  DEBUG_TB_PANELS = [
    'flask_debugtoolbar.panels.versions.VersionDebugPanel',
    'flask_debugtoolbar.panels.timer.TimerDebugPanel',
    'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
    'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
    'flask_debugtoolbar.panels.template.TemplateDebugPanel',
    'flask_debugtoolbar.panels.logger.LoggingPanel',
    'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
    # add the MongoDB panel
    'flask.ext.mongoengine.panels.MongoDebugPanel',
  ]

  # Flask-MongoEngine
  MONGODB_SETTINGS = {'DB': 'testing'}


class DefaultConfig(BaseConfig):
  """docstring for DefaultConfig"""
  DEBUG = True

  # Flask-cache: http://pythonhosted.org/Flask-Cache/
  CACHE_TYPE = 'simple'
  CACHE_DEFAULT_TIMEOUT = 60

  # Flask-babel: http://pythonhosted.org/Flask-Babel/
  ACCEPT_LANGUAGES = ['en', 'sv']
  BABEL_DEFAULT_LOCALE = 'en'

  # Flask-DebugToolbar
  DEBUG_TB_ENABLED = True

  # Session lifespan
  SESSION_DAYS = 30

  DB = FixtureAdapter


class TestConfig(BaseConfig):
  """docstring for TestConfig"""
  TESTING = True
  DEBUG = True
