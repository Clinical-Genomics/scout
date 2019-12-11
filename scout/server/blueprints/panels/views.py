# -*- coding: utf-8 -*-
import logging
import datetime

from flask import abort, Blueprint, request, redirect, url_for, flash, render_template
from flask_weasyprint import HTML, render_pdf
from flask_login import current_user

from scout.server.extensions import store
from scout.server.utils import templated, user_institutes
from .forms import PanelGeneForm
from . import controllers

LOG = logging.getLogger(__name__)
panels_bp = Blueprint('panels', __name__, template_folder='templates')


@panels_bp.route('/panels', methods=['GET', 'POST'])
@templated('panels/panels.html')
def panels():
    """Show all panels for a case."""
    if request.method == 'POST':
        # update an existing panel
        csv_file = request.files['csv_file']
        content = csv_file.stream.read()
        lines = None
        try:
            if b'\n' in content:
                lines = content.decode('utf-8', 'ignore').split('\n')
            else:
                lines = content.decode('windows-1252').split('\r')
        except Exception as err:
            flash('Something went wrong while parsing the panel CSV file! ({})'.format(err), 'danger')
            return redirect(request.referrer)

        new_panel_name = request.form.get('new_panel_name')
        if new_panel_name: #create a new panel
            new_panel_id = controllers.new_panel(
                store=store,
                institute_id=request.form['institute'],
                panel_name=new_panel_name,
                display_name=request.form['display_name'],
                description=request.form['description'],
                csv_lines=lines,
            )
            if new_panel_id is None:
                flash('Something went wrong and the panel list was not updated!','warning')
                return redirect(request.referrer)
            else:
                flash("new gene panel added, {}!".format(new_panel_name),'success')
            return redirect(url_for('panels.panel', panel_id=new_panel_id))

        else: # modify an existing panel
            update_option = request.form['modify_option']
            panel_obj= controllers.update_panel(
                                   store=store,
                                   panel_name=request.form['panel_name'],
                                   csv_lines=lines,
                                   option=update_option
             )
            if panel_obj is None:
                return abort(404, "gene panel not found: {}".format(request.form['panel_name']))
            else:
                return redirect(url_for('panels.panel', panel_id=panel_obj['_id']))

    institutes = list(user_institutes(store, current_user))
    panel_names = [name
                   for institute in institutes
                   for name in
                   store.gene_panels(institute_id=institute['_id']).distinct('panel_name')]

    panel_versions = {}
    for name in panel_names:
        panel_versions[name]=store.gene_panels(panel_id=name)

    panel_groups = []
    for institute_obj in institutes:
         institute_panels = store.latest_panels(institute_obj['_id'])
         panel_groups.append((institute_obj, institute_panels))

    return dict(panel_groups=panel_groups, panel_names=panel_names,
                panel_versions=panel_versions, institutes=institutes)


@panels_bp.route('/panels/<panel_id>', methods=['GET', 'POST'])
@templated('panels/panel.html')
def panel(panel_id):
    """Display (and add pending updates to) a specific gene panel."""
    panel_obj = store.gene_panel(panel_id) or store.panel(panel_id)

    if request.method == 'POST':
        if request.form.get('update_description'):
            panel_obj['description'] = request.form['panel_description']
            store.update_panel(panel_obj=panel_obj)
            return redirect( url_for('panels.panel', panel_id=panel_obj['_id']) )

        raw_hgnc_id = request.form['hgnc_id']
        if '|' in raw_hgnc_id:
            raw_hgnc_id = raw_hgnc_id.split(' | ', 1)[0]
        hgnc_id = 0
        try:
            hgnc_id = int(raw_hgnc_id)
        except:
            flash("Provided HGNC is not valid : '{}'". format(raw_hgnc_id), 'danger')
            return redirect(request.referrer)
        action = request.form['action']
        gene_obj = store.hgnc_gene(hgnc_id)
        if gene_obj is None:
            flash("HGNC id not found: {}".format(hgnc_id), 'warning')
            return redirect(request.referrer)

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
            LOG.debug("marking gene to be deleted: %s", hgnc_id)
            panel_obj = store.add_pending(panel_obj, gene_obj, action='delete')

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
    update_version = request.form.get('version', None)
    new_panel_id = store.apply_pending(panel_obj, update_version)
    return redirect(url_for('panels.panel', panel_id=new_panel_id))


@panels_bp.route('/panels/export-panel/<panel_id>', methods=['GET', 'POST'])
def panel_export(panel_id):
    """Export panel to PDF file"""
    panel_obj = store.panel(panel_id)
    data = controllers.panel_export(store, panel_obj)
    data['report_created_at'] = datetime.datetime.now().strftime("%Y-%m-%d")
    html_report = render_template('panels/panel_pdf_simple.html', **data)
    return render_pdf(HTML(string=html_report), download_filename=data['panel']['panel_name']+'_'+str(data['panel']['version'])+'_'+datetime.datetime.now().strftime("%Y-%m-%d")+'_scout.pdf')


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
        if transcript.get('refseq_id'):
            refseq_id = transcript.get('refseq_id')
            transcript_choices.append((refseq_id, refseq_id))
    form.disease_associated_transcripts.choices = transcript_choices
    if form.validate_on_submit():
        action = 'edit' if panel_gene else 'add'
        info_data = form.data.copy()
        if 'csrf_token' in info_data:
            del info_data['csrf_token']
        if 'custom_inheritance_models' in info_data:
            info_data['custom_inheritance_models'] = info_data['custom_inheritance_models'].split(',')

        store.add_pending(panel_obj, hgnc_gene, action=action, info=info_data)
        return redirect(url_for('.panel', panel_id=panel_id))

    if panel_gene:
        form.custom_inheritance_models.data = ', '.join(panel_gene.get('custom_inheritance_models',[]))
        for field_key in ['disease_associated_transcripts', 'reduced_penetrance',
                          'mosaicism', 'inheritance_models', 'custom_inheritance_models',
                          'database_entry_version', 'comment']:
            form_field = getattr(form, field_key)
            if not form_field.data:
                panel_value = panel_gene.get(field_key)
                if panel_value is not None:
                    form_field.process_data(panel_value)
    return dict(panel=panel_obj, form=form, gene=hgnc_gene, panel_gene=panel_gene)
