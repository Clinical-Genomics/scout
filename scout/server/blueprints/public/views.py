# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for
#from flask_login import current_user

from scout import __version__

public_bp = Blueprint('public', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/public/static')


@public_bp.route('/')
def index():
    """Show the static landing page.

    Doesn't require a user to login. But if they are logged in, they
    should be passed along to their personalized start page (TODO).
    """
    # if current_user.is_authenticated:
    #     return redirect(url_for('core.institutes'))
    return render_template('public/index.html', version=__version__)
