#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from werkzeug.contrib.fixers import ProxyFix

from scout.app import AppFactory

factory = AppFactory()
app = factory(config=os.path.abspath('./instance/prod.cfg'))

app.wsgi_app = ProxyFix(app.wsgi_app)


if __name__ == '__main__':
  app.run(host='0.0.0.0')
