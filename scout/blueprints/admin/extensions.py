# -*- coding: utf-8 -*-

# +--------------------------------------------------------------------+
# | Flask-Admin
# +--------------------------------------------------------------------+
from flask.ext.admin import Admin
from .views import AdminView
admin = Admin(name='Scout', index_view=AdminView())

# +--------------------------------------------------------------------+
# | Flask-MongoEngine
# +--------------------------------------------------------------------+
from flask.ext.mongoengine import MongoEngine
db = MongoEngine()
