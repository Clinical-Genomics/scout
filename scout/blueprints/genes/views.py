# -*- coding: utf-8 -*-
from flask import abort, Blueprint, request, jsonify, redirect, url_for
from flask_login import login_required
from mongoengine import Q

from scout.extensions import store
from scout.utils.helpers import templated
from scout.models import HgncGene

genes_bp = Blueprint('genes', __name__, template_folder='templates',
                     static_folder='static', static_url_path='/genes/static')


@genes_bp.route('/genes')
@templated('genes/genes.html')
@login_required
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
@login_required
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
    return dict(gene=gene_obj)


@genes_bp.route('/api/v1/genes')
@login_required
def api_genes():
    """Return JSON data about genes."""
    query = request.args.get('query')
    # filter genes by matching query to gene information
    gene_query = HgncGene.objects.filter(
        Q(hgnc_symbol__icontains=query) or
        Q(aliases__icontains=query) or
        Q(description__icontains=query)
    )
    json_terms = [{'name': '{} | {}'.format(gene.hgnc_id, gene.hgnc_symbol),
                   'id': gene.hgnc_id} for gene in gene_query]
    return jsonify(json_terms)
