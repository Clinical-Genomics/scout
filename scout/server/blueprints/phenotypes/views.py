# -*- coding: utf-8 -*-
from flask import Blueprint, abort, jsonify, redirect, request, url_for

from scout.server.extensions import store
from scout.server.utils import public_endpoint, templated

from . import controllers

hpo_bp = Blueprint("phenotypes", __name__, template_folder="templates")


@hpo_bp.route("/phenotypes", methods=["GET"])
@templated("phenotypes/hpo_terms.html")
def hpo_terms():
    """Render search box and view for HPO phenotype terms"""
    data = controllers.hpo_terms(store=store)
    return data


@hpo_bp.route("/api/v1/phenotypes", methods=["GET"])
@public_endpoint
def api_hpo_terms():
    """Public API for HPO phenotype terms: retrieve all HPO terms

    Returns:
        data(dict): dict with key "phenotypes" set to an array of all phenotype terms
    """

    data = controllers.hpo_terms(store=store)
    return jsonify(data)
