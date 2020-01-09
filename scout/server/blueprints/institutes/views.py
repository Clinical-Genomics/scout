# -*- coding: utf-8 -*-
import logging

from flask import (Blueprint, render_template, flash, redirect, request)
from flask_login import current_user

from . import controllers
from scout.constants import PHENOTYPE_GROUPS
from scout.server.extensions import store
from scout.server.utils import user_institutes, templated
from .forms import InstituteForm

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
def institute(institute_id):
    """ Edit institute data """

    if institute_id not in current_user.institutes and current_user.is_admin is False:
        flash("Current user doesn't have the permission to modify this institute", 'warning')
        return redirect(request.referrer)

    institute_obj = store.institute(institute_id)
    form = InstituteForm(request.form)

    # if institute is to be updated
    if request.method == 'POST' and form.validate_on_submit():

        flash(request.form)

        # save form values to database
        updated_institute = controllers.update_institute_settings(store,institute_obj,request.form)
        if isinstance(updated_institute, dict):
            flash('institute was updated ', 'success')
        else: # an error message was retuned
            flash(updated_institute, 'warning')

    data = controllers.institute(store, institute_id)
    # get all other institutes to populate the select of the possible collaborators
    institutes_tuples = []
    for inst in store.institutes():
        if not inst['internal_id'] == institute_id:
            institutes_tuples.append( ((inst['internal_id'], inst['internal_id']) ))

    form.display_name.value = institute_obj.get('display_name')
    form.institutes.choices = institutes_tuples
    form.coverage_cutoff.value = institute_obj.get('coverage_cutoff')
    form.frequency_cutoff.value = institute_obj.get('frequency_cutoff')

    return render_template('/overview/institute.html', form=form, **data)
