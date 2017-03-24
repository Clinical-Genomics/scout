# -*- coding: utf-8 -*-
import os

from livereload import Server

from scout.server.app import create_app

app = create_app(config_file=os.environ['SCOUT_CONFIG'])
app.debug = True
server = Server(app.wsgi_app)
server.serve()
