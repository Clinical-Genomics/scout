# -*- coding: utf-8 -*-
from datetime import datetime

from flask import (abort, current_app, Blueprint, flash, redirect, request,
                   session, url_for)
from flask_login import login_user, logout_user
from flask_oauthlib.client import OAuthException

from scout.server.extensions import google, login_manager, oauth, store
from scout.server.utils import public_endpoint
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


@google.tokengetter
def get_google_token():
    """Returns a tuple of Google tokens, if they exist"""
    return session.get('google_token')


@login_bp.route('/login')
@public_endpoint
def login():
    """Login a user if they have access."""
    if current_app.config.get('GOOGLE'):
        callback_url = url_for('.authorized', _external=True)
        next_url = request.args.get('next')
        return google.authorize(callback=callback_url, next=next_url)

    user_email = request.args.get('email')
    user_obj = store.user(user_email)

    if user_obj is None:
        flash("email not whitelisted: {}".format(user_email), 'warning')
        return redirect(url_for('public.index'))

    return perform_login(user_obj)


@login_bp.route('/logout')
def logout():
    logout_user()
    flash('you logged out', 'success')
    return redirect(url_for('public.index'))


@login_bp.route('/authorized')
@public_endpoint
def authorized():
    oauth_response = google.authorized_response()
    if oauth_response is None:
        flash("Access denied: reason={} error={}"
              .format(request.args['error_reason'],
                      request.args['error_description']), 'danger')
        return abort(403)

    elif isinstance(oauth_response, OAuthException):
        current_app.logger.warn(oauth_response.message)
        flash("{} - try again!".format(oauth_response.message), 'warning')
        return redirect(url_for('public.index'))

    # add token to session, do it before validation to be able to fetch
    # additional data (like email) on the authenticated user
    session['google_token'] = (oauth_response['access_token'], '')

    # get additional user info with the access token
    google_user = google.get('userinfo')
    google_data = google_user.data

    user_obj = store.user(google_data['email'])
    if user_obj is None:
        flash('your email is not whitelisted, contact admin.', 'warning')
        return redirect(url_for('public.index'))

    user_obj['name'] = google_data['name']
    user_obj['location'] = google_data['locale']
    user_obj['accessed_at'] = datetime.now()
    store.update_user(user_obj)
    return perform_login(user_obj)


def perform_login(user_dict):
    user_inst = LoginUser(user_dict)
    if login_user(user_inst, remember=True):
        flash("you logged in as: {}".format(user_inst.email), 'success')
        return redirect(request.args.get('next') or url_for('cases.index'))
    else:
        flash('sorry, you could not log in', 'warning')
        return redirect(url_for('public.index'))
