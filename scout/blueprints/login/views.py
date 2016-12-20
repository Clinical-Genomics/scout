# -*- coding: utf-8 -*-
from bson import ObjectId
from flask import (abort, Blueprint, current_app, flash, redirect, request,
                   session, url_for)
from flask_login import confirm_login, login_required, login_user, logout_user
from flask_oauthlib.client import OAuthException
from mongoengine.queryset import DoesNotExist

from scout.extensions import google, login_manager, store
from scout.models import User, Whitelist, AnonymousUser


login = Blueprint('login', __name__, template_folder='templates')


@google.tokengetter
def get_google_token():
    """Returns a tuple of Google tokens, if they exist"""
    return session.get('google_token')


login_manager.login_view = 'login.signin'
login_manager.login_message = 'Please log in to access this page.'
login_manager.refresh_view = 'login.reauth'
login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    """Returns the currently active user as an object."""
    try:
        if not isinstance(user_id, str):
            user_id = user_id.decode('utf-8')
        return User.objects.get(id=ObjectId(user_id))
    except DoesNotExist:
        return None


@login.route('/login')
def signin():
    if current_app.config.get('LOGIN_DISABLED'):
        fake_user = User.objects(email='paul.anderson@magnolia.com').first()
        if fake_user and login_user(fake_user, remember=True):
            return redirect(url_for('core.institutes'))

    callback_url = url_for('.authorized', _external=True)
    return google.authorize(callback=callback_url)


@login.route('/reauth')
@login_required
def reauth():
    if confirm_login():
        flash('Reauthenticated', 'success')
    return redirect(request.args.get('next') or request.referrer or
                    url_for('core.institutes'))


@login.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'success')
    return redirect(url_for('frontend.index'))


@login.route('/authorized')
@google.authorized_handler
def authorized(oauth_response):
    if oauth_response is None:
        flash("Access denied: reason={} error={}"
              .format(request.args['error_reason'],
                      request.args['error_description']))
        return abort(403)

    elif isinstance(oauth_response, OAuthException):
        current_app.logger.warning(oauth_response.message)
        flash("{} - try again!".format(oauth_response.message))
        return redirect(url_for('frontend.index'))

    # add token to session, do it before validation to be able to fetch
    # additional data (like email) on the authenticated user
    session['google_token'] = (oauth_response['access_token'], '')

    # get additional user info with the access token
    google_user = google.get('userinfo')
    google_data = google_user.data

    # match email against whitelist before completing sign up
    try:
        faux_user = Whitelist.objects.get(email=google_data['email'])
    except DoesNotExist:
        flash('Your email is not on the whitelist, contact an admin.')
        return abort(403)

    user_obj = store.getoradd_user(google_data['email'], google_data['name'],
                                   location=google_data['locale'],
                                   institutes=faux_user.institutes)

    if login_user(user_obj, remember=True):
        store.update_access(user_obj)
        flash('Logged in', 'success')
        return redirect(request.args.get('next') or url_for('core.institutes'))

    flash('Sorry, you could not log in', 'warning')
    return redirect(url_for('frontend.index'))
