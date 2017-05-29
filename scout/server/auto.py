# -*- coding: utf-8 -*-
import os

from werkzeug.contrib.fixers import ProxyFix

from .app import create_app

app = create_app(os.environ['SCOUT_CONFIG'])

app.wsgi_app = ProxyFix(app.wsgi_app)
