import logging

from flask import (abort, Blueprint, current_app, redirect, render_template,
                   request, url_for, send_from_directory, jsonify, flash)
from flask_login import current_user

from scout.server.extensions import store

from .controllers import get_dashboard_info

blueprint = Blueprint('dashboard', __name__, template_folder='templates')

LOG = logging.getLogger(__name__)

@blueprint.route('/dashboard')
def index():
    """Display the Scout dashboard."""
    institute_id = None
    total_cases = store.nr_cases(institute_id=None)
    if total_cases == 0:
        flash('no cases loaded - please visit the dashboard later!', 'info')
        return redirect(url_for('cases.index'))
    
    data = get_dashboard_info(store, total_cases, institute_id)
    
    return render_template(
        'dashboard/index.html', **data)
