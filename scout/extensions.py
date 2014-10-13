# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory
located in app.py
"""
from __future__ import absolute_import, unicode_literals

# +--------------------------------------------------------------------+
# | Flask-DebugToolbar
# +--------------------------------------------------------------------+
from flask.ext.debugtoolbar import DebugToolbarExtension
debug_toolbar = DebugToolbarExtension()
