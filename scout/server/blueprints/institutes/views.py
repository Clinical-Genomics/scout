# -*- coding: utf-8 -*-
import logging

from flask import (Blueprint, render_template)
from flask_login import current_user

from scout.constants import PHENOTYPE_GROUPS
from scout.server.extensions import store
from scout.server.utils import user_institutes

log = logging.getLogger(__name__)

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
                'phenotype_groups': ins_obj.get('phenotype_groups', PHENOTYPE_GROUPS)
            }
        )

    data = dict(institutes=institutes)
    return render_template(
        'overview/institutes.html', **data)
