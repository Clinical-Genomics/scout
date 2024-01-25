from flask import Blueprint, jsonify

from scout.server.extensions import store
from scout.server.utils import public_endpoint, templated

from . import controllers

omim_bp = Blueprint(
    "diagnoses",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/diagnoses/static",
)


@omim_bp.route("/diagnoses/<disease_id>", methods=["GET"])
@templated("diagnoses/disease_term.html")
def diagnosis(disease_id):
    """Display information specific to one diagnosis"""

    data = controllers.disease_entry(store, disease_id)
    return data


@omim_bp.route("/diagnoses", methods=["GET"])
@templated("diagnoses/diagnoses.html")
def count_diagnoses():
    """Display the diagnosis counts for each coding system available in database"""

    data = {"counts": store.disease_terminology_count()}
    return data


@omim_bp.route("/api/v1/diagnoses")
@public_endpoint
def api_diagnoses():
    """Return JSON data about OMIM diseases in the database."""

    data = controllers.disease_terms(store)
    return jsonify(data)
