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

    Request get args:
        limit:  max number of phenotypes to return
        page: the page in multiples of limit to return

    Returns:
        data(dict): dict with key "phenotypes" set to an array of all phenotype terms
    """

    limit = request.args.get("limit", None)
    page = request.args.get("page", None)

    data = controllers.hpo_terms(store=store, limit=limit, page=page)
    return jsonify(data)


@hpo_bp.route("/api/v1/phenotypes/search/<search_string>", methods=["GET"])
@public_endpoint
def api_hpo_term_search(search_string):
    """Public API for HPO phenotype term: search for a HPO terms matching a string

    Args:
        search_string(str): match HPO terms containing this string
    Request get args:
        limit:  max number of phenotypes to return
        page: the page in multiples of limit to return
    Returns:
        data(dict): result dict with key "phenotypes" set to an array of all matching phenotype terms
    """
    limit = request.args.get("limit", None)
    page = request.args.get("page", None)
    data = controllers.hpo_terms(store=store, query=search_string, limit=limit, page=page)
    return jsonify(data)
