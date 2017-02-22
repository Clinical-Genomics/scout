# -*- coding: utf-8 -*-
import logging

from flask import abort, Blueprint, flash, request, jsonify, redirect, url_for
from flask_login import login_required, current_user

from scout.extensions import store
from scout.utils.helpers import templated, validate_user
from . import controller

log = logging.getLogger(__name__)
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

    controller.gene(gene_obj)
    return dict(gene=gene_obj)


@genes_bp.route('/api/v1/genes')
@login_required
def api_genes():
    """Return JSON data about genes."""
    query = request.args.get('query')
    # filter genes by matching query to gene information
    gene_query = store.hgnc_genes(query, search=True)
    json_terms = [{'name': '{} | {}'.format(gene['hgnc_id'], gene['hgnc_symbol']),
                   'id': gene['hgnc_id']} for gene in gene_query]
    return jsonify(json_terms)


@genes_bp.route('/genes/<institute_id>/panels')
@templated('genes/panels.html')
@login_required
def panels(institute_id):
    """Show all gene panels for an institute."""
    inst_mod = validate_user(current_user, institute_id)
    inst_panels = store.gene_panels(institute_id)
    return dict(panels=inst_panels, institute=inst_mod)


@genes_bp.route('/genes/panels/<panel_id>', methods=['GET', 'POST'])
@templated('genes/panel.html')
@login_required
def panel(panel_id):
    """Edit a gene panel."""
    gene_panel = store.gene_panel(panel_id)

    if request.method == 'POST':
        if 'hgnc_id' in request.form:
            hgnc_id = int(request.form['hgnc_id'])
            log.debug("marking gene to be deleted: %s", hgnc_id)
            for gene in gene_panel['genes']:
                if gene['hgnc_id'] == hgnc_id:
                    new_gene = dict(hgnc_id=hgnc_id, symbol=gene['symbol'],
                                    action='delete')
                    log.info("adding pending delete of: %s", gene['symbol'])
                    (store.hgnc_collection
                          .update_one({'_id': gene_panel['_id']},
                                      {'$push': {'pending_genes': new_gene}}))
                    gene_panel.save()

        elif 'newGene' in request.form:
            hgnc_id = request.form['newGene']
            if '|' in hgnc_id:
                hgnc_id = hgnc_id.split(' | ', 1)[0]
            hgnc_id = int(hgnc_id)
            log.debug("add pending gene: %s", hgnc_id)
            panel_genes = {gene['hgnc_id']: gene for gene in gene_panel['genes']}
            if hgnc_id not in panel_genes:
                hgnc_gene = store.hgnc_gene(hgnc_id)
                new_gene = dict(hgnc_id=hgnc_id, symbol=hgnc_gene['hgnc_symbol'],
                                action='add')
                log.info("add pending gene: %s", new_gene['symbol'])
                (store.hgnc_collection
                      .update_one({'_id': gene_panel['_id']},
                                  {'$push': {'pending_genes': new_gene}}))
            else:
                symbol = panel_genes[hgnc_id]['symbol']
                flash("gene already in gene panel: {}".format(symbol), 'warning')

    inst_mod = store.institute(gene_panel['institute'])
    return dict(institute=inst_mod, panel=gene_panel)


@genes_bp.route('/genes/panels/<panel_id>/update', methods=['POST'])
@login_required
def panel_update(panel_id):
    """Update a panel to a new version."""
    gene_panel = store.gene_panel(panel_id)
    if len(gene_panel['pending_genes']) == 0:
        flash("panel doesn't contain any updates", 'warning')
        return redirect(url_for('.panel', panel_id=panel['panel_name']))
    else:
        log.info("updating panel: %s", gene_panel['panel_name'])
        store.update_panel(gene_panel)
        return redirect(url_for('.panels', institute_id=gene_panel['institute']))
