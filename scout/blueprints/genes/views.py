# -*- coding: utf-8 -*-
from flask import abort, Blueprint, request, jsonify
from flask_login import login_required, current_user
from flask_mongoengine import Pagination
from mongoengine import Q

from scout.extensions import store
from scout.utils.helpers import templated, validate_user
from scout.models import HgncGene

genes_bp = Blueprint('genes', __name__, template_folder='templates',
                     static_folder='static', static_url_path='/genes/static')


@genes_bp.route('/genes/<symbol>')
@templated('genes/gene.html')
@login_required
def gene(symbol):
    """Render information about a gene."""
    gene_obj = store.hgnc_gene(symbol)
    if gene_obj is None:
        return abort(404)
    return dict(gene=gene_obj)


@genes_bp.route('/api/v1/genes')
@login_required
def genes():
    """Return JSON data about genes."""
    query = request.args.get('query')
    # filter genes by matching query to gene information
    gene_query = HgncGene.objects.filter(
        Q(hgnc_symbol__icontains=query) or
        Q(aliases__icontains=query) or
        Q(description__icontains=query)
    )
    gene_data = [{'id': gene.hgnc_symbol, 'title': gene.description}
                 for gene in gene_query]
    return jsonify(results=gene_data)
