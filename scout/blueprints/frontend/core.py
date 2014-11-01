# -*- coding: utf-8 -*-
from .views import frontend


def init_blueprint(app=None):
  """Initialize and return the Frontend blueprint.

  The frontend doesn't have any plugin dependencies.

  Args:
    app (Flask, optional): Flask app instance

  Returns:
    Blueprint: Flask blueprint instance
  """
  return frontend
