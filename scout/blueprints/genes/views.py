# -*- coding: utf-8 -*-
from flask import abort, Blueprint, request
from flask_login import login_required, current_user
from flask_mongoengine import Pagination

from scout.extensions import store
from scout.utils.helpers import templated, validate_user

genes_bp = Blueprint('genes', __name__, template_folder='templates',
                     static_folder='static', static_url_path='/genes/static')


@genes_bp.route('/genes/<hgnc_symbol>')
@templated('genes/gene.html')
@login_required
def gene(hgnc_symbol):
    """Render information about a gene."""
    gene_obj = store.hgnc_gene(hgnc_symbol)
    if gene_obj is None:
        return abort(404)
    return dict(gene=gene_obj)


@genes_bp.route('/api/v1/genes')
@login_required
def genes():
    """Return JSON data about genes."""
    panels = request.args.getlist('panel')
    return panels
