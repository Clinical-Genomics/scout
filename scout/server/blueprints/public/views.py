# -*- coding: utf-8 -*-
from flask import (
    Blueprint,
    render_template,
    current_app,
    redirect,
    url_for,
    send_from_directory,
)
from flask_ldap3_login.forms import LDAPLoginForm

from scout import __version__
from scout.server.utils import public_endpoint

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
    return render_template("public/index.html", version=__version__, form=form)


@public_bp.route("/favicon")
def favicon():
    return send_from_directory(current_app.static_folder, "favicon.ico")
