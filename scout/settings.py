# -*- coding: utf-8 -*-
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

  REPORT_LANGUAGE = 'en'
  ACCEPT_LANGUAGES = ['en', 'sv']

  BLUEPRINTS = [('scout.core.core', None),
                ('scout.frontend.frontend', None),
                ('scout.login.login', None),
                ('scout.user.user', None),
                ('scout.api.api', None),
                ('scout.browser.browser', None),
                ('scout.pileup.pileup_bp', None),
                ('chanjo_report.server.blueprints.report_bp', '/reports')]

  EXTENSIONS = ['scout.extensions.store',
                'scout.extensions.toolbar',
                'scout.extensions.admin',
                'scout.extensions.db',
                'scout.extensions.oauth',
                'scout.extensions.login_manager',
                'scout.extensions.ssl',
                'scout.extensions.markdown',
                'scout.extensions.mail',
                'scout.extensions.omim',
                'scout.extensions.babel',
                'chanjo_report.server.extensions.api']

  # settings for triggering opening of research mode
  RESEARCH_MODE_RECIPIENT = 'example@domain.com'

  CHANJO_URI = 'sqlite:////vagrant/DEV/coverage.sqlite3'

  # default to storing logs under instance folder
  LOG_FOLDER = os.path.abspath('./instance/logs')

  # recipients of error log emails
  ADMINS = ['yourmail@gmail.com']

  # time zone setting
  TIME_ZONE = 'Europe/Stockholm'


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
