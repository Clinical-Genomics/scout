import logging
import os

from pprint import pprint as pp

from flask import (
    abort,
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
    send_from_directory,
    jsonify,
    flash,
)
from flask_login import current_user

from scout.server.extensions import store

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
    accessible_institutes = current_user.institutes
    if not "admin" in current_user.roles:
        accessible_institutes = current_user.institutes
        if not accessible_institutes:
            flash("Not allowed to see information - please visit the dashboard later!")
            return redirect(url_for("cases.dahboard_general.html"))

    LOG.debug("User accessible institutes: {}".format(accessible_institutes))
    institutes = [inst for inst in store.institutes(accessible_institutes)]

    # Insert a entry that displays all institutes in the beginning of the array
    institutes.insert(0, {"_id": None, "display_name": "All institutes"})

    institute_id = None
    slice_query = None
    panel = 1
    if request.method == "POST":
        institute_id = request.form.get("institute")
        slice_query = request.form.get("query")
        panel = request.form.get("pane_id")

    elif request.method == "GET":
        institute_id = request.args.get("institute")
        slice_query = request.args.get("query")

    # User should be restricted to their own institute if:
    # 1) Their default institute when the page is first loaded
    # 2) if they ask for an institute that they don't belong to
    # 3) if they want perform a query on all institutes

    if not institute_id:
        institute_id = accessible_institutes[0]
    elif (not current_user.is_admin) and (slice_query and institute_id == "None"):
        institute_id = accessible_institutes[0]
    elif (not institute_id in accessible_institutes) and not (institute_id == "None"):
        institute_id = accessible_institutes[0]

    LOG.info("Fetch all cases with institute: %s", institute_id)

    data = get_dashboard_info(store, institute_id, slice_query)
    data["institutes"] = institutes
    data["choice"] = institute_id
    total_cases = data["total_cases"]

    LOG.info("Found %s cases", total_cases)
    if total_cases == 0:
        flash(
            "no cases found for institute {} (with that query) - please visit the dashboard later!".format(
                institute_id
            ),
            "info",
        )
    #        return redirect(url_for('cases.index'))

    return render_template(
        "dashboard/dashboard_general.html",
        institute=institute_id,
        query=slice_query,
        panel=panel,
        **data
    )
