import logging
import os
from pprint import pprint as pp

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from .controllers import get_dashboard_info

blueprint = Blueprint(
    "dashboard",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/dashboard/static",
)

LOG = logging.getLogger(__name__)


@blueprint.route("/dashboard", methods=["GET", "POST"])
def index():
    """Display the Scout dashboard."""
    data = get_dashboard_info(request)

    return render_template(
        "dashboard/dashboard_general.html",
        panel=request.form.get("panel", request.args.get("panel", "1")),
        **data,
    )
