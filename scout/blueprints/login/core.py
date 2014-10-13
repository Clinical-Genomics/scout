# -*- coding: utf-8 -*-
from bson import ObjectId

from .views import login
from .extensions import login_manager, oauth
from ..admin import User


def init_blueprint(app):
  # Flask-OAuthlib
  oauth.init_app(app)

  # Flask-Login
  # create user loader function
  @login_manager.user_loader
  def load_user(user_id):
    """Returns the currently active user as an object.

    ============ LEGACY ==================
    Since this app doesn't handle passwords etc. there isn't as much
    incentive to keep pinging the database for every request protected
    by 'login_required'.

    Instead I set the expiration for the session cookie to expire at
    regular intervals.
    """
    return User.objects.get(id=ObjectId(user_id))

  login_manager.login_view = 'login.index'
  login_manager.login_message = 'Please log in to access this page.'
  login_manager.refresh_view = 'login.reauth'

  login_manager.init_app(app)

  return login
