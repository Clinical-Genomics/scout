# -*- coding: utf-8 -*-
from flask import Blueprint, redirect, request, url_for
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
    data = controllers.cases(all_cases)
    return dict(institute=institute_obj, **data)


@cases_bp.route('/<institute_id>/<case_name>')
@templated('cases/case.html')
def case(institute_id, case_name):
    """Display one case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = controllers.case(store, case_obj)
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
