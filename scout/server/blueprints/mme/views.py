import logging

from flask import (
    Blueprint,
    render_template,
    url_for,
)

from scout.server.extensions import store
from scout.server.utils import institute_and_case

from . import controllers

LOG = logging.getLogger(__name__)

mme_bp = Blueprint(
    "mme",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/mme/static",
)


@mme_bp.route("/<institute_id>/mme_submissions", methods=["GET"])
def mme_submissions(institute_id: str):
    """Retrieve all cases for an institute with associated a MME submission."""

    institute_obj = institute_and_case(store, institute_id)
    data = {
        "institute": institute_obj,
        "mme_cases": controllers.institute_mme_cases(institute_id=institute_id),
    }
    return render_template("mme/mme_submissions.html", **data)
