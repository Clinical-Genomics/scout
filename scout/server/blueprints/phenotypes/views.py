# -*- coding: utf-8 -*-
from flask import abort, Blueprint, request, jsonify, redirect, url_for

from scout.server.extensions import store
from scout.server.utils import templated, public_endpoint
from . import controllers

hpo_bp = Blueprint("phenotypes", __name__, template_folder="templates")


@hpo_bp.route("/phenotypes", methods=["GET"])
@templated("phenotypes/hpo_terms.html")
def hpo_terms():
    """Render search box and view for HPO phenotype terms"""
    data = controllers.hpo_terms(store=store)
    return data
