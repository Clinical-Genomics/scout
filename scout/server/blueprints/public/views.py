# -*- coding: utf-8 -*-
import logging
from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_login import current_user

from scout import __version__
from scout.server.extensions import store
from scout.server.utils import public_endpoint

from . import controllers

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
    event_list = []
    badge_name = current_app.config.get("ACCREDITATION_BADGE")
    if badge_name and not Path(public_bp.static_folder, badge_name).is_file():
        LOG.warning(f'No file with name "{badge_name}" in {public_bp.static_folder}')
        badge_name = None

    if current_user.is_authenticated:
        event_list = controllers.get_events_of_interest(store, current_user)
    return render_template(
        "public/index.html",
        version=__version__,
        accred_badge=badge_name,
        event_list=event_list,
    )


@public_bp.route("/favicon")
def favicon():
    return send_from_directory(current_app.static_folder, "favicon.ico")
