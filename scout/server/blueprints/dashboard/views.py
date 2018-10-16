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

    phenotype_terms = store.case_collection.find({'phenotype_terms.1': {'$exists': True}}).count()
    causative_variants = store.case_collection.find({'causatives.1': {'$exists': True}}).count()
    pinned_variants = store.case_collection.find({'suspects.1': {'$exists': True}}).count()
    cohort_tags = store.case_collection.find({'cohorts.1': {'$exists': True}}).count()
    
    LOG.info("Fetch sanger events")
    sanger_events = store.event_collection.find({'verb':'sanger'})
    LOG.info("Sanger events fetched")
    
    sanger_cases = set()
    nr_evaluated = 0
    var_ids = set()
    LOG.info("Loop events")
    for event in sanger_events:
        case_id = event['case']
        variant_id = event['variant_id']
        LOG.info("Fetch variant")
        variant_obj = store.variant_collection.find_one({'variant_id': variant_id,'case_id':case_id})
        LOG.info("Variant fetched")
        if not variant_obj:
            continue
        doc_id = variant_obj['_id']
        if doc_id in var_ids:
            continue
        var_ids.add(doc_id)

        validation = variant_obj.get('validation', 'not_evaluated')

        # Check that the variant is not evaluated
        if validation in ['True positive', 'False positive']:
            nr_evaluated += 1
        
        sanger_cases.add(case_id)
    LOG.info("Events looped")
        
    
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
