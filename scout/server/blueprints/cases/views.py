# -*- coding: utf-8 -*-
from bson.json_util import dumps
from flask import (abort, Blueprint, current_app, redirect, render_template,
                   request, url_for, Response)
from flask_login import current_user

from scout.server.extensions import store
from scout.server.utils import templated, institute_and_case
from . import controllers

cases_bp = Blueprint('cases', __name__, template_folder='templates')


@cases_bp.route('/institutes')
@templated('cases/index.html')
def index():
    """Display a list of all user institutes."""
    user_institutes = controllers.user_institutes(store, current_user)
    return dict(institutes=user_institutes)


@cases_bp.route('/<institute_id>')
@templated('cases/cases.html')
def cases(institute_id):
    """Display a list of cases for an institute."""
    query = request.args.get('query')
    skip_assigned = request.args.get('skip_assigned')
    institute_obj = store.institute(institute_id)
    all_cases = store.cases(institute_id, name_query=query,
                            skip_assigned=skip_assigned)
    data = controllers.cases(store, all_cases)
    return dict(institute=institute_obj, **data)


@cases_bp.route('/<institute_id>/<case_name>')
@templated('cases/case.html')
def case(institute_id, case_name):
    """Display one case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = controllers.case(store, institute_obj, case_obj)
    return dict(institute=institute_obj, case=case_obj, **data)


@cases_bp.route('/<institute_id>/<case_name>/synopsis', methods=['POST'])
def case_synopsis(institute_id, case_name):
    """Update (PUT) synopsis of a specific case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    new_synopsis = request.form.get('synopsis')
    controllers.update_synopsis(store, institute_obj, case_obj, current_user,
                                new_synopsis)
    return redirect(request.referrer)


@cases_bp.route('/<institute_id>/<case_name>/diagnose', methods=['POST'])
def case_diagnosis(institute_id, case_name):
    """Add or remove a diagnosis for a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    link = url_for('.case', institute_id=institute_id, case_name=case_name)
    level = 'phenotype' if 'phenotype' in request.form else 'gene'
    omim_id = request.form['omim_id']
    remove = True if 'remove' in request.args else False
    store.diagnose(institute_obj, case_obj, current_user, link, level=level,
                   omim_id=omim_id, remove=remove)
    return redirect(request.referrer)


@cases_bp.route('/<institute_id>/<case_name>/phenotypes', methods=['POST'])
@cases_bp.route('/<institute_id>/<case_name>/phenotypes/<phenotype_id>',
                methods=['POST'])
def phenotypes(institute_id, case_name, phenotype_id=None):
    """Handle phenotypes."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    case_url = url_for('.case', institute_id=institute_id, case_name=case_name)
    is_group = request.args.get('is_group') == 'yes'
    user_obj = store.user(current_user.email)

    if phenotype_id:
        # DELETE a phenotype item/group from case
        store.remove_phenotype(institute_obj, case_obj, user_obj, case_url,
                               phenotype_id, is_group=is_group)
    else:
        try:
            # add a new phenotype item/group to the casa
            phenotype_term = request.form['hpo_term']
            if phenotype_term.startswith('HP:') or len(phenotype_term) == 7:
                hpo_term = phenotype_term.split(' | ', 1)[0]
                store.add_phenotype(institute_obj, case_obj, user_obj, case_url,
                                    hpo_term=hpo_term, is_group=is_group)
            else:
                # assume omim id
                store.add_phenotype(institute_obj, case_obj, user_obj, case_url,
                                    omim_term=phenotype_term)
        except ValueError:
            return abort(400, ("unable to add phenotype: {}".format(phenotype_term)))
    return redirect(case_url)


@cases_bp.route('/<institute_id>/<case_name>/phenotypes/actions', methods=['POST'])
def phenotypes_actions(institute_id, case_name):
    """Perform actions on multiple phenotypes."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    case_url = url_for('.case', institute_id=institute_id, case_name=case_name)
    action = request.form['action']
    hpo_ids = request.form.getlist('hpo_id')
    user_obj = store.user(current_user.email)

    if action == 'DELETE':
        for hpo_id in hpo_ids:
            # DELETE a phenotype from the list
            store.remove_phenotype(institute_obj, case_obj, user_obj, case_url, hpo_id)
    elif action == 'PHENOMIZER':
        if len(hpo_ids) == 0:
            hpo_ids = [term['phenotype_id'] for term in case_obj['phenotype_terms']]

        username = current_app.config['PHENOMIZER_USERNAME']
        password = current_app.config['PHENOMIZER_PASSWORD']
        diseases = controllers.hpo_diseases(username, password, hpo_ids)
        return render_template('cases/diseases.html', diseases=diseases,
                               institute=institute_obj, case=case_obj)

    elif action == 'GENES':
        hgnc_symbols = set()
        for raw_symbols in request.form.getlist('genes'):
            # avoid empty lists
            if raw_symbols:
                hgnc_symbols.update(raw_symbols.split('|'))
        gene_dicts = [{'gene_id': hgnc_symbol} for hgnc_symbol in hgnc_symbols]
        store.update_dynamic_gene_list(case_obj, gene_dicts)

    elif action == 'GENERATE':
        if len(hpo_ids) == 0:
            hpo_ids = [term['phenotype_id'] for term in case_obj['phenotype_terms']]
        results = store.generate_hpo_gene_list(*hpo_ids)
        # determine how many HPO terms each gene must match
        hpo_count = int(request.form.get('min_match') or len(hpo_ids))
        gene_ids = [result[0] for result in results if result[1] >= hpo_count]
        hgnc_genes = (HgncGene.objects(hgnc_id__in=gene_ids)
                              .only('hgnc_symbol').select_related())
        hgnc_symbols = [{'gene_id': gene.hgnc_symbol} for gene in hgnc_genes]
        store.update_dynamic_gene_list(case_obj, hgnc_symbols)

    return redirect(case_url)


@cases_bp.route('/<institute_id>/<case_name>/events', methods=['POST'])
@cases_bp.route('/<institute_id>/<case_name>/events/<event_id>', methods=['POST'])
def events(institute_id, case_name, event_id=None):
    """Handle events."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    link = request.form.get('link')
    content = request.form.get('content')
    variant_id = request.args.get('variant_id')
    user_obj = store.user(current_user.email)

    if event_id:
        # delete the event
        store.delete_event(event_id)
    else:
        if variant_id:
            # create a variant comment
            variant_obj = store.variant(variant_id)
            level = request.form.get('level', 'specific')
            store.comment(institute_obj, case_obj, user_obj, link,
                          variant=variant_obj, content=content, comment_level=level)
        else:
            # create a case comment
            store.comment(institute_obj, case_obj, user_obj, link,
                          content=content)

    return redirect(request.referrer)


@cases_bp.route('/<institute_id>/<case_name>/status', methods=['POST'])
def status(institute_id, case_name):
    """Update status of a specific case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)

    status = request.form.get('status', case_obj['status'])
    link = url_for('.case', institute_id=institute_id, case_name=case_name)

    if status == 'archive':
        store.archive_case(institute_obj, case_obj, user_obj, status, link)
    else:
        store.update_status(institute_obj, case_obj, user_obj, status, link)

    return redirect(request.referrer)


@cases_bp.route('/<institute_id>/<case_name>/assign', methods=['POST'])
def assign(institute_id, case_name):
    """Assign and unassign a user from a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    link = url_for('.case', institute_id=institute_id, case_name=case_name)
    user_obj = store.user(current_user.email)
    if request.form.get('action') == 'DELETE':
        # unassign
        store.unassign(institute_obj, case_obj, user_obj, link)
    else:
        store.assign(institute_obj, case_obj, user_obj, link)
    return redirect(request.referrer)


@cases_bp.route('/api/v1/hpo-terms')
def hpoterms():
    """Search for HPO terms."""
    query = request.args.get('query')
    if query is None:
        return abort(500)
    terms = store.hpo_terms(query=query).limit(8)
    json_terms = [{'name': '{} | {}'.format(term['hpo_id'], term['description']),
                   'id': term['hpo_id']} for term in terms]
    return Response(dumps(json_terms), mimetype='application/json; charset=utf-8')


@cases_bp.route('/<institute_id>/<case_name>/panels/<panel_id>')
@templated('cases/panel.html')
def panel(institute_id, case_name, panel_id):
    """Show the list of genes associated with a gene panel."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    panel_obj = store.panel(panel_id)
    # # coverage link for gene
    # covlink_kwargs = genecov_links(case_model.individuals)
    return dict(institute=institute_obj, case=case_obj, panel=panel_obj)
