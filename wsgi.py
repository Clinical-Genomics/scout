#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from werkzeug.contrib.fixers import ProxyFix

from scout.server.app import create_app

app = create_app(config_file=os.environ['SCOUT_CONFIG'])

app.wsgi_app = ProxyFix(app.wsgi_app)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
