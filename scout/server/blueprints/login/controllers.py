import logging
from datetime import datetime
from typing import Optional

import requests
from flask import Response, current_app, flash, redirect, session, url_for
from flask_login import login_user

from scout.server.extensions import ldap_manager, oauth_client, store

from .models import LoginUser

LOG = logging.getLogger(__name__)


def ldap_authorized(userid: str, password: str) -> bool:
    """Log in an LDAP user."""
    authorized = False
    try:
        authorized = ldap_manager.authenticate(
            username=userid,
            password=password,
            base_dn=current_app.config.get("LDAP_BASE_DN") or current_app.config.get("LDAP_BINDDN"),
            attribute=current_app.config.get("LDAP_USER_LOGIN_ATTR")
            or current_app.config.get("LDAP_SEARCH_ATTR"),
        )
    except Exception as ex:
        flash(ex, "danger")

    return authorized


def event_rank(count):
    """Determine event ranking."""
    if count < 100:
        return "aspirant"
    if count < 1000:
        return "constable"
    if count < 4000:
        return "sergeant"
    if count < 12000:
        return "inspector"
    if count < 30000:
        return "superintendent"
    if count < 50000:
        return "commander"
    return "commissioner"


def users(store):
    """Display a list of all users and which institutes they belong to."""
    user_objs = list(store.users())
    for user_obj in user_objs:
        user_institutes = user_obj.get("institutes")
        if user_institutes:
            user_obj["institutes"] = [store.institute(inst_id) for inst_id in user_institutes]
        else:
            user_obj["institutes"] = []
        user_obj["events"] = sum([1 for event in store.user_events(user_obj)])
        user_obj["events_rank"] = event_rank(user_obj["events"])
    return dict(
        users=sorted(user_objs, key=lambda user: -user["events"]),
    )


def user_has_consented(user_consent: Optional[str]) -> bool:
    """Check if user has given consent for activity logging."""
    if not current_app.config.get("USERS_ACTIVITY_LOG_PATH"):
        return True

    if user_consent is None and "consent_given" not in session:
        flash(
            "Logging user activity is a requirement for using this site and accessing your account. Without consent to activity logging, you will not be able to log in into Scout.",
            "warning",
        )
        return False
    return True


def ldap_login(ldap_user: Optional[str], ldap_password: Optional[str]) -> Optional[str]:
    """Authenticate user via LDAP and return user ID if authorized."""

    if not ldap_user or not ldap_password:
        return None

    authorized: bool = ldap_authorized(ldap_user, ldap_password)

    if authorized:
        return ldap_user

    flash("User not authorized by LDAP server", "warning")


def google_login() -> Optional[Response]:
    """Authenticate user via Google OIDC and redirect to the redirect URI. The name of this endpoint should be present on the Google login settings."""
    if "email" in session:
        return redirect(url_for("public.login"))  # Redirect to the login route with session info

    redirect_uri: str = url_for("login.authorized", _external=True)
    try:
        return oauth_client.google.authorize_redirect(redirect_uri)
    except Exception:
        flash("An error has occurred while logging in user using Google OAuth", "warning")
        return None


def keycloak_login() -> Optional[Response]:
    """Authenticate user via Keycloak OIDC and redirect to the redirect URI. The name of this endpoint should be present on the Keycloak login settings."""

    redirect_uri: str = url_for("login.authorized", _external=True)
    try:
        return oauth_client.keycloak.authorize_redirect(redirect_uri)
    except Exception:
        flash("An error has occurred while logging in user using Keycloak", "warning")
        return None


def database_login(user_mail: Optional[str]) -> Optional[str]:
    """Authenticate user against the Scout database and return email if successful."""
    return user_mail


def validate_and_login_user(user_mail: Optional[str], user_id: Optional[str]) -> Response:
    """Validate user in Scout database and log them in."""
    user_obj: Optional[dict] = store.user(email=user_mail, user_id=user_id)

    if user_obj is None:
        flash("User not found in Scout database", "warning")
        session.pop("email", None)
        return redirect(url_for("public.index"))

    user_obj["accessed_at"] = datetime.now()

    if session.get("name"):  # Set name & locale if available (Google Auth)
        user_obj["name"] = session.get("name")
        user_obj["locale"] = session.get("locale")

    store.update_user(user_obj)
    return perform_flask_login(LoginUser(user_obj))


def perform_flask_login(user_dict: "LoginUser") -> Response:
    """Login user using Flask-Login."""
    if login_user(user_dict, remember=True):
        flash(f"Welcome {user_dict.name}", "success")
        return redirect(url_for("cases.index"))

    flash("Sorry, you could not log in", "warning")
    return redirect(url_for("public.index"))


def logout_oidc_user(session, provider: str):
    """Log out a user from an OIDC login provider-"""
    logout_url = current_app.config[provider].get("logout_url")
    if not logout_url or not session.get("token_response"):
        return
    refresh_token = session["token_response"]["refresh_token"]
    requests.post(
        logout_url,
        data={
            "client_id": current_app.config[provider]["client_id"],
            "client_secret": current_app.config[provider]["client_secret"],
            "refresh_token": refresh_token,
        },
    )
