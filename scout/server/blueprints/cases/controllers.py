# -*- coding: utf-8 -*-
from flask import url_for
import query_phenomizer

from scout.constants import CASE_STATUSES, PHENOTYPE_GROUPS

STATUS_MAP = {'solved': 'bg-success', 'archived': 'bg-warning'}
SEX_MAP = {'1': 'male', '2': 'female'}
PHENOTYPE_MAP = {-9: 'missing', 0: 'missing', 1: 'unaffected', 2: 'affected'}


def user_institutes(store, user_obj):
    """Preprocess institute objects."""
    institutes = (store.institute(inst_id) for inst_id in user_obj.institutes)
    for institute in institutes:
        case_count = store.cases(collaborator=institute['internal_id']).count()
        yield (institute, case_count)


def cases(store, case_query):
    """Preprocess case objects."""
    case_groups = {status: [] for status in CASE_STATUSES}
    for case_obj in case_query:
        analysis_types = set(ind['analysis_type'] for ind in case_obj['individuals'])
        case_obj['analysis_types'] = list(analysis_types)
        if case_obj.get('assignee'):
            case_obj['assignee'] = store.user(case_obj['assignee'])
        case_groups[case_obj['status']].append(case_obj)

    data = {
        'prio_cases': case_groups['prioritized'],
        'cases': [(status, case_groups[status]) for status in CASE_STATUSES],
        'found_cases': case_query.count(),
    }
    return data


def case(store, institute_obj, case_obj):
    """Preprocess a single case."""
    for individual in case_obj['individuals']:
        individual['sex_human'] = SEX_MAP.get(individual['sex'], 'unknown')
        individual['phenotype_human'] = PHENOTYPE_MAP.get(individual['phenotype'])

    if case_obj.get('assignee'):
        case_obj['assignee'] = store.user(case_obj['assignee'])

    data = {
        'status_class': STATUS_MAP.get(case_obj['status']),
        'causatives': store.check_causatives(case_obj),
        'comments': store.events(institute_obj, case=case_obj, comments=True),
        'hpo_groups': PHENOTYPE_GROUPS,
        'events': store.events(institute_obj, case=case_obj),
    }
    return data


def update_synopsis(store, institute_obj, case_obj, user_obj, new_synopsis):
    """Update synopsis."""
    # create event only if synopsis was actually changed
    if new_synopsis and case_obj['synopsis'] != new_synopsis:
        link = url_for('cases.case', institute_id=institute_obj['_id'],
                       case_name=case_obj['display_name'])
        store.update_synopsis(institute_obj, case_obj, user_obj, link,
                              content=new_synopsis)


def hpo_diseases(username, password, hpo_ids, p_value_treshold=1):
    """Return the list of HGNC symbols that match annotated HPO terms.

    Args:
        username (str): username to use for phenomizer connection
        password (str): password to use for phenomizer connection

    Returns:
        query_result: a generator of dictionaries on the form
        {
            'p_value': float,
            'disease_source': str,
            'disease_nr': int,
            'gene_symbols': list(str),
            'description': str,
            'raw_line': str
        }
    """
    # skip querying Phenomizer unless at least one HPO terms exists
    try:
        results = query_phenomizer.query(username, password, *hpo_ids)
        diseases = [result for result in results
                    if result['p_value'] <= p_value_treshold]
        return diseases
    except SystemExit:
        return None
