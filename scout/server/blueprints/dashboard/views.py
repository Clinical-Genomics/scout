from flask import Blueprint, render_template, request

from .controllers import populate_dashboard_data

blueprint = Blueprint(
    "dashboard",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/dashboard/static",
)


@blueprint.route("/dashboard", methods=["GET", "POST"])
def index():
    """Display the Scout dashboard."""
    data = populate_dashboard_data(request)

    return render_template(
        "dashboard/dashboard_general.html",
        **data,
    )
