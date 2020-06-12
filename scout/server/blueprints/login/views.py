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
from flask_ldap3_login.forms import LDAPLoginForm
from flask_ldap3_login import AuthenticationResponseStatus

from scout.server.extensions import login_manager, store, ldap_manager, google_client
from scout.server.utils import public_endpoint
from . import controllers
from .models import LoginUser, LdapUser

import requests
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
            flash("username-password combination is not valid, plase try again", "warning")
            return redirect(url_for("public.index"))
        user_id = form.username.data

    if current_app.config.get("GOOGLE"):
        if session.get("email"):
            user_mail = session["email"]
            session.pop("email")
        else:
            LOG.info("Google Login!")
            google_config = current_app.config["GOOGLE"]
            google_login(google_config["client_id"], google_config["client_secret"])

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


def get_google_provider_cfg():
    """Return the Google discovery URL stored in the app settings"""
    discovery_url = current_app.config["GOOGLE"].get("discovery_url")
    if discovery_url is not None:
        return requests.get(discovery_url).json()


def google_login(client_id, client_secret):
    """Login user via Google OAuth2

    Args:
        client_id(str): Google client id
        client_secret(str): Google client secret

    """
    google_provider_cfg = get_google_provider_cfg()
    auth_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    redirect_url = request.base_url + "/oauth2callback"
    LOG.info(f"CALLBACK URL IS---------------->{redirect_url}")
    request_uri = google_client.prepare_request_uri(
        auth_endpoint, redirect_uri=redirect_url, scope=["openid", "email", "profile"],
    )
    LOG.info(f"REQUEST URL is---------------->{request_uri}")
    return redirect(request_uri)  # google login interface


@login_bp.route("/oauth2callback'")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = google_client.prepare_token_request(
        token_endpoint, authorization_response=request.url, redirect_url=request.base_url, code=code
    )
    token_response = requests.post(
        token_url, headers=headers, data=body, auth=(client_id, client_secret),
    )

    # Parse the tokens
    google_client.parse_request_body_response(json.dumps(token_response.json()))

    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified") is None:
        return "User email not available or not verified by Google.", 400

    session["email"] = userinfo_response.json()["email"].lower()
    session["name"] = userinfo_response.json()["given_name"]
    session["locale"] = userinfo_response.json()["locale"]

    return redirect(url_for("login.login"))


@login_bp.route("/logout")
def logout():
    logout_user()
    flash("you logged out", "success")
    return redirect(url_for("public.index"))


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
    flash("sorry, you could not log in", "warning")
    return redirect(url_for("public.index"))


@ldap_manager.save_user
def save_user(dn, username, data, memberships):
    user = LdapUser(dn, username, data)
    ldap_users[dn] = user
    return user
