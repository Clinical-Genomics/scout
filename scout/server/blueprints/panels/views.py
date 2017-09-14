# -*- coding: utf-8 -*-
import logging

from flask import abort, Blueprint, request, jsonify, redirect, url_for, flash
from flask_login import current_user

from scout.server.extensions import store
from scout.server.utils import templated, user_institutes
from scout.server.userpanel import parse_panel, build_panel
from .forms import PanelGeneForm
from . import controllers

log = logging.getLogger(__name__)
panels_bp = Blueprint('panels', __name__, template_folder='templates')


@panels_bp.route('/panels', methods=['GET', 'POST'])
@templated('panels/panels.html')
def panels():
    """Show all panels for a case."""
    if request.method == 'POST':
        # add new panel
        csv_file = request.files['csv_file']
        lines = csv_file.stream.read().decode().split('\r')
        panel_genes = parse_panel(lines)
        try:
            panel_obj = build_panel(
                adapter=store,
                institute_id=request.form['institute_id'],
                panel_name=request.form['panel_name'],
                display_name=request.form['display_name'],
                version=float(request.form['version']) if request.form.get('version') else 1.0,
                panel_genes=panel_genes,
            )
        except ValueError as error:
            flash(error.args[0], 'warning')
            return redirect(request.referrer)
        store.add_gene_panel(panel_obj)
        flash("new gene panel added: {}".format(panel_obj['panel_name']), 'info')

    panel_groups = []
    for institute_obj in user_institutes(store, current_user):
        institute_panels = store.gene_panels(institute_id=institute_obj['_id'])
        panel_groups.append((institute_obj, institute_panels))
    return dict(panel_groups=panel_groups, institutes=user_institutes(store, current_user))


@panels_bp.route('/panels/<panel_id>', methods=['GET', 'POST'])
@templated('panels/panel.html')
def panel(panel_id):
    """Display (and add pending updates to) a specific gene panel."""
    panel_obj = store.gene_panel(panel_id) or store.panel(panel_id)
    if request.method == 'POST':
        raw_hgnc_id = request.form['hgnc_id']
        if '|' in raw_hgnc_id:
            raw_hgnc_id = raw_hgnc_id.split(' | ', 1)[0]
        hgnc_id = int(raw_hgnc_id)
        action = request.form['action']

        if action == 'add':
            panel_gene = controllers.existing_gene(store, panel_obj, hgnc_id)
            if panel_gene:
                flash("gene already in panel: {}".format(panel_gene['symbol']),
                      'warning')
            else:
                # ask user to fill-in more information about the gene
                return redirect(url_for('.gene_edit', panel_id=panel_id,
                                        hgnc_id=hgnc_id))
        elif action == 'delete':
            log.debug("marking gene to be deleted: %s", hgnc_id)
            store.add_pending(panel_obj, hgnc_id, action='delete')

    data = controllers.panel(store, panel_obj)
    if request.args.get('case_id'):
        data['case'] = store.case(request.args['case_id'])
    if request.args.get('institute_id'):
        data['institute'] = store.institute(request.args['institute_id'])
    return data


@panels_bp.route('/panels/<panel_id>/update', methods=['POST'])
def panel_update(panel_id):
    """Update panel to a new version."""
    panel_obj = store.panel(panel_id)
    store.apply_pending(panel_obj)
    return redirect(url_for('.panels'))


@panels_bp.route('/panels/<panel_id>/update/<int:hgnc_id>', methods=['GET', 'POST'])
@templated('panels/gene-edit.html')
def gene_edit(panel_id, hgnc_id):
    """Edit additional information about a panel gene."""
    panel_obj = store.panel(panel_id)
    hgnc_gene = store.hgnc_gene(hgnc_id)
    panel_gene = controllers.existing_gene(store, panel_obj, hgnc_id)

    form = PanelGeneForm()
    transcript_choices = []
    for transcript in hgnc_gene['transcripts']:
        if transcript.get('refseq_ids'):
            for refseq_id in transcript['refseq_ids']:
                transcript_choices.append((refseq_id, refseq_id))
    form.disease_associated_transcripts.choices = transcript_choices

    if form.validate_on_submit():
        action = 'edit' if panel_gene else 'add'
        info_data = form.data.copy()
        if 'csrf_token' in info_data:
            del info_data['csrf_token']
        store.add_pending(panel_obj, hgnc_id, action=action, info=info_data)
        return redirect(url_for('.panel', panel_id=panel_id))

    if panel_gene:
        for field_key in ['disease_associated_transcripts', 'reduced_penetrance',
                          'mosaicism', 'inheritance_models', 'comment']:
            form_field = getattr(form, field_key)
            if not form_field.data:
                panel_value = panel_gene.get(field_key)
                if panel_value is not None:
                    form_field.process_data(panel_value)
    return dict(panel=panel_obj, form=form, gene=hgnc_gene, panel_gene=panel_gene)
