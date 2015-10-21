# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from bson import ObjectId
from flask import (
  abort,
  Blueprint,
  current_app,
  flash,
  redirect,
  request,
  session,
  url_for
)
from flask.ext.login import (
  confirm_login, login_required, login_user, logout_user)
from flask_oauthlib.client import OAuthException
from mongoengine.queryset import DoesNotExist

from ..extensions import google, login_manager
from ..models import User, Whitelist, AnonymousUser


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
    return User.objects.get(id=ObjectId(user_id))
  except DoesNotExist:
    return None


@login.route('/login')
def signin():
  callback_url = url_for('.authorized', _external=True)
  return google.authorize(callback=callback_url)


@login.route('/reauth')
@login_required
def reauth():
  if confirm_login():
    flash('Reauthenticated', 'success')

  return redirect(
    request.args.get('next') or request.referrer or url_for('frontend.index'))


@login.route('/logout', methods=['POST'])
@login_required
def logout():
  logout_user()
  session.pop('google_token', None)
  flash('Logged out', 'success')

  return redirect(url_for('frontend.index'))


@login.route('/authorized')
@google.authorized_handler
def authorized(oauth_response):

  if oauth_response is None:
    flash("Access denied: reason=%s error=%s" % (
      request.args['error_reason'],
      request.args['error_description']
    ))

    return abort(403)

  elif isinstance(oauth_response, OAuthException):
    current_app.logger.warning(oauth_response.message)
    flash("%s - try again!" % oauth_response.message)
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

  # get or create user from the database
  user, was_created = User.objects.get_or_create(
    email = google_data['email'],
    name = google_data['name']
  )

  if was_created:
    user.created_at = datetime.utcnow()
    user.location = google_data['locale']

    # add a default institute if it is specified
    if faux_user.institutes:
      user.institutes = faux_user.institutes

    user.save()

  if login_user(user, remember=True):
    user.accessed_at = datetime.utcnow()
    user.save()
    flash('Logged in', 'success')

    return redirect(request.args.get('next') or url_for('frontend.index'))

  flash('Sorry, you could not log in', 'warning')
  return redirect('frontend.index')
