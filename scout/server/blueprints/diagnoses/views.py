from flask import Blueprint, jsonify

from scout.server.extensions import store
from scout.server.utils import public_endpoint, templated

from . import controllers

omim_bp = Blueprint("diagnoses", __name__, template_folder="templates")


@omim_bp.route("/diagnoses/<disease_id>", methods=["GET"])
@templated("diagnoses/omim_term.html")
def omim_diagnosis(disease_id):
    """Display information specific to one OMIM diagnosis"""

    data = controllers.disease_entry(store, disease_id)
    return data


@omim_bp.route("/diagnoses", methods=["GET"])
@templated("diagnoses/omim_terms.html")
def omim_diagnoses():
    """Display all OMIM diagnoses available in database"""

    data = controllers.disease_terms(store=store)
    return data


@omim_bp.route("/api/v1/diagnoses")
@public_endpoint
def api_diagnoses():
    """Return JSON data about OMIM diseases in the database."""

    data = controllers.disease_terms(store)
    return jsonify(data)
