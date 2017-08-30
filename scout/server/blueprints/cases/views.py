# -*- coding: utf-8 -*-
import os.path

from flask import (abort, Blueprint, current_app, redirect, render_template,
                   request, url_for, send_from_directory, jsonify)
from flask_login import current_user
from dateutil.parser import parse as parse_date

from scout.server.extensions import store, mail
from scout.server.utils import templated, institute_and_case, user_institutes
from . import controllers

cases_bp = Blueprint('cases', __name__, template_folder='templates',
                     static_folder='static', static_url_path='/cases/static')


@cases_bp.route('/institutes')
@templated('cases/index.html')
def index():
    """Display a list of all user institutes."""
    institute_objs = user_institutes(store, current_user)
    institutes_count = ((institute_obj, store.cases(collaborator=institute_obj['_id']).count())
                        for institute_obj in institute_objs if institute_obj)
    return dict(institutes=institutes_count)


@cases_bp.route('/<institute_id>')
@templated('cases/cases.html')
def cases(institute_id):
    """Display a list of cases for an institute."""
    institute_obj = institute_and_case(store, institute_id)
    query = request.args.get('query')
    skip_assigned = request.args.get('skip_assigned')
    all_cases = store.cases(institute_id, name_query=query, skip_assigned=skip_assigned)
    data = controllers.cases(store, all_cases)
    return dict(institute=institute_obj, skip_assigned=skip_assigned, query=query, **data)


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
    user_obj = store.user(current_user.email)
    new_synopsis = request.form.get('synopsis')
    controllers.update_synopsis(store, institute_obj, case_obj, user_obj, new_synopsis)
    return redirect(request.referrer)


@cases_bp.route('/<institute_id>/<case_name>/diagnose', methods=['POST'])
def case_diagnosis(institute_id, case_name):
    """Add or remove a diagnosis for a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for('.case', institute_id=institute_id, case_name=case_name)
    level = 'phenotype' if 'phenotype' in request.form else 'gene'
    omim_id = request.form['omim_id']
    remove = True if request.args.get('remove') == 'yes' else False
    store.diagnose(institute_obj, case_obj, user_obj, link, level=level,
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
            # add a new phenotype item/group to the case
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
            hpo_ids = [term['phenotype_id'] for term in case_obj.get('phenotype_terms', [])]

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
        store.update_dynamic_gene_list(case_obj, hgnc_symbols=hgnc_symbols)

    elif action == 'GENERATE':
        if len(hpo_ids) == 0:
            hpo_ids = [term['phenotype_id'] for term in case_obj.get('phenotype_terms', [])]
        results = store.generate_hpo_gene_list(*hpo_ids)
        # determine how many HPO terms each gene must match
        hpo_count = int(request.form.get('min_match') or 1)
        hgnc_ids = [result[0] for result in results if result[1] >= hpo_count]
        store.update_dynamic_gene_list(case_obj, hgnc_ids=hgnc_ids, phenotype_ids=hpo_ids)

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
            store.comment(institute_obj, case_obj, user_obj, link, content=content)

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
@cases_bp.route('/<institute_id>/<case_name>/<user_id>/assign', methods=['POST'])
def assign(institute_id, case_name, user_id=None):
    """Assign and unassign a user from a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    link = url_for('.case', institute_id=institute_id, case_name=case_name)
    if user_id:
        user_obj = store.user(user_id)
    else:
        user_obj = store.user(current_user.email)
    if request.form.get('action') == 'DELETE':
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
    json_terms = [{'name': '{} | {}'.format(term['_id'], term['description']),
                   'id': term['_id']} for term in terms]
    return jsonify(json_terms)


@cases_bp.route('/<institute_id>/<case_name>/<variant_id>/pin', methods=['POST'])
def pin_variant(institute_id, case_name, variant_id):
    """Pin and unpin variants to/from the list of suspects."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    user_obj = store.user(current_user.email)
    link = url_for('variants.variant', institute_id=institute_id, case_name=case_name,
                   variant_id=variant_id)
    if request.form['action'] == 'ADD':
        store.pin_variant(institute_obj, case_obj, user_obj, link, variant_obj)
    elif request.form['action'] == 'DELETE':
        store.unpin_variant(institute_obj, case_obj, user_obj, link, variant_obj)
    return redirect(request.referrer or link)


@cases_bp.route('/<institute_id>/<case_name>/<variant_id>/validate', methods=['POST'])
def mark_validation(institute_id, case_name, variant_id):
    """Mark a variant as sanger validated."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    user_obj = store.user(current_user.email)
    validate_type = request.form['type'] or None
    link = url_for('variants.variant', institute_id=institute_id, case_name=case_name,
                   variant_id=variant_id)
    store.validate(institute_obj, case_obj, user_obj, link, variant_obj, validate_type)
    return redirect(request.referrer or link)


@cases_bp.route('/<institute_id>/<case_name>/<variant_id>/causative', methods=['POST'])
def mark_causative(institute_id, case_name, variant_id):
    """Mark a variant as confirmed causative."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    user_obj = store.user(current_user.email)
    link = url_for('variants.variant', institute_id=institute_id, case_name=case_name,
                   variant_id=variant_id)
    if request.form['action'] == 'ADD':
        store.mark_causative(institute_obj, case_obj, user_obj, link, variant_obj)
    elif request.form['action'] == 'DELETE':
        store.unmark_causative(institute_obj, case_obj, user_obj, link, variant_obj)

    # send the user back to the case that was marked as solved
    case_url = url_for('.case', institute_id=institute_id, case_name=case_name)
    return redirect(case_url)


@cases_bp.route('/<institute_id>/<case_name>/delivery-report')
def delivery_report(institute_id, case_name):
    """Display delivery report."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    if case_obj.get('delivery_report') is None:
        return abort(404)

    date_str = request.args.get('date')
    if date_str:
        delivery_report = None
        analysis_date = parse_date(date_str)
        for analysis_data in case_obj['analyses']:
            if analysis_data['date'] == analysis_date:
                delivery_report = analysis_data['delivery_report']
        if delivery_report is None:
            return abort(404)
    else:
        delivery_report = case_obj['delivery_report']

    out_dir = os.path.dirname(delivery_report)
    filename = os.path.basename(delivery_report)
    return send_from_directory(out_dir, filename)


@cases_bp.route('/<institute_id>/<case_name>/share', methods=['POST'])
def share(institute_id, case_name):
    """Share a case with a different institute."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    collaborator_id = request.form['collaborator']
    revoke_access = 'revoke' in request.form
    link = url_for('.case', institute_id=institute_id, case_name=case_name)

    if revoke_access:
        store.unshare(institute_obj, case_obj, collaborator_id, user_obj, link)
    else:
        store.share(institute_obj, case_obj, collaborator_id, user_obj, link)

    return redirect(request.referrer)


@cases_bp.route('/<institute_id>/<case_name>/rerun', methods=['POST'])
def rerun(institute_id, case_name):
    """Request a case to be rerun."""
    sender = current_app.config['MAIL_USERNAME']
    recipient = current_app.config['TICKET_SYSTEM_EMAIL']
    controllers.rerun(store, mail, current_user, institute_id, case_name, sender,
                      recipient)
    return redirect(request.referrer)


@cases_bp.route('/<institute_id>/<case_name>/research', methods=['POST'])
def research(institute_id, case_name):
    """Open the research list for a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for('.case', institute_id=institute_id, case_name=case_name)
    store.open_research(institute_obj, case_obj, user_obj, link)
    return redirect(request.referrer)


@cases_bp.route('/<institute_id>/<case_name>/cohorts', methods=['POST'])
def cohorts(institute_id, case_name):
    """Add/remove institute tags."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for('.case', institute_id=institute_id, case_name=case_name)
    cohort_tag = request.form['cohort_tag']
    if request.args.get('remove') == 'yes':
        store.remove_cohort(institute_obj, case_obj, user_obj, link, cohort_tag)
    else:
        store.add_cohort(institute_obj, case_obj, user_obj, link, cohort_tag)
    return redirect(request.referrer)


@cases_bp.route('/<institute_id>/<case_name>/default-panels', methods=['POST'])
def default_panels(institute_id, case_name):
    """Update default panels for a case."""
    panel_ids = request.form.getlist('panel_ids')
    controllers.update_default_panels(store, current_user, institute_id, case_name, panel_ids)
    return redirect(request.referrer)
