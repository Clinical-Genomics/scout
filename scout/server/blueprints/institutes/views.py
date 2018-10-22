# -*- coding: utf-8 -*-
import datetime

import logging

from pprint import pprint as pp

from flask import (abort, Blueprint, current_app, redirect, render_template,
                   request, url_for, send_from_directory, jsonify, Response, flash)
from flask_login import current_user

from dateutil.parser import parse as parse_date
from scout.constants import PHENOTYPE_GROUPS
from scout.server.extensions import store
from scout.server.utils import user_institutes
# from . import controllers

log = logging.getLogger(__name__)

blueprint = Blueprint('institutesov', __name__, template_folder='templates')


@blueprint.route('/institutesov')
def index():
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
                'coverage_cutoff': ins_obj['coverage_cutoff'],
                'sanger_recipients': sanger_recipients,
                'frequency_cutoff': ins_obj.get('frequency_cutoff', 'None'),
                'phenotype_groups': ins_obj.get('phenotype_groups', PHENOTYPE_GROUPS)
            }
        )

    data = dict(institutes=institutes)
    pp(data)
    return render_template(
        'institutesov/index.html', **data)
