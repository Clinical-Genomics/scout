from flask import Blueprint, render_template, request

from .controllers import prepare_data

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
    data = prepare_data(request)

    return render_template(
        "dashboard/dashboard_general.html",
        panel=request.form.get("panel", request.args.get("panel", "1")),
        **data,
    )
