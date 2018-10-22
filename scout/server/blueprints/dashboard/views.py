import logging

from pprint import pprint as pp

from flask import (abort, Blueprint, current_app, redirect, render_template,
                   request, url_for, send_from_directory, jsonify, flash)
from flask_login import current_user

from scout.server.extensions import store

from .controllers import get_dashboard_info

blueprint = Blueprint('dashboard', __name__, template_folder='templates')

LOG = logging.getLogger(__name__)

@blueprint.route('/dashboard', methods=['GET', 'POST'])
def index():
    """Display the Scout dashboard."""
    accessible_institutes = None
    if not 'admin' in current_user.roles:
        accessible_institutes = current_user.institutes
        if not accessible_institutes:
            flash('Not allowed to see information - please visit the dashboard later!')
            return redirect(url_for('cases.index'))

    institutes = [inst for inst in store.institutes(accessible_institutes)]
    # Insert a entry that displays all institutes in the beginning of the array
    institutes.insert(0, {'_id': None, 'display_name': 'All institutes'})

    institute_id = None
    if request.method=='POST':
        institute_id = request.form.get('institute')

    LOG.info("Fetch all cases with institute: %s", institute_id)
    data = get_dashboard_info(store, institute_id)
    data['institutes'] = institutes
    data['choice'] = institute_id
    total_cases = data['total_cases']
    
    LOG.info("Found %s cases", total_cases)
    if total_cases == 0:
        flash('no cases loaded for institute {} - please visit the dashboard later!'.format(institute_id), 'info')
        return redirect(url_for('cases.index'))
    
    return render_template(
        'dashboard/index.html', **data)
