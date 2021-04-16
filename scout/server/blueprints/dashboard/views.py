from flask import Blueprint, render_template, request

from .controllers import get_dashboard_info

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
    data = get_dashboard_info(request)

    return render_template(
        "dashboard/dashboard_general.html",
        panel=request.form.get("panel", request.args.get("panel", "1")),
        **data,
    )
