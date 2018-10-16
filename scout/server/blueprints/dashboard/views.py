import logging

from flask import (abort, Blueprint, current_app, redirect, render_template,
                   request, url_for, send_from_directory, jsonify, flash)
from flask_login import current_user

from scout.server.extensions import store

blueprint = Blueprint('dashboard', __name__, template_folder='templates')

LOG = logging.getLogger(__name__)

@blueprint.route('/dashboard')
def index():
    """Display the Scout dashboard."""
    total_cases = store.cases().count()
    if total_cases == 0:
        flash('no cases loaded - please visit the dashboard later!', 'info')
        return redirect(url_for('cases.index'))
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

    phenotype_terms = store.case_collection.find({'phenotype_terms': {'$exists': True}}).count()
    causative_variants = store.case_collection.find({'causatives': {'$exists': True}}).count()
    pinned_variants = store.case_collection.find({'suspects': {'$exists': True}}).count()
    cohort_tags = store.case_collection.find({'cohorts': {'$exists': True}}).count()

    LOG.info("Fetch sanger variants")
    nr_evaluated = store.variant_collection.find({'validation': {'$exists':True, '$ne': "Not validated"}}).count()
    
    LOG.info("Fetch sanger events")
    sanger_cases = store.event_collection.distinct('case', {'verb':'sanger'})
    LOG.info("Sanger events fetched")
    
    sanger_ordered = len(sanger_cases)
    
    overview = [
        {
            'title': 'Phenotype terms',
            'count': phenotype_terms,
            'percent': phenotype_terms / total_cases,
        }, 
        {
            'title': 'Causative variants',
            'count': causative_variants,
            'percent': causative_variants / total_cases,
        }, 
        {
            'title': 'Pinned variants',
            'count': pinned_variants,
            'percent': pinned_variants / total_cases,
        }, 
        {
            'title': 'Cohort tag',
            'count': cohort_tags,
            'percent': cohort_tags / total_cases,
        },
        {
            'title': 'Sanger ordered',
            'count': sanger_ordered,
            'percent': sanger_ordered / total_cases,
        },
        {
            'title': 'Sanger confirmed',
            'count': nr_evaluated,
            'percent': nr_evaluated / total_cases,
        },
    ]
    return render_template(
        'dashboard/index.html',
        cases=cases,
        analysis_types=analysis_types,
        overview=overview,
    )
