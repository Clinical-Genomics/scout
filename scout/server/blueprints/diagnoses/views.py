from flask import Blueprint

from scout.server.extensions import store
from scout.server.utils import templated, public_endpoint
from . import controllers

omim_bp = Blueprint("diagnoses", __name__, template_folder="templates")


@omim_bp.route("/diagnoses/<omim_nr>", methods=["GET"])
@templated("diagnoses/omim_term.html")
def omim_diagnosis(omim_nr):
    """Display information specific to one OMIM diagnosis"""

    data = controllers.omim_entry(store, omim_nr)
    return data


@omim_bp.route("/diagnoses", methods=["GET"])
@templated("diagnoses/omim_terms.html")
def omim_diagnoses():
    """Display all OMIM diagnoses available in database"""

    data = {"terms": store.disease_terms()}
    return data
