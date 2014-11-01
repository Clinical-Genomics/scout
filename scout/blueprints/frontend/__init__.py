# -*- coding: utf-8 -*-
"""
The Frontend blueprint takes case of all views that are available
without a login. This includes the landing page and about etc.
"""
from __future__ import absolute_import, unicode_literals

from .core import init_blueprint
from .views import frontend
