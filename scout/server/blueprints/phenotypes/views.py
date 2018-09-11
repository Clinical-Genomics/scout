# -*- coding: utf-8 -*-
from flask import abort, Blueprint, request, jsonify, redirect, url_for

from scout.server.extensions import store
from scout.server.utils import templated, public_endpoint
from . import controllers

hpo_bp = Blueprint('phenotypes', __name__, template_folder='templates')

@hpo_bp.route('/phenotypes', methods=['POST', 'GET'])
@templated('phenotypes/hpo_terms.html')
def hpo_terms():
    """Render search box and view for HPO phenotype terms"""
    if request.method == 'GET':
        data = controllers.hpo_terms(store= store, limit=100)
        return data
    else: # POST. user is searching for a specific term or phenotype
        search_term = request.form.get('hpo_term')
        limit = request.form.get('limit')
        data = controllers.hpo_terms(store= store,  query = search_term, limit=limit)
        return dict(data, query=search_term, limit=limit)
