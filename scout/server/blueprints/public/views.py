# -*- coding: utf-8 -*-
import logging

from flask import (
    abort,
    Blueprint,
    current_app,
    redirect,
    render_template,
    send_from_directory,
    url_for,
)
from flask_ldap3_login.forms import LDAPLoginForm

from scout import __version__
from scout.server.utils import public_endpoint

LOG = logging.getLogger(__name__)

public_bp = Blueprint(
    "public",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/public/static",
)


@public_bp.route("/")
@public_endpoint
def index():
    """Show the static landing page."""
    form = None
    if current_app.config.get("LDAP_HOST"):
        form = LDAPLoginForm()

    badge_name = current_app.config.get("ACCREDITATION_BADGE")
    return render_template(
        "public/index.html", version=__version__, form=form, accred_badge=badge_name
    )


@public_bp.route("/favicon")
def favicon():
    return send_from_directory(current_app.static_folder, "favicon.ico")
