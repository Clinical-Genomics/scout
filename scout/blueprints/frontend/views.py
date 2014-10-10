# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import Blueprint, current_app, render_template

frontend = Blueprint('frontend', __name__, template_folder='templates')


@frontend.route('/')
def index():
  current_app.logger.debug('debug')

  return render_template('index.html')
