from flask import (abort, Blueprint, current_app, redirect, render_template,
                   request, url_for, send_from_directory, jsonify)
from flask_login import current_user

from scout.server.extensions import store

blueprint = Blueprint('dashboard', __name__, template_folder='templates')


@blueprint.route('/dashboard')
def index():
    """Display the Scout dashboard."""
    total_cases = store.cases().count()
    cases = [{'status': 'all', 'count': total_cases, 'percent': 1}]
    query = store.case_collection.aggregate([
        {'$group' : {'_id': '$status', 'count': {'$sum': 1}}}
    ])
    for status_group in query:
        cases.append({'status': status_group['_id'],
                      'count': status_group['count'],
                      'percent': status_group['count'] / total_cases})

    query = store.case_collection.aggregate([
        {'$unwind': '$individuals'},
        {'$group': {'_id': '$individuals.analysis_type', 'count': {'$sum': 1}}}
    ])
    analysis_types = [{'name': group['_id'], 'count': group['count']} for group in query]
    return render_template('dashboard/index.html', cases=cases, analysis_types=analysis_types)
