# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask.ext.admin.contrib.mongoengine import ModelView

from .extensions import admin, db
from .models import Institute, Role, User
from .views import UserView


def init_blueprint(app):
  # Flask-Admin
  admin.init_app(app)

  admin.add_view(UserView(User, category='Users'))
  admin.add_view(ModelView(Institute, category='Users'))
  admin.add_view(ModelView(Role, category='Users'))

  # Flask-MongoEngine
  db.init_app(app)

  return None
