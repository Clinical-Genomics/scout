# -*- coding: utf-8 -*-
from datetime import datetime

from flask import (
    abort,
    current_app,
    Blueprint,
    flash,
    redirect,
    request,
    session,
    url_for,
    render_template,
)
from flask_login import login_user, logout_user
from flask_oauthlib.client import OAuthException
from flask_ldap3_login.forms import LDAPLoginForm
from flask_ldap3_login import AuthenticationResponseStatus

from scout.server.extensions import google, login_manager, store, ldap_manager
from scout.server.utils import public_endpoint
from . import controllers
from .models import LoginUser, LdapUser

import logging

LOG = logging.getLogger(__name__)

login_bp = Blueprint(
    "login",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/login/static",
)

login_manager.login_view = "login.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

ldap_users = {}  # used by ldap save_user


@login_manager.user_loader
def load_user(user_id):
    """Returns the currently active user as an object."""
    user_obj = store.user(user_id)
    user_inst = LoginUser(user_obj) if user_obj else None
    return user_inst


@google.tokengetter
def get_google_token():
    """Returns a tuple of Google tokens, if they exist"""
    return session.get("google_token")


@login_bp.route("/login", methods=["GET", "POST"])
@public_endpoint
def login():
    """Login a user if they have access."""
    if "next" in request.args:
        session["next_url"] = request.args["next"]

    user_id = None
    user_mail = None
    if current_app.config.get("LDAP_HOST") and request.method == "POST":
        form = LDAPLoginForm()
        LOG.info("Validating LDAP user")
        if not form.validate_on_submit():
            flash(
                "username-password combination is not valid, plase try again", "warning"
            )
            return redirect(url_for("public.index"))
        user_id = form.username.data

    if current_app.config.get("GOOGLE"):
        if session.get("email"):
            user_mail = session["email"]
            session.pop("email")
        else:
            LOG.info("Validating Google user login")
            callback_url = url_for(".authorized", _external=True)
            return google.authorize(callback=callback_url)

    if request.args.get("email"):  # log in against Scout database
        user_mail = request.args.get("email")
        LOG.info("Validating user {} against Scout database".format(user_id))

    user_obj = store.user(email=user_mail, user_id=user_id)
    if user_obj is None:
        flash("User not whitelisted", "warning")
        return redirect(url_for("public.index"))

    user_obj["accessed_at"] = datetime.now()
    if session.get("name"):  # These args come from google auth
        user_obj["name"] = session.get("name")
        user_obj["locale"] = session.get("locale")
    store.update_user(user_obj)

    user_dict = LoginUser(user_obj)
    return perform_login(user_dict)


@login_bp.route("/logout")
def logout():
    logout_user()
    flash("you logged out", "success")
    return redirect(url_for("public.index"))


@login_bp.route("/authorized")
@public_endpoint
def authorized():
    oauth_response = None
    try:
        oauth_response = google.authorized_response()
    except OAuthException as error:
        current_app.logger.warning("Google OAuthException: {}".format(error))
        flash("{} - try again!".format(error), "warning")
        return redirect(url_for("public.index"))

    if oauth_response is None:
        flash(
            "Access denied: reason={} error={}".format(
                request.args.get["error_reason"], request.args["error_description"]
            ),
            "danger",
        )
        return redirect(url_for("public.index"))

    # add token to session, do it before validation to be able to fetch
    # additional data (like email) on the authenticated user
    session["google_token"] = (oauth_response["access_token"], "")

    # get additional user info with the access token
    google_user = google.get("userinfo")
    google_data = google_user.data

    session["email"] = google_data["email"].lower()
    session["name"] = google_data["name"]
    session["locale"] = google_data["locale"]

    return redirect(url_for("login.login"))


@login_bp.route("/users")
def users():
    """Show all users in the system."""
    data = controllers.users(store)
    return render_template("login/users.html", **data)


def perform_login(user_dict):
    if login_user(user_dict, remember=True):
        flash("you logged in as: {}".format(user_dict.name), "success")
        next_url = session.pop("next_url", None)
        return redirect(request.args.get("next") or next_url or url_for("cases.index"))
    else:
        flash("sorry, you could not log in", "warning")
        return redirect(url_for("public.index"))


@ldap_manager.save_user
def save_user(dn, username, data, memberships):
    user = LdapUser(dn, username, data)
    ldap_users[dn] = user
    return user
