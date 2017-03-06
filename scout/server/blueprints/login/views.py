# -*- coding: utf-8 -*-
from flask import Blueprint, flash, redirect, request, session, url_for
from flask_login import login_user, logout_user, login_required

from scout.server.extensions import login_manager, store
from .models import LoginUser

login_bp = Blueprint('login', __name__)


login_manager.login_view = 'login.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_email):
    """Returns the currently active user as an object."""
    user_obj = store.user(user_email)
    user_inst = LoginUser(user_obj) if user_obj else None
    return user_inst


@login_bp.route('/login')
def login():
    """Login a user if they have access."""
    user_email = request.args.get('email')
    user_obj = store.user(user_email)

    if user_obj is None:
        flash("email not whitelisted: {}".format(user_email), 'warning')
        return redirect(url_for('public.index'))

    user_inst = LoginUser(user_obj)
    if login_user(user_inst, remember=True):
        flash("you logged in as: {}".format(user_email), 'success')
        return redirect(request.args.get('next') or url_for('cases.index'))
    else:
        flash('sorry, you could not log in', 'warning')
        return redirect(url_for('public.index'))


@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('you logged out', 'success')
    return redirect(url_for('public.index'))
