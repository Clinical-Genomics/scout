# -*- coding: utf-8 -*-
import os

from .app import create_app

app = create_app(os.environ['SCOUT_CONFIG'])
