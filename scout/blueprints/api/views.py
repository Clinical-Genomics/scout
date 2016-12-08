# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import Blueprint, request, redirect, url_for
from flask_login import current_user

from scout.utils.helpers import validate_user
from scout.extensions import store

# markdown to HTML converter object
api = Blueprint('api', __name__, url_prefix='/api/v1')


@api.route('/<institute_id>/<case_id>/status', methods=['POST'])
def case_status(institute_id, case_id):
    """Update status of a specific case."""
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)

    status = request.form.get('status', case_model.status)
    link = url_for('core.case', institute_id=institute_id, case_id=case_id)

    if status == 'archive':
        store.archive_case(institute, case_model, current_user, status, link)
    else:
        store.update_status(institute, case_model, current_user, status, link)

    return redirect(request.referrer)


@api.route('/<institute_id>/<case_id>/synopsis', methods=['POST'])
def case_synopsis(institute_id, case_id):
    """Update (PUT) synopsis of a specific case."""
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    new_synopsis = request.form.get('synopsis', case_model.synopsis)

    if case_model.synopsis != new_synopsis:
        # create event only if synopsis was actually changed
        link = url_for('core.case', institute_id=institute_id, case_id=case_id)
        store.update_synopsis(institute, case_model, current_user, link,
                              content=new_synopsis)
    return redirect(request.referrer)


@api.route('/<institute_id>/<case_id>/events', methods=['POST'])
def create_event(institute_id, case_id):
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)

    link = request.form.get('link')
    content = request.form.get('content')
    variant_id = request.args.get('variant_id')

    if variant_id:
        # create a variant comment
        variant_model = store.variant(variant_id)
        level = request.form.get('level', 'specific')
        store.comment(institute, case_model, current_user, link,
                      variant=variant_model, content=content,
                      comment_level=level)
    else:
        # create a case comment
        store.comment(institute, case_model, current_user, link,
                      content=content)

    return redirect(request.referrer)


@api.route('/<institute_id>/<case_id>/events/<event_id>', methods=['POST'])
def delete_event(institute_id, case_id, event_id=None):
    validate_user(current_user, institute_id)
    store.delete_event(event_id)
    return redirect(request.referrer)


@api.route('/<institute_id>/<case_id>/variants/<variant_id>/manual_rank',
           methods=['POST'])
def manual_rank(institute_id, case_id, variant_id):
    """Update the manual variant rank for a variant."""
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    variant_model = store.variant(document_id=variant_id)

    # update the manual rank
    new_manual_rank = int(request.form.get('manual_rank'))
    link = request.referrer

    store.update_manual_rank(institute, case_model, current_user, link,
                             variant_model, new_manual_rank)

    return redirect(request.referrer)
