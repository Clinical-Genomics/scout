# -*- coding: utf-8 -*-
from flask import abort, Blueprint, request, jsonify, redirect, url_for

from scout.server.extensions import store
from scout.server.utils import templated
from . import controllers

genes_bp = Blueprint('genes', __name__, template_folder='templates')


@genes_bp.route('/genes')
@templated('genes/genes.html')
def genes():
    """Render seach box for genes."""
    query = request.args.get('query', '')
    if '|' in query:
        hgnc_id = int(query.split(' | ', 1)[0])
        return redirect(url_for('.gene', hgnc_id=hgnc_id))
    gene_q = store.all_genes().limit(20)
    return dict(genes=gene_q)


@genes_bp.route('/genes/<int:hgnc_id>')
@genes_bp.route('/genes/<hgnc_symbol>')
@templated('genes/gene.html')
def gene(hgnc_id=None, hgnc_symbol=None):
    """Render information about a gene."""
    if hgnc_symbol:
        query = store.hgnc_genes(hgnc_symbol)
        if query.count() < 2:
            gene_obj = query.first()
        else:
            return redirect(url_for('.genes', query=hgnc_symbol))
    else:
        gene_obj = store.hgnc_gene(hgnc_id)

    if gene_obj is None:
        return abort(404)

    controllers.gene(gene_obj)
    return dict(gene=gene_obj)


@genes_bp.route('/api/v1/genes')
def api_genes():
    """Return JSON data about genes."""
    query = request.args.get('query')
    json_out = controllers.genes_to_json(store, query)
    return jsonify(json_out)
