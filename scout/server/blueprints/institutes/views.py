# -*- coding: utf-8 -*-
import logging

from flask import (Blueprint, render_template, flash, redirect, request)
from flask_login import current_user

from scout.constants import PHENOTYPE_GROUPS
from scout.server.extensions import store
from scout.server.utils import user_institutes, templated

LOG = logging.getLogger(__name__)

blueprint = Blueprint('overview', __name__, template_folder='templates')

@blueprint.route('/overview')
def institutes():
    """Display a list of all user institutes."""
    institute_objs = user_institutes(store, current_user)
    institutes = []
    for ins_obj in institute_objs:
        sanger_recipients = []
        for user_mail in ins_obj.get('sanger_recipients',[]):
            user_obj = store.user(user_mail)
            if not user_obj:
                continue
            sanger_recipients.append(user_obj['name'])
        institutes.append(
            {
                'display_name': ins_obj['display_name'],
                'internal_id': ins_obj['_id'],
                'coverage_cutoff': ins_obj.get('coverage_cutoff', 'None'),
                'sanger_recipients': sanger_recipients,
                'frequency_cutoff': ins_obj.get('frequency_cutoff', 'None'),
                'phenotype_groups': ins_obj.get('phenotype_groups', PHENOTYPE_GROUPS),
                'case_count': sum(1 for i in store.cases(collaborator=ins_obj['_id'])),
            }
        )

    data = dict(institutes=institutes)
    return render_template(
        'overview/institutes.html', **data)


@blueprint.route('/overview/edit/<institute_id>', methods=['GET','POST'])
@templated('/overview/institute.html')
def institute(institute_id):
    """ Edit institute data """

    if institute_id not in current_user.institutes or not current_user.is_admin:
        flash("Current user doesn't have the permission to modify this institute", 'warning')
        return redirect(request.referrer)

    # if institute is to be updated
    if request.method == 'POST':
        LOG.info('----------> UPDATING INSTITUTE!!!!')

    data = {
        'institute_obj' : store.institute(institute_id),
        'users' : store.users(institute_id)
    }
    return data
