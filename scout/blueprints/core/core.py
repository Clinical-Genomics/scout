# -*- coding: utf-8 -*-
from .views import core


def init_blueprint(app):
  # backend adapter
  app.db = app.config['DB'](app)

  return core
