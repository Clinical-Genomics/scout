from flask import Blueprint

from scout.server.extensions import store
from scout.server.utils import templated, public_endpoint
from . import controllers

omim_bp = Blueprint("diagnoses", __name__, template_folder="templates")


@omim_bp.route("/diagnoses/<omim_nr>", methods=["GET"])
@templated("diagnoses/omim_term.html")
def omim_diagnosis(omim_nr):
    """Display genes associated to a specific OMIM diagnosis"""

    data = controllers.omim_entry(store, omim_nr)
    return data
