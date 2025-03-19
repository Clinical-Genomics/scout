# -*- coding: utf-8 -*-
import logging
from typing import Optional

from flask import (
    Blueprint,
    Request,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_user, logout_user

from scout.server.extensions import login_manager, oauth_client, store
from scout.server.utils import public_endpoint

from . import controllers
from .models import LoginUser

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


@login_manager.user_loader
def load_user(user_id):
    """Returns the currently active user as an object."""
    user_obj = store.user(user_id)
    user_inst = LoginUser(user_obj) if user_obj else None
    return user_inst


@login_bp.route("/login", methods=["GET", "POST"])
@public_endpoint
def login() -> Response:
    """Login a user if they have access."""

    if controllers.user_has_consented(user_consent=request.form.get("consent_checkbox")) is False:
        return redirect(url_for("public.index"))

    user_id: Optional[str] = None
    user_mail: Optional[str] = None

    if current_app.config.get("LDAP_HOST", current_app.config.get("LDAP_SERVER")):
        user_id = controllers.ldap_login(
            ldap_user=request.form.get("ldap_user"), ldap_password=request.form.get("ldap_password")
        )
        if user_id is None:
            return redirect(url_for("public.index"))

    elif current_app.config.get("GOOGLE"):
        if session.get("email"):
            user_mail = session["email"]
        else:
            # Redirect to Google OAuth if not completed
            return controllers.google_login()

    elif request.form.get("email"):
        user_mail = request.form.get("email")

    return controllers.validate_and_login_user(user_mail=user_mail, user_id=user_id)


@login_bp.route("/authorized")
@public_endpoint
def authorized():
    """Google auth callback function"""
    token = oauth_client.google.authorize_access_token()
    google_user = oauth_client.google.parse_id_token(token, None)
    session["email"] = google_user.get("email").lower()
    session["name"] = google_user.get("name")
    session["locale"] = google_user.get("locale")

    return redirect(url_for(".login"))


@login_bp.route("/logout")
def logout():
    logout_user()
    session.pop("email", None)
    session.pop("name", None)
    session.pop("locale", None)
    session.pop("consent_given", None)
    flash("you logged out", "success")
    return redirect(url_for("public.index"))


@login_bp.route("/users")
def users():
    """Show all users in the system."""
    data = controllers.users(store)
    return render_template("login/users.html", **data)
