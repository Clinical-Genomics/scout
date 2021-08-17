# -*- coding: utf-8 -*-
import logging
from pathlib import Path

from flask import Blueprint, current_app, render_template, send_from_directory
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
    if badge_name and not Path(public_bp.static_folder, badge_name).is_file():
        LOG.warning(f'No file with name "{badge_name}" in {public_bp.static_folder}')
        badge_name = None

    return render_template(
        "public/index.html", version=__version__, form=form, accred_badge=badge_name
    )


@public_bp.route("/favicon")
def favicon():
    return send_from_directory(current_app.static_folder, "favicon.ico")
