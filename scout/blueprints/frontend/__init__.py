# -*- coding: utf-8 -*-
"""
The Frontend blueprint takes care of all views that are available
without a login. This currently only includes the landing page.
"""
from __future__ import absolute_import, unicode_literals

from .core import init_blueprint
from .views import frontend
