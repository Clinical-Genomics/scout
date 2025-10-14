# -*- coding: utf-8 -*-
import logging
from typing import Optional

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, logout_user

from scout.load.user import save_user
from scout.server.blueprints.login.forms import UserForm
from scout.server.extensions import login_manager, oauth_client, store
from scout.server.utils import public_endpoint, refresh_token, safe_redirect_back

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

    elif current_app.config.get("KEYCLOAK"):
        if session.get("email"):
            user_mail = session["email"]
        else:
            return controllers.keycloak_login()

    elif request.form.get("email"):
        user_mail = controllers.database_login(user_mail=request.form.get("email"))

    return controllers.validate_and_login_user(user_mail=user_mail, user_id=user_id)


@login_bp.route("/authorized")
@public_endpoint
def authorized():
    """OIDC callback function."""
    if current_app.config.get("GOOGLE"):
        client = oauth_client.google
    if current_app.config.get("KEYCLOAK"):
        client = oauth_client.keycloak
    token = client.authorize_access_token()
    user = client.parse_id_token(token, None)

    session["email"] = user.get("email").lower()
    session["name"] = user.get("name")
    session["locale"] = user.get("locale")
    session["token_response"] = token

    return redirect(url_for(".login"))


@login_bp.route("/logout")
def logout():

    session.pop("email", None)
    session.pop("name", None)
    session.pop("locale", None)
    session.pop("consent_given", None)

    logout_user()  # logs out user from scout
    for provider in ["GOOGLE", "KEYCLOAK"]:
        if current_app.config.get(provider):
            controllers.logout_oidc_user(session, provider)
    flash("you logged out", "success")
    return redirect(url_for("public.index"))


@login_bp.route("/users")
def users():
    """Show all users in the system."""
    data = controllers.users(store)
    return render_template("login/users.html", **data)


@login_bp.route("/remove_user/<email>", methods=["GET"])
def remove_user(email):
    """Remove a user from the database."""
    if not current_user.is_admin:
        flash("You are not authorized to remove user accounts.", "warning")
        return safe_redirect_back(request)

    user_obj = store.user(email)
    if not user_obj:
        flash(f"User {email} not found in the database", "warning")
        return safe_redirect_back(request)

    if store.user_mme_submissions(user_obj):
        flash(
            f"User {email} has associated Matchmaker Exchange submissions "
            "and can only be removed from the CLI.",
            "warning",
        )
        return safe_redirect_back(request)

    for case_obj in store.cases(assignee=email):
        institute_obj = store.institute(case_obj["owner"])
        inactivate_case = case_obj.get("status", "active") == "active" and case_obj[
            "assignees"
        ] == [email]
        store.unassign(
            institute_obj,
            case_obj,
            user_obj,
            url_for(
                "cases.case",
                institute_id=case_obj["owner"],
                case_name=case_obj["display_name"],
            ),
            inactivate_case,
        )

    store.delete_user(email)
    LOG.warning(f"Removed user {user_obj['email']} from database and from case assignees.")
    return safe_redirect_back(request)


@login_bp.route("/add_user", methods=["POST"])
def add_user():
    """Save a new user in the database and redirect to users page."""
    if current_user.is_admin is False:
        flash("You are not authorized to create a new user.", "warning")
        return safe_redirect_back(request)

    form = UserForm()
    if form.validate_on_submit():
        user_info = {
            "email": form.email.data,
            "name": form.name.data,
            "roles": form.role.data,
            "institutes": form.institute.data,
            "id": form.user_id.data,
        }

        try:
            save_user(user_info=user_info)
            flash("New user successfully saved to the database", "success")

        except Exception:
            flash("An error occurred while creating user.", "warning")

    else:
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                LOG.warning(f"Error in {field_name}: {error}")

    return safe_redirect_back(request)


@login_bp.route("/edit_user/<email>", methods=["GET", "POST"])
def edit_user(email):
    if current_user.is_admin is False:
        flash("Unauthorized", "warning")
        return redirect(url_for("login.users"))

    edit_user = store.user(email)
    if not edit_user:
        flash("User not found", "danger")
        return safe_redirect_back(request)

    form = UserForm()
    if form.validate_on_submit():
        user_info = {
            "email": email,
            "name": form.name.data,
            "roles": form.role.data,
            "institutes": form.institute.data,
            "_id": edit_user["_id"],
        }
        try:
            store.update_user(user_obj=user_info)
            flash(f"User successfully updated", "success")
        except Exception as ex:
            flash(f"An error occurred while updating user:{ex}.", "warning")

        return redirect(url_for("login.users"))

    data = controllers.users(store)
    return render_template("login/users.html", edit_user=edit_user, **data)


@login_bp.route("/refresh_token", methods=["POST"])
def refresh_token_endpoint() -> dict:
    """Refresh the login token and return the updated ID token.

    This endpoint is used for Chanjo2 reports,
    ensuring that the ID token is always fresh.
    """
    refresh_token()  # your existing refresh function
    token_response = session.get("token_response", {})
    id_token = token_response.get("id_token")
    return {"id_token": id_token}
