# -*- coding: utf-8 -*-

from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension()

from flask_bootstrap import Bootstrap
bootstrap = Bootstrap()

from scout.adapter import MongoAdapter
from flask_pymongo import PyMongo
mongo = PyMongo()
store = MongoAdapter()
