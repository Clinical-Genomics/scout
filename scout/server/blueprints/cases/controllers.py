# -*- coding: utf-8 -*-
from flask import url_for

from scout.constants import CASE_STATUSES

STATUS_MAP = {'solved': 'bg-success', 'archived': 'bg-warning'}
SEX_MAP = {'1': 'male', '2': 'female'}
PHENOTYPE_MAP = {-9: 'missing', 0: 'missing', 1: 'unaffected', 2: 'affected'}


def user_institutes(store, user_obj):
    """Preprocess institute objects."""
    institutes = (store.institute(inst_id) for inst_id in user_obj.institutes)
    for institute in institutes:
        case_count = store.cases(collaborator=institute['internal_id']).count()
        yield (institute, case_count)


def cases(case_query):
    """Preprocess case objects."""
    case_groups = {status: [] for status in CASE_STATUSES}
    for case_obj in case_query:
        analysis_types = set(ind['analysis_type'] for ind in case_obj['individuals'])
        case_obj['analysis_types'] = list(analysis_types)
        case_groups[case_obj['status']].append(case_obj)

    data = {
        'prio_cases': case_groups['prioritized'],
        'cases': [(status, case_groups[status]) for status in CASE_STATUSES],
        'found_cases': case_query.count(),
    }
    return data


def case(store, case_obj):
    """Preprocess a single case."""
    for individual in case_obj['individuals']:
        individual['sex_human'] = SEX_MAP.get(individual['sex'], 'unknown')
        individual['phenotype_human'] = PHENOTYPE_MAP.get(individual['phenotype'])

    data = {
        'status_class': STATUS_MAP.get(case_obj['status']),
        'causatives': store.check_causatives(case_obj),
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
